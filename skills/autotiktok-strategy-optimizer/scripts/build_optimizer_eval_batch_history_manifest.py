#!/usr/bin/env python3
"""
Build a historical optimizer eval-batch manifest from a scheduler-facing eval window set.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_eval_batch_lib import (
    OPTIMIZER_EVAL_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSION,
    build_optimizer_eval_batch_manifest_payload,
)
from optimizer_eval_window_set_lib import (
    build_eval_batch_manifest_entries_from_window_set,
    load_optimizer_eval_window_set,
    load_optimizer_runtime_artifact_registry,
    load_optimizer_runtime_profile_catalog,
    load_optimizer_runtime_materialization_plan,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WINDOW_SET = DEFAULT_ROOT / "fixtures" / "optimizer-eval-window-set.sample.json"
DEFAULT_OUTPUT = (
    DEFAULT_ROOT / "fixtures" / "optimizer-eval-batch-history-manifest.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-window-set", type=Path, default=DEFAULT_WINDOW_SET)
    parser.add_argument("--input-artifact-registry", type=Path)
    parser.add_argument("--input-runtime-profile-catalog", type=Path)
    parser.add_argument("--input-materialization-plan", type=Path)
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
        default="optimizer-eval-batch-history-manifest.autotiktok.fixture.2026-04-15",
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--path-style", choices=("repo", "absolute", "basename"), default="repo"
    )
    parser.add_argument("--input-manifest-path")
    parser.add_argument("--input-bundle-path")
    parser.add_argument("--input-offline-cycle-daily-path")
    parser.add_argument("--input-offline-cycle-weekly-path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    window_set_payload = load_optimizer_eval_window_set(args.input_window_set)
    artifact_registry = None
    if args.input_artifact_registry is not None:
        artifact_registry = load_optimizer_runtime_artifact_registry(
            args.input_artifact_registry
        )
    runtime_profile_catalog = None
    if args.input_runtime_profile_catalog is not None:
        runtime_profile_catalog = load_optimizer_runtime_profile_catalog(
            args.input_runtime_profile_catalog
        )
    materialization_plan = None
    if args.input_materialization_plan is not None:
        materialization_plan = load_optimizer_runtime_materialization_plan(
            args.input_materialization_plan
        )
    descriptor_path_overrides = {
        key: value
        for key, value in {
            "optimizer_input_manifest": args.input_manifest_path,
            "optimizer_input_bundle": args.input_bundle_path,
            "optimizer_offline_cycle_daily": args.input_offline_cycle_daily_path,
            "optimizer_offline_cycle_weekly": args.input_offline_cycle_weekly_path,
        }.items()
        if isinstance(value, str) and value
    }
    eval_run_entries = build_eval_batch_manifest_entries_from_window_set(
        window_set_payload=window_set_payload,
        path_style=args.path_style,
        artifact_registry=artifact_registry,
        runtime_profile_catalog=runtime_profile_catalog,
        materialization_plan=materialization_plan,
        descriptor_path_overrides=descriptor_path_overrides or None,
    )
    payload = build_optimizer_eval_batch_manifest_payload(
        eval_run_paths=None,
        eval_run_entries=eval_run_entries,
        schema_version=args.schema_version,
        manifest_id=args.manifest_id,
        generated_at=args.generated_at,
        comparison_dimension=window_set_payload["comparisonDimension"],
        batch_window_label=window_set_payload["batchWindowLabel"],
        window_set_purpose=window_set_payload.get("windowSetPurpose"),
        window_set_batch_type=window_set_payload.get("windowSetBatchType"),
        window_set_batch_type_selection_source=window_set_payload.get(
            "generatedFrom", {}
        ).get("windowSetBatchTypeSelectionSource"),
        comparison_dimension_selection_source=window_set_payload.get(
            "generatedFrom", {}
        ).get("comparisonDimensionSelectionSource"),
        runtime_profile_purpose_policy_id=window_set_payload.get(
            "generatedFrom", {}
        ).get("runtimeProfilePurposePolicyId"),
        runtime_profile_purpose_template_id=window_set_payload.get(
            "generatedFrom", {}
        ).get("runtimeProfilePurposeTemplateId"),
        runtime_profile_purpose_template_family_id=window_set_payload.get(
            "generatedFrom", {}
        ).get("runtimeProfilePurposeTemplateFamilyId"),
        runtime_profile_planner_metadata_contract_family_id=window_set_payload.get(
            "generatedFrom", {}
        ).get("runtimeProfilePlannerMetadataContractFamilyId"),
        runtime_profile_planner_metadata_policy_id=window_set_payload.get(
            "generatedFrom", {}
        ).get("runtimeProfilePlannerMetadataPolicyId"),
        runtime_profile_planner_metadata_contract_id=window_set_payload.get(
            "generatedFrom", {}
        ).get("runtimeProfilePlannerMetadataContractId"),
        path_style=args.path_style,
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer eval batch history manifest to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
