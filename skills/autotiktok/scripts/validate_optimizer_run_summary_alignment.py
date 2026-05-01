#!/usr/bin/env python3
"""
Validate committed optimizer run-summary artifact against deterministic generation.
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
BUILD_RUN_SUMMARY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_run_summary.py"
)
COMMITTED_RUN_SUMMARY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-run-summary.sample.json"
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
            prefix="autotiktok-run-summary-alignment-"
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
            embedded_summary_path = temp_root / "optimizer-run-summary.embedded.json"
            rebuilt_summary_path = temp_root / "optimizer-run-summary.rebuilt.json"
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
                "--run-summary-output",
                str(embedded_summary_path),
                "--output",
                str(cycle_path),
            )
            run_script(
                BUILD_RUN_SUMMARY_SCRIPT,
                "--input-job-orchestration-cycle",
                str(cycle_path),
                "--output",
                str(rebuilt_summary_path),
            )
            embedded_payload = load_json(embedded_summary_path)
            rebuilt_payload = load_json(rebuilt_summary_path)
            committed_payload = load_json(COMMITTED_RUN_SUMMARY)
            if embedded_payload != rebuilt_payload:
                raise RuntimeError(
                    "optimizer run summary rebuilt from orchestration cycle does not match the embedded run summary"
                )
            if embedded_payload != committed_payload:
                raise RuntimeError(
                    "committed optimizer run summary does not match deterministic generation"
                )
            if embedded_payload["summary"]["runStatus"] != "success":
                raise RuntimeError(
                    "optimizer run summary should report a successful orchestration cycle"
                )
            if embedded_payload["summary"]["scheduleCount"] != 2:
                raise RuntimeError(
                    "optimizer run summary should summarize two schedules"
                )
            if embedded_payload["summary"]["jobRunCount"] != 4:
                raise RuntimeError(
                    "optimizer run summary should summarize four job runs"
                )
            if embedded_payload["summary"]["compareArtifactCount"] != 1:
                raise RuntimeError(
                    "optimizer run summary should summarize one compare artifact"
                )
            if embedded_payload["summary"]["compareBatchCount"] != 1:
                raise RuntimeError(
                    "optimizer run summary should summarize one compare batch"
                )
            if (
                embedded_payload["summary"]["retentionPolicyId"]
                != "optimizer-job-artifact-retention-policy.autotiktok.fixture.2026-04-19"
            ):
                raise RuntimeError(
                    "optimizer run summary should preserve artifact retention policy provenance"
                )
        print("Optimizer run summary fixture is aligned with deterministic generation.")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
