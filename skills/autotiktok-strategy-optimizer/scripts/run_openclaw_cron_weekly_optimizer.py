#!/usr/bin/env python3
"""
Run the weekly AutoTikTok optimizer job via the standard OpenClaw cron runtime.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from openclaw_cron_job_lib import (
    render_openclaw_cron_job_summary,
    resolve_openclaw_cron_output_path,
    write_openclaw_cron_payload,
)
from optimizer_lib import DEFAULT_POLICY
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)
from run_weekly_optimizer_job import (
    DEFAULT_BACKFILLS,
    DEFAULT_CHALLENGER_INPUT,
    DEFAULT_CONTEXT,
    DEFAULT_PERFORMANCE,
    DEFAULT_RANKING_OUTPUT,
    build_job_run,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_MANIFEST = (
    DEFAULT_ROOT / "fixtures" / "optimizer-input-manifest.sample.json"
)
DEFAULT_WEEKLY_REVIEW_WINDOW = (
    DEFAULT_ROOT / "fixtures" / "optimizer-weekly-review-window.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_INPUT_MANIFEST)
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
    parser.add_argument(
        "--weekly-review-window-input",
        type=Path,
        default=DEFAULT_WEEKLY_REVIEW_WINDOW,
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
    parser.add_argument(
        "--job-run-id",
        default="optimizer-weekly-job-run.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument(
        "--cycle-id",
        default="optimizer-offline-cycle.autotiktok.fixture.2026-04-18.weekly-job",
    )
    parser.add_argument(
        "--eval-run-id",
        default="optimizer-eval-run.autotiktok.fixture.2026-04-18.weekly-job",
    )
    parser.add_argument(
        "--report-id",
        default="daily-review.autotiktok.fixture.2026-04-18.weekly-job",
    )
    parser.add_argument("--generated-at", default="2026-04-18T04:15:00Z")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()

    output_path = resolve_openclaw_cron_output_path(
        explicit_output=args.output,
        output_root=args.output_root,
        job_run_id=args.job_run_id,
    )

    try:
        payload = build_job_run(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"status=error\nerror={exc}", file=sys.stderr)
        return 1

    write_openclaw_cron_payload(payload, output_path=output_path)
    print(render_openclaw_cron_job_summary(payload, output_path=output_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
