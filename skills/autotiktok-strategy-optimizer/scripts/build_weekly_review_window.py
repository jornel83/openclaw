#!/usr/bin/env python3
"""
Build a multi-day weekly review window fixture from a daily review report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_lib import DEFAULT_POLICY, load_policy
from optimizer_weekly_window_lib import build_weekly_review_window_payload
from reward_lib import load_json


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DAILY_REVIEW = DEFAULT_ROOT / "fixtures" / "daily-review.sample.json"
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-weekly-review-window.sample.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily-review-input", type=Path, default=DEFAULT_DAILY_REVIEW)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--review-window-id",
        default="optimizer-weekly-review-window.autotiktok.fixture.2026-04-20",
    )
    parser.add_argument("--generated-at", default="2026-04-20T07:30:00Z")
    parser.add_argument(
        "--scenario",
        default="promotion_default",
        choices=("promotion_default", "rollback_guardrail"),
    )
    parser.add_argument(
        "--stage-mode",
        choices=("growth", "scale", "search_priority"),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_weekly_review_window_payload(
            report=load_json(args.daily_review_input),
            policy=load_policy(args.policy),
            review_window_id=args.review_window_id,
            generated_at=args.generated_at,
            scenario_id=args.scenario,
        )
        if args.stage_mode is not None:
            payload.setdefault("championProfileSelection", {})["stageMode"] = (
                args.stage_mode
            )
            payload.setdefault("generatedFrom", {})["stageMode"] = args.stage_mode
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote weekly review window to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
