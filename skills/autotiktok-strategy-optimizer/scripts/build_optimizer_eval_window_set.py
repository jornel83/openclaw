#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer eval window-set fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_runtime_profile_lib import (
    DEFAULT_RUNTIME_PROFILE_FAMILY_ID,
    DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID,
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
    RUNTIME_PROFILE_CATALOG_LANES,
    RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
    build_default_runtime_profile_family_entries,
    build_optimizer_runtime_profile_family_registry_payload,
    build_optimizer_runtime_profile_family_registry_reference,
    build_optimizer_runtime_profile_catalog_reference,
    resolve_runtime_profile_catalog_reference_from_family_registry,
    validate_optimizer_runtime_profile_family_registry_payload,
)
from optimizer_runtime_profile_rollout_lib import (
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_FAMILY,
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_ID,
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
    build_default_optimizer_runtime_profile_rollout_family_policies,
    build_optimizer_runtime_profile_rollout_policy_payload,
    build_optimizer_runtime_profile_rollout_policy_reference,
    resolve_runtime_profile_eval_purpose_policy,
    resolve_runtime_profile_routing_from_rollout_policy,
    validate_runtime_profile_planner_metadata_contract_selection,
    validate_optimizer_runtime_profile_rollout_policy_payload,
)
from optimizer_eval_window_set_lib import (
    COMPARISON_DIMENSIONS,
    OPTIMIZER_EVAL_WINDOW_SET_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSION,
    build_optimizer_eval_runtime_source,
    build_planner_runtime_source_descriptor,
    build_runtime_source_descriptor,
    build_optimizer_eval_window_set_entry,
    build_optimizer_eval_window_set_payload,
)

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-eval-window-set.sample.json"


def _build_default_runtime_sources(
    *,
    runtime_source_mode: str,
    input_manifest_path: str,
    input_bundle_path: str,
    input_offline_cycle_daily_path: str,
    input_offline_cycle_weekly_path: str,
) -> list[dict[str, object]]:
    if runtime_source_mode == "descriptor":
        return [
            build_optimizer_eval_runtime_source(
                runtime_source_id="recent-daily-manifest",
                source_descriptor=build_planner_runtime_source_descriptor(
                    profile_id="optimizer_input_manifest_profile",
                ),
                include_weekly_promotion=False,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
            build_optimizer_eval_runtime_source(
                runtime_source_id="recent-weekly-bundle",
                source_descriptor=build_planner_runtime_source_descriptor(
                    profile_id="optimizer_input_bundle_profile",
                ),
                include_weekly_promotion=True,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
            build_optimizer_eval_runtime_source(
                runtime_source_id="historical-daily-cycle",
                source_descriptor=build_planner_runtime_source_descriptor(
                    profile_id="optimizer_offline_cycle_daily_profile",
                ),
                include_weekly_promotion=False,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
            build_optimizer_eval_runtime_source(
                runtime_source_id="historical-weekly-cycle",
                source_descriptor=build_planner_runtime_source_descriptor(
                    profile_id="optimizer_offline_cycle_weekly_profile",
                ),
                include_weekly_promotion=True,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
        ]
    if runtime_source_mode == "sample_descriptor":
        return [
            build_optimizer_eval_runtime_source(
                runtime_source_id="recent-daily-manifest",
                source_descriptor=build_runtime_source_descriptor(
                    artifact_binding="optimizer_input_manifest_sample"
                ),
                include_weekly_promotion=False,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
            build_optimizer_eval_runtime_source(
                runtime_source_id="recent-weekly-bundle",
                source_descriptor=build_runtime_source_descriptor(
                    artifact_binding="optimizer_input_bundle_sample"
                ),
                include_weekly_promotion=True,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
            build_optimizer_eval_runtime_source(
                runtime_source_id="historical-daily-cycle",
                source_descriptor=build_runtime_source_descriptor(
                    artifact_binding="optimizer_offline_cycle_daily_sample"
                ),
                include_weekly_promotion=False,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
            build_optimizer_eval_runtime_source(
                runtime_source_id="historical-weekly-cycle",
                source_descriptor=build_runtime_source_descriptor(
                    artifact_binding="optimizer_offline_cycle_weekly_sample"
                ),
                include_weekly_promotion=True,
                ranking_contract_version="ranking-optimizer-contract.v1",
                ranking_contract_validation_mode="exact",
            ),
        ]
    return [
        build_optimizer_eval_runtime_source(
            runtime_source_id="recent-daily-manifest",
            input_manifest_path=input_manifest_path,
            include_weekly_promotion=False,
            ranking_contract_version="ranking-optimizer-contract.v1",
            ranking_contract_validation_mode="exact",
        ),
        build_optimizer_eval_runtime_source(
            runtime_source_id="recent-weekly-bundle",
            input_bundle_path=input_bundle_path,
            include_weekly_promotion=True,
            ranking_contract_version="ranking-optimizer-contract.v1",
            ranking_contract_validation_mode="exact",
        ),
        build_optimizer_eval_runtime_source(
            runtime_source_id="historical-daily-cycle",
            input_offline_cycle_path=input_offline_cycle_daily_path,
            include_weekly_promotion=False,
            ranking_contract_version="ranking-optimizer-contract.v1",
            ranking_contract_validation_mode="exact",
        ),
        build_optimizer_eval_runtime_source(
            runtime_source_id="historical-weekly-cycle",
            input_offline_cycle_path=input_offline_cycle_weekly_path,
            include_weekly_promotion=True,
            ranking_contract_version="ranking-optimizer-contract.v1",
            ranking_contract_validation_mode="exact",
        ),
    ]


def _build_default_windows() -> list[dict[str, object]]:
    return [
        build_optimizer_eval_window_set_entry(
            window_id="recent-daily",
            history_batch_label="2026-04-15",
            history_window_label="recent_batch",
            scenario_label="current_daily",
            mode="daily_review_only",
            generated_at="2026-04-15T06:00:00Z",
            cycle_id="optimizer-offline-cycle.autotiktok.fixture.2026-04-15.daily",
            eval_run_id="optimizer-eval-run.autotiktok.fixture.2026-04-15.daily",
            report_id="daily-review.autotiktok.fixture.2026-04-15.daily",
            runtime_source_id="recent-daily-manifest",
            include_weekly_promotion=False,
        ),
        build_optimizer_eval_window_set_entry(
            window_id="recent-weekly",
            history_batch_label="2026-04-15",
            history_window_label="recent_batch",
            scenario_label="current_weekly",
            mode="daily_with_weekly_promotion",
            generated_at="2026-04-15T06:00:00Z",
            cycle_id="optimizer-offline-cycle.autotiktok.fixture.2026-04-15",
            eval_run_id="optimizer-eval-run.autotiktok.fixture.2026-04-15",
            report_id="daily-review.autotiktok.fixture.2026-04-15",
            runtime_source_id="recent-weekly-bundle",
            include_weekly_promotion=True,
        ),
        build_optimizer_eval_window_set_entry(
            window_id="historical-daily",
            history_batch_label="2026-04-12",
            history_window_label="historical_batch",
            scenario_label="historical_daily",
            mode="daily_review_only",
            generated_at="2026-04-12T06:00:00Z",
            cycle_id="optimizer-offline-cycle.autotiktok.fixture.2026-04-12.daily",
            eval_run_id="optimizer-eval-run.autotiktok.fixture.2026-04-12.daily",
            report_id="daily-review.autotiktok.fixture.2026-04-12.daily",
            runtime_source_id="historical-daily-cycle",
            include_weekly_promotion=False,
            summary_overrides={
                "topicReward": 0.59,
                "performanceReward": 0.432,
                "combinedReward": 0.5742,
                "postCoverageRate": 0.5,
                "rejectedCount": 2,
                "shadowLeaderProfileId": "scale-default",
            },
        ),
        build_optimizer_eval_window_set_entry(
            window_id="historical-weekly",
            history_batch_label="2026-04-12",
            history_window_label="historical_batch",
            scenario_label="historical_weekly",
            mode="daily_with_weekly_promotion",
            generated_at="2026-04-12T06:00:00Z",
            cycle_id="optimizer-offline-cycle.autotiktok.fixture.2026-04-12",
            eval_run_id="optimizer-eval-run.autotiktok.fixture.2026-04-12",
            report_id="daily-review.autotiktok.fixture.2026-04-12",
            runtime_source_id="historical-weekly-cycle",
            include_weekly_promotion=True,
            summary_overrides={
                "topicReward": 0.59,
                "performanceReward": 0.432,
                "combinedReward": 0.5742,
                "postCoverageRate": 0.5,
                "rejectedCount": 2,
                "shadowLeaderProfileId": "scale-default",
                "weeklyDecision": "keep_champion",
                "selectedChallengerProfileId": None,
            },
        ),
    ]


def _build_default_window_set_components(
    *,
    runtime_source_mode: str,
    input_manifest_path: str,
    input_bundle_path: str,
    input_offline_cycle_daily_path: str,
    input_offline_cycle_weekly_path: str,
) -> dict[str, list[dict[str, object]]]:
    return {
        "runtime_sources": _build_default_runtime_sources(
            runtime_source_mode=runtime_source_mode,
            input_manifest_path=input_manifest_path,
            input_bundle_path=input_bundle_path,
            input_offline_cycle_daily_path=input_offline_cycle_daily_path,
            input_offline_cycle_weekly_path=input_offline_cycle_weekly_path,
        ),
        "windows": _build_default_windows(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_EVAL_WINDOW_SET_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_EVAL_WINDOW_SET_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--window-set-id",
        default="optimizer-eval-window-set.autotiktok.fixture.2026-04-15",
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--comparison-dimension",
        default=None,
        choices=COMPARISON_DIMENSIONS,
    )
    parser.add_argument(
        "--runtime-source-mode",
        choices=("descriptor", "sample_descriptor", "path"),
        default="descriptor",
    )
    parser.add_argument("--batch-window-label", default="2026-04-12..2026-04-15")
    parser.add_argument("--window-set-purpose", default="production_replay")
    parser.add_argument("--window-set-batch-type", default=None)
    parser.add_argument(
        "--input-manifest-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json",
    )
    parser.add_argument(
        "--input-bundle-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json",
    )
    parser.add_argument(
        "--input-offline-cycle-daily-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle-daily.sample.json",
    )
    parser.add_argument(
        "--input-offline-cycle-weekly-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle.sample.json",
    )
    parser.add_argument("--input-runtime-profile-family-registry", type=Path)
    parser.add_argument("--input-runtime-profile-rollout-policy", type=Path)
    parser.add_argument(
        "--runtime-profile-family-id",
        default=None,
    )
    parser.add_argument("--runtime-profile-rollout-class")
    parser.add_argument(
        "--runtime-profile-lane",
        default=None,
        choices=RUNTIME_PROFILE_CATALOG_LANES,
    )
    parser.add_argument(
        "--runtime-profile-catalog-id",
    )
    parser.add_argument(
        "--runtime-profile-catalog-family",
    )
    parser.add_argument(
        "--runtime-profile-catalog-version",
    )
    parser.add_argument(
        "--runtime-profile-catalog-schema-version",
        default=None,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    components = _build_default_window_set_components(
        runtime_source_mode=args.runtime_source_mode,
        input_manifest_path=args.input_manifest_path,
        input_bundle_path=args.input_bundle_path,
        input_offline_cycle_daily_path=args.input_offline_cycle_daily_path,
        input_offline_cycle_weekly_path=args.input_offline_cycle_weekly_path,
    )
    runtime_profile_rollout_policy_reference = None
    runtime_profile_family_registry_reference = None
    runtime_profile_rollout_class = None
    runtime_profile_lane_selection_source = "implicit_default"
    runtime_profile_active_lane = None
    runtime_profile_default_lane = None
    runtime_profile_rollout_strategy = None
    runtime_profile_matched_rollout_rule_id = None
    runtime_profile_purpose_policy_id = None
    runtime_profile_purpose_template_id = None
    runtime_profile_purpose_template_family_id = None
    runtime_profile_planner_metadata_policy_id = None
    runtime_profile_planner_metadata_contract_family_id = None
    runtime_profile_planner_metadata_contract_id = None
    comparison_dimension_selection_source = "fallback_default"
    window_set_batch_type_selection_source = "fallback_default"
    selected_runtime_profile_family_id = (
        args.runtime_profile_family_id or DEFAULT_RUNTIME_PROFILE_FAMILY_ID
    )
    selected_comparison_dimension = args.comparison_dimension
    selected_window_set_batch_type = args.window_set_batch_type
    explicit_catalog_override = any(
        value is not None
        for value in (
            args.runtime_profile_catalog_id,
            args.runtime_profile_catalog_family,
            args.runtime_profile_catalog_version,
        )
    )
    if explicit_catalog_override and not all(
        value is not None
        for value in (
            args.runtime_profile_catalog_id,
            args.runtime_profile_catalog_family,
            args.runtime_profile_catalog_version,
        )
    ):
        raise SystemExit(
            "explicit runtime profile catalog overrides require "
            "--runtime-profile-catalog-id, --runtime-profile-catalog-family, "
            "and --runtime-profile-catalog-version together"
        )
    if args.input_runtime_profile_family_registry is not None:
        family_registry_payload = json.loads(
            args.input_runtime_profile_family_registry.read_text(encoding="utf-8")
        )
        validate_optimizer_runtime_profile_family_registry_payload(
            family_registry_payload
        )
    elif not explicit_catalog_override:
        family_registry_payload = build_optimizer_runtime_profile_family_registry_payload(
            registry_id=DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID,
            schema_version=OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
            generated_at=args.generated_at,
            families=build_default_runtime_profile_family_entries(
                catalog_schema_version=OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION
            ),
        )
    else:
        family_registry_payload = None

    if args.input_runtime_profile_rollout_policy is not None:
        rollout_policy_payload = json.loads(
            args.input_runtime_profile_rollout_policy.read_text(encoding="utf-8")
        )
        validate_optimizer_runtime_profile_rollout_policy_payload(
            rollout_policy_payload
        )
    elif family_registry_payload is not None:
        rollout_policy_payload = build_optimizer_runtime_profile_rollout_policy_payload(
            policy_id=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_ID,
            schema_version=OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
            policy_family=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_FAMILY,
            policy_version=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_VERSION,
            generated_at=args.generated_at,
            runtime_profile_family_registry_reference={
                "registryId": family_registry_payload["registryId"],
                "schemaVersion": family_registry_payload["schemaVersion"],
            },
            family_policies=build_default_optimizer_runtime_profile_rollout_family_policies(
                family_id=selected_runtime_profile_family_id,
            )
        )
    else:
        rollout_policy_payload = None

    selected_runtime_profile_lane = args.runtime_profile_lane
    purpose_policy_resolution = None
    purpose_policy_rollout_class = None
    if rollout_policy_payload is not None:
        rollout_registry_reference = rollout_policy_payload[
            "runtimeProfileFamilyRegistryReference"
        ]
        if family_registry_payload is not None:
            if (
                rollout_registry_reference["registryId"] != family_registry_payload["registryId"]
                or rollout_registry_reference["schemaVersion"]
                != family_registry_payload["schemaVersion"]
            ):
                raise SystemExit(
                    "runtime profile rollout policy must reference the same family registry "
                    "used by this window-set build"
                )
        if args.runtime_profile_lane is None and args.runtime_profile_rollout_class is None:
            purpose_policy_resolution = resolve_runtime_profile_eval_purpose_policy(
                window_set_purpose=args.window_set_purpose,
                requested_family_id=args.runtime_profile_family_id,
                rollout_policy=rollout_policy_payload,
            )
            if purpose_policy_resolution is not None:
                runtime_profile_purpose_policy_id = purpose_policy_resolution[
                    "purposePolicyId"
                ]
                runtime_profile_purpose_template_id = purpose_policy_resolution.get(
                    "purposeTemplateId"
                )
                runtime_profile_purpose_template_family_id = (
                    purpose_policy_resolution.get("purposeTemplateFamilyId")
                )
                runtime_profile_planner_metadata_policy_id = (
                    purpose_policy_resolution.get("plannerMetadataPolicyId")
                )
                runtime_profile_planner_metadata_contract_family_id = (
                    purpose_policy_resolution.get(
                        "plannerMetadataContractFamilyId"
                    )
                )
                runtime_profile_planner_metadata_contract_id = (
                    purpose_policy_resolution.get("plannerMetadataContractId")
                )
                selected_runtime_profile_family_id = purpose_policy_resolution[
                    "familyId"
                ]
                purpose_policy_rollout_class = purpose_policy_resolution[
                    "defaultRolloutClass"
                ]
                if selected_window_set_batch_type is None:
                    purpose_batch_type = purpose_policy_resolution.get(
                        "defaultWindowSetBatchType"
                    )
                    if purpose_batch_type is not None:
                        selected_window_set_batch_type = purpose_batch_type
                        window_set_batch_type_selection_source = (
                            purpose_policy_resolution.get(
                                "defaultWindowSetBatchTypeSource",
                                "purpose_policy",
                            )
                        )
                if selected_comparison_dimension is None:
                    purpose_dimension = purpose_policy_resolution.get(
                        "defaultComparisonDimension"
                    )
                    if purpose_dimension is not None:
                        selected_comparison_dimension = purpose_dimension
                        comparison_dimension_selection_source = (
                            purpose_policy_resolution.get(
                                "defaultComparisonDimensionSource",
                                "purpose_policy",
                            )
                        )
        if selected_comparison_dimension is None:
            selected_comparison_dimension = "historyBatchLabel"
        if selected_window_set_batch_type is None:
            selected_window_set_batch_type = "standard_replay"
        if runtime_profile_planner_metadata_contract_id is not None:
            validate_runtime_profile_planner_metadata_contract_selection(
                metadata_contract_id=runtime_profile_planner_metadata_contract_id,
                window_set_batch_type=str(selected_window_set_batch_type),
                comparison_dimension=str(selected_comparison_dimension),
                rollout_policy=rollout_policy_payload,
            )
        rollout_lane_resolution = resolve_runtime_profile_routing_from_rollout_policy(
            family_id=selected_runtime_profile_family_id,
            requested_lane=args.runtime_profile_lane,
            requested_rollout_class=args.runtime_profile_rollout_class,
            default_rollout_class=purpose_policy_rollout_class,
            default_rollout_class_source=(
                "policy_purpose" if purpose_policy_rollout_class is not None else None
            ),
            purpose_policy_id=runtime_profile_purpose_policy_id,
            purpose_template_id=runtime_profile_purpose_template_id,
            purpose_template_family_id=runtime_profile_purpose_template_family_id,
            planner_metadata_policy_id=runtime_profile_planner_metadata_policy_id,
            planner_metadata_contract_family_id=(
                runtime_profile_planner_metadata_contract_family_id
            ),
            planner_metadata_contract_id=runtime_profile_planner_metadata_contract_id,
            rollout_policy=rollout_policy_payload,
            window_set_id=args.window_set_id,
            batch_window_label=args.batch_window_label,
            comparison_dimension=selected_comparison_dimension,
            window_set_purpose=args.window_set_purpose,
            window_set_batch_type=selected_window_set_batch_type,
            windows=components["windows"],
        )
        selected_runtime_profile_lane = rollout_lane_resolution["selectedLane"]
        runtime_profile_rollout_class = rollout_lane_resolution[
            "selectedRolloutClass"
        ]
        runtime_profile_lane_selection_source = rollout_lane_resolution[
            "laneSelectionSource"
        ]
        runtime_profile_active_lane = rollout_lane_resolution["activeLane"]
        runtime_profile_default_lane = rollout_lane_resolution["defaultLane"]
        runtime_profile_rollout_strategy = rollout_lane_resolution["rolloutStrategy"]
        runtime_profile_matched_rollout_rule_id = rollout_lane_resolution.get(
            "matchedRolloutRuleId"
        )
        runtime_profile_purpose_policy_id = rollout_lane_resolution.get(
            "purposePolicyId", runtime_profile_purpose_policy_id
        )
        runtime_profile_purpose_template_id = rollout_lane_resolution.get(
            "purposeTemplateId", runtime_profile_purpose_template_id
        )
        runtime_profile_purpose_template_family_id = rollout_lane_resolution.get(
            "purposeTemplateFamilyId", runtime_profile_purpose_template_family_id
        )
        runtime_profile_planner_metadata_policy_id = rollout_lane_resolution.get(
            "plannerMetadataPolicyId", runtime_profile_planner_metadata_policy_id
        )
        runtime_profile_planner_metadata_contract_family_id = (
            rollout_lane_resolution.get(
                "plannerMetadataContractFamilyId",
                runtime_profile_planner_metadata_contract_family_id,
            )
        )
        runtime_profile_planner_metadata_contract_id = rollout_lane_resolution.get(
            "plannerMetadataContractId", runtime_profile_planner_metadata_contract_id
        )
        runtime_profile_rollout_policy_reference = (
            build_optimizer_runtime_profile_rollout_policy_reference(
                policy_id=rollout_policy_payload["policyId"],
                schema_version=rollout_policy_payload["schemaVersion"],
                policy_family=rollout_policy_payload["policyFamily"],
                policy_version=rollout_policy_payload["policyVersion"],
                family_id=selected_runtime_profile_family_id,
            )
        )
    elif selected_runtime_profile_lane is None:
        selected_runtime_profile_lane = RUNTIME_PROFILE_CATALOG_LANE_CURRENT
    else:
        runtime_profile_lane_selection_source = "explicit"
        runtime_profile_rollout_class = args.runtime_profile_rollout_class
        runtime_profile_matched_rollout_rule_id = None
    if selected_comparison_dimension is None:
        selected_comparison_dimension = "historyBatchLabel"
    if selected_window_set_batch_type is None:
        selected_window_set_batch_type = "standard_replay"
    if args.comparison_dimension is not None:
        comparison_dimension_selection_source = "explicit"
    if args.window_set_batch_type is not None:
        window_set_batch_type_selection_source = "explicit"

    if family_registry_payload is not None:
        runtime_profile_family_registry_reference = (
            build_optimizer_runtime_profile_family_registry_reference(
                registry_id=family_registry_payload["registryId"],
                schema_version=family_registry_payload["schemaVersion"],
                family_id=selected_runtime_profile_family_id,
                lane=str(selected_runtime_profile_lane),
            )
        )
        runtime_profile_catalog_reference = (
            resolve_runtime_profile_catalog_reference_from_family_registry(
                family_id=selected_runtime_profile_family_id,
                lane=str(selected_runtime_profile_lane),
                family_registry=family_registry_payload,
            )
        )
    else:
        runtime_profile_catalog_reference = build_optimizer_runtime_profile_catalog_reference(
            catalog_id=str(args.runtime_profile_catalog_id),
            catalog_family=str(args.runtime_profile_catalog_family),
            catalog_version=str(args.runtime_profile_catalog_version),
            schema_version=str(
                args.runtime_profile_catalog_schema_version
                or OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION
            ),
        )
    payload = build_optimizer_eval_window_set_payload(
        windows=components["windows"],
        runtime_sources=components["runtime_sources"],
        runtime_profile_rollout_policy_reference=runtime_profile_rollout_policy_reference,
        runtime_profile_family_registry_reference=runtime_profile_family_registry_reference,
        runtime_profile_catalog_reference=runtime_profile_catalog_reference,
        runtime_profile_rollout_class=runtime_profile_rollout_class,
        runtime_profile_lane_selection_source=runtime_profile_lane_selection_source,
        runtime_profile_active_lane=runtime_profile_active_lane,
        runtime_profile_default_lane=runtime_profile_default_lane,
        runtime_profile_rollout_strategy=runtime_profile_rollout_strategy,
        runtime_profile_matched_rollout_rule_id=runtime_profile_matched_rollout_rule_id,
        schema_version=args.schema_version,
        window_set_id=args.window_set_id,
        generated_at=args.generated_at,
        comparison_dimension=str(selected_comparison_dimension),
        comparison_dimension_selection_source=comparison_dimension_selection_source,
        batch_window_label=args.batch_window_label,
        window_set_purpose=args.window_set_purpose,
        window_set_batch_type=str(selected_window_set_batch_type),
        window_set_batch_type_selection_source=window_set_batch_type_selection_source,
    )
    if runtime_profile_purpose_policy_id is not None:
        payload["generatedFrom"]["runtimeProfilePurposePolicyId"] = (
            runtime_profile_purpose_policy_id
        )
    if runtime_profile_purpose_template_id is not None:
        payload["generatedFrom"]["runtimeProfilePurposeTemplateId"] = (
            runtime_profile_purpose_template_id
        )
    if runtime_profile_purpose_template_family_id is not None:
        payload["generatedFrom"]["runtimeProfilePurposeTemplateFamilyId"] = (
            runtime_profile_purpose_template_family_id
        )
    if runtime_profile_planner_metadata_policy_id is not None:
        payload["generatedFrom"]["runtimeProfilePlannerMetadataPolicyId"] = (
            runtime_profile_planner_metadata_policy_id
        )
    if runtime_profile_planner_metadata_contract_family_id is not None:
        payload["generatedFrom"]["runtimeProfilePlannerMetadataContractFamilyId"] = (
            runtime_profile_planner_metadata_contract_family_id
        )
    if runtime_profile_planner_metadata_contract_id is not None:
        payload["generatedFrom"]["runtimeProfilePlannerMetadataContractId"] = (
            runtime_profile_planner_metadata_contract_id
        )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer eval window set to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
