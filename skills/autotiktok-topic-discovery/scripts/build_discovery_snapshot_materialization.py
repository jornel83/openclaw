#!/usr/bin/env python3
"""
Build a discovery snapshot-materialization artifact from standalone source snapshot,
signal item, and video sample inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from discovery_lib import build_snapshot_materialization
from discovery_lib import load_json


DEFAULT_SOURCE_SNAPSHOTS = (
    Path(__file__).resolve().parents[1] / "fixtures" / "source-snapshots.sample.json"
)
DEFAULT_SIGNAL_ITEMS = (
    Path(__file__).resolve().parents[1] / "fixtures" / "signal-items.sample.json"
)
DEFAULT_VIDEO_SAMPLES = (
    Path(__file__).resolve().parents[1] / "fixtures" / "video-samples.sample.json"
)
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "discovery-snapshot-materialization.sample.json"
)
DEFAULT_MATERIALIZATION_ID = "discovery-materialization.autotiktok.fixture.2026-04-15"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshots", type=Path, default=DEFAULT_SOURCE_SNAPSHOTS)
    parser.add_argument("--signal-items", type=Path, default=DEFAULT_SIGNAL_ITEMS)
    parser.add_argument("--video-samples", type=Path, default=DEFAULT_VIDEO_SAMPLES)
    parser.add_argument("--materialization-id", default=DEFAULT_MATERIALIZATION_ID)
    parser.add_argument("--schema-version", default="discovery-snapshot-materialization.sample.v1")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_snapshot_materialization(
            load_json(args.source_snapshots),
            load_json(args.signal_items),
            load_json(args.video_samples),
            materialization_id=args.materialization_id,
            schema_version=args.schema_version,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote discovery snapshot materialization to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
