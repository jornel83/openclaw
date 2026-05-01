#!/usr/bin/env python3
"""
Validate committed optimizer job orchestration-cycle artifact against deterministic generation.
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
COMMITTED_JOB_ORCHESTRATION_CYCLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-orchestration-cycle.sample.json"
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
            prefix="autotiktok-job-orchestration-cycle-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
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
            payload = load_json(cycle_path)
            if payload != load_json(COMMITTED_JOB_ORCHESTRATION_CYCLE):
                raise RuntimeError(
                    "committed optimizer job orchestration cycle does not match deterministic generation"
                )
            if payload["summary"]["jobRunCount"] != 4:
                raise RuntimeError(
                    "optimizer job orchestration cycle should materialize four job runs"
                )
            if payload["summary"]["shadowComparedScheduleCount"] != 2:
                raise RuntimeError(
                    "optimizer job orchestration cycle should shadow-compare two schedules"
                )
            if payload["summary"]["compareBatchCount"] != 1:
                raise RuntimeError(
                    "optimizer job orchestration cycle should emit one compare batch"
                )
            run_summary = payload["artifacts"].get("runSummary")
            if not isinstance(run_summary, dict):
                raise RuntimeError(
                    "optimizer job orchestration cycle should embed a runSummary artifact"
                )
            if run_summary.get("summary", {}).get("runStatus") != "success":
                raise RuntimeError(
                    "optimizer job orchestration cycle embedded run summary should report success"
                )
            if run_summary.get("summary", {}).get("jobRunCount") != 4:
                raise RuntimeError(
                    "optimizer job orchestration cycle embedded run summary should summarize four job runs"
                )
            if (
                payload["summary"]["retentionPolicyId"]
                != "optimizer-job-artifact-retention-policy.autotiktok.fixture.2026-04-19"
            ):
                raise RuntimeError(
                    "optimizer job orchestration cycle should preserve artifact retention policy provenance"
                )
        print(
            "Optimizer job orchestration cycle fixture is aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
