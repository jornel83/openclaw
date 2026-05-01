#!/usr/bin/env python3
"""
Reusable discovery helpers for the AutoTikTok topic-discovery skill.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = SKILL_ROOT / "config" / "discovery-policy.v1.json"
NORMALIZATION_RULE_VERSION = "discovery-normalization.v1"

RAW_SIGNAL_SCHEMA_VERSIONS = {"raw-signals.sample.v1", "raw-signals.v1"}
SNAPSHOT_MATERIALIZATION_SCHEMA_VERSIONS = {
    "discovery-snapshot-materialization.sample.v1",
    "discovery-snapshot-materialization.v1",
}
SOURCE_SNAPSHOTS_SCHEMA_VERSIONS = {
    "discovery-source-snapshots.sample.v1",
    "discovery-source-snapshots.v1",
}
SIGNAL_ITEMS_SCHEMA_VERSIONS = {
    "discovery-signal-items.sample.v1",
    "discovery-signal-items.v1",
}
VIDEO_SAMPLES_SCHEMA_VERSIONS = {
    "discovery-video-samples.sample.v1",
    "discovery-video-samples.v1",
}

RAW_SIGNAL_REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "snapshotId",
    "market",
    "language",
    "capturedAt",
    "sourceSnapshots",
    "signals",
}

RAW_SIGNAL_REQUIRED_FIELDS = {
    "signalId",
    "capturedAt",
    "sourceSnapshotRef",
    "signalConfidence",
    "topicId",
    "topicFingerprint",
    "topicTitle",
    "topicSummary",
    "topicType",
    "sourceType",
    "keywords",
    "contentAngles",
    "seedQueries",
    "relatedQueries",
    "contentGapQueries",
    "searchIntentType",
    "searchPersistenceHint",
    "recommendedMode",
    "freshnessWindow",
    "expandabilityHint",
    "recommendedFormats",
    "requiredAssets",
    "requiredCapabilities",
    "productionComplexity",
    "dependencyRisk",
    "fastTurnaround",
    "executionNotes",
}

SNAPSHOT_MATERIALIZATION_REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "materializationId",
    "snapshotId",
    "market",
    "language",
    "capturedAt",
    "sourceSnapshots",
    "signalItems",
    "videoSamples",
}

SNAPSHOT_REQUIRED_FIELDS = {
    "sourceSnapshotId",
    "source",
    "capturedAt",
}
SOURCE_SNAPSHOTS_REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "snapshotId",
    "market",
    "language",
    "capturedAt",
    "sourceSnapshots",
}
SIGNAL_ITEMS_REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "snapshotId",
    "market",
    "language",
    "capturedAt",
    "signalItems",
}
VIDEO_SAMPLES_REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "snapshotId",
    "market",
    "language",
    "capturedAt",
    "videoSamples",
}

SNAPSHOT_SIGNAL_REQUIRED_FIELDS = {
    "signalId",
    "capturedAt",
    "sourceSnapshotId",
    "signalConfidence",
    "topicId",
    "topicFingerprint",
    "topicTitle",
    "topicSummary",
    "topicType",
    "sourceType",
    "keywords",
    "contentAngles",
    "seedQueries",
    "relatedQueries",
    "contentGapQueries",
    "searchIntentType",
    "searchPersistenceHint",
    "recommendedMode",
    "freshnessWindow",
    "expandabilityHint",
    "recommendedFormats",
    "requiredAssets",
    "requiredCapabilities",
    "productionComplexity",
    "dependencyRisk",
    "fastTurnaround",
    "executionNotes",
}

VIDEO_SAMPLE_REQUIRED_FIELDS = {
    "videoSampleId",
    "sourceSnapshotId",
    "publishedAt",
    "title",
    "desc",
    "hashtags",
    "authorId",
    "metrics",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "up",
    "why",
    "with",
}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def unique_preserve(values: list[str], cap: int | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
        if cap is not None and len(out) >= cap:
            break
    return out


def average(nums: list[float], fallback: float = 0.0) -> float:
    if not nums:
        return fallback
    return sum(nums) / len(nums)


def round_with_precision(value: float, digits: int) -> float:
    return round(value + 1e-9, digits)


def normalize_phrase(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(str(value).lower()))


def tokenize_phrase(value: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(normalize_phrase(value)) if token]


def derive_abstraction_terms(
    topic_title: str,
    keywords: list[str],
    search_phrases: list[str],
    content_angles: list[str],
    *,
    cap: int = 4,
) -> list[str]:
    token_counter: Counter[str] = Counter()
    weighted_phrases = [topic_title, *search_phrases, *keywords, *content_angles]
    for phrase in weighted_phrases:
        for token in tokenize_phrase(phrase):
            if token in STOPWORDS or len(token) <= 1:
                continue
            token_counter[token] += 1
    if not token_counter:
        return []
    return [
        token
        for token, _count in sorted(token_counter.items(), key=lambda item: (-item[1], item[0]))[
            :cap
        ]
    ]


def build_signal_normalization(signal: dict[str, Any]) -> dict[str, Any]:
    normalized_keywords = unique_preserve(
        [normalize_phrase(keyword) for keyword in signal.get("keywords", []) if normalize_phrase(keyword)]
    )
    normalized_content_angles = unique_preserve(
        [normalize_phrase(angle) for angle in signal.get("contentAngles", []) if normalize_phrase(angle)]
    )
    normalized_search_phrases = unique_preserve(
        [
            normalize_phrase(query)
            for query in [
                *signal.get("seedQueries", []),
                *signal.get("relatedQueries", []),
                *signal.get("contentGapQueries", []),
            ]
            if normalize_phrase(query)
        ]
    )
    normalized_topic_title = normalize_phrase(str(signal.get("topicTitle", "")))
    normalized_topic_summary = normalize_phrase(str(signal.get("topicSummary", "")))
    abstraction_terms = derive_abstraction_terms(
        str(signal.get("topicTitle", "")),
        normalized_keywords,
        normalized_search_phrases,
        normalized_content_angles,
    )
    fingerprint_seed = ".".join(
        filter(
            None,
            [
                str(signal.get("topicType", "")),
                str(signal.get("recommendedMode", "")),
                "_".join(abstraction_terms[:3]),
            ],
        )
    )
    search_signal_count = len(normalized_search_phrases)
    if search_signal_count >= 4:
        expansion_signal = "query_dense"
    elif len(normalized_content_angles) >= 3:
        expansion_signal = "angle_dense"
    elif len(normalized_keywords) >= 4:
        expansion_signal = "keyword_dense"
    else:
        expansion_signal = "narrow"
    return {
        "signalId": signal["signalId"],
        "topicFingerprint": signal["topicFingerprint"],
        "topicId": signal["topicId"],
        "topicType": signal["topicType"],
        "sourceType": signal["sourceType"],
        "recommendedMode": signal["recommendedMode"],
        "normalizedTopicTitle": normalized_topic_title,
        "normalizedTopicSummary": normalized_topic_summary,
        "normalizedKeywords": normalized_keywords,
        "normalizedContentAngles": normalized_content_angles,
        "normalizedSearchPhrases": normalized_search_phrases,
        "abstractionTerms": abstraction_terms,
        "fingerprintSeed": fingerprint_seed,
        "searchSignalCount": search_signal_count,
        "contentAngleCount": len(normalized_content_angles),
        "keywordCount": len(normalized_keywords),
        "expansionSignal": expansion_signal,
    }


def build_topic_abstraction(
    topic_fingerprint: str,
    items: list[dict[str, Any]],
    normalized_signals: list[dict[str, Any]],
    anchor: dict[str, Any],
    *,
    recommended_mode: str,
) -> dict[str, Any]:
    normalized_topic_keys = unique_preserve(
        [" ".join(signal["abstractionTerms"]) for signal in normalized_signals if signal["abstractionTerms"]]
    )
    normalized_keyword_pool = unique_preserve(
        [keyword for signal in normalized_signals for keyword in signal["normalizedKeywords"]]
    )
    normalized_search_phrase_pool = unique_preserve(
        [query for signal in normalized_signals for query in signal["normalizedSearchPhrases"]]
    )
    normalized_angle_pool = unique_preserve(
        [angle for signal in normalized_signals for angle in signal["normalizedContentAngles"]]
    )
    abstraction_terms = derive_abstraction_terms(
        str(anchor.get("topicTitle", "")),
        normalized_keyword_pool,
        normalized_search_phrase_pool,
        normalized_angle_pool,
    )
    fingerprint_seed = ".".join(
        filter(None, [str(anchor.get("topicType", "")), recommended_mode, "_".join(abstraction_terms[:3])])
    )
    source_types = unique_preserve([str(item.get("sourceType", "")) for item in items if item.get("sourceType")])
    if len(normalized_search_phrase_pool) >= 4:
        expansion_opportunity = "search_cluster"
    elif len(normalized_angle_pool) >= 3:
        expansion_opportunity = "angle_series"
    elif len(source_types) >= 2:
        expansion_opportunity = "cross_source"
    else:
        expansion_opportunity = "single_thread"
    return {
        "topicAbstractionId": f"abstraction.{topic_fingerprint}",
        "topicFingerprint": topic_fingerprint,
        "topicId": anchor["topicId"],
        "anchorSignalId": anchor["signalId"],
        "signalIds": [item["signalId"] for item in items],
        "normalizedTopicKey": normalized_topic_keys[0] if normalized_topic_keys else normalize_phrase(anchor["topicTitle"]),
        "fingerprintSeed": fingerprint_seed,
        "abstractionTerms": abstraction_terms,
        "normalizedKeywordPool": normalized_keyword_pool,
        "normalizedSearchPhrasePool": normalized_search_phrase_pool,
        "normalizedContentAnglePool": normalized_angle_pool,
        "canonicalTopicTitle": anchor["topicTitle"],
        "canonicalTopicSummary": anchor["topicSummary"],
        "titleSelectionSource": "normalized_anchor_signal",
        "summarySelectionSource": "normalized_anchor_signal",
        "candidateExpansionHints": {
            "expansionOpportunity": expansion_opportunity,
            "sourceTypeCount": len(source_types),
            "searchPhraseCount": len(normalized_search_phrase_pool),
            "contentAngleCount": len(normalized_angle_pool),
            "supportsSeriesPackaging": expansion_opportunity in {"search_cluster", "angle_series"},
        },
    }


def classify_search_coverage(query_count: int) -> str:
    if query_count >= 5:
        return "dense"
    if query_count >= 2:
        return "moderate"
    return "light"


def classify_complexity(value: float) -> str:
    if value <= 0.35:
        return "low"
    if value <= 0.6:
        return "medium"
    return "high"


def classify_packaging_risk(
    *,
    freshness_window: str,
    dependency_risk: str,
    complexity_label: str,
    source_type_count: int,
) -> str:
    if freshness_window == "daily" or dependency_risk == "high":
        return "freshness_sensitive"
    if dependency_risk == "medium" or complexity_label == "high":
        return "coordination_heavy"
    if source_type_count >= 2:
        return "cross_source"
    return "lightweight"


def classify_merge_cluster(
    *,
    signal_count: int,
    source_type_count: int,
    source_snapshot_count: int,
) -> str:
    if signal_count <= 1:
        return "single_signal"
    if source_snapshot_count >= 2 or source_type_count >= 2:
        return "cross_source_cluster"
    return "same_source_cluster"


def classify_dedupe_decision(
    *,
    signal_count: int,
    content_angle_count: int,
    search_intent_count: int,
) -> str:
    if signal_count <= 1:
        return "no_dedupe_required"
    if content_angle_count >= 2:
        return "keep_multi_angle_cluster"
    if search_intent_count >= 2:
        return "preserve_multi_intent_evidence"
    return "collapse_duplicate_signal_variants"


def build_packaged_search_evidence(
    *,
    seed_queries: list[str],
    related_queries: list[str],
    content_gap_queries: list[str],
    search_intent_type: str,
    search_persistence_hint: str,
    source_types: list[str],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    query_count = len(seed_queries) + len(related_queries) + len(content_gap_queries)
    supporting_signal_count = sum(
        1
        for item in items
        if item.get("seedQueries") or item.get("relatedQueries") or item.get("contentGapQueries")
    )
    return {
        "seedQueries": seed_queries,
        "relatedQueries": related_queries,
        "contentGapQueries": content_gap_queries,
        "searchIntentType": search_intent_type,
        "searchPersistenceHint": search_persistence_hint,
        "queryCount": query_count,
        "supportingSignalCount": supporting_signal_count,
        "supportingSourceTypes": source_types,
        "coverageLabel": classify_search_coverage(query_count),
    }


def build_packaged_execution_profile(
    *,
    recommended_formats: list[str],
    required_assets: list[str],
    required_capabilities: list[str],
    production_complexity: float,
    dependency_risk: str,
    fast_turnaround: bool,
    source_type_count: int,
    freshness_window: str,
) -> dict[str, Any]:
    complexity_label = classify_complexity(production_complexity)
    packaging_risk = classify_packaging_risk(
        freshness_window=freshness_window,
        dependency_risk=dependency_risk,
        complexity_label=complexity_label,
        source_type_count=source_type_count,
    )
    return {
        "recommendedFormats": recommended_formats,
        "requiredAssets": required_assets,
        "requiredCapabilities": required_capabilities,
        "productionComplexity": production_complexity,
        "dependencyRisk": dependency_risk,
        "fastTurnaround": fast_turnaround,
        "recommendedFormatCount": len(recommended_formats),
        "requiredAssetCount": len(required_assets),
        "requiredCapabilityCount": len(required_capabilities),
        "sourceTypeCount": source_type_count,
        "complexityLabel": complexity_label,
        "packagingRisk": packaging_risk,
    }


def build_execution_notes(
    *,
    raw_notes: list[str],
    search_coverage_label: str,
    execution_complexity_label: str,
    merge_classification: str,
    packaging_risk: str,
) -> str:
    summary_note = (
        "Packaging summary: "
        f"search coverage {search_coverage_label}; "
        f"complexity {execution_complexity_label}; "
        f"merge {merge_classification}; "
        f"risk {packaging_risk}."
    )
    notes = unique_preserve([note.strip() for note in raw_notes if note and note.strip()])
    return " ".join([*notes, summary_note]).strip()


def _validate_common_signal_fields(
    raw: dict[str, Any],
    prefix: str,
    *,
    snapshot_ref: str,
    snapshot_refs: set[str],
    errors: list[str],
    type_counter: Counter[str],
    fingerprint_to_topic: dict[str, str],
    seen_signal_ids: set[str],
) -> None:
    signal_id = str(raw["signalId"])
    if signal_id in seen_signal_ids:
        errors.append(f"{prefix}.signalId is duplicated: {signal_id}")
    else:
        seen_signal_ids.add(signal_id)

    if snapshot_ref not in snapshot_refs:
        errors.append(f"{prefix} source snapshot is not listed in top-level sourceSnapshots")

    topic_type = str(raw["topicType"])
    type_counter[topic_type] += 1
    if topic_type not in {"trend", "search", "evergreen"}:
        errors.append(f"{prefix}.topicType is invalid: {topic_type}")

    recommended_mode = str(raw["recommendedMode"])
    if recommended_mode not in {"growth", "search", "series"}:
        errors.append(f"{prefix}.recommendedMode is invalid: {recommended_mode}")

    freshness = str(raw["freshnessWindow"])
    if freshness not in {"daily", "weekly", "evergreen"}:
        errors.append(f"{prefix}.freshnessWindow is invalid: {freshness}")

    dependency_risk = str(raw["dependencyRisk"])
    if dependency_risk not in {"low", "medium", "high"}:
        errors.append(f"{prefix}.dependencyRisk is invalid: {dependency_risk}")

    signal_confidence = raw["signalConfidence"]
    if not isinstance(signal_confidence, (int, float)) or not 0 <= float(signal_confidence) <= 1:
        errors.append(f"{prefix}.signalConfidence must be between 0 and 1")

    expandability = raw["expandabilityHint"]
    if not isinstance(expandability, (int, float)) or not 0 <= float(expandability) <= 1:
        errors.append(f"{prefix}.expandabilityHint must be between 0 and 1")

    complexity = raw["productionComplexity"]
    if not isinstance(complexity, (int, float)) or not 0 <= float(complexity) <= 1:
        errors.append(f"{prefix}.productionComplexity must be between 0 and 1")

    if not isinstance(raw["fastTurnaround"], bool):
        errors.append(f"{prefix}.fastTurnaround must be boolean")

    for key in (
        "keywords",
        "contentAngles",
        "seedQueries",
        "relatedQueries",
        "contentGapQueries",
        "recommendedFormats",
        "requiredAssets",
        "requiredCapabilities",
    ):
        if not isinstance(raw[key], list):
            errors.append(f"{prefix}.{key} must be a list")

    fingerprint = str(raw["topicFingerprint"])
    topic_id = str(raw["topicId"])
    existing_topic_id = fingerprint_to_topic.get(fingerprint)
    if existing_topic_id is None:
        fingerprint_to_topic[fingerprint] = topic_id
    elif existing_topic_id != topic_id:
        errors.append(
            f"{prefix}.topicFingerprint maps to conflicting topicIds: {existing_topic_id} vs {topic_id}"
        )


def validate_raw_signal_fixture(payload: dict[str, Any]) -> tuple[list[str], Counter[str]]:
    errors: list[str] = []
    type_counter: Counter[str] = Counter()

    missing_top = sorted(RAW_SIGNAL_REQUIRED_TOP_LEVEL - set(payload.keys()))
    if missing_top:
        return ([f"fixture missing top-level fields: {', '.join(missing_top)}"], type_counter)

    schema_version = str(payload.get("schemaVersion"))
    if schema_version not in RAW_SIGNAL_SCHEMA_VERSIONS:
        errors.append(f"unexpected raw-signal schemaVersion: {schema_version}")

    signals = payload.get("signals")
    if not isinstance(signals, list) or not signals:
        return (["signals must be a non-empty list"], type_counter)

    raw_snapshot_refs = payload.get("sourceSnapshots", [])
    if not isinstance(raw_snapshot_refs, list):
        return (["sourceSnapshots must be a list"], type_counter)
    snapshot_refs = {str(item) for item in raw_snapshot_refs}
    seen_signal_ids: set[str] = set()
    fingerprint_to_topic: dict[str, str] = {}

    for index, raw in enumerate(signals):
        prefix = f"signals[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(RAW_SIGNAL_REQUIRED_FIELDS - set(raw.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        _validate_common_signal_fields(
            raw,
            prefix,
            snapshot_ref=str(raw["sourceSnapshotRef"]),
            snapshot_refs=snapshot_refs,
            errors=errors,
            type_counter=type_counter,
            fingerprint_to_topic=fingerprint_to_topic,
            seen_signal_ids=seen_signal_ids,
        )

    return errors, type_counter


def validate_snapshot_materialization(payload: dict[str, Any]) -> tuple[list[str], Counter[str]]:
    errors: list[str] = []
    type_counter: Counter[str] = Counter()

    missing_top = sorted(SNAPSHOT_MATERIALIZATION_REQUIRED_TOP_LEVEL - set(payload.keys()))
    if missing_top:
        return ([f"materialization missing top-level fields: {', '.join(missing_top)}"], type_counter)

    schema_version = str(payload.get("schemaVersion"))
    if schema_version not in SNAPSHOT_MATERIALIZATION_SCHEMA_VERSIONS:
        errors.append(f"unexpected snapshot-materialization schemaVersion: {schema_version}")

    source_snapshots = payload.get("sourceSnapshots")
    if not isinstance(source_snapshots, list) or not source_snapshots:
        return (["sourceSnapshots must be a non-empty list"], type_counter)
    signal_items = payload.get("signalItems")
    if not isinstance(signal_items, list) or not signal_items:
        return (["signalItems must be a non-empty list"], type_counter)
    video_samples = payload.get("videoSamples")
    if not isinstance(video_samples, list):
        return (["videoSamples must be a list"], type_counter)

    seen_snapshot_ids: set[str] = set()
    snapshot_refs: set[str] = set()
    for index, raw_snapshot in enumerate(source_snapshots):
        prefix = f"sourceSnapshots[{index}]"
        if not isinstance(raw_snapshot, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(SNAPSHOT_REQUIRED_FIELDS - set(raw_snapshot.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue
        snapshot_id = str(raw_snapshot["sourceSnapshotId"])
        if snapshot_id in seen_snapshot_ids:
            errors.append(f"{prefix}.sourceSnapshotId is duplicated: {snapshot_id}")
        else:
            seen_snapshot_ids.add(snapshot_id)
            snapshot_refs.add(snapshot_id)

    seen_video_sample_ids: set[str] = set()
    for index, raw_video in enumerate(video_samples):
        prefix = f"videoSamples[{index}]"
        if not isinstance(raw_video, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(VIDEO_SAMPLE_REQUIRED_FIELDS - set(raw_video.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue
        video_sample_id = str(raw_video["videoSampleId"])
        if video_sample_id in seen_video_sample_ids:
            errors.append(f"{prefix}.videoSampleId is duplicated: {video_sample_id}")
        else:
            seen_video_sample_ids.add(video_sample_id)
        source_snapshot_id = str(raw_video["sourceSnapshotId"])
        if source_snapshot_id not in snapshot_refs:
            errors.append(f"{prefix}.sourceSnapshotId is not listed in sourceSnapshots")
        if not isinstance(raw_video["hashtags"], list):
            errors.append(f"{prefix}.hashtags must be a list")
        if not isinstance(raw_video["metrics"], dict):
            errors.append(f"{prefix}.metrics must be an object")

    seen_signal_ids: set[str] = set()
    fingerprint_to_topic: dict[str, str] = {}
    for index, raw_signal in enumerate(signal_items):
        prefix = f"signalItems[{index}]"
        if not isinstance(raw_signal, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(SNAPSHOT_SIGNAL_REQUIRED_FIELDS - set(raw_signal.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        _validate_common_signal_fields(
            raw_signal,
            prefix,
            snapshot_ref=str(raw_signal["sourceSnapshotId"]),
            snapshot_refs=snapshot_refs,
            errors=errors,
            type_counter=type_counter,
            fingerprint_to_topic=fingerprint_to_topic,
            seen_signal_ids=seen_signal_ids,
        )

        video_sample_id = raw_signal.get("videoSampleId")
        if video_sample_id is not None and str(video_sample_id) not in seen_video_sample_ids:
            errors.append(f"{prefix}.videoSampleId is not listed in top-level videoSamples")

    return errors, type_counter


def validate_source_snapshots_fixture(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing_top = sorted(SOURCE_SNAPSHOTS_REQUIRED_TOP_LEVEL - set(payload.keys()))
    if missing_top:
        return [f"source-snapshots missing top-level fields: {', '.join(missing_top)}"]

    schema_version = str(payload.get("schemaVersion"))
    if schema_version not in SOURCE_SNAPSHOTS_SCHEMA_VERSIONS:
        errors.append(f"unexpected source-snapshots schemaVersion: {schema_version}")

    source_snapshots = payload.get("sourceSnapshots")
    if not isinstance(source_snapshots, list) or not source_snapshots:
        return ["sourceSnapshots must be a non-empty list"]

    seen_snapshot_ids: set[str] = set()
    for index, raw_snapshot in enumerate(source_snapshots):
        prefix = f"sourceSnapshots[{index}]"
        if not isinstance(raw_snapshot, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(SNAPSHOT_REQUIRED_FIELDS - set(raw_snapshot.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue
        snapshot_id = str(raw_snapshot["sourceSnapshotId"])
        if snapshot_id in seen_snapshot_ids:
            errors.append(f"{prefix}.sourceSnapshotId is duplicated: {snapshot_id}")
        else:
            seen_snapshot_ids.add(snapshot_id)

    return errors


def validate_signal_items_fixture(payload: dict[str, Any], snapshot_refs: set[str] | None = None) -> tuple[list[str], Counter[str]]:
    errors: list[str] = []
    type_counter: Counter[str] = Counter()

    missing_top = sorted(SIGNAL_ITEMS_REQUIRED_TOP_LEVEL - set(payload.keys()))
    if missing_top:
        return ([f"signal-items missing top-level fields: {', '.join(missing_top)}"], type_counter)

    schema_version = str(payload.get("schemaVersion"))
    if schema_version not in SIGNAL_ITEMS_SCHEMA_VERSIONS:
        errors.append(f"unexpected signal-items schemaVersion: {schema_version}")

    signal_items = payload.get("signalItems")
    if not isinstance(signal_items, list) or not signal_items:
        return (["signalItems must be a non-empty list"], type_counter)

    seen_signal_ids: set[str] = set()
    fingerprint_to_topic: dict[str, str] = {}
    resolved_snapshot_refs = snapshot_refs or {
        str(item.get("sourceSnapshotId"))
        for item in signal_items
        if isinstance(item, dict) and item.get("sourceSnapshotId")
    }

    for index, raw_signal in enumerate(signal_items):
        prefix = f"signalItems[{index}]"
        if not isinstance(raw_signal, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(SNAPSHOT_SIGNAL_REQUIRED_FIELDS - set(raw_signal.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        _validate_common_signal_fields(
            raw_signal,
            prefix,
            snapshot_ref=str(raw_signal["sourceSnapshotId"]),
            snapshot_refs=resolved_snapshot_refs,
            errors=errors,
            type_counter=type_counter,
            fingerprint_to_topic=fingerprint_to_topic,
            seen_signal_ids=seen_signal_ids,
        )

    return errors, type_counter


def validate_video_samples_fixture(payload: dict[str, Any], snapshot_refs: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    missing_top = sorted(VIDEO_SAMPLES_REQUIRED_TOP_LEVEL - set(payload.keys()))
    if missing_top:
        return [f"video-samples missing top-level fields: {', '.join(missing_top)}"]

    schema_version = str(payload.get("schemaVersion"))
    if schema_version not in VIDEO_SAMPLES_SCHEMA_VERSIONS:
        errors.append(f"unexpected video-samples schemaVersion: {schema_version}")

    video_samples = payload.get("videoSamples")
    if not isinstance(video_samples, list):
        return ["videoSamples must be a list"]

    resolved_snapshot_refs = snapshot_refs or set()
    seen_video_sample_ids: set[str] = set()
    for index, raw_video in enumerate(video_samples):
        prefix = f"videoSamples[{index}]"
        if not isinstance(raw_video, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(VIDEO_SAMPLE_REQUIRED_FIELDS - set(raw_video.keys()))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue
        video_sample_id = str(raw_video["videoSampleId"])
        if video_sample_id in seen_video_sample_ids:
            errors.append(f"{prefix}.videoSampleId is duplicated: {video_sample_id}")
        else:
            seen_video_sample_ids.add(video_sample_id)
        source_snapshot_id = str(raw_video["sourceSnapshotId"])
        if resolved_snapshot_refs and source_snapshot_id not in resolved_snapshot_refs:
            errors.append(f"{prefix}.sourceSnapshotId is not listed in sourceSnapshots")
        if not isinstance(raw_video["hashtags"], list):
            errors.append(f"{prefix}.hashtags must be a list")
        if not isinstance(raw_video["metrics"], dict):
            errors.append(f"{prefix}.metrics must be an object")

    return errors


def build_snapshot_materialization(
    source_snapshots_payload: dict[str, Any],
    signal_items_payload: dict[str, Any],
    video_samples_payload: dict[str, Any],
    *,
    materialization_id: str | None = None,
    schema_version: str = "discovery-snapshot-materialization.v1",
) -> dict[str, Any]:
    source_snapshot_errors = validate_source_snapshots_fixture(source_snapshots_payload)
    snapshot_refs = {
        str(item["sourceSnapshotId"])
        for item in source_snapshots_payload.get("sourceSnapshots", [])
        if isinstance(item, dict) and "sourceSnapshotId" in item
    }
    signal_item_errors, _ = validate_signal_items_fixture(signal_items_payload, snapshot_refs=snapshot_refs)
    video_sample_errors = validate_video_samples_fixture(
        video_samples_payload,
        snapshot_refs=snapshot_refs,
    )
    errors = source_snapshot_errors + signal_item_errors + video_sample_errors
    if errors:
        raise ValueError("; ".join(errors))

    summary_fields = {
        "snapshotId": (
            source_snapshots_payload.get("snapshotId"),
            signal_items_payload.get("snapshotId"),
            video_samples_payload.get("snapshotId"),
        ),
        "market": (
            source_snapshots_payload.get("market"),
            signal_items_payload.get("market"),
            video_samples_payload.get("market"),
        ),
        "language": (
            source_snapshots_payload.get("language"),
            signal_items_payload.get("language"),
            video_samples_payload.get("language"),
        ),
    }
    for field, values in summary_fields.items():
        first_value = values[0]
        for value in values[1:]:
            if value != first_value:
                raise ValueError(f"{field} is inconsistent across snapshot inputs")

    captured_at_values = [
        str(source_snapshots_payload.get("capturedAt")),
        str(signal_items_payload.get("capturedAt")),
        str(video_samples_payload.get("capturedAt")),
    ]

    return {
        "schemaVersion": schema_version,
        "materializationId": materialization_id
        or f"discovery-materialization.{source_snapshots_payload['snapshotId']}",
        "snapshotId": source_snapshots_payload["snapshotId"],
        "market": source_snapshots_payload["market"],
        "language": source_snapshots_payload["language"],
        "capturedAt": min(captured_at_values),
        "sourceSnapshots": source_snapshots_payload["sourceSnapshots"],
        "signalItems": signal_items_payload["signalItems"],
        "videoSamples": video_samples_payload["videoSamples"],
        "generatedFrom": {
            "materializationSource": "separate_snapshot_artifacts",
            "sourceSnapshotSchemaVersion": source_snapshots_payload["schemaVersion"],
            "signalItemsSchemaVersion": signal_items_payload["schemaVersion"],
            "videoSamplesSchemaVersion": video_samples_payload["schemaVersion"],
        },
    }


def materialize_signal_fixture(payload: dict[str, Any]) -> dict[str, Any]:
    schema_version = str(payload.get("schemaVersion", ""))

    if schema_version in RAW_SIGNAL_SCHEMA_VERSIONS:
        errors, _ = validate_raw_signal_fixture(payload)
        if errors:
            raise ValueError("; ".join(errors))
        normalized = dict(payload)
        normalized.setdefault("inputKind", "raw_signal_fixture")
        normalized.setdefault("videoSampleCount", 0)
        return normalized

    if schema_version in SNAPSHOT_MATERIALIZATION_SCHEMA_VERSIONS:
        errors, _ = validate_snapshot_materialization(payload)
        if errors:
            raise ValueError("; ".join(errors))

        source_snapshot_refs = [
            str(snapshot["sourceSnapshotId"]) for snapshot in payload.get("sourceSnapshots", [])
        ]
        signal_items = []
        for raw_signal in payload.get("signalItems", []):
            signal_payload = {
                "signalId": raw_signal["signalId"],
                "capturedAt": raw_signal["capturedAt"],
                "sourceSnapshotRef": raw_signal["sourceSnapshotId"],
                "signalConfidence": raw_signal["signalConfidence"],
                "topicId": raw_signal["topicId"],
                "topicFingerprint": raw_signal["topicFingerprint"],
                "topicTitle": raw_signal["topicTitle"],
                "topicSummary": raw_signal["topicSummary"],
                "topicType": raw_signal["topicType"],
                "sourceType": raw_signal["sourceType"],
                "keywords": raw_signal["keywords"],
                "contentAngles": raw_signal["contentAngles"],
                "seedQueries": raw_signal["seedQueries"],
                "relatedQueries": raw_signal["relatedQueries"],
                "contentGapQueries": raw_signal["contentGapQueries"],
                "searchIntentType": raw_signal["searchIntentType"],
                "searchPersistenceHint": raw_signal["searchPersistenceHint"],
                "recommendedMode": raw_signal["recommendedMode"],
                "freshnessWindow": raw_signal["freshnessWindow"],
                "expandabilityHint": raw_signal["expandabilityHint"],
                "recommendedFormats": raw_signal["recommendedFormats"],
                "requiredAssets": raw_signal["requiredAssets"],
                "requiredCapabilities": raw_signal["requiredCapabilities"],
                "productionComplexity": raw_signal["productionComplexity"],
                "dependencyRisk": raw_signal["dependencyRisk"],
                "fastTurnaround": raw_signal["fastTurnaround"],
                "executionNotes": raw_signal["executionNotes"],
            }
            if "videoSampleId" in raw_signal:
                signal_payload["videoSampleId"] = raw_signal["videoSampleId"]
            signal_items.append(signal_payload)

        return {
            "schemaVersion": "raw-signals.v1",
            "snapshotId": payload["snapshotId"],
            "market": payload["market"],
            "language": payload["language"],
            "capturedAt": payload["capturedAt"],
            "sourceSnapshots": source_snapshot_refs,
            "signals": signal_items,
            "inputKind": "snapshot_materialization",
            "inputSchemaVersion": schema_version,
            "materializationId": payload["materializationId"],
            "videoSampleCount": len(payload.get("videoSamples", [])),
            "materializationSource": payload.get("generatedFrom", {}).get(
                "materializationSource",
                "prebuilt_materialization",
            ),
            "sourceSnapshotSchemaVersion": payload.get("generatedFrom", {}).get(
                "sourceSnapshotSchemaVersion"
            ),
            "signalItemsSchemaVersion": payload.get("generatedFrom", {}).get(
                "signalItemsSchemaVersion"
            ),
            "videoSamplesSchemaVersion": payload.get("generatedFrom", {}).get(
                "videoSamplesSchemaVersion"
            ),
        }

    raise ValueError(f"unsupported discovery input schemaVersion: {schema_version}")


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("schemaVersion") != "discovery-policy.v1":
        errors.append("discovery policy has unexpected schemaVersion")
    for key in (
        "bundleIdPrefix",
        "mergeGroupIdPrefix",
        "mergeReasonTemplate",
        "sourceTypePriority",
        "freshnessPriority",
        "searchPersistencePriority",
        "dependencyRiskPriority",
    ):
        if key not in policy:
            errors.append(f"discovery policy missing `{key}`")
    return errors


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("discovery policy must be an object")
    errors = validate_policy(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def _priority_map(values: list[str]) -> dict[str, int]:
    return {value: index for index, value in enumerate(values)}


def _rank_value(value: str, priorities: dict[str, int]) -> int:
    return priorities.get(value, len(priorities) + 100)


def choose_anchor(items: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    source_priority = _priority_map(policy["sourceTypePriority"])
    freshness_priority = _priority_map(policy["freshnessPriority"])
    persistence_priority = _priority_map(policy["searchPersistencePriority"])

    def score(item: dict[str, Any]) -> tuple[Any, ...]:
        search_signal_count = len(item.get("seedQueries", [])) + len(item.get("relatedQueries", [])) + len(
            item.get("contentGapQueries", [])
        )
        return (
            _rank_value(str(item.get("sourceType", "")), source_priority),
            _rank_value(str(item.get("freshnessWindow", "")), freshness_priority),
            _rank_value(str(item.get("searchPersistenceHint", "")), persistence_priority),
            -search_signal_count,
            -float(item.get("expandabilityHint", 0.0)),
            float(item.get("productionComplexity", 1.0)),
            str(item.get("signalId", "")),
        )

    return min(items, key=score)


def choose_preferred_value(items: list[dict[str, Any]], field: str, priority_order: list[str]) -> str:
    priority_map = _priority_map(priority_order)
    values = [str(item.get(field, "")) for item in items if item.get(field)]
    if not values:
        return ""
    counts = Counter(values)
    return min(
        counts.keys(),
        key=lambda value: (
            _rank_value(value, priority_map),
            -counts[value],
            value,
        ),
    )


def merge_scalar_mode(items: list[dict[str, Any]], field: str, fallback: Any = "") -> Any:
    values = [item.get(field) for item in items if item.get(field) is not None]
    if not values:
        return fallback
    counts = Counter(values)
    return max(counts.keys(), key=lambda value: (counts[value], str(value)))


def build_payload(signal_fixture: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    materialized_fixture = materialize_signal_fixture(signal_fixture)
    signals = materialized_fixture.get("signals")
    if not isinstance(signals, list) or not signals:
        raise ValueError("signal fixture must contain a non-empty `signals` list")

    bundles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in signals:
        if not isinstance(item, dict):
            raise ValueError("every signal must be an object")
        fingerprint = item.get("topicFingerprint")
        if not isinstance(fingerprint, str) or not fingerprint:
            raise ValueError("every signal must provide a non-empty `topicFingerprint`")
        bundles[fingerprint].append(item)

    normalized_signal_map = {
        str(item["signalId"]): build_signal_normalization(item)
        for item in signals
        if isinstance(item, dict)
    }

    normalized_signals: list[dict[str, Any]] = []
    topic_abstractions: list[dict[str, Any]] = []
    evidence_bundles: list[dict[str, Any]] = []
    merge_groups: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for fingerprint, items in sorted(bundles.items()):
        anchor = choose_anchor(items, policy)
        normalized_bundle_signals = [normalized_signal_map[str(item["signalId"])] for item in items]
        normalized_signals.extend(normalized_bundle_signals)
        source_refs = unique_preserve([str(item["signalId"]) for item in items])
        source_types = unique_preserve([str(item["sourceType"]) for item in items])
        source_snapshot_refs = unique_preserve(
            [str(item.get("sourceSnapshotRef", "")) for item in items if item.get("sourceSnapshotRef")]
        )
        video_sample_ids = unique_preserve(
            [str(item.get("videoSampleId", "")) for item in items if item.get("videoSampleId")]
        )
        keywords = unique_preserve(
            [keyword for item in items for keyword in item.get("keywords", [])],
            cap=int(policy["keywordCap"]),
        )
        content_angles = unique_preserve(
            [angle for item in items for angle in item.get("contentAngles", [])],
            cap=int(policy["contentAngleCap"]),
        )
        seed_queries = unique_preserve(
            [query for item in items for query in item.get("seedQueries", [])],
            cap=int(policy["searchQueryCap"]),
        )
        related_queries = unique_preserve(
            [query for item in items for query in item.get("relatedQueries", [])],
            cap=int(policy["searchQueryCap"]),
        )
        content_gap_queries = unique_preserve(
            [query for item in items for query in item.get("contentGapQueries", [])],
            cap=int(policy["searchQueryCap"]),
        )
        recommended_formats = unique_preserve(
            [fmt for item in items for fmt in item.get("recommendedFormats", [])],
            cap=int(policy["recommendedFormatCap"]),
        )
        required_assets = unique_preserve(
            [asset for item in items for asset in item.get("requiredAssets", [])],
            cap=int(policy["requiredAssetCap"]),
        )
        required_capabilities = unique_preserve(
            [cap for item in items for cap in item.get("requiredCapabilities", [])],
            cap=int(policy["requiredCapabilityCap"]),
        )

        bundle_id_prefix = str(policy["bundleIdPrefix"])
        merge_id_prefix = str(policy["mergeGroupIdPrefix"])
        search_query_count = len(seed_queries) + len(related_queries) + len(content_gap_queries)
        search_intent_types = unique_preserve(
            [str(item.get("searchIntentType", "")) for item in items if item.get("searchIntentType")]
        )
        search_persistence_hints = unique_preserve(
            [str(item.get("searchPersistenceHint", "")) for item in items if item.get("searchPersistenceHint")]
        )
        freshness_windows = unique_preserve(
            [str(item.get("freshnessWindow", "")) for item in items if item.get("freshnessWindow")]
        )
        recommended_modes = unique_preserve(
            [str(item.get("recommendedMode", "")) for item in items if item.get("recommendedMode")]
        )
        dependency_risks = unique_preserve(
            [str(item.get("dependencyRisk", "")) for item in items if item.get("dependencyRisk")]
        )
        recommended_mode = merge_scalar_mode(
            items, "recommendedMode", fallback=anchor["recommendedMode"]
        )
        freshness_window = (
            choose_preferred_value(items, "freshnessWindow", policy["freshnessPriority"])
            or anchor["freshnessWindow"]
        )
        search_persistence_hint = (
            choose_preferred_value(
                items, "searchPersistenceHint", policy["searchPersistencePriority"]
            )
            or anchor["searchPersistenceHint"]
        )
        dependency_risk = (
            choose_preferred_value(
                items, "dependencyRisk", policy["dependencyRiskPriority"]
            )
            or anchor["dependencyRisk"]
        )
        production_complexity = round_with_precision(
            average([float(item.get("productionComplexity", 0.0)) for item in items]),
            int(policy["productionComplexityPrecision"]),
        )
        search_evidence = build_packaged_search_evidence(
            seed_queries=seed_queries,
            related_queries=related_queries,
            content_gap_queries=content_gap_queries,
            search_intent_type=merge_scalar_mode(
                items, "searchIntentType", fallback=anchor["searchIntentType"]
            ),
            search_persistence_hint=search_persistence_hint,
            source_types=source_types,
            items=items,
        )
        execution_profile = build_packaged_execution_profile(
            recommended_formats=recommended_formats,
            required_assets=required_assets,
            required_capabilities=required_capabilities,
            production_complexity=production_complexity,
            dependency_risk=dependency_risk,
            fast_turnaround=any(bool(item.get("fastTurnaround")) for item in items),
            source_type_count=len(source_types),
            freshness_window=freshness_window,
        )
        merge_classification = classify_merge_cluster(
            signal_count=len(source_refs),
            source_type_count=len(source_types),
            source_snapshot_count=len(source_snapshot_refs),
        )
        dedupe_decision = classify_dedupe_decision(
            signal_count=len(source_refs),
            content_angle_count=len(content_angles),
            search_intent_count=len(search_intent_types),
        )
        topic_abstraction = build_topic_abstraction(
            fingerprint,
            items,
            normalized_bundle_signals,
            anchor,
            recommended_mode=str(recommended_mode),
        )
        topic_abstractions.append(topic_abstraction)

        evidence_bundles.append(
            {
                "bundleId": f"{bundle_id_prefix}.{fingerprint}",
                "topicFingerprint": fingerprint,
                "topicAbstractionId": topic_abstraction["topicAbstractionId"],
                "anchorSignalId": anchor["signalId"],
                "signalIds": source_refs,
                "sourceSnapshotRefs": source_snapshot_refs,
                "videoSampleIds": video_sample_ids,
                "sourceTypes": source_types,
                "searchIntentTypes": search_intent_types,
                "searchPersistenceHints": search_persistence_hints,
                "normalizedTopicKey": topic_abstraction["normalizedTopicKey"],
                "mergeClassification": merge_classification,
                "searchEvidenceSummary": {
                    "queryCount": search_evidence["queryCount"],
                    "seedQueryCount": len(seed_queries),
                    "relatedQueryCount": len(related_queries),
                    "contentGapQueryCount": len(content_gap_queries),
                    "supportingSignalCount": search_evidence["supportingSignalCount"],
                    "coverageLabel": search_evidence["coverageLabel"],
                },
                "executionEvidenceSummary": {
                    "recommendedFormatCount": execution_profile["recommendedFormatCount"],
                    "requiredAssetCount": execution_profile["requiredAssetCount"],
                    "requiredCapabilityCount": execution_profile["requiredCapabilityCount"],
                    "complexityLabel": execution_profile["complexityLabel"],
                    "packagingRisk": execution_profile["packagingRisk"],
                    "fastTurnaroundCompatible": execution_profile["fastTurnaround"],
                },
                "sourceCount": len(source_refs),
                "searchQueryCount": search_query_count,
                "contentAngleCount": len(content_angles),
                "requiredFormatCount": len(recommended_formats),
            }
        )

        merge_groups.append(
            {
                "mergeGroupId": f"{merge_id_prefix}.{fingerprint}",
                "topicFingerprint": fingerprint,
                "topicId": anchor["topicId"],
                "topicAbstractionId": topic_abstraction["topicAbstractionId"],
                "anchorSignalId": anchor["signalId"],
                "mergedSignalIds": source_refs,
                "mergedSignalCount": len(source_refs),
                "normalizedTopicKey": topic_abstraction["normalizedTopicKey"],
                "fingerprintSeed": topic_abstraction["fingerprintSeed"],
                "mergeClassification": merge_classification,
                "dedupeDecision": dedupe_decision,
                "mergeGuardrails": {
                    "sourceTypes": source_types,
                    "sourceSnapshotCount": len(source_snapshot_refs),
                    "freshnessWindows": freshness_windows,
                    "recommendedModes": recommended_modes,
                    "searchIntentTypes": search_intent_types,
                    "dependencyRisks": dependency_risks,
                },
                "packagingReadiness": {
                    "searchCoverageLabel": search_evidence["coverageLabel"],
                    "executionComplexityLabel": execution_profile["complexityLabel"],
                    "packagingRisk": execution_profile["packagingRisk"],
                    "supportsSeriesPackaging": topic_abstraction["candidateExpansionHints"][
                        "supportsSeriesPackaging"
                    ],
                    "hasVideoEvidence": bool(video_sample_ids),
                },
                "mergeReason": str(policy["mergeReasonTemplate"]),
            }
        )

        candidates.append(
            {
                "schemaVersion": "topic-candidate.v1",
                "topicId": anchor["topicId"],
                "topicFingerprint": fingerprint,
                "topicTitle": topic_abstraction["canonicalTopicTitle"],
                "topicSummary": topic_abstraction["canonicalTopicSummary"],
                "topicType": merge_scalar_mode(items, "topicType", fallback=anchor["topicType"]),
                "sourceType": source_types,
                "sourceRef": source_refs,
                "keywords": keywords,
                "contentAngle": content_angles,
                "recommendedMode": recommended_mode,
                "expandability": round_with_precision(
                    average([float(item.get("expandabilityHint", 0.0)) for item in items]),
                    int(policy["expandabilityPrecision"]),
                ),
                "freshnessWindow": freshness_window,
                "searchEvidence": search_evidence,
                "executionProfile": execution_profile,
                "topicAbstractionId": topic_abstraction["topicAbstractionId"],
                "normalizedTopicKey": topic_abstraction["normalizedTopicKey"],
                "fingerprintSeed": topic_abstraction["fingerprintSeed"],
                "candidateExpansionHints": topic_abstraction["candidateExpansionHints"],
                "mergeClassification": merge_classification,
                "dedupeDecision": dedupe_decision,
                "executionNotes": build_execution_notes(
                    raw_notes=[item.get("executionNotes", "") for item in items],
                    search_coverage_label=search_evidence["coverageLabel"],
                    execution_complexity_label=execution_profile["complexityLabel"],
                    merge_classification=merge_classification,
                    packaging_risk=execution_profile["packagingRisk"],
                ),
            }
        )

    return {
        "schemaVersion": "discovery-dry-run.v1",
        "policyVersion": policy["schemaVersion"],
        "snapshotId": materialized_fixture.get("snapshotId", "snap.discovery.fixture"),
        "generatedFrom": {
            "inputKind": materialized_fixture.get("inputKind", "raw_signal_fixture"),
            "inputSchemaVersion": signal_fixture.get("schemaVersion"),
            "materializedSchemaVersion": materialized_fixture.get("schemaVersion"),
            "materializationId": materialized_fixture.get("materializationId"),
            "materializationSource": materialized_fixture.get("materializationSource"),
            "normalizationRuleVersion": NORMALIZATION_RULE_VERSION,
            "sourceSnapshotSchemaVersion": materialized_fixture.get("sourceSnapshotSchemaVersion"),
            "signalItemsSchemaVersion": materialized_fixture.get("signalItemsSchemaVersion"),
            "videoSamplesSchemaVersion": materialized_fixture.get("videoSamplesSchemaVersion"),
            "sourceSnapshotCount": len(materialized_fixture.get("sourceSnapshots", [])),
            "signalCount": len(signals),
            "videoSampleCount": int(materialized_fixture.get("videoSampleCount", 0)),
            "normalizedSignalCount": len(normalized_signals),
            "topicAbstractionCount": len(topic_abstractions),
        },
        "normalizedSignals": normalized_signals,
        "topicAbstractions": topic_abstractions,
        "evidenceBundles": evidence_bundles,
        "mergeGroups": merge_groups,
        "candidates": candidates,
    }
