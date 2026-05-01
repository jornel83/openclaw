#!/usr/bin/env python3
"""
Validate that the shared topic-candidates fixture matches the current discovery artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DISCOVERY_INPUT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)
DEFAULT_SHARED_INPUT = ROOT / "skills" / "autotiktok" / "fixtures" / "topic-candidates.fixture.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery-input", type=Path, default=DEFAULT_DISCOVERY_INPUT)
    parser.add_argument("--shared-input", type=Path, default=DEFAULT_SHARED_INPUT)
    args = parser.parse_args()

    try:
        discovery = load_json(args.discovery_input)
        shared = load_json(args.shared_input)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    discovery_candidates = discovery.get("candidates")
    shared_candidates = shared.get("candidates")
    if not isinstance(discovery_candidates, list) or not isinstance(shared_candidates, list):
        print("[ERROR] both inputs must contain a `candidates` list")
        return 1

    if discovery_candidates != shared_candidates:
        print("[ERROR] shared topic-candidates fixture is out of sync with discovery output")
        print(
            "Run: python3 skills/autotiktok/scripts/sync_shared_candidates_fixture.py"
        )
        return 1

    generated_from = shared.get("generatedFrom", {})
    if generated_from.get("snapshotId") != discovery.get("snapshotId"):
        print("[ERROR] shared fixture generatedFrom.snapshotId does not match discovery snapshotId")
        return 1

    if generated_from.get("policyVersion") != discovery.get("policyVersion"):
        print("[ERROR] shared fixture generatedFrom.policyVersion does not match discovery policyVersion")
        return 1

    print("Shared topic-candidates fixture is aligned with discovery output.")
    print(f"Discovery input: {args.discovery_input}")
    print(f"Shared fixture: {args.shared_input}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
