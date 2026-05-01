#!/usr/bin/env python3
"""
Build an optimizer eval-run artifact from an offline cycle or directly from runtime inputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_eval_lib import build_optimizer_eval_run_payload
from run_offline_optimizer_cycle import (
    DEFAULT_BACKFILLS,
    DEFAULT_CHALLENGER_INPUT,
    DEFAULT_CONTEXT,
    DEFAULT_PERFORMANCE,
    DEFAULT_RANKING_OUTPUT,
    build_cycle_payload,
)
from reward_lib import load_json
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)
from optimizer_lib import DEFAULT_POLICY


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-eval-run.sample.json"


def build_eval_run(args: argparse.Namespace) -> dict[str, object]:
    if args.input_offline_cycle is not None:
        offline_cycle_payload = load_json(args.input_offline_cycle)
    else:
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
            include_weekly_promotion=args.include_weekly_promotion,
        )
        offline_cycle_payload = build_cycle_payload(offline_cycle_args)
    return build_optimizer_eval_run_payload(
        offline_cycle_payload=offline_cycle_payload,
        eval_run_id=args.eval_run_id,
        generated_at=args.generated_at,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-offline-cycle", type=Path)
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
        "--cycle-id", default="optimizer-offline-cycle.autotiktok.fixture.2026-04-15"
    )
    parser.add_argument(
        "--eval-run-id", default="optimizer-eval-run.autotiktok.fixture.2026-04-15"
    )
    parser.add_argument(
        "--report-id", default="daily-review.autotiktok.fixture.2026-04-15"
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--include-weekly-promotion",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "--exclude-weekly-promotion", dest="include_weekly_promotion", action="store_false"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_eval_run(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer eval run to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
