#!/usr/bin/env python3
"""
Validate the shared ranking fixtures used by the AutoTikTok ranking skill.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from ranking_lib import DEFAULT_DISCOVERY_ARTIFACT, DEFAULT_RUBRIC, validate_rubric

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "autotiktok" / "fixtures"

EXPECTED_PROFILE_IDS = {
    "growth-default",
    "scale-default",
    "search-priority-default",
}

EXPECTED_STAGE_MODES = {"growth", "scale", "search_priority"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_candidates(path: Path) -> list[str]:
    errors: list[str] = []
    payload = load_json(path)
    if not isinstance(payload, dict):
        return ["candidate fixture must be an object"]
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return ["candidate fixture must include a non-empty `candidates` list"]
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"candidates[{index}] must be an object")
            continue
        if candidate.get("schemaVersion") != "topic-candidate.v1":
            errors.append(f"candidates[{index}] has unexpected schemaVersion")
        if candidate.get("topicType") not in {"trend", "search", "evergreen"}:
            errors.append(f"candidates[{index}] has invalid topicType")
        if candidate.get("recommendedMode") not in {"growth", "search", "series"}:
            errors.append(f"candidates[{index}] has invalid recommendedMode")
    return errors


def validate_context_payload(payload: Any, prefix: str = "scoring context") -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{prefix} must be an object"]
    if payload.get("schemaVersion") != "scoring-context.v1":
        errors.append(f"{prefix} has unexpected schemaVersion")
    if payload.get("stageMode") not in EXPECTED_STAGE_MODES:
        errors.append(f"{prefix} has invalid stageMode")
    for key in ("acceptedFormats", "availableAssetTypes", "activeContentBuckets"):
        if not isinstance(payload.get(key), list):
            errors.append(f"{prefix} field `{key}` must be a list")
    return errors


def validate_context(path: Path) -> list[str]:
    return validate_context_payload(load_json(path))


def validate_context_matrix(path: Path) -> list[str]:
    errors: list[str] = []
    payload = load_json(path)
    if not isinstance(payload, dict):
        return ["scoring context matrix must be an object"]
    stages = payload.get("stages")
    if not isinstance(stages, list) or not stages:
        return ["scoring context matrix must include a non-empty `stages` list"]

    seen_stage_modes: set[str] = set()
    for index, stage_entry in enumerate(stages):
        if not isinstance(stage_entry, dict):
            errors.append(f"stages[{index}] must be an object")
            continue
        stage_mode = stage_entry.get("stageMode")
        if stage_mode not in EXPECTED_STAGE_MODES:
            errors.append(f"stages[{index}] has invalid stageMode `{stage_mode}`")
        elif stage_mode in seen_stage_modes:
            errors.append(f"stages[{index}] duplicates stageMode `{stage_mode}`")
        else:
            seen_stage_modes.add(stage_mode)
        context = stage_entry.get("context")
        errors.extend(
            validate_context_payload(context, prefix=f"stages[{index}].context")
        )
        if isinstance(context, dict) and context.get("stageMode") != stage_mode:
            errors.append(
                f"stages[{index}].context.stageMode must match stages[{index}].stageMode"
            )

    missing_stage_modes = EXPECTED_STAGE_MODES - seen_stage_modes
    if missing_stage_modes:
        errors.append(
            "scoring context matrix missing stage modes: "
            + ", ".join(sorted(missing_stage_modes))
        )
    return errors


def validate_profiles(path: Path) -> list[str]:
    errors: list[str] = []
    payload = load_json(path)
    if not isinstance(payload, dict):
        return ["scoring profiles fixture must be an object"]
    profiles = payload.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        return ["scoring profiles fixture must include a non-empty `profiles` list"]

    seen_ids: set[str] = set()
    expected_weight_keys = {
        "demand",
        "fit",
        "rewrite",
        "series",
        "searchCapture",
        "longform",
        "feasibility",
        "competition",
    }
    for index, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            errors.append(f"profiles[{index}] must be an object")
            continue
        profile_id = profile.get("profileId")
        if profile.get("schemaVersion") != "scoring-profile.v1":
            errors.append(f"profiles[{index}] has unexpected schemaVersion")
        if profile_id not in EXPECTED_PROFILE_IDS:
            errors.append(f"profiles[{index}] has invalid profileId `{profile_id}`")
        elif profile_id in seen_ids:
            errors.append(f"profiles[{index}] duplicates profileId `{profile_id}`")
        else:
            seen_ids.add(profile_id)
        weights = profile.get("weights")
        if not isinstance(weights, dict):
            errors.append(f"profiles[{index}].weights must be an object")
            continue
        missing = expected_weight_keys - set(weights.keys())
        if missing:
            errors.append(
                f"profiles[{index}].weights missing keys: {', '.join(sorted(missing))}"
            )
            continue
        total = 0.0
        for key in expected_weight_keys:
            value = weights.get(key)
            if not isinstance(value, (int, float)):
                errors.append(f"profiles[{index}].weights.{key} must be numeric")
                continue
            total += float(value)
        if not math.isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6):
            errors.append(f"profiles[{index}].weights must sum to 1.0, got {total:.6f}")
    return errors


def validate_rubric_file(path: Path) -> list[str]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        return ["feature rubric fixture must be an object"]
    return validate_rubric(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_DISCOVERY_ARTIFACT,
    )
    parser.add_argument(
        "--context",
        type=Path,
        default=DEFAULT_ROOT / "scoring-context.fixture.json",
    )
    parser.add_argument(
        "--context-matrix",
        type=Path,
        default=DEFAULT_ROOT / "scoring-context-matrix.fixture.json",
    )
    parser.add_argument(
        "--profiles",
        type=Path,
        default=DEFAULT_ROOT / "scoring-profiles.fixture.json",
    )
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    args = parser.parse_args()

    try:
        errors = [
            *validate_candidates(args.candidates),
            *validate_context(args.context),
            *validate_context_matrix(args.context_matrix),
            *validate_profiles(args.profiles),
            *validate_rubric_file(args.rubric),
        ]
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Ranking fixture validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Ranking fixtures are valid.")
    print(f"Candidates fixture: {args.candidates}")
    print(f"Context fixture: {args.context}")
    print(f"Context matrix fixture: {args.context_matrix}")
    print(f"Profiles fixture: {args.profiles}")
    print(f"Feature rubric: {args.rubric}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
