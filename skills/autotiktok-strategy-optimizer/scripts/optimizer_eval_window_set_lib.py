#!/usr/bin/env python3
"""
Helpers for scheduler-facing optimizer eval window-set artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from optimizer_eval_batch_lib import (
    COMPARISON_DIMENSIONS,
    ENTRY_SUMMARY_OVERRIDE_KEYS,
    build_optimizer_eval_batch_manifest_entry,
    classify_runtime_source_kind,
)
from optimizer_runtime_profile_lib import (
    DEFAULT_RUNTIME_PROFILE_BINDINGS,
    resolve_runtime_profile_entry,
    validate_optimizer_runtime_profile_family_registry_reference,
    validate_optimizer_runtime_profile_catalog_reference,
    validate_optimizer_runtime_profile_catalog_payload,
)
from optimizer_runtime_profile_rollout_lib import (
    OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SELECTION_SOURCES,
    validate_optimizer_runtime_profile_rollout_policy_reference,
)
from optimizer_runtime_plan_lib import (
    validate_optimizer_runtime_materialization_plan_payload,
)
from reward_lib import load_json


OPTIMIZER_EVAL_WINDOW_SET_SAMPLE_SCHEMA_VERSION = "optimizer-eval-window-set.sample.v1"
OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSION = "optimizer-eval-window-set.v1"
OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSIONS = {
    OPTIMIZER_EVAL_WINDOW_SET_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSION,
}
WINDOW_SET_METADATA_SELECTION_SOURCES = {
    "explicit",
    "purpose_policy",
    "purpose_template",
    "purpose_template_family",
    "metadata_policy_default",
    "fallback_default",
}

OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-runtime-artifact-registry.sample.v1"
)
OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSION = (
    "optimizer-runtime-artifact-registry.v1"
)
OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSIONS = {
    OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSION,
}
OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION = (
    "optimizer-runtime-profile-catalog.sample.v1"
)
OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSION = (
    "optimizer-runtime-profile-catalog.v1"
)
OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSIONS = {
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSION,
}

EVAL_WINDOW_SET_MODES = (
    "daily_review_only",
    "daily_with_weekly_promotion",
)

SAMPLE_ARTIFACT_DESCRIPTOR_KIND = "sample_artifact_binding"
PLANNER_RUNTIME_DESCRIPTOR_KIND = "planner_runtime_binding"
RUNTIME_SOURCE_DESCRIPTOR_BINDINGS: dict[str, dict[str, Any]] = {
    "optimizer_input_manifest_sample": {
        "bindingId": "optimizer_input_manifest",
        "payload": {
            "inputManifestPath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json"
        },
    },
    "optimizer_input_bundle_sample": {
        "bindingId": "optimizer_input_bundle",
        "payload": {
            "inputBundlePath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json"
        },
    },
    "optimizer_offline_cycle_daily_sample": {
        "bindingId": "optimizer_offline_cycle_daily",
        "payload": {
            "inputOfflineCyclePath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle-daily.sample.json"
        },
    },
    "optimizer_offline_cycle_weekly_sample": {
        "bindingId": "optimizer_offline_cycle_weekly",
        "payload": {
            "inputOfflineCyclePath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle.sample.json"
        },
    },
}
PLANNER_RUNTIME_DESCRIPTOR_BINDINGS: dict[tuple[str, str], dict[str, Any]] = {
    (
        profile["jobFamilyGroup"],
        profile["materializationProfile"],
    ): {
        "bindingId": profile["bindingId"],
        "sourceClass": profile["sourceClass"],
        "sourceVariant": profile["sourceVariant"],
        "runtimeSourceKind": profile["runtimeSourceKind"],
        "includeWeeklyPromotion": profile["includeWeeklyPromotion"],
        "payload": dict(profile["payload"]),
        "profileId": profile_id,
    }
    for profile_id, profile in DEFAULT_RUNTIME_PROFILE_BINDINGS.items()
}
PLANNER_RUNTIME_LEGACY_BINDINGS: dict[tuple[str, str], dict[str, str]] = {
    ("optimizer_input", "manifest"): {
        "jobFamilyGroup": "optimizer_input_jobs",
        "materializationProfile": "manifest_from_job_runs",
    },
    ("optimizer_input", "bundle"): {
        "jobFamilyGroup": "optimizer_input_jobs",
        "materializationProfile": "bundle_from_manifest",
    },
    ("optimizer_offline_cycle", "daily"): {
        "jobFamilyGroup": "optimizer_offline_cycle_jobs",
        "materializationProfile": "daily_cycle_from_manifest",
    },
    ("optimizer_offline_cycle", "weekly"): {
        "jobFamilyGroup": "optimizer_offline_cycle_jobs",
        "materializationProfile": "weekly_cycle_from_bundle",
    },
}

RUNTIME_ARTIFACT_FIELDS = (
    "inputManifestPath",
    "inputBundlePath",
    "inputOfflineCyclePath",
)


def build_runtime_source_descriptor(*, artifact_binding: str) -> dict[str, str]:
    if artifact_binding not in RUNTIME_SOURCE_DESCRIPTOR_BINDINGS:
        allowed = ", ".join(sorted(RUNTIME_SOURCE_DESCRIPTOR_BINDINGS))
        raise ValueError(
            f"runtime source descriptor artifactBinding must be one of [{allowed}], got {artifact_binding!r}"
        )
    return {
        "descriptorKind": SAMPLE_ARTIFACT_DESCRIPTOR_KIND,
        "artifactBinding": artifact_binding,
    }


def build_planner_runtime_source_descriptor(
    *,
    profile_id: str | None = None,
    job_family_group: str | None = None,
    materialization_profile: str | None = None,
    source_class: str | None = None,
    source_variant: str | None = None,
) -> dict[str, str]:
    if profile_id is not None:
        if not isinstance(profile_id, str) or not profile_id:
            raise ValueError(
                "planner runtime source descriptor profileId must be a non-empty string"
            )
        return {
            "descriptorKind": PLANNER_RUNTIME_DESCRIPTOR_KIND,
            "profileId": profile_id,
        }
    if job_family_group is None and materialization_profile is None:
        binding_key = (source_class, source_variant)
        if binding_key not in PLANNER_RUNTIME_LEGACY_BINDINGS:
            allowed = ", ".join(
                f"{current_class}:{current_variant}"
                for current_class, current_variant in sorted(
                    PLANNER_RUNTIME_LEGACY_BINDINGS
                )
            )
            raise ValueError(
                "planner runtime source descriptor sourceClass/sourceVariant must be one of "
                f"[{allowed}], got {source_class!r}:{source_variant!r}"
            )
        legacy_binding = PLANNER_RUNTIME_LEGACY_BINDINGS[binding_key]
        job_family_group = legacy_binding["jobFamilyGroup"]
        materialization_profile = legacy_binding["materializationProfile"]
    binding_key = (job_family_group, materialization_profile)
    if binding_key not in PLANNER_RUNTIME_DESCRIPTOR_BINDINGS:
        allowed = ", ".join(
            f"{current_group}:{current_profile}"
            for current_group, current_profile in sorted(
                PLANNER_RUNTIME_DESCRIPTOR_BINDINGS
            )
        )
        raise ValueError(
            "planner runtime source descriptor jobFamilyGroup/materializationProfile must be one of "
            f"[{allowed}], got {job_family_group!r}:{materialization_profile!r}"
        )
    return {
        "descriptorKind": PLANNER_RUNTIME_DESCRIPTOR_KIND,
        "jobFamilyGroup": str(job_family_group),
        "materializationProfile": str(materialization_profile),
    }


def build_optimizer_runtime_artifact_registry_binding(
    *,
    binding_id: str,
    artifact_field: str,
    artifact_path: str,
    runtime_source_kind: str,
    job_family_group: str,
    materialization_profile: str,
    source_class: str,
    source_variant: str,
    materialization_plan_id: str,
) -> dict[str, str]:
    if artifact_field not in RUNTIME_ARTIFACT_FIELDS:
        allowed = ", ".join(RUNTIME_ARTIFACT_FIELDS)
        raise ValueError(
            f"optimizer runtime artifact registry artifactField must be one of [{allowed}], got {artifact_field!r}"
        )
    return {
        "bindingId": binding_id,
        "artifactField": artifact_field,
        "artifactPath": artifact_path,
        "runtimeSourceKind": runtime_source_kind,
        "jobFamilyGroup": job_family_group,
        "materializationProfile": materialization_profile,
        "sourceClass": source_class,
        "sourceVariant": source_variant,
        "materializationPlanId": materialization_plan_id,
    }


def build_optimizer_runtime_artifact_registry_payload(
    *,
    bindings: list[dict[str, Any]],
    schema_version: str,
    registry_id: str,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "registryId": registry_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "bindingCount": len(bindings),
        },
        "bindings": bindings,
    }


def build_default_optimizer_runtime_artifact_registry_bindings(
    *,
    input_manifest_path: str,
    input_bundle_path: str,
    input_offline_cycle_daily_path: str,
    input_offline_cycle_weekly_path: str,
) -> list[dict[str, str]]:
    return [
        build_optimizer_runtime_artifact_registry_binding(
            binding_id="optimizer_input_manifest",
            artifact_field="inputManifestPath",
            artifact_path=input_manifest_path,
            runtime_source_kind="input_manifest",
            job_family_group="optimizer_input_jobs",
            materialization_profile="manifest_from_job_runs",
            source_class="optimizer_input",
            source_variant="manifest",
            materialization_plan_id="optimizer_input_manifest_plan",
        ),
        build_optimizer_runtime_artifact_registry_binding(
            binding_id="optimizer_input_bundle",
            artifact_field="inputBundlePath",
            artifact_path=input_bundle_path,
            runtime_source_kind="input_bundle",
            job_family_group="optimizer_input_jobs",
            materialization_profile="bundle_from_manifest",
            source_class="optimizer_input",
            source_variant="bundle",
            materialization_plan_id="optimizer_input_bundle_plan",
        ),
        build_optimizer_runtime_artifact_registry_binding(
            binding_id="optimizer_offline_cycle_daily",
            artifact_field="inputOfflineCyclePath",
            artifact_path=input_offline_cycle_daily_path,
            runtime_source_kind="offline_cycle",
            job_family_group="optimizer_offline_cycle_jobs",
            materialization_profile="daily_cycle_from_manifest",
            source_class="optimizer_offline_cycle",
            source_variant="daily",
            materialization_plan_id="optimizer_offline_cycle_daily_plan",
        ),
        build_optimizer_runtime_artifact_registry_binding(
            binding_id="optimizer_offline_cycle_weekly",
            artifact_field="inputOfflineCyclePath",
            artifact_path=input_offline_cycle_weekly_path,
            runtime_source_kind="offline_cycle",
            job_family_group="optimizer_offline_cycle_jobs",
            materialization_profile="weekly_cycle_from_bundle",
            source_class="optimizer_offline_cycle",
            source_variant="weekly",
            materialization_plan_id="optimizer_offline_cycle_weekly_plan",
        ),
    ]


def _resolve_runtime_source_descriptor_binding(
    descriptor: dict[str, Any],
    *,
    runtime_profile_catalog: dict[str, Any] | None = None,
) -> tuple[str, dict[str, str]] | None:
    descriptor_kind = descriptor.get("descriptorKind")
    if descriptor_kind == SAMPLE_ARTIFACT_DESCRIPTOR_KIND:
        artifact_binding = descriptor.get("artifactBinding")
        if not isinstance(artifact_binding, str):
            return None
        binding = RUNTIME_SOURCE_DESCRIPTOR_BINDINGS.get(artifact_binding)
        if binding is None:
            return None
        return binding["bindingId"], dict(binding["payload"])
    if descriptor_kind == PLANNER_RUNTIME_DESCRIPTOR_KIND:
        profile_id = descriptor.get("profileId")
        if isinstance(profile_id, str) and profile_id:
            profile_lookup = resolve_runtime_profile_entry(
                profile_id,
                runtime_profile_catalog=runtime_profile_catalog,
            )
            if profile_lookup is None:
                return None
            binding_id = profile_lookup.get("bindingId")
            if not isinstance(binding_id, str) or not binding_id:
                return None
            payload = {}
            default_profile = DEFAULT_RUNTIME_PROFILE_BINDINGS.get(
                profile_lookup.get("profileId")
            )
            if default_profile is not None:
                payload = dict(default_profile["payload"])
            if not payload:
                default_profile = DEFAULT_RUNTIME_PROFILE_BINDINGS.get(profile_id)
                if default_profile is not None:
                    payload = dict(default_profile["payload"])
            if not payload:
                runtime_source_kind = profile_lookup.get("runtimeSourceKind")
                if runtime_source_kind == "input_manifest":
                    payload = {"inputManifestPath": ""}
                elif runtime_source_kind == "input_bundle":
                    payload = {"inputBundlePath": ""}
                elif runtime_source_kind == "offline_cycle":
                    payload = {"inputOfflineCyclePath": ""}
            return binding_id, payload
        job_family_group = descriptor.get("jobFamilyGroup")
        materialization_profile = descriptor.get("materializationProfile")
        if isinstance(job_family_group, str) and isinstance(
            materialization_profile, str
        ):
            binding = PLANNER_RUNTIME_DESCRIPTOR_BINDINGS.get(
                (job_family_group, materialization_profile)
            )
            if binding is None:
                return None
            return binding["bindingId"], dict(binding["payload"])
        source_class = descriptor.get("sourceClass")
        source_variant = descriptor.get("sourceVariant")
        if not isinstance(source_class, str) or not isinstance(source_variant, str):
            return None
        legacy_binding = PLANNER_RUNTIME_LEGACY_BINDINGS.get(
            (source_class, source_variant)
        )
        if legacy_binding is None:
            return None
        binding = PLANNER_RUNTIME_DESCRIPTOR_BINDINGS.get(
            (
                legacy_binding["jobFamilyGroup"],
                legacy_binding["materializationProfile"],
            )
        )
        if binding is None:
            return None
        return binding["bindingId"], dict(binding["payload"])
    return None


def _classify_runtime_source_kind_from_descriptor(
    descriptor: dict[str, Any],
    *,
    runtime_profile_catalog: dict[str, Any] | None = None,
) -> str:
    resolved_binding = _resolve_runtime_source_descriptor_binding(
        descriptor, runtime_profile_catalog=runtime_profile_catalog
    )
    if resolved_binding is None:
        return "unknown"
    _, binding_payload = resolved_binding
    return classify_runtime_source_kind(binding_payload)


def build_optimizer_eval_runtime_source(
    *,
    runtime_source_id: str,
    source_descriptor: dict[str, Any] | None = None,
    input_manifest_path: str | None = None,
    input_bundle_path: str | None = None,
    input_offline_cycle_path: str | None = None,
    include_weekly_promotion: bool,
    ranking_contract_version: str | None = None,
    ranking_contract_validation_mode: str | None = None,
    runtime_profile_catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "runtimeSourceId": runtime_source_id,
        "includeWeeklyPromotion": include_weekly_promotion,
    }
    if source_descriptor is not None:
        payload["sourceDescriptor"] = source_descriptor
    if input_manifest_path is not None:
        payload["inputManifestPath"] = input_manifest_path
    if input_bundle_path is not None:
        payload["inputBundlePath"] = input_bundle_path
    if input_offline_cycle_path is not None:
        payload["inputOfflineCyclePath"] = input_offline_cycle_path
    if ranking_contract_version is not None:
        payload["rankingContractVersion"] = ranking_contract_version
    if ranking_contract_validation_mode is not None:
        payload["rankingContractValidationMode"] = ranking_contract_validation_mode
    if source_descriptor is not None:
        payload["runtimeSourceKind"] = _classify_runtime_source_kind_from_descriptor(
            source_descriptor,
            runtime_profile_catalog=runtime_profile_catalog,
        )
    else:
        payload["runtimeSourceKind"] = classify_runtime_source_kind(payload)
    return payload


def build_optimizer_eval_window_set_entry(
    *,
    window_id: str,
    history_batch_label: str,
    history_window_label: str,
    scenario_label: str,
    mode: str,
    generated_at: str,
    cycle_id: str,
    eval_run_id: str,
    report_id: str,
    runtime_source_id: str | None = None,
    input_manifest_path: str | None = None,
    input_bundle_path: str | None = None,
    input_offline_cycle_path: str | None = None,
    include_weekly_promotion: bool,
    ranking_contract_version: str | None = None,
    ranking_contract_validation_mode: str | None = None,
    summary_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "windowId": window_id,
        "historyBatchLabel": history_batch_label,
        "historyWindowLabel": history_window_label,
        "scenarioLabel": scenario_label,
        "mode": mode,
        "generatedAt": generated_at,
        "cycleId": cycle_id,
        "evalRunId": eval_run_id,
        "reportId": report_id,
        "includeWeeklyPromotion": include_weekly_promotion,
    }
    if runtime_source_id is not None:
        payload["runtimeSourceId"] = runtime_source_id
    if input_manifest_path is not None:
        payload["inputManifestPath"] = input_manifest_path
    if input_bundle_path is not None:
        payload["inputBundlePath"] = input_bundle_path
    if input_offline_cycle_path is not None:
        payload["inputOfflineCyclePath"] = input_offline_cycle_path
    if ranking_contract_version is not None:
        payload["rankingContractVersion"] = ranking_contract_version
    if ranking_contract_validation_mode is not None:
        payload["rankingContractValidationMode"] = ranking_contract_validation_mode
    if summary_overrides:
        payload["summaryOverrides"] = summary_overrides
    return payload


def build_optimizer_eval_window_set_payload(
    *,
    windows: list[dict[str, Any]],
    runtime_sources: list[dict[str, Any]] | None,
    runtime_profile_rollout_policy_reference: dict[str, Any] | None,
    runtime_profile_family_registry_reference: dict[str, Any] | None,
    runtime_profile_catalog_reference: dict[str, Any] | None,
    runtime_profile_rollout_class: str | None,
    runtime_profile_lane_selection_source: str,
    runtime_profile_active_lane: str | None,
    runtime_profile_default_lane: str | None,
    runtime_profile_rollout_strategy: str | None,
    runtime_profile_matched_rollout_rule_id: str | None,
    schema_version: str,
    window_set_id: str,
    generated_at: str,
    comparison_dimension: str,
    comparison_dimension_selection_source: str,
    batch_window_label: str,
    window_set_purpose: str,
    window_set_batch_type: str,
    window_set_batch_type_selection_source: str,
) -> dict[str, Any]:
    mode_counts: dict[str, int] = {}
    for window in windows:
        mode = window["mode"]
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
    payload = {
        "schemaVersion": schema_version,
        "windowSetId": window_set_id,
        "generatedAt": generated_at,
        "comparisonDimension": comparison_dimension,
        "batchWindowLabel": batch_window_label,
        "windowSetPurpose": window_set_purpose,
        "windowSetBatchType": window_set_batch_type,
        "generatedFrom": {
            "windowCount": len(windows),
            "modeCounts": mode_counts,
            "windowSetPurpose": window_set_purpose,
            "windowSetBatchType": window_set_batch_type,
            "windowSetBatchTypeSelectionSource": window_set_batch_type_selection_source,
            "comparisonDimensionSelectionSource": comparison_dimension_selection_source,
        },
        "windows": windows,
    }
    if runtime_sources:
        payload["runtimeSources"] = runtime_sources
        payload["generatedFrom"]["runtimeSourceCount"] = len(runtime_sources)
    if runtime_profile_rollout_policy_reference is not None:
        payload["runtimeProfileRolloutPolicyReference"] = (
            runtime_profile_rollout_policy_reference
        )
        payload["generatedFrom"]["runtimeProfileRolloutPolicyId"] = (
            runtime_profile_rollout_policy_reference["policyId"]
        )
        payload["generatedFrom"]["runtimeProfileRolloutPolicyFamily"] = (
            runtime_profile_rollout_policy_reference["policyFamily"]
        )
        payload["generatedFrom"]["runtimeProfileRolloutPolicyVersion"] = (
            runtime_profile_rollout_policy_reference["policyVersion"]
        )
    if runtime_profile_family_registry_reference is not None:
        payload["runtimeProfileFamilyRegistryReference"] = (
            runtime_profile_family_registry_reference
        )
        payload["generatedFrom"]["runtimeProfileFamilyRegistryId"] = (
            runtime_profile_family_registry_reference["registryId"]
        )
        payload["generatedFrom"]["runtimeProfileFamilyId"] = (
            runtime_profile_family_registry_reference["familyId"]
        )
        payload["generatedFrom"]["runtimeProfileCatalogLane"] = (
            runtime_profile_family_registry_reference["lane"]
        )
    if runtime_profile_catalog_reference is not None:
        payload["runtimeProfileCatalogReference"] = runtime_profile_catalog_reference
        payload["generatedFrom"]["runtimeProfileCatalogId"] = (
            runtime_profile_catalog_reference["catalogId"]
        )
        payload["generatedFrom"]["runtimeProfileCatalogFamily"] = (
            runtime_profile_catalog_reference["catalogFamily"]
        )
        payload["generatedFrom"]["runtimeProfileCatalogVersion"] = (
            runtime_profile_catalog_reference["catalogVersion"]
        )
        payload["generatedFrom"]["runtimeProfileCatalogSchemaVersion"] = (
            runtime_profile_catalog_reference["schemaVersion"]
        )
    payload["generatedFrom"]["runtimeProfileLaneSelectionSource"] = (
        runtime_profile_lane_selection_source
    )
    if runtime_profile_rollout_class is not None:
        payload["generatedFrom"]["runtimeProfileRolloutClass"] = (
            runtime_profile_rollout_class
        )
    if runtime_profile_active_lane is not None:
        payload["generatedFrom"]["runtimeProfileActiveLane"] = (
            runtime_profile_active_lane
        )
    if runtime_profile_default_lane is not None:
        payload["generatedFrom"]["runtimeProfileDefaultLane"] = (
            runtime_profile_default_lane
        )
    if runtime_profile_rollout_strategy is not None:
        payload["generatedFrom"]["runtimeProfileRolloutStrategy"] = (
            runtime_profile_rollout_strategy
        )
    if runtime_profile_matched_rollout_rule_id is not None:
        payload["generatedFrom"]["runtimeProfileMatchedRolloutRuleId"] = (
            runtime_profile_matched_rollout_rule_id
        )
    return payload


def _validate_string(value: Any, *, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")


def _validate_runtime_source_descriptor(
    descriptor: dict[str, Any], *, label: str
) -> None:
    descriptor_kind = descriptor.get("descriptorKind")
    if descriptor_kind == SAMPLE_ARTIFACT_DESCRIPTOR_KIND:
        artifact_binding = descriptor.get("artifactBinding")
        if artifact_binding not in RUNTIME_SOURCE_DESCRIPTOR_BINDINGS:
            allowed = ", ".join(sorted(RUNTIME_SOURCE_DESCRIPTOR_BINDINGS))
            raise ValueError(
                f"{label}.artifactBinding must be one of [{allowed}], got {artifact_binding!r}"
            )
        return
    if descriptor_kind == PLANNER_RUNTIME_DESCRIPTOR_KIND:
        profile_id = descriptor.get("profileId")
        if isinstance(profile_id, str) and profile_id:
            return
        job_family_group = descriptor.get("jobFamilyGroup")
        materialization_profile = descriptor.get("materializationProfile")
        has_new_pair = isinstance(job_family_group, str) and isinstance(
            materialization_profile, str
        )
        source_class = descriptor.get("sourceClass")
        source_variant = descriptor.get("sourceVariant")
        has_legacy_pair = isinstance(source_class, str) and isinstance(
            source_variant, str
        )
        if has_new_pair:
            binding_key = (job_family_group, materialization_profile)
            if binding_key not in PLANNER_RUNTIME_DESCRIPTOR_BINDINGS:
                allowed = ", ".join(
                    f"{current_group}:{current_profile}"
                    for current_group, current_profile in sorted(
                        PLANNER_RUNTIME_DESCRIPTOR_BINDINGS
                    )
                )
                raise ValueError(
                    f"{label}.jobFamilyGroup/materializationProfile must be one of [{allowed}], got {job_family_group!r}:{materialization_profile!r}"
                )
            return
        if has_legacy_pair:
            binding_key = (source_class, source_variant)
            if binding_key not in PLANNER_RUNTIME_LEGACY_BINDINGS:
                allowed = ", ".join(
                    f"{current_class}:{current_variant}"
                    for current_class, current_variant in sorted(
                        PLANNER_RUNTIME_LEGACY_BINDINGS
                    )
                )
                raise ValueError(
                    f"{label}.sourceClass/sourceVariant must be one of [{allowed}], got {source_class!r}:{source_variant!r}"
                )
            return
        raise ValueError(
            f"{label} must include planner descriptor fields `jobFamilyGroup`/`materializationProfile` or compatibility fields `sourceClass`/`sourceVariant`"
        )
    allowed_kinds = ", ".join(
        sorted((SAMPLE_ARTIFACT_DESCRIPTOR_KIND, PLANNER_RUNTIME_DESCRIPTOR_KIND))
    )
    raise ValueError(f"{label}.descriptorKind must be one of [{allowed_kinds}]")


def validate_optimizer_runtime_artifact_registry_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSIONS:
        allowed = ", ".join(
            sorted(OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSIONS)
        )
        raise ValueError(
            "optimizer runtime artifact registry schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    _validate_string(payload.get("registryId"), label="registryId")
    _validate_string(payload.get("generatedAt"), label="generatedAt")
    bindings = payload.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        raise ValueError(
            "optimizer runtime artifact registry must include a non-empty `bindings` list"
        )
    seen_binding_ids: set[str] = set()
    seen_source_pairs: set[tuple[str, str]] = set()
    seen_planner_pairs: set[tuple[str, str]] = set()
    for index, binding in enumerate(bindings):
        label = f"optimizer runtime artifact registry bindings[{index}]"
        if not isinstance(binding, dict):
            raise ValueError(f"{label} must be an object")
        for key in (
            "bindingId",
            "artifactField",
            "artifactPath",
            "runtimeSourceKind",
            "jobFamilyGroup",
            "materializationProfile",
            "sourceClass",
            "sourceVariant",
            "materializationPlanId",
        ):
            _validate_string(binding.get(key), label=f"{label}.{key}")
        binding_id = binding["bindingId"]
        if binding_id in seen_binding_ids:
            raise ValueError(
                f"optimizer runtime artifact registry contains duplicate bindingId {binding_id!r}"
            )
        seen_binding_ids.add(binding_id)
        artifact_field = binding["artifactField"]
        if artifact_field not in RUNTIME_ARTIFACT_FIELDS:
            allowed = ", ".join(RUNTIME_ARTIFACT_FIELDS)
            raise ValueError(
                f"{label}.artifactField must be one of [{allowed}], got {artifact_field!r}"
            )
        runtime_source_kind = binding["runtimeSourceKind"]
        expected_runtime_source_kind = classify_runtime_source_kind(
            {artifact_field: binding["artifactPath"]}
        )
        if runtime_source_kind != expected_runtime_source_kind:
            raise ValueError(
                f"{label}.runtimeSourceKind must be {expected_runtime_source_kind!r}"
            )
        source_pair = (binding["sourceClass"], binding["sourceVariant"])
        if source_pair in seen_source_pairs:
            raise ValueError(
                "optimizer runtime artifact registry contains duplicate "
                f"sourceClass/sourceVariant pair {source_pair!r}"
            )
        seen_source_pairs.add(source_pair)
        planner_pair = (
            binding["jobFamilyGroup"],
            binding["materializationProfile"],
        )
        if planner_pair in seen_planner_pairs:
            raise ValueError(
                "optimizer runtime artifact registry contains duplicate "
                f"jobFamilyGroup/materializationProfile pair {planner_pair!r}"
            )
        seen_planner_pairs.add(planner_pair)


def _validate_runtime_source_payload(source: dict[str, Any], *, label: str) -> None:
    _validate_string(source.get("runtimeSourceId"), label=f"{label}.runtimeSourceId")
    primary_input_keys = (
        "inputManifestPath",
        "inputBundlePath",
        "inputOfflineCyclePath",
    )
    present_inputs = [
        key
        for key in primary_input_keys
        if isinstance(source.get(key), str) and source.get(key)
    ]
    source_descriptor = source.get("sourceDescriptor")
    has_source_descriptor = isinstance(source_descriptor, dict) and bool(source_descriptor)
    if has_source_descriptor == bool(present_inputs):
        allowed = ", ".join(primary_input_keys)
        raise ValueError(
            f"{label} must include exactly one source specification: `sourceDescriptor` or one primary input path from [{allowed}]"
        )
    if has_source_descriptor:
        _validate_runtime_source_descriptor(source_descriptor, label=f"{label}.sourceDescriptor")
    elif len(present_inputs) != 1:
        allowed = ", ".join(primary_input_keys)
        raise ValueError(
            f"{label} must include exactly one primary input path from [{allowed}]"
        )
    include_weekly_promotion = source.get("includeWeeklyPromotion")
    if not isinstance(include_weekly_promotion, bool):
        raise ValueError(f"{label}.includeWeeklyPromotion must be a boolean")
    expected_runtime_source_kind = classify_runtime_source_kind(source)
    if has_source_descriptor:
        expected_runtime_source_kind = _classify_runtime_source_kind_from_descriptor(
            source_descriptor
        )
    runtime_source_kind = source.get("runtimeSourceKind")
    if runtime_source_kind is not None and runtime_source_kind != expected_runtime_source_kind:
        raise ValueError(
            f"{label}.runtimeSourceKind must be {expected_runtime_source_kind!r} when present"
        )
    for key in ("rankingContractVersion", "rankingContractValidationMode"):
        value = source.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label}.{key} must be a non-empty string when present")


def validate_optimizer_eval_window_set_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_EVAL_WINDOW_SET_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer eval window set schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    comparison_dimension = payload.get("comparisonDimension")
    if comparison_dimension not in COMPARISON_DIMENSIONS:
        allowed = ", ".join(COMPARISON_DIMENSIONS)
        raise ValueError(
            "optimizer eval window set comparisonDimension must be one of "
            f"[{allowed}], got {comparison_dimension!r}"
        )
    _validate_string(payload.get("batchWindowLabel"), label="batchWindowLabel")
    _validate_string(payload.get("windowSetPurpose"), label="windowSetPurpose")
    _validate_string(payload.get("windowSetBatchType"), label="windowSetBatchType")
    runtime_profile_catalog_reference = payload.get("runtimeProfileCatalogReference")
    runtime_profile_rollout_policy_reference = payload.get(
        "runtimeProfileRolloutPolicyReference"
    )
    runtime_profile_family_registry_reference = payload.get(
        "runtimeProfileFamilyRegistryReference"
    )
    if runtime_profile_rollout_policy_reference is not None:
        validate_optimizer_runtime_profile_rollout_policy_reference(
            runtime_profile_rollout_policy_reference,
            label="runtimeProfileRolloutPolicyReference",
        )
    if runtime_profile_family_registry_reference is not None:
        validate_optimizer_runtime_profile_family_registry_reference(
            runtime_profile_family_registry_reference,
            label="runtimeProfileFamilyRegistryReference",
        )
    if runtime_profile_catalog_reference is not None:
        validate_optimizer_runtime_profile_catalog_reference(
            runtime_profile_catalog_reference,
            label="runtimeProfileCatalogReference",
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError("optimizer eval window set generatedFrom must be an object")
    lane_selection_source = generated_from.get("runtimeProfileLaneSelectionSource")
    if lane_selection_source is not None:
        if lane_selection_source not in OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SELECTION_SOURCES:
            allowed = ", ".join(
                sorted(OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SELECTION_SOURCES)
            )
            raise ValueError(
                "generatedFrom.runtimeProfileLaneSelectionSource must be one of "
                f"[{allowed}], got {lane_selection_source!r}"
            )
    rollout_class = generated_from.get("runtimeProfileRolloutClass")
    if rollout_class is not None and (
        not isinstance(rollout_class, str) or not rollout_class
    ):
        raise ValueError(
            "generatedFrom.runtimeProfileRolloutClass must be a non-empty string when present"
        )
    rollout_strategy = generated_from.get("runtimeProfileRolloutStrategy")
    if rollout_strategy is not None and (
        not isinstance(rollout_strategy, str) or not rollout_strategy
    ):
        raise ValueError(
            "generatedFrom.runtimeProfileRolloutStrategy must be a non-empty string when present"
        )
    matched_rollout_rule_id = generated_from.get("runtimeProfileMatchedRolloutRuleId")
    if matched_rollout_rule_id is not None and (
        not isinstance(matched_rollout_rule_id, str) or not matched_rollout_rule_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfileMatchedRolloutRuleId must be a non-empty string when present"
        )
    generated_window_set_purpose = generated_from.get("windowSetPurpose")
    if generated_window_set_purpose is not None and (
        not isinstance(generated_window_set_purpose, str)
        or not generated_window_set_purpose
    ):
        raise ValueError(
            "generatedFrom.windowSetPurpose must be a non-empty string when present"
        )
    generated_window_set_batch_type = generated_from.get("windowSetBatchType")
    if generated_window_set_batch_type is not None and (
        not isinstance(generated_window_set_batch_type, str)
        or not generated_window_set_batch_type
    ):
        raise ValueError(
            "generatedFrom.windowSetBatchType must be a non-empty string when present"
        )
    for key in (
        "windowSetBatchTypeSelectionSource",
        "comparisonDimensionSelectionSource",
    ):
        selection_source = generated_from.get(key)
        if selection_source is None:
            continue
        if selection_source not in WINDOW_SET_METADATA_SELECTION_SOURCES:
            allowed = ", ".join(sorted(WINDOW_SET_METADATA_SELECTION_SOURCES))
            raise ValueError(
                f"generatedFrom.{key} must be one of [{allowed}], got {selection_source!r}"
            )
    purpose_policy_id = generated_from.get("runtimeProfilePurposePolicyId")
    if purpose_policy_id is not None and (
        not isinstance(purpose_policy_id, str) or not purpose_policy_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfilePurposePolicyId must be a non-empty string when present"
        )
    purpose_template_id = generated_from.get("runtimeProfilePurposeTemplateId")
    if purpose_template_id is not None and (
        not isinstance(purpose_template_id, str) or not purpose_template_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfilePurposeTemplateId must be a non-empty string when present"
        )
    purpose_template_family_id = generated_from.get(
        "runtimeProfilePurposeTemplateFamilyId"
    )
    if purpose_template_family_id is not None and (
        not isinstance(purpose_template_family_id, str)
        or not purpose_template_family_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfilePurposeTemplateFamilyId must be a non-empty string when present"
        )
    planner_metadata_policy_id = generated_from.get(
        "runtimeProfilePlannerMetadataPolicyId"
    )
    if planner_metadata_policy_id is not None and (
        not isinstance(planner_metadata_policy_id, str)
        or not planner_metadata_policy_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfilePlannerMetadataPolicyId must be a non-empty string when present"
        )
    planner_metadata_contract_family_id = generated_from.get(
        "runtimeProfilePlannerMetadataContractFamilyId"
    )
    if planner_metadata_contract_family_id is not None and (
        not isinstance(planner_metadata_contract_family_id, str)
        or not planner_metadata_contract_family_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfilePlannerMetadataContractFamilyId must be a non-empty string when present"
        )
    planner_metadata_contract_id = generated_from.get(
        "runtimeProfilePlannerMetadataContractId"
    )
    if planner_metadata_contract_id is not None and (
        not isinstance(planner_metadata_contract_id, str)
        or not planner_metadata_contract_id
    ):
        raise ValueError(
            "generatedFrom.runtimeProfilePlannerMetadataContractId must be a non-empty string when present"
        )
    windows = payload.get("windows")
    if not isinstance(windows, list) or not windows:
        raise ValueError("optimizer eval window set must include a non-empty `windows` list")
    runtime_sources = payload.get("runtimeSources")
    runtime_source_by_id: dict[str, dict[str, Any]] = {}
    if runtime_sources is not None:
        if not isinstance(runtime_sources, list) or not runtime_sources:
            raise ValueError(
                "optimizer eval window set runtimeSources must be a non-empty list when present"
            )
        for index, source in enumerate(runtime_sources):
            label = f"optimizer eval window set runtimeSources[{index}]"
            if not isinstance(source, dict):
                raise ValueError(f"{label} must be an object")
            _validate_runtime_source_payload(source, label=label)
            runtime_source_id = source["runtimeSourceId"]
            if runtime_source_id in runtime_source_by_id:
                raise ValueError(
                    "optimizer eval window set runtimeSources contains duplicate "
                    f"runtimeSourceId {runtime_source_id!r}"
                )
            runtime_source_by_id[runtime_source_id] = source
    has_profile_descriptors = any(
        isinstance(source, dict)
        and isinstance(source.get("sourceDescriptor"), dict)
        and isinstance(source["sourceDescriptor"].get("profileId"), str)
        and source["sourceDescriptor"].get("profileId")
        for source in (runtime_sources or [])
    )
    if has_profile_descriptors and runtime_profile_catalog_reference is None:
        raise ValueError(
            "optimizer eval window set must declare runtimeProfileCatalogReference when runtimeSources use planner profileId descriptors"
        )
    for index, window in enumerate(windows):
        label = f"optimizer eval window set windows[{index}]"
        if not isinstance(window, dict):
            raise ValueError(f"{label} must be an object")
        for key in (
            "windowId",
            "historyBatchLabel",
            "historyWindowLabel",
            "scenarioLabel",
            "generatedAt",
            "cycleId",
            "evalRunId",
            "reportId",
        ):
            _validate_string(window.get(key), label=f"{label}.{key}")
        runtime_source_id = window.get("runtimeSourceId")
        primary_input_keys = (
            "inputManifestPath",
            "inputBundlePath",
            "inputOfflineCyclePath",
        )
        present_inputs = [
            key for key in primary_input_keys if isinstance(window.get(key), str) and window.get(key)
        ]
        has_runtime_source_id = isinstance(runtime_source_id, str) and bool(runtime_source_id)
        has_direct_inputs = bool(present_inputs)
        if has_runtime_source_id == has_direct_inputs:
            raise ValueError(
                f"{label} must include exactly one source reference: `runtimeSourceId` or a direct primary input path"
            )
        if has_runtime_source_id:
            if not runtime_source_by_id:
                raise ValueError(
                    f"{label}.runtimeSourceId requires a top-level runtimeSources catalog"
                )
            if runtime_source_id not in runtime_source_by_id:
                raise ValueError(
                    f"{label}.runtimeSourceId {runtime_source_id!r} is not declared in runtimeSources"
                )
        elif len(present_inputs) != 1:
            allowed = ", ".join(primary_input_keys)
            raise ValueError(
                f"{label} must include exactly one primary input path from [{allowed}]"
            )
        mode = window.get("mode")
        if mode not in EVAL_WINDOW_SET_MODES:
            allowed = ", ".join(EVAL_WINDOW_SET_MODES)
            raise ValueError(f"{label}.mode must be one of [{allowed}], got {mode!r}")
        include_weekly_promotion = window.get("includeWeeklyPromotion")
        if not isinstance(include_weekly_promotion, bool):
            raise ValueError(f"{label}.includeWeeklyPromotion must be a boolean")
        expected_include_weekly = mode == "daily_with_weekly_promotion"
        if include_weekly_promotion != expected_include_weekly:
            raise ValueError(
                f"{label}.includeWeeklyPromotion must be {expected_include_weekly} for mode {mode!r}"
            )
        if has_runtime_source_id:
            declared_include_weekly = runtime_source_by_id[runtime_source_id][
                "includeWeeklyPromotion"
            ]
            if include_weekly_promotion != declared_include_weekly:
                raise ValueError(
                    f"{label}.includeWeeklyPromotion must match runtimeSources[{runtime_source_id!r}].includeWeeklyPromotion"
                )
        for key in ("rankingContractVersion", "rankingContractValidationMode"):
            value = window.get(key)
            if value is None:
                continue
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{label}.{key} must be a non-empty string when present"
                )
        summary_overrides = window.get("summaryOverrides")
        if summary_overrides is None:
            continue
        if not isinstance(summary_overrides, dict) or not summary_overrides:
            raise ValueError(f"{label}.summaryOverrides must be a non-empty object")
        unsupported_keys = sorted(
            key for key in summary_overrides if key not in ENTRY_SUMMARY_OVERRIDE_KEYS
        )
        if unsupported_keys:
            allowed = ", ".join(sorted(ENTRY_SUMMARY_OVERRIDE_KEYS))
            joined = ", ".join(unsupported_keys)
            raise ValueError(
                f"{label}.summaryOverrides contains unsupported keys [{joined}]; allowed keys are [{allowed}]"
            )


def load_optimizer_eval_window_set(window_set_path: Path) -> dict[str, Any]:
    payload = load_json(window_set_path)
    validate_optimizer_eval_window_set_payload(payload)
    return payload


def load_optimizer_runtime_artifact_registry(
    registry_path: Path,
) -> dict[str, Any]:
    payload = load_json(registry_path)
    validate_optimizer_runtime_artifact_registry_payload(payload)
    return payload


def load_optimizer_runtime_profile_catalog(
    catalog_path: Path,
) -> dict[str, Any]:
    payload = load_json(catalog_path)
    validate_optimizer_runtime_profile_catalog_payload(payload)
    return payload


def load_optimizer_runtime_materialization_plan(
    plan_path: Path,
) -> dict[str, Any]:
    payload = load_json(plan_path)
    validate_optimizer_runtime_materialization_plan_payload(payload)
    return payload


def resolve_runtime_source(
    source: dict[str, Any],
    *,
    artifact_registry: dict[str, Any] | None = None,
    runtime_profile_catalog: dict[str, Any] | None = None,
    runtime_profile_catalog_reference: dict[str, Any] | None = None,
    materialization_plan: dict[str, Any] | None = None,
    descriptor_path_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    resolved_source = dict(source)
    descriptor = source.get("sourceDescriptor")
    if not isinstance(descriptor, dict) or not descriptor:
        return resolved_source
    if runtime_profile_catalog_reference is not None:
        resolved_source["runtimeProfileCatalogId"] = runtime_profile_catalog_reference[
            "catalogId"
        ]
        resolved_source["runtimeProfileCatalogFamily"] = (
            runtime_profile_catalog_reference["catalogFamily"]
        )
        resolved_source["runtimeProfileCatalogVersion"] = (
            runtime_profile_catalog_reference["catalogVersion"]
        )
        resolved_source["runtimeProfileCatalogSchemaVersion"] = (
            runtime_profile_catalog_reference["schemaVersion"]
        )
    profile_id = descriptor.get("profileId")
    if isinstance(profile_id, str) and profile_id:
        resolved_source["runtimeProfileRequestedId"] = profile_id
        profile_entry = resolve_runtime_profile_entry(
            profile_id,
            runtime_profile_catalog=runtime_profile_catalog,
        )
        if isinstance(profile_entry, dict):
            canonical_profile_id = profile_entry.get("profileId")
            if isinstance(canonical_profile_id, str) and canonical_profile_id:
                resolved_source["runtimeProfileId"] = canonical_profile_id
                resolved_source["runtimeProfileAliasApplied"] = (
                    canonical_profile_id != profile_id
                )
            profile_job_family_group = profile_entry.get("jobFamilyGroup")
            if (
                isinstance(profile_job_family_group, str)
                and profile_job_family_group
            ):
                resolved_source["jobFamilyGroup"] = profile_job_family_group
            profile_materialization_profile = profile_entry.get(
                "materializationProfile"
            )
            if (
                isinstance(profile_materialization_profile, str)
                and profile_materialization_profile
            ):
                resolved_source["materializationProfile"] = (
                    profile_materialization_profile
                )
        else:
            resolved_source["runtimeProfileId"] = profile_id
            resolved_source["runtimeProfileAliasApplied"] = False
    job_family_group = descriptor.get("jobFamilyGroup")
    materialization_profile = descriptor.get("materializationProfile")
    if isinstance(job_family_group, str) and job_family_group:
        resolved_source["jobFamilyGroup"] = job_family_group
    if isinstance(materialization_profile, str) and materialization_profile:
        resolved_source["materializationProfile"] = materialization_profile
    resolved_binding = _resolve_runtime_source_descriptor_binding(
        descriptor,
        runtime_profile_catalog=runtime_profile_catalog,
    )
    if resolved_binding is None:
        return resolved_source
    binding_id, binding_payload = resolved_binding
    materialization_plan_id: str | None = None
    if artifact_registry is not None:
        for binding in artifact_registry.get("bindings", []):
            if not isinstance(binding, dict):
                continue
            if binding.get("bindingId") != binding_id:
                continue
            binding_job_family_group = binding.get("jobFamilyGroup")
            if isinstance(binding_job_family_group, str) and binding_job_family_group:
                resolved_source["jobFamilyGroup"] = binding_job_family_group
            binding_materialization_profile = binding.get("materializationProfile")
            if (
                isinstance(binding_materialization_profile, str)
                and binding_materialization_profile
            ):
                resolved_source["materializationProfile"] = (
                    binding_materialization_profile
                )
            plan_id = binding.get("materializationPlanId")
            if isinstance(plan_id, str) and plan_id:
                materialization_plan_id = plan_id
            artifact_field = binding.get("artifactField")
            artifact_path = binding.get("artifactPath")
            if (
                isinstance(artifact_field, str)
                and artifact_field in RUNTIME_ARTIFACT_FIELDS
                and isinstance(artifact_path, str)
                and artifact_path
            ):
                binding_payload = {artifact_field: artifact_path}
            break
    if descriptor_path_overrides and binding_id in descriptor_path_overrides:
        primary_input_key = next(iter(binding_payload))
        binding_payload[primary_input_key] = descriptor_path_overrides[binding_id]
    resolved_source.update(binding_payload)
    resolved_source["runtimeSourceKind"] = _classify_runtime_source_kind_from_descriptor(
        descriptor,
        runtime_profile_catalog=runtime_profile_catalog,
    )
    if materialization_plan_id is not None:
        resolved_source["materializationPlanId"] = materialization_plan_id
    if materialization_plan is not None and isinstance(materialization_plan_id, str):
        for plan in materialization_plan.get("plans", []):
            if not isinstance(plan, dict):
                continue
            if plan.get("planId") != materialization_plan_id:
                continue
            plan_job_family_group = plan.get("jobFamilyGroup")
            if isinstance(plan_job_family_group, str) and plan_job_family_group:
                resolved_source["jobFamilyGroup"] = plan_job_family_group
            plan_materialization_profile = plan.get("materializationProfile")
            if (
                isinstance(plan_materialization_profile, str)
                and plan_materialization_profile
            ):
                resolved_source["materializationProfile"] = (
                    plan_materialization_profile
                )
            resolved_source["materializationStrategy"] = plan.get(
                "materializationStrategy"
            )
            resolved_source["upstreamJobFamilies"] = list(
                plan.get("upstreamJobFamilies", [])
            )
            resolved_source["requiredArtifactKinds"] = list(
                plan.get("requiredArtifactKinds", [])
            )
            include_weekly_promotion = plan.get("includeWeeklyPromotion")
            if isinstance(include_weekly_promotion, bool):
                resolved_source["planIncludeWeeklyPromotion"] = include_weekly_promotion
            break
    return resolved_source


def build_eval_batch_manifest_entries_from_window_set(
    *,
    window_set_payload: dict[str, Any],
    path_style: str,
    artifact_registry: dict[str, Any] | None = None,
    runtime_profile_catalog: dict[str, Any] | None = None,
    materialization_plan: dict[str, Any] | None = None,
    descriptor_path_overrides: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    runtime_profile_catalog_reference = window_set_payload.get(
        "runtimeProfileCatalogReference"
    )
    if runtime_profile_catalog_reference is not None and runtime_profile_catalog is not None:
        catalog_id = runtime_profile_catalog.get("catalogId")
        catalog_family = runtime_profile_catalog.get("catalogFamily")
        catalog_version = runtime_profile_catalog.get("catalogVersion")
        schema_version = runtime_profile_catalog.get("schemaVersion")
        if catalog_id != runtime_profile_catalog_reference.get("catalogId"):
            raise ValueError(
                "runtime profile catalog id does not match window-set runtimeProfileCatalogReference.catalogId"
            )
        if catalog_family != runtime_profile_catalog_reference.get("catalogFamily"):
            raise ValueError(
                "runtime profile catalog family does not match window-set runtimeProfileCatalogReference.catalogFamily"
            )
        if catalog_version != runtime_profile_catalog_reference.get("catalogVersion"):
            raise ValueError(
                "runtime profile catalog version does not match window-set runtimeProfileCatalogReference.catalogVersion"
            )
        if schema_version != runtime_profile_catalog_reference.get("schemaVersion"):
            raise ValueError(
                "runtime profile catalog schemaVersion does not match window-set runtimeProfileCatalogReference.schemaVersion"
            )
    runtime_source_by_id = {
        source["runtimeSourceId"]: source
        for source in window_set_payload.get("runtimeSources", [])
        if isinstance(source, dict) and isinstance(source.get("runtimeSourceId"), str)
    }
    entries: list[dict[str, Any]] = []
    for window in window_set_payload["windows"]:
        runtime_source_id = window.get("runtimeSourceId")
        if isinstance(runtime_source_id, str) and runtime_source_id:
            runtime_source = resolve_runtime_source(
                runtime_source_by_id[runtime_source_id],
                artifact_registry=artifact_registry,
                runtime_profile_catalog=runtime_profile_catalog,
                runtime_profile_catalog_reference=runtime_profile_catalog_reference,
                materialization_plan=materialization_plan,
                descriptor_path_overrides=descriptor_path_overrides,
            )
        else:
            runtime_source = {
                "includeWeeklyPromotion": window["includeWeeklyPromotion"],
                "rankingContractVersion": window.get("rankingContractVersion"),
                "rankingContractValidationMode": window.get(
                    "rankingContractValidationMode"
                ),
            }
            for key in ("inputManifestPath", "inputBundlePath", "inputOfflineCyclePath"):
                value = window.get(key)
                if isinstance(value, str) and value:
                    runtime_source[key] = value
        entries.append(
            build_optimizer_eval_batch_manifest_entry(
                entry_id=window["windowId"],
                eval_run_id=window["evalRunId"],
                generated_at=window["generatedAt"],
                mode=window["mode"],
                cycle_id=window["cycleId"],
                report_id=window["reportId"],
                history_batch_label=window["historyBatchLabel"],
                history_window_label=window["historyWindowLabel"],
                scenario_label=window["scenarioLabel"],
                summary_overrides=window.get("summaryOverrides"),
                runtime_source=runtime_source,
                path_style=path_style,
            )
        )
    return entries
