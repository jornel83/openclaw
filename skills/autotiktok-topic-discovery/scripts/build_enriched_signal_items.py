#!/usr/bin/env python3
"""
Build enriched signalItems from metadata-only trending signals and videoContentAnalysis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trending_discovery_adapter_lib import build_signal_items_from_trending
from trending_discovery_adapter_lib import load_json
from video_signal_enrichment_lib import CANONICAL_SCHEMA_VERSION
from video_signal_enrichment_lib import build_enriched_signal_items
from video_signal_enrichment_lib import load_json_object
from video_signal_enrichment_lib import render_json


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SIGNAL_ITEMS = (
    SKILL_DIR / "fixtures" / "signal-items.video-content-analysis-base.sample.json"
)
DEFAULT_TRENDING_INPUT = SKILL_DIR / "fixtures" / "trending-consolidated-hot.sample.json"
DEFAULT_VIDEO_CONTENT_ANALYSIS = (
    SKILL_DIR / "fixtures" / "video-content-analysis.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trending-input", type=Path)
    parser.add_argument("--signal-items", type=Path, default=DEFAULT_SIGNAL_ITEMS)
    parser.add_argument(
        "--video-content-analysis",
        type=Path,
        default=DEFAULT_VIDEO_CONTENT_ANALYSIS,
    )
    parser.add_argument("--snapshot-id")
    parser.add_argument("--schema-version", default=CANONICAL_SCHEMA_VERSION)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        signal_items_payload = (
            build_signal_items_from_trending(
                load_json(args.trending_input),
                snapshot_id=args.snapshot_id,
                schema_version="discovery-signal-items.v1",
            )
            if args.trending_input
            else load_json_object(args.signal_items)
        )
        payload = build_enriched_signal_items(
            signal_items_payload,
            load_json_object(args.video_content_analysis),
            schema_version=args.schema_version,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = render_json(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote enriched signal items to {args.output}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
