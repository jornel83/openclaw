#!/usr/bin/env python3
"""
Input adapters for the AutoTikTok daily review runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPT_DIR = DEFAULT_ROOT.parent / "autotiktok" / "scripts"
if str(SHARED_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPT_DIR))

from optimizer_lib import DEFAULT_POLICY, load_policy
from optimizer_bundle_lib import (
    OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSIONS,
    OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSIONS,
    load_optimizer_input_manifest,
    materialize_optimizer_input_bundle_from_manifest,
)
from optimizer_job_input_lib import (
    unwrap_challenger_evaluation_input,
    unwrap_post_performance_signal_input,
    unwrap_topic_outcome_backfill_input,
)
from ranking_optimizer_contract_lib import (
    prepare_ranking_payload_for_optimizer,
    select_optimizer_handoff_payload,
)
from reward_lib import load_json


BACKFILLS_CANONICAL_SCHEMA_VERSIONS = {
    "topic-outcome-backfills.sample.v1",
    "topic-outcome-backfills.v1",
}
BACKFILLS_RAW_SCHEMA_VERSIONS = {
    "topic-outcome-backfills-raw.sample.v1",
    "topic-outcome-backfills-raw.v1",
}
BACKFILLS_SCHEMA_VERSIONS = (
    BACKFILLS_CANONICAL_SCHEMA_VERSIONS | BACKFILLS_RAW_SCHEMA_VERSIONS
)
BACKFILL_RAW_ITEM_SCHEMA_VERSION = "topic-outcome-backfill-raw-item.v1"
PERFORMANCE_CANONICAL_SCHEMA_VERSIONS = {
    "post-performance-signals.sample.v1",
    "post-performance-signals.v1",
}
PERFORMANCE_RAW_SCHEMA_VERSIONS = {
    "post-performance-raw.sample.v1",
    "post-performance-raw.v1",
}
PERFORMANCE_SCHEMA_VERSIONS = (
    PERFORMANCE_CANONICAL_SCHEMA_VERSIONS | PERFORMANCE_RAW_SCHEMA_VERSIONS
)
PERFORMANCE_RAW_ITEM_SCHEMA_VERSION = "post-performance-raw-item.v1"
CHALLENGER_SCHEMA_VERSIONS = {
    "challenger-adjustments.sample.v1",
    "challenger-adjustments.v1",
    "challenger-observations.sample.v1",
    "challenger-observations.v1",
}
CHALLENGER_ADJUSTMENT_SCHEMA_VERSIONS = {
    "challenger-adjustments.sample.v1",
    "challenger-adjustments.v1",
}
CHALLENGER_OBSERVATION_SCHEMA_VERSIONS = {
    "challenger-observations.sample.v1",
    "challenger-observations.v1",
}
CHALLENGER_RAW_OBSERVATION_SCHEMA_VERSIONS = {
    "challenger-observations-raw.sample.v1",
    "challenger-observations-raw.v1",
}
CHALLENGER_RAW_OBSERVATION_ITEM_SCHEMA_VERSION = (
    "challenger-observation-raw-item.v1"
)
CHALLENGER_SCHEMA_VERSIONS = (
    CHALLENGER_SCHEMA_VERSIONS | CHALLENGER_RAW_OBSERVATION_SCHEMA_VERSIONS
)
CHALLENGER_TOPIC_METRIC_KEYS = (
    "Hit@3",
    "Hit@10",
    "NDCG@10",
    "DupRate",
    "TypeCoverage",
    "Novelty",
    "ExecutableRate",
)


@dataclass(frozen=True)
class DailyReviewRuntimeInputs:
    ranking_artifact: dict[str, Any]
    ranking_payload: dict[str, Any]
    contract_metadata: dict[str, Any]
    context_payload: dict[str, Any]
    backfills_payload: dict[str, Any]
    performance_payload: dict[str, Any]
    challenger_payload: dict[str, Any]
    policy: dict[str, Any]
    bundle_metadata: dict[str, Any]
    input_source_metadata: dict[str, Any]


def _require_schema_version(
    payload: dict[str, Any], label: str, allowed_versions: set[str]
) -> str:
    schema_version = payload.get("schemaVersion")
    if schema_version not in allowed_versions:
        allowed = ", ".join(sorted(allowed_versions))
        raise ValueError(
            f"{label}.schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    return str(schema_version)


def _require_string(
    payload: dict[str, Any], key: str, label: str, *, allow_empty: bool = False
) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{label}.{key} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{label}.{key} must be non-empty")
    return value


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string when present")
    return value


def _require_object_list(
    payload: dict[str, Any], key: str, label: str
) -> list[dict[str, Any]]:
    items = payload.get(key)
    if not isinstance(items, list):
        raise ValueError(f"{label}.{key} must be a list")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{label}.{key}[{index}] must be an object")
        normalized.append(item)
    return normalized


def _optional_string_list(payload: dict[str, Any], key: str) -> list[str]:
    raw = payload.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
        raise ValueError(f"{key} must be a list of strings when present")
    return list(raw)


def _bounded_metric(
    payload: dict[str, Any], key: str, label: str, *, required: bool = True
) -> float | None:
    value = payload.get(key)
    if value is None:
        if required:
            raise ValueError(f"{label}.{key} must be present")
        return None
    if not isinstance(value, (int, float)):
        raise ValueError(f"{label}.{key} must be numeric")
    normalized = float(value)
    if not 0 <= normalized <= 1:
        raise ValueError(f"{label}.{key} must be between 0 and 1")
    return normalized


def _bounded_delta(
    payload: dict[str, Any], key: str, label: str, *, required: bool = True
) -> float | None:
    value = payload.get(key)
    if value is None:
        if required:
            raise ValueError(f"{label}.{key} must be present")
        return None
    if not isinstance(value, (int, float)):
        raise ValueError(f"{label}.{key} must be numeric")
    normalized = float(value)
    if not -1 <= normalized <= 1:
        raise ValueError(f"{label}.{key} must be between -1 and 1")
    return normalized


def _optional_positive_int(payload: dict[str, Any], key: str, label: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label}.{key} must be a positive integer when present")
    return value


def _require_object(payload: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{label}.{key} must be an object")
    return value


def _normalize_challenger_topic_metrics(
    payload: dict[str, Any], label: str
) -> dict[str, float]:
    return {
        key: _bounded_metric(payload, key, label) or 0.0
        for key in CHALLENGER_TOPIC_METRIC_KEYS
    }


def _normalize_challenger_performance_summary(
    payload: dict[str, Any], label: str
) -> dict[str, float | None]:
    performance_reward = _bounded_metric(
        payload, "performanceReward", label, required=False
    )
    performance_weight = _bounded_metric(
        payload, "performanceWeight", label, required=False
    )
    post_coverage_rate = _bounded_metric(
        payload, "postCoverageRate", label, required=False
    )
    if performance_reward is None and performance_weight is None and post_coverage_rate is None:
        return {
            "performanceReward": None,
            "performanceWeight": 0.0,
            "postCoverageRate": 0.0,
        }
    if performance_reward is None:
        raise ValueError(f"{label}.performanceReward must be present when a performance summary is provided")
    if performance_weight is None:
        raise ValueError(f"{label}.performanceWeight must be present when a performance summary is provided")
    return {
        "performanceReward": performance_reward,
        "performanceWeight": performance_weight,
        "postCoverageRate": 0.0 if post_coverage_rate is None else post_coverage_rate,
    }


def normalize_scoring_context(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schemaVersion") != "scoring-context.v1":
        raise ValueError("context.schemaVersion must be 'scoring-context.v1'")
    _require_string(payload, "accountId", "context")
    return payload


def normalize_topic_outcome_backfills(
    payload: dict[str, Any], *, expected_run_id: str
) -> dict[str, Any]:
    schema_version = _require_schema_version(
        payload, "backfills", BACKFILLS_SCHEMA_VERSIONS
    )
    is_raw_payload = schema_version in BACKFILLS_RAW_SCHEMA_VERSIONS
    run_id = _require_string(payload, "runId", "backfills")
    if (
        schema_version in {"topic-outcome-backfills.v1", "topic-outcome-backfills-raw.v1"}
        and run_id != expected_run_id
    ):
        raise ValueError(
            f"backfills.runId must match ranking runId {expected_run_id!r}, got {run_id!r}"
        )
    evaluation_window = _require_string(payload, "evaluationWindow", "backfills")
    items = []
    for index, item in enumerate(_require_object_list(payload, "items", "backfills")):
        label = f"backfills.items[{index}]"
        item_schema_version = _require_string(item, "schemaVersion", label)
        item_run_id = _require_string(item, "runId", label)
        if item_run_id != run_id:
            raise ValueError(f"{label}.runId must match backfills.runId")
        backfill_window = _require_string(
            item,
            "observedWindow" if is_raw_payload else "backfillWindow",
            label,
        )
        if backfill_window != evaluation_window:
            raise ValueError(
                f"{label}.{'observedWindow' if is_raw_payload else 'backfillWindow'} "
                "must match backfills.evaluationWindow"
            )
        if is_raw_payload:
            if item_schema_version != BACKFILL_RAW_ITEM_SCHEMA_VERSION:
                raise ValueError(
                    f"{label}.schemaVersion must be {BACKFILL_RAW_ITEM_SCHEMA_VERSION!r}"
                )
            items.append(
                {
                    "schemaVersion": "topic-outcome-backfill.v1",
                    "backfillId": _require_string(item, "backfillId", label),
                    "runId": item_run_id,
                    "topicId": _require_string(item, "topicId", label),
                    "topicFingerprint": _require_string(
                        item, "topicFingerprint", label
                    ),
                    "backfillWindow": backfill_window,
                    "evaluatedAt": _optional_string(item, "matchedAt"),
                    "matchedBy": _require_string(item, "matchStrategy", label),
                    "coverageWindowDays": _optional_positive_int(
                        item, "coverageDays", label
                    ),
                    "searchLift": _bounded_metric(item, "queryLiftScore", label),
                    "futureVideoDensity": _bounded_metric(
                        item, "futureTopicDensityScore", label
                    ),
                    "contentGapPersistence": _bounded_metric(
                        item, "contentGapPersistenceScore", label
                    ),
                    "matchedFutureTopicFingerprints": _optional_string_list(
                        item, "matchedFutureFingerprints"
                    ),
                    "evidenceRefs": _optional_string_list(
                        item, "evidenceSourceRefs"
                    ),
                    "outcomeConfidence": _bounded_metric(
                        item, "matchConfidence", label, required=False
                    ),
                }
            )
            continue
        if item_schema_version != "topic-outcome-backfill.v1":
            raise ValueError(
                f"{label}.schemaVersion must be 'topic-outcome-backfill.v1'"
            )
        items.append(
            {
                "schemaVersion": item_schema_version,
                "backfillId": _require_string(item, "backfillId", label),
                "runId": item_run_id,
                "topicId": _require_string(item, "topicId", label),
                "topicFingerprint": _require_string(item, "topicFingerprint", label),
                "backfillWindow": backfill_window,
                "evaluatedAt": _optional_string(item, "evaluatedAt"),
                "matchedBy": _require_string(item, "matchedBy", label),
                "coverageWindowDays": _optional_positive_int(
                    item, "coverageWindowDays", label
                ),
                "searchLift": _bounded_metric(item, "searchLift", label),
                "futureVideoDensity": _bounded_metric(
                    item, "futureVideoDensity", label
                ),
                "contentGapPersistence": _bounded_metric(
                    item, "contentGapPersistence", label
                ),
                "matchedFutureTopicFingerprints": _optional_string_list(
                    item, "matchedFutureTopicFingerprints"
                ),
                "evidenceRefs": _optional_string_list(item, "evidenceRefs"),
                "outcomeConfidence": _bounded_metric(
                    item, "outcomeConfidence", label, required=False
                ),
            }
        )
    normalized_schema_version = (
        "topic-outcome-backfills.sample.v1"
        if schema_version == "topic-outcome-backfills-raw.sample.v1"
        else "topic-outcome-backfills.v1"
        if schema_version == "topic-outcome-backfills-raw.v1"
        else schema_version
    )
    return {
        "schemaVersion": normalized_schema_version,
        "runId": run_id,
        "snapshotId": _optional_string(payload, "snapshotId"),
        "evaluationWindow": evaluation_window,
        "evaluatedAt": _optional_string(payload, "evaluatedAt"),
        "items": items,
    }


def normalize_post_performance_signals(
    payload: dict[str, Any], *, expected_run_id: str, expected_account_id: str
) -> dict[str, Any]:
    schema_version = _require_schema_version(
        payload, "performance", PERFORMANCE_SCHEMA_VERSIONS
    )
    is_raw_payload = schema_version in PERFORMANCE_RAW_SCHEMA_VERSIONS
    run_id = _require_string(payload, "runId", "performance")
    if (
        schema_version in {"post-performance-signals.v1", "post-performance-raw.v1"}
        and run_id != expected_run_id
    ):
        raise ValueError(
            f"performance.runId must match ranking runId {expected_run_id!r}, got {run_id!r}"
        )
    account_id = _require_string(payload, "accountId", "performance")
    if (
        schema_version in {"post-performance-signals.v1", "post-performance-raw.v1"}
        and account_id != expected_account_id
    ):
        raise ValueError(
            "performance.accountId must match context.accountId "
            f"{expected_account_id!r}, got {account_id!r}"
        )
    measured_window = _require_string(payload, "measuredWindow", "performance")
    items = []
    for index, item in enumerate(_require_object_list(payload, "items", "performance")):
        label = f"performance.items[{index}]"
        item_schema_version = _require_string(item, "schemaVersion", label)
        item_run_id = _require_string(item, "runId", label)
        if item_run_id != run_id:
            raise ValueError(f"{label}.runId must match performance.runId")
        item_account_id = _require_string(item, "accountId", label)
        if item_account_id != account_id:
            raise ValueError(f"{label}.accountId must match performance.accountId")
        item_measured_window = _require_string(item, "measuredWindow", label)
        if item_measured_window != measured_window:
            raise ValueError(
                f"{label}.measuredWindow must match performance.measuredWindow"
            )
        if is_raw_payload:
            if item_schema_version != PERFORMANCE_RAW_ITEM_SCHEMA_VERSION:
                raise ValueError(
                    f"{label}.schemaVersion must be {PERFORMANCE_RAW_ITEM_SCHEMA_VERSION!r}"
                )
            items.append(
                {
                    "schemaVersion": "post-performance-signal.v1",
                    "signalId": _require_string(item, "signalId", label),
                    "runId": item_run_id,
                    "topicId": _require_string(item, "topicId", label),
                    "topicFingerprint": _optional_string(item, "topicFingerprint"),
                    "postId": _require_string(item, "postId", label),
                    "accountId": item_account_id,
                    "publishedAt": _optional_string(item, "publishedAt"),
                    "contentBucketId": _optional_string(item, "contentBucketId"),
                    "format": _optional_string(item, "format"),
                    "measuredWindow": item_measured_window,
                    "measuredAt": _optional_string(item, "measuredAt"),
                    "rawViews": _optional_positive_int(item, "observedViews", label),
                    "baselineViews": _optional_positive_int(
                        item, "expectedViews", label
                    ),
                    "viewLift": _bounded_metric(item, "normalizedViewLift", label),
                    "retentionProxy": _bounded_metric(
                        item, "retentionRatio", label, required=False
                    ),
                    "shareSaveProxy": _bounded_metric(
                        item, "shareSaveRate", label, required=False
                    ),
                    "followConversionProxy": _bounded_metric(
                        item, "followConversionRate", label, required=False
                    ),
                }
            )
            continue
        if item_schema_version != "post-performance-signal.v1":
            raise ValueError(
                f"{label}.schemaVersion must be 'post-performance-signal.v1'"
            )
        items.append(
            {
                "schemaVersion": item_schema_version,
                "signalId": _require_string(item, "signalId", label),
                "runId": item_run_id,
                "topicId": _require_string(item, "topicId", label),
                "topicFingerprint": _optional_string(item, "topicFingerprint"),
                "postId": _require_string(item, "postId", label),
                "accountId": item_account_id,
                "publishedAt": _optional_string(item, "publishedAt"),
                "contentBucketId": _optional_string(item, "contentBucketId"),
                "format": _optional_string(item, "format"),
                "measuredWindow": item_measured_window,
                "measuredAt": _optional_string(item, "measuredAt"),
                "rawViews": _optional_positive_int(item, "rawViews", label),
                "baselineViews": _optional_positive_int(item, "baselineViews", label),
                "viewLift": _bounded_metric(item, "viewLift", label),
                "retentionProxy": _bounded_metric(
                    item, "retentionProxy", label, required=False
                ),
                "shareSaveProxy": _bounded_metric(
                    item, "shareSaveProxy", label, required=False
                ),
                "followConversionProxy": _bounded_metric(
                    item, "followConversionProxy", label, required=False
                ),
            }
        )
    normalized_schema_version = (
        "post-performance-signals.sample.v1"
        if schema_version == "post-performance-raw.sample.v1"
        else "post-performance-signals.v1"
        if schema_version == "post-performance-raw.v1"
        else schema_version
    )
    return {
        "schemaVersion": normalized_schema_version,
        "runId": run_id,
        "accountId": account_id,
        "measuredWindow": measured_window,
        "items": items,
    }


def normalize_challenger_adjustments(
    payload: dict[str, Any], *, champion_profile_id: str
) -> dict[str, Any]:
    schema_version = _require_schema_version(
        payload, "challengers", CHALLENGER_SCHEMA_VERSIONS
    )
    champion_id = _require_string(payload, "championProfileId", "challengers")
    if schema_version == "challenger-adjustments.v1" and champion_id != champion_profile_id:
        raise ValueError(
            "challengers.championProfileId must match ranking champion profile "
            f"{champion_profile_id!r}, got {champion_id!r}"
        )
    challengers = []
    seen_profile_ids: set[str] = set()
    for index, item in enumerate(_require_object_list(payload, "challengers", "challengers")):
        label = f"challengers.items[{index}]"
        profile_id = _require_string(item, "profileId", label)
        if schema_version == "challenger-adjustments.v1" and profile_id == champion_profile_id:
            raise ValueError(
                f"{label}.profileId must differ from championProfileId"
            )
        if profile_id in seen_profile_ids:
            raise ValueError(f"{label}.profileId is duplicated: {profile_id}")
        seen_profile_ids.add(profile_id)
        challengers.append(
            {
                "profileId": profile_id,
                "topicRewardDelta": _bounded_delta(
                    item, "topicRewardDelta", label, required=False
                )
                or 0.0,
                "performanceRewardDelta": _bounded_delta(
                    item, "performanceRewardDelta", label, required=False
                )
                or 0.0,
                "dupRateDelta": _bounded_delta(item, "dupRateDelta", label, required=False)
                or 0.0,
                "typeCoverageDelta": _bounded_delta(
                    item, "typeCoverageDelta", label, required=False
                )
                or 0.0,
                "executableRateDelta": _bounded_delta(
                    item, "executableRateDelta", label, required=False
                )
                or 0.0,
                "holdoutDelta": _bounded_delta(item, "holdoutDelta", label, required=False)
                or 0.0,
                "daysObserved": _optional_positive_int(item, "daysObserved", label) or 1,
                "notes": _optional_string(item, "notes") or "",
            }
        )
    return {
        "schemaVersion": schema_version,
        "inputKind": "adjustments",
        "championProfileId": champion_id,
        "observationWindow": _optional_string(payload, "observationWindow"),
        "generatedAt": _optional_string(payload, "generatedAt"),
        "challengers": challengers,
    }


def normalize_challenger_observations(
    payload: dict[str, Any], *, champion_profile_id: str
) -> dict[str, Any]:
    schema_version = _require_schema_version(
        payload,
        "challengers",
        CHALLENGER_OBSERVATION_SCHEMA_VERSIONS
        | CHALLENGER_RAW_OBSERVATION_SCHEMA_VERSIONS,
    )
    is_raw_payload = schema_version in CHALLENGER_RAW_OBSERVATION_SCHEMA_VERSIONS
    champion_id = _require_string(payload, "championProfileId", "challengers")
    if (
        schema_version
        in {"challenger-observations.v1", "challenger-observations-raw.v1"}
        and champion_id != champion_profile_id
    ):
        raise ValueError(
            "challengers.championProfileId must match ranking champion profile "
            f"{champion_profile_id!r}, got {champion_id!r}"
        )
    evaluation_window = _require_string(payload, "evaluationWindow", "challengers")
    challengers = []
    seen_profile_ids: set[str] = set()
    for index, item in enumerate(_require_object_list(payload, "challengers", "challengers")):
        label = f"challengers.items[{index}]"
        item_schema_version = _require_string(item, "schemaVersion", label)
        profile_id = _require_string(item, "profileId", label)
        if (
            schema_version
            in {"challenger-observations.v1", "challenger-observations-raw.v1"}
            and profile_id == champion_profile_id
        ):
            raise ValueError(f"{label}.profileId must differ from championProfileId")
        if profile_id in seen_profile_ids:
            raise ValueError(f"{label}.profileId is duplicated: {profile_id}")
        seen_profile_ids.add(profile_id)
        if is_raw_payload:
            if item_schema_version != CHALLENGER_RAW_OBSERVATION_ITEM_SCHEMA_VERSION:
                raise ValueError(
                    f"{label}.schemaVersion must be "
                    f"{CHALLENGER_RAW_OBSERVATION_ITEM_SCHEMA_VERSION!r}"
                )
            ranking_quality = _require_object(item, "rankingQuality", label)
            performance_aggregate = _require_object(
                item, "performanceAggregate", label
            )
            performance_summary = _normalize_challenger_performance_summary(
                {
                    "performanceReward": performance_aggregate.get(
                        "normalizedReward"
                    ),
                    "performanceWeight": performance_aggregate.get("appliedWeight"),
                    "postCoverageRate": performance_aggregate.get("coverageRate"),
                },
                f"{label}.performanceAggregate",
            )
            challengers.append(
                {
                    "schemaVersion": "challenger-observation.v1",
                    "profileId": profile_id,
                    "topicMetrics": {
                        "Hit@3": _bounded_metric(
                            ranking_quality, "top3HitRate", f"{label}.rankingQuality"
                        )
                        or 0.0,
                        "Hit@10": _bounded_metric(
                            ranking_quality, "top10HitRate", f"{label}.rankingQuality"
                        )
                        or 0.0,
                        "NDCG@10": _bounded_metric(
                            ranking_quality, "ndcg10", f"{label}.rankingQuality"
                        )
                        or 0.0,
                        "DupRate": _bounded_metric(
                            ranking_quality,
                            "duplicationRate",
                            f"{label}.rankingQuality",
                        )
                        or 0.0,
                        "TypeCoverage": _bounded_metric(
                            ranking_quality,
                            "typeCoverageRate",
                            f"{label}.rankingQuality",
                        )
                        or 0.0,
                        "Novelty": _bounded_metric(
                            ranking_quality, "noveltyScore", f"{label}.rankingQuality"
                        )
                        or 0.0,
                        "ExecutableRate": _bounded_metric(
                            ranking_quality,
                            "executableRate",
                            f"{label}.rankingQuality",
                        )
                        or 0.0,
                    },
                    "performanceSummary": performance_summary,
                    "holdoutDelta": _bounded_delta(
                        item, "holdoutDelta", label, required=False
                    )
                    or 0.0,
                    "daysObserved": _optional_positive_int(
                        item, "observedDays", label
                    )
                    or 1,
                    "notes": _optional_string(item, "notes") or "",
                }
            )
            continue
        if item_schema_version != "challenger-observation.v1":
            raise ValueError(
                f"{label}.schemaVersion must be 'challenger-observation.v1'"
            )
        performance_summary = _normalize_challenger_performance_summary(
            _require_object(item, "performanceSummary", label),
            f"{label}.performanceSummary",
        )
        challengers.append(
            {
                "schemaVersion": item_schema_version,
                "profileId": profile_id,
                "topicMetrics": _normalize_challenger_topic_metrics(
                    _require_object(item, "topicMetrics", label),
                    f"{label}.topicMetrics",
                ),
                "performanceSummary": performance_summary,
                "holdoutDelta": _bounded_delta(
                    item, "holdoutDelta", label, required=False
                )
                or 0.0,
                "daysObserved": _optional_positive_int(item, "daysObserved", label) or 1,
                "notes": _optional_string(item, "notes") or "",
            }
        )
    normalized_schema_version = (
        "challenger-observations.sample.v1"
        if schema_version == "challenger-observations-raw.sample.v1"
        else "challenger-observations.v1"
        if schema_version == "challenger-observations-raw.v1"
        else schema_version
    )
    return {
        "schemaVersion": normalized_schema_version,
        "inputKind": "observations",
        "championProfileId": champion_id,
        "evaluationWindow": evaluation_window,
        "observationWindow": _optional_string(payload, "observationWindow"),
        "generatedAt": _optional_string(payload, "generatedAt"),
        "challengers": challengers,
    }


def normalize_challenger_input(
    payload: dict[str, Any], *, champion_profile_id: str
) -> dict[str, Any]:
    schema_version = _require_schema_version(
        payload, "challengers", CHALLENGER_SCHEMA_VERSIONS
    )
    if schema_version in CHALLENGER_ADJUSTMENT_SCHEMA_VERSIONS:
        return normalize_challenger_adjustments(
            payload, champion_profile_id=champion_profile_id
        )
    return normalize_challenger_observations(
        payload, champion_profile_id=champion_profile_id
    )


def normalize_optimizer_input_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    schema_version = _require_schema_version(
        payload, "bundle", OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSIONS
    )
    artifacts = _require_object(payload, "artifacts", "bundle")
    ranking_artifact = _require_object(artifacts, "ranking", "bundle.artifacts")
    context_payload = _require_object(artifacts, "context", "bundle.artifacts")
    backfills_payload = _require_object(artifacts, "backfills", "bundle.artifacts")
    performance_payload = _require_object(artifacts, "performance", "bundle.artifacts")
    challenger_payload = _require_object(
        artifacts, "challengerInput", "bundle.artifacts"
    )
    return {
        "schemaVersion": schema_version,
        "bundleId": _optional_string(payload, "bundleId"),
        "generatedAt": _optional_string(payload, "generatedAt"),
        "generatedFrom": _require_object(payload, "generatedFrom", "bundle")
        if payload.get("generatedFrom") is not None
        else {},
        "artifacts": {
            "ranking": ranking_artifact,
            "context": context_payload,
            "backfills": backfills_payload,
            "performance": performance_payload,
            "challengerInput": challenger_payload,
        },
    }


def normalize_optimizer_input_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer input manifest schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    artifact_paths = payload.get("artifactPaths")
    artifact_bindings = payload.get("artifactBindings")
    has_paths = isinstance(artifact_paths, dict)
    has_bindings = isinstance(artifact_bindings, dict)
    if has_paths == has_bindings:
        raise ValueError(
            "optimizer input manifest must include exactly one of `artifactPaths` or `artifactBindings`"
        )
    normalized = {
        "schemaVersion": schema_version,
        "manifestId": _optional_string(payload, "manifestId"),
        "generatedAt": _optional_string(payload, "generatedAt"),
        "generatedFrom": payload.get("generatedFrom", {}),
    }
    if has_paths:
        normalized["artifactPaths"] = artifact_paths
        return normalized
    registry_reference = payload.get("inputSourceRegistryReference")
    if not isinstance(registry_reference, dict):
        raise ValueError(
            "optimizer input manifest with artifactBindings must include object `inputSourceRegistryReference`"
        )
    normalized["artifactBindings"] = artifact_bindings
    normalized["inputSourceRegistryReference"] = registry_reference
    return normalized


def _build_runtime_inputs_from_payloads(
    *,
    ranking_artifact_payload: dict[str, Any],
    context_payload_raw: dict[str, Any],
    backfills_payload_raw: dict[str, Any],
    performance_payload_raw: dict[str, Any],
    challenger_payload_raw: dict[str, Any],
    policy_input: Path,
    contract_version: str,
    validation_mode: str,
    bundle_metadata: dict[str, Any] | None = None,
    input_source_metadata: dict[str, Any] | None = None,
) -> DailyReviewRuntimeInputs:
    ranking_artifact, contract_metadata = prepare_ranking_payload_for_optimizer(
        ranking_artifact_payload,
        label="ranking",
        contract_version=contract_version,
        validation_mode=validation_mode,
    )
    ranking_payload = select_optimizer_handoff_payload(
        ranking_artifact,
        contract_version=contract_version,
    )
    context_payload = normalize_scoring_context(context_payload_raw)
    ranking_run_id = ranking_payload["predictionRun"]["runId"]
    ranking_profile_id = ranking_payload["predictionRun"]["profileId"]
    normalized_backfills_payload_raw, backfills_source_metadata = (
        unwrap_topic_outcome_backfill_input(backfills_payload_raw)
    )
    (
        normalized_performance_payload_raw,
        performance_source_metadata,
    ) = unwrap_post_performance_signal_input(performance_payload_raw)
    (
        normalized_challenger_payload_raw,
        challenger_source_metadata,
    ) = unwrap_challenger_evaluation_input(challenger_payload_raw)
    backfills_payload = normalize_topic_outcome_backfills(
        normalized_backfills_payload_raw,
        expected_run_id=ranking_run_id,
    )
    performance_payload = normalize_post_performance_signals(
        normalized_performance_payload_raw,
        expected_run_id=ranking_run_id,
        expected_account_id=context_payload["accountId"],
    )
    challenger_payload = normalize_challenger_input(
        normalized_challenger_payload_raw,
        champion_profile_id=ranking_profile_id,
    )
    policy = load_policy(policy_input)
    return DailyReviewRuntimeInputs(
        ranking_artifact=ranking_artifact,
        ranking_payload=ranking_payload,
        contract_metadata=contract_metadata,
        context_payload=context_payload,
        backfills_payload=backfills_payload,
        performance_payload=performance_payload,
        challenger_payload=challenger_payload,
        policy=policy,
        bundle_metadata={} if bundle_metadata is None else dict(bundle_metadata),
        input_source_metadata=(
            {
                "backfills": backfills_source_metadata,
                "performance": performance_source_metadata,
                "challengerInput": challenger_source_metadata,
            }
            if input_source_metadata is None
            else dict(input_source_metadata)
        ),
    )


def load_daily_review_runtime_inputs_from_bundle(
    *,
    input_bundle: Path,
    policy_input: Path = DEFAULT_POLICY,
    contract_version: str,
    validation_mode: str,
) -> DailyReviewRuntimeInputs:
    bundle_payload = normalize_optimizer_input_bundle(load_json(input_bundle))
    artifacts = bundle_payload["artifacts"]
    return _build_runtime_inputs_from_payloads(
        ranking_artifact_payload=artifacts["ranking"],
        context_payload_raw=artifacts["context"],
        backfills_payload_raw=artifacts["backfills"],
        performance_payload_raw=artifacts["performance"],
        challenger_payload_raw=artifacts["challengerInput"],
        policy_input=policy_input,
        contract_version=contract_version,
        validation_mode=validation_mode,
        bundle_metadata={
            "optimizerInputBundleSchemaVersion": bundle_payload["schemaVersion"],
            "optimizerInputBundleId": bundle_payload.get("bundleId"),
            "optimizerInputBundleGeneratedAt": bundle_payload.get("generatedAt"),
            "optimizerInputBundleGeneratedFrom": bundle_payload.get("generatedFrom", {}),
            "optimizerInputManifestSchemaVersion": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputManifestSchemaVersion"),
            "optimizerInputManifestId": bundle_payload.get("generatedFrom", {}).get(
                "optimizerInputManifestId"
            ),
            "optimizerInputManifestGeneratedAt": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputManifestGeneratedAt"),
            "optimizerInputManifestGeneratedFrom": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputManifestGeneratedFrom", {}),
            "optimizerInputSourceRegistrySchemaVersion": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceRegistrySchemaVersion"),
            "optimizerInputSourceRegistryId": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceRegistryId"),
            "optimizerInputArtifactResolverSchemaVersion": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactResolverSchemaVersion"),
            "optimizerInputArtifactResolverId": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactResolverId"),
            "optimizerInputSourceProviderCatalogSchemaVersion": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderCatalogSchemaVersion"),
            "optimizerInputSourceProviderCatalogId": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderCatalogId"),
            "optimizerInputSourceProviderRegistrySchemaVersion": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderRegistrySchemaVersion"),
            "optimizerInputSourceProviderRegistryId": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderRegistryId"),
            "optimizerInputSourceArtifactCatalogSchemaVersion": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceArtifactCatalogSchemaVersion"),
            "optimizerInputSourceArtifactCatalogId": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceArtifactCatalogId"),
            "optimizerInputSourceProviderLane": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderLane"),
            "optimizerInputSourceProviderKind": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderKind"),
            "optimizerInputSourceProviderClass": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderClass"),
            "optimizerInputSourceProviderHandle": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderHandle"),
            "optimizerInputSourceProviderLocatorKind": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderLocatorKind"),
            "optimizerInputSourceProviderOwner": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderOwner"),
            "optimizerInputArtifactLocatorKind": bundle_payload.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactLocatorKind"),
        },
        input_source_metadata=bundle_payload.get("generatedFrom", {}).get(
            "inputSources", {}
        ),
    )


def load_daily_review_runtime_inputs_from_manifest(
    *,
    input_manifest: Path,
    policy_input: Path = DEFAULT_POLICY,
    contract_version: str,
    validation_mode: str,
) -> DailyReviewRuntimeInputs:
    manifest_payload_raw, _ = load_optimizer_input_manifest(input_manifest)
    manifest_payload = normalize_optimizer_input_manifest(manifest_payload_raw)
    bundle_payload, _ = materialize_optimizer_input_bundle_from_manifest(
        manifest_path=input_manifest,
        bundle_schema_version="optimizer-input-bundle.v1",
    )
    bundle_inputs = normalize_optimizer_input_bundle(bundle_payload)
    artifacts = bundle_inputs["artifacts"]
    return _build_runtime_inputs_from_payloads(
        ranking_artifact_payload=artifacts["ranking"],
        context_payload_raw=artifacts["context"],
        backfills_payload_raw=artifacts["backfills"],
        performance_payload_raw=artifacts["performance"],
        challenger_payload_raw=artifacts["challengerInput"],
        policy_input=policy_input,
        contract_version=contract_version,
        validation_mode=validation_mode,
        bundle_metadata={
            "optimizerInputBundleSchemaVersion": bundle_inputs["schemaVersion"],
            "optimizerInputBundleId": bundle_inputs.get("bundleId"),
            "optimizerInputBundleGeneratedAt": bundle_inputs.get("generatedAt"),
            "optimizerInputBundleGeneratedFrom": bundle_inputs.get("generatedFrom", {}),
            "optimizerInputManifestSchemaVersion": manifest_payload["schemaVersion"],
            "optimizerInputManifestId": manifest_payload.get("manifestId"),
            "optimizerInputManifestGeneratedAt": manifest_payload.get("generatedAt"),
            "optimizerInputManifestGeneratedFrom": manifest_payload.get("generatedFrom", {}),
            "optimizerInputSourceRegistrySchemaVersion": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceRegistrySchemaVersion"),
            "optimizerInputSourceRegistryId": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceRegistryId"),
            "optimizerInputArtifactResolverSchemaVersion": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactResolverSchemaVersion"),
            "optimizerInputArtifactResolverId": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactResolverId"),
            "optimizerInputSourceProviderCatalogSchemaVersion": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderCatalogSchemaVersion"),
            "optimizerInputSourceProviderCatalogId": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderCatalogId"),
            "optimizerInputSourceProviderRegistrySchemaVersion": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderRegistrySchemaVersion"),
            "optimizerInputSourceProviderRegistryId": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderRegistryId"),
            "optimizerInputSourceArtifactCatalogSchemaVersion": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceArtifactCatalogSchemaVersion"),
            "optimizerInputSourceArtifactCatalogId": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceArtifactCatalogId"),
            "optimizerInputSourceProviderLane": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderLane"),
            "optimizerInputSourceProviderKind": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderKind"),
            "optimizerInputSourceProviderClass": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderClass"),
            "optimizerInputSourceProviderHandle": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderHandle"),
            "optimizerInputSourceProviderLocatorKind": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderLocatorKind"),
            "optimizerInputSourceProviderOwner": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderOwner"),
            "optimizerInputArtifactLocatorKind": bundle_inputs.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactLocatorKind"),
        },
        input_source_metadata=bundle_inputs.get("generatedFrom", {}).get(
            "inputSources", {}
        ),
    )


def load_daily_review_runtime_inputs(
    *,
    ranking_input: Path | None = None,
    context_input: Path | None = None,
    backfills_input: Path | None = None,
    performance_input: Path | None = None,
    challenger_input: Path | None = None,
    input_bundle: Path | None = None,
    input_manifest: Path | None = None,
    policy_input: Path = DEFAULT_POLICY,
    contract_version: str,
    validation_mode: str,
) -> DailyReviewRuntimeInputs:
    if input_manifest is not None:
        return load_daily_review_runtime_inputs_from_manifest(
            input_manifest=input_manifest,
            policy_input=policy_input,
            contract_version=contract_version,
            validation_mode=validation_mode,
        )
    if input_bundle is not None:
        return load_daily_review_runtime_inputs_from_bundle(
            input_bundle=input_bundle,
            policy_input=policy_input,
            contract_version=contract_version,
            validation_mode=validation_mode,
        )
    if (
        ranking_input is None
        or context_input is None
        or backfills_input is None
        or performance_input is None
        or challenger_input is None
    ):
        raise ValueError(
            "ranking_input, context_input, backfills_input, performance_input, and "
            "challenger_input are required when neither input_bundle nor input_manifest is provided"
        )
    return _build_runtime_inputs_from_payloads(
        ranking_artifact_payload=load_json(ranking_input),
        context_payload_raw=load_json(context_input),
        backfills_payload_raw=load_json(backfills_input),
        performance_payload_raw=load_json(performance_input),
        challenger_payload_raw=load_json(challenger_input),
        policy_input=policy_input,
        contract_version=contract_version,
        validation_mode=validation_mode,
    )
