#!/usr/bin/env python3
"""
Build an optimizer eval-batch manifest that lists eval-run artifacts to compare.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_eval_batch_lib import (
    COMPARISON_DIMENSIONS,
    OPTIMIZER_EVAL_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSION,
    build_optimizer_eval_batch_manifest_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DAILY_EVAL_RUN = (
    DEFAULT_ROOT / "fixtures" / "optimizer-eval-run-daily.sample.json"
)
DEFAULT_WEEKLY_EVAL_RUN = DEFAULT_ROOT / "fixtures" / "optimizer-eval-run.sample.json"
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-eval-batch-manifest.sample.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-eval-run",
        type=Path,
        action="append",
        help="Explicit eval-run paths. Defaults to the committed daily/weekly comparison fixtures.",
    )
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_EVAL_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_EVAL_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--manifest-id",
        default="optimizer-eval-batch-manifest.autotiktok.fixture.2026-04-15",
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--comparison-dimension",
        default="mode",
        choices=COMPARISON_DIMENSIONS,
    )
    parser.add_argument("--batch-window-label", default="2026-04-15..2026-04-15")
    parser.add_argument("--window-set-purpose")
    parser.add_argument("--window-set-batch-type")
    parser.add_argument(
        "--path-style", choices=("repo", "absolute", "basename"), default="repo"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    eval_run_paths = (
        list(args.input_eval_run)
        if args.input_eval_run
        else [DEFAULT_DAILY_EVAL_RUN, DEFAULT_WEEKLY_EVAL_RUN]
    )
    payload = build_optimizer_eval_batch_manifest_payload(
        eval_run_paths=eval_run_paths,
        schema_version=args.schema_version,
        manifest_id=args.manifest_id,
        generated_at=args.generated_at,
        comparison_dimension=args.comparison_dimension,
        batch_window_label=args.batch_window_label,
        window_set_purpose=args.window_set_purpose,
        window_set_batch_type=args.window_set_batch_type,
        path_style=args.path_style,
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer eval batch manifest to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
