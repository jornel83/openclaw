#!/usr/bin/env python3
"""
Validate the video-content analysis batch runner against committed fixtures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from run_video_content_analysis_batch import DEFAULT_CONFIG
from run_video_content_analysis_batch import DEFAULT_DOWNLOAD_MANIFEST
from run_video_content_analysis_batch import DEFAULT_RESPONSE_FIXTURE
from run_video_content_analysis_batch import build_batch_analysis
from video_content_analysis_lib import SAMPLE_SCHEMA_VERSION
from video_content_analysis_lib import load_json_object
from video_content_analysis_lib import summarize_video_content_analysis


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EXPECTED = SKILL_DIR / "fixtures" / "video-content-analysis.sample.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-manifest", type=Path, default=DEFAULT_DOWNLOAD_MANIFEST)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--response-fixture", type=Path, default=DEFAULT_RESPONSE_FIXTURE)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    try:
        actual = build_batch_analysis(
            download_manifest=load_json_object(args.download_manifest),
            config=load_json_object(args.config),
            provider_override=None,
            model_override=None,
            response_fixture=args.response_fixture,
            cache_dir=None,
            force=False,
            continue_on_error=True,
            limit=0,
            openclaw_bin="openclaw",
            timeout_seconds=180,
            schema_version=SAMPLE_SCHEMA_VERSION,
        )
        expected = load_json_object(args.expected)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if actual != expected:
        print("[ERROR] video content analysis batch fixture is stale")
        print("ACTUAL:")
        print(json.dumps(actual, ensure_ascii=True, indent=2))
        return 1

    summary = summarize_video_content_analysis(expected)
    if args.print_summary:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    print(
        "Validated video content analysis batch runner: "
        f"{summary['requested']} analysis entrie(s)."
    )
    print(f"- analysis_succeeded: {summary['analysisSucceeded']}")
    print(f"- download_missing: {summary['downloadMissing']}")
    print(f"- analysis_failed: {summary['analysisFailed']}")
    print(f"Default video model: {summary['provider']}/{summary['model']}")
    print("Video content analysis batch runner is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
