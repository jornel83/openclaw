#!/usr/bin/env python3
"""
Helpers for planner-facing optimizer runtime profile rollout policies.
"""

from __future__ import annotations

from typing import Any

from optimizer_runtime_profile_lib import (
    DEFAULT_RUNTIME_PROFILE_FAMILY_ID,
    DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID,
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION,
    RUNTIME_PROFILE_CATALOG_LANES,
    RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
    RUNTIME_PROFILE_CATALOG_LANE_PREVIEW,
)


OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-runtime-profile-rollout-policy.sample.v1"
)
OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSION = (
    "optimizer-runtime-profile-rollout-policy.v1"
)
OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSIONS = {
    OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSION,
}
OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SELECTION_SOURCES = {
    "explicit",
    "implicit_default",
    "policy_default",
    "policy_class",
    "policy_purpose",
    "policy_rule",
}
DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_ID = (
    "optimizer-runtime-profile-rollout-policy.autotiktok.fixture.2026-04-15"
)
DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_FAMILY = "autotiktok-runtime-profile-rollout"
DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_VERSION = "2026-04-15"
DEFAULT_RUNTIME_PROFILE_ROLLOUT_STRATEGY = "manual_gated_preview"
DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS = "production"
PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS = "preview_canary"
PLANNER_METADATA_SELECTION_PRIORITIES = {
    "purpose_policy",
    "purpose_template",
    "purpose_template_family",
    "metadata_policy_default",
    "fallback_default",
}
PLANNER_METADATA_ALLOWED_COMPARISON_DIMENSIONS = {
    "mode",
    "rankingProfileId",
    "rankingSnapshotId",
    "evaluationWindow",
    "weeklyDecision",
    "challengerInputKind",
    "historyBatchLabel",
    "historyWindowLabel",
    "scenarioLabel",
}


def _require_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def build_optimizer_runtime_profile_rollout_family_policy(
    *,
    family_id: str,
    active_lane: str,
    default_lane: str,
    default_rollout_class: str,
    allowed_lanes: list[str],
    rollout_classes: list[dict[str, Any]],
    preview_lane: str,
    preview_enabled: bool,
    rollout_strategy: str,
) -> dict[str, Any]:
    return {
        "familyId": family_id,
        "activeLane": active_lane,
        "defaultLane": default_lane,
        "defaultRolloutClass": default_rollout_class,
        "allowedLanes": allowed_lanes,
        "rolloutClasses": rollout_classes,
        "previewLane": preview_lane,
        "previewEnabled": preview_enabled,
        "rolloutStrategy": rollout_strategy,
    }


def build_optimizer_runtime_profile_rollout_class_entry(
    *,
    rollout_class: str,
    selected_lane: str,
) -> dict[str, str]:
    return {
        "rolloutClass": rollout_class,
        "selectedLane": selected_lane,
    }


def build_optimizer_runtime_profile_eval_purpose_policy_entry(
    *,
    purpose_policy_id: str,
    window_set_purpose: str,
    template_id: str | None = None,
    family_id: str | None = None,
    default_rollout_class: str | None = None,
    default_window_set_batch_type: str | None = None,
    default_comparison_dimension: str | None = None,
) -> dict[str, str]:
    payload = {
        "purposePolicyId": purpose_policy_id,
        "windowSetPurpose": window_set_purpose,
    }
    if template_id is not None:
        payload["templateId"] = template_id
    if family_id is not None:
        payload["familyId"] = family_id
    if default_rollout_class is not None:
        payload["defaultRolloutClass"] = default_rollout_class
    if default_window_set_batch_type is not None:
        payload["defaultWindowSetBatchType"] = default_window_set_batch_type
    if default_comparison_dimension is not None:
        payload["defaultComparisonDimension"] = default_comparison_dimension
    return payload


def build_optimizer_runtime_profile_eval_purpose_template_entry(
    *,
    template_id: str,
    template_family_id: str,
    runtime_profile_family_id: str | None = None,
    default_rollout_class: str | None = None,
    default_window_set_batch_type: str | None = None,
    default_comparison_dimension: str | None = None,
) -> dict[str, str]:
    payload = {
        "templateId": template_id,
        "templateFamilyId": template_family_id,
    }
    if runtime_profile_family_id is not None:
        payload["runtimeProfileFamilyId"] = runtime_profile_family_id
    if default_rollout_class is not None:
        payload["defaultRolloutClass"] = default_rollout_class
    if default_window_set_batch_type is not None:
        payload["defaultWindowSetBatchType"] = default_window_set_batch_type
    if default_comparison_dimension is not None:
        payload["defaultComparisonDimension"] = default_comparison_dimension
    return payload


def build_optimizer_runtime_profile_eval_purpose_template_family_entry(
    *,
    template_family_id: str,
    runtime_profile_family_id: str,
    default_rollout_class: str,
    planner_metadata_policy_id: str,
) -> dict[str, str]:
    payload = {
        "templateFamilyId": template_family_id,
        "runtimeProfileFamilyId": runtime_profile_family_id,
        "defaultRolloutClass": default_rollout_class,
        "plannerMetadataPolicyId": planner_metadata_policy_id,
    }
    return payload


def build_optimizer_runtime_profile_planner_metadata_policy_entry(
    *,
    metadata_policy_id: str,
    metadata_contract_family_id: str,
    metadata_contract_id: str,
    default_window_set_batch_type: str,
    default_comparison_dimension: str,
    window_set_batch_type_priority: list[str] | None = None,
    comparison_dimension_priority: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "metadataPolicyId": metadata_policy_id,
        "metadataContractFamilyId": metadata_contract_family_id,
        "metadataContractId": metadata_contract_id,
        "defaultWindowSetBatchType": default_window_set_batch_type,
        "defaultComparisonDimension": default_comparison_dimension,
        "windowSetBatchTypePriority": list(
            window_set_batch_type_priority
            or [
                "purpose_template",
                "purpose_template_family",
                "metadata_policy_default",
                "fallback_default",
            ]
        ),
        "comparisonDimensionPriority": list(
            comparison_dimension_priority
            or [
                "purpose_template",
                "purpose_template_family",
                "metadata_policy_default",
                "fallback_default",
            ]
        ),
    }


def build_optimizer_runtime_profile_planner_metadata_contract_entry(
    *,
    metadata_contract_family_id: str,
    metadata_contract_id: str,
    allowed_window_set_batch_types: list[str],
    allowed_comparison_dimensions: list[str],
) -> dict[str, Any]:
    return {
        "metadataContractFamilyId": metadata_contract_family_id,
        "metadataContractId": metadata_contract_id,
        "allowedWindowSetBatchTypes": list(allowed_window_set_batch_types),
        "allowedComparisonDimensions": list(allowed_comparison_dimensions),
    }


def build_optimizer_runtime_profile_planner_metadata_contract_family_entry(
    *,
    metadata_contract_family_id: str,
    default_metadata_contract_id: str,
    allowed_window_set_batch_types: list[str],
    allowed_comparison_dimensions: list[str],
) -> dict[str, Any]:
    return {
        "metadataContractFamilyId": metadata_contract_family_id,
        "defaultMetadataContractId": default_metadata_contract_id,
        "allowedWindowSetBatchTypes": list(allowed_window_set_batch_types),
        "allowedComparisonDimensions": list(allowed_comparison_dimensions),
    }


def build_optimizer_runtime_profile_rollout_rule_entry(
    *,
    rule_id: str,
    rollout_class: str,
    batch_window_label_prefix: str | None = None,
    scenario_label_prefix: str | None = None,
    window_set_purpose: str | None = None,
    history_window_label_prefix: str | None = None,
    mode: str | None = None,
    comparison_dimension: str | None = None,
    window_set_batch_type: str | None = None,
) -> dict[str, str]:
    payload = {
        "ruleId": rule_id,
        "rolloutClass": rollout_class,
    }
    if batch_window_label_prefix is not None:
        payload["batchWindowLabelPrefix"] = batch_window_label_prefix
    if scenario_label_prefix is not None:
        payload["scenarioLabelPrefix"] = scenario_label_prefix
    if window_set_purpose is not None:
        payload["windowSetPurpose"] = window_set_purpose
    if history_window_label_prefix is not None:
        payload["historyWindowLabelPrefix"] = history_window_label_prefix
    if mode is not None:
        payload["mode"] = mode
    if comparison_dimension is not None:
        payload["comparisonDimension"] = comparison_dimension
    if window_set_batch_type is not None:
        payload["windowSetBatchType"] = window_set_batch_type
    return payload


def build_default_optimizer_runtime_profile_rollout_family_policies(
    *,
    family_id: str = DEFAULT_RUNTIME_PROFILE_FAMILY_ID,
    active_lane: str = RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
    default_lane: str | None = None,
    default_rollout_class: str = DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS,
    preview_enabled: bool = True,
    rollout_strategy: str = DEFAULT_RUNTIME_PROFILE_ROLLOUT_STRATEGY,
) -> list[dict[str, Any]]:
    resolved_default_lane = default_lane or active_lane
    preview_class_lane = (
        RUNTIME_PROFILE_CATALOG_LANE_PREVIEW
        if preview_enabled
        else resolved_default_lane
    )
    return [
        build_optimizer_runtime_profile_rollout_family_policy(
            family_id=family_id,
            active_lane=active_lane,
            default_lane=resolved_default_lane,
            default_rollout_class=default_rollout_class,
            allowed_lanes=list(RUNTIME_PROFILE_CATALOG_LANES),
            rollout_classes=[
                build_optimizer_runtime_profile_rollout_class_entry(
                    rollout_class=DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS,
                    selected_lane=resolved_default_lane,
                ),
                build_optimizer_runtime_profile_rollout_class_entry(
                    rollout_class=PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS,
                    selected_lane=preview_class_lane,
                ),
            ],
            preview_lane=RUNTIME_PROFILE_CATALOG_LANE_PREVIEW,
            preview_enabled=preview_enabled,
            rollout_strategy=rollout_strategy,
        )
    ]


def build_optimizer_runtime_profile_rollout_policy_payload(
    *,
    policy_id: str,
    schema_version: str,
    policy_family: str,
    policy_version: str,
    generated_at: str,
    runtime_profile_family_registry_reference: dict[str, str],
    family_policies: list[dict[str, Any]],
) -> dict[str, Any]:
    default_family_id = DEFAULT_RUNTIME_PROFILE_FAMILY_ID
    if family_policies:
        first_family_id = family_policies[0].get("familyId")
        if isinstance(first_family_id, str) and first_family_id:
            default_family_id = first_family_id
    return {
        "schemaVersion": schema_version,
        "policyId": policy_id,
        "policyFamily": policy_family,
        "policyVersion": policy_version,
        "generatedAt": generated_at,
        "generatedFrom": {
            "familyPolicyCount": len(family_policies),
            "runtimeProfileFamilyRegistryId": runtime_profile_family_registry_reference[
                "registryId"
            ],
        },
        "runtimeProfileFamilyRegistryReference": dict(
            runtime_profile_family_registry_reference
        ),
        "familyPolicies": family_policies,
        "plannerMetadataContractFamilies": [
            build_optimizer_runtime_profile_planner_metadata_contract_family_entry(
                metadata_contract_family_id="standard_replay_metadata_contract_family",
                default_metadata_contract_id="standard_replay_metadata_contract",
                allowed_window_set_batch_types=["standard_replay"],
                allowed_comparison_dimensions=[
                    "historyBatchLabel",
                    "historyWindowLabel",
                    "mode",
                    "evaluationWindow",
                ],
            ),
            build_optimizer_runtime_profile_planner_metadata_contract_family_entry(
                metadata_contract_family_id=(
                    "cross_profile_compare_metadata_contract_family"
                ),
                default_metadata_contract_id=(
                    "cross_profile_compare_metadata_contract"
                ),
                allowed_window_set_batch_types=["cross_profile_comparison"],
                allowed_comparison_dimensions=[
                    "rankingProfileId",
                    "rankingSnapshotId",
                ],
            ),
        ],
        "plannerMetadataContracts": [
            build_optimizer_runtime_profile_planner_metadata_contract_entry(
                metadata_contract_family_id="standard_replay_metadata_contract_family",
                metadata_contract_id="standard_replay_metadata_contract",
                allowed_window_set_batch_types=["standard_replay"],
                allowed_comparison_dimensions=[
                    "historyBatchLabel",
                    "historyWindowLabel",
                    "mode",
                    "evaluationWindow",
                ],
            ),
            build_optimizer_runtime_profile_planner_metadata_contract_entry(
                metadata_contract_family_id=(
                    "cross_profile_compare_metadata_contract_family"
                ),
                metadata_contract_id="cross_profile_compare_metadata_contract",
                allowed_window_set_batch_types=["cross_profile_comparison"],
                allowed_comparison_dimensions=[
                    "rankingProfileId",
                    "rankingSnapshotId",
                ],
            ),
        ],
        "plannerMetadataPolicies": [
            build_optimizer_runtime_profile_planner_metadata_policy_entry(
                metadata_policy_id="standard_replay_metadata_policy",
                metadata_contract_family_id="standard_replay_metadata_contract_family",
                metadata_contract_id="standard_replay_metadata_contract",
                default_window_set_batch_type="standard_replay",
                default_comparison_dimension="historyBatchLabel",
            ),
            build_optimizer_runtime_profile_planner_metadata_policy_entry(
                metadata_policy_id="cross_profile_compare_metadata_policy",
                metadata_contract_family_id=(
                    "cross_profile_compare_metadata_contract_family"
                ),
                metadata_contract_id="cross_profile_compare_metadata_contract",
                default_window_set_batch_type="cross_profile_comparison",
                default_comparison_dimension="rankingProfileId",
            ),
        ],
        "evalPurposeTemplateFamilies": [
            build_optimizer_runtime_profile_eval_purpose_template_family_entry(
                template_family_id="preview_validation_family",
                runtime_profile_family_id=default_family_id,
                default_rollout_class=PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS,
                planner_metadata_policy_id="standard_replay_metadata_policy",
            ),
            build_optimizer_runtime_profile_eval_purpose_template_family_entry(
                template_family_id="cross_profile_validation_family",
                runtime_profile_family_id=default_family_id,
                default_rollout_class=PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS,
                planner_metadata_policy_id="cross_profile_compare_metadata_policy",
            ),
        ],
        "evalPurposeTemplates": [
            build_optimizer_runtime_profile_eval_purpose_template_entry(
                template_id="preview_validation_template",
                template_family_id="preview_validation_family",
            ),
            build_optimizer_runtime_profile_eval_purpose_template_entry(
                template_id="profile_compare_validation_template",
                template_family_id="cross_profile_validation_family",
            ),
        ],
        "evalPurposePolicies": [
            build_optimizer_runtime_profile_eval_purpose_policy_entry(
                purpose_policy_id="preview_validation_default",
                window_set_purpose="preview_validation",
                template_id="preview_validation_template",
            ),
            build_optimizer_runtime_profile_eval_purpose_policy_entry(
                purpose_policy_id="profile_compare_validation_default",
                window_set_purpose="profile_compare_validation",
                template_id="profile_compare_validation_template",
            ),
        ],
        "rolloutClassRules": [
            build_optimizer_runtime_profile_rollout_rule_entry(
                rule_id="preview_batch_label",
                rollout_class=PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS,
                batch_window_label_prefix="preview:",
            ),
            build_optimizer_runtime_profile_rollout_rule_entry(
                rule_id="preview_weekly_shadow_rehearsal",
                rollout_class=PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS,
                window_set_purpose="weekly_shadow_rehearsal",
                history_window_label_prefix="historical_",
                mode="daily_with_weekly_promotion",
            ),
            build_optimizer_runtime_profile_rollout_rule_entry(
                rule_id="preview_scenario_prefix",
                rollout_class=PREVIEW_RUNTIME_PROFILE_ROLLOUT_CLASS,
                scenario_label_prefix="preview_",
            ),
        ],
    }


def build_optimizer_runtime_profile_rollout_policy_reference(
    *,
    policy_id: str,
    schema_version: str,
    policy_family: str,
    policy_version: str,
    family_id: str,
) -> dict[str, str]:
    return {
        "policyId": policy_id,
        "schemaVersion": schema_version,
        "policyFamily": policy_family,
        "policyVersion": policy_version,
        "familyId": family_id,
    }


def build_default_runtime_profile_family_registry_rollout_reference() -> dict[str, str]:
    return {
        "registryId": DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID,
        "schemaVersion": OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
    }


def resolve_runtime_profile_lane_from_rollout_policy(
    *,
    family_id: str,
    requested_lane: str | None,
    requested_rollout_class: str | None,
    rollout_policy: dict[str, Any],
) -> dict[str, str]:
    for family_policy in rollout_policy.get("familyPolicies", []):
        if not isinstance(family_policy, dict):
            continue
        if family_policy.get("familyId") != family_id:
            continue
        default_lane = _require_string(
            family_policy.get("defaultLane"),
            label=f"rollout policy family {family_id!r}.defaultLane",
        )
        active_lane = _require_string(
            family_policy.get("activeLane"),
            label=f"rollout policy family {family_id!r}.activeLane",
        )
        preview_lane = _require_string(
            family_policy.get("previewLane"),
            label=f"rollout policy family {family_id!r}.previewLane",
        )
        preview_enabled = family_policy.get("previewEnabled")
        if not isinstance(preview_enabled, bool):
            raise ValueError(
                f"rollout policy family {family_id!r}.previewEnabled must be a boolean"
            )
        allowed_lanes = family_policy.get("allowedLanes")
        if not isinstance(allowed_lanes, list) or not allowed_lanes:
            raise ValueError(
                f"rollout policy family {family_id!r}.allowedLanes must be a non-empty list"
            )
        default_rollout_class = _require_string(
            family_policy.get("defaultRolloutClass"),
            label=f"rollout policy family {family_id!r}.defaultRolloutClass",
        )
        rollout_classes = family_policy.get("rolloutClasses")
        if not isinstance(rollout_classes, list) or not rollout_classes:
            raise ValueError(
                f"rollout policy family {family_id!r}.rolloutClasses must be a non-empty list"
            )
        rollout_class_to_lane: dict[str, str] = {}
        for class_index, rollout_class_entry in enumerate(rollout_classes):
            class_label = (
                f"rollout policy family {family_id!r}.rolloutClasses[{class_index}]"
            )
            if not isinstance(rollout_class_entry, dict):
                raise ValueError(f"{class_label} must be an object")
            rollout_class = _require_string(
                rollout_class_entry.get("rolloutClass"),
                label=f"{class_label}.rolloutClass",
            )
            selected_lane = _require_string(
                rollout_class_entry.get("selectedLane"),
                label=f"{class_label}.selectedLane",
            )
            rollout_class_to_lane[rollout_class] = selected_lane
        resolved_rollout_class = requested_rollout_class or default_rollout_class
        resolved_lane = requested_lane or rollout_class_to_lane.get(
            resolved_rollout_class, default_lane
        )
        if resolved_lane not in allowed_lanes:
            allowed = ", ".join(sorted(set(str(lane) for lane in allowed_lanes)))
            raise ValueError(
                f"rollout policy family {family_id!r} does not allow lane {resolved_lane!r}; allowed lanes are [{allowed}]"
            )
        if resolved_lane == preview_lane and not preview_enabled:
            raise ValueError(
                f"rollout policy family {family_id!r} does not currently enable preview lane {preview_lane!r}"
            )
        return {
            "selectedLane": resolved_lane,
            "selectedRolloutClass": resolved_rollout_class,
            "laneSelectionSource": "explicit"
            if requested_lane is not None
            else (
                "policy_class"
                if requested_rollout_class is not None
                else "policy_default"
            ),
            "activeLane": active_lane,
            "defaultLane": default_lane,
            "defaultRolloutClass": default_rollout_class,
            "rolloutStrategy": _require_string(
                family_policy.get("rolloutStrategy"),
                label=f"rollout policy family {family_id!r}.rolloutStrategy",
            ),
        }
    raise ValueError(
        f"optimizer runtime profile rollout policy does not define familyId {family_id!r}"
    )


def resolve_runtime_profile_eval_purpose_policy(
    *,
    window_set_purpose: str,
    requested_family_id: str | None,
    rollout_policy: dict[str, Any],
) -> dict[str, str] | None:
    planner_metadata_contract_families = rollout_policy.get(
        "plannerMetadataContractFamilies", []
    )
    planner_metadata_contract_family_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(planner_metadata_contract_families, list):
        for metadata_contract_family in planner_metadata_contract_families:
            if not isinstance(metadata_contract_family, dict):
                continue
            metadata_contract_family_id = metadata_contract_family.get(
                "metadataContractFamilyId"
            )
            if (
                isinstance(metadata_contract_family_id, str)
                and metadata_contract_family_id
            ):
                planner_metadata_contract_family_by_id[
                    metadata_contract_family_id
                ] = metadata_contract_family
    planner_metadata_contracts = rollout_policy.get("plannerMetadataContracts", [])
    planner_metadata_contract_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(planner_metadata_contracts, list):
        for metadata_contract in planner_metadata_contracts:
            if not isinstance(metadata_contract, dict):
                continue
            metadata_contract_id = metadata_contract.get("metadataContractId")
            if isinstance(metadata_contract_id, str) and metadata_contract_id:
                planner_metadata_contract_by_id[metadata_contract_id] = metadata_contract
    planner_metadata_policies = rollout_policy.get("plannerMetadataPolicies", [])
    planner_metadata_policy_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(planner_metadata_policies, list):
        for metadata_policy in planner_metadata_policies:
            if not isinstance(metadata_policy, dict):
                continue
            metadata_policy_id = metadata_policy.get("metadataPolicyId")
            if isinstance(metadata_policy_id, str) and metadata_policy_id:
                planner_metadata_policy_by_id[metadata_policy_id] = metadata_policy
    purpose_template_families = rollout_policy.get("evalPurposeTemplateFamilies", [])
    purpose_template_family_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(purpose_template_families, list):
        for purpose_template_family in purpose_template_families:
            if not isinstance(purpose_template_family, dict):
                continue
            template_family_id = purpose_template_family.get("templateFamilyId")
            if isinstance(template_family_id, str) and template_family_id:
                purpose_template_family_by_id[template_family_id] = (
                    purpose_template_family
                )
    purpose_templates = rollout_policy.get("evalPurposeTemplates", [])
    purpose_template_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(purpose_templates, list):
        for purpose_template in purpose_templates:
            if not isinstance(purpose_template, dict):
                continue
            template_id = purpose_template.get("templateId")
            if isinstance(template_id, str) and template_id:
                purpose_template_by_id[template_id] = purpose_template
    purpose_policies = rollout_policy.get("evalPurposePolicies", [])
    if not isinstance(purpose_policies, list):
        return None
    for purpose_policy in purpose_policies:
        if not isinstance(purpose_policy, dict):
            continue
        if purpose_policy.get("windowSetPurpose") != window_set_purpose:
            continue
        template_id = purpose_policy.get("templateId")
        purpose_template = None
        if template_id is not None:
            template_id = _require_string(
                template_id,
                label=f"evalPurposePolicies[{window_set_purpose!r}].templateId",
            )
            purpose_template = purpose_template_by_id.get(template_id)
            if purpose_template is None:
                raise ValueError(
                    f"evalPurposePolicies[{window_set_purpose!r}].templateId references unknown template {template_id!r}"
                )
            template_family_id = _require_string(
                purpose_template.get("templateFamilyId"),
                label=f"evalPurposeTemplates[{template_id!r}].templateFamilyId",
            )
            purpose_template_family = purpose_template_family_by_id.get(
                template_family_id
            )
            if purpose_template_family is None:
                raise ValueError(
                    f"evalPurposeTemplates[{template_id!r}].templateFamilyId references unknown template family {template_family_id!r}"
                )
            family_id = _require_string(
                purpose_template_family.get("runtimeProfileFamilyId"),
                label=(
                    f"evalPurposeTemplateFamilies[{template_family_id!r}].runtimeProfileFamilyId"
                ),
            )
            planner_metadata_policy_id = _require_string(
                purpose_template_family.get("plannerMetadataPolicyId"),
                label=(
                    f"evalPurposeTemplateFamilies[{template_family_id!r}].plannerMetadataPolicyId"
                ),
            )
            planner_metadata_policy = planner_metadata_policy_by_id.get(
                planner_metadata_policy_id
            )
            if planner_metadata_policy is None:
                raise ValueError(
                    f"evalPurposeTemplateFamilies[{template_family_id!r}].plannerMetadataPolicyId references unknown metadata policy {planner_metadata_policy_id!r}"
                )
            planner_metadata_contract_family_id = _require_string(
                planner_metadata_policy.get("metadataContractFamilyId"),
                label=(
                    f"plannerMetadataPolicies[{planner_metadata_policy_id!r}].metadataContractFamilyId"
                ),
            )
            planner_metadata_contract_family = (
                planner_metadata_contract_family_by_id.get(
                    planner_metadata_contract_family_id
                )
            )
            if planner_metadata_contract_family is None:
                raise ValueError(
                    "plannerMetadataPolicies"
                    f"[{planner_metadata_policy_id!r}].metadataContractFamilyId references "
                    f"unknown metadata contract family {planner_metadata_contract_family_id!r}"
                )
            planner_metadata_contract_id = _require_string(
                planner_metadata_policy.get("metadataContractId"),
                label=(
                    f"plannerMetadataPolicies[{planner_metadata_policy_id!r}].metadataContractId"
                ),
            )
            planner_metadata_contract = planner_metadata_contract_by_id.get(
                planner_metadata_contract_id
            )
            if planner_metadata_contract is None:
                raise ValueError(
                    f"plannerMetadataPolicies[{planner_metadata_policy_id!r}].metadataContractId references unknown metadata contract {planner_metadata_contract_id!r}"
                )
            resolved_contract_family_id = _require_string(
                planner_metadata_contract.get("metadataContractFamilyId"),
                label=(
                    f"plannerMetadataContracts[{planner_metadata_contract_id!r}].metadataContractFamilyId"
                ),
            )
            if resolved_contract_family_id != planner_metadata_contract_family_id:
                raise ValueError(
                    "planner metadata policy "
                    f"{planner_metadata_policy_id!r} references contract family "
                    f"{planner_metadata_contract_family_id!r} but its contract "
                    f"{planner_metadata_contract_id!r} belongs to "
                    f"{resolved_contract_family_id!r}"
                )
        else:
            template_family_id = None
            purpose_template_family = None
            planner_metadata_policy_id = None
            planner_metadata_policy = None
            planner_metadata_contract_family_id = None
            planner_metadata_contract_family = None
            planner_metadata_contract_id = None
            planner_metadata_contract = None
            family_id = _require_string(
                purpose_policy.get("familyId"),
                label=f"evalPurposePolicies[{window_set_purpose!r}].familyId",
            )
        if (
            requested_family_id is not None
            and requested_family_id
            and family_id != requested_family_id
        ):
            continue
        resolved = {
            "purposePolicyId": _require_string(
                purpose_policy.get("purposePolicyId"),
                label=f"evalPurposePolicies[{window_set_purpose!r}].purposePolicyId",
            ),
            "windowSetPurpose": _require_string(
                purpose_policy.get("windowSetPurpose"),
                label=f"evalPurposePolicies[{window_set_purpose!r}].windowSetPurpose",
            ),
            "familyId": family_id,
        }
        if template_id is not None:
            resolved["purposeTemplateId"] = template_id
            resolved["purposeTemplateFamilyId"] = template_family_id
            resolved["plannerMetadataPolicyId"] = planner_metadata_policy_id
            resolved["plannerMetadataContractFamilyId"] = (
                planner_metadata_contract_family_id
            )
            resolved["plannerMetadataContractId"] = planner_metadata_contract_id
            default_rollout_class = purpose_template.get("defaultRolloutClass")
            if default_rollout_class is None:
                default_rollout_class = purpose_template_family.get(
                    "defaultRolloutClass"
                )
                default_rollout_class_source = "purpose_template_family"
            else:
                default_rollout_class_source = "purpose_template"
        else:
            default_rollout_class = purpose_policy.get("defaultRolloutClass")
            default_rollout_class_source = "purpose_policy"
        resolved["defaultRolloutClass"] = _require_string(
            default_rollout_class,
            label=(
                f"evalPurposeTemplates[{template_id!r}].defaultRolloutClass"
                if template_id is not None
                else f"evalPurposePolicies[{window_set_purpose!r}].defaultRolloutClass"
            ),
        )
        resolved["defaultRolloutClassSource"] = default_rollout_class_source
        if template_id is not None:
            def _resolve_planner_metadata_value(
                *,
                field_key: str,
                policy_default_key: str,
                priority_field_name: str,
            ) -> tuple[str | None, str | None]:
                assert planner_metadata_policy is not None
                priorities = planner_metadata_policy.get(priority_field_name)
                if not isinstance(priorities, list) or not priorities:
                    raise ValueError(
                        f"plannerMetadataPolicies[{planner_metadata_policy_id!r}].{priority_field_name} must be a non-empty list"
                    )
                template_value = purpose_template.get(field_key)
                family_value = purpose_template_family.get(field_key)
                metadata_policy_default = planner_metadata_policy.get(policy_default_key)
                candidate_values: dict[str, Any] = {
                    "purpose_template": template_value,
                    "purpose_template_family": family_value,
                    "metadata_policy_default": metadata_policy_default,
                    "fallback_default": None,
                }
                for priority_index, priority in enumerate(priorities):
                    priority_label = (
                        f"plannerMetadataPolicies[{planner_metadata_policy_id!r}]."
                        f"{priority_field_name}[{priority_index}]"
                    )
                    priority_value = _require_string(priority, label=priority_label)
                    if priority_value not in PLANNER_METADATA_SELECTION_PRIORITIES:
                        allowed = ", ".join(sorted(PLANNER_METADATA_SELECTION_PRIORITIES))
                        raise ValueError(
                            f"{priority_label} must be one of [{allowed}], got {priority_value!r}"
                        )
                    candidate_value = candidate_values.get(priority_value)
                    if candidate_value is None:
                        continue
                    return _require_string(
                        candidate_value,
                        label=(
                            f"plannerMetadataPolicies[{planner_metadata_policy_id!r}].{policy_default_key}"
                            if priority_value == "metadata_policy_default"
                            else (
                                f"evalPurposeTemplates[{template_id!r}].{field_key}"
                                if priority_value == "purpose_template"
                                else f"evalPurposeTemplateFamilies[{template_family_id!r}].{field_key}"
                            )
                        ),
                    ), priority_value
                return None, None

            default_window_set_batch_type, default_window_set_batch_type_source = (
                _resolve_planner_metadata_value(
                    field_key="defaultWindowSetBatchType",
                    policy_default_key="defaultWindowSetBatchType",
                    priority_field_name="windowSetBatchTypePriority",
                )
            )
            default_comparison_dimension, default_comparison_dimension_source = (
                _resolve_planner_metadata_value(
                    field_key="defaultComparisonDimension",
                    policy_default_key="defaultComparisonDimension",
                    priority_field_name="comparisonDimensionPriority",
                )
            )
        else:
            default_window_set_batch_type = purpose_policy.get(
                "defaultWindowSetBatchType"
            )
            default_comparison_dimension = purpose_policy.get(
                "defaultComparisonDimension"
            )
            default_window_set_batch_type_source = "purpose_policy"
            default_comparison_dimension_source = "purpose_policy"
        if default_window_set_batch_type is not None:
            resolved["defaultWindowSetBatchType"] = default_window_set_batch_type
            resolved["defaultWindowSetBatchTypeSource"] = (
                default_window_set_batch_type_source
            )
        if default_comparison_dimension is not None:
            resolved["defaultComparisonDimension"] = default_comparison_dimension
            resolved["defaultComparisonDimensionSource"] = (
                default_comparison_dimension_source
            )
        return resolved
    return None


def validate_runtime_profile_planner_metadata_contract_selection(
    *,
    metadata_contract_id: str,
    window_set_batch_type: str,
    comparison_dimension: str,
    rollout_policy: dict[str, Any],
) -> None:
    metadata_contracts = rollout_policy.get("plannerMetadataContracts", [])
    if not isinstance(metadata_contracts, list):
        raise ValueError("plannerMetadataContracts must be a list")
    for metadata_contract in metadata_contracts:
        if not isinstance(metadata_contract, dict):
            continue
        if metadata_contract.get("metadataContractId") != metadata_contract_id:
            continue
        allowed_window_set_batch_types = metadata_contract.get(
            "allowedWindowSetBatchTypes"
        )
        if (
            not isinstance(allowed_window_set_batch_types, list)
            or window_set_batch_type not in allowed_window_set_batch_types
        ):
            allowed = ", ".join(
                sorted(
                    value
                    for value in allowed_window_set_batch_types or []
                    if isinstance(value, str) and value
                )
            )
            raise ValueError(
                "planner metadata contract "
                f"{metadata_contract_id!r} does not allow windowSetBatchType "
                f"{window_set_batch_type!r}; allowed values are [{allowed}]"
            )
        allowed_comparison_dimensions = metadata_contract.get(
            "allowedComparisonDimensions"
        )
        if (
            not isinstance(allowed_comparison_dimensions, list)
            or comparison_dimension not in allowed_comparison_dimensions
        ):
            allowed = ", ".join(
                sorted(
                    value
                    for value in allowed_comparison_dimensions or []
                    if isinstance(value, str) and value
                )
            )
            raise ValueError(
                "planner metadata contract "
                f"{metadata_contract_id!r} does not allow comparisonDimension "
                f"{comparison_dimension!r}; allowed values are [{allowed}]"
            )
        return
    raise ValueError(
        f"planner metadata contract {metadata_contract_id!r} was not found"
    )


def _window_set_matches_rollout_rule(
    rule: dict[str, Any],
    *,
    window_set_id: str,
    batch_window_label: str,
    comparison_dimension: str,
    window_set_purpose: str,
    window_set_batch_type: str,
    windows: list[dict[str, Any]],
) -> bool:
    del window_set_id
    selectors = 0
    batch_window_label_prefix = rule.get("batchWindowLabelPrefix")
    if batch_window_label_prefix is not None:
        selectors += 1
        if not isinstance(batch_window_label_prefix, str) or not batch_window_label.startswith(
            batch_window_label_prefix
        ):
            return False
    expected_window_set_purpose = rule.get("windowSetPurpose")
    if expected_window_set_purpose is not None:
        selectors += 1
        if (
            not isinstance(expected_window_set_purpose, str)
            or window_set_purpose != expected_window_set_purpose
        ):
            return False
    expected_window_set_batch_type = rule.get("windowSetBatchType")
    if expected_window_set_batch_type is not None:
        selectors += 1
        if (
            not isinstance(expected_window_set_batch_type, str)
            or window_set_batch_type != expected_window_set_batch_type
        ):
            return False
    expected_comparison_dimension = rule.get("comparisonDimension")
    if expected_comparison_dimension is not None:
        selectors += 1
        if (
            not isinstance(expected_comparison_dimension, str)
            or comparison_dimension != expected_comparison_dimension
        ):
            return False
    window_level_selector_count = 0
    scenario_label_prefix = rule.get("scenarioLabelPrefix")
    if scenario_label_prefix is not None:
        window_level_selector_count += 1
        if not isinstance(scenario_label_prefix, str):
            return False
    history_window_label_prefix = rule.get("historyWindowLabelPrefix")
    if history_window_label_prefix is not None:
        window_level_selector_count += 1
        if not isinstance(history_window_label_prefix, str):
            return False
    expected_mode = rule.get("mode")
    if expected_mode is not None:
        window_level_selector_count += 1
        if not isinstance(expected_mode, str):
            return False
    if window_level_selector_count > 0:
        selectors += window_level_selector_count
        if not any(
            isinstance(window, dict)
            and (
                scenario_label_prefix is None
                or (
                    isinstance(window.get("scenarioLabel"), str)
                    and window["scenarioLabel"].startswith(scenario_label_prefix)
                )
            )
            and (
                history_window_label_prefix is None
                or (
                    isinstance(window.get("historyWindowLabel"), str)
                    and window["historyWindowLabel"].startswith(
                        history_window_label_prefix
                    )
                )
            )
            and (expected_mode is None or window.get("mode") == expected_mode)
            for window in windows
        ):
            return False
    return selectors > 0


def resolve_runtime_profile_routing_from_rollout_policy(
    *,
    family_id: str,
    requested_lane: str | None,
    requested_rollout_class: str | None,
    default_rollout_class: str | None,
    default_rollout_class_source: str | None,
    purpose_policy_id: str | None,
    purpose_template_id: str | None,
    purpose_template_family_id: str | None,
    planner_metadata_policy_id: str | None,
    planner_metadata_contract_family_id: str | None,
    planner_metadata_contract_id: str | None,
    rollout_policy: dict[str, Any],
    window_set_id: str,
    batch_window_label: str,
    comparison_dimension: str,
    window_set_purpose: str,
    window_set_batch_type: str,
    windows: list[dict[str, Any]],
) -> dict[str, str]:
    matched_rollout_rule_id: str | None = None
    inferred_rollout_class = requested_rollout_class
    if inferred_rollout_class is None and requested_lane is None:
        for rollout_rule in rollout_policy.get("rolloutClassRules", []):
            if not isinstance(rollout_rule, dict):
                continue
            if not _window_set_matches_rollout_rule(
                rollout_rule,
                window_set_id=window_set_id,
                batch_window_label=batch_window_label,
                comparison_dimension=comparison_dimension,
                window_set_purpose=window_set_purpose,
                window_set_batch_type=window_set_batch_type,
                windows=windows,
            ):
                continue
            matched_rollout_rule_id = _require_string(
                rollout_rule.get("ruleId"),
                label="rolloutClassRules[*].ruleId",
            )
            inferred_rollout_class = _require_string(
                rollout_rule.get("rolloutClass"),
                label=f"rolloutClassRules[{matched_rollout_rule_id!r}].rolloutClass",
            )
            break
    if (
        matched_rollout_rule_id is None
        and inferred_rollout_class is None
        and requested_lane is None
        and default_rollout_class is not None
    ):
        inferred_rollout_class = default_rollout_class
    resolution = resolve_runtime_profile_lane_from_rollout_policy(
        family_id=family_id,
        requested_lane=requested_lane,
        requested_rollout_class=inferred_rollout_class,
        rollout_policy=rollout_policy,
    )
    if matched_rollout_rule_id is not None and requested_lane is None and requested_rollout_class is None:
        resolution["laneSelectionSource"] = "policy_rule"
        resolution["matchedRolloutRuleId"] = matched_rollout_rule_id
    elif (
        matched_rollout_rule_id is None
        and requested_lane is None
        and requested_rollout_class is None
        and default_rollout_class is not None
        and default_rollout_class_source is not None
    ):
        resolution["laneSelectionSource"] = default_rollout_class_source
        if purpose_policy_id is not None:
            resolution["purposePolicyId"] = purpose_policy_id
        if purpose_template_id is not None:
            resolution["purposeTemplateId"] = purpose_template_id
        if purpose_template_family_id is not None:
            resolution["purposeTemplateFamilyId"] = purpose_template_family_id
        if planner_metadata_policy_id is not None:
            resolution["plannerMetadataPolicyId"] = planner_metadata_policy_id
        if planner_metadata_contract_family_id is not None:
            resolution["plannerMetadataContractFamilyId"] = (
                planner_metadata_contract_family_id
            )
        if planner_metadata_contract_id is not None:
            resolution["plannerMetadataContractId"] = planner_metadata_contract_id
    return resolution


def validate_optimizer_runtime_profile_rollout_policy_payload(
    payload: dict[str, Any],
) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSIONS:
        allowed = ", ".join(
            sorted(OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSIONS)
        )
        raise ValueError(
            "optimizer runtime profile rollout policy schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    _require_string(payload.get("policyId"), label="policyId")
    _require_string(payload.get("policyFamily"), label="policyFamily")
    _require_string(payload.get("policyVersion"), label="policyVersion")
    _require_string(payload.get("generatedAt"), label="generatedAt")
    registry_reference = payload.get("runtimeProfileFamilyRegistryReference")
    if not isinstance(registry_reference, dict):
        raise ValueError(
            "runtimeProfileFamilyRegistryReference must be an object"
        )
    _require_string(
        registry_reference.get("registryId"),
        label="runtimeProfileFamilyRegistryReference.registryId",
    )
    registry_schema_version = _require_string(
        registry_reference.get("schemaVersion"),
        label="runtimeProfileFamilyRegistryReference.schemaVersion",
    )
    if registry_schema_version not in {
        OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
        OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION,
    }:
        allowed = ", ".join(
            sorted(
                {
                    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
                    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION,
                }
            )
        )
        raise ValueError(
            "runtimeProfileFamilyRegistryReference.schemaVersion must be one of "
            f"[{allowed}], got {registry_schema_version!r}"
        )
    family_policies = payload.get("familyPolicies")
    if not isinstance(family_policies, list) or not family_policies:
        raise ValueError(
            "optimizer runtime profile rollout policy must include a non-empty `familyPolicies` list"
        )
    seen_family_ids: set[str] = set()
    family_to_rollout_classes: dict[str, set[str]] = {}
    for index, family_policy in enumerate(family_policies):
        label = f"familyPolicies[{index}]"
        if not isinstance(family_policy, dict):
            raise ValueError(f"{label} must be an object")
        family_id = _require_string(family_policy.get("familyId"), label=f"{label}.familyId")
        if family_id in seen_family_ids:
            raise ValueError(
                f"optimizer runtime profile rollout policy contains duplicate familyId {family_id!r}"
            )
        seen_family_ids.add(family_id)
        active_lane = _require_string(
            family_policy.get("activeLane"), label=f"{label}.activeLane"
        )
        default_lane = _require_string(
            family_policy.get("defaultLane"), label=f"{label}.defaultLane"
        )
        default_rollout_class = _require_string(
            family_policy.get("defaultRolloutClass"),
            label=f"{label}.defaultRolloutClass",
        )
        preview_lane = _require_string(
            family_policy.get("previewLane"), label=f"{label}.previewLane"
        )
        preview_enabled = family_policy.get("previewEnabled")
        if not isinstance(preview_enabled, bool):
            raise ValueError(f"{label}.previewEnabled must be a boolean")
        _require_string(
            family_policy.get("rolloutStrategy"),
            label=f"{label}.rolloutStrategy",
        )
        allowed_lanes = family_policy.get("allowedLanes")
        if not isinstance(allowed_lanes, list) or not allowed_lanes:
            raise ValueError(f"{label}.allowedLanes must be a non-empty list")
        normalized_allowed_lanes: list[str] = []
        for lane_index, allowed_lane in enumerate(allowed_lanes):
            lane_label = f"{label}.allowedLanes[{lane_index}]"
            lane_value = _require_string(allowed_lane, label=lane_label)
            if lane_value not in RUNTIME_PROFILE_CATALOG_LANES:
                allowed = ", ".join(RUNTIME_PROFILE_CATALOG_LANES)
                raise ValueError(
                    f"{lane_label} must be one of [{allowed}], got {lane_value!r}"
                )
            if lane_value in normalized_allowed_lanes:
                raise ValueError(f"{lane_label} is duplicated within {label}")
            normalized_allowed_lanes.append(lane_value)
        for key, lane_value in (
            ("activeLane", active_lane),
            ("defaultLane", default_lane),
            ("previewLane", preview_lane),
        ):
            if lane_value not in normalized_allowed_lanes:
                raise ValueError(
                    f"{label}.{key} must also appear in {label}.allowedLanes"
                )
        if not preview_enabled and (
            active_lane == preview_lane or default_lane == preview_lane
        ):
            raise ValueError(
                f"{label} cannot select previewLane as active/default when previewEnabled is false"
            )
        rollout_classes = family_policy.get("rolloutClasses")
        if not isinstance(rollout_classes, list) or not rollout_classes:
            raise ValueError(f"{label}.rolloutClasses must be a non-empty list")
        rollout_class_to_lane: dict[str, str] = {}
        for class_index, rollout_class_entry in enumerate(rollout_classes):
            class_label = f"{label}.rolloutClasses[{class_index}]"
            if not isinstance(rollout_class_entry, dict):
                raise ValueError(f"{class_label} must be an object")
            rollout_class = _require_string(
                rollout_class_entry.get("rolloutClass"),
                label=f"{class_label}.rolloutClass",
            )
            if rollout_class in rollout_class_to_lane:
                raise ValueError(
                    f"{class_label}.rolloutClass is duplicated within {label}"
                )
            selected_lane = _require_string(
                rollout_class_entry.get("selectedLane"),
                label=f"{class_label}.selectedLane",
            )
            if selected_lane not in normalized_allowed_lanes:
                allowed = ", ".join(normalized_allowed_lanes)
                raise ValueError(
                    f"{class_label}.selectedLane must be one of [{allowed}], got {selected_lane!r}"
                )
            if selected_lane == preview_lane and not preview_enabled:
                raise ValueError(
                    f"{class_label}.selectedLane cannot be previewLane when previewEnabled is false"
                )
            rollout_class_to_lane[rollout_class] = selected_lane
        family_to_rollout_classes[family_id] = set(rollout_class_to_lane)
        if default_rollout_class not in rollout_class_to_lane:
            raise ValueError(
                f"{label}.defaultRolloutClass must also appear in {label}.rolloutClasses"
            )
        if rollout_class_to_lane[default_rollout_class] != default_lane:
            raise ValueError(
                f"{label}.defaultRolloutClass must resolve to {label}.defaultLane"
            )
    planner_metadata_contract_families = payload.get("plannerMetadataContractFamilies")
    planner_metadata_contracts = payload.get("plannerMetadataContracts")
    planner_metadata_contract_family_ids: set[str] = set()
    planner_metadata_contract_family_defaults: dict[str, dict[str, set[str] | str]] = {}
    if planner_metadata_contract_families is not None:
        if (
            not isinstance(planner_metadata_contract_families, list)
            or not planner_metadata_contract_families
        ):
            raise ValueError(
                "optimizer runtime profile rollout policy plannerMetadataContractFamilies must be a non-empty list when present"
            )
        for index, metadata_contract_family in enumerate(
            planner_metadata_contract_families
        ):
            label = f"plannerMetadataContractFamilies[{index}]"
            if not isinstance(metadata_contract_family, dict):
                raise ValueError(f"{label} must be an object")
            metadata_contract_family_id = _require_string(
                metadata_contract_family.get("metadataContractFamilyId"),
                label=f"{label}.metadataContractFamilyId",
            )
            if metadata_contract_family_id in planner_metadata_contract_family_ids:
                raise ValueError(f"{label}.metadataContractFamilyId is duplicated")
            planner_metadata_contract_family_ids.add(metadata_contract_family_id)
            default_metadata_contract_id = _require_string(
                metadata_contract_family.get("defaultMetadataContractId"),
                label=f"{label}.defaultMetadataContractId",
            )
            allowed_window_set_batch_types = metadata_contract_family.get(
                "allowedWindowSetBatchTypes"
            )
            if (
                not isinstance(allowed_window_set_batch_types, list)
                or not allowed_window_set_batch_types
            ):
                raise ValueError(
                    f"{label}.allowedWindowSetBatchTypes must be a non-empty list"
                )
            normalized_batch_types: set[str] = set()
            for batch_type_index, batch_type in enumerate(
                allowed_window_set_batch_types
            ):
                batch_type_value = _require_string(
                    batch_type,
                    label=f"{label}.allowedWindowSetBatchTypes[{batch_type_index}]",
                )
                normalized_batch_types.add(batch_type_value)
            allowed_comparison_dimensions = metadata_contract_family.get(
                "allowedComparisonDimensions"
            )
            if (
                not isinstance(allowed_comparison_dimensions, list)
                or not allowed_comparison_dimensions
            ):
                raise ValueError(
                    f"{label}.allowedComparisonDimensions must be a non-empty list"
                )
            normalized_dimensions: set[str] = set()
            for dimension_index, dimension in enumerate(
                allowed_comparison_dimensions
            ):
                dimension_value = _require_string(
                    dimension,
                    label=f"{label}.allowedComparisonDimensions[{dimension_index}]",
                )
                if dimension_value not in PLANNER_METADATA_ALLOWED_COMPARISON_DIMENSIONS:
                    allowed = ", ".join(
                        sorted(PLANNER_METADATA_ALLOWED_COMPARISON_DIMENSIONS)
                    )
                    raise ValueError(
                        f"{label}.allowedComparisonDimensions[{dimension_index}] must be one of [{allowed}], got {dimension_value!r}"
                    )
                normalized_dimensions.add(dimension_value)
            planner_metadata_contract_family_defaults[metadata_contract_family_id] = {
                "defaultMetadataContractId": default_metadata_contract_id,
                "allowedWindowSetBatchTypes": normalized_batch_types,
                "allowedComparisonDimensions": normalized_dimensions,
            }
    planner_metadata_policies = payload.get("plannerMetadataPolicies")
    planner_metadata_contract_ids: set[str] = set()
    planner_metadata_contract_defaults: dict[str, dict[str, set[str] | str]] = {}
    if planner_metadata_contracts is not None:
        if (
            not isinstance(planner_metadata_contracts, list)
            or not planner_metadata_contracts
        ):
            raise ValueError(
                "optimizer runtime profile rollout policy plannerMetadataContracts must be a non-empty list when present"
            )
        for index, metadata_contract in enumerate(planner_metadata_contracts):
            label = f"plannerMetadataContracts[{index}]"
            if not isinstance(metadata_contract, dict):
                raise ValueError(f"{label} must be an object")
            metadata_contract_id = _require_string(
                metadata_contract.get("metadataContractId"),
                label=f"{label}.metadataContractId",
            )
            if metadata_contract_id in planner_metadata_contract_ids:
                raise ValueError(f"{label}.metadataContractId is duplicated")
            planner_metadata_contract_ids.add(metadata_contract_id)
            metadata_contract_family_id = _require_string(
                metadata_contract.get("metadataContractFamilyId"),
                label=f"{label}.metadataContractFamilyId",
            )
            if metadata_contract_family_id not in planner_metadata_contract_family_ids:
                allowed = ", ".join(sorted(planner_metadata_contract_family_ids))
                raise ValueError(
                    f"{label}.metadataContractFamilyId must be one of [{allowed}], got {metadata_contract_family_id!r}"
                )
            allowed_window_set_batch_types = metadata_contract.get(
                "allowedWindowSetBatchTypes"
            )
            if (
                not isinstance(allowed_window_set_batch_types, list)
                or not allowed_window_set_batch_types
            ):
                raise ValueError(
                    f"{label}.allowedWindowSetBatchTypes must be a non-empty list"
                )
            normalized_batch_types: set[str] = set()
            for batch_type_index, batch_type in enumerate(
                allowed_window_set_batch_types
            ):
                batch_type_value = _require_string(
                    batch_type,
                    label=f"{label}.allowedWindowSetBatchTypes[{batch_type_index}]",
                )
                normalized_batch_types.add(batch_type_value)
            allowed_comparison_dimensions = metadata_contract.get(
                "allowedComparisonDimensions"
            )
            if (
                not isinstance(allowed_comparison_dimensions, list)
                or not allowed_comparison_dimensions
            ):
                raise ValueError(
                    f"{label}.allowedComparisonDimensions must be a non-empty list"
                )
            normalized_dimensions: set[str] = set()
            for dimension_index, dimension in enumerate(
                allowed_comparison_dimensions
            ):
                dimension_value = _require_string(
                    dimension,
                    label=f"{label}.allowedComparisonDimensions[{dimension_index}]",
                )
                if dimension_value not in {
                    "mode",
                    "rankingProfileId",
                    "rankingSnapshotId",
                    "evaluationWindow",
                    "weeklyDecision",
                    "challengerInputKind",
                    "historyBatchLabel",
                    "historyWindowLabel",
                    "scenarioLabel",
                }:
                    allowed = ", ".join(
                        [
                            "challengerInputKind",
                            "evaluationWindow",
                            "historyBatchLabel",
                            "historyWindowLabel",
                            "mode",
                            "rankingProfileId",
                            "rankingSnapshotId",
                            "scenarioLabel",
                            "weeklyDecision",
                        ]
                    )
                    raise ValueError(
                        f"{label}.allowedComparisonDimensions[{dimension_index}] must be one of [{allowed}], got {dimension_value!r}"
                )
                normalized_dimensions.add(dimension_value)
            family_defaults = planner_metadata_contract_family_defaults[
                metadata_contract_family_id
            ]
            family_batch_types = family_defaults["allowedWindowSetBatchTypes"]
            if not normalized_batch_types.issubset(family_batch_types):
                allowed = ", ".join(sorted(family_batch_types))
                raise ValueError(
                    f"{label}.allowedWindowSetBatchTypes must be a subset of contract family {metadata_contract_family_id!r} allowed values [{allowed}]"
                )
            family_dimensions = family_defaults["allowedComparisonDimensions"]
            if not normalized_dimensions.issubset(family_dimensions):
                allowed = ", ".join(sorted(family_dimensions))
                raise ValueError(
                    f"{label}.allowedComparisonDimensions must be a subset of contract family {metadata_contract_family_id!r} allowed values [{allowed}]"
                )
            planner_metadata_contract_defaults[metadata_contract_id] = {
                "metadataContractFamilyId": metadata_contract_family_id,
                "allowedWindowSetBatchTypes": normalized_batch_types,
                "allowedComparisonDimensions": normalized_dimensions,
            }
        for (
            metadata_contract_family_id,
            family_defaults,
        ) in planner_metadata_contract_family_defaults.items():
            default_metadata_contract_id = family_defaults["defaultMetadataContractId"]
            if default_metadata_contract_id not in planner_metadata_contract_ids:
                allowed = ", ".join(sorted(planner_metadata_contract_ids))
                raise ValueError(
                    "planner metadata contract family "
                    f"{metadata_contract_family_id!r} defaultMetadataContractId must be one of "
                    f"[{allowed}], got {default_metadata_contract_id!r}"
                )
            contract_family_id = planner_metadata_contract_defaults[
                default_metadata_contract_id
            ]["metadataContractFamilyId"]
            if contract_family_id != metadata_contract_family_id:
                raise ValueError(
                    "planner metadata contract family "
                    f"{metadata_contract_family_id!r} defaultMetadataContractId "
                    f"{default_metadata_contract_id!r} belongs to {contract_family_id!r}"
                )
    planner_metadata_policy_ids: set[str] = set()
    if planner_metadata_policies is not None:
        if not isinstance(planner_metadata_policies, list) or not planner_metadata_policies:
            raise ValueError(
                "optimizer runtime profile rollout policy plannerMetadataPolicies must be a non-empty list when present"
            )
        for index, metadata_policy in enumerate(planner_metadata_policies):
            label = f"plannerMetadataPolicies[{index}]"
            if not isinstance(metadata_policy, dict):
                raise ValueError(f"{label} must be an object")
            metadata_policy_id = _require_string(
                metadata_policy.get("metadataPolicyId"),
                label=f"{label}.metadataPolicyId",
            )
            if metadata_policy_id in planner_metadata_policy_ids:
                raise ValueError(f"{label}.metadataPolicyId is duplicated")
            planner_metadata_policy_ids.add(metadata_policy_id)
            metadata_contract_family_id = _require_string(
                metadata_policy.get("metadataContractFamilyId"),
                label=f"{label}.metadataContractFamilyId",
            )
            if metadata_contract_family_id not in planner_metadata_contract_family_ids:
                allowed = ", ".join(sorted(planner_metadata_contract_family_ids))
                raise ValueError(
                    f"{label}.metadataContractFamilyId must be one of [{allowed}], got {metadata_contract_family_id!r}"
                )
            metadata_contract_id = _require_string(
                metadata_policy.get("metadataContractId"),
                label=f"{label}.metadataContractId",
            )
            if metadata_contract_id not in planner_metadata_contract_ids:
                allowed = ", ".join(sorted(planner_metadata_contract_ids))
                raise ValueError(
                    f"{label}.metadataContractId must be one of [{allowed}], got {metadata_contract_id!r}"
                )
            contract_family_id = planner_metadata_contract_defaults[
                metadata_contract_id
            ]["metadataContractFamilyId"]
            if contract_family_id != metadata_contract_family_id:
                raise ValueError(
                    f"{label}.metadataContractId belongs to contract family {contract_family_id!r}, not {metadata_contract_family_id!r}"
                )
            _require_string(
                metadata_policy.get("defaultWindowSetBatchType"),
                label=f"{label}.defaultWindowSetBatchType",
            )
            if (
                metadata_policy["defaultWindowSetBatchType"]
                not in planner_metadata_contract_defaults[metadata_contract_id][
                    "allowedWindowSetBatchTypes"
                ]
            ):
                allowed = ", ".join(
                    sorted(
                        planner_metadata_contract_defaults[metadata_contract_id][
                            "allowedWindowSetBatchTypes"
                        ]
                    )
                )
                raise ValueError(
                    f"{label}.defaultWindowSetBatchType must be one of [{allowed}] from metadata contract {metadata_contract_id!r}"
                )
            default_dimension = _require_string(
                metadata_policy.get("defaultComparisonDimension"),
                label=f"{label}.defaultComparisonDimension",
            )
            if default_dimension not in {
                *PLANNER_METADATA_ALLOWED_COMPARISON_DIMENSIONS,
            }:
                allowed = ", ".join(
                    sorted(PLANNER_METADATA_ALLOWED_COMPARISON_DIMENSIONS)
                )
                raise ValueError(
                    f"{label}.defaultComparisonDimension must be one of [{allowed}], got {default_dimension!r}"
                )
            if (
                default_dimension
                not in planner_metadata_contract_defaults[metadata_contract_id][
                    "allowedComparisonDimensions"
                ]
            ):
                allowed = ", ".join(
                    sorted(
                        planner_metadata_contract_defaults[metadata_contract_id][
                            "allowedComparisonDimensions"
                        ]
                    )
                )
                raise ValueError(
                    f"{label}.defaultComparisonDimension must be one of [{allowed}] from metadata contract {metadata_contract_id!r}"
                )
            for priority_field_name in (
                "windowSetBatchTypePriority",
                "comparisonDimensionPriority",
            ):
                priorities = metadata_policy.get(priority_field_name)
                if not isinstance(priorities, list) or not priorities:
                    raise ValueError(
                        f"{label}.{priority_field_name} must be a non-empty list"
                    )
                for priority_index, priority in enumerate(priorities):
                    priority_label = f"{label}.{priority_field_name}[{priority_index}]"
                    priority_value = _require_string(priority, label=priority_label)
                    if priority_value not in PLANNER_METADATA_SELECTION_PRIORITIES:
                        allowed = ", ".join(
                            sorted(PLANNER_METADATA_SELECTION_PRIORITIES)
                        )
                        raise ValueError(
                            f"{priority_label} must be one of [{allowed}], got {priority_value!r}"
                        )
    eval_purpose_policies = payload.get("evalPurposePolicies")
    eval_purpose_templates = payload.get("evalPurposeTemplates")
    eval_purpose_template_families = payload.get("evalPurposeTemplateFamilies")
    purpose_template_families: dict[str, dict[str, str]] = {}
    if eval_purpose_template_families is not None:
        if (
            not isinstance(eval_purpose_template_families, list)
            or not eval_purpose_template_families
        ):
            raise ValueError(
                "optimizer runtime profile rollout policy evalPurposeTemplateFamilies must be a non-empty list when present"
            )
        seen_template_family_ids: set[str] = set()
        for index, template_family in enumerate(eval_purpose_template_families):
            label = f"evalPurposeTemplateFamilies[{index}]"
            if not isinstance(template_family, dict):
                raise ValueError(f"{label} must be an object")
            template_family_id = _require_string(
                template_family.get("templateFamilyId"),
                label=f"{label}.templateFamilyId",
            )
            if template_family_id in seen_template_family_ids:
                raise ValueError(f"{label}.templateFamilyId is duplicated")
            seen_template_family_ids.add(template_family_id)
            runtime_profile_family_id = _require_string(
                template_family.get("runtimeProfileFamilyId"),
                label=f"{label}.runtimeProfileFamilyId",
            )
            if runtime_profile_family_id not in family_to_rollout_classes:
                allowed = ", ".join(sorted(family_to_rollout_classes))
                raise ValueError(
                    f"{label}.runtimeProfileFamilyId must be one of [{allowed}], got {runtime_profile_family_id!r}"
                )
            default_rollout_class = _require_string(
                template_family.get("defaultRolloutClass"),
                label=f"{label}.defaultRolloutClass",
            )
            planner_metadata_policy_id = _require_string(
                template_family.get("plannerMetadataPolicyId"),
                label=f"{label}.plannerMetadataPolicyId",
            )
            if planner_metadata_policy_id not in planner_metadata_policy_ids:
                allowed = ", ".join(sorted(planner_metadata_policy_ids))
                raise ValueError(
                    f"{label}.plannerMetadataPolicyId must be one of [{allowed}], got {planner_metadata_policy_id!r}"
                )
            if (
                default_rollout_class
                not in family_to_rollout_classes[runtime_profile_family_id]
            ):
                allowed = ", ".join(
                    sorted(family_to_rollout_classes[runtime_profile_family_id])
                )
                raise ValueError(
                    f"{label}.defaultRolloutClass must be one of [{allowed}], got {default_rollout_class!r}"
                )
            purpose_template_families[template_family_id] = {
                "runtimeProfileFamilyId": runtime_profile_family_id,
                "defaultRolloutClass": default_rollout_class,
                "plannerMetadataPolicyId": planner_metadata_policy_id,
            }
    purpose_template_defaults: dict[str, dict[str, str]] = {}
    if eval_purpose_templates is not None:
        if not isinstance(eval_purpose_templates, list) or not eval_purpose_templates:
            raise ValueError(
                "optimizer runtime profile rollout policy evalPurposeTemplates must be a non-empty list when present"
            )
        seen_template_ids: set[str] = set()
        for index, purpose_template in enumerate(eval_purpose_templates):
            label = f"evalPurposeTemplates[{index}]"
            if not isinstance(purpose_template, dict):
                raise ValueError(f"{label} must be an object")
            template_id = _require_string(
                purpose_template.get("templateId"),
                label=f"{label}.templateId",
            )
            if template_id in seen_template_ids:
                raise ValueError(f"{label}.templateId is duplicated")
            seen_template_ids.add(template_id)
            template_family_id = _require_string(
                purpose_template.get("templateFamilyId"),
                label=f"{label}.templateFamilyId",
            )
            if template_family_id not in purpose_template_families:
                allowed = ", ".join(sorted(purpose_template_families))
                raise ValueError(
                    f"{label}.templateFamilyId must be one of [{allowed}], got {template_family_id!r}"
                )
            family_defaults = purpose_template_families[template_family_id]
            family_id = family_defaults["runtimeProfileFamilyId"]
            default_rollout_class = purpose_template.get("defaultRolloutClass")
            if default_rollout_class is None:
                default_rollout_class = family_defaults["defaultRolloutClass"]
            else:
                default_rollout_class = _require_string(
                    default_rollout_class,
                    label=f"{label}.defaultRolloutClass",
                )
                if default_rollout_class not in family_to_rollout_classes[family_id]:
                    allowed = ", ".join(sorted(family_to_rollout_classes[family_id]))
                    raise ValueError(
                        f"{label}.defaultRolloutClass must be one of [{allowed}], got {default_rollout_class!r}"
                    )
            purpose_template_defaults[template_id] = {
                "familyId": family_id,
                "defaultRolloutClass": default_rollout_class,
                "templateFamilyId": template_family_id,
            }
            default_window_set_batch_type = purpose_template.get(
                "defaultWindowSetBatchType"
            )
            if default_window_set_batch_type is not None:
                _require_string(
                    default_window_set_batch_type,
                    label=f"{label}.defaultWindowSetBatchType",
                )
            default_comparison_dimension = purpose_template.get(
                "defaultComparisonDimension"
            )
            if default_comparison_dimension is not None:
                default_dimension = _require_string(
                    default_comparison_dimension,
                    label=f"{label}.defaultComparisonDimension",
                )
                if default_dimension not in {
                    "mode",
                    "rankingProfileId",
                    "rankingSnapshotId",
                    "evaluationWindow",
                    "weeklyDecision",
                    "challengerInputKind",
                    "historyBatchLabel",
                    "historyWindowLabel",
                    "scenarioLabel",
                }:
                    allowed = ", ".join(
                        [
                            "challengerInputKind",
                            "evaluationWindow",
                            "historyBatchLabel",
                            "historyWindowLabel",
                            "mode",
                            "rankingProfileId",
                            "rankingSnapshotId",
                            "scenarioLabel",
                            "weeklyDecision",
                        ]
                    )
                    raise ValueError(
                        f"{label}.defaultComparisonDimension must be one of [{allowed}], got {default_dimension!r}"
                    )
    if eval_purpose_policies is not None:
        if not isinstance(eval_purpose_policies, list) or not eval_purpose_policies:
            raise ValueError(
                "optimizer runtime profile rollout policy evalPurposePolicies must be a non-empty list when present"
            )
        seen_purpose_policy_ids: set[str] = set()
        seen_window_set_purposes: set[str] = set()
        for index, purpose_policy in enumerate(eval_purpose_policies):
            label = f"evalPurposePolicies[{index}]"
            if not isinstance(purpose_policy, dict):
                raise ValueError(f"{label} must be an object")
            purpose_policy_id = _require_string(
                purpose_policy.get("purposePolicyId"),
                label=f"{label}.purposePolicyId",
            )
            if purpose_policy_id in seen_purpose_policy_ids:
                raise ValueError(f"{label}.purposePolicyId is duplicated")
            seen_purpose_policy_ids.add(purpose_policy_id)
            window_set_purpose = _require_string(
                purpose_policy.get("windowSetPurpose"),
                label=f"{label}.windowSetPurpose",
            )
            if window_set_purpose in seen_window_set_purposes:
                raise ValueError(f"{label}.windowSetPurpose is duplicated")
            seen_window_set_purposes.add(window_set_purpose)
            template_id = purpose_policy.get("templateId")
            if template_id is not None:
                template_value = _require_string(
                    template_id,
                    label=f"{label}.templateId",
                )
                if template_value not in purpose_template_defaults:
                    allowed = ", ".join(sorted(purpose_template_defaults))
                    raise ValueError(
                        f"{label}.templateId must be one of [{allowed}], got {template_value!r}"
                    )
            else:
                family_id = _require_string(
                    purpose_policy.get("familyId"), label=f"{label}.familyId"
                )
                if family_id not in family_to_rollout_classes:
                    allowed = ", ".join(sorted(family_to_rollout_classes))
                    raise ValueError(
                        f"{label}.familyId must be one of [{allowed}], got {family_id!r}"
                    )
                default_rollout_class = _require_string(
                    purpose_policy.get("defaultRolloutClass"),
                    label=f"{label}.defaultRolloutClass",
                )
                if default_rollout_class not in family_to_rollout_classes[family_id]:
                    allowed = ", ".join(sorted(family_to_rollout_classes[family_id]))
                    raise ValueError(
                        f"{label}.defaultRolloutClass must be one of [{allowed}], got {default_rollout_class!r}"
                    )
                default_window_set_batch_type = purpose_policy.get(
                    "defaultWindowSetBatchType"
                )
                if default_window_set_batch_type is not None:
                    _require_string(
                        default_window_set_batch_type,
                        label=f"{label}.defaultWindowSetBatchType",
                    )
                default_comparison_dimension = purpose_policy.get(
                    "defaultComparisonDimension"
                )
                if default_comparison_dimension is not None:
                    default_dimension = _require_string(
                        default_comparison_dimension,
                        label=f"{label}.defaultComparisonDimension",
                    )
                    if default_dimension not in {
                        "mode",
                        "rankingProfileId",
                        "rankingSnapshotId",
                        "evaluationWindow",
                        "weeklyDecision",
                        "challengerInputKind",
                        "historyBatchLabel",
                        "historyWindowLabel",
                        "scenarioLabel",
                    }:
                        allowed = ", ".join(
                            [
                                "challengerInputKind",
                                "evaluationWindow",
                                "historyBatchLabel",
                                "historyWindowLabel",
                                "mode",
                                "rankingProfileId",
                                "rankingSnapshotId",
                                "scenarioLabel",
                                "weeklyDecision",
                            ]
                        )
                        raise ValueError(
                            f"{label}.defaultComparisonDimension must be one of [{allowed}], got {default_dimension!r}"
                        )
    rollout_class_rules = payload.get("rolloutClassRules")
    if rollout_class_rules is None:
        return
    if not isinstance(rollout_class_rules, list) or not rollout_class_rules:
        raise ValueError(
            "optimizer runtime profile rollout policy rolloutClassRules must be a non-empty list when present"
        )
    known_rollout_classes = {
        rollout_class_entry["rolloutClass"]
        for family_policy in family_policies
        for rollout_class_entry in family_policy.get("rolloutClasses", [])
        if isinstance(rollout_class_entry, dict)
        and isinstance(rollout_class_entry.get("rolloutClass"), str)
    }
    seen_rule_ids: set[str] = set()
    for index, rollout_rule in enumerate(rollout_class_rules):
        label = f"rolloutClassRules[{index}]"
        if not isinstance(rollout_rule, dict):
            raise ValueError(f"{label} must be an object")
        rule_id = _require_string(rollout_rule.get("ruleId"), label=f"{label}.ruleId")
        if rule_id in seen_rule_ids:
            raise ValueError(f"{label}.ruleId is duplicated")
        seen_rule_ids.add(rule_id)
        rollout_class = _require_string(
            rollout_rule.get("rolloutClass"), label=f"{label}.rolloutClass"
        )
        if rollout_class not in known_rollout_classes:
            allowed = ", ".join(sorted(known_rollout_classes))
            raise ValueError(
                f"{label}.rolloutClass must be one of [{allowed}], got {rollout_class!r}"
            )
        selectors = 0
        for key in (
            "batchWindowLabelPrefix",
            "scenarioLabelPrefix",
            "windowSetPurpose",
            "windowSetBatchType",
            "comparisonDimension",
            "historyWindowLabelPrefix",
            "mode",
        ):
            value = rollout_rule.get(key)
            if value is None:
                continue
            _require_string(value, label=f"{label}.{key}")
            selectors += 1
        if selectors == 0:
            raise ValueError(
                f"{label} must declare at least one selector such as batchWindowLabelPrefix, scenarioLabelPrefix, historyWindowLabelPrefix, mode, windowSetPurpose, windowSetBatchType, or comparisonDimension"
            )


def validate_optimizer_runtime_profile_rollout_policy_reference(
    reference: dict[str, Any],
    *,
    label: str,
) -> None:
    if not isinstance(reference, dict):
        raise ValueError(f"{label} must be an object")
    _require_string(reference.get("policyId"), label=f"{label}.policyId")
    _require_string(reference.get("policyFamily"), label=f"{label}.policyFamily")
    _require_string(reference.get("policyVersion"), label=f"{label}.policyVersion")
    _require_string(reference.get("familyId"), label=f"{label}.familyId")
    schema_version = _require_string(
        reference.get("schemaVersion"), label=f"{label}.schemaVersion"
    )
    if schema_version not in OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSIONS:
        allowed = ", ".join(
            sorted(OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSIONS)
        )
        raise ValueError(
            f"{label}.schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
