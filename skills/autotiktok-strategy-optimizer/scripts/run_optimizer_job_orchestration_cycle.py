#!/usr/bin/env python3
"""
Run a scheduler-facing optimizer orchestration cycle from an execution-context artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from optimizer_input_rollout_lib import load_optimizer_input_rollout_policy
from optimizer_job_orchestration_lib import (
    build_optimizer_job_orchestration_cycle_payload,
    build_optimizer_run_summary_payload,
    load_optimizer_job_artifact_retention_policy,
    load_optimizer_job_error,
    load_optimizer_job_execution_context,
    validate_optimizer_job_orchestration_cycle_payload,
    validate_optimizer_run_summary_payload,
)
from optimizer_job_schedule_lib import load_optimizer_job_schedule
from optimizer_job_shadow_compare_lib import (
    build_optimizer_job_shadow_compare_batch_payload,
    build_optimizer_job_shadow_compare_entry,
    build_optimizer_job_shadow_compare_payload,
    build_optimizer_job_shadow_compare_plan_payload,
)


ROOT = Path(__file__).resolve().parents[3]
RUN_SCHEDULED_JOB_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_scheduled_optimizer_job.py"
)
DEFAULT_SCHEDULE_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.external.sample.json"
)
DEFAULT_EXECUTION_CONTEXT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-execution-context.sample.json"
)
DEFAULT_ARTIFACT_RETENTION_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-artifact-retention-policy.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-orchestration-cycle.sample.json"
)
DEFAULT_RUN_SUMMARY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-run-summary.sample.json"
)


class ScheduledJobFailure(RuntimeError):
    def __init__(self, message: str, *, error_payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.error_payload = error_payload


def _render_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_optional_path(raw_path: object) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def _find_schedule(
    schedule_plan_payload: dict[str, Any], schedule_id: str
) -> dict[str, Any]:
    for schedule in schedule_plan_payload.get("schedules", []):
        if schedule.get("scheduleId") == schedule_id:
            return schedule
    raise ValueError(f"optimizer job scheduleId not found: {schedule_id}")


def _resolve_schedule_input_path(
    *,
    schedule_context: dict[str, Any],
    default_inputs: dict[str, Any],
    field_name: str,
) -> Path | None:
    return _resolve_optional_path(
        schedule_context.get(field_name, default_inputs.get(field_name))
    )


def _build_job_record(
    *,
    schedule_id: str,
    scheduler_rollout_intent: str | None,
    rollout_class: str,
    output_path: Path | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "scheduleId": schedule_id,
        "schedulerRolloutIntent": scheduler_rollout_intent,
        "rolloutClass": rollout_class,
        "generatedAt": payload.get("generatedAt"),
        "outputPath": None if output_path is None else _render_repo_relative(output_path),
        "jobRunId": payload.get("jobRunId"),
        "jobKind": payload.get("jobKind"),
        "mode": payload.get("mode"),
        "summary": payload.get("summary"),
        "generatedFrom": payload.get("generatedFrom"),
    }


def _build_job_result(
    *,
    schedule_id: str,
    scheduler_rollout_intent: str | None,
    rollout_class: str,
    output_path: Path | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "scheduleId": schedule_id,
        "schedulerRolloutIntent": scheduler_rollout_intent,
        "rolloutClass": rollout_class,
        "outputPath": None if output_path is None else _render_repo_relative(output_path),
        "payload": payload,
    }


def _run_scheduled_job(
    *,
    schedule_plan_path: Path,
    schedule_id: str,
    input_manifest_path: Path | None,
    input_bundle_path: Path | None,
    policy_path: Path | None,
    weekly_review_window_path: Path | None,
    input_source_registry_path: Path | None,
    input_rollout_policy_path: Path | None,
    rollout_class: str | None,
    scheduler_run_id: str,
    trigger_kind: str,
    scheduler_owner: str,
    execution_environment: str,
    execution_context_id: str,
    artifact_emission_mode: str,
    scheduler_rollout_intent: str | None,
    output_path: Path,
    error_output_path: Path | None,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(RUN_SCHEDULED_JOB_SCRIPT),
        "--input-schedule-plan",
        str(schedule_plan_path),
        "--schedule-id",
        schedule_id,
        "--scheduler-run-id",
        scheduler_run_id,
        "--scheduler-trigger-kind",
        trigger_kind,
        "--scheduler-owner",
        scheduler_owner,
        "--execution-environment",
        execution_environment,
        "--execution-context-id",
        execution_context_id,
        "--artifact-emission-mode",
        artifact_emission_mode,
        "--output",
        str(output_path),
    ]
    if input_manifest_path is not None:
        command.extend(["--input-manifest", str(input_manifest_path)])
    if input_bundle_path is not None:
        command.extend(["--input-bundle", str(input_bundle_path)])
    if policy_path is not None:
        command.extend(["--policy", str(policy_path)])
    if weekly_review_window_path is not None:
        command.extend(
            ["--weekly-review-window-input", str(weekly_review_window_path)]
        )
    if input_source_registry_path is not None:
        command.extend(
            ["--input-source-registry", str(input_source_registry_path)]
        )
    if input_rollout_policy_path is not None:
        command.extend(
            ["--input-rollout-policy", str(input_rollout_policy_path)]
        )
    if rollout_class is not None:
        command.extend(["--input-rollout-class", rollout_class])
    if scheduler_rollout_intent is not None:
        command.extend(["--scheduler-rollout-intent", scheduler_rollout_intent])
    if error_output_path is not None:
        command.extend(["--error-output", str(error_output_path)])

    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        structured_error = None
        if error_output_path is not None and error_output_path.exists():
            structured_error = load_optimizer_job_error(error_output_path)
        error_details = result.stderr or result.stdout or "scheduled job failed"
        raise ScheduledJobFailure(
            error_details.strip(),
            error_payload=structured_error,
        )
    return json.loads(output_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-schedule-plan", type=Path, default=DEFAULT_SCHEDULE_PLAN)
    parser.add_argument(
        "--input-execution-context", type=Path, default=DEFAULT_EXECUTION_CONTEXT
    )
    parser.add_argument(
        "--input-artifact-retention-policy",
        type=Path,
        default=DEFAULT_ARTIFACT_RETENTION_POLICY,
    )
    parser.add_argument("--run-summary-output", type=Path)
    parser.add_argument(
        "--cycle-run-id",
        default="optimizer-job-orchestration-cycle.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument("--generated-at", default="2026-04-19T03:35:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        schedule_plan_payload = load_optimizer_job_schedule(args.input_schedule_plan)
        execution_context_payload = load_optimizer_job_execution_context(
            args.input_execution_context
        )
        default_run_context = execution_context_payload["defaultRunContext"]
        default_inputs = execution_context_payload["defaultInputs"]
        rollout_policy_path = _resolve_optional_path(
            default_inputs.get("inputRolloutPolicyPath")
        )
        input_rollout_policy_payload = (
            None
            if rollout_policy_path is None
            else load_optimizer_input_rollout_policy(rollout_policy_path)
        )
        artifact_retention_policy_payload = (
            None
            if args.input_artifact_retention_policy is None
            else load_optimizer_job_artifact_retention_policy(
                args.input_artifact_retention_policy
            )
        )
        artifact_emission_mode = default_run_context["artifactEmissionMode"]
        run_summary_output = args.run_summary_output
        job_run_records: list[dict[str, Any]] = []
        job_run_results: list[dict[str, Any]] = []
        compare_specs: list[dict[str, str]] = []
        compare_entries: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-orchestration-cycle-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            output_root = _resolve_optional_path(default_run_context.get("outputRoot"))

            for schedule_context in execution_context_payload["schedules"]:
                if not schedule_context.get("enabled", True):
                    continue
                schedule_id = schedule_context["scheduleId"]
                schedule = _find_schedule(schedule_plan_payload, schedule_id)
                job_kind = schedule["jobKind"]
                input_manifest_path = _resolve_schedule_input_path(
                    schedule_context=schedule_context,
                    default_inputs=default_inputs,
                    field_name="inputManifestPath",
                )
                input_bundle_path = _resolve_schedule_input_path(
                    schedule_context=schedule_context,
                    default_inputs=default_inputs,
                    field_name="inputBundlePath",
                )
                policy_path = _resolve_schedule_input_path(
                    schedule_context=schedule_context,
                    default_inputs=default_inputs,
                    field_name="policyPath",
                )
                weekly_review_window_path = _resolve_schedule_input_path(
                    schedule_context=schedule_context,
                    default_inputs=default_inputs,
                    field_name="weeklyReviewWindowPath",
                )
                input_source_registry_path = _resolve_schedule_input_path(
                    schedule_context=schedule_context,
                    default_inputs=default_inputs,
                    field_name="inputSourceRegistryPath",
                )
                production_scheduler_rollout_intent = schedule_context.get(
                    "productionSchedulerRolloutIntent", "production"
                )
                production_rollout_class = schedule_context.get(
                    "productionRolloutClass", "production"
                )
                shadow_scheduler_rollout_intent = schedule_context.get(
                    "shadowSchedulerRolloutIntent"
                )
                shadow_rollout_class = schedule_context.get("shadowRolloutClass")

                baseline_output_path = (
                    temp_root / f"{schedule_id}.production.json"
                    if artifact_emission_mode == "inline_only"
                    else output_root
                    / "job-runs"
                    / schedule_id
                    / "production"
                    / f"{schedule_id}.production.json"
                )
                baseline_error_path = temp_root / f"{schedule_id}.production.error.json"
                try:
                    baseline_payload = _run_scheduled_job(
                        schedule_plan_path=args.input_schedule_plan,
                        schedule_id=schedule_id,
                        input_manifest_path=input_manifest_path,
                        input_bundle_path=input_bundle_path,
                        policy_path=policy_path,
                        weekly_review_window_path=weekly_review_window_path
                        if job_kind == "weekly_optimizer_job"
                        else None,
                        input_source_registry_path=input_source_registry_path,
                        input_rollout_policy_path=rollout_policy_path,
                        rollout_class=None
                        if production_rollout_class == "production"
                        else production_rollout_class,
                        scheduler_run_id=(
                            f"{default_run_context['schedulerRunId']}.{schedule_id}.production"
                        ),
                        trigger_kind=default_run_context["triggerKind"],
                        scheduler_owner=default_run_context["schedulerOwner"],
                        execution_environment=default_run_context["executionEnvironment"],
                        execution_context_id=execution_context_payload["executionContextId"],
                        artifact_emission_mode=artifact_emission_mode,
                        scheduler_rollout_intent=production_scheduler_rollout_intent,
                        output_path=baseline_output_path,
                        error_output_path=baseline_error_path
                        if default_run_context["emitErrorArtifact"]
                        else None,
                    )
                except ScheduledJobFailure as exc:
                    if exc.error_payload is not None:
                        errors.append(exc.error_payload)
                        continue
                    raise
                job_run_records.append(
                    _build_job_record(
                        schedule_id=schedule_id,
                        scheduler_rollout_intent=production_scheduler_rollout_intent,
                        rollout_class=production_rollout_class,
                        output_path=baseline_output_path
                        if artifact_emission_mode == "write_through_output_root"
                        else None,
                        payload=baseline_payload,
                    )
                )
                job_run_results.append(
                    _build_job_result(
                        schedule_id=schedule_id,
                        scheduler_rollout_intent=production_scheduler_rollout_intent,
                        rollout_class=production_rollout_class,
                        output_path=baseline_output_path
                        if artifact_emission_mode == "write_through_output_root"
                        else None,
                        payload=baseline_payload,
                    )
                )

                if shadow_rollout_class is None:
                    continue

                candidate_output_path = (
                    temp_root / f"{schedule_id}.{shadow_rollout_class}.json"
                    if artifact_emission_mode == "inline_only"
                    else output_root
                    / "job-runs"
                    / schedule_id
                    / shadow_rollout_class
                    / f"{schedule_id}.{shadow_rollout_class}.json"
                )
                candidate_error_path = (
                    temp_root / f"{schedule_id}.{shadow_rollout_class}.error.json"
                )
                try:
                    candidate_payload = _run_scheduled_job(
                        schedule_plan_path=args.input_schedule_plan,
                        schedule_id=schedule_id,
                        input_manifest_path=None,
                        input_bundle_path=None,
                        policy_path=policy_path,
                        weekly_review_window_path=weekly_review_window_path
                        if job_kind == "weekly_optimizer_job"
                        else None,
                        input_source_registry_path=input_source_registry_path,
                        input_rollout_policy_path=rollout_policy_path,
                        rollout_class=shadow_rollout_class,
                        scheduler_run_id=(
                            f"{default_run_context['schedulerRunId']}.{schedule_id}.{shadow_rollout_class}"
                        ),
                        trigger_kind=default_run_context["triggerKind"],
                        scheduler_owner=default_run_context["schedulerOwner"],
                        execution_environment=default_run_context["executionEnvironment"],
                        execution_context_id=execution_context_payload["executionContextId"],
                        artifact_emission_mode=artifact_emission_mode,
                        scheduler_rollout_intent=shadow_scheduler_rollout_intent,
                        output_path=candidate_output_path,
                        error_output_path=candidate_error_path
                        if default_run_context["emitErrorArtifact"]
                        else None,
                    )
                except ScheduledJobFailure as exc:
                    if exc.error_payload is not None:
                        errors.append(exc.error_payload)
                        continue
                    raise
                job_run_records.append(
                    _build_job_record(
                        schedule_id=schedule_id,
                        scheduler_rollout_intent=shadow_scheduler_rollout_intent,
                        rollout_class=shadow_rollout_class,
                        output_path=candidate_output_path
                        if artifact_emission_mode == "write_through_output_root"
                        else None,
                        payload=candidate_payload,
                    )
                )
                job_run_results.append(
                    _build_job_result(
                        schedule_id=schedule_id,
                        scheduler_rollout_intent=shadow_scheduler_rollout_intent,
                        rollout_class=shadow_rollout_class,
                        output_path=candidate_output_path
                        if artifact_emission_mode == "write_through_output_root"
                        else None,
                        payload=candidate_payload,
                    )
                )
                comparison_id = schedule_context["comparisonId"]
                compare_specs.append(
                    {
                        "comparisonId": comparison_id,
                        "scheduleId": schedule_id,
                        "baselineSchedulerRolloutIntent": production_scheduler_rollout_intent,
                        "baselineRolloutClass": production_rollout_class,
                        "candidateSchedulerRolloutIntent": shadow_scheduler_rollout_intent,
                        "candidateRolloutClass": shadow_rollout_class,
                    }
                )
                compare_entries.append(
                    build_optimizer_job_shadow_compare_entry(
                        comparison_id=comparison_id,
                        schedule=schedule,
                        baseline_scheduler_rollout_intent=production_scheduler_rollout_intent,
                        baseline_rollout_class=production_rollout_class,
                        candidate_scheduler_rollout_intent=shadow_scheduler_rollout_intent,
                        candidate_rollout_class=shadow_rollout_class,
                        baseline_payload=baseline_payload,
                        candidate_payload=candidate_payload,
                    )
                )

        shadow_compare_plan_payload = (
            None
            if not compare_specs
            else build_optimizer_job_shadow_compare_plan_payload(
                compare_plan_id=(
                    "optimizer-job-shadow-compare-plan.autotiktok.cycle.2026-04-19"
                ),
                generated_at=args.generated_at,
                schedule_plan_payload=schedule_plan_payload,
                input_rollout_policy_payload=input_rollout_policy_payload or {},
                comparisons=compare_specs,
            )
        )
        shadow_compare_payload = (
            None
            if shadow_compare_plan_payload is None
            else build_optimizer_job_shadow_compare_payload(
                compare_id=(
                    "optimizer-job-shadow-compare.autotiktok.cycle.2026-04-19"
                ),
                generated_at=args.generated_at,
                compare_plan_payload=shadow_compare_plan_payload,
                schedule_plan_payload=schedule_plan_payload,
                input_rollout_policy_payload=input_rollout_policy_payload or {},
                comparisons=compare_entries,
            )
        )
        shadow_compare_batch_payload = (
            None
            if shadow_compare_payload is None
            or not execution_context_payload["defaultRunContext"]["emitCompareBatch"]
            else build_optimizer_job_shadow_compare_batch_payload(
                compare_payloads=[shadow_compare_payload],
                batch_id=(
                    "optimizer-job-shadow-compare-batch.autotiktok.cycle.2026-04-19"
                ),
                generated_at=args.generated_at,
                source_mode="orchestration_cycle",
                source_descriptor={
                    "executionContextId": execution_context_payload[
                        "executionContextId"
                    ],
                    "compareArtifactCount": 1,
                },
                comparison_dimension="scheduleId",
                batch_window_label="2026-04-19.orchestration-cycle",
            )
        )
        run_summary_payload = build_optimizer_run_summary_payload(
            run_summary_id="optimizer-run-summary.autotiktok.fixture.2026-04-19",
            generated_at=args.generated_at,
            execution_context_payload=execution_context_payload,
            schedule_plan_payload=schedule_plan_payload,
            artifact_retention_policy_payload=artifact_retention_policy_payload,
            cycle_run_id=args.cycle_run_id,
            cycle_schema_version="optimizer-job-orchestration-cycle.sample.v1",
            job_runs=job_run_results,
            shadow_compare_payload=shadow_compare_payload,
            shadow_compare_batch_payload=shadow_compare_batch_payload,
            errors=errors,
        )
        validate_optimizer_run_summary_payload(run_summary_payload)
        payload = build_optimizer_job_orchestration_cycle_payload(
            cycle_run_id=args.cycle_run_id,
            generated_at=args.generated_at,
            execution_context_payload=execution_context_payload,
            schedule_plan_payload=schedule_plan_payload,
            input_rollout_policy_payload=input_rollout_policy_payload,
            artifact_retention_policy_payload=artifact_retention_policy_payload,
            run_summary_payload=run_summary_payload,
            job_runs=job_run_records,
            shadow_compare_plan_payload=shadow_compare_plan_payload,
            shadow_compare_payload=shadow_compare_payload,
            shadow_compare_batch_payload=shadow_compare_batch_payload,
            errors=errors,
            artifact_emission_mode=artifact_emission_mode,
        )
        validate_optimizer_job_orchestration_cycle_payload(payload)
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    if run_summary_output is not None:
        run_summary_output.parent.mkdir(parents=True, exist_ok=True)
        run_summary_output.write_text(
            json.dumps(run_summary_payload, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote optimizer run summary to {run_summary_output}")
    print(f"Wrote optimizer job orchestration cycle to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
