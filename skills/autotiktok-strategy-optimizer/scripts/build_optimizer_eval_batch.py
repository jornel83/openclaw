#!/usr/bin/env python3
"""
Build an optimizer eval-batch artifact from eval-run inputs or an eval-batch manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from build_optimizer_eval_run import build_eval_run
from optimizer_eval_batch_lib import (
    COMPARISON_DIMENSIONS,
    build_optimizer_eval_batch_payload,
    load_optimizer_eval_batch_manifest,
)
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)
from reward_lib import load_json
from run_offline_optimizer_cycle import (
    DEFAULT_BACKFILLS,
    DEFAULT_CHALLENGER_INPUT,
    DEFAULT_CONTEXT,
    DEFAULT_PERFORMANCE,
    DEFAULT_RANKING_OUTPUT,
)
from optimizer_lib import DEFAULT_POLICY


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-eval-batch.sample.json"


def _build_eval_run_args(
    args: argparse.Namespace,
    *,
    suffix: str,
    include_weekly_promotion: bool,
) -> argparse.Namespace:
    return argparse.Namespace(
        input_offline_cycle=None,
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
        cycle_id=f"{args.cycle_id}.{suffix}",
        eval_run_id=f"{args.eval_run_id}.{suffix}",
        report_id=f"{args.report_id}.{suffix}",
        generated_at=args.generated_at,
        include_weekly_promotion=include_weekly_promotion,
    )


def _build_default_comparison_eval_runs(
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    return [
        build_eval_run(
            _build_eval_run_args(
                args, suffix="daily", include_weekly_promotion=False
            )
        ),
        build_eval_run(
            _build_eval_run_args(
                args, suffix="weekly", include_weekly_promotion=True
            )
        ),
    ]


def build_eval_batch(args: argparse.Namespace) -> dict[str, object]:
    comparison_dimension = args.comparison_dimension
    batch_window_label = args.batch_window_label
    window_set_purpose = args.window_set_purpose
    window_set_batch_type = args.window_set_batch_type
    window_set_batch_type_selection_source = None
    comparison_dimension_selection_source = None
    runtime_profile_purpose_policy_id = None
    runtime_profile_purpose_template_id = None
    runtime_profile_purpose_template_family_id = None
    runtime_profile_planner_metadata_contract_family_id = None
    runtime_profile_planner_metadata_policy_id = None
    runtime_profile_planner_metadata_contract_id = None
    if args.input_eval_run:
        eval_runs = [load_json(path) for path in args.input_eval_run]
        source_mode = "explicit_eval_runs"
        source_descriptor = {
            "inputEvalRunPaths": [str(path) for path in args.input_eval_run]
        }
    elif args.input_eval_batch_manifest is not None:
        manifest_payload, eval_runs = load_optimizer_eval_batch_manifest(
            args.input_eval_batch_manifest
        )
        comparison_dimension = manifest_payload["comparisonDimension"]
        batch_window_label = manifest_payload["batchWindowLabel"]
        window_set_purpose = manifest_payload.get("windowSetPurpose")
        window_set_batch_type = manifest_payload.get("windowSetBatchType")
        window_set_batch_type_selection_source = manifest_payload.get(
            "windowSetBatchTypeSelectionSource"
        )
        comparison_dimension_selection_source = manifest_payload.get(
            "comparisonDimensionSelectionSource"
        )
        runtime_profile_purpose_policy_id = manifest_payload.get(
            "runtimeProfilePurposePolicyId"
        )
        runtime_profile_purpose_template_id = manifest_payload.get(
            "runtimeProfilePurposeTemplateId"
        )
        runtime_profile_purpose_template_family_id = manifest_payload.get(
            "runtimeProfilePurposeTemplateFamilyId"
        )
        runtime_profile_planner_metadata_contract_family_id = manifest_payload.get(
            "runtimeProfilePlannerMetadataContractFamilyId"
        )
        runtime_profile_planner_metadata_policy_id = manifest_payload.get(
            "runtimeProfilePlannerMetadataPolicyId"
        )
        runtime_profile_planner_metadata_contract_id = manifest_payload.get(
            "runtimeProfilePlannerMetadataContractId"
        )
        source_mode = "eval_batch_manifest"
        source_input_key = (
            "inputEvalRunEntries"
            if "evalRunEntries" in manifest_payload
            else "inputEvalRunPaths"
        )
        manifest_input_value = (
            manifest_payload["evalRunEntries"]
            if source_input_key == "inputEvalRunEntries"
            else manifest_payload["evalRunPaths"]
        )
        source_descriptor = {
            "manifestSchemaVersion": manifest_payload["schemaVersion"],
            "manifestId": manifest_payload.get("manifestId"),
            source_input_key: manifest_input_value,
        }
    else:
        eval_runs = _build_default_comparison_eval_runs(args)
        source_mode = "default_mode_comparison"
        source_descriptor = {
            "comparisonModes": ["daily_review_only", "daily_with_weekly_promotion"],
            "rankingContractVersion": args.ranking_contract_version,
            "rankingContractValidationMode": args.ranking_contract_validation_mode,
        }
    return build_optimizer_eval_batch_payload(
        eval_runs=eval_runs,
        batch_id=args.batch_id,
        generated_at=args.generated_at,
        source_mode=source_mode,
        source_descriptor=source_descriptor,
        comparison_dimension=comparison_dimension,
        batch_window_label=batch_window_label,
        window_set_purpose=window_set_purpose,
        window_set_batch_type=window_set_batch_type,
        window_set_batch_type_selection_source=window_set_batch_type_selection_source,
        comparison_dimension_selection_source=comparison_dimension_selection_source,
        runtime_profile_purpose_policy_id=runtime_profile_purpose_policy_id,
        runtime_profile_purpose_template_id=runtime_profile_purpose_template_id,
        runtime_profile_purpose_template_family_id=(
            runtime_profile_purpose_template_family_id
        ),
        runtime_profile_planner_metadata_contract_family_id=(
            runtime_profile_planner_metadata_contract_family_id
        ),
        runtime_profile_planner_metadata_policy_id=(
            runtime_profile_planner_metadata_policy_id
        ),
        runtime_profile_planner_metadata_contract_id=(
            runtime_profile_planner_metadata_contract_id
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-eval-run", type=Path, action="append")
    parser.add_argument("--input-eval-batch-manifest", type=Path)
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
        "--batch-id", default="optimizer-eval-batch.autotiktok.fixture.2026-04-15"
    )
    parser.add_argument(
        "--report-id", default="daily-review.autotiktok.fixture.2026-04-15"
    )
    parser.add_argument(
        "--comparison-dimension",
        default="mode",
        choices=COMPARISON_DIMENSIONS,
    )
    parser.add_argument(
        "--batch-window-label", default="2026-04-15..2026-04-15"
    )
    parser.add_argument("--window-set-purpose")
    parser.add_argument("--window-set-batch-type")
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload = build_eval_batch(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer eval batch to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
