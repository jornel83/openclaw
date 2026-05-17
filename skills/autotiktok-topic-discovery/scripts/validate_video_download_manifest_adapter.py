#!/usr/bin/env python3
"""
Validate the normalized videoDownloadManifest adapter fixture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from video_download_manifest_lib import build_video_download_manifest
from video_download_manifest_lib import load_json_object
from video_download_manifest_lib import summarize_video_download_manifest
from video_download_manifest_lib import validate_video_download_manifest


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO_SAMPLES = SKILL_DIR / "fixtures" / "video-samples.download-adapter.sample.json"
DEFAULT_RAW_MANIFEST = SKILL_DIR / "fixtures" / "video-download-raw.sample.json"
DEFAULT_EXPECTED = SKILL_DIR / "fixtures" / "video-download-manifest.sample.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-samples", type=Path, default=DEFAULT_VIDEO_SAMPLES)
    parser.add_argument("--raw-manifest", type=Path, default=DEFAULT_RAW_MANIFEST)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    try:
        video_samples = load_json_object(args.video_samples)
        raw_manifest = load_json_object(args.raw_manifest)
        expected = load_json_object(args.expected)
        actual = build_video_download_manifest(
            video_samples,
            raw_manifest,
            schema_version=str(expected.get("schemaVersion")),
        )
        errors = validate_video_download_manifest(expected)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if actual != expected:
        print("[ERROR] normalized video download manifest fixture is stale")
        print("ACTUAL:")
        print(json.dumps(actual, ensure_ascii=True, indent=2))
        return 1
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    summary = summarize_video_download_manifest(expected)
    if args.print_summary:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    print(
        "Validated "
        f"{args.expected}: {summary['requested']} video download entrie(s)."
    )
    print(f"- downloaded: {summary['downloaded']}")
    print(f"- download_missing: {summary['downloadMissing']}")
    print(f"- download_error: {summary['downloadError']}")
    print(f"- invalid_file: {summary['invalidFile']}")
    print(f"- duplicate_raw_downloads: {summary['duplicateRawDownloads']}")
    print("Video download manifest adapter is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
