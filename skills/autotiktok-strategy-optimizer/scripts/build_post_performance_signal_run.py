#!/usr/bin/env python3
"""
Wrap a post-performance payload in a scheduler-facing job-run envelope.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_job_input_lib import (
    POST_PERFORMANCE_SIGNAL_JOB_KIND,
    POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
    POST_PERFORMANCE_SIGNAL_RUN_SCHEMA_VERSION,
    build_optimizer_job_run_payload,
)
from reward_lib import load_json


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = DEFAULT_ROOT / "fixtures" / "post-performance-signals.sample.json"
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "post-performance-signal-run.sample.json"


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    payload = load_json(args.input)
    return build_optimizer_job_run_payload(
        payload=payload,
        schema_version=args.schema_version,
        job_run_id=args.job_run_id,
        job_kind=POST_PERFORMANCE_SIGNAL_JOB_KIND,
        generated_at=args.generated_at,
        generated_from={
            "rankingRunId": payload.get("runId"),
            "accountId": payload.get("accountId"),
            "measuredWindow": payload.get("measuredWindow"),
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "Path to a canonical post-performance-signals payload or a raw "
            "post-performance payload"
        ),
    )
    parser.add_argument(
        "--schema-version",
        default=POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
        choices=(
            POST_PERFORMANCE_SIGNAL_RUN_SAMPLE_SCHEMA_VERSION,
            POST_PERFORMANCE_SIGNAL_RUN_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--job-run-id",
        default="job.post-performance-signal.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T00:10:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        rendered = json.dumps(build_payload(args), ensure_ascii=True, indent=2)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote post performance signal run to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
