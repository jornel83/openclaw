#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer run-summary fixture from an orchestration-cycle artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_job_orchestration_lib import (
    load_optimizer_job_orchestration_cycle,
    validate_optimizer_run_summary_payload,
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
    / "optimizer-run-summary.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-job-orchestration-cycle", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        cycle_payload = load_optimizer_job_orchestration_cycle(
            args.input_job_orchestration_cycle
        )
        run_summary = cycle_payload.get("artifacts", {}).get("runSummary")
        if not isinstance(run_summary, dict):
            raise ValueError(
                "optimizer job orchestration cycle does not embed artifacts.runSummary"
            )
        validate_optimizer_run_summary_payload(run_summary)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(run_summary, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer run summary to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
