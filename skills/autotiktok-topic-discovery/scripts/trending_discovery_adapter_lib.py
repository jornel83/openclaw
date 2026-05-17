#!/usr/bin/env python3
"""
Helpers for recognizing AutoTikTok trending outputs before discovery ingestion.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


VIDEO_SAMPLE_ARTIFACT_KEYS = (
    "absolute_hot_video_samples",
    "fresh_hot_video_samples",
)
SUPPORTED_VIEW_FILTERS = ("all", "both", "absolute_hot", "fresh_hot")
CANONICAL_VIDEO_SAMPLE_REQUIRED_FIELDS = {
    "videoSampleId",
    "sourceSnapshotId",
    "publishedAt",
    "title",
    "desc",
    "hashtags",
    "authorId",
    "metrics",
}
RAW_RANKED_VIDEO_ROW_REQUIRED_FIELDS = {
    "video_id",
    "create_time",
    "description",
    "author_id",
    "view_count",
    "like_count",
    "share_count",
}
RAW_RANKED_VIDEO_ROW_OPTIONAL_FIELDS = {
    "hashtags",
    "comment_count",
    "duration_sec",
    "cover_url",
    "share_url",
    "url",
}
RAW_RANKED_DIAGNOSTIC_FIELDS = (
    "absolute_hot_score",
    "fresh_hot_score",
    "hot_score",
    "ranking_mode",
    "ranking_rank",
    "route_rank",
    "age_hours",
    "engagement",
    "quality",
    "velocity",
)
HASHTAG_PATTERN = re.compile(r"(?<!\w)#([A-Za-z0-9_]+)")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
SIGNAL_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "with",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("trending input must be a JSON object")
    return payload


def _is_video_sample_artifact(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("videoSamples"), list)


def classify_trending_payload_kind(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("routes"), list):
        return "bakeoff_routes"
    if any(_is_video_sample_artifact(payload.get(key)) for key in VIDEO_SAMPLE_ARTIFACT_KEYS):
        return "consolidated_topn"
    if _is_video_sample_artifact(payload):
        return "video_samples_artifact"
    return "unsupported"


def classify_video_sample_row(row: dict[str, Any]) -> str:
    if CANONICAL_VIDEO_SAMPLE_REQUIRED_FIELDS.issubset(row.keys()) and isinstance(
        row.get("metrics"), dict
    ):
        return "canonical_video_sample"
    if RAW_RANKED_VIDEO_ROW_REQUIRED_FIELDS.issubset(row.keys()):
        return "raw_ranked_video_row"
    return "unknown_video_sample_row"


def _view_from_artifact_key(artifact_key: str, artifact_path: str) -> str:
    if "consolidated" in artifact_path:
        return "consolidated_hot"
    if artifact_key == "absolute_hot_video_samples":
        return "absolute_hot"
    if artifact_key == "fresh_hot_video_samples":
        return "fresh_hot"
    return "unknown"


def normalize_view_filter(view: str | None) -> set[str] | None:
    normalized = (view or "all").strip().lower()
    if normalized in ("all", "both"):
        return None
    if normalized in ("absolute_hot", "fresh_hot"):
        return {normalized}
    raise ValueError(
        "view must be one of " + ", ".join(SUPPORTED_VIEW_FILTERS)
    )


def iter_trending_video_sample_artifacts(
    payload: dict[str, Any],
    *,
    views: set[str] | None = None,
) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    routes = payload.get("routes")
    if isinstance(routes, list):
        for route_index, route in enumerate(routes):
            if not isinstance(route, dict):
                continue
            route_id = str(route.get("route_id") or f"route-{route_index}")
            for artifact_key in VIDEO_SAMPLE_ARTIFACT_KEYS:
                artifact = route.get(artifact_key)
                if not _is_video_sample_artifact(artifact):
                    continue
                view = _view_from_artifact_key(artifact_key, artifact_key)
                if views is not None and view not in views:
                    continue
                artifacts.append(
                    {
                        "artifactPath": f"routes[{route_index}].{artifact_key}",
                        "artifactKey": artifact_key,
                        "routeId": route_id,
                        "view": view,
                        "artifact": artifact,
                    }
                )
    for artifact_key in VIDEO_SAMPLE_ARTIFACT_KEYS:
        artifact = payload.get(artifact_key)
        if not _is_video_sample_artifact(artifact):
            continue
        view = _view_from_artifact_key(artifact_key, artifact.get("snapshotId", ""))
        if views is not None and view not in views:
            continue
        artifacts.append(
            {
                "artifactPath": artifact_key,
                "artifactKey": artifact_key,
                "routeId": "top-level",
                "view": view,
                "artifact": artifact,
            }
        )
    if _is_video_sample_artifact(payload) and views is None:
        artifacts.append(
            {
                "artifactPath": "$",
                "artifactKey": "videoSamples",
                "routeId": "top-level",
                "view": "unknown",
                "artifact": payload,
            }
        )
    return artifacts


def _shape_summary(rows: list[Any]) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    sample_field_counter: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, dict):
            counter["unknown_video_sample_row"] += 1
            continue
        counter[classify_video_sample_row(row)] += 1
        sample_field_counter.update(row.keys())
    if not rows:
        dominant_shape = "empty"
    elif len(counter) == 1:
        dominant_shape = next(iter(counter))
    else:
        dominant_shape = "mixed_video_sample_rows"
    return {
        "dominantSampleShape": dominant_shape,
        "sampleShapeCounts": dict(sorted(counter.items())),
        "sampleFields": sorted(sample_field_counter),
        "requiresAdapterNormalization": dominant_shape != "canonical_video_sample",
    }


def build_trending_adapter_contract(
    payload: dict[str, Any],
    *,
    views: set[str] | None = None,
) -> dict[str, Any]:
    payload_kind = classify_trending_payload_kind(payload)
    artifacts = []
    for entry in iter_trending_video_sample_artifacts(payload, views=views):
        artifact = entry["artifact"]
        rows = artifact.get("videoSamples") or []
        shape_summary = _shape_summary(rows)
        artifacts.append(
            {
                "artifactPath": entry["artifactPath"],
                "artifactKey": entry["artifactKey"],
                "routeId": entry["routeId"],
                "view": entry["view"],
                "schemaVersion": artifact.get("schemaVersion"),
                "snapshotId": artifact.get("snapshotId"),
                "market": artifact.get("market"),
                "language": artifact.get("language"),
                "capturedAt": artifact.get("capturedAt"),
                "sampleCount": len(rows),
                **shape_summary,
            }
        )
    return {
        "schemaVersion": "discovery-trending-adapter-contract.v1",
        "sourceSkill": "autotiktok-trending",
        "payloadKind": payload_kind,
        "artifactCount": len(artifacts),
        "artifacts": artifacts,
        "fieldOrigins": {
            "collectorTopLevelFields": ["snapshotId", "market", "language", "capturedAt"],
            "collectorRawRowFields": sorted(RAW_RANKED_VIDEO_ROW_REQUIRED_FIELDS),
            "collectorRawOptionalRowFields": sorted(RAW_RANKED_VIDEO_ROW_OPTIONAL_FIELDS),
            "adapterGeneratedFields": [
                "sourceSnapshots",
                "videoSampleId",
                "platformVideoId",
                "sourceSnapshotId",
                "publishedAt",
                "title",
                "desc",
                "authorId",
                "metrics",
            ],
            "rawMetaFields": list(RAW_RANKED_DIAGNOSTIC_FIELDS),
        },
    }


def _compact_timestamp(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("-", "")
        .replace(":", "")
        .replace(".", "")
    )


def _source_subtype_for_view(view: str) -> str:
    if view == "absolute_hot":
        return "absolute_hot_video_sample"
    if view == "fresh_hot":
        return "fresh_hot_video_sample"
    if view == "consolidated_hot":
        return "consolidated_hot_video_sample"
    return "video_sample"


def _require_consistent_artifact_field(artifacts: list[dict[str, Any]], field: str) -> str:
    values = [str(artifact.get(field) or "") for artifact in artifacts]
    first_value = values[0] if values else ""
    for value in values[1:]:
        if value != first_value:
            raise ValueError(f"{field} is inconsistent across trending video sample artifacts")
    if not first_value:
        raise ValueError(f"trending video sample artifacts are missing {field}")
    return first_value


def build_trending_discovery_snapshot_id(market: str, captured_at: str) -> str:
    return f"snap.discovery.tiktok-trending.{market.lower()}.{_compact_timestamp(captured_at)}"


def build_source_snapshots_from_trending(
    payload: dict[str, Any],
    *,
    snapshot_id: str | None = None,
    schema_version: str = "discovery-source-snapshots.v1",
    views: set[str] | None = None,
) -> dict[str, Any]:
    errors = validate_trending_adapter_contract(payload, views=views)
    if errors:
        raise ValueError("; ".join(errors))

    contract = build_trending_adapter_contract(payload, views=views)
    artifacts = contract["artifacts"]
    market = _require_consistent_artifact_field(artifacts, "market")
    language = _require_consistent_artifact_field(artifacts, "language")
    captured_at_values = [str(artifact["capturedAt"]) for artifact in artifacts]
    captured_at = min(captured_at_values)
    top_level_snapshot_id = snapshot_id or build_trending_discovery_snapshot_id(market, captured_at)

    source_snapshots: list[dict[str, Any]] = []
    seen_source_snapshot_ids: set[str] = set()
    for artifact in artifacts:
        source_snapshot_id = str(artifact.get("snapshotId") or "")
        if source_snapshot_id in seen_source_snapshot_ids:
            continue
        seen_source_snapshot_ids.add(source_snapshot_id)
        source_snapshots.append(
            {
                "sourceSnapshotId": source_snapshot_id,
                "source": "public_tiktok",
                "sourceSubtype": _source_subtype_for_view(str(artifact.get("view") or "")),
                "capturedAt": artifact["capturedAt"],
                "generatedFrom": {
                    "sourceSkill": "autotiktok-trending",
                    "payloadKind": contract["payloadKind"],
                    "artifactPath": artifact["artifactPath"],
                    "artifactKey": artifact["artifactKey"],
                    "routeId": artifact["routeId"],
                    "view": artifact["view"],
                    "dominantSampleShape": artifact["dominantSampleShape"],
                    "requiresAdapterNormalization": artifact[
                        "requiresAdapterNormalization"
                    ],
                },
            }
        )

    return {
        "schemaVersion": schema_version,
        "snapshotId": top_level_snapshot_id,
        "market": market,
        "language": language,
        "capturedAt": captured_at,
        "sourceSnapshots": source_snapshots,
        "generatedFrom": {
            "sourceSkill": "autotiktok-trending",
            "payloadKind": contract["payloadKind"],
            "artifactCount": contract["artifactCount"],
        },
    }


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _metric_number(value: Any, field: str) -> int | float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field} must be numeric")
        try:
            parsed = float(stripped)
        except ValueError as exc:
            raise ValueError(f"{field} must be numeric") from exc
        return int(parsed) if parsed.is_integer() else parsed
    raise ValueError(f"{field} must be numeric")


def _optional_metric_number(value: Any) -> int | float | None:
    if value in (None, ""):
        return None
    return _metric_number(value, "optional metric")


def _clean_hashtag(value: Any) -> str:
    cleaned = _as_text(value).lstrip("#").strip().lower()
    return re.sub(r"[^a-z0-9_]", "", cleaned)


def _clean_hashtags(raw_hashtags: Any, description: str) -> list[str]:
    candidates: list[str] = []
    if isinstance(raw_hashtags, list):
        candidates.extend(_as_text(item) for item in raw_hashtags)
    elif isinstance(raw_hashtags, str):
        candidates.extend(HASHTAG_PATTERN.findall(raw_hashtags))
    candidates.extend(HASHTAG_PATTERN.findall(description))

    seen: set[str] = set()
    hashtags: list[str] = []
    for candidate in candidates:
        hashtag = _clean_hashtag(candidate)
        if not hashtag or hashtag in seen:
            continue
        seen.add(hashtag)
        hashtags.append(hashtag)
    return hashtags


def _set_optional(sample: dict[str, Any], key: str, value: Any) -> None:
    if value in (None, ""):
        return
    sample[key] = value


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _unique_texts(values: list[Any], *, cap: int | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = _as_text(value).lower()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
        if cap is not None and len(out) >= cap:
            break
    return out


def _raw_ranked_row_meta(
    row: dict[str, Any],
    *,
    artifact_path: str,
    artifact_key: str,
    route_id: str,
    view: str,
    row_index: int,
) -> dict[str, Any]:
    raw_meta: dict[str, Any] = {
        "adapterRowShape": "raw_ranked_video_row",
        "adapterArtifactPath": artifact_path,
        "adapterArtifactKey": artifact_key,
        "adapterRouteId": route_id,
        "adapterView": view,
        "adapterRowIndex": row_index,
    }
    for field in RAW_RANKED_DIAGNOSTIC_FIELDS:
        if field in row:
            raw_meta[field] = row[field]
    for field in ("category_id", "category_name", "source_ids", "source_labels", "url"):
        if field in row:
            raw_meta[field] = row[field]
    return raw_meta


def _normalize_canonical_video_sample(
    row: dict[str, Any],
    *,
    source_snapshot_id: str,
) -> dict[str, Any]:
    normalized = dict(row)
    row_source_snapshot_id = _as_text(normalized.get("sourceSnapshotId"))
    if row_source_snapshot_id and row_source_snapshot_id != source_snapshot_id:
        raise ValueError(
            "canonical row sourceSnapshotId does not match artifact snapshotId: "
            f"{row_source_snapshot_id}"
        )
    normalized["sourceSnapshotId"] = source_snapshot_id
    return normalized


def _normalize_raw_ranked_video_row(
    row: dict[str, Any],
    *,
    source_snapshot_id: str,
    market: str,
    artifact_path: str,
    artifact_key: str,
    route_id: str,
    view: str,
    row_index: int,
) -> dict[str, Any]:
    platform_video_id = _as_text(row.get("video_id"))
    description = _as_text(row.get("description"))
    share_url = _as_text(row.get("share_url")) or _as_text(row.get("url"))
    metrics: dict[str, Any] = {
        "views": _metric_number(row.get("view_count"), "view_count"),
        "likes": _metric_number(row.get("like_count"), "like_count"),
        "shares": _metric_number(row.get("share_count"), "share_count"),
    }
    comments = _optional_metric_number(row.get("comment_count"))
    if comments is not None:
        metrics["comments"] = comments

    normalized: dict[str, Any] = {
        "videoSampleId": f"tt:{platform_video_id}",
        "platformVideoId": platform_video_id,
        "sourceSnapshotId": source_snapshot_id,
        "publishedAt": _as_text(row.get("create_time")),
        "title": description,
        "desc": description,
        "hashtags": _clean_hashtags(row.get("hashtags"), description),
        "authorId": _as_text(row.get("author_id")),
        "metrics": metrics,
        "rawMeta": _raw_ranked_row_meta(
            row,
            artifact_path=artifact_path,
            artifact_key=artifact_key,
            route_id=route_id,
            view=view,
            row_index=row_index,
        ),
    }
    _set_optional(normalized, "authorHandle", _as_text(row.get("author")))
    _set_optional(
        normalized,
        "authorDisplayName",
        _as_text(row.get("author_display_name")),
    )
    _set_optional(normalized, "durationSec", _optional_metric_number(row.get("duration_sec")))
    _set_optional(normalized, "coverUrl", _as_text(row.get("cover_url")))
    _set_optional(normalized, "shareUrl", share_url)
    _set_optional(normalized, "region", _as_text(row.get("region")) or market)
    return normalized


def _normalize_trending_video_sample_row(
    row: dict[str, Any],
    *,
    artifact: dict[str, Any],
    artifact_path: str,
    artifact_key: str,
    route_id: str,
    view: str,
    row_index: int,
) -> dict[str, Any]:
    source_snapshot_id = _as_text(artifact.get("snapshotId"))
    row_shape = classify_video_sample_row(row)
    if row_shape == "canonical_video_sample":
        return _normalize_canonical_video_sample(
            row,
            source_snapshot_id=source_snapshot_id,
        )
    if row_shape == "raw_ranked_video_row":
        return _normalize_raw_ranked_video_row(
            row,
            source_snapshot_id=source_snapshot_id,
            market=_as_text(artifact.get("market")),
            artifact_path=artifact_path,
            artifact_key=artifact_key,
            route_id=route_id,
            view=view,
            row_index=row_index,
        )
    raise ValueError(f"unsupported video sample row shape: {row_shape}")


def _float_from_any(value: Any, fallback: float = 0.0) -> float:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return fallback
    return fallback


def _source_score(sample: dict[str, Any]) -> float:
    raw_meta = sample.get("rawMeta") if isinstance(sample.get("rawMeta"), dict) else {}
    for key in ("hot_score", "absolute_hot_score", "fresh_hot_score"):
        score = _float_from_any(raw_meta.get(key), fallback=-1.0)
        if score >= 0:
            return _clamp(score, 0.0, 1.0)
    views = _float_from_any(sample.get("metrics", {}).get("views"))
    if views >= 150000:
        return 0.78
    if views >= 50000:
        return 0.68
    return 0.58


def _video_id_suffix(sample: dict[str, Any]) -> str:
    platform_id = _as_text(sample.get("platformVideoId")) or _as_text(
        sample.get("videoSampleId")
    )
    compact = re.sub(r"[^a-zA-Z0-9]", "", platform_id)
    return (compact[-8:] or "unknown").lower()


def _seed_terms(sample: dict[str, Any]) -> list[str]:
    hashtags = sample.get("hashtags") if isinstance(sample.get("hashtags"), list) else []
    terms = _unique_texts(hashtags, cap=4)
    if terms:
        return terms
    desc_tokens = [
        token
        for token in TOKEN_PATTERN.findall(_as_text(sample.get("desc")).lower())
        if token not in SIGNAL_STOPWORDS and len(token) > 1
    ]
    return _unique_texts(desc_tokens, cap=4) or [_video_id_suffix(sample)]


def _signal_slug(sample: dict[str, Any]) -> str:
    return "_".join(_seed_terms(sample)[:3])


def _topic_label(sample: dict[str, Any]) -> str:
    terms = _seed_terms(sample)[:3]
    if sample.get("hashtags"):
        return " ".join(f"#{term}" for term in terms)
    return " ".join(terms)


def _signal_confidence(sample: dict[str, Any]) -> float:
    score = _source_score(sample)
    return round(_clamp(0.52 + score * 0.38, 0.55, 0.9), 2)


def _expandability_hint(sample: dict[str, Any]) -> float:
    hashtags = sample.get("hashtags") if isinstance(sample.get("hashtags"), list) else []
    metrics = sample.get("metrics") if isinstance(sample.get("metrics"), dict) else {}
    views = _float_from_any(metrics.get("views"))
    tag_hint = min(0.22, len(hashtags) * 0.045)
    view_hint = 0.18 if views >= 150000 else 0.12 if views >= 50000 else 0.08
    score_hint = _source_score(sample) * 0.16
    return round(_clamp(0.35 + tag_hint + view_hint + score_hint, 0.4, 0.86), 2)


def _production_complexity(sample: dict[str, Any]) -> float:
    duration = _float_from_any(sample.get("durationSec"))
    if duration and duration <= 15:
        return 0.38
    if duration and duration <= 45:
        return 0.48
    return 0.54


def _build_signal_item_from_video_sample(
    sample: dict[str, Any],
    *,
    captured_at: str,
) -> dict[str, Any]:
    slug = _signal_slug(sample)
    suffix = _video_id_suffix(sample)
    topic_label = _topic_label(sample)
    author_handle = _as_text(sample.get("authorHandle"))
    keywords = _unique_texts(
        [
            *(_seed_terms(sample)[:4]),
            author_handle,
        ],
        cap=5,
    )
    related_queries = _unique_texts(
        [
            f"tiktok {topic_label}",
            f"{topic_label} trend",
            f"@{author_handle}" if author_handle else "",
        ],
        cap=3,
    )
    metrics = sample.get("metrics") if isinstance(sample.get("metrics"), dict) else {}
    views = int(_float_from_any(metrics.get("views")))
    return {
        "signalId": f"sig.discovery.tiktok_trending.{slug}.{suffix}",
        "capturedAt": captured_at,
        "sourceSnapshotId": sample["sourceSnapshotId"],
        "videoSampleId": sample["videoSampleId"],
        "signalConfidence": _signal_confidence(sample),
        "topicId": f"tp_trend_tiktok_trending_{slug}",
        "topicFingerprint": f"fp.trend.tiktok_trending.{slug}",
        "topicTitle": f"TikTok trend: {topic_label}",
        "topicSummary": (
            "Metadata-only TikTok trend signal derived from public video sample "
            f"{sample['videoSampleId']} with {views} observed views."
        ),
        "topicType": "trend",
        "sourceType": "public_video_sample",
        "keywords": keywords,
        "contentAngles": [
            f"trend reaction around {topic_label}",
            "why this video is gaining attention",
        ],
        "seedQueries": _seed_terms(sample)[:2],
        "relatedQueries": related_queries,
        "contentGapQueries": [],
        "searchIntentType": "trend_reaction",
        "searchPersistenceHint": "daily",
        "recommendedMode": "growth",
        "freshnessWindow": "daily",
        "expandabilityHint": _expandability_hint(sample),
        "recommendedFormats": ["talking_head", "image_plus_voiceover"],
        "requiredAssets": ["reference video", "trend screenshots"],
        "requiredCapabilities": ["trend commentary", "fast edit packaging"],
        "productionComplexity": _production_complexity(sample),
        "dependencyRisk": "medium",
        "fastTurnaround": True,
        "executionNotes": (
            "metadata-derived synthetic signal from autotiktok-trending; "
            "replace or enrich with MP4 multimodal analysis when available."
        ),
    }


def build_video_samples_from_trending(
    payload: dict[str, Any],
    *,
    snapshot_id: str | None = None,
    schema_version: str = "discovery-video-samples.v1",
    views: set[str] | None = None,
) -> dict[str, Any]:
    errors = validate_trending_adapter_contract(payload, views=views)
    if errors:
        raise ValueError("; ".join(errors))

    contract = build_trending_adapter_contract(payload, views=views)
    artifacts = contract["artifacts"]
    market = _require_consistent_artifact_field(artifacts, "market")
    language = _require_consistent_artifact_field(artifacts, "language")
    captured_at_values = [str(artifact["capturedAt"]) for artifact in artifacts]
    captured_at = min(captured_at_values)
    top_level_snapshot_id = snapshot_id or build_trending_discovery_snapshot_id(
        market,
        captured_at,
    )

    normalized_samples: list[dict[str, Any]] = []
    seen_video_sample_ids: set[str] = set()
    duplicates: list[dict[str, Any]] = []
    for entry in iter_trending_video_sample_artifacts(payload, views=views):
        artifact = entry["artifact"]
        rows = artifact.get("videoSamples") or []
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(
                    f"{entry['artifactPath']}.videoSamples[{row_index}] must be an object"
                )
            normalized = _normalize_trending_video_sample_row(
                row,
                artifact=artifact,
                artifact_path=entry["artifactPath"],
                artifact_key=entry["artifactKey"],
                route_id=entry["routeId"],
                view=entry["view"],
                row_index=row_index,
            )
            video_sample_id = str(normalized["videoSampleId"])
            if video_sample_id in seen_video_sample_ids:
                duplicates.append(
                    {
                        "videoSampleId": video_sample_id,
                        "droppedArtifactPath": entry["artifactPath"],
                        "droppedSourceSnapshotId": normalized["sourceSnapshotId"],
                    }
                )
                continue
            seen_video_sample_ids.add(video_sample_id)
            normalized_samples.append(normalized)

    return {
        "schemaVersion": schema_version,
        "snapshotId": top_level_snapshot_id,
        "market": market,
        "language": language,
        "capturedAt": captured_at,
        "videoSamples": normalized_samples,
        "generatedFrom": {
            "sourceSkill": "autotiktok-trending",
            "payloadKind": contract["payloadKind"],
            "artifactCount": contract["artifactCount"],
            "dedupeRule": "first_seen_by_artifact_and_row_order",
            "duplicateVideoSamples": duplicates,
        },
    }


def build_signal_items_from_trending(
    payload: dict[str, Any],
    *,
    snapshot_id: str | None = None,
    schema_version: str = "discovery-signal-items.v1",
    views: set[str] | None = None,
) -> dict[str, Any]:
    video_samples_payload = build_video_samples_from_trending(
        payload,
        snapshot_id=snapshot_id,
        views=views,
    )
    signal_items = [
        _build_signal_item_from_video_sample(
            sample,
            captured_at=video_samples_payload["capturedAt"],
        )
        for sample in video_samples_payload["videoSamples"]
    ]
    return {
        "schemaVersion": schema_version,
        "snapshotId": video_samples_payload["snapshotId"],
        "market": video_samples_payload["market"],
        "language": video_samples_payload["language"],
        "capturedAt": video_samples_payload["capturedAt"],
        "signalItems": signal_items,
        "generatedFrom": {
            "sourceSkill": "autotiktok-trending",
            "derivationMode": "metadata_only_synthetic",
            "videoSamplesSchemaVersion": video_samples_payload["schemaVersion"],
            "videoSampleCount": len(video_samples_payload["videoSamples"]),
        },
    }


def validate_trending_adapter_contract(
    payload: dict[str, Any],
    *,
    views: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = build_trending_adapter_contract(payload, views=views)
    if contract["payloadKind"] == "unsupported":
        return ["unsupported trending payload shape"]
    if contract["artifactCount"] == 0:
        return ["trending payload does not contain video sample artifacts"]
    for artifact in contract["artifacts"]:
        prefix = artifact["artifactPath"]
        for field in ("schemaVersion", "snapshotId", "market", "language", "capturedAt"):
            if not artifact.get(field):
                errors.append(f"{prefix} missing {field}")
        if artifact.get("schemaVersion") != "discovery-video-samples.v1":
            errors.append(f"{prefix} has unexpected schemaVersion: {artifact.get('schemaVersion')}")
        if artifact["sampleCount"] <= 0:
            errors.append(f"{prefix} must contain at least one video sample row")
        shape_counts = artifact.get("sampleShapeCounts", {})
        if shape_counts.get("unknown_video_sample_row"):
            errors.append(f"{prefix} contains unknown video sample rows")
    return errors
