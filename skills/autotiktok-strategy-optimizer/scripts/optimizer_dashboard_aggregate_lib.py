#!/usr/bin/env python3
"""
Helpers for dashboard-facing optimizer aggregate artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from optimizer_job_orchestration_lib import (
    load_optimizer_job_error,
    load_optimizer_job_orchestration_cycle,
    validate_optimizer_job_error_payload,
    validate_optimizer_job_orchestration_cycle_payload,
    validate_optimizer_run_summary_payload,
)
from optimizer_job_shadow_compare_lib import (
    load_optimizer_job_shadow_compare_batch,
    validate_optimizer_job_shadow_compare_batch_payload,
)


OPTIMIZER_RECENT_RUN_SUMMARIES_SAMPLE_SCHEMA_VERSION = (
    "optimizer-recent-run-summaries.sample.v1"
)
OPTIMIZER_RECENT_RUN_SUMMARIES_SCHEMA_VERSION = "optimizer-recent-run-summaries.v1"
OPTIMIZER_RECENT_RUN_SUMMARIES_SCHEMA_VERSIONS = {
    OPTIMIZER_RECENT_RUN_SUMMARIES_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RECENT_RUN_SUMMARIES_SCHEMA_VERSION,
}

OPTIMIZER_RECENT_COMPARE_SUMMARIES_SAMPLE_SCHEMA_VERSION = (
    "optimizer-recent-compare-summaries.sample.v1"
)
OPTIMIZER_RECENT_COMPARE_SUMMARIES_SCHEMA_VERSION = (
    "optimizer-recent-compare-summaries.v1"
)
OPTIMIZER_RECENT_COMPARE_SUMMARIES_SCHEMA_VERSIONS = {
    OPTIMIZER_RECENT_COMPARE_SUMMARIES_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RECENT_COMPARE_SUMMARIES_SCHEMA_VERSION,
}

OPTIMIZER_RECENT_WEEKLY_DECISIONS_SAMPLE_SCHEMA_VERSION = (
    "optimizer-recent-weekly-decisions.sample.v1"
)
OPTIMIZER_RECENT_WEEKLY_DECISIONS_SCHEMA_VERSION = (
    "optimizer-recent-weekly-decisions.v1"
)
OPTIMIZER_RECENT_WEEKLY_DECISIONS_SCHEMA_VERSIONS = {
    OPTIMIZER_RECENT_WEEKLY_DECISIONS_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RECENT_WEEKLY_DECISIONS_SCHEMA_VERSION,
}

OPTIMIZER_RECENT_FAILURE_SUMMARIES_SAMPLE_SCHEMA_VERSION = (
    "optimizer-recent-failure-summaries.sample.v1"
)
OPTIMIZER_RECENT_FAILURE_SUMMARIES_SCHEMA_VERSION = (
    "optimizer-recent-failure-summaries.v1"
)
OPTIMIZER_RECENT_FAILURE_SUMMARIES_SCHEMA_VERSIONS = {
    OPTIMIZER_RECENT_FAILURE_SUMMARIES_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RECENT_FAILURE_SUMMARIES_SCHEMA_VERSION,
}

OPTIMIZER_RECENT_RUN_SUMMARY_STATUSES = {
    "success",
    "partial_failure",
    "failed",
}

OPTIMIZER_RECENT_WEEKLY_DECISIONS = {
    "promote",
    "keep",
    "rollback_champion",
}

OPTIMIZER_RECENT_ROLLBACK_SEVERITIES = {
    "none",
    "watch",
    "warning",
    "critical",
}


def _validate_non_empty_string(value: object, *, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_optional_string(value: object, *, label: str) -> None:
    if value is not None and (not isinstance(value, str) or not value):
        raise ValueError(f"{label} must be null or a non-empty string")


def _validate_string_list(value: object, *, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    rendered: list[str] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, str) or not entry:
            raise ValueError(f"{label}[{index}] must be a non-empty string")
        rendered.append(entry)
    return rendered


def _validate_counter(value: object, *, label: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    for key, count in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{label} keys must be non-empty strings")
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"{label}.{key} must be a non-negative integer")


def _increment_counter(counter: dict[str, int], value: object, *, amount: int = 1) -> None:
    if isinstance(value, str) and value:
        counter[value] = counter.get(value, 0) + amount


def _merge_counter(counter: dict[str, int], incoming: object) -> None:
    if not isinstance(incoming, dict):
        return
    for key, count in incoming.items():
        if isinstance(key, str) and key and isinstance(count, int) and count >= 0:
            counter[key] = counter.get(key, 0) + count


def _sorted_counter(counter: dict[str, int]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _sorted_unique_strings(values: set[str]) -> list[str]:
    return sorted(value for value in values if value)


def _sort_entries(entries: list[dict[str, Any]], *, id_key: str) -> list[dict[str, Any]]:
    return sorted(
        entries,
        key=lambda entry: (
            str(entry.get("generatedAt", "")),
            str(entry.get(id_key, "")),
        ),
        reverse=True,
    )


def build_optimizer_recent_run_summaries_payload(
    *,
    aggregate_id: str,
    generated_at: str,
    cycle_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    cycle_ids: set[str] = set()
    run_summary_ids: set[str] = set()
    run_summary_schema_versions: set[str] = set()
    run_status_counts: dict[str, int] = {}
    scheduler_rollout_intent_counts: dict[str, int] = {}
    weekly_decision_counts: dict[str, int] = {}
    rollback_severity_counts: dict[str, int] = {}
    total_schedule_count = 0
    total_job_run_count = 0
    total_production_job_run_count = 0
    total_shadow_job_run_count = 0
    total_compare_artifact_count = 0
    total_compare_batch_count = 0
    total_error_count = 0

    for cycle_payload in cycle_payloads:
        validate_optimizer_job_orchestration_cycle_payload(cycle_payload)
        cycle_id = cycle_payload.get("cycleRunId")
        if isinstance(cycle_id, str) and cycle_id:
            cycle_ids.add(cycle_id)
        run_summary = cycle_payload.get("artifacts", {}).get("runSummary")
        if not isinstance(run_summary, dict):
            raise ValueError(
                "optimizer job orchestration cycle must embed artifacts.runSummary"
            )
        validate_optimizer_run_summary_payload(run_summary)
        run_summary_id = run_summary.get("runSummaryId")
        run_summary_ids.add(run_summary_id)
        run_summary_schema_versions.add(run_summary.get("schemaVersion"))
        summary = run_summary.get("summary", {})
        schedule_summaries = run_summary.get("scheduleSummaries", [])
        error_summaries = run_summary.get("errorSummaries", [])
        run_status = summary.get("runStatus")
        _increment_counter(run_status_counts, run_status)
        _merge_counter(
            scheduler_rollout_intent_counts,
            summary.get("schedulerRolloutIntentCounts"),
        )
        _merge_counter(weekly_decision_counts, summary.get("weeklyDecisionCounts"))
        _merge_counter(rollback_severity_counts, summary.get("rollbackSeverityCounts"))
        total_schedule_count += (
            summary.get("scheduleCount", 0)
            if isinstance(summary.get("scheduleCount"), int)
            else 0
        )
        total_job_run_count += (
            summary.get("jobRunCount", 0)
            if isinstance(summary.get("jobRunCount"), int)
            else 0
        )
        total_production_job_run_count += (
            summary.get("productionJobRunCount", 0)
            if isinstance(summary.get("productionJobRunCount"), int)
            else 0
        )
        total_shadow_job_run_count += (
            summary.get("shadowJobRunCount", 0)
            if isinstance(summary.get("shadowJobRunCount"), int)
            else 0
        )
        total_compare_artifact_count += (
            summary.get("compareArtifactCount", 0)
            if isinstance(summary.get("compareArtifactCount"), int)
            else 0
        )
        total_compare_batch_count += (
            summary.get("compareBatchCount", 0)
            if isinstance(summary.get("compareBatchCount"), int)
            else 0
        )
        total_error_count += len(error_summaries) if isinstance(error_summaries, list) else 0
        entries.append(
            {
                "runSummaryId": run_summary_id,
                "generatedAt": run_summary.get("generatedAt"),
                "orchestrationCycleId": cycle_id,
                "runStatus": run_status,
                "scheduleCount": summary.get("scheduleCount"),
                "jobRunCount": summary.get("jobRunCount"),
                "productionJobRunCount": summary.get("productionJobRunCount"),
                "shadowJobRunCount": summary.get("shadowJobRunCount"),
                "compareArtifactCount": summary.get("compareArtifactCount"),
                "compareBatchCount": summary.get("compareBatchCount"),
                "errorCount": len(error_summaries)
                if isinstance(error_summaries, list)
                else 0,
                "retentionPolicyId": summary.get("retentionPolicyId"),
                "scheduleIds": sorted(
                    schedule_summary["scheduleId"]
                    for schedule_summary in schedule_summaries
                    if isinstance(schedule_summary, dict)
                    and isinstance(schedule_summary.get("scheduleId"), str)
                    and schedule_summary.get("scheduleId")
                ),
                "schedulerRolloutIntentCounts": summary.get(
                    "schedulerRolloutIntentCounts", {}
                ),
                "weeklyDecisionCounts": summary.get("weeklyDecisionCounts", {}),
                "rollbackSeverityCounts": summary.get("rollbackSeverityCounts", {}),
            }
        )

    entries = _sort_entries(entries, id_key="runSummaryId")
    return {
        "schemaVersion": OPTIMIZER_RECENT_RUN_SUMMARIES_SAMPLE_SCHEMA_VERSION,
        "recentRunSummariesId": aggregate_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "sourceMode": "orchestration_cycle_artifacts",
            "optimizerJobOrchestrationCycleIds": sorted(cycle_ids),
            "optimizerRunSummaryIds": sorted(run_summary_ids),
            "optimizerRunSummarySchemaVersions": sorted(run_summary_schema_versions),
            "cycleCount": len(cycle_payloads),
            "runSummaryCount": len(entries),
        },
        "summary": {
            "runSummaryCount": len(entries),
            "runStatusCounts": _sorted_counter(run_status_counts),
            "scheduleCount": total_schedule_count,
            "jobRunCount": total_job_run_count,
            "productionJobRunCount": total_production_job_run_count,
            "shadowJobRunCount": total_shadow_job_run_count,
            "compareArtifactCount": total_compare_artifact_count,
            "compareBatchCount": total_compare_batch_count,
            "errorCount": total_error_count,
            "schedulerRolloutIntentCounts": _sorted_counter(
                scheduler_rollout_intent_counts
            ),
            "weeklyDecisionCounts": _sorted_counter(weekly_decision_counts),
            "rollbackSeverityCounts": _sorted_counter(rollback_severity_counts),
        },
        "entries": entries,
    }


def build_optimizer_recent_compare_summaries_payload(
    *,
    aggregate_id: str,
    generated_at: str,
    compare_batch_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    group_entries: list[dict[str, Any]] = []
    compare_batch_ids: set[str] = set()
    compare_batch_schema_versions: set[str] = set()
    compared_compare_ids: set[str] = set()
    compared_schedule_ids: set[str] = set()
    candidate_scheduler_rollout_intents: set[str] = set()
    candidate_rollout_classes: set[str] = set()
    candidate_runtime_profile_rollout_classes: set[str] = set()
    candidate_window_set_purposes: set[str] = set()
    candidate_comparison_dimensions: set[str] = set()
    candidate_source_lanes: set[str] = set()
    batch_window_labels: set[str] = set()
    total_compare_artifact_count = 0
    total_comparison_count = 0
    total_matched_comparison_count = 0
    total_mismatched_comparison_count = 0

    for batch_payload in compare_batch_payloads:
        validate_optimizer_job_shadow_compare_batch_payload(batch_payload)
        batch_id = batch_payload.get("batchId")
        compare_batch_ids.add(batch_id)
        compare_batch_schema_versions.add(batch_payload.get("schemaVersion"))
        summary = batch_payload.get("summary", {})
        group_summaries = batch_payload.get("groupSummaries", [])
        compared_compare_ids.update(summary.get("comparedCompareIds", []))
        compared_schedule_ids.update(summary.get("comparedScheduleIds", []))
        candidate_scheduler_rollout_intents.update(
            summary.get("comparedCandidateSchedulerRolloutIntents", [])
        )
        candidate_rollout_classes.update(summary.get("comparedCandidateRolloutClasses", []))
        candidate_runtime_profile_rollout_classes.update(
            summary.get("comparedCandidateRuntimeProfileRolloutClasses", [])
        )
        candidate_window_set_purposes.update(
            summary.get("comparedCandidateWindowSetPurposes", [])
        )
        candidate_comparison_dimensions.update(
            summary.get("comparedCandidateComparisonDimensions", [])
        )
        candidate_source_lanes.update(summary.get("comparedCandidateSourceLanes", []))
        if isinstance(summary.get("batchWindowLabel"), str) and summary.get(
            "batchWindowLabel"
        ):
            batch_window_labels.add(summary["batchWindowLabel"])
        total_compare_artifact_count += (
            summary.get("compareArtifactCount", 0)
            if isinstance(summary.get("compareArtifactCount"), int)
            else 0
        )
        total_comparison_count += (
            summary.get("comparisonCount", 0)
            if isinstance(summary.get("comparisonCount"), int)
            else 0
        )
        total_matched_comparison_count += (
            summary.get("matchedComparisonCount", 0)
            if isinstance(summary.get("matchedComparisonCount"), int)
            else 0
        )
        total_mismatched_comparison_count += (
            summary.get("mismatchedComparisonCount", 0)
            if isinstance(summary.get("mismatchedComparisonCount"), int)
            else 0
        )
        entries.append(
            {
                "compareBatchId": batch_id,
                "generatedAt": batch_payload.get("generatedAt"),
                "sourceMode": batch_payload.get("generatedFrom", {}).get("sourceMode"),
                "comparisonDimension": summary.get("comparisonDimension"),
                "batchWindowLabel": summary.get("batchWindowLabel"),
                "compareArtifactCount": summary.get("compareArtifactCount"),
                "comparisonCount": summary.get("comparisonCount"),
                "matchedComparisonCount": summary.get("matchedComparisonCount"),
                "mismatchedComparisonCount": summary.get("mismatchedComparisonCount"),
                "groupCount": summary.get("groupCount"),
                "comparedCompareIds": summary.get("comparedCompareIds", []),
                "comparedScheduleIds": summary.get("comparedScheduleIds", []),
                "candidateSchedulerRolloutIntents": summary.get(
                    "comparedCandidateSchedulerRolloutIntents", []
                ),
                "candidateRolloutClasses": summary.get(
                    "comparedCandidateRolloutClasses", []
                ),
                "candidateRuntimeProfileRolloutClasses": summary.get(
                    "comparedCandidateRuntimeProfileRolloutClasses", []
                ),
                "candidateWindowSetPurposes": summary.get(
                    "comparedCandidateWindowSetPurposes", []
                ),
                "candidateComparisonDimensions": summary.get(
                    "comparedCandidateComparisonDimensions", []
                ),
                "candidateSourceLanes": summary.get(
                    "comparedCandidateSourceLanes", []
                ),
            }
        )
        for group_summary in group_summaries:
            if not isinstance(group_summary, dict):
                continue
            group_entries.append(
                {
                    "compareBatchId": batch_id,
                    "generatedAt": batch_payload.get("generatedAt"),
                    "batchWindowLabel": summary.get("batchWindowLabel"),
                    "groupValue": group_summary.get("groupValue"),
                    "comparisonCount": group_summary.get("comparisonCount"),
                    "matchedComparisonCount": group_summary.get(
                        "matchedComparisonCount"
                    ),
                    "mismatchedComparisonCount": group_summary.get(
                        "mismatchedComparisonCount"
                    ),
                    "candidateSchedulerRolloutIntents": group_summary.get(
                        "candidateSchedulerRolloutIntents", []
                    ),
                    "candidateRolloutClasses": group_summary.get(
                        "candidateRolloutClasses", []
                    ),
                    "candidateRuntimeProfileRolloutClasses": group_summary.get(
                        "candidateRuntimeProfileRolloutClasses", []
                    ),
                    "candidateWindowSetPurposes": group_summary.get(
                        "candidateWindowSetPurposes", []
                    ),
                    "candidateComparisonDimensions": group_summary.get(
                        "candidateComparisonDimensions", []
                    ),
                    "candidateSourceLanes": group_summary.get(
                        "candidateSourceLanes", []
                    ),
                }
            )

    entries = _sort_entries(entries, id_key="compareBatchId")
    group_entries = sorted(
        group_entries,
        key=lambda entry: (
            str(entry.get("generatedAt", "")),
            str(entry.get("compareBatchId", "")),
            str(entry.get("groupValue", "")),
        ),
        reverse=True,
    )
    return {
        "schemaVersion": OPTIMIZER_RECENT_COMPARE_SUMMARIES_SAMPLE_SCHEMA_VERSION,
        "recentCompareSummariesId": aggregate_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "sourceMode": "compare_batch_artifacts",
            "optimizerJobShadowCompareBatchIds": sorted(compare_batch_ids),
            "optimizerJobShadowCompareBatchSchemaVersions": sorted(
                compare_batch_schema_versions
            ),
            "optimizerJobShadowCompareIds": sorted(compared_compare_ids),
            "compareBatchCount": len(entries),
            "groupEntryCount": len(group_entries),
        },
        "summary": {
            "compareBatchCount": len(entries),
            "compareArtifactCount": total_compare_artifact_count,
            "comparisonCount": total_comparison_count,
            "matchedComparisonCount": total_matched_comparison_count,
            "mismatchedComparisonCount": total_mismatched_comparison_count,
            "groupEntryCount": len(group_entries),
            "batchWindowLabels": _sorted_unique_strings(batch_window_labels),
            "comparedScheduleIds": _sorted_unique_strings(compared_schedule_ids),
            "candidateSchedulerRolloutIntents": _sorted_unique_strings(
                candidate_scheduler_rollout_intents
            ),
            "candidateRolloutClasses": _sorted_unique_strings(
                candidate_rollout_classes
            ),
            "candidateRuntimeProfileRolloutClasses": _sorted_unique_strings(
                candidate_runtime_profile_rollout_classes
            ),
            "candidateWindowSetPurposes": _sorted_unique_strings(
                candidate_window_set_purposes
            ),
            "candidateComparisonDimensions": _sorted_unique_strings(
                candidate_comparison_dimensions
            ),
            "candidateSourceLanes": _sorted_unique_strings(candidate_source_lanes),
        },
        "entries": entries,
        "groupEntries": group_entries,
    }


def build_optimizer_recent_weekly_decisions_payload(
    *,
    aggregate_id: str,
    generated_at: str,
    cycle_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    cycle_ids: set[str] = set()
    job_run_ids: set[str] = set()
    scheduler_rollout_intent_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    rollback_severity_counts: dict[str, int] = {}
    stage_mode_counts: dict[str, int] = {}
    selected_challenger_profile_ids: set[str] = set()

    for cycle_payload in cycle_payloads:
        validate_optimizer_job_orchestration_cycle_payload(cycle_payload)
        cycle_id = cycle_payload.get("cycleRunId")
        if isinstance(cycle_id, str) and cycle_id:
            cycle_ids.add(cycle_id)
        for job_run in cycle_payload.get("artifacts", {}).get("jobRuns", []):
            if not isinstance(job_run, dict):
                continue
            summary = job_run.get("summary", {})
            if not isinstance(summary, dict):
                continue
            weekly_decision = summary.get("weeklyDecision")
            if not isinstance(weekly_decision, str) or not weekly_decision:
                continue
            generated_from = job_run.get("generatedFrom", {})
            if not isinstance(generated_from, dict):
                generated_from = {}
            job_run_id = job_run.get("jobRunId")
            job_run_ids.add(job_run_id)
            scheduler_rollout_intent = job_run.get("schedulerRolloutIntent")
            rollback_severity = generated_from.get("weeklyRollbackSeverity")
            weekly_stage_mode = generated_from.get("weeklyStageMode")
            selected_challenger_profile_id = summary.get(
                "selectedChallengerProfileId"
            )
            _increment_counter(
                scheduler_rollout_intent_counts, scheduler_rollout_intent
            )
            _increment_counter(decision_counts, weekly_decision)
            _increment_counter(rollback_severity_counts, rollback_severity)
            _increment_counter(stage_mode_counts, weekly_stage_mode)
            if (
                isinstance(selected_challenger_profile_id, str)
                and selected_challenger_profile_id
            ):
                selected_challenger_profile_ids.add(selected_challenger_profile_id)
            entries.append(
                {
                    "weeklyDecisionEntryId": (
                        f"{job_run.get('scheduleId')}:{scheduler_rollout_intent}:{job_run_id}"
                    ),
                    "jobRunId": job_run_id,
                    "generatedAt": job_run.get("generatedAt"),
                    "orchestrationCycleId": cycle_id,
                    "scheduleId": job_run.get("scheduleId"),
                    "schedulerRolloutIntent": scheduler_rollout_intent,
                    "rolloutClass": job_run.get("rolloutClass"),
                    "jobKind": job_run.get("jobKind"),
                    "rankingProfileId": summary.get("rankingProfileId"),
                    "evaluationWindow": summary.get("evaluationWindow"),
                    "dailyRecommendation": summary.get("dailyRecommendation"),
                    "weeklyDecision": weekly_decision,
                    "rollbackSeverity": rollback_severity,
                    "selectedChallengerProfileId": selected_challenger_profile_id,
                    "shadowLeaderProfileId": summary.get("shadowLeaderProfileId"),
                    "weeklyStageMode": weekly_stage_mode,
                    "weeklyStagePolicyId": generated_from.get("weeklyStagePolicyId"),
                    "weeklyStagePolicySelectionSource": generated_from.get(
                        "weeklyStagePolicySelectionSource"
                    ),
                    "minimumAverageRewardDelta": generated_from.get(
                        "minimumAverageRewardDelta"
                    ),
                    "minimumAverageHoldoutDelta": generated_from.get(
                        "minimumAverageHoldoutDelta"
                    ),
                }
            )

    entries = _sort_entries(entries, id_key="weeklyDecisionEntryId")
    return {
        "schemaVersion": OPTIMIZER_RECENT_WEEKLY_DECISIONS_SAMPLE_SCHEMA_VERSION,
        "recentWeeklyDecisionsId": aggregate_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "sourceMode": "orchestration_cycle_artifacts",
            "optimizerJobOrchestrationCycleIds": sorted(cycle_ids),
            "optimizerJobRunIds": sorted(job_run_ids),
            "cycleCount": len(cycle_payloads),
            "weeklyDecisionCount": len(entries),
        },
        "summary": {
            "weeklyDecisionCount": len(entries),
            "schedulerRolloutIntentCounts": _sorted_counter(
                scheduler_rollout_intent_counts
            ),
            "decisionCounts": _sorted_counter(decision_counts),
            "rollbackSeverityCounts": _sorted_counter(rollback_severity_counts),
            "stageModeCounts": _sorted_counter(stage_mode_counts),
            "selectedChallengerProfileIds": sorted(selected_challenger_profile_ids),
        },
        "entries": entries,
    }


def build_optimizer_recent_failure_summaries_payload(
    *,
    aggregate_id: str,
    generated_at: str,
    cycle_payloads: list[dict[str, Any]],
    standalone_error_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    cycle_ids: set[str] = set()
    standalone_error_ids: set[str] = set()
    error_code_counts: dict[str, int] = {}
    failure_stage_counts: dict[str, int] = {}
    owner_hint_counts: dict[str, int] = {}
    schedule_id_counts: dict[str, int] = {}
    retryable_count = 0

    for cycle_payload in cycle_payloads:
        validate_optimizer_job_orchestration_cycle_payload(cycle_payload)
        cycle_id = cycle_payload.get("cycleRunId")
        if isinstance(cycle_id, str) and cycle_id:
            cycle_ids.add(cycle_id)
        for error_payload in cycle_payload.get("artifacts", {}).get("errors", []):
            if not isinstance(error_payload, dict):
                continue
            validate_optimizer_job_error_payload(error_payload)
            _append_recent_failure_entry(
                entries=entries,
                error_payload=error_payload,
                source_kind="orchestration_cycle",
                source_id=cycle_id,
            )
            _increment_counter(error_code_counts, error_payload.get("errorCode"))
            _increment_counter(
                failure_stage_counts, error_payload.get("failureStage")
            )
            _increment_counter(owner_hint_counts, error_payload.get("ownerHint"))
            _increment_counter(schedule_id_counts, error_payload.get("scheduleId"))
            if error_payload.get("retryable") is True:
                retryable_count += 1

    for error_payload in standalone_error_payloads:
        validate_optimizer_job_error_payload(error_payload)
        error_id = error_payload.get("errorId")
        if isinstance(error_id, str) and error_id:
            standalone_error_ids.add(error_id)
        _append_recent_failure_entry(
            entries=entries,
            error_payload=error_payload,
            source_kind="job_error_artifact",
            source_id=error_id,
        )
        _increment_counter(error_code_counts, error_payload.get("errorCode"))
        _increment_counter(failure_stage_counts, error_payload.get("failureStage"))
        _increment_counter(owner_hint_counts, error_payload.get("ownerHint"))
        _increment_counter(schedule_id_counts, error_payload.get("scheduleId"))
        if error_payload.get("retryable") is True:
            retryable_count += 1

    entries = _sort_entries(entries, id_key="errorId")
    failure_count = len(entries)
    return {
        "schemaVersion": OPTIMIZER_RECENT_FAILURE_SUMMARIES_SAMPLE_SCHEMA_VERSION,
        "recentFailureSummariesId": aggregate_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "sourceMode": "mixed_error_sources",
            "optimizerJobOrchestrationCycleIds": sorted(cycle_ids),
            "standaloneOptimizerJobErrorIds": sorted(standalone_error_ids),
            "cycleCount": len(cycle_payloads),
            "standaloneErrorCount": len(standalone_error_payloads),
            "failureCount": failure_count,
        },
        "summary": {
            "failureCount": failure_count,
            "retryableCount": retryable_count,
            "nonRetryableCount": failure_count - retryable_count,
            "errorCodeCounts": _sorted_counter(error_code_counts),
            "failureStageCounts": _sorted_counter(failure_stage_counts),
            "ownerHintCounts": _sorted_counter(owner_hint_counts),
            "scheduleIdCounts": _sorted_counter(schedule_id_counts),
        },
        "entries": entries,
    }


def _append_recent_failure_entry(
    *,
    entries: list[dict[str, Any]],
    error_payload: dict[str, Any],
    source_kind: str,
    source_id: str | None,
) -> None:
    generated_from = error_payload.get("generatedFrom", {})
    entries.append(
        {
            "errorId": error_payload.get("errorId"),
            "generatedAt": error_payload.get("generatedAt"),
            "sourceKind": source_kind,
            "sourceId": source_id,
            "errorCode": error_payload.get("errorCode"),
            "failureStage": error_payload.get("failureStage"),
            "retryable": error_payload.get("retryable"),
            "ownerHint": error_payload.get("ownerHint"),
            "failureSummary": error_payload.get("failureSummary"),
            "scheduleId": error_payload.get("scheduleId"),
            "schedulerRolloutIntent": generated_from.get(
                "optimizerJobSchedulerRolloutIntent"
            ),
            "rolloutClass": generated_from.get("optimizerInputRolloutClass"),
            "jobKind": generated_from.get("optimizerJobKind"),
            "scheduleProfile": generated_from.get("optimizerJobScheduleProfile"),
            "runtimeProfileRolloutClass": generated_from.get(
                "optimizerJobRuntimeProfileRolloutClass"
            ),
            "windowSetPurpose": generated_from.get("optimizerJobWindowSetPurpose"),
            "comparisonDimension": generated_from.get(
                "optimizerJobComparisonDimension"
            ),
        }
    )


def validate_optimizer_recent_run_summaries_payload(payload: dict[str, Any]) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_RECENT_RUN_SUMMARIES_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer recent run summaries payload must declare a supported schemaVersion"
        )
    _validate_non_empty_string(
        payload.get("recentRunSummariesId"), label="recentRunSummariesId"
    )
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer recent run summaries payload must declare generatedFrom"
        )
    _validate_non_empty_string(
        generated_from.get("sourceMode"), label="generatedFrom.sourceMode"
    )
    _validate_string_list(
        generated_from.get("optimizerJobOrchestrationCycleIds", []),
        label="generatedFrom.optimizerJobOrchestrationCycleIds",
    )
    _validate_string_list(
        generated_from.get("optimizerRunSummaryIds", []),
        label="generatedFrom.optimizerRunSummaryIds",
    )
    _validate_string_list(
        generated_from.get("optimizerRunSummarySchemaVersions", []),
        label="generatedFrom.optimizerRunSummarySchemaVersions",
    )
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "optimizer recent run summaries payload must declare entries"
        )
    if generated_from.get("runSummaryCount") != len(entries):
        raise ValueError(
            "optimizer recent run summaries generatedFrom.runSummaryCount mismatch"
        )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("optimizer recent run summaries payload must declare summary")
    if summary.get("runSummaryCount") != len(entries):
        raise ValueError(
            "optimizer recent run summaries summary.runSummaryCount mismatch"
        )
    _validate_counter(summary.get("runStatusCounts"), label="summary.runStatusCounts")
    _validate_counter(
        summary.get("schedulerRolloutIntentCounts"),
        label="summary.schedulerRolloutIntentCounts",
    )
    _validate_counter(
        summary.get("weeklyDecisionCounts"), label="summary.weeklyDecisionCounts"
    )
    _validate_counter(
        summary.get("rollbackSeverityCounts"),
        label="summary.rollbackSeverityCounts",
    )
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "optimizer recent run summaries entries must be objects"
            )
        entry_id = entry.get("runSummaryId")
        _validate_non_empty_string(entry_id, label="entry.runSummaryId")
        if entry_id in seen_ids:
            raise ValueError(
                f"duplicate optimizer recent run summaries entry {entry_id}"
            )
        seen_ids.add(entry_id)
        _validate_non_empty_string(entry.get("generatedAt"), label="entry.generatedAt")
        _validate_non_empty_string(
            entry.get("orchestrationCycleId"), label="entry.orchestrationCycleId"
        )
        if entry.get("runStatus") not in OPTIMIZER_RECENT_RUN_SUMMARY_STATUSES:
            raise ValueError(
                "optimizer recent run summaries entry must use a supported runStatus"
            )
        for field_name in (
            "scheduleCount",
            "jobRunCount",
            "productionJobRunCount",
            "shadowJobRunCount",
            "compareArtifactCount",
            "compareBatchCount",
            "errorCount",
        ):
            value = entry.get(field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"optimizer recent run summaries entry {entry_id} {field_name} must be a non-negative integer"
                )
        _validate_optional_string(
            entry.get("retentionPolicyId"), label="entry.retentionPolicyId"
        )
        _validate_string_list(entry.get("scheduleIds", []), label="entry.scheduleIds")
        _validate_counter(
            entry.get("schedulerRolloutIntentCounts"),
            label="entry.schedulerRolloutIntentCounts",
        )
        _validate_counter(
            entry.get("weeklyDecisionCounts"), label="entry.weeklyDecisionCounts"
        )
        _validate_counter(
            entry.get("rollbackSeverityCounts"), label="entry.rollbackSeverityCounts"
        )


def validate_optimizer_recent_compare_summaries_payload(payload: dict[str, Any]) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_RECENT_COMPARE_SUMMARIES_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer recent compare summaries payload must declare a supported schemaVersion"
        )
    _validate_non_empty_string(
        payload.get("recentCompareSummariesId"), label="recentCompareSummariesId"
    )
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer recent compare summaries payload must declare generatedFrom"
        )
    _validate_non_empty_string(
        generated_from.get("sourceMode"), label="generatedFrom.sourceMode"
    )
    _validate_string_list(
        generated_from.get("optimizerJobShadowCompareBatchIds", []),
        label="generatedFrom.optimizerJobShadowCompareBatchIds",
    )
    _validate_string_list(
        generated_from.get("optimizerJobShadowCompareBatchSchemaVersions", []),
        label="generatedFrom.optimizerJobShadowCompareBatchSchemaVersions",
    )
    _validate_string_list(
        generated_from.get("optimizerJobShadowCompareIds", []),
        label="generatedFrom.optimizerJobShadowCompareIds",
    )
    entries = payload.get("entries")
    group_entries = payload.get("groupEntries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "optimizer recent compare summaries payload must declare entries"
        )
    if not isinstance(group_entries, list):
        raise ValueError(
            "optimizer recent compare summaries payload must declare groupEntries"
        )
    if generated_from.get("compareBatchCount") != len(entries):
        raise ValueError(
            "optimizer recent compare summaries generatedFrom.compareBatchCount mismatch"
        )
    if generated_from.get("groupEntryCount") != len(group_entries):
        raise ValueError(
            "optimizer recent compare summaries generatedFrom.groupEntryCount mismatch"
        )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(
            "optimizer recent compare summaries payload must declare summary"
        )
    if summary.get("compareBatchCount") != len(entries):
        raise ValueError(
            "optimizer recent compare summaries summary.compareBatchCount mismatch"
        )
    if summary.get("groupEntryCount") != len(group_entries):
        raise ValueError(
            "optimizer recent compare summaries summary.groupEntryCount mismatch"
        )
    for field_name in (
        "compareArtifactCount",
        "comparisonCount",
        "matchedComparisonCount",
        "mismatchedComparisonCount",
    ):
        value = summary.get(field_name)
        if not isinstance(value, int) or value < 0:
            raise ValueError(
                f"optimizer recent compare summaries summary {field_name} must be a non-negative integer"
            )
    for field_name in (
        "batchWindowLabels",
        "comparedScheduleIds",
        "candidateSchedulerRolloutIntents",
        "candidateRolloutClasses",
        "candidateRuntimeProfileRolloutClasses",
        "candidateWindowSetPurposes",
        "candidateComparisonDimensions",
        "candidateSourceLanes",
    ):
        _validate_string_list(summary.get(field_name, []), label=f"summary.{field_name}")
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "optimizer recent compare summaries entries must be objects"
            )
        entry_id = entry.get("compareBatchId")
        _validate_non_empty_string(entry_id, label="entry.compareBatchId")
        if entry_id in seen_ids:
            raise ValueError(
                f"duplicate optimizer recent compare summaries entry {entry_id}"
            )
        seen_ids.add(entry_id)
        _validate_non_empty_string(entry.get("generatedAt"), label="entry.generatedAt")
        _validate_non_empty_string(entry.get("sourceMode"), label="entry.sourceMode")
        _validate_non_empty_string(
            entry.get("comparisonDimension"), label="entry.comparisonDimension"
        )
        _validate_non_empty_string(
            entry.get("batchWindowLabel"), label="entry.batchWindowLabel"
        )
        for field_name in (
            "compareArtifactCount",
            "comparisonCount",
            "matchedComparisonCount",
            "mismatchedComparisonCount",
            "groupCount",
        ):
            value = entry.get(field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"optimizer recent compare summaries entry {entry_id} {field_name} must be a non-negative integer"
                )
        for field_name in (
            "comparedCompareIds",
            "comparedScheduleIds",
            "candidateSchedulerRolloutIntents",
            "candidateRolloutClasses",
            "candidateRuntimeProfileRolloutClasses",
            "candidateWindowSetPurposes",
            "candidateComparisonDimensions",
            "candidateSourceLanes",
        ):
            _validate_string_list(entry.get(field_name, []), label=f"entry.{field_name}")
    for entry in group_entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "optimizer recent compare summaries groupEntries must be objects"
            )
        _validate_non_empty_string(
            entry.get("compareBatchId"), label="groupEntry.compareBatchId"
        )
        _validate_non_empty_string(
            entry.get("generatedAt"), label="groupEntry.generatedAt"
        )
        _validate_non_empty_string(
            entry.get("batchWindowLabel"), label="groupEntry.batchWindowLabel"
        )
        _validate_non_empty_string(
            entry.get("groupValue"), label="groupEntry.groupValue"
        )
        for field_name in (
            "comparisonCount",
            "matchedComparisonCount",
            "mismatchedComparisonCount",
        ):
            value = entry.get(field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"optimizer recent compare summaries groupEntry {field_name} must be a non-negative integer"
                )
        for field_name in (
            "candidateSchedulerRolloutIntents",
            "candidateRolloutClasses",
            "candidateRuntimeProfileRolloutClasses",
            "candidateWindowSetPurposes",
            "candidateComparisonDimensions",
            "candidateSourceLanes",
        ):
            _validate_string_list(
                entry.get(field_name, []), label=f"groupEntry.{field_name}"
            )


def validate_optimizer_recent_weekly_decisions_payload(payload: dict[str, Any]) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_RECENT_WEEKLY_DECISIONS_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer recent weekly decisions payload must declare a supported schemaVersion"
        )
    _validate_non_empty_string(
        payload.get("recentWeeklyDecisionsId"), label="recentWeeklyDecisionsId"
    )
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer recent weekly decisions payload must declare generatedFrom"
        )
    _validate_non_empty_string(
        generated_from.get("sourceMode"), label="generatedFrom.sourceMode"
    )
    _validate_string_list(
        generated_from.get("optimizerJobOrchestrationCycleIds", []),
        label="generatedFrom.optimizerJobOrchestrationCycleIds",
    )
    _validate_string_list(
        generated_from.get("optimizerJobRunIds", []),
        label="generatedFrom.optimizerJobRunIds",
    )
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "optimizer recent weekly decisions payload must declare entries"
        )
    if generated_from.get("weeklyDecisionCount") != len(entries):
        raise ValueError(
            "optimizer recent weekly decisions generatedFrom.weeklyDecisionCount mismatch"
        )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(
            "optimizer recent weekly decisions payload must declare summary"
        )
    if summary.get("weeklyDecisionCount") != len(entries):
        raise ValueError(
            "optimizer recent weekly decisions summary.weeklyDecisionCount mismatch"
        )
    _validate_counter(
        summary.get("schedulerRolloutIntentCounts"),
        label="summary.schedulerRolloutIntentCounts",
    )
    _validate_counter(summary.get("decisionCounts"), label="summary.decisionCounts")
    _validate_counter(
        summary.get("rollbackSeverityCounts"),
        label="summary.rollbackSeverityCounts",
    )
    _validate_counter(summary.get("stageModeCounts"), label="summary.stageModeCounts")
    _validate_string_list(
        summary.get("selectedChallengerProfileIds", []),
        label="summary.selectedChallengerProfileIds",
    )
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "optimizer recent weekly decisions entries must be objects"
            )
        entry_id = entry.get("weeklyDecisionEntryId")
        _validate_non_empty_string(entry_id, label="entry.weeklyDecisionEntryId")
        if entry_id in seen_ids:
            raise ValueError(
                f"duplicate optimizer recent weekly decisions entry {entry_id}"
            )
        seen_ids.add(entry_id)
        _validate_non_empty_string(entry.get("jobRunId"), label="entry.jobRunId")
        _validate_non_empty_string(entry.get("generatedAt"), label="entry.generatedAt")
        _validate_non_empty_string(
            entry.get("orchestrationCycleId"), label="entry.orchestrationCycleId"
        )
        _validate_non_empty_string(entry.get("scheduleId"), label="entry.scheduleId")
        _validate_non_empty_string(
            entry.get("schedulerRolloutIntent"), label="entry.schedulerRolloutIntent"
        )
        _validate_non_empty_string(
            entry.get("rolloutClass"), label="entry.rolloutClass"
        )
        _validate_non_empty_string(entry.get("jobKind"), label="entry.jobKind")
        _validate_non_empty_string(
            entry.get("rankingProfileId"), label="entry.rankingProfileId"
        )
        _validate_non_empty_string(
            entry.get("evaluationWindow"), label="entry.evaluationWindow"
        )
        _validate_non_empty_string(
            entry.get("dailyRecommendation"), label="entry.dailyRecommendation"
        )
        if entry.get("weeklyDecision") not in OPTIMIZER_RECENT_WEEKLY_DECISIONS:
            raise ValueError(
                "optimizer recent weekly decisions entry must use a supported weeklyDecision"
            )
        if entry.get("rollbackSeverity") not in OPTIMIZER_RECENT_ROLLBACK_SEVERITIES:
            raise ValueError(
                "optimizer recent weekly decisions entry must use a supported rollbackSeverity"
            )
        _validate_optional_string(
            entry.get("selectedChallengerProfileId"),
            label="entry.selectedChallengerProfileId",
        )
        _validate_optional_string(
            entry.get("shadowLeaderProfileId"), label="entry.shadowLeaderProfileId"
        )
        _validate_non_empty_string(
            entry.get("weeklyStageMode"), label="entry.weeklyStageMode"
        )
        _validate_non_empty_string(
            entry.get("weeklyStagePolicyId"), label="entry.weeklyStagePolicyId"
        )
        _validate_non_empty_string(
            entry.get("weeklyStagePolicySelectionSource"),
            label="entry.weeklyStagePolicySelectionSource",
        )
        for field_name in (
            "minimumAverageRewardDelta",
            "minimumAverageHoldoutDelta",
        ):
            value = entry.get(field_name)
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"optimizer recent weekly decisions entry {entry_id} {field_name} must be numeric"
                )


def validate_optimizer_recent_failure_summaries_payload(
    payload: dict[str, Any]
) -> None:
    if (
        payload.get("schemaVersion")
        not in OPTIMIZER_RECENT_FAILURE_SUMMARIES_SCHEMA_VERSIONS
    ):
        raise ValueError(
            "optimizer recent failure summaries payload must declare a supported schemaVersion"
        )
    _validate_non_empty_string(
        payload.get("recentFailureSummariesId"), label="recentFailureSummariesId"
    )
    _validate_non_empty_string(payload.get("generatedAt"), label="generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer recent failure summaries payload must declare generatedFrom"
        )
    _validate_non_empty_string(
        generated_from.get("sourceMode"), label="generatedFrom.sourceMode"
    )
    _validate_string_list(
        generated_from.get("optimizerJobOrchestrationCycleIds", []),
        label="generatedFrom.optimizerJobOrchestrationCycleIds",
    )
    _validate_string_list(
        generated_from.get("standaloneOptimizerJobErrorIds", []),
        label="generatedFrom.standaloneOptimizerJobErrorIds",
    )
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "optimizer recent failure summaries payload must declare entries"
        )
    if generated_from.get("failureCount") != len(entries):
        raise ValueError(
            "optimizer recent failure summaries generatedFrom.failureCount mismatch"
        )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(
            "optimizer recent failure summaries payload must declare summary"
        )
    if summary.get("failureCount") != len(entries):
        raise ValueError(
            "optimizer recent failure summaries summary.failureCount mismatch"
        )
    retryable_count = summary.get("retryableCount")
    non_retryable_count = summary.get("nonRetryableCount")
    if not isinstance(retryable_count, int) or retryable_count < 0:
        raise ValueError(
            "optimizer recent failure summaries summary.retryableCount must be a non-negative integer"
        )
    if not isinstance(non_retryable_count, int) or non_retryable_count < 0:
        raise ValueError(
            "optimizer recent failure summaries summary.nonRetryableCount must be a non-negative integer"
        )
    if retryable_count + non_retryable_count != len(entries):
        raise ValueError(
            "optimizer recent failure summaries retryable/nonRetryable counts mismatch"
        )
    _validate_counter(summary.get("errorCodeCounts"), label="summary.errorCodeCounts")
    _validate_counter(
        summary.get("failureStageCounts"), label="summary.failureStageCounts"
    )
    _validate_counter(summary.get("ownerHintCounts"), label="summary.ownerHintCounts")
    _validate_counter(
        summary.get("scheduleIdCounts"), label="summary.scheduleIdCounts"
    )
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "optimizer recent failure summaries entries must be objects"
            )
        entry_id = entry.get("errorId")
        _validate_non_empty_string(entry_id, label="entry.errorId")
        if entry_id in seen_ids:
            raise ValueError(
                f"duplicate optimizer recent failure summaries entry {entry_id}"
            )
        seen_ids.add(entry_id)
        _validate_non_empty_string(entry.get("generatedAt"), label="entry.generatedAt")
        _validate_non_empty_string(entry.get("sourceKind"), label="entry.sourceKind")
        _validate_non_empty_string(entry.get("sourceId"), label="entry.sourceId")
        _validate_non_empty_string(entry.get("errorCode"), label="entry.errorCode")
        _validate_non_empty_string(
            entry.get("failureStage"), label="entry.failureStage"
        )
        if not isinstance(entry.get("retryable"), bool):
            raise ValueError(
                "optimizer recent failure summaries entry retryable must be a boolean"
            )
        _validate_non_empty_string(entry.get("ownerHint"), label="entry.ownerHint")
        _validate_non_empty_string(
            entry.get("failureSummary"), label="entry.failureSummary"
        )
        _validate_non_empty_string(entry.get("scheduleId"), label="entry.scheduleId")
        for field_name in (
            "schedulerRolloutIntent",
            "rolloutClass",
            "jobKind",
            "scheduleProfile",
            "runtimeProfileRolloutClass",
        ):
            _validate_optional_string(entry.get(field_name), label=f"entry.{field_name}")
        for field_name in ("windowSetPurpose", "comparisonDimension"):
            _validate_optional_string(entry.get(field_name), label=f"entry.{field_name}")


def load_optimizer_recent_run_summaries(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_optimizer_recent_run_summaries_payload(payload)
    return payload


def load_optimizer_recent_compare_summaries(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_optimizer_recent_compare_summaries_payload(payload)
    return payload


def load_optimizer_recent_weekly_decisions(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_optimizer_recent_weekly_decisions_payload(payload)
    return payload


def load_optimizer_recent_failure_summaries(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_optimizer_recent_failure_summaries_payload(payload)
    return payload


def load_optimizer_orchestration_cycle_inputs(paths: list[Path]) -> list[dict[str, Any]]:
    return [load_optimizer_job_orchestration_cycle(path) for path in paths]


def load_optimizer_compare_batch_inputs(paths: list[Path]) -> list[dict[str, Any]]:
    return [load_optimizer_job_shadow_compare_batch(path) for path in paths]


def load_optimizer_job_error_inputs(paths: list[Path]) -> list[dict[str, Any]]:
    return [load_optimizer_job_error(path) for path in paths]
