#!/usr/bin/env python3
"""
Sync the shared topic-candidates fixture from a discovery artifact.
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
DEFAULT_OUTPUT = ROOT / "skills" / "autotiktok" / "fixtures" / "topic-candidates.fixture.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_shared_fixture(discovery_payload: dict[str, Any]) -> dict[str, Any]:
    candidates = discovery_payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("discovery payload must include a non-empty `candidates` list")
    return {
        "fixtureSetVersion": "topic-candidates.fixture.v1",
        "description": "Topic candidates derived from the current discovery sample output for ranking and workflow replay.",
        "generatedFrom": {
            "schemaVersion": discovery_payload.get("schemaVersion"),
            "policyVersion": discovery_payload.get("policyVersion"),
            "snapshotId": discovery_payload.get("snapshotId"),
            "sourceArtifact": "skills/autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json",
        },
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery-input", type=Path, default=DEFAULT_DISCOVERY_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_shared_fixture(load_json(args.discovery_input))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote shared topic-candidates fixture to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
