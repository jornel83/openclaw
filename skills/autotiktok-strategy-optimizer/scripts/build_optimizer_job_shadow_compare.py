#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job shadow-compare artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from build_optimizer_job_shadow_compare_plan import (
    expand_comparisons_with_schedule_intents,
)
from optimizer_job_shadow_compare_lib import (
    build_optimizer_job_shadow_compare_entry,
    build_optimizer_job_shadow_compare_plan_payload,
    build_optimizer_job_shadow_compare_payload,
    validate_optimizer_job_shadow_compare_plan_payload,
    validate_optimizer_job_shadow_compare_payload,
)
from optimizer_job_schedule_lib import load_optimizer_job_schedule
from optimizer_input_rollout_lib import load_optimizer_input_rollout_policy


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
    / "optimizer-job-shadow-compare.sample.json"
)
DEFAULT_COMPARE_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.sample.json"
)
RUN_SCHEDULED_JOB_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_scheduled_optimizer_job.py"
)

DEFAULT_COMPARISON_SPECS = (
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
)


def _run_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"{script.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_schedule(
    schedule_plan_payload: dict[str, Any], schedule_id: str
) -> dict[str, Any]:
    for schedule in schedule_plan_payload.get("schedules", []):
        if schedule.get("scheduleId") == schedule_id:
            return schedule
    raise ValueError(f"optimizer job scheduleId not found: {schedule_id}")


def _build_comparison_entry(
    *,
    schedule_plan_path: Path,
    input_rollout_policy_path: Path,
    schedule_plan_payload: dict[str, Any],
    comparison_spec: dict[str, str],
    temp_root: Path,
) -> dict[str, Any]:
    comparison_id = comparison_spec["comparisonId"]
    schedule_id = comparison_spec["scheduleId"]
    baseline_scheduler_rollout_intent = comparison_spec["baselineSchedulerRolloutIntent"]
    baseline_rollout_class = comparison_spec["baselineRolloutClass"]
    candidate_scheduler_rollout_intent = comparison_spec["candidateSchedulerRolloutIntent"]
    candidate_rollout_class = comparison_spec["candidateRolloutClass"]
    schedule = _find_schedule(schedule_plan_payload, schedule_id)

    production_path = (
        temp_root / f"{comparison_id}.baseline.{baseline_scheduler_rollout_intent}.json"
    )
    shadow_path = (
        temp_root / f"{comparison_id}.candidate.{candidate_scheduler_rollout_intent}.json"
    )

    _run_script(
        RUN_SCHEDULED_JOB_SCRIPT,
        "--input-schedule-plan",
        str(schedule_plan_path),
        "--schedule-id",
        schedule_id,
        "--scheduler-rollout-intent",
        baseline_scheduler_rollout_intent,
        "--output",
        str(production_path),
    )
    _run_script(
        RUN_SCHEDULED_JOB_SCRIPT,
        "--input-schedule-plan",
        str(schedule_plan_path),
        "--schedule-id",
        schedule_id,
        "--scheduler-rollout-intent",
        candidate_scheduler_rollout_intent,
        "--input-rollout-class",
        candidate_rollout_class,
        "--input-rollout-policy",
        str(input_rollout_policy_path),
        "--output",
        str(shadow_path),
    )

    return build_optimizer_job_shadow_compare_entry(
        comparison_id=comparison_id,
        schedule=schedule,
        baseline_scheduler_rollout_intent=baseline_scheduler_rollout_intent,
        baseline_rollout_class=baseline_rollout_class,
        candidate_scheduler_rollout_intent=candidate_scheduler_rollout_intent,
        candidate_rollout_class=candidate_rollout_class,
        baseline_payload=_load_json(production_path),
        candidate_payload=_load_json(shadow_path),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-schedule-plan", type=Path, default=DEFAULT_SCHEDULE_PLAN
    )
    parser.add_argument(
        "--input-rollout-policy", type=Path, default=DEFAULT_INPUT_ROLLOUT_POLICY
    )
    parser.add_argument("--input-compare-plan", type=Path, default=DEFAULT_COMPARE_PLAN)
    parser.add_argument(
        "--compare-id",
        default="optimizer-job-shadow-compare.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T05:45:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        schedule_plan_payload = load_optimizer_job_schedule(args.input_schedule_plan)
        input_rollout_policy_payload = load_optimizer_input_rollout_policy(
            args.input_rollout_policy
        )
        if args.input_compare_plan.exists():
            compare_plan_payload = _load_json(args.input_compare_plan)
        else:
            compare_plan_payload = build_optimizer_job_shadow_compare_plan_payload(
                compare_plan_id=(
                    "optimizer-job-shadow-compare-plan.autotiktok.fixture.2026-04-18"
                ),
                generated_at="2026-04-18T05:40:00Z",
                schedule_plan_payload=schedule_plan_payload,
                input_rollout_policy_payload=input_rollout_policy_payload,
                comparisons=expand_comparisons_with_schedule_intents(
                    schedule_plan_payload=schedule_plan_payload,
                    comparisons=list(DEFAULT_COMPARISON_SPECS),
                ),
            )
        validate_optimizer_job_shadow_compare_plan_payload(compare_plan_payload)
        if compare_plan_payload["generatedFrom"].get(
            "optimizerJobSchedulePlanId"
        ) != schedule_plan_payload.get("schedulePlanId"):
            raise ValueError(
                "optimizer job shadow compare plan schedulePlanId does not match the provided schedule plan"
            )
        if compare_plan_payload["generatedFrom"].get(
            "optimizerInputRolloutPolicyId"
        ) != input_rollout_policy_payload.get("policyId"):
            raise ValueError(
                "optimizer job shadow compare plan rollout policy does not match the provided rollout policy"
            )
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-shadow-compare-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            comparisons = [
                _build_comparison_entry(
                    schedule_plan_path=args.input_schedule_plan,
                    input_rollout_policy_path=args.input_rollout_policy,
                    schedule_plan_payload=schedule_plan_payload,
                    comparison_spec=comparison_spec,
                    temp_root=temp_root,
                )
                for comparison_spec in compare_plan_payload["comparisons"]
            ]
        payload = build_optimizer_job_shadow_compare_payload(
            compare_id=args.compare_id,
            generated_at=args.generated_at,
            compare_plan_payload=compare_plan_payload,
            schedule_plan_payload=schedule_plan_payload,
            input_rollout_policy_payload=input_rollout_policy_payload,
            comparisons=comparisons,
        )
        validate_optimizer_job_shadow_compare_payload(payload)
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job shadow compare to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
