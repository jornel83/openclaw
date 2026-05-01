#!/usr/bin/env python3
"""
Validate scheduler-facing optimizer job schedule artifacts and scheduled-job dispatch.
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
COMMITTED_JOB_SCHEDULE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json"
)
COMMITTED_DAILY_JOB_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-daily-job-run.sample.json"
)
COMMITTED_WEEKLY_JOB_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-job-run.sample.json"
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


def assert_equal(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{label} drifted from deterministic generation")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-job-schedule-alignment-") as temp_dir:
            temp_root = Path(temp_dir)
            generated_schedule = temp_root / "optimizer-job-schedule.json"
            generated_daily_job = temp_root / "optimizer-daily-job-run.json"
            generated_weekly_job = temp_root / "optimizer-weekly-job-run.json"

            run_script(BUILD_JOB_SCHEDULE_SCRIPT, "--output", str(generated_schedule))
            assert_equal(
                load_json(generated_schedule),
                load_json(COMMITTED_JOB_SCHEDULE),
                "optimizer job schedule fixture",
            )

            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(COMMITTED_JOB_SCHEDULE),
                "--schedule-id",
                "daily_optimizer_job",
                "--output",
                str(generated_daily_job),
            )
            assert_equal(
                load_json(generated_daily_job),
                load_json(COMMITTED_DAILY_JOB_RUN),
                "scheduled daily optimizer job run",
            )

            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(COMMITTED_JOB_SCHEDULE),
                "--schedule-id",
                "weekly_optimizer_job",
                "--output",
                str(generated_weekly_job),
            )
            assert_equal(
                load_json(generated_weekly_job),
                load_json(COMMITTED_WEEKLY_JOB_RUN),
                "scheduled weekly optimizer job run",
            )

        print(
            "Optimizer job schedule plan and scheduled-job dispatch are aligned with "
            "deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
