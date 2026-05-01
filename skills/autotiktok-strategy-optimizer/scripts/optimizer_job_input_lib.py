#!/usr/bin/env python3
"""
Helpers for wrapping and unwrapping scheduler-facing optimizer job inputs.
"""

from __future__ import annotations

from typing import Any


DIRECT_ARTIFACT_SOURCE_KIND = "direct_artifact"
JOB_RUN_ENVELOPE_SOURCE_KIND = "job_run_envelope"

TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION = (
    "topic-outcome-backfill-run.sample.v1"
)
TOPIC_OUTCOME_BACKFILL_RUN_SCHEMA_VERSION = "topic-outcome-backfill-run.v1"
POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION = (
    "post-performance-signal-run.sample.v1"
)
POST_PERFORMANCE_SIGNAL_RUN_SCHEMA_VERSION = "post-performance-signal-run.v1"
CHALLENGER_EVALUATION_RUN_SAMPLE_SCHEMA_VERSION = (
    "challenger-evaluation-run.sample.v1"
)
CHALLENGER_EVALUATION_RUN_SCHEMA_VERSION = "challenger-evaluation-run.v1"

TOPIC_OUTCOME_BACKFILL_RUN_SCHEMA_VERSIONS = {
    TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
    TOPIC_OUTCOME_BACKFILL_RUN_SCHEMA_VERSION,
}
POST_PERFORMANCE_SIGNAL_RUN_SCHEMA_VERSIONS = {
    POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
    POST_PERFORMANCE_SIGNAL_RUN_SCHEMA_VERSION,
}
CHALLENGER_EVALUATION_RUN_SCHEMA_VERSIONS = {
    CHALLENGER_EVALUATION_RUN_SAMPLE_SCHEMA_VERSION,
    CHALLENGER_EVALUATION_RUN_SCHEMA_VERSION,
}

TOPIC_OUTCOME_BACKFILL_JOB_KIND = "topic_outcome_backfill"
POST_PERFORMANCE_SIGNAL_JOB_KIND = "post_performance_signal"
CHALLENGER_EVALUATION_JOB_KIND = "challenger_evaluation"


def _require_string(
    payload: dict[str, Any], key: str, label: str, *, allow_empty: bool = False
) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{label}.{key} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{label}.{key} must be non-empty")
    return value


def _require_object(payload: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{label}.{key} must be an object")
    return value


def _normalize_source_metadata(
    *,
    source_kind: str,
    source_schema_version: str | None,
    artifact_schema_version: str | None,
    job_run_schema_version: str | None,
    job_run_id: str | None,
    job_kind: str | None,
    job_generated_at: str | None,
    job_generated_from: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "sourceKind": source_kind,
        "sourceSchemaVersion": source_schema_version,
        "artifactSchemaVersion": artifact_schema_version,
        "jobRunSchemaVersion": job_run_schema_version,
        "jobRunId": job_run_id,
        "jobKind": job_kind,
        "jobGeneratedAt": job_generated_at,
        "jobGeneratedFrom": {}
        if job_generated_from is None
        else dict(job_generated_from),
    }


def build_optimizer_job_run_payload(
    *,
    payload: dict[str, Any],
    schema_version: str,
    job_run_id: str,
    job_kind: str,
    generated_at: str,
    generated_from: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "jobRunId": job_run_id,
        "jobKind": job_kind,
        "generatedAt": generated_at,
        "generatedFrom": dict(generated_from),
        "payload": payload,
    }


def _unwrap_optimizer_job_input(
    payload: dict[str, Any],
    *,
    label: str,
    allowed_schema_versions: set[str],
    expected_job_kind: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    schema_version = payload.get("schemaVersion")
    if schema_version not in allowed_schema_versions:
        artifact_schema_version = payload.get("schemaVersion")
        return payload, _normalize_source_metadata(
            source_kind=DIRECT_ARTIFACT_SOURCE_KIND,
            source_schema_version=None
            if not isinstance(artifact_schema_version, str)
            else artifact_schema_version,
            artifact_schema_version=None
            if not isinstance(artifact_schema_version, str)
            else artifact_schema_version,
            job_run_schema_version=None,
            job_run_id=None,
            job_kind=None,
            job_generated_at=None,
            job_generated_from={},
        )

    job_run_id = _require_string(payload, "jobRunId", label)
    job_kind = _require_string(payload, "jobKind", label)
    if job_kind != expected_job_kind:
        raise ValueError(
            f"{label}.jobKind must be {expected_job_kind!r}, got {job_kind!r}"
        )
    generated_at = _require_string(payload, "generatedAt", label)
    generated_from = _require_object(payload, "generatedFrom", label)
    inner_payload = _require_object(payload, "payload", label)
    artifact_schema_version = inner_payload.get("schemaVersion")
    if not isinstance(artifact_schema_version, str) or not artifact_schema_version:
        raise ValueError(f"{label}.payload.schemaVersion must be a non-empty string")
    return inner_payload, _normalize_source_metadata(
        source_kind=JOB_RUN_ENVELOPE_SOURCE_KIND,
        source_schema_version=str(schema_version),
        artifact_schema_version=artifact_schema_version,
        job_run_schema_version=str(schema_version),
        job_run_id=job_run_id,
        job_kind=job_kind,
        job_generated_at=generated_at,
        job_generated_from=generated_from,
    )


def unwrap_topic_outcome_backfill_input(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return _unwrap_optimizer_job_input(
        payload,
        label="topicOutcomeBackfillRun",
        allowed_schema_versions=TOPIC_OUTCOME_BACKFILL_RUN_SCHEMA_VERSIONS,
        expected_job_kind=TOPIC_OUTCOME_BACKFILL_JOB_KIND,
    )


def unwrap_post_performance_signal_input(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return _unwrap_optimizer_job_input(
        payload,
        label="postPerformanceSignalRun",
        allowed_schema_versions=POST_PERFORMANCE_SIGNAL_RUN_SCHEMA_VERSIONS,
        expected_job_kind=POST_PERFORMANCE_SIGNAL_JOB_KIND,
    )


def unwrap_challenger_evaluation_input(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return _unwrap_optimizer_job_input(
        payload,
        label="challengerEvaluationRun",
        allowed_schema_versions=CHALLENGER_EVALUATION_RUN_SCHEMA_VERSIONS,
        expected_job_kind=CHALLENGER_EVALUATION_JOB_KIND,
    )
