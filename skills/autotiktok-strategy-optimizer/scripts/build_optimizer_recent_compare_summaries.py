#!/usr/bin/env python3
"""
Build dashboard-facing recent optimizer compare summaries from compare-batch artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_dashboard_aggregate_lib import (
    build_optimizer_recent_compare_summaries_payload,
    load_optimizer_compare_batch_inputs,
    load_optimizer_orchestration_cycle_inputs,
    validate_optimizer_recent_compare_summaries_payload,
)
from optimizer_job_shadow_compare_lib import validate_optimizer_job_shadow_compare_batch_payload


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMPARE_BATCH = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch.sample.json"
)
DEFAULT_CYCLE = (
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
    / "optimizer-recent-compare-summaries.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-job-shadow-compare-batch",
        action="append",
        type=Path,
        dest="input_compare_batches",
    )
    parser.add_argument(
        "--input-job-orchestration-cycle",
        action="append",
        type=Path,
        dest="input_job_orchestration_cycles",
    )
    parser.add_argument(
        "--aggregate-id",
        default="optimizer-recent-compare-summaries.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument("--generated-at", default="2026-04-19T03:38:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    compare_batch_paths = args.input_compare_batches or [DEFAULT_COMPARE_BATCH]
    cycle_paths = args.input_job_orchestration_cycles or [DEFAULT_CYCLE]

    try:
        compare_batch_payloads = load_optimizer_compare_batch_inputs(compare_batch_paths)
        cycle_payloads = load_optimizer_orchestration_cycle_inputs(cycle_paths)
        for cycle_payload in cycle_payloads:
            embedded_batch = cycle_payload.get("artifacts", {}).get("shadowCompareBatch")
            if embedded_batch is None:
                continue
            if not isinstance(embedded_batch, dict):
                raise ValueError(
                    "optimizer job orchestration cycle embedded shadowCompareBatch must be an object"
                )
            validate_optimizer_job_shadow_compare_batch_payload(embedded_batch)
            compare_batch_payloads.append(embedded_batch)
        payload = build_optimizer_recent_compare_summaries_payload(
            aggregate_id=args.aggregate_id,
            generated_at=args.generated_at,
            compare_batch_payloads=compare_batch_payloads,
        )
        validate_optimizer_recent_compare_summaries_payload(payload)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer recent compare summaries to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
