#!/usr/bin/env python3
"""
Helpers for scheduler-facing optimizer execution-context, error, and cycle artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OPTIMIZER_JOB_EXECUTION_CONTEXT_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-execution-context.sample.v1"
)
OPTIMIZER_JOB_EXECUTION_CONTEXT_SCHEMA_VERSION = (
    "optimizer-job-execution-context.v1"
)
OPTIMIZER_JOB_EXECUTION_CONTEXT_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_EXECUTION_CONTEXT_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_EXECUTION_CONTEXT_SCHEMA_VERSION,
}
OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-orchestration-cycle.sample.v1"
)
OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SCHEMA_VERSION = (
    "optimizer-job-orchestration-cycle.v1"
)
OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SCHEMA_VERSION,
}
OPTIMIZER_JOB_ERROR_SAMPLE_SCHEMA_VERSION = "optimizer-job-error.sample.v1"
OPTIMIZER_JOB_ERROR_SCHEMA_VERSION = "optimizer-job-error.v1"
OPTIMIZER_JOB_ERROR_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_ERROR_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_ERROR_SCHEMA_VERSION,
}
OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-artifact-retention-policy.sample.v1"
)
OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SCHEMA_VERSION = (
    "optimizer-job-artifact-retention-policy.v1"
)
OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SCHEMA_VERSION,
}
OPTIMIZER_RUN_SUMMARY_SAMPLE_SCHEMA_VERSION = "optimizer-run-summary.sample.v1"
OPTIMIZER_RUN_SUMMARY_SCHEMA_VERSION = "optimizer-run-summary.v1"
OPTIMIZER_RUN_SUMMARY_SCHEMA_VERSIONS = {
    OPTIMIZER_RUN_SUMMARY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUN_SUMMARY_SCHEMA_VERSION,
}
OPTIMIZER_JOB_ARTIFACT_EMISSION_MODES = {
    "inline_only",
    "write_through_output_root",
}
OPTIMIZER_JOB_ERROR_CODES = {
    "scheduled_job_failed",
    "input_resolution_failure",
    "rollout_policy_failure",
    "job_materialization_failure",
    "artifact_emission_failure",
    "scheduler_dispatch_failure",
    "execution_context_invalid",
    "orchestration_cycle_failed",
}
OPTIMIZER_JOB_ERROR_FAILURE_STAGES = {
    "schedule_resolution",
    "input_resolution",
    "rollout_policy_resolution",
    "job_materialization",
    "artifact_emission",
    "scheduler_dispatch",
    "orchestration_cycle",
}
OPTIMIZER_JOB_ERROR_OWNER_HINTS = {
    "scheduler_config",
    "input_pipeline",
    "rollout_policy",
    "optimizer_runner",
    "ops",
}
OPTIMIZER_JOB_ARTIFACT_RETENTION_TIERS = {
    "ephemeral",
    "operational",
    "audit",
    "failure_audit",
}
OPTIMIZER_RUN_SUMMARY_STATUSES = {
    "success",
    "partial_failure",
    "failed",
}
OPTIMIZER_SCHEDULER_COMPATIBILITY_RUNTIME_ROLE = "compatibility_rehearsal"
OPTIMIZER_SCHEDULER_COMPATIBILITY_PREFERRED_RECURRING_RUNTIME = "openclaw_cron"
OPTIMIZER_SCHEDULER_COMPATIBILITY_INTENDED_USES = [
    "fixture_generation",
    "deterministic_rehearsal",
    "cutover_validation",
]


def build_optimizer_job_execution_context_payload(
    *,
    execution_context_id: str,
    generated_at: str,
    schedule_plan_payload: dict[str, Any],
    schedule_plan_path: str,
    input_rollout_policy_payload: dict[str, Any] | None,
    input_rollout_policy_path: str | None,
    default_run_context: dict[str, Any],
    default_inputs: dict[str, Any],
    schedules: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": OPTIMIZER_JOB_EXECUTION_CONTEXT_SAMPLE_SCHEMA_VERSION,
        "executionContextId": execution_context_id,
        "generatedAt": generated_at,
        "runtimeRole": OPTIMIZER_SCHEDULER_COMPATIBILITY_RUNTIME_ROLE,
        "preferredRecurringRuntime": OPTIMIZER_SCHEDULER_COMPATIBILITY_PREFERRED_RECURRING_RUNTIME,
        "intendedUses": list(OPTIMIZER_SCHEDULER_COMPATIBILITY_INTENDED_USES),
        "generatedFrom": {
            "optimizerJobScheduleSchemaVersion": schedule_plan_payload.get(
                "schemaVersion"
            ),
            "optimizerJobSchedulePlanId": schedule_plan_payload.get("schedulePlanId"),
            "optimizerJobSchedulePath": schedule_plan_path,
            "optimizerInputRolloutPolicySchemaVersion": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("schemaVersion"),
            "optimizerInputRolloutPolicyId": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("policyId"),
            "optimizerInputRolloutPolicyPath": input_rollout_policy_path,
            "scheduleCount": len(schedule_plan_payload.get("schedules", [])),
            "enabledScheduleCount": sum(
                1 for schedule in schedules if schedule.get("enabled", True)
            ),
        },
        "defaultRunContext": default_run_context,
        "defaultInputs": default_inputs,
        "schedules": schedules,
    }


def build_optimizer_job_artifact_retention_policy_payload(
    *,
    policy_id: str,
    generated_at: str,
    artifact_policies: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SAMPLE_SCHEMA_VERSION,
        "policyId": policy_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "artifactPolicyCount": len(artifact_policies),
        },
        "artifactPolicies": artifact_policies,
    }


def build_optimizer_job_error_payload(
    *,
    error_id: str,
    generated_at: str,
    error_code: str,
    error_message: str,
    schedule_id: str,
    execution_context_id: str | None,
    schedule_plan_id: str | None,
    scheduler_run_id: str | None,
    trigger_kind: str | None,
    scheduler_owner: str | None,
    execution_environment: str | None,
    scheduler_rollout_intent: str | None,
    rollout_class: str | None,
    failure_stage: str,
    retryable: bool,
    owner_hint: str,
    failure_summary: str,
    job_kind: str | None = None,
    schedule_profile: str | None = None,
    runtime_profile_rollout_class: str | None = None,
    window_set_purpose: str | None = None,
    comparison_dimension: str | None = None,
) -> dict[str, Any]:
    return {
        "schemaVersion": OPTIMIZER_JOB_ERROR_SAMPLE_SCHEMA_VERSION,
        "errorId": error_id,
        "generatedAt": generated_at,
        "errorCode": error_code,
        "failureStage": failure_stage,
        "retryable": retryable,
        "ownerHint": owner_hint,
        "failureSummary": failure_summary,
        "errorMessage": error_message,
        "scheduleId": schedule_id,
        "generatedFrom": {
            "optimizerJobExecutionContextId": execution_context_id,
            "optimizerJobSchedulePlanId": schedule_plan_id,
            "optimizerJobSchedulerRunId": scheduler_run_id,
            "optimizerJobTriggerKind": trigger_kind,
            "optimizerJobSchedulerOwner": scheduler_owner,
            "optimizerJobExecutionEnvironment": execution_environment,
            "optimizerJobSchedulerRolloutIntent": scheduler_rollout_intent,
            "optimizerInputRolloutClass": rollout_class,
            "optimizerJobKind": job_kind,
            "optimizerJobScheduleProfile": schedule_profile,
            "optimizerJobRuntimeProfileRolloutClass": runtime_profile_rollout_class,
            "optimizerJobWindowSetPurpose": window_set_purpose,
            "optimizerJobComparisonDimension": comparison_dimension,
        },
    }


def _increment_counter(counter: dict[str, int], value: object) -> None:
    if isinstance(value, str) and value:
        counter[value] = counter.get(value, 0) + 1


def _sorted_counter(counter: dict[str, int]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _extract_production_run_runtime_summary(
    job_run_payload: dict[str, Any],
) -> dict[str, Any]:
    summary = job_run_payload.get("summary", {})
    offline_cycle = job_run_payload.get("artifacts", {}).get("offlineCycle", {})
    weekly_promotion = offline_cycle.get("artifacts", {}).get("weeklyPromotion")
    gate_summary = (
        weekly_promotion.get("gateSummary", {})
        if isinstance(weekly_promotion, dict)
        else {}
    )
    rollback_severity = gate_summary.get("rollbackSeverity")
    if not isinstance(rollback_severity, str) or not rollback_severity:
        rollback_severity = None
    return {
        "dailyRecommendation": summary.get("dailyRecommendation"),
        "weeklyDecision": summary.get("weeklyDecision"),
        "rollbackSeverity": rollback_severity,
        "selectedChallengerProfileId": summary.get("selectedChallengerProfileId"),
        "shadowLeaderProfileId": summary.get("shadowLeaderProfileId"),
    }


def build_optimizer_run_summary_payload(
    *,
    run_summary_id: str,
    generated_at: str,
    execution_context_payload: dict[str, Any],
    schedule_plan_payload: dict[str, Any],
    artifact_retention_policy_payload: dict[str, Any] | None,
    cycle_run_id: str,
    cycle_schema_version: str,
    job_runs: list[dict[str, Any]],
    shadow_compare_payload: dict[str, Any] | None,
    shadow_compare_batch_payload: dict[str, Any] | None,
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    schedule_catalog = {
        schedule["scheduleId"]: schedule
        for schedule in schedule_plan_payload.get("schedules", [])
        if isinstance(schedule, dict)
        and isinstance(schedule.get("scheduleId"), str)
        and schedule.get("scheduleId")
    }
    enabled_schedule_ids = [
        schedule["scheduleId"]
        for schedule in execution_context_payload.get("schedules", [])
        if isinstance(schedule, dict)
        and isinstance(schedule.get("scheduleId"), str)
        and schedule.get("scheduleId")
        and schedule.get("enabled", True)
    ]
    job_runs_by_schedule: dict[str, list[dict[str, Any]]] = {
        schedule_id: [] for schedule_id in enabled_schedule_ids
    }
    scheduler_rollout_intent_counts: dict[str, int] = {}
    weekly_decision_counts: dict[str, int] = {}
    rollback_severity_counts: dict[str, int] = {}
    production_job_run_count = 0
    shadow_job_run_count = 0
    for job_run in job_runs:
        schedule_id = job_run.get("scheduleId")
        if isinstance(schedule_id, str) and schedule_id:
            job_runs_by_schedule.setdefault(schedule_id, []).append(job_run)
        scheduler_rollout_intent = job_run.get("schedulerRolloutIntent")
        _increment_counter(scheduler_rollout_intent_counts, scheduler_rollout_intent)
        if scheduler_rollout_intent == "production":
            production_job_run_count += 1
            production_runtime_summary = _extract_production_run_runtime_summary(
                job_run.get("payload", {})
            )
            _increment_counter(
                weekly_decision_counts, production_runtime_summary.get("weeklyDecision")
            )
            _increment_counter(
                rollback_severity_counts,
                production_runtime_summary.get("rollbackSeverity"),
            )
        else:
            shadow_job_run_count += 1

    compare_entries = (
        []
        if shadow_compare_payload is None
        else shadow_compare_payload.get("comparisons", [])
    )
    compare_entries_by_schedule: dict[str, list[dict[str, Any]]] = {
        schedule_id: [] for schedule_id in enabled_schedule_ids
    }
    for entry in compare_entries:
        if not isinstance(entry, dict):
            continue
        schedule_id = entry.get("scheduleId")
        if isinstance(schedule_id, str) and schedule_id:
            compare_entries_by_schedule.setdefault(schedule_id, []).append(entry)

    error_entries_by_schedule: dict[str, list[dict[str, Any]]] = {
        schedule_id: [] for schedule_id in enabled_schedule_ids
    }
    for error in errors:
        if not isinstance(error, dict):
            continue
        schedule_id = error.get("scheduleId")
        if isinstance(schedule_id, str) and schedule_id:
            error_entries_by_schedule.setdefault(schedule_id, []).append(error)

    schedule_summaries: list[dict[str, Any]] = []
    successful_schedule_count = 0
    partial_failure_schedule_count = 0
    failed_schedule_count = 0
    for schedule_id in enabled_schedule_ids:
        schedule = schedule_catalog.get(schedule_id, {})
        schedule_job_runs = job_runs_by_schedule.get(schedule_id, [])
        production_entry = next(
            (
                entry
                for entry in schedule_job_runs
                if entry.get("schedulerRolloutIntent") == "production"
            ),
            None,
        )
        shadow_entries = [
            entry
            for entry in schedule_job_runs
            if entry.get("schedulerRolloutIntent") != "production"
        ]
        compare_items = compare_entries_by_schedule.get(schedule_id, [])
        schedule_errors = error_entries_by_schedule.get(schedule_id, [])
        if schedule_errors and not schedule_job_runs:
            schedule_status = "failed"
            failed_schedule_count += 1
        elif schedule_errors:
            schedule_status = "partial_failure"
            partial_failure_schedule_count += 1
        else:
            schedule_status = "success"
            successful_schedule_count += 1

        production_payload = (
            {}
            if production_entry is None
            else production_entry.get("payload", {})
        )
        production_runtime_summary = _extract_production_run_runtime_summary(
            production_payload
        )
        schedule_summaries.append(
            {
                "scheduleId": schedule_id,
                "cadenceKind": schedule.get("cadenceKind"),
                "jobKind": schedule.get("jobKind"),
                "status": schedule_status,
                "jobRunCount": len(schedule_job_runs),
                "productionJobRunId": None
                if production_entry is None
                else production_entry.get("payload", {}).get("jobRunId"),
                "productionSchedulerRolloutIntent": None
                if production_entry is None
                else production_entry.get("schedulerRolloutIntent"),
                "productionRolloutClass": None
                if production_entry is None
                else production_entry.get("rolloutClass"),
                "shadowJobRunCount": len(shadow_entries),
                "shadowSchedulerRolloutIntents": sorted(
                    {
                        entry["schedulerRolloutIntent"]
                        for entry in shadow_entries
                        if isinstance(entry.get("schedulerRolloutIntent"), str)
                        and entry.get("schedulerRolloutIntent")
                    }
                ),
                "shadowRolloutClasses": sorted(
                    {
                        entry["rolloutClass"]
                        for entry in shadow_entries
                        if isinstance(entry.get("rolloutClass"), str)
                        and entry.get("rolloutClass")
                    }
                ),
                "compareCount": len(compare_items),
                "mismatchedCompareCount": sum(
                    1 for item in compare_items if not item.get("semanticMatch", False)
                ),
                "productionDailyRecommendation": production_runtime_summary.get(
                    "dailyRecommendation"
                ),
                "productionWeeklyDecision": production_runtime_summary.get(
                    "weeklyDecision"
                ),
                "productionRollbackSeverity": production_runtime_summary.get(
                    "rollbackSeverity"
                ),
                "productionSelectedChallengerProfileId": production_runtime_summary.get(
                    "selectedChallengerProfileId"
                ),
                "productionShadowLeaderProfileId": production_runtime_summary.get(
                    "shadowLeaderProfileId"
                ),
            }
        )

    compare_summaries: list[dict[str, Any]] = []
    if shadow_compare_payload is not None:
        compare_summary = shadow_compare_payload.get("summary", {})
        compare_summaries.append(
            {
                "compareId": shadow_compare_payload.get("compareId"),
                "comparePlanId": shadow_compare_payload.get("generatedFrom", {}).get(
                    "optimizerJobShadowComparePlanId"
                ),
                "comparisonCount": compare_summary.get("comparisonCount"),
                "matchedComparisonCount": compare_summary.get("matchedComparisonCount"),
                "mismatchedComparisonCount": compare_summary.get(
                    "mismatchedComparisonCount"
                ),
                "candidateSchedulerRolloutIntents": sorted(
                    {
                        entry["candidate"]["schedulerRolloutIntent"]
                        for entry in compare_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("candidate"), dict)
                        and isinstance(
                            entry["candidate"].get("schedulerRolloutIntent"), str
                        )
                        and entry["candidate"].get("schedulerRolloutIntent")
                    }
                ),
                "candidateRolloutClasses": sorted(
                    {
                        entry["candidate"]["rolloutClass"]
                        for entry in compare_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("candidate"), dict)
                        and isinstance(entry["candidate"].get("rolloutClass"), str)
                        and entry["candidate"].get("rolloutClass")
                    }
                ),
                "candidateRuntimeProfileRolloutClasses": sorted(
                    {
                        entry["candidate"]["runtimeProfileRolloutClass"]
                        for entry in compare_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("candidate"), dict)
                        and isinstance(
                            entry["candidate"].get("runtimeProfileRolloutClass"), str
                        )
                        and entry["candidate"].get("runtimeProfileRolloutClass")
                    }
                ),
                "candidateWindowSetPurposes": sorted(
                    {
                        entry["candidate"]["windowSetPurpose"]
                        for entry in compare_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("candidate"), dict)
                        and isinstance(entry["candidate"].get("windowSetPurpose"), str)
                        and entry["candidate"].get("windowSetPurpose")
                    }
                ),
                "candidateComparisonDimensions": sorted(
                    {
                        entry["candidate"]["comparisonDimension"]
                        for entry in compare_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("candidate"), dict)
                        and isinstance(
                            entry["candidate"].get("comparisonDimension"), str
                        )
                        and entry["candidate"].get("comparisonDimension")
                    }
                ),
                "candidateSourceLanes": sorted(
                    {
                        entry["candidate"]["inputProvenance"]["optimizerInputSourceLane"]
                        for entry in compare_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("candidate"), dict)
                        and isinstance(entry["candidate"].get("inputProvenance"), dict)
                        and isinstance(
                            entry["candidate"]["inputProvenance"].get(
                                "optimizerInputSourceLane"
                            ),
                            str,
                        )
                        and entry["candidate"]["inputProvenance"].get(
                            "optimizerInputSourceLane"
                        )
                    }
                ),
            }
        )

    error_summaries = [
        {
            "errorId": error.get("errorId"),
            "errorCode": error.get("errorCode"),
            "scheduleId": error.get("scheduleId"),
            "failureStage": error.get("failureStage"),
            "retryable": error.get("retryable"),
            "ownerHint": error.get("ownerHint"),
            "failureSummary": error.get("failureSummary"),
        }
        for error in errors
        if isinstance(error, dict)
    ]

    compare_batch_summary = (
        {}
        if shadow_compare_batch_payload is None
        else shadow_compare_batch_payload.get("summary", {})
    )
    compare_artifact_count = 0 if shadow_compare_payload is None else 1
    compare_batch_count = 0 if shadow_compare_batch_payload is None else 1
    if failed_schedule_count == len(enabled_schedule_ids) and enabled_schedule_ids:
        run_status = "failed"
    elif failed_schedule_count or partial_failure_schedule_count or errors:
        run_status = "partial_failure"
    else:
        run_status = "success"

    return {
        "schemaVersion": OPTIMIZER_RUN_SUMMARY_SAMPLE_SCHEMA_VERSION,
        "runSummaryId": run_summary_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "optimizerJobExecutionContextSchemaVersion": execution_context_payload.get(
                "schemaVersion"
            ),
            "optimizerJobExecutionContextId": execution_context_payload.get(
                "executionContextId"
            ),
            "optimizerJobScheduleSchemaVersion": schedule_plan_payload.get(
                "schemaVersion"
            ),
            "optimizerJobSchedulePlanId": schedule_plan_payload.get("schedulePlanId"),
            "optimizerJobOrchestrationCycleSchemaVersion": cycle_schema_version,
            "optimizerJobOrchestrationCycleId": cycle_run_id,
            "optimizerJobArtifactRetentionPolicySchemaVersion": None
            if artifact_retention_policy_payload is None
            else artifact_retention_policy_payload.get("schemaVersion"),
            "optimizerJobArtifactRetentionPolicyId": None
            if artifact_retention_policy_payload is None
            else artifact_retention_policy_payload.get("policyId"),
            "scheduleCount": len(enabled_schedule_ids),
            "jobRunCount": len(job_runs),
            "errorCount": len(error_summaries),
            "compareArtifactCount": compare_artifact_count,
            "compareBatchCount": compare_batch_count,
        },
        "summary": {
            "runStatus": run_status,
            "scheduleCount": len(enabled_schedule_ids),
            "successfulScheduleCount": successful_schedule_count,
            "partialFailureScheduleCount": partial_failure_schedule_count,
            "failedScheduleCount": failed_schedule_count,
            "jobRunCount": len(job_runs),
            "productionJobRunCount": production_job_run_count,
            "shadowJobRunCount": shadow_job_run_count,
            "compareArtifactCount": compare_artifact_count,
            "compareBatchCount": compare_batch_count,
            "matchedComparisonCount": compare_batch_summary.get(
                "matchedComparisonCount",
                0
                if shadow_compare_payload is None
                else shadow_compare_payload.get("summary", {}).get(
                    "matchedComparisonCount", 0
                ),
            ),
            "mismatchedComparisonCount": compare_batch_summary.get(
                "mismatchedComparisonCount",
                0
                if shadow_compare_payload is None
                else shadow_compare_payload.get("summary", {}).get(
                    "mismatchedComparisonCount", 0
                ),
            ),
            "retentionPolicyId": None
            if artifact_retention_policy_payload is None
            else artifact_retention_policy_payload.get("policyId"),
            "schedulerRolloutIntentCounts": _sorted_counter(
                scheduler_rollout_intent_counts
            ),
            "weeklyDecisionCounts": _sorted_counter(weekly_decision_counts),
            "rollbackSeverityCounts": _sorted_counter(rollback_severity_counts),
        },
        "scheduleSummaries": schedule_summaries,
        "compareSummaries": compare_summaries,
        "errorSummaries": error_summaries,
    }


def build_optimizer_job_orchestration_cycle_payload(
    *,
    cycle_run_id: str,
    generated_at: str,
    execution_context_payload: dict[str, Any],
    schedule_plan_payload: dict[str, Any],
    input_rollout_policy_payload: dict[str, Any] | None,
    artifact_retention_policy_payload: dict[str, Any] | None,
    run_summary_payload: dict[str, Any] | None,
    job_runs: list[dict[str, Any]],
    shadow_compare_plan_payload: dict[str, Any] | None,
    shadow_compare_payload: dict[str, Any] | None,
    shadow_compare_batch_payload: dict[str, Any] | None,
    errors: list[dict[str, Any]],
    artifact_emission_mode: str,
) -> dict[str, Any]:
    executed_schedule_ids = sorted(
        {
            entry.get("scheduleId")
            for entry in job_runs
            if isinstance(entry.get("scheduleId"), str) and entry.get("scheduleId")
        }
    )
    shadow_compared_schedule_ids = sorted(
        {
            entry.get("scheduleId")
            for entry in (
                []
                if shadow_compare_payload is None
                else shadow_compare_payload.get("comparisons", [])
            )
            if isinstance(entry.get("scheduleId"), str) and entry.get("scheduleId")
        }
    )
    retention_managed_artifact_kinds = sorted(
        {
            policy.get("artifactKind")
            for policy in (
                []
                if artifact_retention_policy_payload is None
                else artifact_retention_policy_payload.get("artifactPolicies", [])
            )
            if isinstance(policy, dict)
            and isinstance(policy.get("artifactKind"), str)
            and policy.get("artifactKind")
        }
    )
    return {
        "schemaVersion": OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SAMPLE_SCHEMA_VERSION,
        "cycleRunId": cycle_run_id,
        "generatedAt": generated_at,
        "runtimeRole": OPTIMIZER_SCHEDULER_COMPATIBILITY_RUNTIME_ROLE,
        "preferredRecurringRuntime": OPTIMIZER_SCHEDULER_COMPATIBILITY_PREFERRED_RECURRING_RUNTIME,
        "intendedUses": list(OPTIMIZER_SCHEDULER_COMPATIBILITY_INTENDED_USES),
        "generatedFrom": {
            "optimizerJobExecutionContextSchemaVersion": execution_context_payload.get(
                "schemaVersion"
            ),
            "optimizerJobExecutionContextId": execution_context_payload.get(
                "executionContextId"
            ),
            "optimizerJobScheduleSchemaVersion": schedule_plan_payload.get(
                "schemaVersion"
            ),
            "optimizerJobSchedulePlanId": schedule_plan_payload.get("schedulePlanId"),
            "optimizerInputRolloutPolicySchemaVersion": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("schemaVersion"),
            "optimizerInputRolloutPolicyId": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("policyId"),
            "optimizerJobArtifactRetentionPolicySchemaVersion": None
            if artifact_retention_policy_payload is None
            else artifact_retention_policy_payload.get("schemaVersion"),
            "optimizerJobArtifactRetentionPolicyId": None
            if artifact_retention_policy_payload is None
            else artifact_retention_policy_payload.get("policyId"),
            "scheduleCount": len(execution_context_payload.get("schedules", [])),
            "jobRunCount": len(job_runs),
            "shadowComparisonCount": 0
            if shadow_compare_payload is None
            else len(shadow_compare_payload.get("comparisons", [])),
            "errorCount": len(errors),
        },
        "summary": {
            "scheduleCount": len(execution_context_payload.get("schedules", [])),
            "executedScheduleCount": len(executed_schedule_ids),
            "shadowComparedScheduleCount": len(shadow_compared_schedule_ids),
            "jobRunCount": len(job_runs),
            "compareArtifactCount": 0 if shadow_compare_payload is None else 1,
            "compareBatchCount": 0 if shadow_compare_batch_payload is None else 1,
            "errorCount": len(errors),
            "artifactEmissionMode": artifact_emission_mode,
            "executedScheduleIds": executed_schedule_ids,
            "shadowComparedScheduleIds": shadow_compared_schedule_ids,
            "retentionPolicyId": None
            if artifact_retention_policy_payload is None
            else artifact_retention_policy_payload.get("policyId"),
            "retentionManagedArtifactCount": len(retention_managed_artifact_kinds),
            "retentionManagedArtifactKinds": retention_managed_artifact_kinds,
        },
        "artifacts": {
            "jobRuns": job_runs,
            "shadowComparePlan": shadow_compare_plan_payload,
            "shadowCompare": shadow_compare_payload,
            "shadowCompareBatch": shadow_compare_batch_payload,
            "retentionPolicy": artifact_retention_policy_payload,
            "runSummary": run_summary_payload,
            "errors": errors,
        },
    }


def _validate_non_empty_string(value: object, *, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")


def validate_optimizer_job_execution_context_payload(payload: dict[str, Any]) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_JOB_EXECUTION_CONTEXT_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer job execution context must declare a supported schemaVersion"
        )
    _validate_non_empty_string(
        payload.get("executionContextId"), label="executionContextId"
    )
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    if payload.get("runtimeRole") != OPTIMIZER_SCHEDULER_COMPATIBILITY_RUNTIME_ROLE:
        raise ValueError(
            "optimizer job execution context must declare compatibility_rehearsal runtimeRole"
        )
    if (
        payload.get("preferredRecurringRuntime")
        != OPTIMIZER_SCHEDULER_COMPATIBILITY_PREFERRED_RECURRING_RUNTIME
    ):
        raise ValueError(
            "optimizer job execution context must declare openclaw_cron as preferredRecurringRuntime"
        )
    if payload.get("intendedUses") != OPTIMIZER_SCHEDULER_COMPATIBILITY_INTENDED_USES:
        raise ValueError(
            "optimizer job execution context must declare the committed compatibility intendedUses"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job execution context must declare generatedFrom"
        )
    _validate_non_empty_string(
        generated_from.get("optimizerJobSchedulePlanId"),
        label="generatedFrom.optimizerJobSchedulePlanId",
    )
    default_run_context = payload.get("defaultRunContext")
    if not isinstance(default_run_context, dict):
        raise ValueError(
            "optimizer job execution context must declare defaultRunContext"
        )
    _validate_non_empty_string(
        default_run_context.get("schedulerRunId"),
        label="defaultRunContext.schedulerRunId",
    )
    _validate_non_empty_string(
        default_run_context.get("triggerKind"),
        label="defaultRunContext.triggerKind",
    )
    _validate_non_empty_string(
        default_run_context.get("schedulerOwner"),
        label="defaultRunContext.schedulerOwner",
    )
    _validate_non_empty_string(
        default_run_context.get("executionEnvironment"),
        label="defaultRunContext.executionEnvironment",
    )
    artifact_emission_mode = default_run_context.get("artifactEmissionMode")
    if artifact_emission_mode not in OPTIMIZER_JOB_ARTIFACT_EMISSION_MODES:
        raise ValueError(
            "optimizer job execution context must use a supported artifactEmissionMode"
        )
    output_root = default_run_context.get("outputRoot")
    if artifact_emission_mode == "write_through_output_root":
        _validate_non_empty_string(
            output_root, label="defaultRunContext.outputRoot"
        )
    elif output_root is not None and (
        not isinstance(output_root, str) or not output_root
    ):
        raise ValueError(
            "defaultRunContext.outputRoot must be null or a non-empty string"
        )
    for field_name in (
        "emitShadowCompare",
        "emitCompareBatch",
        "emitErrorArtifact",
    ):
        if not isinstance(default_run_context.get(field_name), bool):
            raise ValueError(
                f"defaultRunContext.{field_name} must be a boolean"
            )

    default_inputs = payload.get("defaultInputs")
    if not isinstance(default_inputs, dict):
        raise ValueError("optimizer job execution context must declare defaultInputs")
    if default_inputs.get("inputManifestPath") is None and default_inputs.get(
        "inputBundlePath"
    ) is None:
        raise ValueError(
            "optimizer job execution context defaultInputs must declare inputManifestPath or inputBundlePath"
        )
    for optional_path_field in (
        "inputManifestPath",
        "inputBundlePath",
        "policyPath",
        "inputSourceRegistryPath",
        "inputRolloutPolicyPath",
        "weeklyReviewWindowPath",
    ):
        value = default_inputs.get(optional_path_field)
        if value is not None and (not isinstance(value, str) or not value):
            raise ValueError(
                f"defaultInputs.{optional_path_field} must be null or a non-empty string"
            )

    schedules = payload.get("schedules")
    if not isinstance(schedules, list) or not schedules:
        raise ValueError("optimizer job execution context must declare schedules")
    enabled_schedule_count = 0
    seen_schedule_ids: set[str] = set()
    for schedule in schedules:
        if not isinstance(schedule, dict):
            raise ValueError(
                "optimizer job execution context schedules must be objects"
            )
        schedule_id = schedule.get("scheduleId")
        _validate_non_empty_string(schedule_id, label="schedule.scheduleId")
        if schedule_id in seen_schedule_ids:
            raise ValueError(f"duplicate execution context scheduleId {schedule_id}")
        seen_schedule_ids.add(schedule_id)
        enabled = schedule.get("enabled")
        if not isinstance(enabled, bool):
            raise ValueError(
                f"optimizer job execution context schedule {schedule_id} must declare enabled"
            )
        if enabled:
            enabled_schedule_count += 1
        for path_field in (
            "inputManifestPath",
            "inputBundlePath",
            "policyPath",
            "inputSourceRegistryPath",
            "inputRolloutPolicyPath",
            "weeklyReviewWindowPath",
        ):
            value = schedule.get(path_field)
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError(
                    f"optimizer job execution context schedule {schedule_id} {path_field} must be null or a non-empty string"
                )
        production_rollout_class = schedule.get("productionRolloutClass")
        production_scheduler_rollout_intent = schedule.get(
            "productionSchedulerRolloutIntent"
        )
        if production_scheduler_rollout_intent is not None:
            _validate_non_empty_string(
                production_scheduler_rollout_intent,
                label=f"schedule {schedule_id} productionSchedulerRolloutIntent",
            )
        if production_rollout_class is not None:
            _validate_non_empty_string(
                production_rollout_class,
                label=f"schedule {schedule_id} productionRolloutClass",
            )
        shadow_rollout_class = schedule.get("shadowRolloutClass")
        shadow_scheduler_rollout_intent = schedule.get("shadowSchedulerRolloutIntent")
        if shadow_scheduler_rollout_intent is not None:
            _validate_non_empty_string(
                shadow_scheduler_rollout_intent,
                label=f"schedule {schedule_id} shadowSchedulerRolloutIntent",
            )
        if shadow_rollout_class is not None:
            _validate_non_empty_string(
                shadow_rollout_class,
                label=f"schedule {schedule_id} shadowRolloutClass",
            )
            _validate_non_empty_string(
                schedule.get("comparisonId"),
                label=f"schedule {schedule_id} comparisonId",
            )
        if (
            shadow_scheduler_rollout_intent is not None
            and shadow_rollout_class is None
        ):
            raise ValueError(
                f"optimizer job execution context schedule {schedule_id} shadowSchedulerRolloutIntent requires shadowRolloutClass"
            )
        comparison_id = schedule.get("comparisonId")
        if comparison_id is not None and (
            not isinstance(comparison_id, str) or not comparison_id
        ):
            raise ValueError(
                f"optimizer job execution context schedule {schedule_id} comparisonId must be null or a non-empty string"
            )
    if generated_from.get("enabledScheduleCount") != enabled_schedule_count:
        raise ValueError(
            "optimizer job execution context enabledScheduleCount mismatch"
        )


def validate_optimizer_job_error_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") not in OPTIMIZER_JOB_ERROR_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer job error payload must declare a supported schemaVersion"
        )
    _validate_non_empty_string(payload.get("errorId"), label="errorId")
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    error_code = payload.get("errorCode")
    if error_code not in OPTIMIZER_JOB_ERROR_CODES:
        raise ValueError(
            "optimizer job error payload must use a supported errorCode"
        )
    failure_stage = payload.get("failureStage")
    if failure_stage not in OPTIMIZER_JOB_ERROR_FAILURE_STAGES:
        raise ValueError(
            "optimizer job error payload must use a supported failureStage"
        )
    if not isinstance(payload.get("retryable"), bool):
        raise ValueError("optimizer job error payload retryable must be a boolean")
    owner_hint = payload.get("ownerHint")
    if owner_hint not in OPTIMIZER_JOB_ERROR_OWNER_HINTS:
        raise ValueError(
            "optimizer job error payload must use a supported ownerHint"
        )
    _validate_non_empty_string(
        payload.get("failureSummary"), label="failureSummary"
    )
    _validate_non_empty_string(payload.get("errorMessage"), label="errorMessage")
    _validate_non_empty_string(payload.get("scheduleId"), label="scheduleId")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError("optimizer job error payload must declare generatedFrom")


def validate_optimizer_job_artifact_retention_policy_payload(
    payload: dict[str, Any]
) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_JOB_ARTIFACT_RETENTION_POLICY_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer job artifact retention policy must declare a supported schemaVersion"
        )
    _validate_non_empty_string(payload.get("policyId"), label="policyId")
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job artifact retention policy must declare generatedFrom"
        )
    artifact_policies = payload.get("artifactPolicies")
    if not isinstance(artifact_policies, list) or not artifact_policies:
        raise ValueError(
            "optimizer job artifact retention policy must declare artifactPolicies"
        )
    if generated_from.get("artifactPolicyCount") != len(artifact_policies):
        raise ValueError(
            "optimizer job artifact retention policy artifactPolicyCount mismatch"
        )
    seen_artifact_kinds: set[str] = set()
    for policy in artifact_policies:
        if not isinstance(policy, dict):
            raise ValueError(
                "optimizer job artifact retention policy entries must be objects"
            )
        artifact_kind = policy.get("artifactKind")
        _validate_non_empty_string(artifact_kind, label="artifactPolicy.artifactKind")
        if artifact_kind in seen_artifact_kinds:
            raise ValueError(
                f"duplicate optimizer job artifact retention policy artifactKind {artifact_kind}"
            )
        seen_artifact_kinds.add(artifact_kind)
        retention_tier = policy.get("retentionTier")
        if retention_tier not in OPTIMIZER_JOB_ARTIFACT_RETENTION_TIERS:
            raise ValueError(
                "optimizer job artifact retention policy must use a supported retentionTier"
            )
        keep_latest_count = policy.get("keepLatestCount")
        if not isinstance(keep_latest_count, int) or keep_latest_count < 0:
            raise ValueError(
                "optimizer job artifact retention policy keepLatestCount must be a non-negative integer"
            )
        if not isinstance(policy.get("keepFailureArtifacts"), bool):
            raise ValueError(
                "optimizer job artifact retention policy keepFailureArtifacts must be a boolean"
            )
        partition_dimensions = policy.get("partitionDimensions")
        if not isinstance(partition_dimensions, list):
            raise ValueError(
                "optimizer job artifact retention policy partitionDimensions must be a list"
            )
        for dimension in partition_dimensions:
            _validate_non_empty_string(
                dimension, label="artifactPolicy.partitionDimensions[]"
            )


def validate_optimizer_job_orchestration_cycle_payload(payload: dict[str, Any]) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_JOB_ORCHESTRATION_CYCLE_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer job orchestration cycle must declare a supported schemaVersion"
        )
    _validate_non_empty_string(payload.get("cycleRunId"), label="cycleRunId")
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    if payload.get("runtimeRole") != OPTIMIZER_SCHEDULER_COMPATIBILITY_RUNTIME_ROLE:
        raise ValueError(
            "optimizer job orchestration cycle must declare compatibility_rehearsal runtimeRole"
        )
    if (
        payload.get("preferredRecurringRuntime")
        != OPTIMIZER_SCHEDULER_COMPATIBILITY_PREFERRED_RECURRING_RUNTIME
    ):
        raise ValueError(
            "optimizer job orchestration cycle must declare openclaw_cron as preferredRecurringRuntime"
        )
    if payload.get("intendedUses") != OPTIMIZER_SCHEDULER_COMPATIBILITY_INTENDED_USES:
        raise ValueError(
            "optimizer job orchestration cycle must declare the committed compatibility intendedUses"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job orchestration cycle must declare generatedFrom"
        )
    _validate_non_empty_string(
        generated_from.get("optimizerJobExecutionContextId"),
        label="generatedFrom.optimizerJobExecutionContextId",
    )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("optimizer job orchestration cycle must declare summary")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("optimizer job orchestration cycle must declare artifacts")
    run_summary = artifacts.get("runSummary")
    if run_summary is not None:
        if not isinstance(run_summary, dict):
            raise ValueError(
                "optimizer job orchestration cycle artifacts.runSummary must be an object when present"
            )
        validate_optimizer_run_summary_payload(run_summary)
        if (
            run_summary.get("generatedFrom", {}).get("optimizerJobOrchestrationCycleId")
            != payload.get("cycleRunId")
        ):
            raise ValueError(
                "optimizer job orchestration cycle run summary must reference the containing cycleRunId"
            )
        if run_summary.get("generatedFrom", {}).get(
            "optimizerJobExecutionContextId"
        ) != generated_from.get("optimizerJobExecutionContextId"):
            raise ValueError(
                "optimizer job orchestration cycle run summary execution context mismatch"
            )
        run_summary_summary = run_summary.get("summary", {})
        if run_summary_summary.get("jobRunCount") != summary.get("jobRunCount"):
            raise ValueError(
                "optimizer job orchestration cycle run summary jobRunCount mismatch"
            )
        if run_summary_summary.get("compareArtifactCount") != summary.get(
            "compareArtifactCount"
        ):
            raise ValueError(
                "optimizer job orchestration cycle run summary compareArtifactCount mismatch"
            )
        if run_summary_summary.get("compareBatchCount") != summary.get(
            "compareBatchCount"
        ):
            raise ValueError(
                "optimizer job orchestration cycle run summary compareBatchCount mismatch"
            )
    retention_policy = artifacts.get("retentionPolicy")
    if retention_policy is not None:
        if not isinstance(retention_policy, dict):
            raise ValueError(
                "optimizer job orchestration cycle artifacts.retentionPolicy must be an object when present"
            )
        validate_optimizer_job_artifact_retention_policy_payload(retention_policy)
        if generated_from.get("optimizerJobArtifactRetentionPolicyId") != retention_policy.get(
            "policyId"
        ):
            raise ValueError(
                "optimizer job orchestration cycle retention policy id mismatch"
            )
        if generated_from.get(
            "optimizerJobArtifactRetentionPolicySchemaVersion"
        ) != retention_policy.get("schemaVersion"):
            raise ValueError(
                "optimizer job orchestration cycle retention policy schemaVersion mismatch"
            )
        managed_artifact_kinds = sorted(
            {
                policy.get("artifactKind")
                for policy in retention_policy.get("artifactPolicies", [])
                if isinstance(policy, dict)
                and isinstance(policy.get("artifactKind"), str)
                and policy.get("artifactKind")
            }
        )
        if summary.get("retentionPolicyId") != retention_policy.get("policyId"):
            raise ValueError(
                "optimizer job orchestration cycle summary retentionPolicyId mismatch"
            )
        if summary.get("retentionManagedArtifactKinds") != managed_artifact_kinds:
            raise ValueError(
                "optimizer job orchestration cycle summary retentionManagedArtifactKinds mismatch"
            )
        if summary.get("retentionManagedArtifactCount") != len(managed_artifact_kinds):
            raise ValueError(
                "optimizer job orchestration cycle summary retentionManagedArtifactCount mismatch"
            )
    job_runs = artifacts.get("jobRuns")
    if not isinstance(job_runs, list):
        raise ValueError(
            "optimizer job orchestration cycle artifacts.jobRuns must be a list"
        )
    errors = artifacts.get("errors")
    if not isinstance(errors, list):
        raise ValueError(
            "optimizer job orchestration cycle artifacts.errors must be a list"
        )
    for error in errors:
        if not isinstance(error, dict):
            raise ValueError(
                "optimizer job orchestration cycle errors must be objects"
            )
        validate_optimizer_job_error_payload(error)


def validate_optimizer_run_summary_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") not in OPTIMIZER_RUN_SUMMARY_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer run summary must declare a supported schemaVersion"
        )
    _validate_non_empty_string(payload.get("runSummaryId"), label="runSummaryId")
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError("optimizer run summary must declare generatedFrom")
    for field_name in (
        "optimizerJobExecutionContextId",
        "optimizerJobSchedulePlanId",
        "optimizerJobOrchestrationCycleId",
    ):
        _validate_non_empty_string(generated_from.get(field_name), label=field_name)
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("optimizer run summary must declare summary")
    if summary.get("runStatus") not in OPTIMIZER_RUN_SUMMARY_STATUSES:
        raise ValueError("optimizer run summary must declare a supported runStatus")
    schedule_summaries = payload.get("scheduleSummaries")
    if not isinstance(schedule_summaries, list) or not schedule_summaries:
        raise ValueError("optimizer run summary must declare scheduleSummaries")
    compare_summaries = payload.get("compareSummaries")
    if not isinstance(compare_summaries, list):
        raise ValueError("optimizer run summary must declare compareSummaries")
    error_summaries = payload.get("errorSummaries")
    if not isinstance(error_summaries, list):
        raise ValueError("optimizer run summary must declare errorSummaries")
    if generated_from.get("scheduleCount") != len(schedule_summaries):
        raise ValueError("optimizer run summary scheduleCount mismatch")
    if generated_from.get("errorCount") != len(error_summaries):
        raise ValueError("optimizer run summary errorCount mismatch")
    if generated_from.get("compareArtifactCount") != len(compare_summaries):
        raise ValueError("optimizer run summary compareArtifactCount mismatch")
    if summary.get("scheduleCount") != len(schedule_summaries):
        raise ValueError("optimizer run summary summary.scheduleCount mismatch")
    if (
        summary.get("successfulScheduleCount", 0)
        + summary.get("partialFailureScheduleCount", 0)
        + summary.get("failedScheduleCount", 0)
        != len(schedule_summaries)
    ):
        raise ValueError(
            "optimizer run summary schedule status counts must add up to scheduleCount"
        )
    for index, schedule_summary in enumerate(schedule_summaries):
        if not isinstance(schedule_summary, dict):
            raise ValueError("optimizer run summary scheduleSummaries must be objects")
        label = f"scheduleSummaries[{index}]"
        for field_name in ("scheduleId", "cadenceKind", "jobKind", "status"):
            _validate_non_empty_string(
                schedule_summary.get(field_name), label=f"{label}.{field_name}"
            )
        if schedule_summary.get("status") not in OPTIMIZER_RUN_SUMMARY_STATUSES:
            raise ValueError(f"{label}.status must be a supported run status")
        for field_name in ("jobRunCount", "shadowJobRunCount", "compareCount", "mismatchedCompareCount"):
            if not isinstance(schedule_summary.get(field_name), int) or schedule_summary.get(field_name) < 0:
                raise ValueError(
                    f"{label}.{field_name} must be a non-negative integer"
                )
        for list_field in ("shadowSchedulerRolloutIntents", "shadowRolloutClasses"):
            if not isinstance(schedule_summary.get(list_field), list):
                raise ValueError(f"{label}.{list_field} must be a list")
    for index, compare_summary in enumerate(compare_summaries):
        if not isinstance(compare_summary, dict):
            raise ValueError("optimizer run summary compareSummaries must be objects")
        label = f"compareSummaries[{index}]"
        _validate_non_empty_string(compare_summary.get("compareId"), label=f"{label}.compareId")
        for field_name in (
            "comparisonCount",
            "matchedComparisonCount",
            "mismatchedComparisonCount",
        ):
            if not isinstance(compare_summary.get(field_name), int) or compare_summary.get(field_name) < 0:
                raise ValueError(
                    f"{label}.{field_name} must be a non-negative integer"
                )
    for index, error_summary in enumerate(error_summaries):
        if not isinstance(error_summary, dict):
            raise ValueError("optimizer run summary errorSummaries must be objects")
        label = f"errorSummaries[{index}]"
        for field_name in ("errorId", "errorCode", "scheduleId", "failureStage", "ownerHint", "failureSummary"):
            _validate_non_empty_string(
                error_summary.get(field_name), label=f"{label}.{field_name}"
            )
        if not isinstance(error_summary.get("retryable"), bool):
            raise ValueError(f"{label}.retryable must be a boolean")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"optimizer artifact not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"optimizer artifact is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"optimizer artifact must be a JSON object: {path}")
    return payload


def load_optimizer_job_execution_context(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    validate_optimizer_job_execution_context_payload(payload)
    return payload


def load_optimizer_job_error(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    validate_optimizer_job_error_payload(payload)
    return payload


def load_optimizer_job_artifact_retention_policy(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    validate_optimizer_job_artifact_retention_policy_payload(payload)
    return payload


def load_optimizer_run_summary(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    validate_optimizer_run_summary_payload(payload)
    return payload


def load_optimizer_job_orchestration_cycle(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    validate_optimizer_job_orchestration_cycle_payload(payload)
    return payload
