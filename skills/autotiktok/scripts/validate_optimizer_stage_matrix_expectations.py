#!/usr/bin/env python3
"""
Validate intended cross-stage optimizer behavior from the committed optimizer stage matrix.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "optimizer-stage-matrix.sample.json"
)


EXPECTED_PROFILES = {
    "growth": "growth-default",
    "scale": "scale-default",
    "search_priority": "search-priority-default",
}

EXPECTED_TOP_TOPIC_ID = "tp_evergreen_ad_mistakes_001"
EXPECTED_REJECTED_TOPIC_ID = "tp_trend_wired_earbuds_001"
EXPECTED_SHADOW_LEADER_IDS = {
    "growth": "search-priority-default",
    "scale": "search-priority-default",
    "search_priority": "scale-default",
}
EXPECTED_RECOMMENDATION_KINDS = {
    "growth": "observe_challenger",
    "scale": "observe_challenger",
    "search_priority": "keep_champion",
}
MAX_PERFORMANCE_WEIGHT = 0.15


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    try:
        payload = load_json(MATRIX_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors: list[str] = []
    expect(
        payload.get("schemaVersion") == "optimizer-stage-matrix.v1",
        "optimizer stage matrix has unexpected schemaVersion",
        errors,
    )

    generated_from = payload.get("generatedFrom", {})
    expect(
        generated_from.get("optimizerPolicyVersion") == "optimizer-policy.v1",
        "optimizer stage matrix should carry optimizer-policy.v1 provenance",
        errors,
    )

    stages = payload.get("stages")
    if not isinstance(stages, list) or not stages:
        print("[ERROR] optimizer stage matrix must include a non-empty `stages` list")
        return 1

    stage_map = {stage.get("stageMode"): stage for stage in stages if isinstance(stage, dict)}
    expect(
        set(stage_map.keys()) == set(EXPECTED_PROFILES.keys()),
        "optimizer stage matrix does not include the expected stage modes",
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
        expect(
            stage.get("shadowLeaderProfileId") == EXPECTED_SHADOW_LEADER_IDS[stage_mode],
            f"{stage_mode} should keep {EXPECTED_SHADOW_LEADER_IDS[stage_mode]} as the shadow leader",
            errors,
        )
        expect(
            stage.get("recommendationKind") == EXPECTED_RECOMMENDATION_KINDS[stage_mode],
            f"{stage_mode} should stay in {EXPECTED_RECOMMENDATION_KINDS[stage_mode]} mode during daily optimization",
            errors,
        )
        expect(
            stage.get("topTopicId") == EXPECTED_TOP_TOPIC_ID,
            f"{stage_mode} should keep {EXPECTED_TOP_TOPIC_ID} as the champion topic",
            errors,
        )
        rejected_topic_ids = stage.get("rejectedTopicIds", [])
        expect(
            isinstance(rejected_topic_ids, list) and EXPECTED_REJECTED_TOPIC_ID in rejected_topic_ids,
            f"{stage_mode} should keep {EXPECTED_REJECTED_TOPIC_ID} rejected",
            errors,
        )
        performance_weight = float(stage.get("performanceWeight", 0.0))
        expect(
            0.0 < performance_weight <= MAX_PERFORMANCE_WEIGHT,
            f"{stage_mode} performanceWeight must stay within (0, {MAX_PERFORMANCE_WEIGHT}]",
            errors,
        )
        combined_reward = float(stage.get("combinedReward", 0.0))
        topic_reward = float(stage.get("topicReward", 0.0))
        expect(
            0.0 <= topic_reward <= 1.0,
            f"{stage_mode} topicReward must stay within [0, 1]",
            errors,
        )
        expect(
            0.0 <= combined_reward <= 1.0,
            f"{stage_mode} combinedReward must stay within [0, 1]",
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
            top_topic_ids == {EXPECTED_TOP_TOPIC_ID},
            "optimizer stage matrix should keep the same top topic across stage modes",
            errors,
        )

        combined_rewards = {
            round(float(growth.get("combinedReward", 0.0)), 6),
            round(float(scale.get("combinedReward", 0.0)), 6),
            round(float(search.get("combinedReward", 0.0)), 6),
        }
        expect(
            len(combined_rewards) == 1,
            "current optimizer stage matrix should keep combinedReward stable across stage modes",
            errors,
        )

        topic_rewards = {
            round(float(growth.get("topicReward", 0.0)), 6),
            round(float(scale.get("topicReward", 0.0)), 6),
            round(float(search.get("topicReward", 0.0)), 6),
        }
        expect(
            len(topic_rewards) == 1,
            "current optimizer stage matrix should keep topicReward stable across stage modes",
            errors,
        )

        growth_p1 = int(growth.get("priorityCounts", {}).get("P1", 0))
        scale_p1 = int(scale.get("priorityCounts", {}).get("P1", 0))
        search_p1 = int(search.get("priorityCounts", {}).get("P1", 0))
        expect(
            scale_p1 >= growth_p1,
            "scale mode should not reduce the number of P1 topics compared with growth",
            errors,
        )
        expect(
            search_p1 >= growth_p1,
            "search_priority mode should not reduce the number of P1 topics compared with growth",
            errors,
        )

    if errors:
        print("[ERROR] optimizer stage matrix does not satisfy intended stage-mode expectations:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Optimizer stage matrix satisfies intended stage-mode expectations.")
    print(f"Optimizer matrix: {MATRIX_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
