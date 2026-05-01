#!/usr/bin/env python3
"""
Validate preview/profile-compare scheduler cutover lanes in optimizer job shadow compares.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_INPUT_ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_rollout_policy.py"
)
BUILD_JOB_SCHEDULE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_schedule.py"
)
BUILD_JOB_SHADOW_COMPARE_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_plan.py"
)
BUILD_JOB_SHADOW_COMPARE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare.py"
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


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-job-shadow-compare-cutover-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            schedule_path = temp_root / "optimizer-job-schedule.json"
            compare_plan_path = temp_root / "optimizer-job-shadow-compare-plan.json"
            compare_path = temp_root / "optimizer-job-shadow-compare.json"

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
                BUILD_JOB_SHADOW_COMPARE_PLAN_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--output",
                str(compare_plan_path),
            )
            run_script(
                BUILD_JOB_SHADOW_COMPARE_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(compare_plan_path),
                "--output",
                str(compare_path),
            )

            payload = load_json(compare_path)
            comparisons = {
                entry["comparisonId"]: entry for entry in payload["comparisons"]
            }
            preview_entry = comparisons["daily_preview_validation_vs_production"]
            profile_entry = comparisons[
                "daily_profile_compare_validation_vs_production"
            ]

            for comparison_id, entry, expected_purpose, expected_dimension in (
                (
                    "daily_preview_validation_vs_production",
                    preview_entry,
                    "preview_validation",
                    "historyBatchLabel",
                ),
                (
                    "daily_profile_compare_validation_vs_production",
                    profile_entry,
                    "profile_compare_validation",
                    "rankingProfileId",
                ),
            ):
                if entry["baseline"]["schedulerRolloutIntent"] != "production":
                    raise RuntimeError(
                        f"{comparison_id} baseline should remain production"
                    )
                if entry["baseline"]["rolloutClass"] != "production":
                    raise RuntimeError(
                        f"{comparison_id} baseline should keep production rollout class"
                    )
                if entry["candidate"]["rolloutClass"] != "production":
                    raise RuntimeError(
                        f"{comparison_id} candidate should keep production input rollout class"
                    )
                if entry["candidate"]["runtimeProfileRolloutClass"] != "preview_canary":
                    raise RuntimeError(
                        f"{comparison_id} candidate should resolve preview_canary runtime profile"
                    )
                if entry["candidate"]["windowSetPurpose"] != expected_purpose:
                    raise RuntimeError(
                        f"{comparison_id} candidate should preserve {expected_purpose} window-set purpose"
                    )
                if entry["candidate"]["comparisonDimension"] != expected_dimension:
                    raise RuntimeError(
                        f"{comparison_id} candidate should preserve {expected_dimension} comparison dimension"
                    )
                if not entry["semanticMatch"]:
                    raise RuntimeError(
                        f"{comparison_id} should remain semantically aligned during cutover rehearsal"
                    )

            if payload["summary"]["comparedRuntimeProfileRolloutClasses"] != [
                "preview_canary",
                "production",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare should aggregate preview_canary and production runtime profile rollout classes"
                )

        print(
            "Optimizer job shadow compare cutover lanes are aligned with preview/profile-compare scheduler intent semantics."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
