#!/usr/bin/env python3
"""
Build an optimizer input manifest that points at the artifacts needed by module 2.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_INPUT_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSION,
    build_optimizer_input_manifest_from_source_registry,
    build_optimizer_input_manifest_payload,
)
from optimizer_input_rollout_lib import (
    load_optimizer_input_rollout_policy,
    resolve_optimizer_input_rollout_selection,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING_OUTPUT = (
    DEFAULT_ROOT.parent / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
DEFAULT_CONTEXT = DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
DEFAULT_BACKFILLS = DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-run.sample.json"
DEFAULT_PERFORMANCE = DEFAULT_ROOT / "fixtures" / "post-performance-signal-run.sample.json"
DEFAULT_CHALLENGER_INPUT = DEFAULT_ROOT / "fixtures" / "challenger-evaluation-run.sample.json"
DEFAULT_INPUT_SOURCE_REGISTRY = (
    DEFAULT_ROOT / "fixtures" / "optimizer-input-source-registry.sample.json"
)
DEFAULT_INPUT_ROLLOUT_POLICY = (
    DEFAULT_ROOT / "fixtures" / "optimizer-input-rollout-policy.sample.json"
)
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-input-manifest.sample.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        default=OPTIMIZER_INPUT_MANIFEST_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_INPUT_MANIFEST_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSION,
        ),
    )
    parser.add_argument("--manifest-id", default="optimizer-input-manifest.autotiktok.fixture.2026-04-15")
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--path-style",
        choices=("repo", "absolute", "basename"),
        default="repo",
    )
    parser.add_argument("--input-source-registry", type=Path)
    parser.add_argument("--source-lane")
    parser.add_argument("--input-rollout-policy", type=Path)
    parser.add_argument("--input-rollout-class")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.source_lane is not None and args.input_rollout_class is not None:
        raise ValueError(
            "--source-lane and --input-rollout-class are mutually exclusive"
        )

    resolved_source_lane = args.source_lane
    input_rollout_policy_reference = None
    input_rollout_class = None
    input_lane_selection_source = None
    input_rollout_strategy = None
    if args.input_rollout_class is not None or args.input_rollout_policy is not None:
        rollout_policy_path = (
            args.input_rollout_policy
            if args.input_rollout_policy is not None
            else DEFAULT_INPUT_ROLLOUT_POLICY
        )
        rollout_policy_payload = load_optimizer_input_rollout_policy(rollout_policy_path)
        selection = resolve_optimizer_input_rollout_selection(
            rollout_policy_payload,
            explicit_rollout_class=args.input_rollout_class,
        )
        resolved_source_lane = selection["sourceLane"]
        input_rollout_class = selection["rolloutClass"]
        input_lane_selection_source = selection["selectionSource"]
        input_rollout_strategy = selection["rolloutStrategy"]
        try:
            rollout_policy_path_label = rollout_policy_path.relative_to(
                DEFAULT_ROOT.parents[1]
            ).as_posix()
        except ValueError:
            rollout_policy_path_label = str(rollout_policy_path)
        input_rollout_policy_reference = {
            "schemaVersion": rollout_policy_payload.get("schemaVersion"),
            "policyId": rollout_policy_payload.get("policyId"),
            "path": rollout_policy_path_label,
        }

    if resolved_source_lane is not None:
        registry_path = (
            args.input_source_registry
            if args.input_source_registry is not None
            else DEFAULT_INPUT_SOURCE_REGISTRY
        )
        payload = build_optimizer_input_manifest_from_source_registry(
            registry_path=registry_path,
            source_lane=resolved_source_lane,
            schema_version=args.schema_version,
            manifest_id=args.manifest_id,
            generated_at=args.generated_at,
            input_rollout_policy_reference=input_rollout_policy_reference,
            input_rollout_class=input_rollout_class,
            input_lane_selection_source=input_lane_selection_source,
            input_rollout_strategy=input_rollout_strategy,
        )
    else:
        payload = build_optimizer_input_manifest_payload(
            ranking_input=args.ranking_input,
            context_input=args.context_input,
            backfills_input=args.backfills_input,
            performance_input=args.performance_input,
            challenger_input=args.challenger_input,
            schema_version=args.schema_version,
            manifest_id=args.manifest_id,
            generated_at=args.generated_at,
            path_style=args.path_style,
        )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer input manifest to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
