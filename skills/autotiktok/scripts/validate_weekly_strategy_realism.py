#!/usr/bin/env python3
"""
Validate weekly strategy realism fixtures and rollback semantics.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BUILD_WEEKLY_REVIEW_WINDOW_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_weekly_review_window.py"
)
WEEKLY_PROMOTION_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "weekly_promotion_mock.py"
)
COMMITTED_WEEKLY_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)
COMMITTED_WEEKLY_PROMOTION = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.sample.json"
)


def run_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        committed_window = load_json(COMMITTED_WEEKLY_WINDOW)
        committed_weekly = load_json(COMMITTED_WEEKLY_PROMOTION)
        reward_horizons = committed_window.get("rewardHorizonPolicy", {}).get("horizons", [])
        if [item.get("horizonId") for item in reward_horizons] != ["t+1", "t+3", "t+7"]:
            raise RuntimeError("committed weekly review window has unexpected reward horizon policy")
        if committed_window["windows"][0]["availableRewardHorizonIds"] != [
            "t+1",
            "t+3",
            "t+7",
        ]:
            raise RuntimeError("oldest committed weekly window should expose t+7 availability")
        if committed_window["windows"][-1]["availableRewardHorizonIds"] != [
            "t+1",
            "t+3",
        ]:
            raise RuntimeError("newest committed weekly window should keep only required reward horizons")
        if committed_window["bestChallengerProfileId"] != "search-priority-default":
            raise RuntimeError("committed weekly review window picked an unexpected leader")
        if committed_window["rollbackSignals"]["rollbackTriggered"]:
            raise RuntimeError("committed weekly review window should not trigger rollback")
        if committed_window["rollbackSignals"]["rollbackEligible"]:
            raise RuntimeError("committed weekly review window should not mark rollbackEligible")
        if committed_window["rollbackSignals"]["rollbackSeverity"] != "none":
            raise RuntimeError("committed weekly review window should keep rollbackSeverity=none")
        if committed_weekly["decision"] != "promote":
            raise RuntimeError("committed weekly promotion sample should model promotion")
        if committed_weekly["gateSummary"]["weeklyStageMode"] != "growth":
            raise RuntimeError("committed weekly promotion sample should keep weeklyStageMode=growth")
        if committed_weekly["gateSummary"]["weeklyStagePolicyId"] != "growth_weekly_gate":
            raise RuntimeError("committed weekly promotion sample should use growth_weekly_gate")
        if committed_weekly["gateSummary"]["requiredRewardHorizonIds"] != ["t+1", "t+3"]:
            raise RuntimeError("committed weekly promotion sample has unexpected required reward horizons")
        if not committed_weekly.get("promotionCandidateReviews"):
            raise RuntimeError("committed weekly promotion sample must declare promotionCandidateReviews")
        if committed_weekly["promotionCandidateReviews"][0]["profileId"] != "search-priority-default":
            raise RuntimeError("committed weekly promotion sample has unexpected lead challenger review")
        if not committed_weekly["promotionCandidateReviews"][0]["eligibleForPromotion"]:
            raise RuntimeError("committed weekly promotion sample should keep an eligible lead challenger")
        if committed_weekly.get("championSafetyReview", {}).get("rollbackEligible"):
            raise RuntimeError("committed weekly promotion sample should not mark champion rollbackEligible")
        if committed_weekly.get("championSafetyReview", {}).get("rollbackTriggered"):
            raise RuntimeError("committed weekly promotion sample should not mark champion rollbackTriggered")
        if committed_weekly.get("championSafetyReview", {}).get("rollbackSeverity") != "none":
            raise RuntimeError("committed weekly promotion sample should keep rollbackSeverity=none")
        if committed_weekly.get("sourceReviewWindowId") != committed_window.get(
            "reviewWindowId"
        ):
            raise RuntimeError("weekly promotion sample must point at committed weekly window")

        with tempfile.TemporaryDirectory(prefix="autotiktok-weekly-strategy-") as temp_dir:
            temp_root = Path(temp_dir)
            rollback_window_path = temp_root / "weekly-window-rollback.json"
            rollback_weekly_path = temp_root / "weekly-rollback.json"
            run_script(
                BUILD_WEEKLY_REVIEW_WINDOW_SCRIPT,
                "--scenario",
                "rollback_guardrail",
                "--output",
                str(rollback_window_path),
            )
            rollback_window = load_json(rollback_window_path)
            if not rollback_window["rollbackSignals"]["rollbackTriggered"]:
                raise RuntimeError("rollback weekly review window did not trigger rollback")
            if rollback_window["rollbackSignals"]["rollbackSeverity"] != "critical":
                raise RuntimeError("rollback weekly review window should escalate to critical severity")
            if "critical_holdout_regression" not in rollback_window["rollbackSignals"]["rollbackReasonCodes"]:
                raise RuntimeError("rollback weekly review window should include critical_holdout_regression")
            run_script(
                WEEKLY_PROMOTION_SCRIPT,
                "--weekly-review-window-input",
                str(rollback_window_path),
                "--output",
                str(rollback_weekly_path),
            )
            rollback_weekly = load_json(rollback_weekly_path)
            if rollback_weekly["decision"] != "rollback_champion":
                raise RuntimeError("rollback scenario did not emit rollback_champion")
            if not rollback_weekly.get("championSafetyReview", {}).get("rollbackTriggered"):
                raise RuntimeError("rollback scenario did not mark championSafetyReview.rollbackTriggered")
            if rollback_weekly.get("championSafetyReview", {}).get("rollbackSeverity") != "critical":
                raise RuntimeError("rollback scenario should emit championSafetyReview.rollbackSeverity=critical")
            if "critical_holdout_regression" not in rollback_weekly.get("championSafetyReview", {}).get("rollbackReasonCodes", []):
                raise RuntimeError("rollback scenario should emit championSafetyReview.rollbackReasonCodes")

            scale_window_path = temp_root / "weekly-window-scale.json"
            scale_weekly_path = temp_root / "weekly-scale.json"
            scale_window = dict(committed_window)
            scale_window["championProfileSelection"] = dict(committed_window["championProfileSelection"])
            scale_window["generatedFrom"] = dict(committed_window["generatedFrom"])
            scale_window["championProfileSelection"]["stageMode"] = "scale"
            scale_window["generatedFrom"]["stageMode"] = "scale"
            scale_window_path.write_text(
                json.dumps(scale_window, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            run_script(
                WEEKLY_PROMOTION_SCRIPT,
                "--weekly-review-window-input",
                str(scale_window_path),
                "--output",
                str(scale_weekly_path),
            )
            scale_weekly = load_json(scale_weekly_path)
            if scale_weekly["decision"] != "keep_champion":
                raise RuntimeError("scale stage should keep champion under stricter weekly gates")
            if scale_weekly["gateSummary"]["weeklyStagePolicyId"] != "scale_weekly_gate":
                raise RuntimeError("scale stage should resolve scale_weekly_gate")
            failed_gate_ids = scale_weekly["promotionCandidateReviews"][0]["failedGateIds"]
            if "minimum_average_reward_delta" not in failed_gate_ids:
                raise RuntimeError("scale stage should fail minimum_average_reward_delta")
            if "minimum_average_holdout_delta" not in failed_gate_ids:
                raise RuntimeError("scale stage should fail minimum_average_holdout_delta")

        print("Weekly strategy realism fixtures and rollback semantics are aligned.")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
