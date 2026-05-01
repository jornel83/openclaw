#!/usr/bin/env python3
"""
Helpers for optimizer input manifests and bundles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from optimizer_job_input_lib import (
    unwrap_challenger_evaluation_input,
    unwrap_post_performance_signal_input,
    unwrap_topic_outcome_backfill_input,
)
from reward_lib import load_json


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SKILL_ROOT.parents[1]

OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION = "optimizer-input-bundle.sample.v1"
OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSION = "optimizer-input-bundle.v1"
OPTIMIZER_INPUT_MANIFEST_SAMPLE_SCHEMA_VERSION = "optimizer-input-manifest.sample.v1"
OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSION = "optimizer-input-manifest.v1"
OPTIMIZER_INPUT_SOURCE_REGISTRY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-input-source-registry.sample.v1"
)
OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSION = "optimizer-input-source-registry.v1"
OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION = (
    "optimizer-source-artifact-catalog.sample.v1"
)
OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSION = (
    "optimizer-source-artifact-catalog.v1"
)
OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-source-provider-registry.sample.v1"
)
OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSION = (
    "optimizer-source-provider-registry.v1"
)
OPTIMIZER_SOURCE_PROVIDER_CATALOG_SAMPLE_SCHEMA_VERSION = (
    "optimizer-source-provider-catalog.sample.v1"
)
OPTIMIZER_SOURCE_PROVIDER_CATALOG_SCHEMA_VERSION = (
    "optimizer-source-provider-catalog.v1"
)
OPTIMIZER_JOB_ARTIFACT_RESOLVER_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-artifact-resolver.sample.v1"
)
OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSION = "optimizer-job-artifact-resolver.v1"

OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSIONS = {
    OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSION,
}
OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSIONS = {
    OPTIMIZER_INPUT_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSION,
}
OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSIONS = {
    OPTIMIZER_INPUT_SOURCE_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSION,
}
OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSIONS = {
    OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSION,
}
OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSIONS = {
    OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSION,
}
OPTIMIZER_SOURCE_PROVIDER_CATALOG_SCHEMA_VERSIONS = {
    OPTIMIZER_SOURCE_PROVIDER_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_PROVIDER_CATALOG_SCHEMA_VERSION,
}
OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_ARTIFACT_RESOLVER_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSION,
}

MANIFEST_ARTIFACT_KEYS = (
    "ranking",
    "context",
    "backfills",
    "performance",
    "challengerInput",
)
INPUT_SOURCE_RESOLUTION_MODES = {"direct_path", "job_artifact_resolver"}
SOURCE_PROVIDER_KINDS = {"materialized_fixture", "raw_job_envelope"}
SOURCE_ARTIFACT_CATALOG_RESOLUTION_MODES = {"direct_path", "artifact_catalog_entry"}
SOURCE_PROVIDER_RESOLUTION_MODES = {"direct_path", "provider_binding_registry"}
SOURCE_PROVIDER_LOCATOR_KINDS = {"artifact_uri"}
SOURCE_PROVIDER_BINDING_KINDS = {"catalog_service_binding"}
SOURCE_PROVIDER_BINDING_LOCATOR_KINDS = {"artifact_locator_reference"}
SOURCE_ARTIFACT_LOCATOR_KINDS = {"provider_locator"}
SOURCE_PROVIDER_SOURCE_CLASSES = {"artifact_catalog_service"}
JOB_ARTIFACT_RESOLVER_STRATEGIES = {"provider_catalog_locator"}

RESOLVED_SOURCE_METADATA_FIELDS = (
    "providerLane",
    "providerKind",
    "upstreamJobKind",
    "sourceProviderId",
    "providerClass",
    "providerHandle",
    "providerEndpoint",
    "locatorKind",
    "providerBindingId",
    "providerBindingKind",
    "providerOwner",
    "bindingLocatorKind",
    "artifactCatalogEntryId",
    "artifactLocatorKind",
    "artifactLocatorUri",
    "providerSourceClass",
    "resolverEntryId",
    "resolverStrategy",
    "providerRequestKey",
)


def _path_label(path: Path, *, style: str) -> str:
    if style == "absolute":
        return str(path)
    if style == "basename":
        return path.name
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _require_optional_string(
    payload: dict[str, Any], *, field_name: str, label: str
) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}.{field_name} must be a non-empty string when present")
    return value


def _collect_uniform_value(
    sources: list[dict[str, Any]], field_name: str
) -> str | None:
    values = {
        value
        for source in sources
        if isinstance(source, dict)
        for value in [source.get(field_name)]
        if isinstance(value, str) and value
    }
    if not values:
        return None
    if len(values) == 1:
        return next(iter(values))
    return None


def _build_resolved_source_metadata(source: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        "bindingId": source.get("bindingId"),
        "artifactKey": source.get("artifactKey"),
        "sourceLane": source.get("sourceLane"),
        "resolutionMode": source.get("resolutionMode", "direct_path"),
    }
    for field_name in RESOLVED_SOURCE_METADATA_FIELDS:
        value = source.get(field_name)
        if isinstance(value, str) and value:
            metadata[field_name] = value
    return metadata


def build_optimizer_input_bundle_payload(
    *,
    ranking_payload: dict[str, Any],
    context_payload: dict[str, Any],
    backfills_payload: dict[str, Any],
    performance_payload: dict[str, Any],
    challenger_input_payload: dict[str, Any],
    schema_version: str,
    bundle_id: str,
    generated_at: str,
) -> dict[str, Any]:
    ranking_run = ranking_payload.get("predictionRun", {})
    candidate_source = ranking_payload.get("candidateSource", {})
    normalized_backfills_payload, backfills_source = unwrap_topic_outcome_backfill_input(
        backfills_payload
    )
    (
        normalized_performance_payload,
        performance_source,
    ) = unwrap_post_performance_signal_input(performance_payload)
    (
        normalized_challenger_input_payload,
        challenger_input_source,
    ) = unwrap_challenger_evaluation_input(challenger_input_payload)
    return {
        "schemaVersion": schema_version,
        "bundleId": bundle_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "rankingRunId": ranking_run.get("runId"),
            "rankingSnapshotId": ranking_run.get("snapshotId"),
            "rankingProfileId": ranking_run.get("profileId"),
            "candidateSourceKind": candidate_source.get("sourceKind"),
            "candidateSourceSnapshotId": candidate_source.get("sourceSnapshotId"),
            "candidateSourceInputKind": candidate_source.get("sourceInputKind"),
            "candidateSourceMaterializationId": candidate_source.get(
                "sourceMaterializationId"
            ),
            "candidateSourceNormalizationRuleVersion": candidate_source.get(
                "sourceNormalizationRuleVersion"
            ),
            "inputSources": {
                "backfills": backfills_source,
                "performance": performance_source,
                "challengerInput": challenger_input_source,
            },
        },
        "artifacts": {
            "ranking": ranking_payload,
            "context": context_payload,
            "backfills": normalized_backfills_payload,
            "performance": normalized_performance_payload,
            "challengerInput": normalized_challenger_input_payload,
        },
    }


def build_optimizer_input_manifest_payload(
    *,
    ranking_input: Path,
    context_input: Path,
    backfills_input: Path,
    performance_input: Path,
    challenger_input: Path,
    schema_version: str,
    manifest_id: str,
    generated_at: str,
    path_style: str,
    artifact_bindings: dict[str, str] | None = None,
    input_source_registry_reference: dict[str, str] | None = None,
    source_lane: str | None = None,
    generated_from_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ranking_payload = load_json(ranking_input)
    ranking_run = ranking_payload.get("predictionRun", {})
    payload = {
        "schemaVersion": schema_version,
        "manifestId": manifest_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "rankingRunId": ranking_run.get("runId"),
            "rankingSnapshotId": ranking_run.get("snapshotId"),
            "rankingProfileId": ranking_run.get("profileId"),
        },
    }
    if source_lane is not None:
        payload["generatedFrom"]["sourceLane"] = source_lane
    if generated_from_overrides is not None:
        payload["generatedFrom"].update(generated_from_overrides)
    if artifact_bindings is not None:
        if input_source_registry_reference is None:
            raise ValueError(
                "input_source_registry_reference is required when artifact_bindings are provided"
            )
        payload["artifactBindings"] = dict(artifact_bindings)
        payload["inputSourceRegistryReference"] = dict(input_source_registry_reference)
        return payload
    payload["artifactPaths"] = {
        "ranking": _path_label(ranking_input, style=path_style),
        "context": _path_label(context_input, style=path_style),
        "backfills": _path_label(backfills_input, style=path_style),
        "performance": _path_label(performance_input, style=path_style),
        "challengerInput": _path_label(challenger_input, style=path_style),
    }
    return payload


def build_optimizer_input_manifest_from_source_registry(
    *,
    registry_path: Path,
    source_lane: str,
    schema_version: str,
    manifest_id: str,
    generated_at: str,
    input_rollout_policy_reference: dict[str, str] | None = None,
    input_rollout_class: str | None = None,
    input_lane_selection_source: str | None = None,
    input_rollout_strategy: str | None = None,
) -> dict[str, Any]:
    registry_payload, registry_sources = load_optimizer_input_source_registry(
        registry_path
    )
    artifact_bindings: dict[str, str] = {}
    resolved_paths: dict[str, Path] = {}
    selected_sources: list[dict[str, Any]] = []
    selected_sources_by_key: dict[str, dict[str, Any]] = {}
    for key in MANIFEST_ARTIFACT_KEYS:
        matches = [
            source
            for source in registry_sources.values()
            if source["artifactKey"] == key and source["sourceLane"] == source_lane
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one optimizer input binding for artifactKey={key!r} "
                f"lane={source_lane!r}"
            )
        source = matches[0]
        selected_sources.append(source)
        selected_sources_by_key[key] = source
        artifact_bindings[key] = source["bindingId"]
        resolved_paths[key] = source["resolvedPath"]

    generated_from_overrides: dict[str, Any] = {
        "optimizerInputSourceRegistrySchemaVersion": registry_payload.get(
            "schemaVersion"
        ),
        "optimizerInputSourceRegistryId": registry_payload.get("registryId"),
    }
    if any(
        source.get("resolutionMode") == "job_artifact_resolver"
        for source in selected_sources
    ):
        generated_from_overrides["optimizerInputArtifactResolverSchemaVersion"] = (
            registry_payload.get("resolvedInputArtifactResolverSchemaVersion")
        )
        generated_from_overrides["optimizerInputArtifactResolverId"] = registry_payload.get(
            "resolvedInputArtifactResolverId"
        )
        generated_from_overrides[
            "optimizerInputSourceProviderCatalogSchemaVersion"
        ] = registry_payload.get("resolvedInputSourceProviderCatalogSchemaVersion")
        generated_from_overrides["optimizerInputSourceProviderCatalogId"] = (
            registry_payload.get("resolvedInputSourceProviderCatalogId")
        )
        generated_from_overrides[
            "optimizerInputSourceProviderRegistrySchemaVersion"
        ] = registry_payload.get("resolvedInputSourceProviderRegistrySchemaVersion")
        generated_from_overrides["optimizerInputSourceProviderRegistryId"] = (
            registry_payload.get("resolvedInputSourceProviderRegistryId")
        )
        generated_from_overrides[
            "optimizerInputSourceArtifactCatalogSchemaVersion"
        ] = registry_payload.get("resolvedInputSourceArtifactCatalogSchemaVersion")
        generated_from_overrides["optimizerInputSourceArtifactCatalogId"] = (
            registry_payload.get("resolvedInputSourceArtifactCatalogId")
        )
        generated_from_overrides["optimizerInputSourceProviderLane"] = (
            _collect_uniform_value(selected_sources, "providerLane")
        )
        generated_from_overrides["optimizerInputSourceProviderKind"] = (
            _collect_uniform_value(selected_sources, "providerKind")
        )
        generated_from_overrides["optimizerInputSourceProviderClass"] = (
            _collect_uniform_value(selected_sources, "providerClass")
        )
        generated_from_overrides["optimizerInputSourceProviderHandle"] = (
            _collect_uniform_value(selected_sources, "providerHandle")
        )
        generated_from_overrides["optimizerInputSourceProviderLocatorKind"] = (
            _collect_uniform_value(selected_sources, "locatorKind")
        )
        generated_from_overrides["optimizerInputSourceProviderOwner"] = (
            _collect_uniform_value(selected_sources, "providerOwner")
        )
        generated_from_overrides["optimizerInputArtifactLocatorKind"] = (
            _collect_uniform_value(selected_sources, "artifactLocatorKind")
        )
        generated_from_overrides["resolvedSources"] = {
            key: _build_resolved_source_metadata(source)
            for key, source in selected_sources_by_key.items()
        }
    if input_rollout_policy_reference is not None:
        generated_from_overrides["inputRolloutPolicySchemaVersion"] = (
            input_rollout_policy_reference.get("schemaVersion")
        )
        generated_from_overrides["inputRolloutPolicyId"] = (
            input_rollout_policy_reference.get("policyId")
        )
    if input_rollout_class is not None:
        generated_from_overrides["inputRolloutClass"] = input_rollout_class
    if input_lane_selection_source is not None:
        generated_from_overrides["inputLaneSelectionSource"] = (
            input_lane_selection_source
        )
    if input_rollout_strategy is not None:
        generated_from_overrides["inputRolloutStrategy"] = input_rollout_strategy

    try:
        registry_path_label = registry_path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        registry_path_label = str(registry_path)

    return build_optimizer_input_manifest_payload(
        ranking_input=resolved_paths["ranking"],
        context_input=resolved_paths["context"],
        backfills_input=resolved_paths["backfills"],
        performance_input=resolved_paths["performance"],
        challenger_input=resolved_paths["challengerInput"],
        schema_version=schema_version,
        manifest_id=manifest_id,
        generated_at=generated_at,
        path_style="repo",
        artifact_bindings=artifact_bindings,
        input_source_registry_reference={
            "schemaVersion": registry_payload.get("schemaVersion"),
            "registryId": registry_payload.get("registryId"),
            "path": registry_path_label,
        },
        source_lane=source_lane,
        generated_from_overrides=generated_from_overrides,
    )


def build_optimizer_input_source_registry_payload(
    *,
    schema_version: str,
    registry_id: str,
    generated_at: str,
    sources: list[dict[str, Any]],
    input_artifact_resolver_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schemaVersion": schema_version,
        "registryId": registry_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "sourceCount": len(sources),
            "laneCount": len(
                {source["sourceLane"] for source in sources if "sourceLane" in source}
            ),
        },
        "sources": sources,
    }
    if input_artifact_resolver_reference is not None:
        payload["inputArtifactResolverReference"] = dict(
            input_artifact_resolver_reference
        )
    return payload


def build_optimizer_source_artifact_catalog_payload(
    *,
    schema_version: str,
    catalog_id: str,
    generated_at: str,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "catalogId": catalog_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "entryCount": len(entries),
            "laneCount": len(
                {
                    entry["providerLane"]
                    for entry in entries
                    if "providerLane" in entry
                }
            ),
        },
        "entries": entries,
    }


def build_optimizer_source_provider_registry_payload(
    *,
    schema_version: str,
    registry_id: str,
    generated_at: str,
    bindings: list[dict[str, Any]],
    input_source_artifact_catalog_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schemaVersion": schema_version,
        "registryId": registry_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "bindingCount": len(bindings),
            "laneCount": len(
                {
                    binding["providerLane"]
                    for binding in bindings
                    if "providerLane" in binding
                }
            ),
        },
        "bindings": bindings,
    }
    if input_source_artifact_catalog_reference is not None:
        payload["inputSourceArtifactCatalogReference"] = dict(
            input_source_artifact_catalog_reference
        )
    return payload


def build_optimizer_source_provider_catalog_payload(
    *,
    schema_version: str,
    catalog_id: str,
    generated_at: str,
    providers: list[dict[str, Any]],
    input_source_provider_registry_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schemaVersion": schema_version,
        "catalogId": catalog_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "providerCount": len(providers),
            "laneCount": len(
                {
                    provider["providerLane"]
                    for provider in providers
                    if "providerLane" in provider
                }
            ),
        },
        "providers": providers,
    }
    if input_source_provider_registry_reference is not None:
        payload["inputSourceProviderRegistryReference"] = dict(
            input_source_provider_registry_reference
        )
    return payload


def build_optimizer_job_artifact_resolver_payload(
    *,
    schema_version: str,
    resolver_id: str,
    generated_at: str,
    entries: list[dict[str, Any]],
    input_source_provider_catalog_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schemaVersion": schema_version,
        "resolverId": resolver_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "entryCount": len(entries),
            "laneCount": len(
                {
                    entry["resolverLane"]
                    for entry in entries
                    if "resolverLane" in entry
                }
            ),
        },
        "entries": entries,
    }
    if input_source_provider_catalog_reference is not None:
        payload["inputSourceProviderCatalogReference"] = dict(
            input_source_provider_catalog_reference
        )
    return payload


def validate_optimizer_input_manifest_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_INPUT_MANIFEST_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer input manifest schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    artifact_paths = payload.get("artifactPaths")
    artifact_bindings = payload.get("artifactBindings")
    has_paths = isinstance(artifact_paths, dict)
    has_bindings = isinstance(artifact_bindings, dict)
    if has_paths == has_bindings:
        raise ValueError(
            "optimizer input manifest must include exactly one of `artifactPaths` or `artifactBindings`"
        )
    if has_paths:
        for key in MANIFEST_ARTIFACT_KEYS:
            value = artifact_paths.get(key)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"optimizer input manifest artifactPaths.{key} must be a non-empty string"
                )
        return
    registry_reference = payload.get("inputSourceRegistryReference")
    if not isinstance(registry_reference, dict):
        raise ValueError(
            "optimizer input manifest with artifactBindings must include object `inputSourceRegistryReference`"
        )
    path_value = registry_reference.get("path")
    if not isinstance(path_value, str) or not path_value:
        raise ValueError(
            "optimizer input manifest inputSourceRegistryReference.path must be a non-empty string"
        )
    for key in MANIFEST_ARTIFACT_KEYS:
        value = artifact_bindings.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(
                f"optimizer input manifest artifactBindings.{key} must be a non-empty string"
            )


def validate_optimizer_input_source_registry_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer input source registry schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(
            "optimizer input source registry must include a non-empty `sources` list"
        )
    resolver_reference = payload.get("inputArtifactResolverReference")
    if resolver_reference is not None:
        if not isinstance(resolver_reference, dict):
            raise ValueError(
                "optimizer input source registry inputArtifactResolverReference must be an object"
            )
        path_value = resolver_reference.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(
                "optimizer input source registry inputArtifactResolverReference.path must be a non-empty string"
            )
    seen_binding_ids: set[str] = set()
    for index, source in enumerate(sources):
        label = f"optimizer input source registry sources[{index}]"
        if not isinstance(source, dict):
            raise ValueError(f"{label} must be an object")
        binding_id = source.get("bindingId")
        if not isinstance(binding_id, str) or not binding_id:
            raise ValueError(f"{label}.bindingId must be a non-empty string")
        if binding_id in seen_binding_ids:
            raise ValueError(f"{label}.bindingId is duplicated: {binding_id}")
        seen_binding_ids.add(binding_id)
        artifact_key = source.get("artifactKey")
        if artifact_key not in MANIFEST_ARTIFACT_KEYS:
            allowed = ", ".join(MANIFEST_ARTIFACT_KEYS)
            raise ValueError(f"{label}.artifactKey must be one of [{allowed}]")
        source_lane = source.get("sourceLane")
        if not isinstance(source_lane, str) or not source_lane:
            raise ValueError(f"{label}.sourceLane must be a non-empty string")
        resolution_mode = source.get("resolutionMode", "direct_path")
        if resolution_mode not in INPUT_SOURCE_RESOLUTION_MODES:
            allowed = ", ".join(sorted(INPUT_SOURCE_RESOLUTION_MODES))
            raise ValueError(f"{label}.resolutionMode must be one of [{allowed}]")
        if resolution_mode == "direct_path":
            path_value = source.get("path")
            if not isinstance(path_value, str) or not path_value:
                raise ValueError(f"{label}.path must be a non-empty string")
            continue
        if resolver_reference is None:
            raise ValueError(
                f"{label} uses job_artifact_resolver but registry has no inputArtifactResolverReference"
            )
        resolver_entry_id = source.get("resolverEntryId")
        if not isinstance(resolver_entry_id, str) or not resolver_entry_id:
            raise ValueError(
                f"{label}.resolverEntryId must be a non-empty string when resolutionMode=job_artifact_resolver"
            )


def validate_optimizer_source_provider_catalog_payload(payload: dict[str, Any]) -> None:
    registry_reference = payload.get("inputSourceProviderRegistryReference")
    if registry_reference is not None:
        if not isinstance(registry_reference, dict):
            raise ValueError(
                "optimizer source provider catalog inputSourceProviderRegistryReference must be an object"
            )
        path_value = registry_reference.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(
                "optimizer source provider catalog inputSourceProviderRegistryReference.path must be a non-empty string"
            )
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_SOURCE_PROVIDER_CATALOG_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_SOURCE_PROVIDER_CATALOG_SCHEMA_VERSIONS))
        raise ValueError(
            "optimizer source provider catalog schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    providers = payload.get("providers")
    if not isinstance(providers, list) or not providers:
        raise ValueError(
            "optimizer source provider catalog must include a non-empty `providers` list"
        )
    seen_provider_ids: set[str] = set()
    for index, provider in enumerate(providers):
        label = f"optimizer source provider catalog providers[{index}]"
        if not isinstance(provider, dict):
            raise ValueError(f"{label} must be an object")
        source_provider_id = provider.get("sourceProviderId")
        if not isinstance(source_provider_id, str) or not source_provider_id:
            raise ValueError(f"{label}.sourceProviderId must be a non-empty string")
        if source_provider_id in seen_provider_ids:
            raise ValueError(
                f"{label}.sourceProviderId is duplicated: {source_provider_id}"
            )
        seen_provider_ids.add(source_provider_id)
        artifact_key = provider.get("artifactKey")
        if artifact_key not in MANIFEST_ARTIFACT_KEYS:
            allowed = ", ".join(MANIFEST_ARTIFACT_KEYS)
            raise ValueError(f"{label}.artifactKey must be one of [{allowed}]")
        provider_lane = provider.get("providerLane")
        if not isinstance(provider_lane, str) or not provider_lane:
            raise ValueError(f"{label}.providerLane must be a non-empty string")
        provider_kind = provider.get("providerKind")
        if provider_kind not in SOURCE_PROVIDER_KINDS:
            allowed = ", ".join(sorted(SOURCE_PROVIDER_KINDS))
            raise ValueError(f"{label}.providerKind must be one of [{allowed}]")
        upstream_job_kind = provider.get("upstreamJobKind")
        if not isinstance(upstream_job_kind, str) or not upstream_job_kind:
            raise ValueError(f"{label}.upstreamJobKind must be a non-empty string")
        locator_kind = _require_optional_string(
            provider, field_name="locatorKind", label=label
        )
        if locator_kind is not None and locator_kind not in SOURCE_PROVIDER_LOCATOR_KINDS:
            allowed = ", ".join(sorted(SOURCE_PROVIDER_LOCATOR_KINDS))
            raise ValueError(f"{label}.locatorKind must be one of [{allowed}]")
        provider_class = _require_optional_string(
            provider, field_name="providerClass", label=label
        )
        if (
            provider_class is not None
            and provider_class not in SOURCE_PROVIDER_SOURCE_CLASSES
        ):
            allowed = ", ".join(sorted(SOURCE_PROVIDER_SOURCE_CLASSES))
            raise ValueError(f"{label}.providerClass must be one of [{allowed}]")
        _require_optional_string(provider, field_name="providerHandle", label=label)
        _require_optional_string(provider, field_name="providerEndpoint", label=label)
        resolution_mode = provider.get("resolutionMode", "direct_path")
        if resolution_mode not in SOURCE_PROVIDER_RESOLUTION_MODES:
            allowed = ", ".join(sorted(SOURCE_PROVIDER_RESOLUTION_MODES))
            raise ValueError(f"{label}.resolutionMode must be one of [{allowed}]")
        if resolution_mode == "direct_path":
            path_value = provider.get("path")
            if not isinstance(path_value, str) or not path_value:
                raise ValueError(f"{label}.path must be a non-empty string")
            continue
        if registry_reference is None:
            raise ValueError(
                f"{label} uses provider_binding_registry but catalog has no inputSourceProviderRegistryReference"
            )
        provider_binding_id = provider.get("providerBindingId")
        if not isinstance(provider_binding_id, str) or not provider_binding_id:
            raise ValueError(
                f"{label}.providerBindingId must be a non-empty string when resolutionMode=provider_binding_registry"
            )


def validate_optimizer_source_artifact_catalog_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSIONS))
        raise ValueError(
            "optimizer source artifact catalog schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "optimizer source artifact catalog must include a non-empty `entries` list"
        )
    seen_entry_ids: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"optimizer source artifact catalog entries[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        entry_id = entry.get("artifactCatalogEntryId")
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(f"{label}.artifactCatalogEntryId must be a non-empty string")
        if entry_id in seen_entry_ids:
            raise ValueError(
                f"{label}.artifactCatalogEntryId is duplicated: {entry_id}"
            )
        seen_entry_ids.add(entry_id)
        artifact_key = entry.get("artifactKey")
        if artifact_key not in MANIFEST_ARTIFACT_KEYS:
            allowed = ", ".join(MANIFEST_ARTIFACT_KEYS)
            raise ValueError(f"{label}.artifactKey must be one of [{allowed}]")
        provider_lane = entry.get("providerLane")
        if not isinstance(provider_lane, str) or not provider_lane:
            raise ValueError(f"{label}.providerLane must be a non-empty string")
        provider_kind = entry.get("providerKind")
        if provider_kind not in SOURCE_PROVIDER_KINDS:
            allowed = ", ".join(sorted(SOURCE_PROVIDER_KINDS))
            raise ValueError(f"{label}.providerKind must be one of [{allowed}]")
        upstream_job_kind = entry.get("upstreamJobKind")
        if not isinstance(upstream_job_kind, str) or not upstream_job_kind:
            raise ValueError(f"{label}.upstreamJobKind must be a non-empty string")
        artifact_locator_kind = _require_optional_string(
            entry, field_name="artifactLocatorKind", label=label
        )
        if (
            artifact_locator_kind is not None
            and artifact_locator_kind not in SOURCE_ARTIFACT_LOCATOR_KINDS
        ):
            allowed = ", ".join(sorted(SOURCE_ARTIFACT_LOCATOR_KINDS))
            raise ValueError(f"{label}.artifactLocatorKind must be one of [{allowed}]")
        provider_source_class = _require_optional_string(
            entry, field_name="providerSourceClass", label=label
        )
        if (
            provider_source_class is not None
            and provider_source_class not in SOURCE_PROVIDER_SOURCE_CLASSES
        ):
            allowed = ", ".join(sorted(SOURCE_PROVIDER_SOURCE_CLASSES))
            raise ValueError(f"{label}.providerSourceClass must be one of [{allowed}]")
        _require_optional_string(entry, field_name="artifactLocatorUri", label=label)
        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(f"{label}.path must be a non-empty string")


def validate_optimizer_source_provider_registry_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSIONS))
        raise ValueError(
            "optimizer source provider registry schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    artifact_catalog_reference = payload.get("inputSourceArtifactCatalogReference")
    if artifact_catalog_reference is not None:
        if not isinstance(artifact_catalog_reference, dict):
            raise ValueError(
                "optimizer source provider registry inputSourceArtifactCatalogReference must be an object"
            )
        path_value = artifact_catalog_reference.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(
                "optimizer source provider registry inputSourceArtifactCatalogReference.path must be a non-empty string"
            )
    bindings = payload.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        raise ValueError(
            "optimizer source provider registry must include a non-empty `bindings` list"
        )
    seen_binding_ids: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"optimizer source provider registry bindings[{index}]"
        if not isinstance(binding, dict):
            raise ValueError(f"{label} must be an object")
        binding_id = binding.get("providerBindingId")
        if not isinstance(binding_id, str) or not binding_id:
            raise ValueError(f"{label}.providerBindingId must be a non-empty string")
        if binding_id in seen_binding_ids:
            raise ValueError(
                f"{label}.providerBindingId is duplicated: {binding_id}"
            )
        seen_binding_ids.add(binding_id)
        artifact_key = binding.get("artifactKey")
        if artifact_key not in MANIFEST_ARTIFACT_KEYS:
            allowed = ", ".join(MANIFEST_ARTIFACT_KEYS)
            raise ValueError(f"{label}.artifactKey must be one of [{allowed}]")
        provider_lane = binding.get("providerLane")
        if not isinstance(provider_lane, str) or not provider_lane:
            raise ValueError(f"{label}.providerLane must be a non-empty string")
        provider_kind = binding.get("providerKind")
        if provider_kind not in SOURCE_PROVIDER_KINDS:
            allowed = ", ".join(sorted(SOURCE_PROVIDER_KINDS))
            raise ValueError(f"{label}.providerKind must be one of [{allowed}]")
        upstream_job_kind = binding.get("upstreamJobKind")
        if not isinstance(upstream_job_kind, str) or not upstream_job_kind:
            raise ValueError(f"{label}.upstreamJobKind must be a non-empty string")
        provider_binding_kind = _require_optional_string(
            binding, field_name="providerBindingKind", label=label
        )
        if (
            provider_binding_kind is not None
            and provider_binding_kind not in SOURCE_PROVIDER_BINDING_KINDS
        ):
            allowed = ", ".join(sorted(SOURCE_PROVIDER_BINDING_KINDS))
            raise ValueError(f"{label}.providerBindingKind must be one of [{allowed}]")
        binding_locator_kind = _require_optional_string(
            binding, field_name="bindingLocatorKind", label=label
        )
        if (
            binding_locator_kind is not None
            and binding_locator_kind not in SOURCE_PROVIDER_BINDING_LOCATOR_KINDS
        ):
            allowed = ", ".join(sorted(SOURCE_PROVIDER_BINDING_LOCATOR_KINDS))
            raise ValueError(f"{label}.bindingLocatorKind must be one of [{allowed}]")
        _require_optional_string(binding, field_name="providerOwner", label=label)
        resolution_mode = binding.get("resolutionMode", "direct_path")
        if resolution_mode not in SOURCE_ARTIFACT_CATALOG_RESOLUTION_MODES:
            allowed = ", ".join(sorted(SOURCE_ARTIFACT_CATALOG_RESOLUTION_MODES))
            raise ValueError(f"{label}.resolutionMode must be one of [{allowed}]")
        if resolution_mode == "direct_path":
            path_value = binding.get("path")
            if not isinstance(path_value, str) or not path_value:
                raise ValueError(f"{label}.path must be a non-empty string")
            continue
        if artifact_catalog_reference is None:
            raise ValueError(
                f"{label} uses artifact_catalog_entry but registry has no inputSourceArtifactCatalogReference"
            )
        entry_id = binding.get("artifactCatalogEntryId")
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(
                f"{label}.artifactCatalogEntryId must be a non-empty string when resolutionMode=artifact_catalog_entry"
            )


def validate_optimizer_job_artifact_resolver_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer job artifact resolver schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "optimizer job artifact resolver must include a non-empty `entries` list"
        )
    provider_reference = payload.get("inputSourceProviderCatalogReference")
    if provider_reference is not None:
        if not isinstance(provider_reference, dict):
            raise ValueError(
                "optimizer job artifact resolver inputSourceProviderCatalogReference must be an object"
            )
        path_value = provider_reference.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ValueError(
                "optimizer job artifact resolver inputSourceProviderCatalogReference.path must be a non-empty string"
            )
    seen_entry_ids: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"optimizer job artifact resolver entries[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        resolver_entry_id = entry.get("resolverEntryId")
        if not isinstance(resolver_entry_id, str) or not resolver_entry_id:
            raise ValueError(f"{label}.resolverEntryId must be a non-empty string")
        if resolver_entry_id in seen_entry_ids:
            raise ValueError(
                f"{label}.resolverEntryId is duplicated: {resolver_entry_id}"
            )
        seen_entry_ids.add(resolver_entry_id)
        artifact_key = entry.get("artifactKey")
        if artifact_key not in MANIFEST_ARTIFACT_KEYS:
            allowed = ", ".join(MANIFEST_ARTIFACT_KEYS)
            raise ValueError(f"{label}.artifactKey must be one of [{allowed}]")
        resolver_lane = entry.get("resolverLane")
        if not isinstance(resolver_lane, str) or not resolver_lane:
            raise ValueError(f"{label}.resolverLane must be a non-empty string")
        resolver_strategy = _require_optional_string(
            entry, field_name="resolverStrategy", label=label
        )
        if (
            resolver_strategy is not None
            and resolver_strategy not in JOB_ARTIFACT_RESOLVER_STRATEGIES
        ):
            allowed = ", ".join(sorted(JOB_ARTIFACT_RESOLVER_STRATEGIES))
            raise ValueError(f"{label}.resolverStrategy must be one of [{allowed}]")
        _require_optional_string(entry, field_name="providerRequestKey", label=label)
        source_provider_id = entry.get("sourceProviderId")
        if source_provider_id is None:
            artifact_key = entry.get("artifactKey")
            if artifact_key not in MANIFEST_ARTIFACT_KEYS:
                allowed = ", ".join(MANIFEST_ARTIFACT_KEYS)
                raise ValueError(f"{label}.artifactKey must be one of [{allowed}]")
            upstream_job_kind = entry.get("upstreamJobKind")
            if not isinstance(upstream_job_kind, str) or not upstream_job_kind:
                raise ValueError(f"{label}.upstreamJobKind must be a non-empty string")
            path_value = entry.get("path")
            if not isinstance(path_value, str) or not path_value:
                raise ValueError(f"{label}.path must be a non-empty string")
            continue
        if not isinstance(source_provider_id, str) or not source_provider_id:
            raise ValueError(f"{label}.sourceProviderId must be a non-empty string")
        if provider_reference is None:
            raise ValueError(
                f"{label} references sourceProviderId but resolver has no inputSourceProviderCatalogReference"
            )


def _resolve_path_from_label(label: str, *, manifest_path: Path) -> Path:
    candidate = Path(label)
    if candidate.is_absolute():
        return candidate
    repo_candidate = REPO_ROOT / candidate
    if repo_candidate.exists():
        return repo_candidate
    return (manifest_path.parent / candidate).resolve()


def _resolve_registry_path_from_reference(
    reference: dict[str, Any], *, manifest_path: Path
) -> Path:
    path_label = reference.get("path")
    if not isinstance(path_label, str) or not path_label:
        raise ValueError(
            "optimizer input manifest inputSourceRegistryReference.path must be a non-empty string"
    )
    return _resolve_path_from_label(path_label, manifest_path=manifest_path)


def _resolve_resolver_path_from_reference(
    reference: dict[str, Any], *, registry_path: Path
) -> Path:
    path_label = reference.get("path")
    if not isinstance(path_label, str) or not path_label:
        raise ValueError(
            "optimizer input source registry inputArtifactResolverReference.path must be a non-empty string"
        )
    return _resolve_path_from_label(path_label, manifest_path=registry_path)


def _resolve_provider_catalog_path_from_reference(
    reference: dict[str, Any], *, resolver_path: Path
) -> Path:
    path_label = reference.get("path")
    if not isinstance(path_label, str) or not path_label:
        raise ValueError(
            "optimizer job artifact resolver inputSourceProviderCatalogReference.path must be a non-empty string"
        )
    return _resolve_path_from_label(path_label, manifest_path=resolver_path)


def _resolve_provider_registry_path_from_reference(
    reference: dict[str, Any], *, catalog_path: Path
) -> Path:
    path_label = reference.get("path")
    if not isinstance(path_label, str) or not path_label:
        raise ValueError(
            "optimizer source provider catalog inputSourceProviderRegistryReference.path must be a non-empty string"
        )
    return _resolve_path_from_label(path_label, manifest_path=catalog_path)


def _resolve_source_artifact_catalog_path_from_reference(
    reference: dict[str, Any], *, registry_path: Path
) -> Path:
    path_label = reference.get("path")
    if not isinstance(path_label, str) or not path_label:
        raise ValueError(
            "optimizer source provider registry inputSourceArtifactCatalogReference.path must be a non-empty string"
        )
    return _resolve_path_from_label(path_label, manifest_path=registry_path)


def load_optimizer_source_artifact_catalog(
    catalog_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = load_json(catalog_path)
    validate_optimizer_source_artifact_catalog_payload(payload)
    resolved_entries: dict[str, dict[str, Any]] = {}
    for entry in payload["entries"]:
        resolved = dict(entry)
        resolved["resolvedPath"] = _resolve_path_from_label(
            str(entry["path"]),
            manifest_path=catalog_path,
        )
        resolved_entries[str(entry["artifactCatalogEntryId"])] = resolved
    return payload, resolved_entries


def load_optimizer_source_provider_registry(
    registry_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = load_json(registry_path)
    validate_optimizer_source_provider_registry_payload(payload)
    artifact_catalog_reference = payload.get("inputSourceArtifactCatalogReference")
    artifact_catalog_payload = None
    resolved_artifact_entries: dict[str, dict[str, Any]] = {}
    if isinstance(artifact_catalog_reference, dict):
        artifact_catalog_path = _resolve_source_artifact_catalog_path_from_reference(
            artifact_catalog_reference, registry_path=registry_path
        )
        (
            artifact_catalog_payload,
            resolved_artifact_entries,
        ) = load_optimizer_source_artifact_catalog(artifact_catalog_path)
        payload["resolvedInputSourceArtifactCatalogPath"] = str(artifact_catalog_path)
        payload["resolvedInputSourceArtifactCatalogSchemaVersion"] = (
            artifact_catalog_payload.get("schemaVersion")
        )
        payload["resolvedInputSourceArtifactCatalogId"] = artifact_catalog_payload.get(
            "catalogId"
        )
    resolved_bindings: dict[str, dict[str, Any]] = {}
    for binding in payload["bindings"]:
        resolved = dict(binding)
        resolution_mode = binding.get("resolutionMode", "direct_path")
        if resolution_mode == "artifact_catalog_entry":
            entry_id = str(binding["artifactCatalogEntryId"])
            artifact_entry = resolved_artifact_entries.get(entry_id)
            if artifact_entry is None:
                raise ValueError(
                    "optimizer source provider registry references unknown "
                    f"artifactCatalogEntryId {entry_id!r}"
                )
            for field_name in (
                "artifactKey",
                "providerLane",
                "providerKind",
                "upstreamJobKind",
            ):
                if binding[field_name] != artifact_entry[field_name]:
                    raise ValueError(
                        "optimizer source provider registry binding "
                        f"{binding['providerBindingId']!r} expects {field_name}="
                        f"{binding[field_name]!r} but artifact catalog entry {entry_id!r} provides "
                        f"{artifact_entry[field_name]!r}"
                    )
            resolved["path"] = artifact_entry["path"]
            resolved["resolvedPath"] = artifact_entry["resolvedPath"]
            for field_name in (
                "artifactCatalogEntryId",
                "artifactLocatorKind",
                "artifactLocatorUri",
                "providerSourceClass",
            ):
                if field_name in artifact_entry:
                    resolved[field_name] = artifact_entry[field_name]
        else:
            resolved["resolvedPath"] = _resolve_path_from_label(
                str(binding["path"]),
                manifest_path=registry_path,
            )
        resolved_bindings[str(binding["providerBindingId"])] = resolved
    return payload, resolved_bindings


def load_optimizer_source_provider_catalog(
    catalog_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = load_json(catalog_path)
    validate_optimizer_source_provider_catalog_payload(payload)
    registry_reference = payload.get("inputSourceProviderRegistryReference")
    registry_payload = None
    resolved_bindings: dict[str, dict[str, Any]] = {}
    if isinstance(registry_reference, dict):
        registry_path = _resolve_provider_registry_path_from_reference(
            registry_reference, catalog_path=catalog_path
        )
        registry_payload, resolved_bindings = load_optimizer_source_provider_registry(
            registry_path
        )
        payload["resolvedInputSourceProviderRegistryPath"] = str(registry_path)
        payload["resolvedInputSourceProviderRegistrySchemaVersion"] = registry_payload.get(
            "schemaVersion"
        )
        payload["resolvedInputSourceProviderRegistryId"] = registry_payload.get(
            "registryId"
        )
        payload["resolvedInputSourceArtifactCatalogPath"] = registry_payload.get(
            "resolvedInputSourceArtifactCatalogPath"
        )
        payload["resolvedInputSourceArtifactCatalogSchemaVersion"] = registry_payload.get(
            "resolvedInputSourceArtifactCatalogSchemaVersion"
        )
        payload["resolvedInputSourceArtifactCatalogId"] = registry_payload.get(
            "resolvedInputSourceArtifactCatalogId"
        )
    resolved_providers: dict[str, dict[str, Any]] = {}
    for provider in payload["providers"]:
        resolved = dict(provider)
        resolution_mode = provider.get("resolutionMode", "direct_path")
        if resolution_mode == "provider_binding_registry":
            binding_id = str(provider["providerBindingId"])
            binding = resolved_bindings.get(binding_id)
            if binding is None:
                raise ValueError(
                    "optimizer source provider catalog references unknown "
                    f"providerBindingId {binding_id!r}"
                )
            for field_name in (
                "artifactKey",
                "providerLane",
                "providerKind",
                "upstreamJobKind",
            ):
                if provider[field_name] != binding[field_name]:
                    raise ValueError(
                        "optimizer source provider catalog provider "
                        f"{provider['sourceProviderId']!r} expects {field_name}="
                        f"{provider[field_name]!r} but binding {binding_id!r} provides "
                        f"{binding[field_name]!r}"
                    )
            resolved["path"] = binding["path"]
            resolved["resolvedPath"] = binding["resolvedPath"]
            for field_name in (
                "providerBindingId",
                "providerBindingKind",
                "providerOwner",
                "bindingLocatorKind",
                "artifactCatalogEntryId",
                "artifactLocatorKind",
                "artifactLocatorUri",
                "providerSourceClass",
            ):
                if field_name in binding:
                    resolved[field_name] = binding[field_name]
        else:
            resolved["resolvedPath"] = _resolve_path_from_label(
                str(provider["path"]),
                manifest_path=catalog_path,
            )
        resolved_providers[str(provider["sourceProviderId"])] = resolved
    return payload, resolved_providers


def load_optimizer_job_artifact_resolver(
    resolver_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = load_json(resolver_path)
    validate_optimizer_job_artifact_resolver_payload(payload)
    provider_reference = payload.get("inputSourceProviderCatalogReference")
    provider_payload = None
    resolved_providers: dict[str, dict[str, Any]] = {}
    if isinstance(provider_reference, dict):
        provider_catalog_path = _resolve_provider_catalog_path_from_reference(
            provider_reference, resolver_path=resolver_path
        )
        provider_payload, resolved_providers = load_optimizer_source_provider_catalog(
            provider_catalog_path
        )
        payload["resolvedInputSourceProviderCatalogPath"] = str(provider_catalog_path)
        payload["resolvedInputSourceProviderCatalogSchemaVersion"] = provider_payload.get(
            "schemaVersion"
        )
        payload["resolvedInputSourceProviderCatalogId"] = provider_payload.get(
            "catalogId"
        )
        payload["resolvedInputSourceProviderRegistryPath"] = provider_payload.get(
            "resolvedInputSourceProviderRegistryPath"
        )
        payload["resolvedInputSourceProviderRegistrySchemaVersion"] = provider_payload.get(
            "resolvedInputSourceProviderRegistrySchemaVersion"
        )
        payload["resolvedInputSourceProviderRegistryId"] = provider_payload.get(
            "resolvedInputSourceProviderRegistryId"
        )
        payload["resolvedInputSourceArtifactCatalogPath"] = provider_payload.get(
            "resolvedInputSourceArtifactCatalogPath"
        )
        payload["resolvedInputSourceArtifactCatalogSchemaVersion"] = provider_payload.get(
            "resolvedInputSourceArtifactCatalogSchemaVersion"
        )
        payload["resolvedInputSourceArtifactCatalogId"] = provider_payload.get(
            "resolvedInputSourceArtifactCatalogId"
        )
    resolved_entries: dict[str, dict[str, Any]] = {}
    for entry in payload["entries"]:
        resolved = dict(entry)
        source_provider_id = resolved.get("sourceProviderId")
        if isinstance(source_provider_id, str) and source_provider_id:
            provider = resolved_providers.get(source_provider_id)
            if provider is None:
                raise ValueError(
                    "optimizer job artifact resolver references unknown "
                    f"sourceProviderId {source_provider_id!r}"
                )
            if provider["providerLane"] != resolved["resolverLane"]:
                raise ValueError(
                    f"resolver entry {resolved['resolverEntryId']!r} expects resolverLane "
                    f"{resolved['resolverLane']!r} but source provider {source_provider_id!r} "
                    f"provides {provider['providerLane']!r}"
                )
            resolved["artifactKey"] = provider["artifactKey"]
            resolved["upstreamJobKind"] = provider["upstreamJobKind"]
            resolved["path"] = provider["path"]
            resolved["providerKind"] = provider["providerKind"]
            resolved["providerLane"] = provider["providerLane"]
            resolved["resolvedPath"] = provider["resolvedPath"]
            for field_name in (
                "sourceProviderId",
                "providerClass",
                "providerHandle",
                "providerEndpoint",
                "locatorKind",
                "providerBindingId",
                "providerBindingKind",
                "providerOwner",
                "bindingLocatorKind",
                "artifactCatalogEntryId",
                "artifactLocatorKind",
                "artifactLocatorUri",
                "providerSourceClass",
            ):
                if field_name in provider:
                    resolved[field_name] = provider[field_name]
        else:
            resolved["resolvedPath"] = _resolve_path_from_label(
                str(entry["path"]), manifest_path=resolver_path
            )
        resolved_entries[str(entry["resolverEntryId"])] = resolved
    return payload, resolved_entries


def load_optimizer_input_source_registry(
    registry_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = load_json(registry_path)
    validate_optimizer_input_source_registry_payload(payload)
    resolver_reference = payload.get("inputArtifactResolverReference")
    resolver_payload = None
    resolved_resolver_entries: dict[str, dict[str, Any]] = {}
    if isinstance(resolver_reference, dict):
        resolver_path = _resolve_resolver_path_from_reference(
            resolver_reference, registry_path=registry_path
        )
        resolver_payload, resolved_resolver_entries = load_optimizer_job_artifact_resolver(
            resolver_path
        )
        payload["resolvedInputArtifactResolverPath"] = str(resolver_path)
        payload["resolvedInputArtifactResolverSchemaVersion"] = resolver_payload.get(
            "schemaVersion"
        )
        payload["resolvedInputArtifactResolverId"] = resolver_payload.get("resolverId")
        payload["resolvedInputSourceProviderCatalogPath"] = resolver_payload.get(
            "resolvedInputSourceProviderCatalogPath"
        )
        payload["resolvedInputSourceProviderCatalogSchemaVersion"] = resolver_payload.get(
            "resolvedInputSourceProviderCatalogSchemaVersion"
        )
        payload["resolvedInputSourceProviderCatalogId"] = resolver_payload.get(
            "resolvedInputSourceProviderCatalogId"
        )
        payload["resolvedInputSourceProviderRegistryPath"] = resolver_payload.get(
            "resolvedInputSourceProviderRegistryPath"
        )
        payload["resolvedInputSourceProviderRegistrySchemaVersion"] = resolver_payload.get(
            "resolvedInputSourceProviderRegistrySchemaVersion"
        )
        payload["resolvedInputSourceProviderRegistryId"] = resolver_payload.get(
            "resolvedInputSourceProviderRegistryId"
        )
        payload["resolvedInputSourceArtifactCatalogPath"] = resolver_payload.get(
            "resolvedInputSourceArtifactCatalogPath"
        )
        payload["resolvedInputSourceArtifactCatalogSchemaVersion"] = resolver_payload.get(
            "resolvedInputSourceArtifactCatalogSchemaVersion"
        )
        payload["resolvedInputSourceArtifactCatalogId"] = resolver_payload.get(
            "resolvedInputSourceArtifactCatalogId"
        )
    resolved_sources: dict[str, dict[str, Any]] = {}
    for source in payload["sources"]:
        resolved = dict(source)
        resolution_mode = resolved.get("resolutionMode", "direct_path")
        if resolution_mode == "direct_path":
            resolved["resolvedPath"] = _resolve_path_from_label(
                str(source["path"]), manifest_path=registry_path
            )
        else:
            resolver_entry_id = str(source["resolverEntryId"])
            resolver_entry = resolved_resolver_entries.get(resolver_entry_id)
            if resolver_entry is None:
                raise ValueError(
                    "optimizer input source registry binding "
                    f"{source['bindingId']!r} references unknown resolverEntryId {resolver_entry_id!r}"
                )
            if resolver_entry["artifactKey"] != source["artifactKey"]:
                raise ValueError(
                    "optimizer input source registry binding "
                    f"{source['bindingId']!r} expects artifactKey {source['artifactKey']!r} "
                    f"but resolver entry {resolver_entry_id!r} provides {resolver_entry['artifactKey']!r}"
                )
            if resolver_entry["resolverLane"] != source["sourceLane"]:
                raise ValueError(
                    "optimizer input source registry binding "
                    f"{source['bindingId']!r} expects sourceLane {source['sourceLane']!r} "
                    f"but resolver entry {resolver_entry_id!r} provides {resolver_entry['resolverLane']!r}"
                )
            resolved["resolvedPath"] = resolver_entry["resolvedPath"]
            for field_name in RESOLVED_SOURCE_METADATA_FIELDS:
                value = resolver_entry.get(field_name)
                if isinstance(value, str) and value:
                    resolved[field_name] = value
            resolved["resolvedFromResolverEntry"] = {
                "resolverEntryId": resolver_entry["resolverEntryId"],
                "resolverLane": resolver_entry["resolverLane"],
                "upstreamJobKind": resolver_entry["upstreamJobKind"],
                **{
                    field_name: resolver_entry[field_name]
                    for field_name in RESOLVED_SOURCE_METADATA_FIELDS
                    if field_name
                    not in {"resolverEntryId", "resolverLane", "upstreamJobKind"}
                    and isinstance(resolver_entry.get(field_name), str)
                    and resolver_entry.get(field_name)
                },
            }
        resolved_sources[str(source["bindingId"])] = resolved
    return payload, resolved_sources


def load_optimizer_input_manifest(
    manifest_path: Path,
) -> tuple[dict[str, Any], dict[str, Path]]:
    payload = load_json(manifest_path)
    validate_optimizer_input_manifest_payload(payload)
    artifact_paths = payload.get("artifactPaths")
    if isinstance(artifact_paths, dict):
        resolved = {
            key: _resolve_path_from_label(artifact_paths[key], manifest_path=manifest_path)
            for key in MANIFEST_ARTIFACT_KEYS
        }
        return payload, resolved
    registry_reference = payload["inputSourceRegistryReference"]
    registry_path = _resolve_registry_path_from_reference(
        registry_reference, manifest_path=manifest_path
    )
    registry_payload, resolved_sources = load_optimizer_input_source_registry(
        registry_path
    )
    artifact_bindings = payload["artifactBindings"]
    resolved = {}
    selected_sources: list[dict[str, Any]] = []
    for key in MANIFEST_ARTIFACT_KEYS:
        binding_id = artifact_bindings[key]
        source = resolved_sources.get(binding_id)
        if source is None:
            raise ValueError(
                f"optimizer input manifest artifactBindings.{key} references unknown bindingId {binding_id!r}"
            )
        if source["artifactKey"] != key:
            raise ValueError(
                "optimizer input manifest artifact binding "
                f"{binding_id!r} has artifactKey {source['artifactKey']!r}, expected {key!r}"
            )
        selected_sources.append(source)
        resolved[key] = source["resolvedPath"]
    payload["resolvedInputSourceRegistryPath"] = str(registry_path)
    payload["resolvedInputSourceRegistrySchemaVersion"] = registry_payload.get(
        "schemaVersion"
    )
    payload["resolvedInputSourceRegistryId"] = registry_payload.get("registryId")
    if any(
        source.get("resolutionMode") == "job_artifact_resolver"
        for source in selected_sources
    ):
        payload["resolvedInputArtifactResolverPath"] = registry_payload.get(
            "resolvedInputArtifactResolverPath"
        )
        payload["resolvedInputArtifactResolverSchemaVersion"] = registry_payload.get(
            "resolvedInputArtifactResolverSchemaVersion"
        )
        payload["resolvedInputArtifactResolverId"] = registry_payload.get(
            "resolvedInputArtifactResolverId"
        )
        payload["resolvedInputSourceProviderCatalogPath"] = registry_payload.get(
            "resolvedInputSourceProviderCatalogPath"
        )
        payload[
            "resolvedInputSourceProviderCatalogSchemaVersion"
        ] = registry_payload.get("resolvedInputSourceProviderCatalogSchemaVersion")
        payload["resolvedInputSourceProviderCatalogId"] = registry_payload.get(
            "resolvedInputSourceProviderCatalogId"
        )
        payload["resolvedInputSourceProviderRegistryPath"] = registry_payload.get(
            "resolvedInputSourceProviderRegistryPath"
        )
        payload[
            "resolvedInputSourceProviderRegistrySchemaVersion"
        ] = registry_payload.get("resolvedInputSourceProviderRegistrySchemaVersion")
        payload["resolvedInputSourceProviderRegistryId"] = registry_payload.get(
            "resolvedInputSourceProviderRegistryId"
        )
        payload["resolvedInputSourceArtifactCatalogPath"] = registry_payload.get(
            "resolvedInputSourceArtifactCatalogPath"
        )
        payload["resolvedInputSourceArtifactCatalogSchemaVersion"] = registry_payload.get(
            "resolvedInputSourceArtifactCatalogSchemaVersion"
        )
        payload["resolvedInputSourceArtifactCatalogId"] = registry_payload.get(
            "resolvedInputSourceArtifactCatalogId"
        )
    return payload, resolved


def materialize_optimizer_input_bundle_from_manifest(
    *,
    manifest_path: Path,
    bundle_schema_version: str,
    bundle_id: str | None = None,
    generated_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_payload, artifact_paths = load_optimizer_input_manifest(manifest_path)
    derived_bundle_id = bundle_id
    if derived_bundle_id is None:
        manifest_id = manifest_payload.get("manifestId")
        if isinstance(manifest_id, str) and manifest_id:
            derived_bundle_id = manifest_id.replace("manifest", "bundle")
        else:
            derived_bundle_id = "optimizer-input-bundle.from-manifest"
    bundle_payload = build_optimizer_input_bundle_payload(
        ranking_payload=load_json(artifact_paths["ranking"]),
        context_payload=load_json(artifact_paths["context"]),
        backfills_payload=load_json(artifact_paths["backfills"]),
        performance_payload=load_json(artifact_paths["performance"]),
        challenger_input_payload=load_json(artifact_paths["challengerInput"]),
        schema_version=bundle_schema_version,
        bundle_id=derived_bundle_id,
        generated_at=generated_at
        or str(manifest_payload.get("generatedAt") or ""),
    )
    bundle_payload["generatedFrom"]["optimizerInputManifestSchemaVersion"] = manifest_payload.get(
        "schemaVersion"
    )
    bundle_payload["generatedFrom"]["optimizerInputManifestId"] = manifest_payload.get(
        "manifestId"
    )
    bundle_payload["generatedFrom"]["optimizerInputManifestGeneratedAt"] = manifest_payload.get(
        "generatedAt"
    )
    bundle_payload["generatedFrom"]["optimizerInputManifestGeneratedFrom"] = manifest_payload.get(
        "generatedFrom", {}
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceRegistrySchemaVersion"] = manifest_payload.get(
        "resolvedInputSourceRegistrySchemaVersion"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceRegistryId"] = manifest_payload.get(
        "resolvedInputSourceRegistryId"
    )
    bundle_payload["generatedFrom"]["optimizerInputArtifactResolverSchemaVersion"] = manifest_payload.get(
        "resolvedInputArtifactResolverSchemaVersion"
    )
    bundle_payload["generatedFrom"]["optimizerInputArtifactResolverId"] = manifest_payload.get(
        "resolvedInputArtifactResolverId"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceProviderCatalogSchemaVersion"] = manifest_payload.get(
        "resolvedInputSourceProviderCatalogSchemaVersion"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceProviderCatalogId"] = manifest_payload.get(
        "resolvedInputSourceProviderCatalogId"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceProviderRegistrySchemaVersion"] = manifest_payload.get(
        "resolvedInputSourceProviderRegistrySchemaVersion"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceProviderRegistryId"] = manifest_payload.get(
        "resolvedInputSourceProviderRegistryId"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceArtifactCatalogSchemaVersion"] = manifest_payload.get(
        "resolvedInputSourceArtifactCatalogSchemaVersion"
    )
    bundle_payload["generatedFrom"]["optimizerInputSourceArtifactCatalogId"] = manifest_payload.get(
        "resolvedInputSourceArtifactCatalogId"
    )
    manifest_generated_from = manifest_payload.get("generatedFrom", {})
    for field_name in (
        "sourceLane",
        "inputRolloutPolicySchemaVersion",
        "inputRolloutPolicyId",
        "inputRolloutClass",
        "inputLaneSelectionSource",
        "inputRolloutStrategy",
        "optimizerInputSourceProviderLane",
        "optimizerInputSourceProviderKind",
        "optimizerInputSourceProviderClass",
        "optimizerInputSourceProviderHandle",
        "optimizerInputSourceProviderLocatorKind",
        "optimizerInputSourceProviderOwner",
        "optimizerInputArtifactLocatorKind",
        "resolvedSources",
    ):
        if field_name in manifest_generated_from:
            bundle_payload["generatedFrom"][field_name] = manifest_generated_from[
                field_name
            ]
    return bundle_payload, manifest_payload
