#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job execution-context fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_input_rollout_lib import load_optimizer_input_rollout_policy
from optimizer_job_orchestration_lib import (
    build_optimizer_job_execution_context_payload,
    validate_optimizer_job_execution_context_payload,
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
DEFAULT_INPUT_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.sample.json"
)
DEFAULT_INPUT_SOURCE_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-source-registry.sample.json"
)
DEFAULT_INPUT_ROLLOUT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-rollout-policy.sample.json"
)
DEFAULT_WEEKLY_REVIEW_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)
DEFAULT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "config"
    / "optimizer-policy.v1.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-execution-context.sample.json"
)


def _render_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-schedule-plan", type=Path, default=DEFAULT_SCHEDULE_PLAN)
    parser.add_argument(
        "--input-rollout-policy", type=Path, default=DEFAULT_INPUT_ROLLOUT_POLICY
    )
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_INPUT_MANIFEST)
    parser.add_argument(
        "--input-source-registry", type=Path, default=DEFAULT_INPUT_SOURCE_REGISTRY
    )
    parser.add_argument(
        "--weekly-review-window-input",
        type=Path,
        default=DEFAULT_WEEKLY_REVIEW_WINDOW,
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--execution-context-id",
        default="optimizer-job-execution-context.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument("--generated-at", default="2026-04-19T03:30:00Z")
    parser.add_argument(
        "--scheduler-run-id",
        default="optimizer-scheduler.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument(
        "--artifact-emission-mode",
        choices=("inline_only", "write_through_output_root"),
        default="inline_only",
    )
    parser.add_argument("--output-root")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        schedule_plan_payload = load_optimizer_job_schedule(args.input_schedule_plan)
        input_rollout_policy_payload = load_optimizer_input_rollout_policy(
            args.input_rollout_policy
        )
        payload = build_optimizer_job_execution_context_payload(
            execution_context_id=args.execution_context_id,
            generated_at=args.generated_at,
            schedule_plan_payload=schedule_plan_payload,
            schedule_plan_path=_render_repo_relative(args.input_schedule_plan),
            input_rollout_policy_payload=input_rollout_policy_payload,
            input_rollout_policy_path=_render_repo_relative(args.input_rollout_policy),
            default_run_context={
                "schedulerRunId": args.scheduler_run_id,
                "triggerKind": "planner",
                "schedulerOwner": "repo_scheduler_fixture",
                "executionEnvironment": "scheduler_managed",
                "artifactEmissionMode": args.artifact_emission_mode,
                "outputRoot": args.output_root,
                "emitShadowCompare": True,
                "emitCompareBatch": True,
                "emitErrorArtifact": True,
            },
            default_inputs={
                "inputManifestPath": _render_repo_relative(args.input_manifest),
                "inputBundlePath": None,
                "policyPath": _render_repo_relative(args.policy),
                "inputSourceRegistryPath": _render_repo_relative(
                    args.input_source_registry
                ),
                "inputRolloutPolicyPath": _render_repo_relative(
                    args.input_rollout_policy
                ),
                "weeklyReviewWindowPath": _render_repo_relative(
                    args.weekly_review_window_input
                ),
            },
            schedules=[
                {
                    "scheduleId": "daily_optimizer_job",
                    "enabled": True,
                    "productionSchedulerRolloutIntent": "production",
                    "shadowSchedulerRolloutIntent": "raw_shadow_validation",
                    "productionRolloutClass": "production",
                    "shadowRolloutClass": "raw_shadow_validation",
                    "comparisonId": "daily_raw_shadow_vs_production",
                },
                {
                    "scheduleId": "weekly_optimizer_job",
                    "enabled": True,
                    "productionSchedulerRolloutIntent": "production",
                    "shadowSchedulerRolloutIntent": "real_provider_shadow_validation",
                    "productionRolloutClass": "production",
                    "shadowRolloutClass": "real_shadow_validation",
                    "comparisonId": "weekly_real_shadow_vs_production",
                },
            ],
        )
        validate_optimizer_job_execution_context_payload(payload)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job execution context to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
