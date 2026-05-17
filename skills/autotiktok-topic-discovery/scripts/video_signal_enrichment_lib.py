#!/usr/bin/env python3
"""
Helpers for enriching metadata-only signalItems with videoContentAnalysis sidecars.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CANONICAL_SCHEMA_VERSION = "discovery-signal-items.v1"
SAMPLE_SCHEMA_VERSION = "discovery-signal-items.sample.v1"
STATUS_ANALYSIS_SUCCEEDED = "analysis_succeeded"
STATUS_DOWNLOAD_MISSING = "download_missing"
STATUS_ANALYSIS_FAILED = "analysis_failed"


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"


def _as_text(value: Any) -> str:
    return str(value or "").strip()


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _unique_texts(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _as_text(value)
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def _index_analyses(video_content_analysis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    analyses = video_content_analysis.get("analyses")
    if not isinstance(analyses, list):
        raise ValueError("videoContentAnalysis must contain analyses list")
    indexed: dict[str, dict[str, Any]] = {}
    for index, analysis in enumerate(analyses):
        if not isinstance(analysis, dict):
            raise ValueError(f"analyses[{index}] must be an object")
        video_sample_id = _as_text(analysis.get("videoSampleId"))
        if not video_sample_id:
            raise ValueError(f"analyses[{index}] is missing videoSampleId")
        indexed[video_sample_id] = analysis
    return indexed


def _analysis_reference(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "analysisId": analysis.get("analysisId"),
        "videoSampleId": analysis.get("videoSampleId"),
        "platformVideoId": analysis.get("platformVideoId"),
        "sourceSnapshotId": analysis.get("sourceSnapshotId"),
        "status": analysis.get("status"),
        "provider": analysis.get("provider"),
        "model": analysis.get("model"),
        "analysisConfidence": analysis.get("analysisConfidence"),
    }


def _with_reference(
    signal_item: dict[str, Any],
    analysis: dict[str, Any],
    *,
    enrichment_lane: str,
) -> dict[str, Any]:
    raw_meta = signal_item.get("rawMeta") if isinstance(signal_item.get("rawMeta"), dict) else {}
    return {
        **signal_item,
        "rawMeta": {
            **raw_meta,
            "enrichmentLane": enrichment_lane,
            "videoContentAnalysisReference": _analysis_reference(analysis),
        },
    }


def _append_note(signal_item: dict[str, Any], note: str) -> str:
    current = _as_text(signal_item.get("executionNotes"))
    if not current:
        return note
    return f"{current} {note}"


def _float_value(value: Any, fallback: float = 0.0) -> float:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        return float(value)
    return fallback


def _enrich_success(signal_item: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    enriched = _with_reference(
        signal_item,
        analysis,
        enrichment_lane="video_content_analysis",
    )
    summary = _as_text(analysis.get("contentSummary"))
    visual_evidence = [
        f"video proof: {item}" for item in _as_list(analysis.get("visualEvidence"))[:2]
    ]
    replication_hints = _as_list(analysis.get("replicationHints"))[:2]
    model_ref = f"{analysis.get('provider')}/{analysis.get('model')}"
    current_expandability = _float_value(signal_item.get("expandabilityHint"), fallback=0.0)
    enriched["topicSummary"] = (
        f"{signal_item['topicSummary']} MP4 analysis adds: {summary}"
        if summary
        else signal_item["topicSummary"]
    )
    enriched["contentAngles"] = _unique_texts(
        [*_as_list(signal_item.get("contentAngles")), *visual_evidence]
    )
    enriched["requiredAssets"] = _unique_texts(
        [
            *_as_list(signal_item.get("requiredAssets")),
            "local MP4 reference",
            "video understanding sidecar",
        ]
    )
    enriched["recommendedFormats"] = _unique_texts(
        [
            *_as_list(signal_item.get("recommendedFormats")),
            "reference_video_breakdown",
        ]
    )
    enriched["requiredCapabilities"] = _unique_texts(
        [
            *_as_list(signal_item.get("requiredCapabilities")),
            "video content interpretation",
        ]
    )
    enriched["expandabilityHint"] = round(min(0.94, current_expandability + 0.08), 2)
    enriched["executionNotes"] = _append_note(
        signal_item,
        f"Enriched with videoContentAnalysis {analysis.get('analysisId')} from {model_ref}.",
    )
    enriched["rawMeta"]["videoContentEvidence"] = {
        "contentSummary": summary,
        "visualEvidence": _as_list(analysis.get("visualEvidence"))[:3],
        "replicationHints": replication_hints,
    }
    return enriched


def _enrich_fallback(signal_item: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    enriched = _with_reference(
        signal_item,
        analysis,
        enrichment_lane="metadata_only_fallback",
    )
    error_codes = [
        _as_text(error.get("code"))
        for error in _as_list(analysis.get("errors"))
        if isinstance(error, dict)
    ]
    enriched["executionNotes"] = _append_note(
        signal_item,
        f"MP4 analysis status {analysis.get('status')}; metadata-only fallback preserved.",
    )
    enriched["rawMeta"]["videoContentFallback"] = {
        "status": analysis.get("status"),
        "errorCodes": [code for code in error_codes if code],
    }
    return enriched


def build_enriched_signal_items(
    signal_items_payload: dict[str, Any],
    video_content_analysis: dict[str, Any],
    *,
    schema_version: str = CANONICAL_SCHEMA_VERSION,
) -> dict[str, Any]:
    signal_items = signal_items_payload.get("signalItems")
    if not isinstance(signal_items, list) or not signal_items:
        raise ValueError("signalItems input must contain a non-empty signalItems list")
    analyses_by_video_sample_id = _index_analyses(video_content_analysis)

    enriched_items: list[dict[str, Any]] = []
    enriched_count = 0
    fallback_count = 0
    unmatched_count = 0
    for index, signal_item in enumerate(signal_items):
        if not isinstance(signal_item, dict):
            raise ValueError(f"signalItems[{index}] must be an object")
        video_sample_id = _as_text(signal_item.get("videoSampleId"))
        analysis = analyses_by_video_sample_id.get(video_sample_id)
        if analysis is None:
            unmatched_count += 1
            enriched_items.append(dict(signal_item))
            continue
        if analysis.get("status") == STATUS_ANALYSIS_SUCCEEDED:
            enriched_items.append(_enrich_success(signal_item, analysis))
            enriched_count += 1
        elif analysis.get("status") in {STATUS_DOWNLOAD_MISSING, STATUS_ANALYSIS_FAILED}:
            enriched_items.append(_enrich_fallback(signal_item, analysis))
            fallback_count += 1
        else:
            raise ValueError(f"unsupported videoContentAnalysis status: {analysis.get('status')}")

    return {
        "schemaVersion": schema_version,
        "snapshotId": signal_items_payload.get("snapshotId"),
        "market": signal_items_payload.get("market"),
        "language": signal_items_payload.get("language"),
        "capturedAt": signal_items_payload.get("capturedAt"),
        "signalItems": enriched_items,
        "generatedFrom": {
            "sourceSkill": "autotiktok-topic-discovery",
            "derivationMode": "video_content_analysis_enriched_signal_items",
            "inputSignalItemsSchemaVersion": signal_items_payload.get("schemaVersion"),
            "videoContentAnalysisSchemaVersion": video_content_analysis.get("schemaVersion"),
            "videoContentAnalysisSnapshotId": video_content_analysis.get("snapshotId"),
            "fallbackPolicy": "preserve_metadata_only_signal_item",
        },
        "summary": {
            "requested": len(signal_items),
            "enriched": enriched_count,
            "metadataOnlyFallback": fallback_count,
            "metadataOnlyUnmatched": unmatched_count,
        },
    }
