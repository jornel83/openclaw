#!/usr/bin/env python3
"""
Helpers for planner-facing optimizer runtime profile catalogs.
"""

from __future__ import annotations

from typing import Any


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
OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-runtime-profile-family-registry.sample.v1"
)
OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION = (
    "optimizer-runtime-profile-family-registry.v1"
)
OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSIONS = {
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION,
}
RUNTIME_PROFILE_CATALOG_LANE_CURRENT = "current"
RUNTIME_PROFILE_CATALOG_LANE_PREVIEW = "preview"
RUNTIME_PROFILE_CATALOG_LANES = (
    RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
    RUNTIME_PROFILE_CATALOG_LANE_PREVIEW,
)
DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID = (
    "optimizer-runtime-profile-family-registry.autotiktok.fixture.2026-04-15"
)
DEFAULT_RUNTIME_PROFILE_FAMILY_ID = "autotiktok-runtime-profiles"
DEFAULT_RUNTIME_PROFILE_CATALOG_FAMILY = "autotiktok-runtime-profiles"
DEFAULT_RUNTIME_PROFILE_CATALOG_VERSION = "2026-04-15"
DEFAULT_RUNTIME_PROFILE_CATALOG_ID = (
    "optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15"
)
PREVIEW_RUNTIME_PROFILE_CATALOG_FAMILY = "autotiktok-runtime-profiles-preview"
PREVIEW_RUNTIME_PROFILE_CATALOG_VERSION = "2026-04-16-preview"
PREVIEW_RUNTIME_PROFILE_CATALOG_ID = (
    "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16"
)

DEFAULT_RUNTIME_PROFILE_BINDINGS: dict[str, dict[str, Any]] = {
    "optimizer_input_manifest_profile": {
        "bindingId": "optimizer_input_manifest",
        "runtimeSourceKind": "input_manifest",
        "includeWeeklyPromotion": False,
        "jobFamilyGroup": "optimizer_input_jobs",
        "materializationProfile": "manifest_from_job_runs",
        "sourceClass": "optimizer_input",
        "sourceVariant": "manifest",
        "rankingContractVersion": "ranking-optimizer-contract.v1",
        "rankingContractValidationMode": "exact",
        "payload": {
            "inputManifestPath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json"
        },
    },
    "optimizer_input_bundle_profile": {
        "bindingId": "optimizer_input_bundle",
        "runtimeSourceKind": "input_bundle",
        "includeWeeklyPromotion": True,
        "jobFamilyGroup": "optimizer_input_jobs",
        "materializationProfile": "bundle_from_manifest",
        "sourceClass": "optimizer_input",
        "sourceVariant": "bundle",
        "rankingContractVersion": "ranking-optimizer-contract.v1",
        "rankingContractValidationMode": "exact",
        "payload": {
            "inputBundlePath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json"
        },
    },
    "optimizer_offline_cycle_daily_profile": {
        "bindingId": "optimizer_offline_cycle_daily",
        "runtimeSourceKind": "offline_cycle",
        "includeWeeklyPromotion": False,
        "jobFamilyGroup": "optimizer_offline_cycle_jobs",
        "materializationProfile": "daily_cycle_from_manifest",
        "sourceClass": "optimizer_offline_cycle",
        "sourceVariant": "daily",
        "rankingContractVersion": "ranking-optimizer-contract.v1",
        "rankingContractValidationMode": "exact",
        "payload": {
            "inputOfflineCyclePath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle-daily.sample.json"
        },
    },
    "optimizer_offline_cycle_weekly_profile": {
        "bindingId": "optimizer_offline_cycle_weekly",
        "runtimeSourceKind": "offline_cycle",
        "includeWeeklyPromotion": True,
        "jobFamilyGroup": "optimizer_offline_cycle_jobs",
        "materializationProfile": "weekly_cycle_from_bundle",
        "sourceClass": "optimizer_offline_cycle",
        "sourceVariant": "weekly",
        "rankingContractVersion": "ranking-optimizer-contract.v1",
        "rankingContractValidationMode": "exact",
        "payload": {
            "inputOfflineCyclePath": "skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle.sample.json"
        },
    },
}
PREVIEW_RUNTIME_PROFILE_BINDINGS: dict[str, dict[str, Any]] = {
    "optimizer_input_manifest_profile_preview": {
        **DEFAULT_RUNTIME_PROFILE_BINDINGS["optimizer_input_manifest_profile"],
        "aliasProfileIds": ["optimizer_input_manifest_profile"],
    },
    "optimizer_input_bundle_profile_preview": {
        **DEFAULT_RUNTIME_PROFILE_BINDINGS["optimizer_input_bundle_profile"],
        "aliasProfileIds": ["optimizer_input_bundle_profile"],
    },
    "optimizer_offline_cycle_daily_profile_preview": {
        **DEFAULT_RUNTIME_PROFILE_BINDINGS["optimizer_offline_cycle_daily_profile"],
        "aliasProfileIds": ["optimizer_offline_cycle_daily_profile"],
    },
    "optimizer_offline_cycle_weekly_profile_preview": {
        **DEFAULT_RUNTIME_PROFILE_BINDINGS["optimizer_offline_cycle_weekly_profile"],
        "aliasProfileIds": ["optimizer_offline_cycle_weekly_profile"],
    },
}


def build_optimizer_runtime_profile_entry(
    *,
    profile_id: str,
    binding_id: str,
    runtime_source_kind: str,
    include_weekly_promotion: bool,
    job_family_group: str,
    materialization_profile: str,
    source_class: str,
    source_variant: str,
    ranking_contract_version: str,
    ranking_contract_validation_mode: str,
    alias_profile_ids: list[str] | None = None,
) -> dict[str, Any]:
    payload = {
        "profileId": profile_id,
        "bindingId": binding_id,
        "runtimeSourceKind": runtime_source_kind,
        "includeWeeklyPromotion": include_weekly_promotion,
        "jobFamilyGroup": job_family_group,
        "materializationProfile": materialization_profile,
        "sourceClass": source_class,
        "sourceVariant": source_variant,
        "rankingContractVersion": ranking_contract_version,
        "rankingContractValidationMode": ranking_contract_validation_mode,
    }
    if alias_profile_ids:
        payload["aliasProfileIds"] = alias_profile_ids
    return payload


def get_default_runtime_profile_catalog_metadata(
    *,
    catalog_lane: str = RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
) -> dict[str, str]:
    if catalog_lane == RUNTIME_PROFILE_CATALOG_LANE_CURRENT:
        return {
            "catalogId": DEFAULT_RUNTIME_PROFILE_CATALOG_ID,
            "catalogFamily": DEFAULT_RUNTIME_PROFILE_CATALOG_FAMILY,
            "catalogVersion": DEFAULT_RUNTIME_PROFILE_CATALOG_VERSION,
        }
    if catalog_lane == RUNTIME_PROFILE_CATALOG_LANE_PREVIEW:
        return {
            "catalogId": PREVIEW_RUNTIME_PROFILE_CATALOG_ID,
            "catalogFamily": PREVIEW_RUNTIME_PROFILE_CATALOG_FAMILY,
            "catalogVersion": PREVIEW_RUNTIME_PROFILE_CATALOG_VERSION,
        }
    allowed = ", ".join(RUNTIME_PROFILE_CATALOG_LANES)
    raise ValueError(f"catalog_lane must be one of [{allowed}], got {catalog_lane!r}")


def build_default_optimizer_runtime_profile_entries(
    *,
    catalog_lane: str = RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
) -> list[dict[str, Any]]:
    if catalog_lane == RUNTIME_PROFILE_CATALOG_LANE_CURRENT:
        bindings = DEFAULT_RUNTIME_PROFILE_BINDINGS
    elif catalog_lane == RUNTIME_PROFILE_CATALOG_LANE_PREVIEW:
        bindings = PREVIEW_RUNTIME_PROFILE_BINDINGS
    else:
        allowed = ", ".join(RUNTIME_PROFILE_CATALOG_LANES)
        raise ValueError(
            f"catalog_lane must be one of [{allowed}], got {catalog_lane!r}"
        )
    entries: list[dict[str, Any]] = []
    for profile_id, profile in bindings.items():
        entries.append(
            build_optimizer_runtime_profile_entry(
                profile_id=profile_id,
                binding_id=profile["bindingId"],
                runtime_source_kind=profile["runtimeSourceKind"],
                include_weekly_promotion=profile["includeWeeklyPromotion"],
                job_family_group=profile["jobFamilyGroup"],
                materialization_profile=profile["materializationProfile"],
                source_class=profile["sourceClass"],
                source_variant=profile["sourceVariant"],
                ranking_contract_version=profile["rankingContractVersion"],
                ranking_contract_validation_mode=profile[
                    "rankingContractValidationMode"
                ],
                alias_profile_ids=profile.get("aliasProfileIds"),
            )
        )
    return entries


def build_optimizer_runtime_profile_catalog_payload(
    *,
    profiles: list[dict[str, Any]],
    schema_version: str,
    catalog_id: str,
    catalog_family: str,
    catalog_version: str,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "catalogId": catalog_id,
        "catalogFamily": catalog_family,
        "catalogVersion": catalog_version,
        "generatedAt": generated_at,
        "generatedFrom": {
            "profileCount": len(profiles),
        },
        "profiles": profiles,
    }


def build_optimizer_runtime_profile_catalog_reference(
    *,
    catalog_id: str,
    schema_version: str,
    catalog_family: str,
    catalog_version: str,
) -> dict[str, str]:
    return {
        "catalogId": catalog_id,
        "schemaVersion": schema_version,
        "catalogFamily": catalog_family,
        "catalogVersion": catalog_version,
    }


def build_optimizer_runtime_profile_family_lane_entry(
    *,
    lane: str,
    catalog_reference: dict[str, str],
) -> dict[str, Any]:
    return {
        "lane": lane,
        "catalog": dict(catalog_reference),
    }


def build_optimizer_runtime_profile_family_entry(
    *,
    family_id: str,
    default_lane: str,
    lanes: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "familyId": family_id,
        "defaultLane": default_lane,
        "supportedLanes": [lane["lane"] for lane in lanes],
        "lanes": lanes,
    }


def build_default_runtime_profile_family_entries(
    *,
    catalog_schema_version: str = OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
) -> list[dict[str, Any]]:
    return [
        build_optimizer_runtime_profile_family_entry(
            family_id=DEFAULT_RUNTIME_PROFILE_FAMILY_ID,
            default_lane=RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
            lanes=[
                build_optimizer_runtime_profile_family_lane_entry(
                    lane=RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
                    catalog_reference=build_optimizer_runtime_profile_catalog_reference(
                        catalog_id=get_default_runtime_profile_catalog_metadata(
                            catalog_lane=RUNTIME_PROFILE_CATALOG_LANE_CURRENT
                        )["catalogId"],
                        catalog_family=get_default_runtime_profile_catalog_metadata(
                            catalog_lane=RUNTIME_PROFILE_CATALOG_LANE_CURRENT
                        )["catalogFamily"],
                        catalog_version=get_default_runtime_profile_catalog_metadata(
                            catalog_lane=RUNTIME_PROFILE_CATALOG_LANE_CURRENT
                        )["catalogVersion"],
                        schema_version=catalog_schema_version,
                    ),
                ),
                build_optimizer_runtime_profile_family_lane_entry(
                    lane=RUNTIME_PROFILE_CATALOG_LANE_PREVIEW,
                    catalog_reference=build_optimizer_runtime_profile_catalog_reference(
                        catalog_id=get_default_runtime_profile_catalog_metadata(
                            catalog_lane=RUNTIME_PROFILE_CATALOG_LANE_PREVIEW
                        )["catalogId"],
                        catalog_family=get_default_runtime_profile_catalog_metadata(
                            catalog_lane=RUNTIME_PROFILE_CATALOG_LANE_PREVIEW
                        )["catalogFamily"],
                        catalog_version=get_default_runtime_profile_catalog_metadata(
                            catalog_lane=RUNTIME_PROFILE_CATALOG_LANE_PREVIEW
                        )["catalogVersion"],
                        schema_version=catalog_schema_version,
                    ),
                ),
            ],
        )
    ]


def build_optimizer_runtime_profile_family_registry_payload(
    *,
    registry_id: str,
    schema_version: str,
    generated_at: str,
    families: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "registryId": registry_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "familyCount": len(families),
        },
        "families": families,
    }


def build_optimizer_runtime_profile_family_registry_reference(
    *,
    registry_id: str,
    schema_version: str,
    family_id: str,
    lane: str,
) -> dict[str, str]:
    return {
        "registryId": registry_id,
        "schemaVersion": schema_version,
        "familyId": family_id,
        "lane": lane,
    }


def _require_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def resolve_runtime_profile_entry(
    profile_id: str,
    *,
    runtime_profile_catalog: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if runtime_profile_catalog is not None:
        exact_match: dict[str, Any] | None = None
        alias_match: dict[str, Any] | None = None
        for profile in runtime_profile_catalog.get("profiles", []):
            if not isinstance(profile, dict):
                continue
            canonical_profile_id = profile.get("profileId")
            if canonical_profile_id == profile_id:
                exact_match = dict(profile)
                break
            aliases = profile.get("aliasProfileIds")
            if (
                alias_match is None
                and isinstance(aliases, list)
                and profile_id in aliases
            ):
                alias_match = dict(profile)
        if exact_match is not None:
            return exact_match
        if alias_match is not None:
            return alias_match
    default_profile = DEFAULT_RUNTIME_PROFILE_BINDINGS.get(profile_id)
    if default_profile is None:
        return None
    return build_optimizer_runtime_profile_entry(
        profile_id=profile_id,
        binding_id=default_profile["bindingId"],
        runtime_source_kind=default_profile["runtimeSourceKind"],
        include_weekly_promotion=default_profile["includeWeeklyPromotion"],
        job_family_group=default_profile["jobFamilyGroup"],
        materialization_profile=default_profile["materializationProfile"],
        source_class=default_profile["sourceClass"],
        source_variant=default_profile["sourceVariant"],
        ranking_contract_version=default_profile["rankingContractVersion"],
        ranking_contract_validation_mode=default_profile[
            "rankingContractValidationMode"
        ],
        alias_profile_ids=default_profile.get("aliasProfileIds"),
    )


def resolve_runtime_profile_catalog_reference_from_family_registry(
    *,
    family_id: str,
    lane: str,
    family_registry: dict[str, Any],
) -> dict[str, str]:
    for family in family_registry.get("families", []):
        if not isinstance(family, dict):
            continue
        if family.get("familyId") != family_id:
            continue
        for current_lane in family.get("lanes", []):
            if not isinstance(current_lane, dict):
                continue
            if current_lane.get("lane") != lane:
                continue
            catalog = current_lane.get("catalog")
            if not isinstance(catalog, dict):
                raise ValueError(
                    "optimizer runtime profile family registry lane catalog must be an object"
                )
            validate_optimizer_runtime_profile_catalog_reference(
                catalog,
                label=f"runtime profile family registry {family_id}:{lane} catalog",
            )
            return dict(catalog)
        raise ValueError(
            f"optimizer runtime profile family registry family {family_id!r} does not define lane {lane!r}"
        )
    raise ValueError(
        f"optimizer runtime profile family registry does not define familyId {family_id!r}"
    )


def validate_optimizer_runtime_profile_catalog_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSIONS))
        raise ValueError(
            "optimizer runtime profile catalog schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    _require_string(payload.get("catalogId"), label="catalogId")
    _require_string(payload.get("catalogFamily"), label="catalogFamily")
    _require_string(payload.get("catalogVersion"), label="catalogVersion")
    _require_string(payload.get("generatedAt"), label="generatedAt")
    profiles = payload.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError(
            "optimizer runtime profile catalog must include a non-empty `profiles` list"
        )
    seen_profile_ids: set[str] = set()
    seen_request_ids: set[str] = set()
    seen_binding_ids: set[str] = set()
    seen_planner_pairs: set[tuple[str, str]] = set()
    for index, profile in enumerate(profiles):
        label = f"optimizer runtime profile catalog profiles[{index}]"
        if not isinstance(profile, dict):
            raise ValueError(f"{label} must be an object")
        profile_id = _require_string(profile.get("profileId"), label=f"{label}.profileId")
        if profile_id in seen_profile_ids:
            raise ValueError(
                f"optimizer runtime profile catalog contains duplicate profileId {profile_id!r}"
            )
        seen_profile_ids.add(profile_id)
        if profile_id in seen_request_ids:
            raise ValueError(
                "optimizer runtime profile catalog contains duplicate requested "
                f"profile id {profile_id!r}"
            )
        seen_request_ids.add(profile_id)
        binding_id = _require_string(profile.get("bindingId"), label=f"{label}.bindingId")
        if binding_id in seen_binding_ids:
            raise ValueError(
                f"optimizer runtime profile catalog contains duplicate bindingId {binding_id!r}"
            )
        seen_binding_ids.add(binding_id)
        _require_string(
            profile.get("runtimeSourceKind"), label=f"{label}.runtimeSourceKind"
        )
        include_weekly_promotion = profile.get("includeWeeklyPromotion")
        if not isinstance(include_weekly_promotion, bool):
            raise ValueError(f"{label}.includeWeeklyPromotion must be a boolean")
        job_family_group = _require_string(
            profile.get("jobFamilyGroup"), label=f"{label}.jobFamilyGroup"
        )
        materialization_profile = _require_string(
            profile.get("materializationProfile"),
            label=f"{label}.materializationProfile",
        )
        planner_pair = (job_family_group, materialization_profile)
        if planner_pair in seen_planner_pairs:
            raise ValueError(
                "optimizer runtime profile catalog contains duplicate "
                f"jobFamilyGroup/materializationProfile pair {planner_pair!r}"
            )
        seen_planner_pairs.add(planner_pair)
        _require_string(profile.get("sourceClass"), label=f"{label}.sourceClass")
        _require_string(profile.get("sourceVariant"), label=f"{label}.sourceVariant")
        _require_string(
            profile.get("rankingContractVersion"),
            label=f"{label}.rankingContractVersion",
        )
        _require_string(
            profile.get("rankingContractValidationMode"),
            label=f"{label}.rankingContractValidationMode",
        )
        alias_profile_ids = profile.get("aliasProfileIds")
        if alias_profile_ids is None:
            continue
        if not isinstance(alias_profile_ids, list) or not alias_profile_ids:
            raise ValueError(f"{label}.aliasProfileIds must be a non-empty list")
        local_aliases: set[str] = set()
        for alias_index, alias_profile_id in enumerate(alias_profile_ids):
            alias_label = f"{label}.aliasProfileIds[{alias_index}]"
            alias_value = _require_string(alias_profile_id, label=alias_label)
            if alias_value == profile_id:
                raise ValueError(
                    f"{alias_label} must differ from canonical profileId {profile_id!r}"
                )
            if alias_value in local_aliases:
                raise ValueError(f"{alias_label} is duplicated within {label}")
            local_aliases.add(alias_value)
            if alias_value in seen_request_ids:
                raise ValueError(
                    "optimizer runtime profile catalog contains duplicate requested "
                    f"profile id {alias_value!r}"
                )
            seen_request_ids.add(alias_value)


def validate_optimizer_runtime_profile_family_registry_payload(
    payload: dict[str, Any],
) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSIONS:
        allowed = ", ".join(
            sorted(OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSIONS)
        )
        raise ValueError(
            "optimizer runtime profile family registry schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    _require_string(payload.get("registryId"), label="registryId")
    _require_string(payload.get("generatedAt"), label="generatedAt")
    families = payload.get("families")
    if not isinstance(families, list) or not families:
        raise ValueError(
            "optimizer runtime profile family registry must include a non-empty `families` list"
        )
    seen_family_ids: set[str] = set()
    for index, family in enumerate(families):
        label = f"optimizer runtime profile family registry families[{index}]"
        if not isinstance(family, dict):
            raise ValueError(f"{label} must be an object")
        family_id = _require_string(family.get("familyId"), label=f"{label}.familyId")
        if family_id in seen_family_ids:
            raise ValueError(
                f"optimizer runtime profile family registry contains duplicate familyId {family_id!r}"
            )
        seen_family_ids.add(family_id)
        default_lane = _require_string(
            family.get("defaultLane"), label=f"{label}.defaultLane"
        )
        supported_lanes = family.get("supportedLanes")
        if not isinstance(supported_lanes, list) or not supported_lanes:
            raise ValueError(f"{label}.supportedLanes must be a non-empty list")
        normalized_supported_lanes: list[str] = []
        for lane_index, supported_lane in enumerate(supported_lanes):
            lane_label = f"{label}.supportedLanes[{lane_index}]"
            lane_value = _require_string(supported_lane, label=lane_label)
            if lane_value in normalized_supported_lanes:
                raise ValueError(f"{lane_label} is duplicated within {label}")
            normalized_supported_lanes.append(lane_value)
        lanes = family.get("lanes")
        if not isinstance(lanes, list) or not lanes:
            raise ValueError(f"{label}.lanes must be a non-empty list")
        seen_lanes: set[str] = set()
        for lane_index, lane_entry in enumerate(lanes):
            lane_label = f"{label}.lanes[{lane_index}]"
            if not isinstance(lane_entry, dict):
                raise ValueError(f"{lane_label} must be an object")
            lane_name = _require_string(lane_entry.get("lane"), label=f"{lane_label}.lane")
            if lane_name in seen_lanes:
                raise ValueError(f"{lane_label}.lane is duplicated within {label}")
            seen_lanes.add(lane_name)
            if lane_name not in normalized_supported_lanes:
                raise ValueError(
                    f"{lane_label}.lane must also appear in {label}.supportedLanes"
                )
            validate_optimizer_runtime_profile_catalog_reference(
                lane_entry.get("catalog"),
                label=f"{lane_label}.catalog",
            )
        if default_lane not in seen_lanes:
            raise ValueError(
                f"{label}.defaultLane must also appear in {label}.lanes"
            )


def validate_optimizer_runtime_profile_catalog_reference(
    reference: dict[str, Any],
    *,
    label: str,
) -> None:
    if not isinstance(reference, dict):
        raise ValueError(f"{label} must be an object")
    _require_string(reference.get("catalogId"), label=f"{label}.catalogId")
    _require_string(reference.get("catalogFamily"), label=f"{label}.catalogFamily")
    _require_string(reference.get("catalogVersion"), label=f"{label}.catalogVersion")
    schema_version = _require_string(
        reference.get("schemaVersion"), label=f"{label}.schemaVersion"
    )
    if schema_version not in OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSIONS))
        raise ValueError(
            f"{label}.schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )


def validate_optimizer_runtime_profile_family_registry_reference(
    reference: dict[str, Any],
    *,
    label: str,
) -> None:
    if not isinstance(reference, dict):
        raise ValueError(f"{label} must be an object")
    _require_string(reference.get("registryId"), label=f"{label}.registryId")
    _require_string(reference.get("familyId"), label=f"{label}.familyId")
    lane = _require_string(reference.get("lane"), label=f"{label}.lane")
    if lane not in RUNTIME_PROFILE_CATALOG_LANES:
        allowed = ", ".join(RUNTIME_PROFILE_CATALOG_LANES)
        raise ValueError(f"{label}.lane must be one of [{allowed}], got {lane!r}")
    schema_version = _require_string(
        reference.get("schemaVersion"), label=f"{label}.schemaVersion"
    )
    if schema_version not in OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSIONS:
        allowed = ", ".join(
            sorted(OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSIONS)
        )
        raise ValueError(
            f"{label}.schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
