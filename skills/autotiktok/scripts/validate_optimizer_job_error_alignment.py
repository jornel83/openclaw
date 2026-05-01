#!/usr/bin/env python3
"""
Validate committed optimizer job-error fixture against deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_JOB_ERROR_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_error_sample.py"
)
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
COMMITTED_JOB_ERROR = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-error.sample.json"
)
INPUT_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.sample.json"
)


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-job-error-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            built_error_path = temp_root / "optimizer-job-error.json"
            emitted_error_path = temp_root / "optimizer-job-error.emitted.json"
            schedule_result = run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
                "--output",
                str(schedule_path),
            )
            if schedule_result.returncode != 0:
                raise RuntimeError(schedule_result.stderr or schedule_result.stdout)
            build_result = run_script(
                BUILD_JOB_ERROR_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--output",
                str(built_error_path),
            )
            if build_result.returncode != 0:
                raise RuntimeError(build_result.stderr or build_result.stdout)
            built_payload = load_json(built_error_path)
            committed_payload = load_json(COMMITTED_JOB_ERROR)
            if built_payload != committed_payload:
                raise RuntimeError(
                    "committed optimizer job error does not match deterministic generation"
                )
            scheduled_job_result = run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
                "--input-manifest",
                str(INPUT_MANIFEST),
                "--scheduler-run-id",
                "optimizer-scheduler.autotiktok.fixture.failure-check",
                "--scheduler-rollout-intent",
                "real_provider_shadow_validation",
                "--error-output",
                str(emitted_error_path),
            )
            if scheduled_job_result.returncode == 0:
                raise RuntimeError(
                    "scheduled weekly optimizer job should fail without a weekly review window input"
                )
            emitted_payload = load_json(emitted_error_path)
            if emitted_payload["errorCode"] != "input_resolution_failure":
                raise RuntimeError(
                    "scheduled optimizer job should classify missing weekly window as input_resolution_failure"
                )
            if emitted_payload["failureStage"] != "input_resolution":
                raise RuntimeError(
                    "scheduled optimizer job should classify missing weekly window at input_resolution stage"
                )
            if emitted_payload["retryable"] is not False:
                raise RuntimeError(
                    "scheduled optimizer job missing weekly window should not be retryable"
                )
            if emitted_payload["ownerHint"] != "input_pipeline":
                raise RuntimeError(
                    "scheduled optimizer job missing weekly window should route to input_pipeline owner"
                )
        print("Optimizer job error fixture is aligned with deterministic generation.")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
