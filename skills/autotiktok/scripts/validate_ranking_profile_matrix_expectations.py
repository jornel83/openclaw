#!/usr/bin/env python3
"""
Validate intended cross-stage ranking behavior from the committed ranking profile matrix.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = (
    ROOT
    / "skills"
    / "autotiktok-topic-ranking"
    / "fixtures"
    / "ranking-profile-matrix.sample.json"
)


EXPECTED_PROFILES = {
    "growth": "growth-default",
    "scale": "scale-default",
    "search_priority": "search-priority-default",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def score_row(stage: dict[str, Any], topic_id: str) -> dict[str, Any] | None:
    for row in stage.get("scores", []):
        if row.get("topicId") == topic_id:
            return row
    return None


def priority_rank(value: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(value, 0)


def main() -> int:
    try:
        payload = load_json(MATRIX_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors: list[str] = []
    expect(
        payload.get("schemaVersion") == "ranking-profile-matrix.v1",
        "ranking profile matrix has unexpected schemaVersion",
        errors,
    )

    stages = payload.get("stages")
    if not isinstance(stages, list) or not stages:
        print("[ERROR] ranking profile matrix must include a non-empty `stages` list")
        return 1

    stage_map = {stage.get("stageMode"): stage for stage in stages if isinstance(stage, dict)}
    expect(
        set(stage_map.keys()) == set(EXPECTED_PROFILES.keys()),
        "ranking profile matrix does not include the expected stage modes",
        errors,
    )

    for stage_mode, profile_id in EXPECTED_PROFILES.items():
        stage = stage_map.get(stage_mode)
        if stage is None:
            continue
        expect(
            stage.get("profileId") == profile_id,
            f"{stage_mode} does not resolve to {profile_id}",
            errors,
        )

    growth = stage_map.get("growth")
    scale = stage_map.get("scale")
    search = stage_map.get("search_priority")

    if growth and scale and search:
        top_topic_ids = {
            growth.get("topTopicId"),
            scale.get("topTopicId"),
            search.get("topTopicId"),
        }
        expect(
            top_topic_ids == {"tp_evergreen_ad_mistakes_001"},
            "top topic is not stable across stage modes",
            errors,
        )

        for stage_mode, stage in (
            ("growth", growth),
            ("scale", scale),
            ("search_priority", search),
        ):
            trend_row = score_row(stage, "tp_trend_wired_earbuds_001")
            expect(
                trend_row is not None and bool(trend_row.get("isRejected")),
                f"trend earbuds topic should stay rejected in {stage_mode}",
                errors,
            )

        growth_search_row = score_row(growth, "tp_search_ai_ad_hooks_001")
        scale_search_row = score_row(scale, "tp_search_ai_ad_hooks_001")
        search_search_row = score_row(search, "tp_search_ai_ad_hooks_001")

        if growth_search_row and scale_search_row and search_search_row:
            expect(
                growth_search_row.get("priorityLevel") == "P2",
                "search-led hook topic should stay P2 in growth mode",
                errors,
            )
            expect(
                scale_search_row.get("priorityLevel") == "P1",
                "search-led hook topic should promote to P1 in scale mode",
                errors,
            )
            expect(
                search_search_row.get("priorityLevel") == "P1",
                "search-led hook topic should promote to P1 in search_priority mode",
                errors,
            )
            expect(
                float(search_search_row.get("scoreTotal", 0.0))
                > float(growth_search_row.get("scoreTotal", 0.0)),
                "search_priority should score the search-led hook topic above growth mode",
                errors,
            )
            expect(
                priority_rank(scale_search_row.get("priorityLevel", ""))
                >= priority_rank(growth_search_row.get("priorityLevel", "")),
                "scale mode should not demote the search-led hook topic below growth priority",
                errors,
            )

        expect(
            int(scale.get("priorityCounts", {}).get("P1", 0))
            >= int(growth.get("priorityCounts", {}).get("P1", 0)),
            "scale mode should not reduce the number of P1 topics compared with growth",
            errors,
        )
        expect(
            int(search.get("priorityCounts", {}).get("P1", 0))
            >= int(growth.get("priorityCounts", {}).get("P1", 0)),
            "search_priority mode should not reduce the number of P1 topics compared with growth",
            errors,
        )

    if errors:
        print("[ERROR] ranking profile matrix does not satisfy intended stage-mode expectations:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Ranking profile matrix satisfies intended stage-mode expectations.")
    print(f"Ranking matrix: {MATRIX_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
