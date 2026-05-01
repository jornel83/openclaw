#!/usr/bin/env python3
"""
Helpers for standard OpenClaw cron entrypoints for AutoTikTok optimizer jobs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_OPENCLAW_CRON_OUTPUT_ROOT = Path("/tmp/openclaw-autotiktok")


def resolve_openclaw_cron_output_path(
    *,
    explicit_output: Path | None,
    output_root: Path | None,
    job_run_id: str,
) -> Path:
    if explicit_output is not None:
        return explicit_output
    root = output_root or DEFAULT_OPENCLAW_CRON_OUTPUT_ROOT
    return root / f"{job_run_id}.json"


def write_openclaw_cron_payload(
    payload: dict[str, Any],
    *,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def render_openclaw_cron_job_summary(
    payload: dict[str, Any],
    *,
    output_path: Path,
) -> str:
    summary = payload.get("summary", {})
    lines = [
        "status=ok",
        f"job_kind={payload.get('jobKind')}",
        f"job_run_id={payload.get('jobRunId')}",
        f"output={output_path}",
        f"ranking_run_id={summary.get('rankingRunId')}",
        f"ranking_profile_id={summary.get('rankingProfileId')}",
        f"daily_recommendation={summary.get('dailyRecommendation')}",
        f"shadow_leader_profile_id={summary.get('shadowLeaderProfileId')}",
    ]
    weekly_decision = summary.get("weeklyDecision")
    if weekly_decision is not None:
        lines.append(f"weekly_decision={weekly_decision}")
    selected_challenger = summary.get("selectedChallengerProfileId")
    if selected_challenger is not None:
        lines.append(f"selected_challenger_profile_id={selected_challenger}")
    return "\n".join(lines)
