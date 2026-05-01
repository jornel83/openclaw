#!/usr/bin/env python3
"""
Run a scheduled optimizer job from a scheduler-facing job schedule plan.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

from optimizer_bundle_lib import build_optimizer_input_manifest_from_source_registry
from optimizer_input_rollout_lib import (
    load_optimizer_input_rollout_policy,
)
from optimizer_job_orchestration_lib import (
    OPTIMIZER_JOB_ARTIFACT_EMISSION_MODES,
    build_optimizer_job_error_payload,
    validate_optimizer_job_error_payload,
)
from optimizer_job_schedule_lib import (
    load_optimizer_job_schedule,
    resolve_optimizer_job_schedule_execution_policy,
)
from run_daily_optimizer_job import build_job_run as build_daily_job_run
from run_weekly_optimizer_job import build_job_run as build_weekly_job_run


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEDULE_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json"
)


def _resolve_repo_path(raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def _find_schedule(payload: dict[str, object], schedule_id: str) -> dict[str, object]:
    for schedule in payload.get("schedules", []):
        if schedule.get("scheduleId") == schedule_id:
            return schedule
    raise ValueError(f"optimizer job scheduleId not found: {schedule_id}")


def _render_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_schedule_optional_path(raw_path: object) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    return _resolve_repo_path(raw_path)


def _resolve_output_path(
    *,
    explicit_output: Path | None,
    explicit_output_root: Path | None,
    schedule: dict[str, object],
    schedule_plan: dict[str, object],
    job_run_id: str,
) -> tuple[Path, Path | None]:
    if explicit_output is not None:
        return explicit_output, explicit_output_root
    output_emission_mode = schedule.get(
        "outputEmissionMode", schedule_plan.get("defaultOutputEmissionMode")
    )
    if output_emission_mode == "output_root":
        output_root = explicit_output_root
        if output_root is None:
            default_output_root = schedule.get(
                "defaultOutputRoot", schedule_plan.get("defaultOutputRoot")
            )
            output_root = _resolve_schedule_optional_path(default_output_root)
        if output_root is None:
            raise ValueError(
                "scheduled optimizer job requires --output-root when outputEmissionMode=output_root"
            )
        output_subdir = schedule.get("outputSubdir")
        if not isinstance(output_subdir, str) or not output_subdir:
            raise ValueError(
                "scheduled optimizer job schedule must declare outputSubdir when outputEmissionMode=output_root"
            )
        return output_root / output_subdir / f"{job_run_id}.json", output_root
    output_path = _resolve_schedule_optional_path(schedule.get("defaultOutputPath"))
    if output_path is None:
        raise ValueError(
            "scheduled optimizer job requires defaultOutputPath when outputEmissionMode=direct_output_path"
        )
    return output_path, explicit_output_root


def _build_shadow_manifest_for_schedule(
    *,
    input_source_registry: Path | None,
    input_rollout_policy: Path | None,
    input_rollout_policy_payload: dict[str, object] | None,
    execution_policy: dict[str, str | None] | None,
    temp_root: Path,
    generated_at: str,
    job_run_id: str,
) -> Path | None:
    if execution_policy is None or execution_policy.get("sourceLane") is None:
        return None
    registry_path = input_source_registry
    rollout_policy_path = input_rollout_policy
    if registry_path is None or rollout_policy_path is None:
        raise ValueError(
            "scheduled optimizer shadow rollout requires both input source registry and rollout policy"
        )
    if input_rollout_policy_payload is None:
        raise ValueError(
            "scheduled optimizer shadow rollout requires input rollout policy payload"
        )

    manifest_payload = build_optimizer_input_manifest_from_source_registry(
        registry_path=registry_path,
        source_lane=execution_policy["sourceLane"],
        schema_version="optimizer-input-manifest.v1",
        manifest_id=f"{job_run_id}.input-manifest",
        generated_at=generated_at,
        input_rollout_policy_reference={
            "schemaVersion": input_rollout_policy_payload.get("schemaVersion"),
            "policyId": input_rollout_policy_payload.get("policyId"),
            "path": _render_repo_relative(rollout_policy_path),
        },
        input_rollout_class=execution_policy["inputRolloutClass"],
        input_lane_selection_source=execution_policy["inputLaneSelectionSource"],
        input_rollout_strategy=execution_policy["inputRolloutStrategy"],
    )
    manifest_path = temp_root / (
        f"{job_run_id}.{execution_policy['schedulerRolloutIntent']}.manifest.json"
    )
    manifest_path.write_text(
        json.dumps(manifest_payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _classify_scheduled_job_failure(
    *,
    exc: Exception,
    schedule: dict[str, object] | None,
    schedule_plan: dict[str, object] | None,
    resolved_execution_policy: dict[str, str | None] | None,
) -> dict[str, object]:
    message = str(exc)
    lowered = message.lower()
    if isinstance(exc, FileNotFoundError) or "no such file" in lowered or "not found" in lowered:
        return {
            "errorCode": "input_resolution_failure",
            "failureStage": "input_resolution",
            "retryable": False,
            "ownerHint": "input_pipeline",
            "failureSummary": "scheduled optimizer job could not resolve required runtime inputs",
        }
    if isinstance(exc, OSError):
        return {
            "errorCode": "artifact_emission_failure",
            "failureStage": "artifact_emission",
            "retryable": True,
            "ownerHint": "ops",
            "failureSummary": "failed to write or read a scheduled optimizer job artifact",
        }
    if (
        "input_manifest" in lowered
        or "input_bundle" in lowered
        or "policy path" in lowered
        or "weekly review window input" in lowered
        or "input source registry" in lowered
        or "input rollout policy" in lowered
    ):
        return {
            "errorCode": "input_resolution_failure",
            "failureStage": "input_resolution",
            "retryable": False,
            "ownerHint": "input_pipeline",
            "failureSummary": "scheduled optimizer job could not resolve required runtime inputs",
        }
    if (
        "rollout" in lowered
        or "windowsetpurpose" in lowered
        or "comparisondimension" in lowered
    ):
        return {
            "errorCode": "rollout_policy_failure",
            "failureStage": "rollout_policy_resolution",
            "retryable": False,
            "ownerHint": "rollout_policy",
            "failureSummary": "scheduled optimizer job could not resolve rollout policy metadata",
        }
    if "scheduleid not found" in lowered or "output_root" in lowered:
        return {
            "errorCode": "scheduler_dispatch_failure",
            "failureStage": "scheduler_dispatch",
            "retryable": False,
            "ownerHint": "scheduler_config",
            "failureSummary": "scheduled optimizer job dispatch configuration is invalid",
        }
    return {
        "errorCode": "job_materialization_failure",
        "failureStage": "job_materialization",
        "retryable": False,
        "ownerHint": "optimizer_runner",
        "failureSummary": "scheduled optimizer job failed while materializing runtime artifacts",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-schedule-plan", type=Path, default=DEFAULT_SCHEDULE_PLAN)
    parser.add_argument("--schedule-id", required=True)
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--input-bundle", type=Path)
    parser.add_argument("--ranking-input", type=Path)
    parser.add_argument("--context-input", type=Path)
    parser.add_argument("--backfills-input", type=Path)
    parser.add_argument("--performance-input", type=Path)
    parser.add_argument("--challenger-input", dest="challenger_input", type=Path)
    parser.add_argument("--challenger-adjustments", dest="challenger_input", type=Path)
    parser.add_argument("--weekly-review-window-input", type=Path)
    parser.add_argument("--input-source-registry", type=Path)
    parser.add_argument("--input-rollout-policy", type=Path)
    parser.add_argument("--input-rollout-class")
    parser.add_argument("--scheduler-rollout-intent")
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--scheduler-run-id")
    parser.add_argument(
        "--scheduler-trigger-kind", choices=("manual", "cron", "planner")
    )
    parser.add_argument("--scheduler-owner")
    parser.add_argument(
        "--execution-environment", choices=("repo_local", "scheduler_managed")
    )
    parser.add_argument("--execution-context-id")
    parser.add_argument(
        "--artifact-emission-mode",
        choices=tuple(sorted(OPTIMIZER_JOB_ARTIFACT_EMISSION_MODES)),
    )
    parser.add_argument("--error-output", type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--ranking-contract-version")
    parser.add_argument("--ranking-contract-validation-mode")
    parser.add_argument("--job-run-id")
    parser.add_argument("--cycle-id")
    parser.add_argument("--eval-run-id")
    parser.add_argument("--report-id")
    parser.add_argument("--generated-at")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    schedule_plan: dict[str, object] | None = None
    schedule: dict[str, object] | None = None
    resolved_execution_policy: dict[str, str | None] | None = None
    try:
        if args.input_bundle is not None and args.input_rollout_class is not None:
            raise ValueError(
                "--input-bundle and --input-rollout-class are mutually exclusive"
            )
        if args.input_manifest is not None and args.input_rollout_class is not None:
            raise ValueError(
                "--input-manifest and --input-rollout-class are mutually exclusive"
            )
        schedule_plan = load_optimizer_job_schedule(args.input_schedule_plan)
        schedule = _find_schedule(schedule_plan, args.schedule_id)
        default_input_mode = schedule["defaultInputMode"]
        default_input_path = _resolve_schedule_optional_path(
            schedule.get("defaultInputPath")
        )
        resolved_input_source_registry_path = args.input_source_registry or _resolve_schedule_optional_path(
            schedule.get("defaultInputSourceRegistryPath")
            or schedule_plan.get("generatedFrom", {}).get(
                "optimizerInputSourceRegistryPath"
            )
        )
        resolved_input_rollout_policy_path = args.input_rollout_policy or _resolve_schedule_optional_path(
            schedule_plan.get("generatedFrom", {}).get(
                "optimizerInputRolloutPolicyPath"
            )
        )
        input_rollout_policy_payload = (
            None
            if resolved_input_rollout_policy_path is None
            else load_optimizer_input_rollout_policy(resolved_input_rollout_policy_path)
        )
        resolved_execution_policy = resolve_optimizer_job_schedule_execution_policy(
            schedule_plan,
            input_rollout_policy_payload=input_rollout_policy_payload,
            schedule_id=args.schedule_id,
            explicit_scheduler_rollout_intent=args.scheduler_rollout_intent,
            explicit_rollout_class=args.input_rollout_class,
        )
        resolved_generated_at = args.generated_at or schedule["defaultGeneratedAt"]
        resolved_job_run_id = args.job_run_id or schedule["defaultJobRunId"]
        with tempfile.TemporaryDirectory(prefix="autotiktok-scheduled-job-") as temp_dir:
            temp_root = Path(temp_dir)
            generated_manifest_path = _build_shadow_manifest_for_schedule(
                input_source_registry=resolved_input_source_registry_path,
                input_rollout_policy=resolved_input_rollout_policy_path,
                input_rollout_policy_payload=input_rollout_policy_payload,
                execution_policy=None
                if (
                    args.input_manifest is not None
                    or args.input_bundle is not None
                    or (
                        args.input_rollout_class is None
                        and args.scheduler_rollout_intent is None
                    )
                )
                else resolved_execution_policy,
                temp_root=temp_root,
                generated_at=resolved_generated_at,
                job_run_id=resolved_job_run_id,
            )
            runner_args = argparse.Namespace(
                input_manifest=args.input_manifest
                or generated_manifest_path
                or (default_input_path if default_input_mode == "manifest" else None),
                input_bundle=args.input_bundle
                or (default_input_path if default_input_mode == "bundle" else None),
                ranking_input=args.ranking_input,
                context_input=args.context_input,
                backfills_input=args.backfills_input,
                performance_input=args.performance_input,
                challenger_input=args.challenger_input,
                policy=args.policy
                or _resolve_schedule_optional_path(schedule.get("defaultPolicyPath")),
                weekly_review_window_input=args.weekly_review_window_input
                or _resolve_schedule_optional_path(
                    schedule.get("defaultWeeklyReviewWindowPath")
                ),
                ranking_contract_version=args.ranking_contract_version
                or schedule["rankingContractVersion"],
                ranking_contract_validation_mode=args.ranking_contract_validation_mode
                or schedule["rankingContractValidationMode"],
                job_run_id=resolved_job_run_id,
                cycle_id=args.cycle_id or schedule["defaultCycleId"],
                eval_run_id=args.eval_run_id or schedule["defaultEvalRunId"],
                report_id=args.report_id or schedule["defaultReportId"],
                generated_at=resolved_generated_at,
            )
            builder = (
                build_daily_job_run
                if schedule["jobKind"] == "daily_optimizer_job"
                else build_weekly_job_run
            )
            if runner_args.input_manifest is None and runner_args.input_bundle is None:
                raise ValueError(
                    "scheduled optimizer job must resolve either input_manifest or input_bundle"
                )
            if runner_args.policy is None:
                raise ValueError(
                    "scheduled optimizer job must resolve a policy path"
                )
            if (
                schedule["jobKind"] == "weekly_optimizer_job"
                and runner_args.weekly_review_window_input is None
            ):
                raise ValueError(
                    "scheduled weekly optimizer job must resolve a weekly review window input"
                )
            payload = builder(runner_args)
            output_path, resolved_output_root = _resolve_output_path(
                explicit_output=args.output,
                explicit_output_root=args.output_root,
                schedule=schedule,
                schedule_plan=schedule_plan,
                job_run_id=resolved_job_run_id,
            )
            include_schedule_metadata = (
                schedule_plan.get("scheduleProfile") == "external_scheduler"
                or args.scheduler_run_id is not None
                or args.scheduler_trigger_kind is not None
                or args.scheduler_owner is not None
                or args.execution_environment is not None
                or args.execution_context_id is not None
                or args.artifact_emission_mode is not None
                or resolved_output_root is not None
                or args.input_rollout_class is not None
                or args.scheduler_rollout_intent is not None
            )
            if include_schedule_metadata:
                payload.setdefault("generatedFrom", {})
                payload["generatedFrom"].update(
                    {
                        "optimizerJobScheduleSchemaVersion": schedule_plan.get(
                            "schemaVersion"
                        ),
                        "optimizerJobSchedulePlanId": schedule_plan.get(
                            "schedulePlanId"
                        ),
                        "optimizerJobScheduleId": schedule.get("scheduleId"),
                        "optimizerJobScheduleProfile": schedule_plan.get(
                            "scheduleProfile"
                        ),
                        "optimizerJobSchedulerRolloutIntent": resolved_execution_policy.get(
                            "schedulerRolloutIntent"
                        ),
                        "optimizerJobSchedulerRolloutIntentSelectionSource": resolved_execution_policy.get(
                            "selectionSource"
                        ),
                        "optimizerJobRuntimeProfileRolloutClass": resolved_execution_policy.get(
                            "runtimeProfileRolloutClass"
                        ),
                        "optimizerJobWindowSetPurpose": resolved_execution_policy.get(
                            "windowSetPurpose"
                        ),
                        "optimizerJobComparisonDimension": resolved_execution_policy.get(
                            "comparisonDimension"
                        ),
                        "optimizerJobExecutionContextId": args.execution_context_id,
                        "optimizerJobArtifactEmissionMode": args.artifact_emission_mode,
                        "optimizerJobPathResolutionMode": schedule.get(
                            "pathResolutionMode",
                            schedule_plan.get("defaultPathResolutionMode"),
                        ),
                        "optimizerJobOutputEmissionMode": schedule.get(
                            "outputEmissionMode",
                            schedule_plan.get("defaultOutputEmissionMode"),
                        ),
                        "optimizerJobOutputRoot": None
                        if resolved_output_root is None
                        else _render_repo_relative(resolved_output_root),
                        "optimizerJobSchedulerRunId": args.scheduler_run_id,
                        "optimizerJobTriggerKind": args.scheduler_trigger_kind
                        or schedule.get(
                            "defaultTriggerKind",
                            schedule_plan.get("defaultTriggerKind"),
                        ),
                        "optimizerJobSchedulerOwner": args.scheduler_owner
                        or schedule.get(
                            "defaultSchedulerOwner",
                            schedule_plan.get("defaultSchedulerOwner"),
                        ),
                        "optimizerJobExecutionEnvironment": args.execution_environment
                        or schedule.get(
                            "defaultExecutionEnvironment",
                            schedule_plan.get("defaultExecutionEnvironment"),
                        ),
                    }
                )
            rendered = json.dumps(payload, ensure_ascii=True, indent=2)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        if args.error_output is not None:
            failure_details = _classify_scheduled_job_failure(
                exc=exc,
                schedule=schedule,
                schedule_plan=schedule_plan,
                resolved_execution_policy=resolved_execution_policy,
            )
            error_payload = build_optimizer_job_error_payload(
                error_id=(
                    f"{args.schedule_id}.error"
                    if getattr(args, "schedule_id", None)
                    else "optimizer-scheduled-job.error"
                ),
                generated_at=args.generated_at or "unknown",
                error_code=str(failure_details["errorCode"]),
                failure_stage=str(failure_details["failureStage"]),
                retryable=bool(failure_details["retryable"]),
                owner_hint=str(failure_details["ownerHint"]),
                failure_summary=str(failure_details["failureSummary"]),
                error_message=str(exc),
                schedule_id=getattr(args, "schedule_id", None) or "unknown_schedule",
                execution_context_id=args.execution_context_id,
                schedule_plan_id=None
                if schedule_plan is None
                else schedule_plan.get("schedulePlanId"),
                scheduler_run_id=args.scheduler_run_id,
                trigger_kind=args.scheduler_trigger_kind
                or (
                    None
                    if schedule is None
                    else schedule.get(
                        "defaultTriggerKind",
                        schedule_plan.get("defaultTriggerKind")
                        if schedule_plan is not None
                        else None,
                    )
                ),
                scheduler_owner=args.scheduler_owner
                or (
                    None
                    if schedule is None
                    else schedule.get(
                        "defaultSchedulerOwner",
                        schedule_plan.get("defaultSchedulerOwner")
                        if schedule_plan is not None
                        else None,
                    )
                ),
                execution_environment=args.execution_environment
                or (
                    None
                    if schedule is None
                    else schedule.get(
                        "defaultExecutionEnvironment",
                        schedule_plan.get("defaultExecutionEnvironment")
                        if schedule_plan is not None
                        else None,
                    )
                ),
                scheduler_rollout_intent=None
                if resolved_execution_policy is None
                else resolved_execution_policy.get("schedulerRolloutIntent"),
                rollout_class=None
                if resolved_execution_policy is None
                else resolved_execution_policy.get("inputRolloutClass"),
                job_kind=None if schedule is None else schedule.get("jobKind"),
                schedule_profile=None
                if schedule_plan is None
                else schedule_plan.get("scheduleProfile"),
                runtime_profile_rollout_class=None
                if resolved_execution_policy is None
                else resolved_execution_policy.get("runtimeProfileRolloutClass"),
                window_set_purpose=None
                if resolved_execution_policy is None
                else resolved_execution_policy.get("windowSetPurpose"),
                comparison_dimension=None
                if resolved_execution_policy is None
                else resolved_execution_policy.get("comparisonDimension"),
            )
            validate_optimizer_job_error_payload(error_payload)
            args.error_output.parent.mkdir(parents=True, exist_ok=True)
            args.error_output.write_text(
                json.dumps(error_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
        print(f"[ERROR] {exc}")
        return 1

    print(f"Wrote scheduled optimizer job run to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
