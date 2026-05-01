#!/usr/bin/env python3
"""
Wrap a topic-outcome-backfill payload in a scheduler-facing job-run envelope.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_job_input_lib import (
    TOPIC_OUTCOME_BACKFILL_JOB_KIND,
    TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
    TOPIC_OUTCOME_BACKFILL_RUN_SCHEMA_VERSION,
    build_optimizer_job_run_payload,
)
from reward_lib import load_json


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = DEFAULT_ROOT / "fixtures" / "topic-outcome-backfills.sample.json"
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-run.sample.json"


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    payload = load_json(args.input)
    return build_optimizer_job_run_payload(
        payload=payload,
        schema_version=args.schema_version,
        job_run_id=args.job_run_id,
        job_kind=TOPIC_OUTCOME_BACKFILL_JOB_KIND,
        generated_at=args.generated_at,
        generated_from={
            "rankingRunId": payload.get("runId"),
            "rankingSnapshotId": payload.get("snapshotId"),
            "evaluationWindow": payload.get("evaluationWindow"),
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "Path to a canonical topic-outcome-backfills payload or a raw "
            "topic-outcome-backfills payload"
        ),
    )
    parser.add_argument(
        "--schema-version",
        default=TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
        choices=(
            TOPIC_OUTCOME_BACKFILL_RUN_SAMPLE_SCHEMA_VERSION,
            TOPIC_OUTCOME_BACKFILL_RUN_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--job-run-id",
        default="job.topic-outcome-backfill.autotiktok.fixture.2026-04-16",
    )
    parser.add_argument("--generated-at", default="2026-04-16T00:05:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        rendered = json.dumps(build_payload(args), ensure_ascii=True, indent=2)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote topic outcome backfill run to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
