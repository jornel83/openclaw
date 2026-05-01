#!/usr/bin/env python3
"""
Shared reward helpers for the AutoTikTok optimizer skill.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "config" / "optimizer-policy.v1.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def clamp_zero_one(name: str, value: float) -> float:
    if not 0 <= value <= 1:
        raise ValueError(f"metric `{name}` must be between 0 and 1, got {value}")
    return value


def metric_value(payload: dict[str, Any], name: str, required: bool = True) -> float:
    raw = payload.get(name)
    if raw is None:
        if required:
            raise ValueError(f"missing metric `{name}`")
        return 0.0
    if not isinstance(raw, (int, float)):
        raise ValueError(f"metric `{name}` must be numeric")
    return float(raw)


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    payload = load_json(path)
    if payload.get("schemaVersion") != "optimizer-policy.v1":
        raise ValueError("optimizer policy has unexpected schemaVersion")
    return payload


def topic_reward(metrics: dict[str, Any], policy: dict[str, Any] | None = None) -> float:
    active_policy = load_policy() if policy is None else policy
    weights = active_policy["topicRewardWeights"]
    hit3 = clamp_zero_one("Hit@3", metric_value(metrics, "Hit@3"))
    ndcg10 = clamp_zero_one("NDCG@10", metric_value(metrics, "NDCG@10"))
    hit10 = clamp_zero_one("Hit@10", metric_value(metrics, "Hit@10"))
    novelty = clamp_zero_one("Novelty", metric_value(metrics, "Novelty"))
    type_coverage = clamp_zero_one("TypeCoverage", metric_value(metrics, "TypeCoverage"))
    executable_rate = clamp_zero_one(
        "ExecutableRate", metric_value(metrics, "ExecutableRate")
    )
    dup_rate = clamp_zero_one("DupRate", metric_value(metrics, "DupRate"))
    return (
        float(weights["Hit@3"]) * hit3
        + float(weights["NDCG@10"]) * ndcg10
        + float(weights["Hit@10"]) * hit10
        + float(weights["Novelty"]) * novelty
        + float(weights["TypeCoverage"]) * type_coverage
        + float(weights["ExecutableRate"]) * executable_rate
        - float(weights["DupRatePenalty"]) * dup_rate
    )


def performance_reward(metrics: dict[str, Any], policy: dict[str, Any] | None = None) -> float:
    active_policy = load_policy() if policy is None else policy
    weights = active_policy["performanceRewardWeights"]
    view_lift = clamp_zero_one("ViewLift", metric_value(metrics, "ViewLift"))
    retention = clamp_zero_one(
        "RetentionProxy", metric_value(metrics, "RetentionProxy", required=False)
    )
    share_save = clamp_zero_one(
        "ShareSaveProxy", metric_value(metrics, "ShareSaveProxy", required=False)
    )
    follow_conversion = clamp_zero_one(
        "FollowConversionProxy",
        metric_value(metrics, "FollowConversionProxy", required=False),
    )
    if all(
        metrics.get(key) is None
        for key in ("RetentionProxy", "ShareSaveProxy", "FollowConversionProxy")
    ):
        return view_lift
    return (
        float(weights["ViewLift"]) * view_lift
        + float(weights["RetentionProxy"]) * retention
        + float(weights["ShareSaveProxy"]) * share_save
        + float(weights["FollowConversionProxy"]) * follow_conversion
    )


def combined_reward(topic_score: float, performance_score: float | None, performance_weight: float) -> float:
    weight = clamp_zero_one("performanceWeight", performance_weight)
    perf = 0.0 if performance_score is None else performance_score
    if performance_score is None:
        weight = 0.0
    return topic_score * (1 - weight) + perf * weight
