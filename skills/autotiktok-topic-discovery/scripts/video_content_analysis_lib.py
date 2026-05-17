#!/usr/bin/env python3
"""
Contract helpers for AutoTikTok MP4 video-content analysis artifacts.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CANONICAL_SCHEMA_VERSION = "discovery-video-content-analysis.v1"
SAMPLE_SCHEMA_VERSION = "discovery-video-content-analysis.sample.v1"
CONFIG_SCHEMA_VERSION = "autotiktok-video-understanding-config.v1"
DEFAULT_PROVIDER = "google"
DEFAULT_MODEL = "gemini-3-flash-preview"
DEFAULT_CAPABILITY = "video.describe"
DEFAULT_TRANSPORT = "openclaw-infer"
STATUS_ANALYSIS_SUCCEEDED = "analysis_succeeded"
STATUS_DOWNLOAD_MISSING = "download_missing"
STATUS_ANALYSIS_FAILED = "analysis_failed"
DOWNLOAD_STATUS_DOWNLOADED = "downloaded"
DOWNLOAD_STATUS_ERROR = "error"
DOWNLOAD_STATUS_INVALID_FILE = "invalid_file"
DOWNLOAD_STATUS_MISSING = "missing"
SUPPORTED_STATUSES = {
    STATUS_ANALYSIS_SUCCEEDED,
    STATUS_DOWNLOAD_MISSING,
    STATUS_ANALYSIS_FAILED,
}
ANALYSIS_ID_SAFE_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]+")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"


def model_ref(provider: str, model: str) -> str:
    return f"{provider}/{model}"


def safe_analysis_token(value: Any) -> str:
    token = ANALYSIS_ID_SAFE_PATTERN.sub("-", str(value or "").strip())
    return token.strip("-") or "unknown"


def analysis_id_for(video_sample_id: str, provider: str, model: str) -> str:
    video_token = safe_analysis_token(video_sample_id).replace("tt-", "tt.")
    return f"vca.{video_token}.{safe_analysis_token(provider)}.{safe_analysis_token(model)}"


def resolve_video_understanding(
    config: dict[str, Any],
    *,
    provider_override: str | None = None,
    model_override: str | None = None,
) -> dict[str, str]:
    provider = (provider_override or str(config.get("defaultProvider") or DEFAULT_PROVIDER)).strip()
    model = (model_override or str(config.get("defaultModel") or DEFAULT_MODEL)).strip()
    selection_source = "cli_override" if provider_override or model_override else "config_default"
    if not provider:
        raise ValueError("video understanding provider is empty")
    if not model:
        raise ValueError("video understanding model is empty")
    return {
        "capability": DEFAULT_CAPABILITY,
        "transport": DEFAULT_TRANSPORT,
        "provider": provider,
        "model": model,
        "selectionSource": selection_source,
        "configPath": "skills/autotiktok-topic-discovery/config/video-understanding.v1.json",
    }


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _add_required_string_error(
    errors: list[str],
    value: Any,
    field: str,
) -> None:
    if not _is_non_empty_string(value):
        errors.append(f"{field} must be a non-empty string")


def _is_number_between_zero_and_one(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def validate_video_understanding_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if config.get("schemaVersion") != CONFIG_SCHEMA_VERSION:
        errors.append(
            f"config schemaVersion must be {CONFIG_SCHEMA_VERSION}, got {config.get('schemaVersion')}"
        )
    if config.get("capability") != DEFAULT_CAPABILITY:
        errors.append(f"config capability must be {DEFAULT_CAPABILITY}")
    if config.get("transport") != DEFAULT_TRANSPORT:
        errors.append(f"config transport must be {DEFAULT_TRANSPORT}")
    if config.get("defaultProvider") != DEFAULT_PROVIDER:
        errors.append(f"config defaultProvider must be {DEFAULT_PROVIDER}")
    if config.get("defaultModel") != DEFAULT_MODEL:
        errors.append(f"config defaultModel must be {DEFAULT_MODEL}")

    model_selection = config.get("modelSelection")
    if not isinstance(model_selection, dict):
        errors.append("config modelSelection must be an object")
    else:
        if model_selection.get("selectionSource") != "config_default":
            errors.append("config modelSelection.selectionSource must be config_default")
        if model_selection.get("defaultModelRef") != f"{DEFAULT_PROVIDER}/{DEFAULT_MODEL}":
            errors.append(
                f"config modelSelection.defaultModelRef must be {DEFAULT_PROVIDER}/{DEFAULT_MODEL}"
            )
        override_args = model_selection.get("overrideArgs")
        if not isinstance(override_args, list) or not {"--provider", "--model"}.issubset(
            set(override_args)
        ):
            errors.append("config modelSelection.overrideArgs must include --provider and --model")

    artifact_defaults = config.get("artifactDefaults")
    if not isinstance(artifact_defaults, dict):
        errors.append("config artifactDefaults must be an object")
    else:
        if artifact_defaults.get("schemaVersion") != CANONICAL_SCHEMA_VERSION:
            errors.append(
                f"config artifactDefaults.schemaVersion must be {CANONICAL_SCHEMA_VERSION}"
            )
        status_values = artifact_defaults.get("statusValues")
        if set(status_values or []) != SUPPORTED_STATUSES:
            errors.append("config artifactDefaults.statusValues must match supported statuses")
        if artifact_defaults.get("sidecarOnly") is not True:
            errors.append("config artifactDefaults.sidecarOnly must be true")

    fallback_policy = config.get("fallbackPolicy")
    if not isinstance(fallback_policy, dict):
        errors.append("config fallbackPolicy must be an object")
    else:
        for key in ("missingDownload", "analysisFailure", "timeout"):
            if fallback_policy.get(key) != "keep_metadata_only_signal":
                errors.append(f"config fallbackPolicy.{key} must keep metadata-only signal")
    return errors


def _validate_video_understanding(
    payload: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    video_understanding = payload.get("videoUnderstanding")
    if not isinstance(video_understanding, dict):
        return ["videoUnderstanding must be an object"]
    expected = {
        "capability": DEFAULT_CAPABILITY,
        "transport": DEFAULT_TRANSPORT,
    }
    for field, expected_value in expected.items():
        if video_understanding.get(field) != expected_value:
            errors.append(f"videoUnderstanding.{field} must be {expected_value}")
    _add_required_string_error(errors, video_understanding.get("provider"), "videoUnderstanding.provider")
    _add_required_string_error(errors, video_understanding.get("model"), "videoUnderstanding.model")
    if video_understanding.get("selectionSource") not in {"config_default", "cli_override"}:
        errors.append("videoUnderstanding.selectionSource must be config_default or cli_override")
    if video_understanding.get("selectionSource") == "config_default":
        if video_understanding.get("provider") != config.get("defaultProvider"):
            errors.append("videoUnderstanding.provider must match config defaultProvider")
        if video_understanding.get("model") != config.get("defaultModel"):
            errors.append("videoUnderstanding.model must match config defaultModel")
    _add_required_string_error(errors, video_understanding.get("configPath"), "videoUnderstanding.configPath")
    return errors


def _validate_download(
    entry: dict[str, Any],
    *,
    prefix: str,
    status: str,
) -> list[str]:
    errors: list[str] = []
    download = entry.get("download")
    if not isinstance(download, dict):
        return [f"{prefix}.download must be an object"]
    _add_required_string_error(errors, download.get("manifestEntryId"), f"{prefix}.download.manifestEntryId")
    download_status = download.get("status")
    if status == STATUS_ANALYSIS_SUCCEEDED:
        if download_status != DOWNLOAD_STATUS_DOWNLOADED:
            errors.append(f"{prefix}.download.status must be downloaded on success")
        _add_required_string_error(errors, entry.get("videoPath"), f"{prefix}.videoPath")
        if download.get("mimeType") != "video/mp4":
            errors.append(f"{prefix}.download.mimeType must be video/mp4")
        file_size = download.get("fileSizeBytes")
        if isinstance(file_size, bool) or not isinstance(file_size, int) or file_size <= 0:
            errors.append(f"{prefix}.download.fileSizeBytes must be a positive integer")
    elif status == STATUS_DOWNLOAD_MISSING:
        if download_status != DOWNLOAD_STATUS_MISSING:
            errors.append(f"{prefix}.download.status must be missing")
        if entry.get("videoPath") is not None:
            errors.append(f"{prefix}.videoPath must be null when download is missing")
    elif status == STATUS_ANALYSIS_FAILED:
        if download_status not in {
            DOWNLOAD_STATUS_DOWNLOADED,
            DOWNLOAD_STATUS_ERROR,
            DOWNLOAD_STATUS_INVALID_FILE,
        }:
            errors.append(
                f"{prefix}.download.status must be downloaded, error, or invalid_file on analysis failure"
            )
        if download_status == DOWNLOAD_STATUS_DOWNLOADED:
            _add_required_string_error(errors, entry.get("videoPath"), f"{prefix}.videoPath")
            if download.get("mimeType") != "video/mp4":
                errors.append(f"{prefix}.download.mimeType must be video/mp4")
    return errors


def _validate_provenance(entry: dict[str, Any], *, prefix: str) -> list[str]:
    errors: list[str] = []
    provenance = entry.get("provenance")
    if not isinstance(provenance, dict):
        return [f"{prefix}.provenance must be an object"]
    if provenance.get("inputVideoSampleReference") != entry.get("videoSampleId"):
        errors.append(
            f"{prefix}.provenance.inputVideoSampleReference must match videoSampleId"
        )
    _add_required_string_error(
        errors,
        provenance.get("inputDownloadManifestReference"),
        f"{prefix}.provenance.inputDownloadManifestReference",
    )
    if provenance.get("command") != "openclaw infer video describe":
        errors.append(f"{prefix}.provenance.command must be openclaw infer video describe")
    if provenance.get("rawOutputKind") != "video.description":
        errors.append(f"{prefix}.provenance.rawOutputKind must be video.description")
    _add_required_string_error(
        errors,
        provenance.get("rawOutputSource"),
        f"{prefix}.provenance.rawOutputSource",
    )
    return errors


def _validate_analysis_entry(
    entry: Any,
    *,
    index: int,
    provider: str,
    model: str,
) -> list[str]:
    prefix = f"analyses[{index}]"
    errors: list[str] = []
    if not isinstance(entry, dict):
        return [f"{prefix} must be an object"]
    for field in (
        "analysisId",
        "videoSampleId",
        "platformVideoId",
        "sourceSnapshotId",
        "provider",
        "model",
        "status",
    ):
        _add_required_string_error(errors, entry.get(field), f"{prefix}.{field}")
    for field in ("descriptionText", "contentSummary"):
        if not isinstance(entry.get(field), str):
            errors.append(f"{prefix}.{field} must be a string")
    if entry.get("provider") != provider:
        errors.append(f"{prefix}.provider must match videoUnderstanding.provider")
    if entry.get("model") != model:
        errors.append(f"{prefix}.model must match videoUnderstanding.model")

    status = entry.get("status")
    if status not in SUPPORTED_STATUSES:
        errors.append(f"{prefix}.status is unsupported: {status}")
        return errors

    errors.extend(_validate_download(entry, prefix=prefix, status=str(status)))
    errors.extend(_validate_provenance(entry, prefix=prefix))

    visual_evidence = entry.get("visualEvidence")
    replication_hints = entry.get("replicationHints")
    entry_errors = entry.get("errors")
    if not isinstance(visual_evidence, list):
        errors.append(f"{prefix}.visualEvidence must be a list")
        visual_evidence = []
    if not isinstance(replication_hints, list):
        errors.append(f"{prefix}.replicationHints must be a list")
        replication_hints = []
    if not isinstance(entry_errors, list):
        errors.append(f"{prefix}.errors must be a list")
        entry_errors = []
    if not _is_number_between_zero_and_one(entry.get("analysisConfidence")):
        errors.append(f"{prefix}.analysisConfidence must be between 0 and 1")

    if status == STATUS_ANALYSIS_SUCCEEDED:
        if not entry.get("descriptionText", "").strip():
            errors.append(f"{prefix}.descriptionText must be populated on success")
        if not entry.get("contentSummary", "").strip():
            errors.append(f"{prefix}.contentSummary must be populated on success")
        if len(visual_evidence) == 0:
            errors.append(f"{prefix}.visualEvidence must be populated on success")
        if len(replication_hints) == 0:
            errors.append(f"{prefix}.replicationHints must be populated on success")
        if len(entry_errors) != 0:
            errors.append(f"{prefix}.errors must be empty on success")
    else:
        if entry.get("descriptionText", "").strip():
            errors.append(f"{prefix}.descriptionText must be empty for fallback statuses")
        if entry.get("contentSummary", "").strip():
            errors.append(f"{prefix}.contentSummary must be empty for fallback statuses")
        if len(entry_errors) == 0:
            errors.append(f"{prefix}.errors must explain fallback statuses")
    return errors


def _expected_summary_counts(analyses: list[Any]) -> dict[str, int]:
    counts = Counter(entry.get("status") for entry in analyses if isinstance(entry, dict))
    return {
        "requested": len(analyses),
        "analysisSucceeded": counts[STATUS_ANALYSIS_SUCCEEDED],
        "downloadMissing": counts[STATUS_DOWNLOAD_MISSING],
        "analysisFailed": counts[STATUS_ANALYSIS_FAILED],
        "fallbackToMetadataOnly": counts[STATUS_DOWNLOAD_MISSING] + counts[STATUS_ANALYSIS_FAILED],
    }


def validate_video_content_analysis(
    payload: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    schema_version = payload.get("schemaVersion")
    if schema_version not in {CANONICAL_SCHEMA_VERSION, SAMPLE_SCHEMA_VERSION}:
        errors.append(f"schemaVersion is unsupported: {schema_version}")
    for field in ("snapshotId", "market", "language", "capturedAt"):
        _add_required_string_error(errors, payload.get(field), field)
    errors.extend(_validate_video_understanding(payload, config))

    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        errors.append("generatedFrom must be an object")
    else:
        if generated_from.get("sourceSkill") != "autotiktok-video-download":
            errors.append("generatedFrom.sourceSkill must be autotiktok-video-download")
        if generated_from.get("derivationMode") != "mp4_multimodal_sidecar":
            errors.append("generatedFrom.derivationMode must be mp4_multimodal_sidecar")
        if generated_from.get("enhancementMode") != "sidecar_only":
            errors.append("generatedFrom.enhancementMode must be sidecar_only")
        if generated_from.get("fallbackLane") != "metadata_only_signal_items":
            errors.append("generatedFrom.fallbackLane must be metadata_only_signal_items")

    analyses = payload.get("analyses")
    if not isinstance(analyses, list) or len(analyses) == 0:
        errors.append("analyses must be a non-empty list")
        analyses = []
    provider = str(payload.get("videoUnderstanding", {}).get("provider", ""))
    model = str(payload.get("videoUnderstanding", {}).get("model", ""))
    seen_analysis_ids: set[str] = set()
    seen_video_sample_ids: set[str] = set()
    for index, entry in enumerate(analyses):
        errors.extend(
            _validate_analysis_entry(entry, index=index, provider=provider, model=model)
        )
        if not isinstance(entry, dict):
            continue
        analysis_id = str(entry.get("analysisId") or "")
        video_sample_id = str(entry.get("videoSampleId") or "")
        if analysis_id in seen_analysis_ids:
            errors.append(f"analyses[{index}].analysisId is duplicated")
        if video_sample_id in seen_video_sample_ids:
            errors.append(f"analyses[{index}].videoSampleId is duplicated")
        seen_analysis_ids.add(analysis_id)
        seen_video_sample_ids.add(video_sample_id)

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary must be an object")
    else:
        for key, expected_value in _expected_summary_counts(analyses).items():
            if summary.get(key) != expected_value:
                errors.append(f"summary.{key} must be {expected_value}")
    return errors


def summarize_video_content_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    analyses = payload.get("analyses") if isinstance(payload.get("analyses"), list) else []
    counts = _expected_summary_counts(analyses)
    video_understanding = payload.get("videoUnderstanding")
    if not isinstance(video_understanding, dict):
        video_understanding = {}
    return {
        "schemaVersion": payload.get("schemaVersion"),
        "provider": video_understanding.get("provider"),
        "model": video_understanding.get("model"),
        **counts,
    }


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _content_summary_from_description(text: str) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return text.strip()
    return sentences[0]


def _visual_evidence_from_description(text: str) -> list[str]:
    sentences = _split_sentences(text)
    if not sentences and text.strip():
        sentences = [text.strip()]
    return sentences[:3]


def _replication_hints_from_description(text: str) -> list[str]:
    summary = _content_summary_from_description(text)
    if not summary:
        return []
    return [
        "reuse the clearest visual transformation described in the reference video",
        "capture close-up proof shots that make the topic immediately legible",
        "package the hook around the concrete object, action, or scene in the video",
    ]


def _description_from_openclaw_payload(payload: dict[str, Any]) -> str:
    outputs = payload.get("outputs")
    if not isinstance(outputs, list):
        return ""
    texts: list[str] = []
    for output in outputs:
        if not isinstance(output, dict):
            continue
        if output.get("kind") not in (None, "video.description"):
            continue
        text = output.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text.strip())
    return "\n".join(texts).strip()


def _download_payload_from_manifest_entry(entry: dict[str, Any]) -> dict[str, Any]:
    status = entry.get("status")
    download_status = {
        "downloaded": DOWNLOAD_STATUS_DOWNLOADED,
        "download_missing": DOWNLOAD_STATUS_MISSING,
        "download_error": DOWNLOAD_STATUS_ERROR,
        "invalid_file": DOWNLOAD_STATUS_INVALID_FILE,
    }.get(str(status), entry.get("downloadStatus"))
    return {
        "manifestEntryId": entry.get("manifestEntryId"),
        "status": download_status,
        "mimeType": entry.get("mimeType"),
        "fileSizeBytes": entry.get("fileSizeBytes"),
        "downloadedAt": entry.get("downloadedAt"),
    }


def _base_analysis_entry(
    download: dict[str, Any],
    video_understanding: dict[str, str],
) -> dict[str, Any]:
    return {
        "analysisId": analysis_id_for(
            str(download.get("videoSampleId") or ""),
            video_understanding["provider"],
            video_understanding["model"],
        ),
        "videoSampleId": download.get("videoSampleId"),
        "platformVideoId": download.get("platformVideoId"),
        "sourceSnapshotId": download.get("sourceSnapshotId"),
        "videoPath": download.get("videoPath"),
        "provider": video_understanding["provider"],
        "model": video_understanding["model"],
        "download": _download_payload_from_manifest_entry(download),
    }


def fallback_analysis_entry(
    download: dict[str, Any],
    video_understanding: dict[str, str],
    *,
    status: str,
    raw_output_source: str,
    errors: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        **_base_analysis_entry(download, video_understanding),
        "status": status,
        "descriptionText": "",
        "contentSummary": "",
        "visualEvidence": [],
        "replicationHints": [],
        "analysisConfidence": 0.0,
        "provenance": {
            "inputVideoSampleReference": download.get("videoSampleId"),
            "inputDownloadManifestReference": download.get("manifestEntryId"),
            "command": "openclaw infer video describe",
            "rawOutputKind": "video.description",
            "rawOutputSource": raw_output_source,
        },
        "errors": errors if errors is not None else list(download.get("errors") or []),
    }


def success_analysis_entry(
    download: dict[str, Any],
    video_understanding: dict[str, str],
    *,
    openclaw_payload: dict[str, Any],
    raw_output_source: str,
) -> dict[str, Any]:
    text = _description_from_openclaw_payload(openclaw_payload)
    if not text:
        return fallback_analysis_entry(
            download,
            video_understanding,
            status=STATUS_ANALYSIS_FAILED,
            raw_output_source=raw_output_source,
            errors=[
                {
                    "code": "missing_description",
                    "message": "OpenClaw video describe returned no description text.",
                }
            ],
        )
    return {
        **_base_analysis_entry(download, video_understanding),
        "status": STATUS_ANALYSIS_SUCCEEDED,
        "descriptionText": text,
        "contentSummary": _content_summary_from_description(text),
        "visualEvidence": _visual_evidence_from_description(text),
        "replicationHints": _replication_hints_from_description(text),
        "analysisConfidence": 0.84,
        "provenance": {
            "inputVideoSampleReference": download.get("videoSampleId"),
            "inputDownloadManifestReference": download.get("manifestEntryId"),
            "command": "openclaw infer video describe",
            "rawOutputKind": "video.description",
            "rawOutputSource": raw_output_source,
        },
        "errors": [],
    }


def build_video_content_analysis_artifact(
    *,
    download_manifest: dict[str, Any],
    video_understanding: dict[str, str],
    analyses: list[dict[str, Any]],
    schema_version: str = CANONICAL_SCHEMA_VERSION,
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "snapshotId": download_manifest.get("snapshotId"),
        "market": download_manifest.get("market"),
        "language": download_manifest.get("language"),
        "capturedAt": download_manifest.get("capturedAt"),
        "videoUnderstanding": video_understanding,
        "generatedFrom": {
            "sourceSkill": "autotiktok-video-download",
            "inputVideoSamplesSchemaVersion": download_manifest.get("generatedFrom", {}).get(
                "inputVideoSamplesSchemaVersion"
            ),
            "downloadManifestSchemaVersion": download_manifest.get("schemaVersion"),
            "derivationMode": "mp4_multimodal_sidecar",
            "enhancementMode": "sidecar_only",
            "fallbackLane": "metadata_only_signal_items",
        },
        "analyses": analyses,
        "summary": _expected_summary_counts(analyses),
    }
