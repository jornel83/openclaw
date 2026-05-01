#!/usr/bin/env python3
"""
Generate a mock daily review report for the AutoTikTok optimizer skill.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPT_DIR = DEFAULT_ROOT.parent / "autotiktok" / "scripts"
if str(SHARED_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPT_DIR))

from daily_review_service import build_daily_review_report
from optimizer_input_adapters import (
    load_daily_review_runtime_inputs,
)
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)
from optimizer_lib import DEFAULT_POLICY

DEFAULT_RANKING_OUTPUT = (
    DEFAULT_ROOT.parent / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
DEFAULT_CHALLENGER_INPUT = (
    DEFAULT_ROOT / "fixtures" / "challenger-evaluation-run.sample.json"
)


def build_report(args: argparse.Namespace) -> dict[str, object]:
    inputs = load_daily_review_runtime_inputs(
        input_manifest=args.input_manifest,
        input_bundle=args.input_bundle,
        ranking_input=args.ranking_input,
        context_input=args.context_input,
        backfills_input=args.backfills_input,
        performance_input=args.performance_input,
        challenger_input=args.challenger_input,
        policy_input=args.policy,
        contract_version=args.ranking_contract_version,
        validation_mode=args.ranking_contract_validation_mode,
    )
    return build_daily_review_report(
        inputs,
        report_id=args.report_id,
        generated_at=args.generated_at,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--input-bundle", type=Path)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING_OUTPUT)
    parser.add_argument(
        "--context-input",
        type=Path,
        default=DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json",
    )
    parser.add_argument(
        "--backfills-input",
        type=Path,
        default=DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-run.sample.json",
    )
    parser.add_argument(
        "--performance-input",
        type=Path,
        default=DEFAULT_ROOT / "fixtures" / "post-performance-signal-run.sample.json",
    )
    parser.add_argument(
        "--challenger-input",
        dest="challenger_input",
        type=Path,
        default=DEFAULT_CHALLENGER_INPUT,
    )
    parser.add_argument(
        "--challenger-adjustments",
        dest="challenger_input",
        type=Path,
    )
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
    parser.add_argument("--report-id", default="daily-review.autotiktok.fixture.2026-04-15")
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = build_report(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote daily review report to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
