#!/usr/bin/env python3
"""
Validate the AutoTikTok video-content analysis contract fixture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from video_content_analysis_lib import load_json_object
from video_content_analysis_lib import summarize_video_content_analysis
from video_content_analysis_lib import validate_video_content_analysis
from video_content_analysis_lib import validate_video_understanding_config


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = SKILL_DIR / "fixtures" / "video-content-analysis.sample.json"
DEFAULT_CONFIG = SKILL_DIR / "config" / "video-understanding.v1.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    try:
        config = load_json_object(args.config)
        payload = load_json_object(args.input)
        errors = [
            *validate_video_understanding_config(config),
            *validate_video_content_analysis(payload, config),
        ]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    summary = summarize_video_content_analysis(payload)
    if args.print_summary:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    print(
        "Validated "
        f"{args.input}: {summary['requested']} video content analysis entrie(s)."
    )
    print(f"- analysis_succeeded: {summary['analysisSucceeded']}")
    print(f"- download_missing: {summary['downloadMissing']}")
    print(f"- analysis_failed: {summary['analysisFailed']}")
    print(f"Default video model: {summary['provider']}/{summary['model']}")
    print("Video content analysis contract is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
