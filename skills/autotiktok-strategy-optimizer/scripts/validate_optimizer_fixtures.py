#!/usr/bin/env python3
"""
Validate the optimizer sample fixtures for backfills, post performance, and challenger inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from optimizer_bundle_lib import validate_optimizer_input_manifest_payload
from optimizer_job_input_lib import (
    CHALLENGER_EVALUATION_JOB_KIND,
    CHALLENGER_EVALUATION_RUN_SAMPLE_SCHEMA_VERSION,
    POST_PERFORMANCE_SIGNAL_JOB_KIND,
    POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
    TOPIC_OUTCOME_BACKFILL_JOB_KIND,
    TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "fixtures"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_backfills(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "topic-outcome-backfills.sample.v1":
        errors.append("backfills fixture has unexpected schemaVersion")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return [*errors, "backfills fixture must include a non-empty items list"]
    run_id = payload.get("runId")
    if payload.get("evaluationWindow") not in {"t_plus_1", "t_plus_3", "t_plus_7"}:
        errors.append("backfills fixture has invalid evaluationWindow")
    for index, item in enumerate(items):
        prefix = f"backfills.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("schemaVersion") != "topic-outcome-backfill.v1":
            errors.append(f"{prefix} has unexpected schemaVersion")
        if item.get("runId") != run_id:
            errors.append(f"{prefix}.runId must match top-level runId")
        if item.get("backfillWindow") != payload.get("evaluationWindow"):
            errors.append(f"{prefix}.backfillWindow must match top-level evaluationWindow")
        if item.get("matchedBy") not in {"topic_fingerprint", "weak_semantic_match", "manual_review"}:
            errors.append(f"{prefix}.matchedBy is invalid")
        for key in ("searchLift", "futureVideoDensity", "contentGapPersistence", "outcomeConfidence"):
            value = item.get(key)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                errors.append(f"{prefix}.{key} must be between 0 and 1")
    return errors


def validate_backfills_raw(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "topic-outcome-backfills-raw.sample.v1":
        errors.append("raw backfills fixture has unexpected schemaVersion")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return [*errors, "raw backfills fixture must include a non-empty items list"]
    run_id = payload.get("runId")
    if payload.get("evaluationWindow") not in {"t_plus_1", "t_plus_3", "t_plus_7"}:
        errors.append("raw backfills fixture has invalid evaluationWindow")
    for index, item in enumerate(items):
        prefix = f"rawBackfills.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("schemaVersion") != "topic-outcome-backfill-raw-item.v1":
            errors.append(f"{prefix} has unexpected schemaVersion")
        if item.get("runId") != run_id:
            errors.append(f"{prefix}.runId must match top-level runId")
        if item.get("observedWindow") != payload.get("evaluationWindow"):
            errors.append(f"{prefix}.observedWindow must match top-level evaluationWindow")
        if item.get("matchStrategy") not in {
            "topic_fingerprint",
            "weak_semantic_match",
            "manual_review",
        }:
            errors.append(f"{prefix}.matchStrategy is invalid")
        for key in (
            "queryLiftScore",
            "futureTopicDensityScore",
            "contentGapPersistenceScore",
            "matchConfidence",
        ):
            value = item.get(key)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                errors.append(f"{prefix}.{key} must be between 0 and 1")
    return errors


def validate_performance(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "post-performance-signals.sample.v1":
        errors.append("performance fixture has unexpected schemaVersion")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return [*errors, "performance fixture must include a non-empty items list"]
    run_id = payload.get("runId")
    account_id = payload.get("accountId")
    for index, item in enumerate(items):
        prefix = f"performance.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("schemaVersion") != "post-performance-signal.v1":
            errors.append(f"{prefix} has unexpected schemaVersion")
        if item.get("runId") != run_id:
            errors.append(f"{prefix}.runId must match top-level runId")
        if item.get("accountId") != account_id:
            errors.append(f"{prefix}.accountId must match top-level accountId")
        if item.get("measuredWindow") != payload.get("measuredWindow"):
            errors.append(f"{prefix}.measuredWindow must match top-level measuredWindow")
        for key in ("viewLift", "retentionProxy", "shareSaveProxy", "followConversionProxy"):
            value = item.get(key)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                errors.append(f"{prefix}.{key} must be between 0 and 1")
        for key in ("rawViews", "baselineViews"):
            value = item.get(key)
            if not isinstance(value, int) or value <= 0:
                errors.append(f"{prefix}.{key} must be a positive integer")
    return errors


def validate_performance_raw(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "post-performance-raw.sample.v1":
        errors.append("raw performance fixture has unexpected schemaVersion")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return [*errors, "raw performance fixture must include a non-empty items list"]
    run_id = payload.get("runId")
    account_id = payload.get("accountId")
    for index, item in enumerate(items):
        prefix = f"rawPerformance.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("schemaVersion") != "post-performance-raw-item.v1":
            errors.append(f"{prefix} has unexpected schemaVersion")
        if item.get("runId") != run_id:
            errors.append(f"{prefix}.runId must match top-level runId")
        if item.get("accountId") != account_id:
            errors.append(f"{prefix}.accountId must match top-level accountId")
        if item.get("measuredWindow") != payload.get("measuredWindow"):
            errors.append(f"{prefix}.measuredWindow must match top-level measuredWindow")
        for key in ("normalizedViewLift", "retentionRatio", "shareSaveRate", "followConversionRate"):
            value = item.get(key)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                errors.append(f"{prefix}.{key} must be between 0 and 1")
        for key in ("observedViews", "expectedViews"):
            value = item.get(key)
            if not isinstance(value, int) or value <= 0:
                errors.append(f"{prefix}.{key} must be a positive integer")
    return errors


def validate_challenger_adjustments(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "challenger-adjustments.sample.v1":
        errors.append("challenger-adjustments fixture has unexpected schemaVersion")
    challengers = payload.get("challengers")
    if not isinstance(challengers, list) or not challengers:
        return [*errors, "challenger-adjustments fixture must include a non-empty challengers list"]
    champion = payload.get("championProfileId")
    seen_profiles: set[str] = set()
    for index, item in enumerate(challengers):
        prefix = f"challengers[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        profile_id = item.get("profileId")
        if not isinstance(profile_id, str) or not profile_id:
            errors.append(f"{prefix}.profileId must be a non-empty string")
            continue
        if profile_id == champion:
            errors.append(f"{prefix}.profileId must differ from championProfileId")
        if profile_id in seen_profiles:
            errors.append(f"{prefix}.profileId is duplicated: {profile_id}")
        else:
            seen_profiles.add(profile_id)
        for key in (
            "topicRewardDelta",
            "performanceRewardDelta",
            "dupRateDelta",
            "typeCoverageDelta",
            "executableRateDelta",
            "holdoutDelta",
        ):
            value = item.get(key)
            if not isinstance(value, (int, float)) or not -1 <= float(value) <= 1:
                errors.append(f"{prefix}.{key} must be between -1 and 1")
        days_observed = item.get("daysObserved")
        if not isinstance(days_observed, int) or days_observed <= 0:
            errors.append(f"{prefix}.daysObserved must be a positive integer")
    return errors


def validate_challenger_observations(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "challenger-observations.sample.v1":
        errors.append("challenger-observations fixture has unexpected schemaVersion")
    challengers = payload.get("challengers")
    if not isinstance(challengers, list) or not challengers:
        return [*errors, "challenger-observations fixture must include a non-empty challengers list"]
    if payload.get("evaluationWindow") not in {"t_plus_1", "t_plus_3", "t_plus_7"}:
        errors.append("challenger-observations fixture has invalid evaluationWindow")
    seen_profiles: set[str] = set()
    for index, item in enumerate(challengers):
        prefix = f"challengerObservations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("schemaVersion") != "challenger-observation.v1":
            errors.append(f"{prefix} has unexpected schemaVersion")
        profile_id = item.get("profileId")
        if not isinstance(profile_id, str) or not profile_id:
            errors.append(f"{prefix}.profileId must be a non-empty string")
            continue
        if profile_id in seen_profiles:
            errors.append(f"{prefix}.profileId is duplicated: {profile_id}")
        else:
            seen_profiles.add(profile_id)
        topic_metrics = item.get("topicMetrics")
        if not isinstance(topic_metrics, dict):
            errors.append(f"{prefix}.topicMetrics must be an object")
        else:
            for key in (
                "Hit@3",
                "Hit@10",
                "NDCG@10",
                "DupRate",
                "TypeCoverage",
                "Novelty",
                "ExecutableRate",
            ):
                value = topic_metrics.get(key)
                if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                    errors.append(f"{prefix}.topicMetrics[{key}] must be between 0 and 1")
        performance_summary = item.get("performanceSummary")
        if not isinstance(performance_summary, dict):
            errors.append(f"{prefix}.performanceSummary must be an object")
        else:
            for key in ("performanceReward", "performanceWeight", "postCoverageRate"):
                value = performance_summary.get(key)
                if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                    errors.append(f"{prefix}.performanceSummary.{key} must be between 0 and 1")
        holdout_delta = item.get("holdoutDelta")
        if not isinstance(holdout_delta, (int, float)) or not -1 <= float(holdout_delta) <= 1:
            errors.append(f"{prefix}.holdoutDelta must be between -1 and 1")
        days_observed = item.get("daysObserved")
        if not isinstance(days_observed, int) or days_observed <= 0:
            errors.append(f"{prefix}.daysObserved must be a positive integer")
    return errors


def validate_challenger_observations_raw(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "challenger-observations-raw.sample.v1":
        errors.append("raw challenger-observations fixture has unexpected schemaVersion")
    challengers = payload.get("challengers")
    if not isinstance(challengers, list) or not challengers:
        return [
            *errors,
            "raw challenger-observations fixture must include a non-empty challengers list",
        ]
    if payload.get("evaluationWindow") not in {"t_plus_1", "t_plus_3", "t_plus_7"}:
        errors.append("raw challenger-observations fixture has invalid evaluationWindow")
    seen_profiles: set[str] = set()
    for index, item in enumerate(challengers):
        prefix = f"rawChallengerObservations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("schemaVersion") != "challenger-observation-raw-item.v1":
            errors.append(f"{prefix} has unexpected schemaVersion")
        profile_id = item.get("profileId")
        if not isinstance(profile_id, str) or not profile_id:
            errors.append(f"{prefix}.profileId must be a non-empty string")
            continue
        if profile_id in seen_profiles:
            errors.append(f"{prefix}.profileId is duplicated: {profile_id}")
        else:
            seen_profiles.add(profile_id)
        ranking_quality = item.get("rankingQuality")
        if not isinstance(ranking_quality, dict):
            errors.append(f"{prefix}.rankingQuality must be an object")
        else:
            for key in (
                "top3HitRate",
                "top10HitRate",
                "ndcg10",
                "duplicationRate",
                "typeCoverageRate",
                "noveltyScore",
                "executableRate",
            ):
                value = ranking_quality.get(key)
                if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                    errors.append(f"{prefix}.rankingQuality.{key} must be between 0 and 1")
        performance_aggregate = item.get("performanceAggregate")
        if not isinstance(performance_aggregate, dict):
            errors.append(f"{prefix}.performanceAggregate must be an object")
        else:
            for key in ("normalizedReward", "appliedWeight", "coverageRate"):
                value = performance_aggregate.get(key)
                if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                    errors.append(
                        f"{prefix}.performanceAggregate.{key} must be between 0 and 1"
                    )
        holdout_delta = item.get("holdoutDelta")
        if not isinstance(holdout_delta, (int, float)) or not -1 <= float(holdout_delta) <= 1:
            errors.append(f"{prefix}.holdoutDelta must be between -1 and 1")
        observed_days = item.get("observedDays")
        if not isinstance(observed_days, int) or observed_days <= 0:
            errors.append(f"{prefix}.observedDays must be a positive integer")
    return errors


def validate_optimizer_input_bundle(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != "optimizer-input-bundle.sample.v1":
        errors.append("optimizer input bundle has unexpected schemaVersion")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        return [*errors, "optimizer input bundle must include an object `artifacts` field"]
    ranking = artifacts.get("ranking")
    context = artifacts.get("context")
    backfills = artifacts.get("backfills")
    performance = artifacts.get("performance")
    challenger_input = artifacts.get("challengerInput")
    if not isinstance(ranking, dict):
        errors.append("optimizer input bundle artifacts.ranking must be an object")
    else:
        if ranking.get("schemaVersion") != "ranking-output.v1":
            errors.append("optimizer input bundle ranking artifact has unexpected schemaVersion")
    if not isinstance(context, dict):
        errors.append("optimizer input bundle artifacts.context must be an object")
    else:
        if context.get("schemaVersion") != "scoring-context.v1":
            errors.append("optimizer input bundle context artifact has unexpected schemaVersion")
    if not isinstance(backfills, dict):
        errors.append("optimizer input bundle artifacts.backfills must be an object")
    else:
        errors.extend(validate_backfills(backfills))
    if not isinstance(performance, dict):
        errors.append("optimizer input bundle artifacts.performance must be an object")
    else:
        errors.extend(validate_performance(performance))
    if not isinstance(challenger_input, dict):
        errors.append("optimizer input bundle artifacts.challengerInput must be an object")
    else:
        schema_version = challenger_input.get("schemaVersion")
        if schema_version == "challenger-adjustments.sample.v1":
            errors.extend(validate_challenger_adjustments(challenger_input))
        elif schema_version == "challenger-observations.sample.v1":
            errors.extend(validate_challenger_observations(challenger_input))
        else:
            errors.append("optimizer input bundle challengerInput has unexpected schemaVersion")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        errors.append("optimizer input bundle must include object generatedFrom")
    else:
        input_sources = generated_from.get("inputSources")
        if not isinstance(input_sources, dict):
            errors.append("optimizer input bundle generatedFrom.inputSources must be an object")
        else:
            for key, expected_source_schema_version, expected_job_kind in (
                (
                    "backfills",
                    TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
                    TOPIC_OUTCOME_BACKFILL_JOB_KIND,
                ),
                (
                    "performance",
                    POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
                    POST_PERFORMANCE_SIGNAL_JOB_KIND,
                ),
                (
                    "challengerInput",
                    CHALLENGER_EVALUATION_RUN_SAMPLE_SCHEMA_VERSION,
                    CHALLENGER_EVALUATION_JOB_KIND,
                ),
            ):
                value = input_sources.get(key)
                prefix = f"optimizer input bundle generatedFrom.inputSources.{key}"
                if not isinstance(value, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                if value.get("sourceKind") != "job_run_envelope":
                    errors.append(f"{prefix}.sourceKind must be 'job_run_envelope'")
                if value.get("sourceSchemaVersion") != expected_source_schema_version:
                    errors.append(
                        f"{prefix}.sourceSchemaVersion must be {expected_source_schema_version!r}"
                    )
                if value.get("jobRunSchemaVersion") != expected_source_schema_version:
                    errors.append(
                        f"{prefix}.jobRunSchemaVersion must be {expected_source_schema_version!r}"
                    )
                if value.get("jobKind") != expected_job_kind:
                    errors.append(f"{prefix}.jobKind must be {expected_job_kind!r}")
                if not isinstance(value.get("jobRunId"), str) or not value.get("jobRunId"):
                    errors.append(f"{prefix}.jobRunId must be a non-empty string")
                if not isinstance(value.get("jobGeneratedAt"), str) or not value.get(
                    "jobGeneratedAt"
                ):
                    errors.append(f"{prefix}.jobGeneratedAt must be a non-empty string")
    return errors


def validate_optimizer_input_manifest(payload: dict[str, Any]) -> list[str]:
    try:
        validate_optimizer_input_manifest_payload(payload)
        return []
    except ValueError as exc:
        return [str(exc)]


def validate_optimizer_job_run(
    payload: dict[str, Any],
    *,
    schema_version: str,
    job_kind: str,
    expected_payload_validator,
    label: str,
) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != schema_version:
        errors.append(f"{label} has unexpected schemaVersion")
    if payload.get("jobKind") != job_kind:
        errors.append(f"{label}.jobKind must be {job_kind!r}")
    job_run_id = payload.get("jobRunId")
    if not isinstance(job_run_id, str) or not job_run_id:
        errors.append(f"{label}.jobRunId must be a non-empty string")
    generated_at = payload.get("generatedAt")
    if not isinstance(generated_at, str) or not generated_at:
        errors.append(f"{label}.generatedAt must be a non-empty string")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        errors.append(f"{label}.generatedFrom must be an object")
    inner_payload = payload.get("payload")
    if not isinstance(inner_payload, dict):
        return [*errors, f"{label}.payload must be an object"]
    return [*errors, *expected_payload_validator(inner_payload)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backfills",
        type=Path,
        default=DEFAULT_ROOT / "topic-outcome-backfills.sample.json",
    )
    parser.add_argument(
        "--backfill-run",
        type=Path,
        default=DEFAULT_ROOT / "topic-outcome-backfill-run.sample.json",
    )
    parser.add_argument(
        "--backfill-raw-run",
        type=Path,
        default=DEFAULT_ROOT / "topic-outcome-backfill-raw-run.sample.json",
    )
    parser.add_argument(
        "--backfills-raw",
        type=Path,
        default=DEFAULT_ROOT / "topic-outcome-backfills-raw.sample.json",
    )
    parser.add_argument(
        "--performance",
        type=Path,
        default=DEFAULT_ROOT / "post-performance-signals.sample.json",
    )
    parser.add_argument(
        "--performance-raw",
        type=Path,
        default=DEFAULT_ROOT / "post-performance-raw.sample.json",
    )
    parser.add_argument(
        "--performance-run",
        type=Path,
        default=DEFAULT_ROOT / "post-performance-signal-run.sample.json",
    )
    parser.add_argument(
        "--performance-raw-run",
        type=Path,
        default=DEFAULT_ROOT / "post-performance-signal-raw-run.sample.json",
    )
    parser.add_argument(
        "--challengers",
        type=Path,
        default=DEFAULT_ROOT / "challenger-adjustments.sample.json",
    )
    parser.add_argument(
        "--challenger-observations",
        type=Path,
        default=DEFAULT_ROOT / "challenger-observations.sample.json",
    )
    parser.add_argument(
        "--challenger-observations-raw",
        type=Path,
        default=DEFAULT_ROOT / "challenger-observations-raw.sample.json",
    )
    parser.add_argument(
        "--challenger-evaluation-run",
        type=Path,
        default=DEFAULT_ROOT / "challenger-evaluation-run.sample.json",
    )
    parser.add_argument(
        "--challenger-evaluation-raw-run",
        type=Path,
        default=DEFAULT_ROOT / "challenger-evaluation-raw-run.sample.json",
    )
    parser.add_argument(
        "--input-manifest",
        type=Path,
        default=DEFAULT_ROOT / "optimizer-input-manifest.sample.json",
    )
    parser.add_argument(
        "--input-bundle",
        type=Path,
        default=DEFAULT_ROOT / "optimizer-input-bundle.sample.json",
    )
    args = parser.parse_args()

    try:
        errors = [
            *validate_backfills(load_json(args.backfills)),
            *validate_optimizer_job_run(
                load_json(args.backfill_run),
                schema_version=TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
                job_kind=TOPIC_OUTCOME_BACKFILL_JOB_KIND,
                expected_payload_validator=validate_backfills,
                label="topic outcome backfill run fixture",
            ),
            *validate_backfills_raw(load_json(args.backfills_raw)),
            *validate_optimizer_job_run(
                load_json(args.backfill_raw_run),
                schema_version=TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
                job_kind=TOPIC_OUTCOME_BACKFILL_JOB_KIND,
                expected_payload_validator=validate_backfills_raw,
                label="topic outcome backfill raw run fixture",
            ),
            *validate_performance(load_json(args.performance)),
            *validate_performance_raw(load_json(args.performance_raw)),
            *validate_optimizer_job_run(
                load_json(args.performance_run),
                schema_version=POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
                job_kind=POST_PERFORMANCE_SIGNAL_JOB_KIND,
                expected_payload_validator=validate_performance,
                label="post performance signal run fixture",
            ),
            *validate_optimizer_job_run(
                load_json(args.performance_raw_run),
                schema_version=POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
                job_kind=POST_PERFORMANCE_SIGNAL_JOB_KIND,
                expected_payload_validator=validate_performance_raw,
                label="post performance raw run fixture",
            ),
            *validate_challenger_adjustments(load_json(args.challengers)),
            *validate_challenger_observations(load_json(args.challenger_observations)),
            *validate_challenger_observations_raw(
                load_json(args.challenger_observations_raw)
            ),
            *validate_optimizer_job_run(
                load_json(args.challenger_evaluation_run),
                schema_version=CHALLENGER_EVALUATION_RUN_SAMPLE_SCHEMA_VERSION,
                job_kind=CHALLENGER_EVALUATION_JOB_KIND,
                expected_payload_validator=validate_challenger_observations,
                label="challenger evaluation run fixture",
            ),
            *validate_optimizer_job_run(
                load_json(args.challenger_evaluation_raw_run),
                schema_version=CHALLENGER_EVALUATION_RUN_SAMPLE_SCHEMA_VERSION,
                job_kind=CHALLENGER_EVALUATION_JOB_KIND,
                expected_payload_validator=validate_challenger_observations_raw,
                label="challenger evaluation raw run fixture",
            ),
            *validate_optimizer_input_manifest(load_json(args.input_manifest)),
            *validate_optimizer_input_bundle(load_json(args.input_bundle)),
        ]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Optimizer fixture validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Optimizer fixtures are valid.")
    print(f"Backfills fixture: {args.backfills}")
    print(f"Backfill run fixture: {args.backfill_run}")
    print(f"Raw backfills fixture: {args.backfills_raw}")
    print(f"Raw backfill run fixture: {args.backfill_raw_run}")
    print(f"Performance fixture: {args.performance}")
    print(f"Raw performance fixture: {args.performance_raw}")
    print(f"Performance run fixture: {args.performance_run}")
    print(f"Raw performance run fixture: {args.performance_raw_run}")
    print(f"Challenger adjustments fixture: {args.challengers}")
    print(f"Challenger observations fixture: {args.challenger_observations}")
    print(f"Raw challenger observations fixture: {args.challenger_observations_raw}")
    print(f"Challenger evaluation run fixture: {args.challenger_evaluation_run}")
    print(f"Raw challenger evaluation run fixture: {args.challenger_evaluation_raw_run}")
    print(f"Optimizer input manifest fixture: {args.input_manifest}")
    print(f"Optimizer input bundle fixture: {args.input_bundle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
