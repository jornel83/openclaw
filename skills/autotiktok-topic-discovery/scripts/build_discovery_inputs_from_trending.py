#!/usr/bin/env python3
"""
Build all discovery input artifacts from an AutoTikTok trending output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trending_discovery_adapter_lib import build_signal_items_from_trending
from trending_discovery_adapter_lib import build_source_snapshots_from_trending
from trending_discovery_adapter_lib import build_video_samples_from_trending
from trending_discovery_adapter_lib import load_json
from trending_discovery_adapter_lib import normalize_view_filter
from trending_discovery_adapter_lib import SUPPORTED_VIEW_FILTERS


DEFAULT_INPUT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "trending-consolidated-hot.sample.json"
)
OUTPUT_FILENAMES = {
    "sourceSnapshots": "source-snapshots.from-trending.json",
    "videoSamples": "video-samples.from-trending.json",
    "signalItems": "signal-items.from-trending.synthetic.json",
}


def render_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--snapshot-id")
    parser.add_argument(
        "--view",
        choices=SUPPORTED_VIEW_FILTERS,
        default="all",
        help=(
            "Trending view to materialize. Use absolute_hot or fresh_hot for a "
            "single-view TopN run; use both/all only when both views will be "
            "downloaded and video-understood before ranking."
        ),
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    try:
        trending_payload = load_json(args.input)
        views = normalize_view_filter(args.view)
        artifacts = {
            "sourceSnapshots": build_source_snapshots_from_trending(
                trending_payload,
                snapshot_id=args.snapshot_id,
                views=views,
            ),
            "videoSamples": build_video_samples_from_trending(
                trending_payload,
                snapshot_id=args.snapshot_id,
                views=views,
            ),
            "signalItems": build_signal_items_from_trending(
                trending_payload,
                snapshot_id=args.snapshot_id,
                views=views,
            ),
        }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for key, filename in OUTPUT_FILENAMES.items():
            output_path = args.output_dir / filename
            output_path.write_text(render_json(artifacts[key]), encoding="utf-8")
            print(f"Wrote {key} to {output_path}")
        return 0

    print(render_json(artifacts), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
