#!/usr/bin/env python3
"""
Validate committed optimizer job shadow-compare batch artifacts against deterministic generation.
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
BUILD_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_batch_manifest.py"
)
BUILD_JOB_SHADOW_COMPARE_BATCH_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_batch.py"
)
COMMITTED_DAILY_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.daily.sample.json"
)
COMMITTED_WEEKLY_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.weekly.sample.json"
)
COMMITTED_DAILY_COMPARE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare.daily.sample.json"
)
COMMITTED_WEEKLY_COMPARE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare.weekly.sample.json"
)
COMMITTED_BATCH_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch-manifest.sample.json"
)
COMMITTED_BATCH = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch.sample.json"
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
            prefix="autotiktok-job-shadow-compare-batch-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            schedule_path = temp_root / "optimizer-job-schedule.json"
            daily_plan_path = temp_root / "optimizer-job-shadow-compare-plan.daily.json"
            weekly_plan_path = temp_root / "optimizer-job-shadow-compare-plan.weekly.json"
            daily_compare_path = temp_root / "optimizer-job-shadow-compare.daily.json"
            weekly_compare_path = temp_root / "optimizer-job-shadow-compare.weekly.json"
            batch_manifest_path = (
                temp_root / "optimizer-job-shadow-compare-batch-manifest.json"
            )
            batch_path = temp_root / "optimizer-job-shadow-compare-batch.json"

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
                "--comparison-scope",
                "daily",
                "--compare-plan-id",
                "optimizer-job-shadow-compare-plan.daily.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:41:00Z",
                "--output",
                str(daily_plan_path),
            )
            run_script(
                BUILD_JOB_SHADOW_COMPARE_PLAN_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "weekly",
                "--compare-plan-id",
                "optimizer-job-shadow-compare-plan.weekly.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:42:00Z",
                "--output",
                str(weekly_plan_path),
            )
            run_script(
                BUILD_JOB_SHADOW_COMPARE_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(daily_plan_path),
                "--compare-id",
                "optimizer-job-shadow-compare.daily.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:46:00Z",
                "--output",
                str(daily_compare_path),
            )
            run_script(
                BUILD_JOB_SHADOW_COMPARE_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(weekly_plan_path),
                "--compare-id",
                "optimizer-job-shadow-compare.weekly.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:47:00Z",
                "--output",
                str(weekly_compare_path),
            )
            run_script(
                BUILD_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCRIPT,
                "--input-compare-artifact",
                str(COMMITTED_DAILY_COMPARE),
                "--input-compare-artifact",
                str(COMMITTED_WEEKLY_COMPARE),
                "--output",
                str(batch_manifest_path),
            )
            run_script(
                BUILD_JOB_SHADOW_COMPARE_BATCH_SCRIPT,
                "--input-batch-manifest",
                str(batch_manifest_path),
                "--output",
                str(batch_path),
            )

            if load_json(daily_plan_path) != load_json(COMMITTED_DAILY_PLAN):
                raise RuntimeError(
                    "committed daily optimizer job shadow compare plan does not match deterministic generation"
                )
            if load_json(weekly_plan_path) != load_json(COMMITTED_WEEKLY_PLAN):
                raise RuntimeError(
                    "committed weekly optimizer job shadow compare plan does not match deterministic generation"
                )
            if load_json(daily_compare_path) != load_json(COMMITTED_DAILY_COMPARE):
                raise RuntimeError(
                    "committed daily optimizer job shadow compare does not match deterministic generation"
                )
            if load_json(weekly_compare_path) != load_json(COMMITTED_WEEKLY_COMPARE):
                raise RuntimeError(
                    "committed weekly optimizer job shadow compare does not match deterministic generation"
                )
            if load_json(batch_manifest_path) != load_json(COMMITTED_BATCH_MANIFEST):
                raise RuntimeError(
                    "committed optimizer job shadow compare batch manifest does not match deterministic generation"
                )
            batch_payload = load_json(batch_path)
            if batch_payload != load_json(COMMITTED_BATCH):
                raise RuntimeError(
                    "committed optimizer job shadow compare batch does not match deterministic generation"
                )
            summary = batch_payload["summary"]
            if summary["compareArtifactCount"] != 2:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate two compare artifacts"
                )
            if summary["comparisonCount"] != 4:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate four comparisons"
                )
            if summary["matchedComparisonCount"] != 4:
                raise RuntimeError(
                    "optimizer job shadow compare batch should have all comparisons matched"
                )
            if summary["comparedScheduleIds"] != [
                "daily_optimizer_job",
                "weekly_optimizer_job",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate daily and weekly scheduleIds"
                )
            if summary["comparedCandidateRolloutClasses"] != [
                "production",
                "raw_shadow_validation",
                "real_shadow_validation",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate production, raw-shadow, and real-shadow rollout classes"
                )
            if summary["comparedCandidateSchedulerRolloutIntents"] != [
                "preview_validation",
                "profile_compare_validation",
                "raw_shadow_validation",
                "real_provider_shadow_validation",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate raw-shadow, real-shadow, preview-validation, and profile-compare scheduler rollout intents"
                )
            if summary["comparedCandidateSourceLanes"] != [
                "real_provider_shadow",
                "sample_canonical",
                "sample_raw_shadow",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate canonical, raw-shadow, and real-shadow source lanes"
                )
            if summary["comparisonDimension"] != "candidateSchedulerRolloutIntent":
                raise RuntimeError(
                    "optimizer job shadow compare batch should group by candidateSchedulerRolloutIntent"
                )
            if summary["comparedCandidateRuntimeProfileRolloutClasses"] != [
                "preview_canary",
                "production",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate production and preview_canary runtime profile rollout classes"
                )
            if summary["comparedCandidateWindowSetPurposes"] != [
                "preview_validation",
                "profile_compare_validation",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate preview-validation and profile-compare window-set purposes"
                )
            if summary["comparedCandidateComparisonDimensions"] != [
                "historyBatchLabel",
                "rankingProfileId",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should aggregate historyBatchLabel and rankingProfileId comparison dimensions"
                )
            group_values = [item["groupValue"] for item in batch_payload["groupSummaries"]]
            if group_values != [
                "preview_validation",
                "profile_compare_validation",
                "raw_shadow_validation",
                "real_provider_shadow_validation",
            ]:
                raise RuntimeError(
                    "optimizer job shadow compare batch should emit one group per candidate scheduler rollout intent"
                )

        print(
            "Optimizer job shadow compare batch artifacts are aligned with deterministic scheduler generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
