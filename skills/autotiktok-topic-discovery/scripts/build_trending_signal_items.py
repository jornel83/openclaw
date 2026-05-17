#!/usr/bin/env python3
"""
Build metadata-only synthetic discovery signalItems from an AutoTikTok trending output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trending_discovery_adapter_lib import build_signal_items_from_trending
from trending_discovery_adapter_lib import load_json
from trending_discovery_adapter_lib import normalize_view_filter
from trending_discovery_adapter_lib import SUPPORTED_VIEW_FILTERS


DEFAULT_INPUT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "trending-consolidated-hot.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--snapshot-id")
    parser.add_argument("--schema-version", default="discovery-signal-items.v1")
    parser.add_argument(
        "--view",
        choices=SUPPORTED_VIEW_FILTERS,
        default="all",
        help="Trending view to materialize: absolute_hot, fresh_hot, or both/all.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = build_signal_items_from_trending(
            load_json(args.input),
            snapshot_id=args.snapshot_id,
            schema_version=args.schema_version,
            views=normalize_view_filter(args.view),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote trending signal items to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
