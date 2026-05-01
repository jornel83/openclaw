#!/usr/bin/env python3
"""
Helpers for multi-day weekly review window artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from typing import Any

from reward_lib import combined_reward


WEEKLY_REVIEW_WINDOW_SAMPLE_SCHEMA_VERSION = "optimizer-weekly-review-window.sample.v1"
WEEKLY_REVIEW_WINDOW_SCHEMA_VERSION = "optimizer-weekly-review-window.v1"
WEEKLY_REVIEW_WINDOW_SCHEMA_VERSIONS = {
    WEEKLY_REVIEW_WINDOW_SAMPLE_SCHEMA_VERSION,
    WEEKLY_REVIEW_WINDOW_SCHEMA_VERSION,
}


DEFAULT_WEEKLY_WINDOW_SCENARIOS: dict[str, list[dict[str, Any]]] = {
    "promotion_default": [
        {
            "windowId": "2026-04-13",
            "observedAt": "2026-04-13T08:00:00Z",
            "champion": {
                "topicReward": 0.639,
                "performanceReward": 0.475,
                "performanceWeight": 0.1,
                "combinedReward": 0.6226,
                "dupRate": 0.34,
                "typeCoverage": 0.96,
                "executableRate": 0.65,
                "holdoutDelta": 0.002,
                "postCoverageRate": 0.61,
            },
            "challengers": {
                "search-priority-default": {
                    "topicReward": 0.667,
                    "performanceReward": 0.482,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.6485,
                    "dupRate": 0.334,
                    "typeCoverage": 0.97,
                    "executableRate": 0.656,
                    "holdoutDelta": 0.004,
                    "postCoverageRate": 0.62,
                    "daysObserved": 5,
                    "hardGatePass": True,
                },
                "scale-default": {
                    "topicReward": 0.646,
                    "performanceReward": 0.478,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.6292,
                    "dupRate": 0.39,
                    "typeCoverage": 0.87,
                    "executableRate": 0.58,
                    "holdoutDelta": -0.016,
                    "postCoverageRate": 0.61,
                    "daysObserved": 5,
                    "hardGatePass": False,
                },
            },
        },
        {
            "windowId": "2026-04-14",
            "observedAt": "2026-04-14T08:00:00Z",
            "champion": {
                "topicReward": 0.646,
                "performanceReward": 0.482,
                "performanceWeight": 0.1,
                "combinedReward": 0.6296,
                "dupRate": 0.337,
                "typeCoverage": 0.98,
                "executableRate": 0.659,
                "holdoutDelta": 0.004,
                "postCoverageRate": 0.64,
            },
            "challengers": {
                "search-priority-default": {
                    "topicReward": 0.675,
                    "performanceReward": 0.496,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.6571,
                    "dupRate": 0.333,
                    "typeCoverage": 0.99,
                    "executableRate": 0.664,
                    "holdoutDelta": 0.009,
                    "postCoverageRate": 0.65,
                    "daysObserved": 6,
                    "hardGatePass": True,
                },
                "scale-default": {
                    "topicReward": 0.652,
                    "performanceReward": 0.486,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.6354,
                    "dupRate": 0.387,
                    "typeCoverage": 0.875,
                    "executableRate": 0.584,
                    "holdoutDelta": -0.012,
                    "postCoverageRate": 0.63,
                    "daysObserved": 6,
                    "hardGatePass": False,
                },
            },
        },
        {
            "windowId": "2026-04-15",
            "observedAt": "2026-04-15T08:00:00Z",
            "champion": {
                "holdoutDelta": 0.006,
            },
            "challengers": {
                "search-priority-default": {},
                "scale-default": {},
            },
        },
    ],
    "rollback_guardrail": [
        {
            "windowId": "2026-04-13",
            "observedAt": "2026-04-13T08:00:00Z",
            "champion": {
                "topicReward": 0.606,
                "performanceReward": 0.44,
                "performanceWeight": 0.1,
                "combinedReward": 0.5894,
                "dupRate": 0.351,
                "typeCoverage": 0.93,
                "executableRate": 0.62,
                "holdoutDelta": -0.035,
                "postCoverageRate": 0.58,
            },
            "challengers": {
                "search-priority-default": {
                    "topicReward": 0.615,
                    "performanceReward": 0.446,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.5981,
                    "dupRate": 0.345,
                    "typeCoverage": 0.95,
                    "executableRate": 0.626,
                    "holdoutDelta": -0.004,
                    "postCoverageRate": 0.6,
                    "daysObserved": 5,
                    "hardGatePass": True,
                },
                "scale-default": {
                    "topicReward": 0.61,
                    "performanceReward": 0.442,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.5932,
                    "dupRate": 0.392,
                    "typeCoverage": 0.85,
                    "executableRate": 0.575,
                    "holdoutDelta": -0.02,
                    "postCoverageRate": 0.58,
                    "daysObserved": 5,
                    "hardGatePass": False,
                },
            },
        },
        {
            "windowId": "2026-04-14",
            "observedAt": "2026-04-14T08:00:00Z",
            "champion": {
                "topicReward": 0.609,
                "performanceReward": 0.444,
                "performanceWeight": 0.1,
                "combinedReward": 0.5925,
                "dupRate": 0.349,
                "typeCoverage": 0.94,
                "executableRate": 0.622,
                "holdoutDelta": -0.032,
                "postCoverageRate": 0.59,
            },
            "challengers": {
                "search-priority-default": {
                    "topicReward": 0.618,
                    "performanceReward": 0.449,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.6011,
                    "dupRate": 0.344,
                    "typeCoverage": 0.955,
                    "executableRate": 0.628,
                    "holdoutDelta": 0.0,
                    "postCoverageRate": 0.61,
                    "daysObserved": 6,
                    "hardGatePass": True,
                },
                "scale-default": {
                    "topicReward": 0.612,
                    "performanceReward": 0.445,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.5953,
                    "dupRate": 0.389,
                    "typeCoverage": 0.852,
                    "executableRate": 0.578,
                    "holdoutDelta": -0.018,
                    "postCoverageRate": 0.59,
                    "daysObserved": 6,
                    "hardGatePass": False,
                },
            },
        },
        {
            "windowId": "2026-04-15",
            "observedAt": "2026-04-15T08:00:00Z",
            "champion": {
                "topicReward": 0.603,
                "performanceReward": 0.438,
                "performanceWeight": 0.1,
                "combinedReward": 0.5865,
                "dupRate": 0.353,
                "typeCoverage": 0.93,
                "executableRate": 0.619,
                "holdoutDelta": -0.041,
                "postCoverageRate": 0.57,
            },
            "challengers": {
                "search-priority-default": {
                    "topicReward": 0.621,
                    "performanceReward": 0.455,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.6044,
                    "dupRate": 0.343,
                    "typeCoverage": 0.958,
                    "executableRate": 0.632,
                    "holdoutDelta": 0.002,
                    "postCoverageRate": 0.62,
                    "daysObserved": 7,
                    "hardGatePass": True,
                },
                "scale-default": {
                    "topicReward": 0.614,
                    "performanceReward": 0.447,
                    "performanceWeight": 0.1,
                    "combinedReward": 0.5973,
                    "dupRate": 0.388,
                    "typeCoverage": 0.854,
                    "executableRate": 0.58,
                    "holdoutDelta": -0.017,
                    "postCoverageRate": 0.59,
                    "daysObserved": 7,
                    "hardGatePass": False,
                },
            },
        },
    ],
}


DEFAULT_REWARD_HORIZON_ADJUSTMENTS = {
    "t+1": {
        "topicReward": -0.006,
        "performanceReward": -0.004,
        "holdoutDelta": -0.004,
        "postCoverageRate": -0.02,
    },
    "t+3": {
        "topicReward": 0.0,
        "performanceReward": 0.0,
        "holdoutDelta": 0.0,
        "postCoverageRate": 0.0,
    },
    "t+7": {
        "topicReward": 0.009,
        "performanceReward": 0.006,
        "holdoutDelta": 0.006,
        "postCoverageRate": 0.012,
    },
}


def _round(value: float) -> float:
    return round(float(value), 6)


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


def _clamp_zero_one(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _max_consecutive_true(flags: list[bool]) -> int:
    best = 0
    current = 0
    for flag in flags:
        if flag:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _load_reward_horizons(policy: dict[str, Any]) -> list[dict[str, Any]]:
    reward_horizons = policy["weeklyPromotion"].get("rewardHorizons")
    if not isinstance(reward_horizons, list) or not reward_horizons:
        raise ValueError(
            "optimizer policy weeklyPromotion.rewardHorizons must be a non-empty list"
        )
    horizons: list[dict[str, Any]] = []
    for item in reward_horizons:
        horizon_id = str(item["horizonId"])
        horizons.append(
            {
                "horizonId": horizon_id,
                "windowDays": int(item["windowDays"]),
                "weight": float(item["weight"]),
                "required": bool(item.get("required", False)),
            }
        )
    return horizons


def _base_champion_observation(report: dict[str, Any]) -> dict[str, Any]:
    topic = report["topicRewardBreakdown"]
    combined = report["combinedRewardBreakdown"]
    return {
        "topicReward": float(topic["topicReward"]),
        "performanceReward": float(combined["performanceReward"] or 0.0),
        "performanceWeight": float(combined["performanceWeight"] or 0.0),
        "combinedReward": float(combined["combinedReward"]),
        "dupRate": float(topic["dupRate"]),
        "typeCoverage": float(topic["typeCoverage"]),
        "executableRate": float(topic["executableRate"]),
        "holdoutDelta": 0.0,
        "postCoverageRate": float(combined.get("postCoverageRate") or 0.0),
    }


def _base_challenger_observations(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for item in report.get("shadowLeaderboard", []):
        rows[item["profileId"]] = {
            "profileId": item["profileId"],
            "topicReward": float(item["topicReward"]),
            "performanceReward": float(item["performanceReward"] or 0.0),
            "performanceWeight": float(item["performanceWeight"] or 0.0),
            "combinedReward": float(item["combinedReward"]),
            "dupRate": float(item["dupRate"]),
            "typeCoverage": float(item["typeCoverage"]),
            "executableRate": float(item["executableRate"]),
            "holdoutDelta": float(item["holdoutDelta"]),
            "postCoverageRate": float(item.get("postCoverageRate") or 0.0),
            "daysObserved": int(item["daysObserved"]),
            "hardGatePass": bool(item["hardGatePass"]),
            "sourceInputKind": item.get("sourceInputKind"),
            "notes": item.get("notes"),
        }
    return rows


def _merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(base)
    payload.update(overrides)
    return payload


def _available_reward_horizons(
    reward_horizons: list[dict[str, Any]],
    *,
    window_id: str,
    generated_at: str,
) -> tuple[int, list[dict[str, Any]]]:
    generated_date = _parse_iso_datetime(generated_at).date()
    window_date = _parse_iso_date(window_id)
    days_since_window_start = max(0, (generated_date - window_date).days)
    available = [
        item
        for item in reward_horizons
        if days_since_window_start >= int(item["windowDays"])
    ]
    if not available:
        raise ValueError(
            f"weekly review window `{window_id}` does not satisfy any configured reward horizon"
        )
    return days_since_window_start, available


def _build_reward_horizon_breakdown(
    observation: dict[str, Any],
    *,
    available_horizons: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    configured_weight_total = sum(float(item["weight"]) for item in available_horizons)
    if configured_weight_total <= 0:
        raise ValueError("configured reward horizon weights must sum to a positive value")

    breakdown: list[dict[str, Any]] = []
    weighted_topic_reward = 0.0
    weighted_performance_reward = 0.0
    weighted_holdout_delta = 0.0
    weighted_post_coverage_rate = 0.0

    for horizon in available_horizons:
        horizon_id = str(horizon["horizonId"])
        adjustments = DEFAULT_REWARD_HORIZON_ADJUSTMENTS.get(
            horizon_id, DEFAULT_REWARD_HORIZON_ADJUSTMENTS["t+3"]
        )
        effective_weight = float(horizon["weight"]) / configured_weight_total
        topic_reward = _clamp_zero_one(
            float(observation["topicReward"]) + float(adjustments["topicReward"])
        )
        performance_reward = _clamp_zero_one(
            float(observation["performanceReward"])
            + float(adjustments["performanceReward"])
        )
        holdout_delta = _round(
            float(observation["holdoutDelta"]) + float(adjustments["holdoutDelta"])
        )
        post_coverage_rate = _clamp_zero_one(
            float(observation["postCoverageRate"])
            + float(adjustments["postCoverageRate"])
        )
        performance_weight = _round(float(observation["performanceWeight"]))
        combined = _round(
            combined_reward(topic_reward, performance_reward, performance_weight)
        )
        breakdown.append(
            {
                "horizonId": horizon_id,
                "windowDays": int(horizon["windowDays"]),
                "configuredWeight": _round(horizon["weight"]),
                "effectiveWeight": _round(effective_weight),
                "required": bool(horizon["required"]),
                "topicReward": _round(topic_reward),
                "performanceReward": _round(performance_reward),
                "performanceWeight": performance_weight,
                "combinedReward": combined,
                "holdoutDelta": holdout_delta,
                "postCoverageRate": _round(post_coverage_rate),
            }
        )
        weighted_topic_reward += effective_weight * topic_reward
        weighted_performance_reward += effective_weight * performance_reward
        weighted_holdout_delta += effective_weight * holdout_delta
        weighted_post_coverage_rate += effective_weight * post_coverage_rate

    performance_weight = _round(float(observation["performanceWeight"]))
    weighted_topic_reward = _round(weighted_topic_reward)
    weighted_performance_reward = _round(weighted_performance_reward)
    return breakdown, {
        "topicReward": weighted_topic_reward,
        "performanceReward": weighted_performance_reward,
        "performanceWeight": performance_weight,
        "combinedReward": _round(
            combined_reward(
                weighted_topic_reward,
                weighted_performance_reward,
                performance_weight,
            )
        ),
        "dupRate": _round(observation["dupRate"]),
        "typeCoverage": _round(observation["typeCoverage"]),
        "executableRate": _round(observation["executableRate"]),
        "holdoutDelta": _round(weighted_holdout_delta),
        "postCoverageRate": _round(weighted_post_coverage_rate),
        "rewardHorizonBreakdown": breakdown,
    }


def _build_window_entries(
    report: dict[str, Any],
    scenario_id: str,
    *,
    generated_at: str,
    reward_horizons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scenario = DEFAULT_WEEKLY_WINDOW_SCENARIOS.get(scenario_id)
    if scenario is None:
        raise ValueError(f"unknown weekly review scenario: {scenario_id}")
    base_champion = _base_champion_observation(report)
    base_challengers = _base_challenger_observations(report)
    entries = []
    for item in scenario:
        days_since_window_start, available_horizons = _available_reward_horizons(
            reward_horizons,
            window_id=item["windowId"],
            generated_at=generated_at,
        )
        champion = _merge(base_champion, item.get("champion", {}))
        _, champion_summary = _build_reward_horizon_breakdown(
            champion,
            available_horizons=available_horizons,
        )
        challengers = []
        for profile_id, base_row in base_challengers.items():
            challenger = _merge(base_row, item.get("challengers", {}).get(profile_id, {}))
            challenger_breakdown, challenger_summary = _build_reward_horizon_breakdown(
                challenger,
                available_horizons=available_horizons,
            )
            challengers.append(
                {
                    "profileId": challenger["profileId"],
                    **challenger_summary,
                    "combinedRewardDelta": _round(
                        float(challenger_summary["combinedReward"])
                        - float(champion_summary["combinedReward"])
                    ),
                    "daysObserved": int(challenger["daysObserved"]),
                    "hardGatePass": bool(challenger["hardGatePass"]),
                    "sourceInputKind": challenger.get("sourceInputKind"),
                    "notes": challenger.get("notes"),
                    "rewardHorizonBreakdown": challenger_breakdown,
                }
            )
        entries.append(
            {
                "windowId": item["windowId"],
                "observedAt": item["observedAt"],
                "daysSinceWindowStart": days_since_window_start,
                "availableRewardHorizonIds": [
                    str(horizon["horizonId"]) for horizon in available_horizons
                ],
                "sourceReportId": report["reportId"],
                "championObservation": champion_summary,
                "challengerObservations": challengers,
            }
        )
    return entries


def _aggregate_champion(
    windows: list[dict[str, Any]],
    policy: dict[str, Any],
    reward_horizons: list[dict[str, Any]],
) -> dict[str, Any]:
    weekly = policy["weeklyPromotion"]
    observations = [window["championObservation"] for window in windows]
    combined_rewards = [float(item["combinedReward"]) for item in observations]
    holdouts = [float(item["holdoutDelta"]) for item in observations]
    dup_rates = [float(item["dupRate"]) for item in observations]
    type_coverages = [float(item["typeCoverage"]) for item in observations]
    executable_rates = [float(item["executableRate"]) for item in observations]
    post_coverages = [float(item["postCoverageRate"]) for item in observations]
    rollback_holdout_floor = float(weekly.get("rollbackHoldoutFloor", -0.03))
    rollback_reward_floor = float(weekly.get("rollbackCombinedRewardFloor", 0.6))
    holdout_breach_flags = [value < rollback_holdout_floor for value in holdouts]
    reward_breach_flags = [value < rollback_reward_floor for value in combined_rewards]
    holdout_breaches = sum(1 for value in holdouts if value < rollback_holdout_floor)
    reward_breaches = sum(
        1 for value in combined_rewards if value < rollback_reward_floor
    )
    horizon_summaries = []
    for horizon in reward_horizons:
        horizon_id = str(horizon["horizonId"])
        horizon_rows = []
        for window in windows:
            for item in window["championObservation"]["rewardHorizonBreakdown"]:
                if item["horizonId"] == horizon_id:
                    horizon_rows.append(item)
        if not horizon_rows:
            continue
        horizon_summaries.append(
            {
                "horizonId": horizon_id,
                "windowDays": int(horizon["windowDays"]),
                "configuredWeight": _round(horizon["weight"]),
                "required": bool(horizon["required"]),
                "availableWindowCount": len(horizon_rows),
                "avgCombinedReward": _round(
                    sum(float(item["combinedReward"]) for item in horizon_rows)
                    / len(horizon_rows)
                ),
                "minCombinedReward": _round(
                    min(float(item["combinedReward"]) for item in horizon_rows)
                ),
                "avgHoldoutDelta": _round(
                    sum(float(item["holdoutDelta"]) for item in horizon_rows)
                    / len(horizon_rows)
                ),
                "minHoldoutDelta": _round(
                    min(float(item["holdoutDelta"]) for item in horizon_rows)
                ),
                "avgPostCoverageRate": _round(
                    sum(float(item["postCoverageRate"]) for item in horizon_rows)
                    / len(horizon_rows)
                ),
            }
        )
    return {
        "windowCount": len(observations),
        "avgCombinedReward": _round(sum(combined_rewards) / len(combined_rewards)),
        "minCombinedReward": _round(min(combined_rewards)),
        "avgHoldoutDelta": _round(sum(holdouts) / len(holdouts)),
        "minHoldoutDelta": _round(min(holdouts)),
        "avgDupRate": _round(sum(dup_rates) / len(dup_rates)),
        "avgTypeCoverage": _round(sum(type_coverages) / len(type_coverages)),
        "avgExecutableRate": _round(sum(executable_rates) / len(executable_rates)),
        "avgPostCoverageRate": _round(sum(post_coverages) / len(post_coverages)),
        "holdoutFloorBreachCount": holdout_breaches,
        "combinedRewardFloorBreachCount": reward_breaches,
        "maxConsecutiveHoldoutFloorBreachDays": _max_consecutive_true(
            holdout_breach_flags
        ),
        "maxConsecutiveCombinedRewardFloorBreachDays": _max_consecutive_true(
            reward_breach_flags
        ),
        "rewardHorizonSummaries": horizon_summaries,
    }


def _aggregate_challengers(
    windows: list[dict[str, Any]],
    reward_horizons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for window in windows:
        for item in window["challengerObservations"]:
            grouped.setdefault(item["profileId"], []).append(item)
    rows = []
    for profile_id, items in grouped.items():
        combined_rewards = [float(item["combinedReward"]) for item in items]
        reward_deltas = [float(item["combinedRewardDelta"]) for item in items]
        holdouts = [float(item["holdoutDelta"]) for item in items]
        dup_rates = [float(item["dupRate"]) for item in items]
        type_coverages = [float(item["typeCoverage"]) for item in items]
        executable_rates = [float(item["executableRate"]) for item in items]
        post_coverages = [float(item["postCoverageRate"]) for item in items]
        reward_horizon_summaries = []
        for horizon in reward_horizons:
            horizon_id = str(horizon["horizonId"])
            horizon_rows = []
            for item in items:
                for breakdown in item["rewardHorizonBreakdown"]:
                    if breakdown["horizonId"] == horizon_id:
                        horizon_rows.append(breakdown)
            if not horizon_rows:
                continue
            champion_horizon_rows = []
            for window in windows:
                matching = [
                    breakdown
                    for breakdown in window["championObservation"]["rewardHorizonBreakdown"]
                    if breakdown["horizonId"] == horizon_id
                ]
                champion_horizon_rows.extend(matching)
            reward_horizon_summaries.append(
                {
                    "horizonId": horizon_id,
                    "windowDays": int(horizon["windowDays"]),
                    "configuredWeight": _round(horizon["weight"]),
                    "required": bool(horizon["required"]),
                    "availableWindowCount": len(horizon_rows),
                    "avgCombinedReward": _round(
                        sum(float(item["combinedReward"]) for item in horizon_rows)
                        / len(horizon_rows)
                    ),
                    "avgCombinedRewardDelta": _round(
                        (
                            sum(float(item["combinedReward"]) for item in horizon_rows)
                            / len(horizon_rows)
                        )
                        - (
                            sum(float(item["combinedReward"]) for item in champion_horizon_rows)
                            / len(champion_horizon_rows)
                        )
                    ),
                    "minHoldoutDelta": _round(
                        min(float(item["holdoutDelta"]) for item in horizon_rows)
                    ),
                    "avgHoldoutDelta": _round(
                        sum(float(item["holdoutDelta"]) for item in horizon_rows)
                        / len(horizon_rows)
                    ),
                    "avgPostCoverageRate": _round(
                        sum(float(item["postCoverageRate"]) for item in horizon_rows)
                        / len(horizon_rows)
                    ),
                }
            )

        rows.append(
            {
                "profileId": profile_id,
                "windowCount": len(items),
                "avgCombinedReward": _round(sum(combined_rewards) / len(combined_rewards)),
                "avgCombinedRewardDelta": _round(
                    sum(reward_deltas) / len(reward_deltas)
                ),
                "minHoldoutDelta": _round(min(holdouts)),
                "avgHoldoutDelta": _round(sum(holdouts) / len(holdouts)),
                "avgDupRate": _round(sum(dup_rates) / len(dup_rates)),
                "avgTypeCoverage": _round(sum(type_coverages) / len(type_coverages)),
                "avgExecutableRate": _round(
                    sum(executable_rates) / len(executable_rates)
                ),
                "avgPostCoverageRate": _round(
                    sum(post_coverages) / len(post_coverages)
                ),
                "daysObservedMax": max(int(item["daysObserved"]) for item in items),
                "winningDayCount": sum(
                    1 for item in items if float(item["combinedRewardDelta"]) > 0.0
                ),
                "hardGatePassDayCount": sum(
                    1 for item in items if bool(item["hardGatePass"])
                ),
                "rewardHorizonSummaries": reward_horizon_summaries,
            }
        )
    rows.sort(key=lambda item: item["avgCombinedRewardDelta"], reverse=True)
    return rows


def build_weekly_review_window_payload(
    *,
    report: dict[str, Any],
    policy: dict[str, Any],
    review_window_id: str,
    generated_at: str,
    scenario_id: str,
) -> dict[str, Any]:
    reward_horizons = _load_reward_horizons(policy)
    windows = _build_window_entries(
        report,
        scenario_id,
        generated_at=generated_at,
        reward_horizons=reward_horizons,
    )
    aggregated_champion = _aggregate_champion(windows, policy, reward_horizons)
    challenger_summaries = _aggregate_challengers(windows, reward_horizons)
    best_challenger_profile_id = (
        challenger_summaries[0]["profileId"] if challenger_summaries else None
    )
    weekly = policy["weeklyPromotion"]
    rollback_min_breach_days = int(weekly.get("rollbackMinBreachDays", 2))
    rollback_critical_holdout_floor = float(
        weekly.get("rollbackCriticalHoldoutFloor", -0.04)
    )
    rollback_critical_reward_floor = float(
        weekly.get("rollbackCriticalCombinedRewardFloor", 0.58)
    )
    rollback_reason_codes: list[str] = []
    if aggregated_champion["holdoutFloorBreachCount"] > 0:
        rollback_reason_codes.append("holdout_floor_breach_days")
    if aggregated_champion["combinedRewardFloorBreachCount"] > 0:
        rollback_reason_codes.append("combined_reward_floor_breach_days")
    if aggregated_champion["minHoldoutDelta"] <= rollback_critical_holdout_floor:
        rollback_reason_codes.append("critical_holdout_regression")
    if aggregated_champion["minCombinedReward"] <= rollback_critical_reward_floor:
        rollback_reason_codes.append("critical_reward_regression")
    rollback_eligible = bool(rollback_reason_codes)
    rollback_triggered = (
        aggregated_champion["holdoutFloorBreachCount"] >= rollback_min_breach_days
        or aggregated_champion["combinedRewardFloorBreachCount"]
        >= rollback_min_breach_days
        or "critical_holdout_regression" in rollback_reason_codes
        or "critical_reward_regression" in rollback_reason_codes
    )
    rollback_severity = "none"
    if rollback_reason_codes:
        rollback_severity = "watch"
    if rollback_triggered:
        rollback_severity = "warning"
    if any(
        code in rollback_reason_codes
        for code in ("critical_holdout_regression", "critical_reward_regression")
    ):
        rollback_severity = "critical"
    ranking_context = report.get("rankingContext", {})
    candidate_source = report.get("candidateSource", {})
    report_generated_from = report.get("generatedFrom", {})
    return {
        "schemaVersion": WEEKLY_REVIEW_WINDOW_SAMPLE_SCHEMA_VERSION,
        "reviewWindowId": review_window_id,
        "generatedAt": generated_at,
        "profileId": report["profileId"],
        "championProfileSelection": ranking_context,
        "championCandidateSource": candidate_source,
        "generatedFrom": {
            "policyVersion": policy["schemaVersion"],
            "sourceReportSchemaVersion": report["schemaVersion"],
            "sourceReportId": report["reportId"],
            "sourceReportCount": len(windows),
            "scenarioId": scenario_id,
            "rankingRunId": report.get("runId"),
            "rankingSnapshotId": report_generated_from.get("rankingSnapshotId"),
            "requestedProfileId": ranking_context.get("requestedProfileId"),
            "resolvedProfileId": ranking_context.get("resolvedProfileId"),
            "profileSelectionSource": ranking_context.get("selectionSource"),
            "stageMode": ranking_context.get("stageMode"),
            "candidateSourceKind": candidate_source.get("sourceKind"),
            "candidateInputSchemaVersion": candidate_source.get("inputSchemaVersion"),
            "candidateSourceSnapshotId": candidate_source.get("sourceSnapshotId"),
            "candidateSourcePolicyVersion": candidate_source.get("sourcePolicyVersion"),
            "challengerInputKind": report_generated_from.get("challengerInputKind"),
            "rankingOptimizerContractId": report_generated_from.get(
                "rankingOptimizerContractId"
            ),
            "rankingOptimizerContractVersion": report_generated_from.get(
                "rankingOptimizerContractVersion"
            ),
            "rankingOptimizerContractValidationMode": report_generated_from.get(
                "rankingOptimizerContractValidationMode"
            ),
            "rankingOptimizerContractValidated": bool(
                report_generated_from.get("rankingOptimizerContractValidated", False)
            ),
            "rankingOptimizerSurfaceSource": report_generated_from.get(
                "rankingOptimizerSurfaceSource"
            ),
            "rankingOptimizerDeprecationPhase": report_generated_from.get(
                "rankingOptimizerDeprecationPhase"
            ),
            "rankingOptimizerCanonicalSurface": report_generated_from.get(
                "rankingOptimizerCanonicalSurface"
            ),
            "rankingOptimizerDeprecatedTopLevelFields": list(
                report_generated_from.get(
                    "rankingOptimizerDeprecatedTopLevelFields", []
                )
            ),
            "rankingOptimizerNextHardFailContractVersion": report_generated_from.get(
                "rankingOptimizerNextHardFailContractVersion"
            ),
            "rankingOptimizerCompatApplied": bool(
                report_generated_from.get("rankingOptimizerCompatApplied", False)
            ),
            "rankingOptimizerCompatAliasesApplied": list(
                report_generated_from.get(
                    "rankingOptimizerCompatAliasesApplied", []
                )
            ),
        },
        "rewardHorizonPolicy": {
            "aggregationMethod": "weighted_horizon_average",
            "horizons": [
                {
                    "horizonId": item["horizonId"],
                    "windowDays": int(item["windowDays"]),
                    "configuredWeight": _round(item["weight"]),
                    "required": bool(item["required"]),
                }
                for item in reward_horizons
            ],
        },
        "windows": windows,
        "aggregatedChampion": aggregated_champion,
        "challengerSummaries": challenger_summaries,
        "rollbackSignals": {
            "rollbackHoldoutFloor": float(weekly.get("rollbackHoldoutFloor", -0.03)),
            "rollbackCombinedRewardFloor": float(
                weekly.get("rollbackCombinedRewardFloor", 0.6)
            ),
            "rollbackMinBreachDays": rollback_min_breach_days,
            "rollbackCriticalHoldoutFloor": rollback_critical_holdout_floor,
            "rollbackCriticalCombinedRewardFloor": rollback_critical_reward_floor,
            "rollbackEligible": rollback_eligible,
            "rollbackSeverity": rollback_severity,
            "rollbackReasonCodes": rollback_reason_codes,
            "holdoutFloorBreachCount": aggregated_champion["holdoutFloorBreachCount"],
            "combinedRewardFloorBreachCount": aggregated_champion[
                "combinedRewardFloorBreachCount"
            ],
            "maxConsecutiveHoldoutFloorBreachDays": aggregated_champion[
                "maxConsecutiveHoldoutFloorBreachDays"
            ],
            "maxConsecutiveCombinedRewardFloorBreachDays": aggregated_champion[
                "maxConsecutiveCombinedRewardFloorBreachDays"
            ],
            "rollbackTriggered": rollback_triggered,
        },
        "bestChallengerProfileId": best_challenger_profile_id,
    }


def validate_weekly_review_window_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in WEEKLY_REVIEW_WINDOW_SCHEMA_VERSIONS:
        raise ValueError(
            "weekly review window payload must declare a supported schemaVersion"
        )
    if not isinstance(payload.get("reviewWindowId"), str) or not payload["reviewWindowId"]:
        raise ValueError("weekly review window payload must declare reviewWindowId")
    if not isinstance(payload.get("generatedAt"), str) or not payload["generatedAt"]:
        raise ValueError("weekly review window payload must declare generatedAt")
    reward_horizon_policy = payload.get("rewardHorizonPolicy")
    if not isinstance(reward_horizon_policy, dict):
        raise ValueError(
            "weekly review window payload must declare rewardHorizonPolicy"
        )
    horizons = reward_horizon_policy.get("horizons")
    if not isinstance(horizons, list) or not horizons:
        raise ValueError(
            "weekly review window payload must declare rewardHorizonPolicy.horizons"
        )
    windows = payload.get("windows")
    if not isinstance(windows, list) or not windows:
        raise ValueError("weekly review window payload must declare windows")
    for window in windows:
        if not isinstance(window.get("availableRewardHorizonIds"), list) or not window[
            "availableRewardHorizonIds"
        ]:
            raise ValueError(
                "weekly review window windows must declare availableRewardHorizonIds"
            )
        champion = window.get("championObservation")
        if not isinstance(champion, dict):
            raise ValueError(
                "weekly review window windows must declare championObservation"
            )
        champion_breakdown = champion.get("rewardHorizonBreakdown")
        if not isinstance(champion_breakdown, list) or not champion_breakdown:
            raise ValueError(
                "weekly review window championObservation must declare rewardHorizonBreakdown"
            )
        for item in window.get("challengerObservations", []):
            if not isinstance(item.get("rewardHorizonBreakdown"), list) or not item[
                "rewardHorizonBreakdown"
            ]:
                raise ValueError(
                    "weekly review window challenger observations must declare rewardHorizonBreakdown"
                )
    aggregated_champion = payload.get("aggregatedChampion")
    if not isinstance(aggregated_champion, dict):
        raise ValueError(
            "weekly review window payload must declare aggregatedChampion"
        )
    if not isinstance(aggregated_champion.get("rewardHorizonSummaries"), list):
        raise ValueError(
            "weekly review window aggregatedChampion must declare rewardHorizonSummaries"
        )
    challenger_summaries = payload.get("challengerSummaries")
    if not isinstance(challenger_summaries, list):
        raise ValueError(
            "weekly review window payload must declare challengerSummaries"
        )
    for item in challenger_summaries:
        if not isinstance(item.get("rewardHorizonSummaries"), list):
            raise ValueError(
                "weekly review window challenger summaries must declare rewardHorizonSummaries"
            )
    rollback_signals = payload.get("rollbackSignals")
    if not isinstance(rollback_signals, dict):
        raise ValueError("weekly review window payload must declare rollbackSignals")
    if not isinstance(rollback_signals.get("rollbackReasonCodes"), list):
        raise ValueError(
            "weekly review window rollbackSignals must declare rollbackReasonCodes"
        )
    if rollback_signals.get("rollbackSeverity") not in {"none", "watch", "warning", "critical"}:
        raise ValueError(
            "weekly review window rollbackSignals must declare a supported rollbackSeverity"
        )
