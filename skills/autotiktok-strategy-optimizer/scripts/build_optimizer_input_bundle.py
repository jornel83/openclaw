#!/usr/bin/env python3
"""
Build a single optimizer input bundle from ranking, context, and evaluation-side artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSION,
    build_optimizer_input_bundle_payload,
    materialize_optimizer_input_bundle_from_manifest,
)
from reward_lib import load_json


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING_OUTPUT = (
    DEFAULT_ROOT.parent / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
DEFAULT_CONTEXT = DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
DEFAULT_BACKFILLS = DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-run.sample.json"
DEFAULT_PERFORMANCE = DEFAULT_ROOT / "fixtures" / "post-performance-signal-run.sample.json"
DEFAULT_CHALLENGER_INPUT = DEFAULT_ROOT / "fixtures" / "challenger-evaluation-run.sample.json"
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-input-bundle.sample.json"


def build_bundle(args: argparse.Namespace) -> dict[str, object]:
    if args.input_manifest is not None:
        bundle_payload, _ = materialize_optimizer_input_bundle_from_manifest(
            manifest_path=args.input_manifest,
            bundle_schema_version=args.schema_version,
            bundle_id=args.bundle_id,
            generated_at=args.generated_at,
        )
        return bundle_payload
    return build_optimizer_input_bundle_payload(
        ranking_payload=load_json(args.ranking_input),
        context_payload=load_json(args.context_input),
        backfills_payload=load_json(args.backfills_input),
        performance_payload=load_json(args.performance_input),
        challenger_input_payload=load_json(args.challenger_input),
        schema_version=args.schema_version,
        bundle_id=args.bundle_id,
        generated_at=args.generated_at,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING_OUTPUT)
    parser.add_argument("--context-input", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--backfills-input", type=Path, default=DEFAULT_BACKFILLS)
    parser.add_argument("--performance-input", type=Path, default=DEFAULT_PERFORMANCE)
    parser.add_argument(
        "--challenger-input", dest="challenger_input", type=Path, default=DEFAULT_CHALLENGER_INPUT
    )
    parser.add_argument("--challenger-adjustments", dest="challenger_input", type=Path)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSION,
        ),
    )
    parser.add_argument("--bundle-id", default="optimizer-input-bundle.autotiktok.fixture.2026-04-15")
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_bundle(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer input bundle to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
