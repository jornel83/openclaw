#!/usr/bin/env python3
"""
Run MP4 video understanding for a normalized videoDownloadManifest.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from video_content_analysis_lib import CANONICAL_SCHEMA_VERSION
from video_content_analysis_lib import STATUS_ANALYSIS_FAILED
from video_content_analysis_lib import STATUS_DOWNLOAD_MISSING
from video_content_analysis_lib import build_video_content_analysis_artifact
from video_content_analysis_lib import fallback_analysis_entry
from video_content_analysis_lib import load_json_object
from video_content_analysis_lib import model_ref
from video_content_analysis_lib import render_json
from video_content_analysis_lib import resolve_video_understanding
from video_content_analysis_lib import safe_analysis_token
from video_content_analysis_lib import success_analysis_entry
from video_content_analysis_lib import validate_video_content_analysis
from video_content_analysis_lib import validate_video_understanding_config


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DOWNLOAD_MANIFEST = SKILL_DIR / "fixtures" / "video-download-manifest.sample.json"
DEFAULT_CONFIG = SKILL_DIR / "config" / "video-understanding.v1.json"
DEFAULT_RESPONSE_FIXTURE = SKILL_DIR / "fixtures" / "video-describe-responses.sample.json"


def _response_key(download: dict[str, Any]) -> str:
    return str(download.get("videoSampleId") or download.get("videoPath") or "")


def _load_response_fixture(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    payload = load_json_object(path)
    responses = payload.get("responses")
    if not isinstance(responses, list):
        raise ValueError("response fixture must contain responses list")
    indexed: dict[str, dict[str, Any]] = {}
    for index, response in enumerate(responses):
        if not isinstance(response, dict):
            raise ValueError(f"responses[{index}] must be an object")
        key = str(response.get("videoSampleId") or response.get("path") or "")
        if not key:
            outputs = response.get("outputs")
            if isinstance(outputs, list) and outputs and isinstance(outputs[0], dict):
                key = str(outputs[0].get("path") or "")
        if not key:
            raise ValueError(f"responses[{index}] must include videoSampleId or path")
        indexed[key] = response
    return indexed


def _cache_path(cache_dir: Path, download: dict[str, Any], model_value: str) -> Path:
    token = safe_analysis_token(f"{download.get('videoSampleId')}.{model_value}")
    return cache_dir / f"{token}.json"


def _read_cached_response(
    *,
    cache_dir: Path | None,
    download: dict[str, Any],
    model_value: str,
    force: bool,
) -> dict[str, Any] | None:
    if cache_dir is None or force:
        return None
    path = _cache_path(cache_dir, download, model_value)
    if not path.is_file():
        return None
    return load_json_object(path)


def _write_cached_response(
    *,
    cache_dir: Path | None,
    download: dict[str, Any],
    model_value: str,
    response: dict[str, Any],
) -> None:
    if cache_dir is None:
        return
    cache_dir.mkdir(parents=True, exist_ok=True)
    _cache_path(cache_dir, download, model_value).write_text(
        render_json(response),
        encoding="utf-8",
    )


def _run_openclaw_video_describe(
    *,
    openclaw_bin: str,
    download: dict[str, Any],
    model_value: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    video_path = str(download.get("videoPath") or "")
    if not video_path:
        raise ValueError("downloaded video entry is missing videoPath")
    result = subprocess.run(
        [
            openclaw_bin,
            "infer",
            "video",
            "describe",
            "--file",
            video_path,
            "--model",
            model_value,
            "--json",
        ],
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "openclaw failed")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("openclaw video describe returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("openclaw video describe must return a JSON object")
    return payload


def _analysis_for_download(
    *,
    download: dict[str, Any],
    video_understanding: dict[str, str],
    responses: dict[str, dict[str, Any]],
    cache_dir: Path | None,
    force: bool,
    continue_on_error: bool,
    openclaw_bin: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    download_status = download.get("status")
    if download_status == "download_missing":
        return fallback_analysis_entry(
            download,
            video_understanding,
            status=STATUS_DOWNLOAD_MISSING,
            raw_output_source="not_invoked",
        )
    if download_status != "downloaded":
        return fallback_analysis_entry(
            download,
            video_understanding,
            status=STATUS_ANALYSIS_FAILED,
            raw_output_source="not_invoked",
        )

    selected_model = model_ref(video_understanding["provider"], video_understanding["model"])
    cached = _read_cached_response(
        cache_dir=cache_dir,
        download=download,
        model_value=selected_model,
        force=force,
    )
    if cached is not None:
        return success_analysis_entry(
            download,
            video_understanding,
            openclaw_payload=cached,
            raw_output_source="cache",
        )

    key = _response_key(download)
    response = responses.get(key) or responses.get(str(download.get("videoPath") or ""))
    raw_output_source = "response_fixture"
    if response is None:
        raw_output_source = "openclaw_cli"
        try:
            response = _run_openclaw_video_describe(
                openclaw_bin=openclaw_bin,
                download=download,
                model_value=selected_model,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            if not continue_on_error:
                raise
            return fallback_analysis_entry(
                download,
                video_understanding,
                status=STATUS_ANALYSIS_FAILED,
                raw_output_source=raw_output_source,
                errors=[{"code": "provider_error", "message": str(exc)}],
            )
    _write_cached_response(
        cache_dir=cache_dir,
        download=download,
        model_value=selected_model,
        response=response,
    )
    return success_analysis_entry(
        download,
        video_understanding,
        openclaw_payload=response,
        raw_output_source=raw_output_source,
    )


def build_batch_analysis(
    *,
    download_manifest: dict[str, Any],
    config: dict[str, Any],
    provider_override: str | None,
    model_override: str | None,
    response_fixture: Path | None,
    cache_dir: Path | None,
    force: bool,
    continue_on_error: bool,
    limit: int,
    openclaw_bin: str,
    timeout_seconds: int,
    schema_version: str,
) -> dict[str, Any]:
    config_errors = validate_video_understanding_config(config)
    if config_errors:
        raise ValueError("; ".join(config_errors))
    video_understanding = resolve_video_understanding(
        config,
        provider_override=provider_override,
        model_override=model_override,
    )
    responses = _load_response_fixture(response_fixture)
    downloads = download_manifest.get("downloads")
    if not isinstance(downloads, list):
        raise ValueError("download manifest must contain downloads list")
    selected_downloads = downloads[:limit] if limit and limit > 0 else downloads
    analyses = [
        _analysis_for_download(
            download=download,
            video_understanding=video_understanding,
            responses=responses,
            cache_dir=cache_dir,
            force=force,
            continue_on_error=continue_on_error,
            openclaw_bin=openclaw_bin,
            timeout_seconds=timeout_seconds,
        )
        for download in selected_downloads
        if isinstance(download, dict)
    ]
    payload = build_video_content_analysis_artifact(
        download_manifest=download_manifest,
        video_understanding=video_understanding,
        analyses=analyses,
        schema_version=schema_version,
    )
    validation_errors = validate_video_content_analysis(payload, config)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-manifest", type=Path, default=DEFAULT_DOWNLOAD_MANIFEST)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--provider")
    parser.add_argument("--model")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--response-fixture", type=Path)
    parser.add_argument("--use-default-response-fixture", action="store_true")
    parser.add_argument("--openclaw-bin", default="openclaw")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--schema-version", default=CANONICAL_SCHEMA_VERSION)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    response_fixture = args.response_fixture
    if response_fixture is None and args.use_default_response_fixture:
        response_fixture = DEFAULT_RESPONSE_FIXTURE

    try:
        payload = build_batch_analysis(
            download_manifest=load_json_object(args.download_manifest),
            config=load_json_object(args.config),
            provider_override=args.provider,
            model_override=args.model,
            response_fixture=response_fixture,
            cache_dir=args.cache_dir,
            force=args.force,
            continue_on_error=args.continue_on_error,
            limit=args.limit,
            openclaw_bin=args.openclaw_bin,
            timeout_seconds=args.timeout_seconds,
            schema_version=args.schema_version,
        )
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = render_json(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote video content analysis to {args.output}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
