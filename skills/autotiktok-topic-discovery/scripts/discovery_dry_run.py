#!/usr/bin/env python3
"""
Build evidence bundles, merge groups, and topic candidates from sample signals.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from discovery_lib import DEFAULT_POLICY, build_payload, build_snapshot_materialization, load_json, load_policy


DEFAULT_INPUT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "discovery-snapshot-materialization.sample.json"
)
DEFAULT_SOURCE_SNAPSHOTS = (
    Path(__file__).resolve().parents[1] / "fixtures" / "source-snapshots.sample.json"
)
DEFAULT_SIGNAL_ITEMS = (
    Path(__file__).resolve().parents[1] / "fixtures" / "signal-items.sample.json"
)
DEFAULT_VIDEO_SAMPLES = (
    Path(__file__).resolve().parents[1] / "fixtures" / "video-samples.sample.json"
)
DEFAULT_MATERIALIZATION_ID = "discovery-materialization.autotiktok.fixture.2026-04-15"
DEFAULT_MATERIALIZATION_SCHEMA_VERSION = "discovery-snapshot-materialization.sample.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        "--signals",
        dest="input_path",
        type=Path,
        default=None,
        help="Path to either a raw-signals fixture or a snapshot-materialization fixture.",
    )
    parser.add_argument("--source-snapshots", type=Path)
    parser.add_argument("--signal-items", type=Path)
    parser.add_argument("--video-samples", type=Path)
    parser.add_argument("--materialization-id")
    parser.add_argument(
        "--materialization-schema-version",
        default="discovery-snapshot-materialization.v1",
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        use_component_inputs = any(
            value is not None
            for value in (args.source_snapshots, args.signal_items, args.video_samples)
        )
        if args.input_path is not None and use_component_inputs:
            raise ValueError(
                "--input/--signals cannot be combined with --source-snapshots, --signal-items, or --video-samples"
            )
        if use_component_inputs:
            if not args.source_snapshots or not args.signal_items or not args.video_samples:
                raise ValueError(
                    "--source-snapshots, --signal-items, and --video-samples must be passed together"
                )
            discovery_input = build_snapshot_materialization(
                load_json(args.source_snapshots),
                load_json(args.signal_items),
                load_json(args.video_samples),
                materialization_id=args.materialization_id,
                schema_version=args.materialization_schema_version,
            )
        elif args.input_path is not None:
            discovery_input = load_json(args.input_path)
        else:
            discovery_input = build_snapshot_materialization(
                load_json(DEFAULT_SOURCE_SNAPSHOTS),
                load_json(DEFAULT_SIGNAL_ITEMS),
                load_json(DEFAULT_VIDEO_SAMPLES),
                materialization_id=DEFAULT_MATERIALIZATION_ID,
                schema_version=DEFAULT_MATERIALIZATION_SCHEMA_VERSION,
            )
        payload = build_payload(discovery_input, load_policy(args.policy))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote discovery dry-run output to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
