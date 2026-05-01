#!/usr/bin/env python3
"""
Run the daily optimizer orchestration job from manifest/bundle/runtime inputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_eval_lib import build_optimizer_eval_run_payload
from optimizer_job_run_lib import build_optimizer_job_run_payload
from run_offline_optimizer_cycle import (
    DEFAULT_BACKFILLS,
    DEFAULT_CHALLENGER_INPUT,
    DEFAULT_CONTEXT,
    DEFAULT_PERFORMANCE,
    DEFAULT_RANKING_OUTPUT,
    build_cycle_payload,
)
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)
from optimizer_lib import DEFAULT_POLICY


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-daily-job-run.sample.json"


def build_job_run(args: argparse.Namespace) -> dict[str, object]:
    offline_cycle_args = argparse.Namespace(
        input_manifest=args.input_manifest,
        input_bundle=args.input_bundle,
        ranking_input=args.ranking_input,
        context_input=args.context_input,
        backfills_input=args.backfills_input,
        performance_input=args.performance_input,
        challenger_input=args.challenger_input,
        policy=args.policy,
        ranking_contract_version=args.ranking_contract_version,
        ranking_contract_validation_mode=args.ranking_contract_validation_mode,
        cycle_id=args.cycle_id,
        report_id=args.report_id,
        generated_at=args.generated_at,
        include_weekly_promotion=False,
    )
    offline_cycle_payload = build_cycle_payload(offline_cycle_args)
    eval_run_payload = build_optimizer_eval_run_payload(
        offline_cycle_payload=offline_cycle_payload,
        eval_run_id=args.eval_run_id,
        generated_at=args.generated_at,
    )
    return build_optimizer_job_run_payload(
        job_run_id=args.job_run_id,
        job_kind="daily_optimizer_job",
        generated_at=args.generated_at,
        offline_cycle_payload=offline_cycle_payload,
        eval_run_payload=eval_run_payload,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--input-bundle", type=Path)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING_OUTPUT)
    parser.add_argument("--context-input", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--backfills-input", type=Path, default=DEFAULT_BACKFILLS)
    parser.add_argument("--performance-input", type=Path, default=DEFAULT_PERFORMANCE)
    parser.add_argument(
        "--challenger-input",
        dest="challenger_input",
        type=Path,
        default=DEFAULT_CHALLENGER_INPUT,
    )
    parser.add_argument("--challenger-adjustments", dest="challenger_input", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--ranking-contract-version",
        default=RANKING_OPTIMIZER_CONTRACT_VERSION,
    )
    parser.add_argument(
        "--ranking-contract-validation-mode",
        default=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        choices=(
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
        ),
    )
    parser.add_argument(
        "--job-run-id",
        default="optimizer-daily-job-run.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument(
        "--cycle-id",
        default="optimizer-offline-cycle.autotiktok.fixture.2026-04-18.daily-job",
    )
    parser.add_argument(
        "--eval-run-id",
        default="optimizer-eval-run.autotiktok.fixture.2026-04-18.daily-job",
    )
    parser.add_argument(
        "--report-id",
        default="daily-review.autotiktok.fixture.2026-04-18.daily-job",
    )
    parser.add_argument("--generated-at", default="2026-04-18T04:00:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_job_run(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote daily optimizer job run to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
