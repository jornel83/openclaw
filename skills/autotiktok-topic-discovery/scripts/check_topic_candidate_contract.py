#!/usr/bin/env python3
"""
Validate a topic-candidate artifact against the discovery-owned contract.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_INPUT = (
    Path(__file__).resolve().parents[2]
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)

REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "topicId",
    "topicFingerprint",
    "topicTitle",
    "topicSummary",
    "topicType",
    "sourceType",
    "sourceRef",
    "keywords",
    "contentAngle",
    "recommendedMode",
    "expandability",
    "freshnessWindow",
    "searchEvidence",
    "executionProfile",
    "executionNotes",
}

REQUIRED_SEARCH_EVIDENCE = {
    "seedQueries",
    "relatedQueries",
    "contentGapQueries",
    "searchIntentType",
    "searchPersistenceHint",
}

REQUIRED_EXECUTION_PROFILE = {
    "recommendedFormats",
    "requiredAssets",
    "requiredCapabilities",
    "productionComplexity",
    "dependencyRisk",
    "fastTurnaround",
}


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def validate_candidates(payload: dict[str, Any]) -> tuple[list[str], Counter[str]]:
    errors: list[str] = []
    type_counter: Counter[str] = Counter()

    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return ["top-level field `candidates` must be a list"], type_counter

    seen_ids: set[str] = set()
    seen_fingerprints: set[str] = set()

    for index, candidate_raw in enumerate(candidates):
        prefix = f"candidates[{index}]"
        if not isinstance(candidate_raw, dict):
            errors.append(f"{prefix} must be an object")
            continue
        candidate = candidate_raw
        missing = sorted(REQUIRED_TOP_LEVEL - set(candidate.keys()))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
            continue

        topic_id = candidate.get("topicId")
        fingerprint = candidate.get("topicFingerprint")
        topic_type = candidate.get("topicType")
        type_counter[str(topic_type)] += 1

        if topic_id in seen_ids:
            errors.append(f"{prefix}.topicId is duplicated: {topic_id}")
        else:
            seen_ids.add(str(topic_id))

        if fingerprint in seen_fingerprints:
            errors.append(f"{prefix}.topicFingerprint is duplicated: {fingerprint}")
        else:
            seen_fingerprints.add(str(fingerprint))

        if not isinstance(candidate.get("sourceType"), list) or not candidate["sourceType"]:
            errors.append(f"{prefix}.sourceType must be a non-empty list")
        if not isinstance(candidate.get("sourceRef"), list) or not candidate["sourceRef"]:
            errors.append(f"{prefix}.sourceRef must be a non-empty list")
        if len(candidate.get("sourceRef", [])) != len(set(candidate.get("sourceRef", []))):
            errors.append(f"{prefix}.sourceRef must not contain duplicates")
        if len(candidate.get("contentAngle", [])) != len(set(candidate.get("contentAngle", []))):
            errors.append(f"{prefix}.contentAngle must not contain duplicates")

        expandability = candidate.get("expandability")
        if not isinstance(expandability, (int, float)) or not 0 <= float(expandability) <= 1:
            errors.append(f"{prefix}.expandability must be between 0 and 1")

        search_evidence = candidate.get("searchEvidence")
        if not isinstance(search_evidence, dict):
            errors.append(f"{prefix}.searchEvidence must be an object")
        else:
            missing_search = sorted(REQUIRED_SEARCH_EVIDENCE - set(search_evidence.keys()))
            if missing_search:
                errors.append(
                    f"{prefix}.searchEvidence missing fields: {', '.join(missing_search)}"
                )
            for key in ("seedQueries", "relatedQueries", "contentGapQueries"):
                if not isinstance(search_evidence.get(key), list):
                    errors.append(f"{prefix}.searchEvidence.{key} must be a list")

        execution_profile = candidate.get("executionProfile")
        if not isinstance(execution_profile, dict):
            errors.append(f"{prefix}.executionProfile must be an object")
        else:
            missing_execution = sorted(
                REQUIRED_EXECUTION_PROFILE - set(execution_profile.keys())
            )
            if missing_execution:
                errors.append(
                    f"{prefix}.executionProfile missing fields: {', '.join(missing_execution)}"
                )
            complexity = execution_profile.get("productionComplexity")
            if not isinstance(complexity, (int, float)) or not 0 <= float(complexity) <= 1:
                errors.append(
                    f"{prefix}.executionProfile.productionComplexity must be between 0 and 1"
                )
            for key in ("recommendedFormats", "requiredAssets", "requiredCapabilities"):
                if not isinstance(execution_profile.get(key), list):
                    errors.append(f"{prefix}.executionProfile.{key} must be a list")

    return errors, type_counter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to a topic-candidate fixture JSON file.",
    )
    args = parser.parse_args()

    try:
        payload = _require_dict(_load_json(args.input), "fixture payload")
        errors, type_counter = validate_candidates(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Topic-candidate contract validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    candidate_count = len(_require_list(payload["candidates"], "candidates"))
    print("Topic-candidate contract is valid.")
    print(f"Candidates: {candidate_count}")
    print(
        "Topic types: "
        + ", ".join(f"{topic_type}={count}" for topic_type, count in sorted(type_counter.items()))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
