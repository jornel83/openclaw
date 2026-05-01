#!/usr/bin/env python3
"""
Generate a mock weekly promotion decision from a daily review report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_lib import DEFAULT_POLICY, build_weekly_decision, load_policy
from reward_lib import load_json

DEFAULT_DAILY_REVIEW = Path(__file__).resolve().parents[1] / "fixtures" / "daily-review.sample.json"
DEFAULT_WEEKLY_REVIEW_WINDOW = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily-review-input", type=Path)
    parser.add_argument("--weekly-review-window-input", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        input_path = (
            args.weekly_review_window_input
            or args.daily_review_input
            or DEFAULT_WEEKLY_REVIEW_WINDOW
        )
        payload = build_weekly_decision(load_json(input_path), load_policy(args.policy))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote weekly promotion decision to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
