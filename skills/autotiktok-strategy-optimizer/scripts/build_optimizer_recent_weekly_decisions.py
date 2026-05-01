#!/usr/bin/env python3
"""
Build dashboard-facing recent optimizer weekly decision summaries.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_dashboard_aggregate_lib import (
    build_optimizer_recent_weekly_decisions_payload,
    load_optimizer_orchestration_cycle_inputs,
    validate_optimizer_recent_weekly_decisions_payload,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-orchestration-cycle.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-weekly-decisions.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-job-orchestration-cycle",
        action="append",
        type=Path,
        dest="input_job_orchestration_cycles",
    )
    parser.add_argument(
        "--aggregate-id",
        default="optimizer-recent-weekly-decisions.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument("--generated-at", default="2026-04-19T03:39:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    input_paths = args.input_job_orchestration_cycles or [DEFAULT_INPUT]

    try:
        cycle_payloads = load_optimizer_orchestration_cycle_inputs(input_paths)
        payload = build_optimizer_recent_weekly_decisions_payload(
            aggregate_id=args.aggregate_id,
            generated_at=args.generated_at,
            cycle_payloads=cycle_payloads,
        )
        validate_optimizer_recent_weekly_decisions_payload(payload)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer recent weekly decisions to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
