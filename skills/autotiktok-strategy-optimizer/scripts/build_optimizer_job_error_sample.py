#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job-error fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_job_orchestration_lib import (
    build_optimizer_job_error_payload,
    validate_optimizer_job_error_payload,
)
from optimizer_job_schedule_lib import load_optimizer_job_schedule


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEDULE_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.external.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-error.sample.json"
)


def _find_schedule(payload: dict[str, object], schedule_id: str) -> dict[str, object]:
    for schedule in payload.get("schedules", []):
        if schedule.get("scheduleId") == schedule_id:
            return schedule
    raise ValueError(f"optimizer job scheduleId not found: {schedule_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-schedule-plan", type=Path, default=DEFAULT_SCHEDULE_PLAN)
    parser.add_argument("--schedule-id", default="weekly_optimizer_job")
    parser.add_argument(
        "--error-id",
        default="weekly_optimizer_job.error.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument("--generated-at", default="2026-04-19T03:36:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        schedule_plan = load_optimizer_job_schedule(args.input_schedule_plan)
        schedule = _find_schedule(schedule_plan, args.schedule_id)
        payload = build_optimizer_job_error_payload(
            error_id=args.error_id,
            generated_at=args.generated_at,
            error_code="input_resolution_failure",
            failure_stage="input_resolution",
            retryable=False,
            owner_hint="input_pipeline",
            failure_summary="scheduled optimizer job could not resolve required runtime inputs",
            error_message="scheduled weekly optimizer job must resolve a weekly review window input",
            schedule_id=args.schedule_id,
            execution_context_id="optimizer-job-execution-context.autotiktok.fixture.2026-04-19",
            schedule_plan_id=schedule_plan.get("schedulePlanId"),
            scheduler_run_id="optimizer-scheduler.autotiktok.fixture.2026-04-19.weekly_optimizer_job.real_shadow_validation",
            trigger_kind=schedule.get(
                "defaultTriggerKind", schedule_plan.get("defaultTriggerKind")
            ),
            scheduler_owner=schedule.get(
                "defaultSchedulerOwner", schedule_plan.get("defaultSchedulerOwner")
            ),
            execution_environment=schedule.get(
                "defaultExecutionEnvironment",
                schedule_plan.get("defaultExecutionEnvironment"),
            ),
            scheduler_rollout_intent="real_provider_shadow_validation",
            rollout_class="real_shadow_validation",
            job_kind=schedule.get("jobKind"),
            schedule_profile=schedule_plan.get("scheduleProfile"),
            runtime_profile_rollout_class="production",
            window_set_purpose=None,
            comparison_dimension=None,
        )
        validate_optimizer_job_error_payload(payload)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job error fixture to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
