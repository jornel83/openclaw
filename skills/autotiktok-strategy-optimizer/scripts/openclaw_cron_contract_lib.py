#!/usr/bin/env python3
"""
Standard OpenClaw cron contract helpers for AutoTikTok optimizer jobs.
"""

from __future__ import annotations

from pathlib import Path
import shlex
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

OPENCLAW_CRON_CONTRACT_SCHEMA_VERSION = "optimizer-openclaw-cron-contract.sample.v1"
OPENCLAW_CRON_CONTRACT_ID = "optimizer-openclaw-cron-contract.autotiktok.fixture.2026-04-21"
OPENCLAW_CRON_DEFAULT_GENERATED_AT = "2026-04-21T12:00:00Z"

DAILY_OPENCLAW_CRON_JOB_NAME = "autotiktok:daily-optimizer"
WEEKLY_OPENCLAW_CRON_JOB_NAME = "autotiktok:weekly-optimizer"

OPENCLAW_CRON_DEFAULT_SESSION_TARGET = "isolated"
OPENCLAW_CRON_DEFAULT_DELIVERY_MODE = "none"
OPENCLAW_CRON_DEFAULT_TOOLS_ALLOW = ["exec", "read", "write"]


def _render_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _build_openclaw_cron_add_args(job: dict[str, Any]) -> list[str]:
    return [
        "openclaw",
        "cron",
        "add",
        "--name",
        str(job["jobName"]),
        "--cron",
        str(job["schedule"]["expr"]),
        "--tz",
        str(job["schedule"]["tz"]),
        "--session",
        str(job["sessionTarget"]),
        "--message",
        str(job["cronPrompt"]),
        "--tools",
        ",".join(job["toolsAllow"]),
        "--light-context",
        "--no-deliver",
    ]


def _build_openclaw_cron_edit_args(job: dict[str, Any]) -> list[str]:
    return [
        "openclaw",
        "cron",
        "edit",
        "<job-id>",
        "--cron",
        str(job["schedule"]["expr"]),
        "--tz",
        str(job["schedule"]["tz"]),
        "--session",
        str(job["sessionTarget"]),
        "--message",
        str(job["cronPrompt"]),
        "--tools",
        ",".join(job["toolsAllow"]),
        "--light-context",
        "--no-deliver",
    ]


def _build_job(
    *,
    job_id: str,
    job_name: str,
    cron_expr: str,
    cron_tz: str,
    entry_script_path: Path,
    cron_prompt: str,
) -> dict[str, Any]:
    job: dict[str, Any] = {
        "jobId": job_id,
        "jobName": job_name,
        "schedule": {
            "kind": "cron",
            "expr": cron_expr,
            "tz": cron_tz,
        },
        "sessionTarget": OPENCLAW_CRON_DEFAULT_SESSION_TARGET,
        "deliveryMode": OPENCLAW_CRON_DEFAULT_DELIVERY_MODE,
        "lightContext": True,
        "toolsAllow": list(OPENCLAW_CRON_DEFAULT_TOOLS_ALLOW),
        "entryScriptPath": _render_repo_relative(entry_script_path),
        "cronPrompt": cron_prompt,
        "management": {
            "listFirst": True,
            "matchMode": "exact_name",
            "createCommand": "openclaw cron add",
            "updateCommand": "openclaw cron edit",
        },
    }
    job["cliTemplates"] = {
        "add": shlex.join(_build_openclaw_cron_add_args(job)),
        "edit": shlex.join(_build_openclaw_cron_edit_args(job)),
    }
    return job


def build_optimizer_openclaw_cron_contract_payload(
    *,
    generated_at: str = OPENCLAW_CRON_DEFAULT_GENERATED_AT,
    contract_id: str = OPENCLAW_CRON_CONTRACT_ID,
    schema_version: str = OPENCLAW_CRON_CONTRACT_SCHEMA_VERSION,
) -> dict[str, Any]:
    jobs = [
        _build_job(
            job_id="daily_optimizer_openclaw_cron",
            job_name=DAILY_OPENCLAW_CRON_JOB_NAME,
            cron_expr="0 4 * * *",
            cron_tz="UTC",
            entry_script_path=ROOT
            / "skills"
            / "autotiktok-strategy-optimizer"
            / "scripts"
            / "run_openclaw_cron_daily_optimizer.py",
            cron_prompt=(
                "Run python3 skills/autotiktok-strategy-optimizer/scripts/"
                "run_openclaw_cron_daily_optimizer.py and summarize the result, "
                "key decision, and output artifact path."
            ),
        ),
        _build_job(
            job_id="weekly_optimizer_openclaw_cron",
            job_name=WEEKLY_OPENCLAW_CRON_JOB_NAME,
            cron_expr="15 4 * * 0",
            cron_tz="UTC",
            entry_script_path=ROOT
            / "skills"
            / "autotiktok-strategy-optimizer"
            / "scripts"
            / "run_openclaw_cron_weekly_optimizer.py",
            cron_prompt=(
                "Run python3 skills/autotiktok-strategy-optimizer/scripts/"
                "run_openclaw_cron_weekly_optimizer.py and summarize the weekly "
                "decision and output artifact path."
            ),
        ),
    ]
    return {
        "schemaVersion": schema_version,
        "contractId": contract_id,
        "generatedAt": generated_at,
        "summary": {
            "jobCount": len(jobs),
            "defaultSessionTarget": OPENCLAW_CRON_DEFAULT_SESSION_TARGET,
            "defaultDeliveryMode": OPENCLAW_CRON_DEFAULT_DELIVERY_MODE,
        },
        "managementPolicy": {
            "requiresExplicitApproval": True,
            "listFirst": True,
            "exactNameMatch": True,
            "createMissingWith": "openclaw cron add",
            "updateExistingWith": "openclaw cron edit",
        },
        "jobs": jobs,
    }
