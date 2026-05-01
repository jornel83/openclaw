#!/usr/bin/env python3
"""
Validate committed stage-specific weekly promotion fixtures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GROWTH_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)
SCALE_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.scale.sample.json"
)
SEARCH_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.search-priority.sample.json"
)
GROWTH_WEEKLY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.sample.json"
)
SCALE_WEEKLY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.scale.sample.json"
)
SEARCH_WEEKLY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.search-priority.sample.json"
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    try:
        growth_window = load_json(GROWTH_WINDOW)
        scale_window = load_json(SCALE_WINDOW)
        search_window = load_json(SEARCH_WINDOW)
        growth_weekly = load_json(GROWTH_WEEKLY)
        scale_weekly = load_json(SCALE_WEEKLY)
        search_weekly = load_json(SEARCH_WEEKLY)

        require(
            growth_window["championProfileSelection"]["stageMode"] == "growth",
            "growth weekly window should keep championProfileSelection.stageMode=growth",
        )
        require(
            scale_window["championProfileSelection"]["stageMode"] == "scale",
            "scale weekly window should keep championProfileSelection.stageMode=scale",
        )
        require(
            search_window["championProfileSelection"]["stageMode"] == "search_priority",
            "search weekly window should keep championProfileSelection.stageMode=search_priority",
        )

        require(
            growth_weekly["decision"] == "promote",
            "growth weekly fixture should still promote the lead challenger",
        )
        require(
            growth_weekly["gateSummary"]["weeklyStagePolicyId"] == "growth_weekly_gate",
            "growth weekly fixture should resolve growth_weekly_gate",
        )

        for payload, expected_policy_id, expected_stage in (
            (scale_weekly, "scale_weekly_gate", "scale"),
            (search_weekly, "search_priority_weekly_gate", "search_priority"),
        ):
            require(
                payload["decision"] == "keep_champion",
                f"{expected_stage} weekly fixture should keep champion under stricter stage gates",
            )
            require(
                payload["gateSummary"]["weeklyStageMode"] == expected_stage,
                f"{expected_stage} weekly fixture should record weeklyStageMode={expected_stage}",
            )
            require(
                payload["gateSummary"]["weeklyStagePolicyId"] == expected_policy_id,
                f"{expected_stage} weekly fixture should resolve {expected_policy_id}",
            )
            failed_gate_ids = payload["promotionCandidateReviews"][0]["failedGateIds"]
            require(
                "minimum_average_reward_delta" in failed_gate_ids,
                f"{expected_stage} weekly fixture should fail minimum_average_reward_delta",
            )
            require(
                "minimum_average_holdout_delta" in failed_gate_ids,
                f"{expected_stage} weekly fixture should fail minimum_average_holdout_delta",
            )

        require(
            growth_weekly["sourceReviewWindowId"] == growth_window["reviewWindowId"],
            "growth weekly fixture must point at growth weekly window",
        )
        require(
            scale_weekly["sourceReviewWindowId"] == scale_window["reviewWindowId"],
            "scale weekly fixture must point at scale weekly window",
        )
        require(
            search_weekly["sourceReviewWindowId"] == search_window["reviewWindowId"],
            "search weekly fixture must point at search weekly window",
        )

        print("Weekly stage policy fixtures are aligned.")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
