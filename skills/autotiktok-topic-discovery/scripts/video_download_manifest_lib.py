#!/usr/bin/env python3
"""
Normalize autotiktok-video-download manifests and join them to videoSamples.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CANONICAL_SCHEMA_VERSION = "discovery-video-download-manifest.v1"
SAMPLE_SCHEMA_VERSION = "discovery-video-download-manifest.sample.v1"
RAW_DOWNLOAD_SKILL = "tiktok-video-download"
STATUS_DOWNLOADED = "downloaded"
STATUS_DOWNLOAD_MISSING = "download_missing"
STATUS_DOWNLOAD_ERROR = "download_error"
STATUS_INVALID_FILE = "invalid_file"
SUPPORTED_STATUSES = {
    STATUS_DOWNLOADED,
    STATUS_DOWNLOAD_MISSING,
    STATUS_DOWNLOAD_ERROR,
    STATUS_INVALID_FILE,
}
JOIN_RULE = "platformVideoId_primary_shareUrl_secondary_fileStem_fallback"
VIDEO_ID_PATTERN = re.compile(r"/video/(\d+)|/v/(\d+)")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            parsed = float(stripped)
        except ValueError:
            return None
        return int(parsed) if parsed.is_integer() else None
    return None


def _extract_video_id_from_url(url: str) -> str:
    match = VIDEO_ID_PATTERN.search(url)
    if not match:
        return ""
    return next((group for group in match.groups() if group), "")


def _video_id_from_file(value: str) -> str:
    stem = Path(value).stem
    return stem if stem.isdigit() else ""


def _raw_video_id(record: dict[str, Any]) -> str:
    return (
        _as_text(record.get("video_id"))
        or _extract_video_id_from_url(_as_text(record.get("url")))
        or _video_id_from_file(_as_text(record.get("file")))
    )


def _sample_video_id(sample: dict[str, Any]) -> str:
    return _as_text(sample.get("platformVideoId")) or _as_text(
        sample.get("videoSampleId")
    ).removeprefix("tt:")


def _sample_share_url(sample: dict[str, Any]) -> str:
    return _as_text(sample.get("shareUrl")) or _as_text(
        sample.get("rawMeta", {}).get("url") if isinstance(sample.get("rawMeta"), dict) else ""
    )


def _mime_type_from_path(path_value: str) -> str | None:
    suffix = Path(path_value).suffix.lower()
    if suffix == ".mp4":
        return "video/mp4"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mov":
        return "video/quicktime"
    return None


def _base_entry(sample: dict[str, Any]) -> dict[str, Any]:
    platform_video_id = _sample_video_id(sample)
    return {
        "manifestEntryId": f"download.tt.{platform_video_id}",
        "videoSampleId": _as_text(sample.get("videoSampleId")),
        "platformVideoId": platform_video_id,
        "sourceSnapshotId": _as_text(sample.get("sourceSnapshotId")),
        "shareUrl": _sample_share_url(sample),
    }


def _error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _warning(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _raw_indexes_for_sample(
    sample: dict[str, Any],
    raw_downloads: list[dict[str, Any]],
) -> tuple[list[int], str]:
    platform_video_id = _sample_video_id(sample)
    share_url = _sample_share_url(sample)
    if platform_video_id:
        matches = [
            index
            for index, record in enumerate(raw_downloads)
            if _raw_video_id(record) == platform_video_id
        ]
        if matches:
            return matches, "platform_video_id"
    if share_url:
        matches = [
            index
            for index, record in enumerate(raw_downloads)
            if _as_text(record.get("url")) == share_url
        ]
        if matches:
            return matches, "share_url"
    if platform_video_id:
        matches = [
            index
            for index, record in enumerate(raw_downloads)
            if _video_id_from_file(_as_text(record.get("file"))) == platform_video_id
        ]
        if matches:
            return matches, "file_stem"
    return [], "none"


def _join_status(match_strategy: str) -> str:
    if match_strategy == "platform_video_id":
        return "matched_by_platform_video_id"
    if match_strategy == "share_url":
        return "matched_by_share_url"
    if match_strategy == "file_stem":
        return "matched_by_file_stem"
    return "missing_download"


def _downloaded_entry(
    sample: dict[str, Any],
    record: dict[str, Any],
    *,
    raw_index: int,
    duplicate_indexes: list[int],
    match_strategy: str,
) -> dict[str, Any]:
    file_path = _as_text(record.get("file"))
    file_size = _optional_int(record.get("size_bytes"))
    duration_sec = _optional_int(record.get("duration_sec"))
    mime_type = _mime_type_from_path(file_path)
    warnings = []
    if duplicate_indexes:
        warnings.append(
            _warning(
                "duplicate_download",
                "Multiple raw download records matched this video sample; the first usable record was kept.",
            )
        )
    if mime_type != "video/mp4" or not file_size or file_size <= 0:
        return {
            **_base_entry(sample),
            "status": STATUS_INVALID_FILE,
            "joinStatus": _join_status(match_strategy),
            "matchStrategy": match_strategy,
            "videoPath": file_path or None,
            "mimeType": mime_type,
            "fileSizeBytes": file_size,
            "durationSec": duration_sec,
            "downloadStatus": _as_text(record.get("status")),
            "rawDownloadIndexes": [raw_index],
            "duplicateRawDownloadIndexes": duplicate_indexes,
            "downloadedAt": record.get("downloaded_at") or record.get("downloadedAt"),
            "warnings": warnings,
            "errors": [
                _error(
                    "invalid_file",
                    "Downloaded file must be a non-empty MP4 before video understanding can run.",
                )
            ],
        }
    return {
        **_base_entry(sample),
        "status": STATUS_DOWNLOADED,
        "joinStatus": _join_status(match_strategy),
        "matchStrategy": match_strategy,
        "videoPath": file_path,
        "mimeType": mime_type,
        "fileSizeBytes": file_size,
        "durationSec": duration_sec,
        "downloadStatus": _as_text(record.get("status")),
        "rawDownloadIndexes": [raw_index],
        "duplicateRawDownloadIndexes": duplicate_indexes,
        "downloadedAt": record.get("downloaded_at") or record.get("downloadedAt"),
        "warnings": warnings,
        "errors": [],
    }


def _missing_entry(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        **_base_entry(sample),
        "status": STATUS_DOWNLOAD_MISSING,
        "joinStatus": "missing_download",
        "matchStrategy": "none",
        "videoPath": None,
        "mimeType": None,
        "fileSizeBytes": None,
        "durationSec": None,
        "downloadStatus": "missing",
        "rawDownloadIndexes": [],
        "duplicateRawDownloadIndexes": [],
        "downloadedAt": None,
        "warnings": [],
        "errors": [_error("download_missing", "No raw download record matched this video sample.")],
    }


def _error_entry(
    sample: dict[str, Any],
    record: dict[str, Any],
    *,
    raw_index: int,
    duplicate_indexes: list[int],
    match_strategy: str,
) -> dict[str, Any]:
    message = _as_text(record.get("error")) or "Raw download failed."
    return {
        **_base_entry(sample),
        "status": STATUS_DOWNLOAD_ERROR,
        "joinStatus": _join_status(match_strategy),
        "matchStrategy": match_strategy,
        "videoPath": None,
        "mimeType": None,
        "fileSizeBytes": None,
        "durationSec": None,
        "downloadStatus": "error",
        "rawDownloadIndexes": [raw_index],
        "duplicateRawDownloadIndexes": duplicate_indexes,
        "downloadedAt": None,
        "warnings": [],
        "errors": [_error("download_error", message)],
    }


def _normalize_sample_download(
    sample: dict[str, Any],
    raw_downloads: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_indexes, match_strategy = _raw_indexes_for_sample(sample, raw_downloads)
    if not raw_indexes:
        return _missing_entry(sample)
    primary_index = raw_indexes[0]
    duplicate_indexes = raw_indexes[1:]
    record = raw_downloads[primary_index]
    raw_status = _as_text(record.get("status"))
    if raw_status == "error":
        return _error_entry(
            sample,
            record,
            raw_index=primary_index,
            duplicate_indexes=duplicate_indexes,
            match_strategy=match_strategy,
        )
    return _downloaded_entry(
        sample,
        record,
        raw_index=primary_index,
        duplicate_indexes=duplicate_indexes,
        match_strategy=match_strategy,
    )


def _summary(downloads: list[dict[str, Any]], unmatched_raw_downloads: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(download["status"] for download in downloads)
    duplicate_count = sum(len(download["duplicateRawDownloadIndexes"]) for download in downloads)
    return {
        "requested": len(downloads),
        "downloaded": counts[STATUS_DOWNLOADED],
        "downloadMissing": counts[STATUS_DOWNLOAD_MISSING],
        "downloadError": counts[STATUS_DOWNLOAD_ERROR],
        "invalidFile": counts[STATUS_INVALID_FILE],
        "duplicateRawDownloads": duplicate_count,
        "unmatchedRawDownloads": len(unmatched_raw_downloads),
        "fallbackToMetadataOnly": counts[STATUS_DOWNLOAD_MISSING]
        + counts[STATUS_DOWNLOAD_ERROR]
        + counts[STATUS_INVALID_FILE],
    }


def build_video_download_manifest(
    video_samples_payload: dict[str, Any],
    raw_download_manifest: dict[str, Any],
    *,
    schema_version: str = CANONICAL_SCHEMA_VERSION,
) -> dict[str, Any]:
    raw_downloads = raw_download_manifest.get("downloads")
    if not isinstance(raw_downloads, list):
        raise ValueError("raw download manifest must contain downloads list")
    raw_download_objects = []
    for index, record in enumerate(raw_downloads):
        if not isinstance(record, dict):
            raise ValueError(f"raw downloads[{index}] must be an object")
        raw_download_objects.append(record)
    video_samples = video_samples_payload.get("videoSamples")
    if not isinstance(video_samples, list) or not video_samples:
        raise ValueError("videoSamples payload must contain a non-empty videoSamples list")
    normalized_downloads = [
        _normalize_sample_download(sample, raw_download_objects)
        for sample in video_samples
        if isinstance(sample, dict)
    ]
    matched_raw_indexes: set[int] = set()
    for download in normalized_downloads:
        matched_raw_indexes.update(download["rawDownloadIndexes"])
        matched_raw_indexes.update(download["duplicateRawDownloadIndexes"])
    unmatched_raw_downloads = [
        {
            "rawDownloadIndex": index,
            "videoId": _raw_video_id(record),
            "url": _as_text(record.get("url")),
            "status": _as_text(record.get("status")),
        }
        for index, record in enumerate(raw_download_objects)
        if index not in matched_raw_indexes
    ]
    return {
        "schemaVersion": schema_version,
        "snapshotId": video_samples_payload.get("snapshotId"),
        "market": video_samples_payload.get("market"),
        "language": video_samples_payload.get("language"),
        "capturedAt": raw_download_manifest.get("captured_at")
        or raw_download_manifest.get("capturedAt")
        or video_samples_payload.get("capturedAt"),
        "generatedFrom": {
            "sourceSkill": "autotiktok-video-download",
            "inputVideoSamplesSchemaVersion": video_samples_payload.get("schemaVersion"),
            "rawDownloadManifestSkill": raw_download_manifest.get("skill"),
            "rawDownloadManifestSummary": raw_download_manifest.get("summary"),
            "joinRule": JOIN_RULE,
            "fallbackLane": "metadata_only_signal_items",
        },
        "downloads": normalized_downloads,
        "unmatchedRawDownloads": unmatched_raw_downloads,
        "summary": _summary(normalized_downloads, unmatched_raw_downloads),
    }


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _required_string(errors: list[str], value: Any, field: str) -> None:
    if not _is_non_empty_string(value):
        errors.append(f"{field} must be a non-empty string")


def _required_nullable_string(errors: list[str], value: Any, field: str) -> None:
    if value is not None and not isinstance(value, str):
        errors.append(f"{field} must be null or string")


def validate_video_download_manifest(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") not in {CANONICAL_SCHEMA_VERSION, SAMPLE_SCHEMA_VERSION}:
        errors.append(f"schemaVersion is unsupported: {payload.get('schemaVersion')}")
    for field in ("snapshotId", "market", "language", "capturedAt"):
        _required_string(errors, payload.get(field), field)
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        errors.append("generatedFrom must be an object")
    else:
        if generated_from.get("sourceSkill") != "autotiktok-video-download":
            errors.append("generatedFrom.sourceSkill must be autotiktok-video-download")
        if generated_from.get("rawDownloadManifestSkill") != RAW_DOWNLOAD_SKILL:
            errors.append(f"generatedFrom.rawDownloadManifestSkill must be {RAW_DOWNLOAD_SKILL}")
        if generated_from.get("joinRule") != JOIN_RULE:
            errors.append(f"generatedFrom.joinRule must be {JOIN_RULE}")
        if generated_from.get("fallbackLane") != "metadata_only_signal_items":
            errors.append("generatedFrom.fallbackLane must be metadata_only_signal_items")

    downloads = payload.get("downloads")
    if not isinstance(downloads, list) or not downloads:
        errors.append("downloads must be a non-empty list")
        downloads = []
    seen_entry_ids: set[str] = set()
    seen_video_sample_ids: set[str] = set()
    for index, entry in enumerate(downloads):
        prefix = f"downloads[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in (
            "manifestEntryId",
            "videoSampleId",
            "platformVideoId",
            "sourceSnapshotId",
            "shareUrl",
            "status",
            "joinStatus",
            "matchStrategy",
            "downloadStatus",
        ):
            _required_string(errors, entry.get(field), f"{prefix}.{field}")
        _required_nullable_string(errors, entry.get("videoPath"), f"{prefix}.videoPath")
        _required_nullable_string(errors, entry.get("mimeType"), f"{prefix}.mimeType")
        if entry.get("status") not in SUPPORTED_STATUSES:
            errors.append(f"{prefix}.status is unsupported: {entry.get('status')}")
        if not isinstance(entry.get("rawDownloadIndexes"), list):
            errors.append(f"{prefix}.rawDownloadIndexes must be a list")
        if not isinstance(entry.get("duplicateRawDownloadIndexes"), list):
            errors.append(f"{prefix}.duplicateRawDownloadIndexes must be a list")
        if not isinstance(entry.get("warnings"), list):
            errors.append(f"{prefix}.warnings must be a list")
        if not isinstance(entry.get("errors"), list):
            errors.append(f"{prefix}.errors must be a list")
        if entry.get("manifestEntryId") in seen_entry_ids:
            errors.append(f"{prefix}.manifestEntryId is duplicated")
        if entry.get("videoSampleId") in seen_video_sample_ids:
            errors.append(f"{prefix}.videoSampleId is duplicated")
        seen_entry_ids.add(_as_text(entry.get("manifestEntryId")))
        seen_video_sample_ids.add(_as_text(entry.get("videoSampleId")))

        if entry.get("status") == STATUS_DOWNLOADED:
            if entry.get("mimeType") != "video/mp4":
                errors.append(f"{prefix}.mimeType must be video/mp4 when downloaded")
            if not isinstance(entry.get("fileSizeBytes"), int) or entry.get("fileSizeBytes") <= 0:
                errors.append(f"{prefix}.fileSizeBytes must be positive when downloaded")
            if entry.get("errors"):
                errors.append(f"{prefix}.errors must be empty when downloaded")
        elif entry.get("status") == STATUS_DOWNLOAD_MISSING:
            if entry.get("videoPath") is not None:
                errors.append(f"{prefix}.videoPath must be null when download is missing")
            if entry.get("rawDownloadIndexes") != []:
                errors.append(f"{prefix}.rawDownloadIndexes must be empty when missing")
            if not entry.get("errors"):
                errors.append(f"{prefix}.errors must explain missing downloads")
        else:
            if not entry.get("errors"):
                errors.append(f"{prefix}.errors must explain fallback statuses")

    unmatched = payload.get("unmatchedRawDownloads")
    if not isinstance(unmatched, list):
        errors.append("unmatchedRawDownloads must be a list")
        unmatched = []
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary must be an object")
    else:
        expected = _summary([entry for entry in downloads if isinstance(entry, dict)], unmatched)
        for key, value in expected.items():
            if summary.get(key) != value:
                errors.append(f"summary.{key} must be {value}")
    return errors


def summarize_video_download_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return {
        "schemaVersion": payload.get("schemaVersion"),
        "requested": summary.get("requested"),
        "downloaded": summary.get("downloaded"),
        "downloadMissing": summary.get("downloadMissing"),
        "downloadError": summary.get("downloadError"),
        "invalidFile": summary.get("invalidFile"),
        "duplicateRawDownloads": summary.get("duplicateRawDownloads"),
        "fallbackToMetadataOnly": summary.get("fallbackToMetadataOnly"),
    }
