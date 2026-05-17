#!/usr/bin/env python3
"""
Build a normalized videoDownloadManifest from videoSamples and raw download output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from video_download_manifest_lib import build_video_download_manifest
from video_download_manifest_lib import load_json_object


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO_SAMPLES = SKILL_DIR / "fixtures" / "video-samples.download-adapter.sample.json"
DEFAULT_RAW_MANIFEST = SKILL_DIR / "fixtures" / "video-download-raw.sample.json"


def render_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-samples", type=Path, default=DEFAULT_VIDEO_SAMPLES)
    parser.add_argument("--raw-manifest", type=Path, default=DEFAULT_RAW_MANIFEST)
    parser.add_argument("--schema-version", default="discovery-video-download-manifest.v1")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = build_video_download_manifest(
            load_json_object(args.video_samples),
            load_json_object(args.raw_manifest),
            schema_version=args.schema_version,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = render_json(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote video download manifest to {args.output}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
