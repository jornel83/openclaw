#!/usr/bin/env python3
"""
Compute TopicReward, PerformanceReward, and CombinedReward for AutoTikTok evaluation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import json
from typing import Any

from reward_lib import (
    clamp_zero_one,
    combined_reward,
    load_json,
    load_policy,
    performance_reward,
    topic_reward,
)
from optimizer_lib import DEFAULT_POLICY


def parse_inline_topic_metrics(args: argparse.Namespace) -> dict[str, Any] | None:
    inline_fields = ("hit3", "ndcg10", "hit10", "novelty", "type_coverage", "executable_rate", "dup_rate")
    if not any(getattr(args, field) is not None for field in inline_fields):
        return None
    required_map = {
        "Hit@3": args.hit3,
        "NDCG@10": args.ndcg10,
        "Hit@10": args.hit10,
        "Novelty": args.novelty,
        "TypeCoverage": args.type_coverage,
        "ExecutableRate": args.executable_rate,
        "DupRate": args.dup_rate,
    }
    missing = [name for name, value in required_map.items() if value is None]
    if missing:
        raise ValueError(
            "inline topic metrics require all topic inputs; missing " + ", ".join(missing)
        )
    return required_map


def parse_inline_performance_metrics(args: argparse.Namespace) -> dict[str, Any] | None:
    inline_fields = ("view_lift", "retention_proxy", "share_save_proxy", "follow_conversion_proxy")
    if not any(getattr(args, field) is not None for field in inline_fields):
        return None
    if args.view_lift is None:
        raise ValueError("inline performance metrics require --view-lift")
    return {
        "ViewLift": args.view_lift,
        "RetentionProxy": args.retention_proxy,
        "ShareSaveProxy": args.share_save_proxy,
        "FollowConversionProxy": args.follow_conversion_proxy,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic-input", type=Path, help="JSON file with topic-layer metrics.")
    parser.add_argument(
        "--performance-input",
        type=Path,
        help="JSON file with performance-layer metrics.",
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--performance-weight", type=float, default=0.0)
    parser.add_argument("--hit3", type=float)
    parser.add_argument("--ndcg10", type=float)
    parser.add_argument("--hit10", type=float)
    parser.add_argument("--novelty", type=float)
    parser.add_argument("--type-coverage", type=float)
    parser.add_argument("--executable-rate", type=float)
    parser.add_argument("--dup-rate", type=float)
    parser.add_argument("--view-lift", type=float)
    parser.add_argument("--retention-proxy", type=float)
    parser.add_argument("--share-save-proxy", type=float)
    parser.add_argument("--follow-conversion-proxy", type=float)
    args = parser.parse_args()

    try:
        topic_metrics = (
            load_json(args.topic_input)
            if args.topic_input
            else parse_inline_topic_metrics(args)
        )
        if topic_metrics is None:
            raise ValueError("provide --topic-input or the inline topic metric flags")

        performance_metrics = (
            load_json(args.performance_input)
            if args.performance_input
            else parse_inline_performance_metrics(args)
        )
        policy = load_policy(args.policy)

        topic_score = topic_reward(topic_metrics, policy=policy)
        performance_score = (
            performance_reward(performance_metrics, policy=policy) if performance_metrics is not None else 0.0
        )
        performance_weight = clamp_zero_one("performanceWeight", float(args.performance_weight))
        if performance_metrics is None:
            performance_weight = 0.0

        combined = combined_reward(topic_score, performance_score if performance_metrics is not None else None, performance_weight)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(json.dumps(
        {
            "topicReward": round(topic_score, 6),
            "performanceReward": round(performance_score, 6),
            "performanceWeight": round(performance_weight, 6),
            "combinedReward": round(combined, 6),
        },
        ensure_ascii=True,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
