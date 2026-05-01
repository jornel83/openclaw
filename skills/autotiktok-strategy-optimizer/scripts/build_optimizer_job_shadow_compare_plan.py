#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job shadow-compare plan artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_input_rollout_lib import load_optimizer_input_rollout_policy
from optimizer_job_schedule_lib import load_optimizer_job_schedule
from optimizer_job_shadow_compare_lib import (
    build_optimizer_job_shadow_compare_plan_payload,
    validate_optimizer_job_shadow_compare_plan_payload,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEDULE_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json"
)
DEFAULT_INPUT_ROLLOUT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-rollout-policy.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.sample.json"
)

DEFAULT_COMPARISONS = [
    {
        "comparisonId": "daily_raw_shadow_vs_production",
        "scheduleId": "daily_optimizer_job",
        "baselineSchedulerRolloutIntent": "production",
        "candidateSchedulerRolloutIntent": "raw_shadow_validation",
    },
    {
        "comparisonId": "weekly_real_shadow_vs_production",
        "scheduleId": "weekly_optimizer_job",
        "baselineSchedulerRolloutIntent": "production",
        "candidateSchedulerRolloutIntent": "real_provider_shadow_validation",
    },
    {
        "comparisonId": "daily_preview_validation_vs_production",
        "scheduleId": "daily_optimizer_job",
        "baselineSchedulerRolloutIntent": "production",
        "candidateSchedulerRolloutIntent": "preview_validation",
    },
    {
        "comparisonId": "daily_profile_compare_validation_vs_production",
        "scheduleId": "daily_optimizer_job",
        "baselineSchedulerRolloutIntent": "production",
        "candidateSchedulerRolloutIntent": "profile_compare_validation",
    },
]

COMPARISON_SCOPES = ("all", "daily", "weekly")


def get_comparisons_for_scope(scope: str) -> list[dict[str, str]]:
    if scope == "all":
        return list(DEFAULT_COMPARISONS)
    if scope == "daily":
        return [
            comparison
            for comparison in DEFAULT_COMPARISONS
            if comparison["scheduleId"] == "daily_optimizer_job"
        ]
    if scope == "weekly":
        return [
            comparison
            for comparison in DEFAULT_COMPARISONS
            if comparison["scheduleId"] == "weekly_optimizer_job"
        ]
    raise ValueError(f"unsupported comparison scope: {scope}")


def expand_comparisons_with_schedule_intents(
    *,
    schedule_plan_payload: dict[str, object],
    comparisons: list[dict[str, str]],
) -> list[dict[str, str]]:
    scheduler_intent_catalog = {
        entry["schedulerRolloutIntent"]: entry
        for entry in schedule_plan_payload.get("schedulerRolloutIntents", [])
        if isinstance(entry, dict)
        and isinstance(entry.get("schedulerRolloutIntent"), str)
        and entry.get("schedulerRolloutIntent")
    }
    schedule_catalog = {
        entry["scheduleId"]: entry
        for entry in schedule_plan_payload.get("schedules", [])
        if isinstance(entry, dict)
        and isinstance(entry.get("scheduleId"), str)
        and entry.get("scheduleId")
    }
    expanded: list[dict[str, str]] = []
    for comparison in comparisons:
        schedule_id = comparison["scheduleId"]
        schedule = schedule_catalog.get(schedule_id)
        if schedule is None:
            raise ValueError(f"optimizer job scheduleId not found: {schedule_id}")
        allowed_scheduler_rollout_intents = set(
            schedule.get("allowedSchedulerRolloutIntents", [])
        )
        baseline_intent = comparison["baselineSchedulerRolloutIntent"]
        candidate_intent = comparison["candidateSchedulerRolloutIntent"]
        if baseline_intent not in scheduler_intent_catalog:
            raise ValueError(
                f"optimizer job schedulerRolloutIntent not found: {baseline_intent!r}"
            )
        if candidate_intent not in scheduler_intent_catalog:
            raise ValueError(
                f"optimizer job schedulerRolloutIntent not found: {candidate_intent!r}"
            )
        if allowed_scheduler_rollout_intents and (
            baseline_intent not in allowed_scheduler_rollout_intents
            or candidate_intent not in allowed_scheduler_rollout_intents
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} does not allow one of the requested scheduler rollout intents"
            )
        baseline_entry = scheduler_intent_catalog[baseline_intent]
        candidate_entry = scheduler_intent_catalog[candidate_intent]
        expanded.append(
            {
                "comparisonId": comparison["comparisonId"],
                "scheduleId": schedule_id,
                "baselineSchedulerRolloutIntent": baseline_intent,
                "baselineRolloutClass": baseline_entry["inputRolloutClass"],
                "baselineRuntimeProfileRolloutClass": baseline_entry[
                    "runtimeProfileRolloutClass"
                ],
                "baselineWindowSetPurpose": baseline_entry.get("windowSetPurpose"),
                "baselineComparisonDimension": baseline_entry.get(
                    "comparisonDimension"
                ),
                "candidateSchedulerRolloutIntent": candidate_intent,
                "candidateRolloutClass": candidate_entry["inputRolloutClass"],
                "candidateRuntimeProfileRolloutClass": candidate_entry[
                    "runtimeProfileRolloutClass"
                ],
                "candidateWindowSetPurpose": candidate_entry.get("windowSetPurpose"),
                "candidateComparisonDimension": candidate_entry.get(
                    "comparisonDimension"
                ),
            }
        )
    return expanded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-schedule-plan", type=Path, default=DEFAULT_SCHEDULE_PLAN
    )
    parser.add_argument(
        "--input-rollout-policy", type=Path, default=DEFAULT_INPUT_ROLLOUT_POLICY
    )
    parser.add_argument(
        "--comparison-scope",
        choices=COMPARISON_SCOPES,
        default="all",
        help="Select the committed shadow-compare subset to materialize.",
    )
    parser.add_argument(
        "--compare-plan-id",
        default="optimizer-job-shadow-compare-plan.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T05:40:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        schedule_plan_payload = load_optimizer_job_schedule(args.input_schedule_plan)
        input_rollout_policy_payload = load_optimizer_input_rollout_policy(
            args.input_rollout_policy
        )
        comparisons = expand_comparisons_with_schedule_intents(
            schedule_plan_payload=schedule_plan_payload,
            comparisons=get_comparisons_for_scope(args.comparison_scope),
        )
        payload = build_optimizer_job_shadow_compare_plan_payload(
            compare_plan_id=args.compare_plan_id,
            generated_at=args.generated_at,
            schedule_plan_payload=schedule_plan_payload,
            input_rollout_policy_payload=input_rollout_policy_payload,
            comparisons=comparisons,
        )
        validate_optimizer_job_shadow_compare_plan_payload(payload)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job shadow compare plan to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
