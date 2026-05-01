#!/usr/bin/env python3
"""
Validate the snapshot-materialization fixture used by the AutoTikTok discovery skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from discovery_lib import load_json
from discovery_lib import validate_snapshot_materialization


DEFAULT_INPUT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "discovery-snapshot-materialization.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    try:
        payload = load_json(args.input)
        if not isinstance(payload, dict):
            raise ValueError("snapshot-materialization fixture must be an object")
        errors, type_counter = validate_snapshot_materialization(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Snapshot-materialization fixture validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Snapshot-materialization fixture is valid.")
    print(f"Signal items: {len(payload['signalItems'])}")
    print(
        "Topic types: "
        + ", ".join(f"{topic_type}={count}" for topic_type, count in sorted(type_counter.items()))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
