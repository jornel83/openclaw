#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job shadow-compare batch manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_job_shadow_compare_lib import (
    JOB_SHADOW_COMPARISON_DIMENSIONS,
    OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCHEMA_VERSION,
    build_optimizer_job_shadow_compare_batch_manifest_payload,
    validate_optimizer_job_shadow_compare_batch_manifest_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DAILY_COMPARE = (
    DEFAULT_ROOT / "fixtures" / "optimizer-job-shadow-compare.daily.sample.json"
)
DEFAULT_WEEKLY_COMPARE = (
    DEFAULT_ROOT / "fixtures" / "optimizer-job-shadow-compare.weekly.sample.json"
)
DEFAULT_OUTPUT = (
    DEFAULT_ROOT
    / "fixtures"
    / "optimizer-job-shadow-compare-batch-manifest.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-compare-artifact",
        type=Path,
        action="append",
        help="Explicit optimizer-job-shadow-compare artifact paths. Defaults to the committed daily/weekly comparison fixtures.",
    )
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--manifest-id",
        default="optimizer-job-shadow-compare-batch-manifest.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T06:10:00Z")
    parser.add_argument(
        "--comparison-dimension",
        default="candidateSchedulerRolloutIntent",
        choices=JOB_SHADOW_COMPARISON_DIMENSIONS,
    )
    parser.add_argument("--batch-window-label", default="2026-04-18.daily-weekly")
    parser.add_argument(
        "--path-style", choices=("repo", "absolute", "basename"), default="repo"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    compare_paths = (
        list(args.input_compare_artifact)
        if args.input_compare_artifact
        else [DEFAULT_DAILY_COMPARE, DEFAULT_WEEKLY_COMPARE]
    )
    payload = build_optimizer_job_shadow_compare_batch_manifest_payload(
        compare_paths=compare_paths,
        schema_version=args.schema_version,
        manifest_id=args.manifest_id,
        generated_at=args.generated_at,
        comparison_dimension=args.comparison_dimension,
        batch_window_label=args.batch_window_label,
        path_style=args.path_style,
    )
    validate_optimizer_job_shadow_compare_batch_manifest_payload(payload)
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job shadow compare batch manifest to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
