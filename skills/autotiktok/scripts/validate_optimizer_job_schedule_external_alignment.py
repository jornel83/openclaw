#!/usr/bin/env python3
"""
Validate external-scheduler optimizer job schedule artifacts and output-root dispatch.
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
COMMITTED_EXTERNAL_JOB_SCHEDULE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.external.sample.json"
)
COMMITTED_INPUT_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.sample.json"
)
COMMITTED_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "config"
    / "optimizer-policy.v1.json"
)
COMMITTED_WEEKLY_REVIEW_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
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
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-job-schedule-external-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            generated_schedule = temp_root / "optimizer-job-schedule.external.json"
            output_root = temp_root / "scheduled-outputs"

            run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--input-manifest",
                str(COMMITTED_INPUT_MANIFEST),
                "--weekly-review-window-input",
                str(COMMITTED_WEEKLY_REVIEW_WINDOW),
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
                "--output",
                str(generated_schedule),
            )
            assert_equal(
                load_json(generated_schedule),
                load_json(COMMITTED_EXTERNAL_JOB_SCHEDULE),
                "optimizer external job schedule fixture",
            )

            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(COMMITTED_EXTERNAL_JOB_SCHEDULE),
                "--schedule-id",
                "daily_optimizer_job",
                "--input-manifest",
                str(COMMITTED_INPUT_MANIFEST),
                "--policy",
                str(COMMITTED_POLICY),
                "--output-root",
                str(output_root),
                "--scheduler-run-id",
                "cron.daily.2026-04-18",
                "--scheduler-trigger-kind",
                "cron",
                "--scheduler-owner",
                "external_scheduler",
                "--execution-environment",
                "scheduler_managed",
            )
            daily_output = (
                output_root
                / "daily_optimizer_job"
                / "optimizer-daily-job-run.autotiktok.fixture.2026-04-18.json"
            )
            if not daily_output.exists():
                raise RuntimeError(
                    "external daily optimizer job did not emit output into output_root"
                )
            daily_payload = load_json(daily_output)
            if (
                daily_payload["generatedFrom"].get("optimizerJobScheduleProfile")
                != "external_scheduler"
            ):
                raise RuntimeError(
                    "external daily optimizer job did not record external_scheduler profile"
                )
            if (
                daily_payload["generatedFrom"].get("optimizerJobOutputEmissionMode")
                != "output_root"
            ):
                raise RuntimeError(
                    "external daily optimizer job did not record output_root emission mode"
                )
            if (
                daily_payload["generatedFrom"].get("optimizerJobTriggerKind")
                != "cron"
            ):
                raise RuntimeError(
                    "external daily optimizer job did not record cron trigger kind"
                )
            if (
                daily_payload["generatedFrom"].get("optimizerJobSchedulerOwner")
                != "external_scheduler"
            ):
                raise RuntimeError(
                    "external daily optimizer job did not record external_scheduler owner"
                )
            if (
                daily_payload["generatedFrom"].get("optimizerJobExecutionEnvironment")
                != "scheduler_managed"
            ):
                raise RuntimeError(
                    "external daily optimizer job did not record scheduler_managed execution environment"
                )

            run_script(
                RUN_SCHEDULED_JOB_SCRIPT,
                "--input-schedule-plan",
                str(COMMITTED_EXTERNAL_JOB_SCHEDULE),
                "--schedule-id",
                "weekly_optimizer_job",
                "--input-manifest",
                str(COMMITTED_INPUT_MANIFEST),
                "--policy",
                str(COMMITTED_POLICY),
                "--weekly-review-window-input",
                str(COMMITTED_WEEKLY_REVIEW_WINDOW),
                "--output-root",
                str(output_root),
                "--scheduler-run-id",
                "cron.weekly.2026-04-18",
                "--scheduler-trigger-kind",
                "planner",
                "--scheduler-owner",
                "external_scheduler",
                "--execution-environment",
                "scheduler_managed",
            )
            weekly_output = (
                output_root
                / "weekly_optimizer_job"
                / "optimizer-weekly-job-run.autotiktok.fixture.2026-04-18.json"
            )
            if not weekly_output.exists():
                raise RuntimeError(
                    "external weekly optimizer job did not emit output into output_root"
                )
            weekly_payload = load_json(weekly_output)
            if (
                weekly_payload["generatedFrom"].get("optimizerJobScheduleProfile")
                != "external_scheduler"
            ):
                raise RuntimeError(
                    "external weekly optimizer job did not record external_scheduler profile"
                )
            if (
                weekly_payload["generatedFrom"].get("optimizerJobOutputEmissionMode")
                != "output_root"
            ):
                raise RuntimeError(
                    "external weekly optimizer job did not record output_root emission mode"
                )
            if (
                weekly_payload["generatedFrom"].get("optimizerJobTriggerKind")
                != "planner"
            ):
                raise RuntimeError(
                    "external weekly optimizer job did not record planner trigger kind"
                )
            if (
                weekly_payload["generatedFrom"].get("optimizerJobSchedulerOwner")
                != "external_scheduler"
            ):
                raise RuntimeError(
                    "external weekly optimizer job did not record external_scheduler owner"
                )
            if (
                weekly_payload["generatedFrom"].get("optimizerJobExecutionEnvironment")
                != "scheduler_managed"
            ):
                raise RuntimeError(
                    "external weekly optimizer job did not record scheduler_managed execution environment"
                )

        print(
            "External optimizer job schedule fixture and output-root dispatch are aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
