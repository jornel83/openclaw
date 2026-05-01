#!/usr/bin/env python3
"""
Validate the preferred OpenClaw cron runtime artifacts and entrypoints.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_OPENCLAW_CRON_CONTRACT_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_openclaw_cron_contract.py"
)
COMMITTED_OPENCLAW_CRON_CONTRACT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-openclaw-cron-contract.sample.json"
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


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
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
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_equal(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{label} drifted from deterministic generation")


def validate_entrypoint_summary(
    *,
    stdout: str,
    expected_payload: dict[str, Any],
    output_path: Path,
) -> None:
    expected_lines = {
        "status=ok",
        f"job_kind={expected_payload['jobKind']}",
        f"job_run_id={expected_payload['jobRunId']}",
        f"output={output_path}",
        f"ranking_run_id={expected_payload['summary']['rankingRunId']}",
        f"ranking_profile_id={expected_payload['summary']['rankingProfileId']}",
        f"daily_recommendation={expected_payload['summary']['dailyRecommendation']}",
        (
            "shadow_leader_profile_id="
            f"{expected_payload['summary']['shadowLeaderProfileId']}"
        ),
    }
    output_lines = set(stdout.strip().splitlines())
    missing = expected_lines - output_lines
    if missing:
        raise RuntimeError(
            "OpenClaw cron entrypoint summary is missing expected lines: "
            + ", ".join(sorted(missing))
        )
    weekly_decision = expected_payload["summary"].get("weeklyDecision")
    if weekly_decision is not None and f"weekly_decision={weekly_decision}" not in output_lines:
        raise RuntimeError("weekly OpenClaw cron entrypoint did not print weekly_decision")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-openclaw-cron-runtime-alignment-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            generated_contract = temp_root / "optimizer-openclaw-cron-contract.json"
            run_script(
                BUILD_OPENCLAW_CRON_CONTRACT_SCRIPT,
                "--output",
                str(generated_contract),
            )
            committed_contract = load_json(COMMITTED_OPENCLAW_CRON_CONTRACT)
            assert_equal(
                load_json(generated_contract),
                committed_contract,
                "optimizer OpenClaw cron contract fixture",
            )

            jobs_by_name = {
                job["jobName"]: job for job in committed_contract["jobs"]
            }
            expected_jobs = {
                "autotiktok:daily-optimizer": load_json(COMMITTED_DAILY_JOB_RUN),
                "autotiktok:weekly-optimizer": load_json(COMMITTED_WEEKLY_JOB_RUN),
            }
            if set(jobs_by_name) != set(expected_jobs):
                raise RuntimeError(
                    "optimizer OpenClaw cron contract should expose daily and weekly stable job names"
                )

            for job_name, expected_payload in expected_jobs.items():
                job = jobs_by_name[job_name]
                entry_script = ROOT / job["entryScriptPath"]
                if not entry_script.exists():
                    raise RuntimeError(
                        f"OpenClaw cron entrypoint {job['entryScriptPath']} does not exist"
                    )
                output_root = temp_root / job_name.replace(":", "-")
                result = run_script(
                    entry_script,
                    "--output-root",
                    str(output_root),
                )
                output_path = output_root / f"{expected_payload['jobRunId']}.json"
                if not output_path.exists():
                    raise RuntimeError(
                        f"{job_name} did not emit {expected_payload['jobRunId']}.json into output_root"
                    )
                assert_equal(
                    load_json(output_path),
                    expected_payload,
                    f"{job_name} OpenClaw cron runtime output",
                )
                validate_entrypoint_summary(
                    stdout=result.stdout,
                    expected_payload=expected_payload,
                    output_path=output_path,
                )

        print(
            "Optimizer OpenClaw cron contract and preferred runtime entrypoints are aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
