#!/usr/bin/env python3
"""
Validate committed optimizer recent failure summaries artifact against deterministic generation.
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
BUILD_JOB_ERROR_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_error_sample.py"
)
BUILD_RECENT_FAILURE_SUMMARIES_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_recent_failure_summaries.py"
)
COMMITTED_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-failure-summaries.sample.json"
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
            prefix="autotiktok-recent-failure-summaries-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = temp_root / "optimizer-job-execution-context.json"
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            error_path = temp_root / "optimizer-job-error.json"
            aggregate_path = temp_root / "optimizer-recent-failure-summaries.json"
            run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
                "--output",
                str(schedule_path),
            )
            run_script(
                BUILD_JOB_EXECUTION_CONTEXT_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
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
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
                "--output",
                str(cycle_path),
            )
            run_script(
                BUILD_JOB_ERROR_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--output",
                str(error_path),
            )
            run_script(
                BUILD_RECENT_FAILURE_SUMMARIES_SCRIPT,
                "--input-job-error",
                str(error_path),
                "--input-job-orchestration-cycle",
                str(cycle_path),
                "--output",
                str(aggregate_path),
            )
            payload = load_json(aggregate_path)
            committed = load_json(COMMITTED_OUTPUT)
            if payload != committed:
                raise RuntimeError(
                    "committed optimizer recent failure summaries do not match deterministic generation"
                )
            if payload["summary"]["failureCount"] != 1:
                raise RuntimeError(
                    "optimizer recent failure summaries should aggregate one committed error"
                )
            if payload["summary"]["retryableCount"] != 0:
                raise RuntimeError(
                    "optimizer recent failure summaries should keep the committed sample non-retryable"
                )
            if payload["summary"]["ownerHintCounts"] != {"input_pipeline": 1}:
                raise RuntimeError(
                    "optimizer recent failure summaries should preserve the committed owner hint counts"
                )
        print(
            "Optimizer recent failure summaries fixture is aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
