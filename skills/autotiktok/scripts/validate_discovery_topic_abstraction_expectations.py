#!/usr/bin/env python3
"""
Validate semantic expectations for the committed discovery topic-abstraction output.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    try:
        payload = load_json(DISCOVERY_OUTPUT)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors: list[str] = []
    generated_from = payload.get("generatedFrom", {})
    normalized_signals = payload.get("normalizedSignals", [])
    abstractions = payload.get("topicAbstractions", [])
    candidates = payload.get("candidates", [])
    evidence_bundles = payload.get("evidenceBundles", [])
    merge_groups = payload.get("mergeGroups", [])

    expect(
        generated_from.get("normalizationRuleVersion") == "discovery-normalization.v1",
        "discovery output must declare discovery-normalization.v1",
        errors,
    )
    expect(
        len(normalized_signals) == generated_from.get("signalCount"),
        "normalizedSignals count must match generatedFrom.signalCount",
        errors,
    )
    expect(
        len(abstractions) == generated_from.get("topicAbstractionCount"),
        "topicAbstractions count must match generatedFrom.topicAbstractionCount",
        errors,
    )
    expect(
        len(abstractions) == len(candidates),
        "topicAbstractions count must match candidates count",
        errors,
    )

    abstraction_ids = {
        abstraction.get("topicAbstractionId"): abstraction for abstraction in abstractions if isinstance(abstraction, dict)
    }

    for index, abstraction in enumerate(abstractions):
        prefix = f"topicAbstractions[{index}]"
        normalized_topic_key = abstraction.get("normalizedTopicKey")
        fingerprint_seed = abstraction.get("fingerprintSeed")
        hints = abstraction.get("candidateExpansionHints", {})
        expect(bool(normalized_topic_key), f"{prefix}.normalizedTopicKey must be non-empty", errors)
        expect(bool(fingerprint_seed), f"{prefix}.fingerprintSeed must be non-empty", errors)
        expect(isinstance(hints, dict), f"{prefix}.candidateExpansionHints must be an object", errors)
        expect(
            hints.get("expansionOpportunity") in {
                "search_cluster",
                "angle_series",
                "cross_source",
                "single_thread",
            },
            f"{prefix}.candidateExpansionHints.expansionOpportunity is invalid",
            errors,
        )

    for index, candidate in enumerate(candidates):
        prefix = f"candidates[{index}]"
        abstraction_id = candidate.get("topicAbstractionId")
        abstraction = abstraction_ids.get(abstraction_id)
        expect(
            abstraction is not None,
            f"{prefix}.topicAbstractionId must resolve to topicAbstractions",
            errors,
        )
        if abstraction is None:
            continue
        expect(
            candidate.get("normalizedTopicKey") == abstraction.get("normalizedTopicKey"),
            f"{prefix}.normalizedTopicKey must match its abstraction",
            errors,
        )
        expect(
            candidate.get("fingerprintSeed") == abstraction.get("fingerprintSeed"),
            f"{prefix}.fingerprintSeed must match its abstraction",
            errors,
        )

    for collection_name, entries in (
        ("evidenceBundles", evidence_bundles),
        ("mergeGroups", merge_groups),
    ):
        for index, entry in enumerate(entries):
            abstraction_id = entry.get("topicAbstractionId")
            expect(
                abstraction_id in abstraction_ids,
                f"{collection_name}[{index}].topicAbstractionId must resolve to topicAbstractions",
                errors,
            )

    if errors:
        print("[ERROR] Discovery topic-abstraction expectations failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Discovery topic-abstraction expectations are satisfied.")
    print(f"Discovery output: {DISCOVERY_OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
