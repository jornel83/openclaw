#!/usr/bin/env python3
"""
Validate committed optimizer recent compare summaries artifact against deterministic generation.
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
BUILD_JOB_EXECUTION_CONTEXT_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_execution_context.py"
)
BUILD_RETENTION_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_artifact_retention_policy.py"
)
RUN_JOB_ORCHESTRATION_CYCLE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_optimizer_job_orchestration_cycle.py"
)
BUILD_COMPARE_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_plan.py"
)
BUILD_COMPARE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare.py"
)
BUILD_COMPARE_BATCH_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_batch_manifest.py"
)
BUILD_COMPARE_BATCH_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_batch.py"
)
BUILD_RECENT_COMPARE_SUMMARIES_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_recent_compare_summaries.py"
)
COMMITTED_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-compare-summaries.sample.json"
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
            prefix="autotiktok-recent-compare-summaries-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            replay_schedule_path = temp_root / "optimizer-job-schedule.json"
            external_schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = temp_root / "optimizer-job-execution-context.json"
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            daily_plan_path = temp_root / "optimizer-job-shadow-compare-plan.daily.json"
            weekly_plan_path = (
                temp_root / "optimizer-job-shadow-compare-plan.weekly.json"
            )
            daily_compare_path = temp_root / "optimizer-job-shadow-compare.daily.json"
            weekly_compare_path = (
                temp_root / "optimizer-job-shadow-compare.weekly.json"
            )
            compare_batch_manifest_path = (
                temp_root / "optimizer-job-shadow-compare-batch-manifest.json"
            )
            compare_batch_path = (
                temp_root / "optimizer-job-shadow-compare-batch.json"
            )
            aggregate_path = temp_root / "optimizer-recent-compare-summaries.json"

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
                str(replay_schedule_path),
            )
            run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
                "--output",
                str(external_schedule_path),
            )
            run_script(
                BUILD_JOB_EXECUTION_CONTEXT_SCRIPT,
                "--input-schedule-plan",
                str(external_schedule_path),
                "--output",
                str(execution_context_path),
            )
            run_script(
                BUILD_RETENTION_POLICY_SCRIPT,
                "--output",
                str(retention_policy_path),
            )
            run_script(
                RUN_JOB_ORCHESTRATION_CYCLE_SCRIPT,
                "--input-schedule-plan",
                str(external_schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
                "--output",
                str(cycle_path),
            )
            run_script(
                BUILD_COMPARE_PLAN_SCRIPT,
                "--input-schedule-plan",
                str(replay_schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "daily",
                "--output",
                str(daily_plan_path),
            )
            run_script(
                BUILD_COMPARE_PLAN_SCRIPT,
                "--input-schedule-plan",
                str(replay_schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "weekly",
                "--output",
                str(weekly_plan_path),
            )
            run_script(
                BUILD_COMPARE_SCRIPT,
                "--input-schedule-plan",
                str(replay_schedule_path),
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
                BUILD_COMPARE_SCRIPT,
                "--input-schedule-plan",
                str(replay_schedule_path),
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
                BUILD_COMPARE_BATCH_MANIFEST_SCRIPT,
                "--input-compare-artifact",
                str(daily_compare_path),
                "--input-compare-artifact",
                str(weekly_compare_path),
                "--output",
                str(compare_batch_manifest_path),
            )
            run_script(
                BUILD_COMPARE_BATCH_SCRIPT,
                "--input-batch-manifest",
                str(compare_batch_manifest_path),
                "--output",
                str(compare_batch_path),
            )
            run_script(
                BUILD_RECENT_COMPARE_SUMMARIES_SCRIPT,
                "--input-job-shadow-compare-batch",
                str(compare_batch_path),
                "--input-job-orchestration-cycle",
                str(cycle_path),
                "--output",
                str(aggregate_path),
            )
            payload = load_json(aggregate_path)
            committed = load_json(COMMITTED_OUTPUT)
            if payload != committed:
                raise RuntimeError(
                    "committed optimizer recent compare summaries do not match deterministic generation"
                )
            if payload["summary"]["compareBatchCount"] != 2:
                raise RuntimeError(
                    "optimizer recent compare summaries should aggregate two compare batches"
                )
            if payload["summary"]["comparisonCount"] != 6:
                raise RuntimeError(
                    "optimizer recent compare summaries should aggregate six comparisons"
                )
            if payload["summary"]["groupEntryCount"] != 6:
                raise RuntimeError(
                    "optimizer recent compare summaries should flatten six group entries"
                )
        print(
            "Optimizer recent compare summaries fixture is aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
