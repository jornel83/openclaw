#!/usr/bin/env python3
"""
Validate committed optimizer job shadow-compare artifacts against deterministic generation.
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
BUILD_JOB_SHADOW_COMPARE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare.py"
)
BUILD_JOB_SHADOW_COMPARE_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_plan.py"
)
COMMITTED_COMPARE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare.sample.json"
)
COMMITTED_COMPARE_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.sample.json"
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
            prefix="autotiktok-job-shadow-compare-alignment-"
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

            generated_plan = load_json(compare_plan_path)
            committed_plan = load_json(COMMITTED_COMPARE_PLAN)
            if generated_plan != committed_plan:
                raise RuntimeError(
                    "committed optimizer job shadow compare plan does not match deterministic generation"
                )

            generated = load_json(compare_path)
            committed = load_json(COMMITTED_COMPARE)
            if generated != committed:
                raise RuntimeError(
                    "committed optimizer job shadow compare does not match deterministic generation"
                )

            if generated["summary"]["matchedComparisonCount"] != generated["summary"][
                "comparisonCount"
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare should have all comparisons matched"
                )

            comparisons = {
                entry["comparisonId"]: entry for entry in generated["comparisons"]
            }
            if sorted(comparisons) != [
                "daily_preview_validation_vs_production",
                "daily_profile_compare_validation_vs_production",
                "daily_raw_shadow_vs_production",
                "weekly_real_shadow_vs_production",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare should materialize raw-shadow, real-shadow, preview-validation, and profile-compare comparisons"
                )
            daily_entry = comparisons["daily_raw_shadow_vs_production"]
            if (
                daily_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceLane"
                )
                != "sample_raw_shadow"
            ):
                raise RuntimeError(
                    "daily raw-shadow compare should resolve sample_raw_shadow"
                )
            if (
                daily_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceProviderRegistryId"
                )
                is not None
            ):
                raise RuntimeError(
                    "daily raw-shadow compare should not resolve provider-registry provenance"
                )
            if (
                daily_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceArtifactCatalogId"
                )
                is not None
            ):
                raise RuntimeError(
                    "daily raw-shadow compare should not resolve source-artifact-catalog provenance"
                )

            weekly_entry = comparisons["weekly_real_shadow_vs_production"]
            if (
                weekly_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceLane"
                )
                != "real_provider_shadow"
            ):
                raise RuntimeError(
                    "weekly real-shadow compare should resolve real_provider_shadow"
                )
            if (
                weekly_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceProviderRegistryId"
                )
                != "optimizer-source-provider-registry.autotiktok.fixture.2026-04-18"
            ):
                raise RuntimeError(
                    "weekly real-shadow compare should preserve provider-registry provenance"
                )
            if (
                weekly_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceArtifactCatalogId"
                )
                != "optimizer-source-artifact-catalog.autotiktok.fixture.2026-04-18"
            ):
                raise RuntimeError(
                    "weekly real-shadow compare should preserve source-artifact-catalog provenance"
                )
            if (
                weekly_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputSourceProviderClass"
                )
                != "artifact_catalog_service"
            ):
                raise RuntimeError(
                    "weekly real-shadow compare should preserve provider-backed source class provenance"
                )
            if (
                weekly_entry["candidate"]["inputProvenance"].get(
                    "optimizerInputArtifactLocatorKind"
                )
                != "provider_locator"
            ):
                raise RuntimeError(
                    "weekly real-shadow compare should preserve provider-backed artifact locator provenance"
                )

            preview_entry = comparisons["daily_preview_validation_vs_production"]
            if preview_entry["baseline"].get("schedulerRolloutIntent") != "production":
                raise RuntimeError(
                    "daily preview-validation compare baseline should remain production"
                )
            if (
                preview_entry["candidate"].get("schedulerRolloutIntent")
                != "preview_validation"
            ):
                raise RuntimeError(
                    "daily preview-validation compare candidate should resolve preview_validation"
                )
            if (
                preview_entry["candidate"].get("runtimeProfileRolloutClass")
                != "preview_canary"
            ):
                raise RuntimeError(
                    "daily preview-validation compare should preserve preview_canary runtime profile rollout class"
                )
            if (
                preview_entry["candidate"].get("windowSetPurpose")
                != "preview_validation"
            ):
                raise RuntimeError(
                    "daily preview-validation compare should preserve preview_validation window-set purpose"
                )
            if (
                preview_entry["candidate"].get("comparisonDimension")
                != "historyBatchLabel"
            ):
                raise RuntimeError(
                    "daily preview-validation compare should preserve historyBatchLabel comparison dimension"
                )

            profile_compare_entry = comparisons[
                "daily_profile_compare_validation_vs_production"
            ]
            if (
                profile_compare_entry["baseline"].get("schedulerRolloutIntent")
                != "production"
            ):
                raise RuntimeError(
                    "daily profile-compare compare baseline should remain production"
                )
            if (
                profile_compare_entry["candidate"].get("schedulerRolloutIntent")
                != "profile_compare_validation"
            ):
                raise RuntimeError(
                    "daily profile-compare compare candidate should resolve profile_compare_validation"
                )
            if (
                profile_compare_entry["candidate"].get(
                    "runtimeProfileRolloutClass"
                )
                != "preview_canary"
            ):
                raise RuntimeError(
                    "daily profile-compare compare should preserve preview_canary runtime profile rollout class"
                )
            if (
                profile_compare_entry["candidate"].get("windowSetPurpose")
                != "profile_compare_validation"
            ):
                raise RuntimeError(
                    "daily profile-compare compare should preserve profile_compare_validation window-set purpose"
                )
            if (
                profile_compare_entry["candidate"].get("comparisonDimension")
                != "rankingProfileId"
            ):
                raise RuntimeError(
                    "daily profile-compare compare should preserve rankingProfileId comparison dimension"
                )

        print(
            "Optimizer job shadow compare plan and compare artifact are aligned with deterministic scheduler generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
