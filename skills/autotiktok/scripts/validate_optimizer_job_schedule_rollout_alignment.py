#!/usr/bin/env python3
"""
Validate scheduler-driven optimizer input rollout classes against production semantics.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_JOB_SCHEDULE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_schedule.py"
)
RUN_SCHEDULED_JOB_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_scheduled_optimizer_job.py"
)
BUILD_INPUT_ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_rollout_policy.py"
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_semantic_view(payload: dict[str, Any]) -> dict[str, Any]:
    offline_cycle = payload["artifacts"]["offlineCycle"]
    daily_review = offline_cycle["artifacts"]["dailyReview"]
    weekly_promotion = offline_cycle["artifacts"].get("weeklyPromotion")
    combined_breakdown = daily_review.get("combinedRewardBreakdown", {})
    recommendation = daily_review.get("recommendation", {})
    return {
        "jobKind": payload.get("jobKind"),
        "mode": payload.get("mode"),
        "rankingProfileId": payload.get("summary", {}).get("rankingProfileId"),
        "dailyRecommendation": payload.get("summary", {}).get("dailyRecommendation"),
        "shadowLeaderProfileId": payload.get("summary", {}).get("shadowLeaderProfileId"),
        "selectedChallengerProfileId": payload.get("summary", {}).get(
            "selectedChallengerProfileId"
        ),
        "weeklyDecision": payload.get("summary", {}).get("weeklyDecision"),
        "dailyRecommendationReason": recommendation.get("reason"),
        "combinedReward": combined_breakdown.get("combinedReward"),
        "postCoverageRate": combined_breakdown.get("postCoverageRate"),
        "weeklyDecisionReason": None
        if weekly_promotion is None
        else weekly_promotion.get("reason"),
    }


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-job-schedule-rollout-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            daily_production_path = temp_root / "daily-production.json"
            daily_raw_shadow_path = temp_root / "daily-raw-shadow.json"
            daily_preview_path = temp_root / "daily-preview-validation.json"
            daily_profile_compare_path = (
                temp_root / "daily-profile-compare-validation.json"
            )
            weekly_production_path = temp_root / "weekly-production.json"
            weekly_real_shadow_path = temp_root / "weekly-real-shadow.json"

            run_script(
                BUILD_INPUT_ROLLOUT_POLICY_SCRIPT,
                "--output",
                str(rollout_policy_path),
            )
            run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--output",
                str(schedule_path),
            )

            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--output",
                str(daily_production_path),
            )
            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--input-rollout-class",
                "raw_shadow_validation",
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--output",
                str(daily_raw_shadow_path),
            )
            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--scheduler-rollout-intent",
                "preview_validation",
                "--output",
                str(daily_preview_path),
            )
            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--scheduler-rollout-intent",
                "profile_compare_validation",
                "--output",
                str(daily_profile_compare_path),
            )
            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
                "--output",
                str(weekly_production_path),
            )
            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
                "--input-rollout-class",
                "real_shadow_validation",
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--output",
                str(weekly_real_shadow_path),
            )

            daily_production = load_json(daily_production_path)
            daily_raw_shadow = load_json(daily_raw_shadow_path)
            daily_preview = load_json(daily_preview_path)
            daily_profile_compare = load_json(daily_profile_compare_path)
            weekly_production = load_json(weekly_production_path)
            weekly_real_shadow = load_json(weekly_real_shadow_path)

            if build_semantic_view(daily_production) != build_semantic_view(
                daily_raw_shadow
            ):
                raise RuntimeError(
                    "scheduled daily raw-shadow rollout drifted from production semantics"
                )
            if build_semantic_view(weekly_production) != build_semantic_view(
                weekly_real_shadow
            ):
                raise RuntimeError(
                    "scheduled weekly real-shadow rollout drifted from production semantics"
                )
            if build_semantic_view(daily_production) != build_semantic_view(
                daily_preview
            ):
                raise RuntimeError(
                    "scheduled daily preview-validation rollout drifted from production semantics"
                )
            if build_semantic_view(daily_production) != build_semantic_view(
                daily_profile_compare
            ):
                raise RuntimeError(
                    "scheduled daily profile-compare rollout drifted from production semantics"
                )

            if (
                daily_raw_shadow["generatedFrom"].get("optimizerInputSourceLane")
                != "sample_raw_shadow"
            ):
                raise RuntimeError(
                    "scheduled daily raw-shadow rollout did not resolve sample_raw_shadow"
                )
            if (
                daily_raw_shadow["generatedFrom"].get("optimizerInputRolloutClass")
                != "raw_shadow_validation"
            ):
                raise RuntimeError(
                    "scheduled daily raw-shadow rollout did not record raw_shadow_validation"
                )
            if (
                daily_raw_shadow["generatedFrom"].get(
                    "optimizerJobSchedulerRolloutIntent"
                )
                != "raw_shadow_validation"
            ):
                raise RuntimeError(
                    "scheduled daily raw-shadow rollout did not record raw_shadow_validation scheduler intent"
                )
            if (
                weekly_real_shadow["generatedFrom"].get("optimizerInputSourceLane")
                != "real_provider_shadow"
            ):
                raise RuntimeError(
                    "scheduled weekly real-shadow rollout did not resolve real_provider_shadow"
                )
            if (
                weekly_real_shadow["generatedFrom"].get("optimizerInputRolloutClass")
                != "real_shadow_validation"
            ):
                raise RuntimeError(
                    "scheduled weekly real-shadow rollout did not record real_shadow_validation"
                )
            if (
                weekly_real_shadow["generatedFrom"].get(
                    "optimizerJobSchedulerRolloutIntent"
                )
                != "real_provider_shadow_validation"
            ):
                raise RuntimeError(
                    "scheduled weekly real-shadow rollout did not record real_provider_shadow_validation scheduler intent"
                )
            if (
                weekly_real_shadow["generatedFrom"].get(
                    "optimizerInputSourceProviderClass"
                )
                != "artifact_catalog_service"
            ):
                raise RuntimeError(
                    "scheduled weekly real-shadow rollout did not preserve provider-backed source class provenance"
                )
            if (
                weekly_real_shadow["generatedFrom"].get(
                    "optimizerInputArtifactLocatorKind"
                )
                != "provider_locator"
            ):
                raise RuntimeError(
                    "scheduled weekly real-shadow rollout did not preserve artifact locator provenance"
                )
            if (
                daily_preview["generatedFrom"].get(
                    "optimizerJobSchedulerRolloutIntent"
                )
                != "preview_validation"
            ):
                raise RuntimeError(
                    "scheduled daily preview-validation rollout did not record preview_validation scheduler intent"
                )
            if (
                daily_preview["generatedFrom"].get(
                    "optimizerJobRuntimeProfileRolloutClass"
                )
                != "preview_canary"
            ):
                raise RuntimeError(
                    "scheduled daily preview-validation rollout did not resolve preview_canary runtime profile"
                )
            if (
                daily_preview["generatedFrom"].get("optimizerJobWindowSetPurpose")
                != "preview_validation"
            ):
                raise RuntimeError(
                    "scheduled daily preview-validation rollout did not preserve preview window-set purpose"
                )
            if (
                daily_preview["generatedFrom"].get("optimizerJobComparisonDimension")
                != "historyBatchLabel"
            ):
                raise RuntimeError(
                    "scheduled daily preview-validation rollout did not preserve historyBatchLabel comparison dimension"
                )
            if (
                daily_profile_compare["generatedFrom"].get(
                    "optimizerJobSchedulerRolloutIntent"
                )
                != "profile_compare_validation"
            ):
                raise RuntimeError(
                    "scheduled daily profile-compare rollout did not record profile_compare_validation scheduler intent"
                )
            if (
                daily_profile_compare["generatedFrom"].get(
                    "optimizerJobRuntimeProfileRolloutClass"
                )
                != "preview_canary"
            ):
                raise RuntimeError(
                    "scheduled daily profile-compare rollout did not resolve preview_canary runtime profile"
                )
            if (
                daily_profile_compare["generatedFrom"].get(
                    "optimizerJobWindowSetPurpose"
                )
                != "profile_compare_validation"
            ):
                raise RuntimeError(
                    "scheduled daily profile-compare rollout did not preserve profile-compare window-set purpose"
                )
            if (
                daily_profile_compare["generatedFrom"].get(
                    "optimizerJobComparisonDimension"
                )
                != "rankingProfileId"
            ):
                raise RuntimeError(
                    "scheduled daily profile-compare rollout did not preserve rankingProfileId comparison dimension"
                )

        print(
            "Optimizer scheduled-job rollout classes are aligned with production semantics."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
