#!/usr/bin/env python3
"""
Shared validator for the ranking-output subset consumed by the optimizer layer.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


RANKING_OPTIMIZER_CONTRACT_ID = "ranking_optimizer_handoff"
RANKING_OPTIMIZER_CONTRACT_VERSION = "ranking-optimizer-contract.v1"
RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION = "ranking-optimizer-contract.vNext-preview"
RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE = "exact"
RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE = "compat"
RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL = "legacy_top_level"
RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL_COMPAT = "legacy_top_level_compat"
RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF = "optimizer_handoff"
SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS = (
    RANKING_OPTIMIZER_CONTRACT_VERSION,
    RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
)
SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES = (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
)
SUPPORTED_RANKING_OPTIMIZER_SURFACE_SOURCES = (
    RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
    RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL_COMPAT,
    RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
)
RANKING_OUTPUT_SCHEMA_VERSION = "ranking-output.v1"
OPTIMIZER_HANDOFF_KEY = "optimizerHandoff"
OPTIMIZER_HANDOFF_SCHEMA_VERSION = "ranking-optimizer-handoff.v2-preview"
OPTIMIZER_HANDOFF_DEPRECATION_POLICY_KEY = "deprecationPolicy"
OPTIMIZER_HANDOFF_DEPRECATION_POLICY_SCHEMA_VERSION = (
    "ranking-optimizer-deprecation-policy.v1"
)
OPTIMIZER_HANDOFF_DEPRECATION_PHASE = "dual_write_preview"
OPTIMIZER_HANDOFF_CANONICAL_SURFACE = OPTIMIZER_HANDOFF_KEY
OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION = "ranking-optimizer-contract.v2"
OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS = (
    "profileId",
    "profileSelection",
    "candidateSource",
    "scores",
    "predictionRun",
    "rankingSummary",
    "rerankDiagnostics",
)

FEATURE_KEYS = (
    "demand",
    "competition",
    "fit",
    "rewrite",
    "series",
    "searchCapture",
    "longform",
    "feasibility",
)

PRIORITY_LEVELS = {"P0", "P1", "P2"}


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{label} must be an object")
    return {}


def require_list(value: Any, label: str, errors: list[str]) -> list[Any]:
    if isinstance(value, list):
        return value
    errors.append(f"{label} must be a list")
    return []


def _apply_alias(
    target: dict[str, Any],
    key: str,
    value: Any,
    alias_name: str,
    aliases: list[str],
) -> None:
    if key not in target and value is not None:
        target[key] = value
        aliases.append(alias_name)


def build_optimizer_handoff_deprecation_policy() -> dict[str, Any]:
    return {
        "schemaVersion": OPTIMIZER_HANDOFF_DEPRECATION_POLICY_SCHEMA_VERSION,
        "phase": OPTIMIZER_HANDOFF_DEPRECATION_PHASE,
        "canonicalSurface": OPTIMIZER_HANDOFF_CANONICAL_SURFACE,
        "deprecatedTopLevelFields": list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
        "exactPreviewRequiresTopLevelMirror": True,
        "compatPreviewUsesLegacyFallback": True,
        "nextHardFailContractVersion": OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION,
    }


def build_ranking_optimizer_contract_metadata(
    *,
    validated: bool = True,
    contract_version: str = RANKING_OPTIMIZER_CONTRACT_VERSION,
    validation_mode: str = RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    compat_aliases_applied: list[str] | None = None,
    surface_source: str = RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
    deprecation_phase: str | None = None,
    canonical_surface: str | None = None,
    deprecated_top_level_fields: list[str] | None = None,
    next_hard_fail_contract_version: str | None = None,
) -> dict[str, Any]:
    if contract_version not in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS:
        raise ValueError(
            f"unsupported ranking optimizer contract version `{contract_version}`"
        )
    if validation_mode not in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES:
        raise ValueError(
            f"unsupported ranking optimizer contract validation mode `{validation_mode}`"
        )
    if surface_source not in SUPPORTED_RANKING_OPTIMIZER_SURFACE_SOURCES:
        raise ValueError(
            f"unsupported ranking optimizer surface source `{surface_source}`"
        )
    aliases = list(compat_aliases_applied or [])
    return {
        "rankingOptimizerContractId": RANKING_OPTIMIZER_CONTRACT_ID,
        "rankingOptimizerContractVersion": contract_version,
        "rankingOptimizerContractValidationMode": validation_mode,
        "rankingOptimizerContractValidated": validated,
        "rankingOptimizerSurfaceSource": surface_source,
        "rankingOptimizerCompatApplied": bool(aliases),
        "rankingOptimizerCompatAliasesApplied": aliases,
        "rankingOptimizerDeprecationPhase": deprecation_phase,
        "rankingOptimizerCanonicalSurface": canonical_surface,
        "rankingOptimizerDeprecatedTopLevelFields": list(
            deprecated_top_level_fields or []
        ),
        "rankingOptimizerNextHardFailContractVersion": next_hard_fail_contract_version,
    }


def validate_ranking_optimizer_contract_metadata(
    metadata: dict[str, Any],
    *,
    label: str,
    expected_contract_id: str | None = RANKING_OPTIMIZER_CONTRACT_ID,
    expected_contract_version: str | None = RANKING_OPTIMIZER_CONTRACT_VERSION,
    expected_validation_mode: str | None = RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    expected_validated: bool | None = True,
    expected_surface_source: str | None = None,
) -> list[str]:
    errors: list[str] = []
    contract_id = metadata.get("rankingOptimizerContractId")
    contract_version = metadata.get("rankingOptimizerContractVersion")
    validation_mode = metadata.get("rankingOptimizerContractValidationMode")
    validated = metadata.get("rankingOptimizerContractValidated")
    surface_source = metadata.get("rankingOptimizerSurfaceSource")
    compat_applied = metadata.get("rankingOptimizerCompatApplied")
    compat_aliases = metadata.get("rankingOptimizerCompatAliasesApplied")
    deprecation_phase = metadata.get("rankingOptimizerDeprecationPhase")
    canonical_surface = metadata.get("rankingOptimizerCanonicalSurface")
    deprecated_top_level_fields = metadata.get("rankingOptimizerDeprecatedTopLevelFields")
    next_hard_fail_contract_version = metadata.get(
        "rankingOptimizerNextHardFailContractVersion"
    )

    expect(
        isinstance(contract_id, str) and bool(contract_id),
        f"{label} rankingOptimizerContractId must be a non-empty string",
        errors,
    )
    if isinstance(contract_version, str):
        expect(
            contract_version in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS,
            f"{label} rankingOptimizerContractVersion is not in the supported version set",
            errors,
        )
    else:
        errors.append(
            f"{label} rankingOptimizerContractVersion must be a non-empty string"
        )

    if isinstance(validation_mode, str):
        expect(
            validation_mode in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES,
            f"{label} rankingOptimizerContractValidationMode is not supported",
            errors,
        )
    else:
        errors.append(
            f"{label} rankingOptimizerContractValidationMode must be a non-empty string"
        )

    expect(
        isinstance(validated, bool),
        f"{label} rankingOptimizerContractValidated must be a boolean",
        errors,
    )
    if isinstance(surface_source, str):
        expect(
            surface_source in SUPPORTED_RANKING_OPTIMIZER_SURFACE_SOURCES,
            f"{label} rankingOptimizerSurfaceSource is not supported",
            errors,
        )
    else:
        errors.append(
            f"{label} rankingOptimizerSurfaceSource must be a non-empty string"
        )
    expect(
        isinstance(compat_applied, bool),
        f"{label} rankingOptimizerCompatApplied must be a boolean",
        errors,
    )
    expect(
        isinstance(compat_aliases, list),
        f"{label} rankingOptimizerCompatAliasesApplied must be a list",
        errors,
    )
    if deprecation_phase is not None:
        expect(
            isinstance(deprecation_phase, str) and bool(deprecation_phase),
            f"{label} rankingOptimizerDeprecationPhase must be a non-empty string when present",
            errors,
        )
    if canonical_surface is not None:
        expect(
            isinstance(canonical_surface, str) and bool(canonical_surface),
            f"{label} rankingOptimizerCanonicalSurface must be a non-empty string when present",
            errors,
        )
    expect(
        isinstance(deprecated_top_level_fields, list),
        f"{label} rankingOptimizerDeprecatedTopLevelFields must be a list",
        errors,
    )
    if next_hard_fail_contract_version is not None:
        expect(
            isinstance(next_hard_fail_contract_version, str)
            and bool(next_hard_fail_contract_version),
            f"{label} rankingOptimizerNextHardFailContractVersion must be a non-empty string when present",
            errors,
        )
    if isinstance(compat_applied, bool) and isinstance(compat_aliases, list):
        expect(
            compat_applied == bool(compat_aliases),
            f"{label} rankingOptimizerCompatApplied must reflect whether compat aliases were applied",
            errors,
        )

    if expected_contract_id is not None:
        expect(
            contract_id == expected_contract_id,
            f"{label} rankingOptimizerContractId does not match expected contract id",
            errors,
        )
    if expected_contract_version is not None:
        expect(
            contract_version == expected_contract_version,
            f"{label} rankingOptimizerContractVersion does not match expected contract version",
            errors,
        )
    if expected_validation_mode is not None:
        expect(
            validation_mode == expected_validation_mode,
            f"{label} rankingOptimizerContractValidationMode does not match expected validation mode",
            errors,
        )
    if expected_validated is not None:
        expect(
            validated is expected_validated,
            f"{label} rankingOptimizerContractValidated does not match expected validation state",
            errors,
        )
    if expected_surface_source is not None:
        expect(
            surface_source == expected_surface_source,
            f"{label} rankingOptimizerSurfaceSource does not match expected surface source",
            errors,
        )

    return errors


def select_optimizer_handoff_payload(
    payload: dict[str, Any],
    *,
    contract_version: str = RANKING_OPTIMIZER_CONTRACT_VERSION,
) -> dict[str, Any]:
    if contract_version == RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION:
        optimizer_handoff = payload.get(OPTIMIZER_HANDOFF_KEY)
        if isinstance(optimizer_handoff, dict):
            return optimizer_handoff
    return payload


def _normalize_legacy_top_level_surface(
    payload: dict[str, Any],
    aliases: list[str],
) -> None:
    prediction_run = payload.get("predictionRun", {})
    if not isinstance(prediction_run, dict):
        prediction_run = {}

    _apply_alias(
        payload,
        "schemaVersion",
        RANKING_OUTPUT_SCHEMA_VERSION,
        "schemaVersion<-implicit_ranking_output_v1",
        aliases,
    )

    top_profile_id = payload.get("profileId")
    profile_selection = payload.get("profileSelection")
    if not isinstance(profile_selection, dict):
        profile_selection = {}
        payload["profileSelection"] = profile_selection
    _apply_alias(
        profile_selection,
        "resolvedProfileId",
        top_profile_id or prediction_run.get("profileId"),
        "profileSelection.resolvedProfileId<-profileId",
        aliases,
    )
    _apply_alias(
        profile_selection,
        "requestedProfileId",
        profile_selection.get("resolvedProfileId"),
        "profileSelection.requestedProfileId<-profileSelection.resolvedProfileId",
        aliases,
    )
    _apply_alias(
        profile_selection,
        "selectionSource",
        prediction_run.get("profileSelectionSource"),
        "profileSelection.selectionSource<-predictionRun.profileSelectionSource",
        aliases,
    )

    candidate_source = payload.get("candidateSource")
    if not isinstance(candidate_source, dict):
        candidate_source = {}
        payload["candidateSource"] = candidate_source
    _apply_alias(
        candidate_source,
        "topicCandidateSchemaVersion",
        prediction_run.get("topicCandidateSchemaVersion"),
        "candidateSource.topicCandidateSchemaVersion<-predictionRun.topicCandidateSchemaVersion",
        aliases,
    )
    _apply_alias(
        candidate_source,
        "inputSchemaVersion",
        prediction_run.get("candidateInputSchemaVersion"),
        "candidateSource.inputSchemaVersion<-predictionRun.candidateInputSchemaVersion",
        aliases,
    )
    _apply_alias(
        candidate_source,
        "sourceKind",
        prediction_run.get("candidateSourceKind"),
        "candidateSource.sourceKind<-predictionRun.candidateSourceKind",
        aliases,
    )
    _apply_alias(
        candidate_source,
        "sourceSnapshotId",
        prediction_run.get("candidateSourceSnapshotId"),
        "candidateSource.sourceSnapshotId<-predictionRun.candidateSourceSnapshotId",
        aliases,
    )
    _apply_alias(
        candidate_source,
        "sourcePolicyVersion",
        prediction_run.get("candidateSourcePolicyVersion"),
        "candidateSource.sourcePolicyVersion<-predictionRun.candidateSourcePolicyVersion",
        aliases,
    )
    _apply_alias(
        candidate_source,
        "rankingSnapshotId",
        prediction_run.get("snapshotId"),
        "candidateSource.rankingSnapshotId<-predictionRun.snapshotId",
        aliases,
    )


def _normalize_optimizer_handoff_surface(
    payload: dict[str, Any],
    aliases: list[str],
) -> None:
    optimizer_handoff = payload.get(OPTIMIZER_HANDOFF_KEY)
    if not isinstance(optimizer_handoff, dict):
        optimizer_handoff = {}
        payload[OPTIMIZER_HANDOFF_KEY] = optimizer_handoff
        aliases.append("optimizerHandoff<-legacy_top_level")

    _apply_alias(
        optimizer_handoff,
        "schemaVersion",
        OPTIMIZER_HANDOFF_SCHEMA_VERSION,
        "optimizerHandoff.schemaVersion<-default_preview_schema",
        aliases,
    )
    _apply_alias(
        optimizer_handoff,
        "deprecatedTopLevelFields",
        list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
        "optimizerHandoff.deprecatedTopLevelFields<-default_legacy_field_set",
        aliases,
    )
    _apply_alias(
        optimizer_handoff,
        OPTIMIZER_HANDOFF_DEPRECATION_POLICY_KEY,
        build_optimizer_handoff_deprecation_policy(),
        "optimizerHandoff.deprecationPolicy<-default_preview_policy",
        aliases,
    )
    for field in OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS:
        _apply_alias(
            optimizer_handoff,
            field,
            deepcopy(payload.get(field)),
            f"optimizerHandoff.{field}<-{field}",
            aliases,
        )


def resolve_ranking_optimizer_surface_source(
    payload: dict[str, Any],
    *,
    contract_version: str,
    compat_aliases_applied: list[str],
) -> str:
    if contract_version != RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION:
        return RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL
    if any(
        alias == "optimizerHandoff<-legacy_top_level"
        or alias.startswith("optimizerHandoff.")
        for alias in compat_aliases_applied
    ):
        return RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL_COMPAT
    optimizer_handoff = payload.get(OPTIMIZER_HANDOFF_KEY)
    if isinstance(optimizer_handoff, dict):
        return RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF
    return RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL


def extract_optimizer_handoff_deprecation_metadata(
    payload: dict[str, Any],
) -> dict[str, Any]:
    optimizer_handoff = payload.get(OPTIMIZER_HANDOFF_KEY)
    if not isinstance(optimizer_handoff, dict):
        return {
            "deprecation_phase": None,
            "canonical_surface": None,
            "deprecated_top_level_fields": [],
            "next_hard_fail_contract_version": None,
        }

    deprecation_policy = optimizer_handoff.get(OPTIMIZER_HANDOFF_DEPRECATION_POLICY_KEY)
    if not isinstance(deprecation_policy, dict):
        return {
            "deprecation_phase": None,
            "canonical_surface": None,
            "deprecated_top_level_fields": list(
                optimizer_handoff.get("deprecatedTopLevelFields", [])
                if isinstance(optimizer_handoff.get("deprecatedTopLevelFields"), list)
                else []
            ),
            "next_hard_fail_contract_version": None,
        }

    deprecated_fields = deprecation_policy.get("deprecatedTopLevelFields")
    return {
        "deprecation_phase": deprecation_policy.get("phase"),
        "canonical_surface": deprecation_policy.get("canonicalSurface"),
        "deprecated_top_level_fields": list(deprecated_fields)
        if isinstance(deprecated_fields, list)
        else [],
        "next_hard_fail_contract_version": deprecation_policy.get(
            "nextHardFailContractVersion"
        ),
    }


def normalize_ranking_payload_for_optimizer(
    payload: dict[str, Any],
    *,
    contract_version: str = RANKING_OPTIMIZER_CONTRACT_VERSION,
    validation_mode: str = RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
) -> tuple[dict[str, Any], list[str]]:
    if contract_version not in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS:
        raise ValueError(
            f"unsupported ranking optimizer contract version `{contract_version}`"
        )
    if validation_mode not in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES:
        raise ValueError(
            f"unsupported ranking optimizer contract validation mode `{validation_mode}`"
        )

    normalized = deepcopy(payload)
    aliases: list[str] = []
    if validation_mode == RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE:
        _normalize_legacy_top_level_surface(normalized, aliases)
        if contract_version == RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION:
            _normalize_optimizer_handoff_surface(normalized, aliases)

    return normalized, aliases


def prepare_ranking_payload_for_optimizer(
    payload: dict[str, Any],
    label: str = "ranking",
    *,
    contract_version: str = RANKING_OPTIMIZER_CONTRACT_VERSION,
    validation_mode: str = RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
) -> tuple[dict[str, Any], dict[str, Any]]:
    normalized_payload, aliases = normalize_ranking_payload_for_optimizer(
        payload,
        contract_version=contract_version,
        validation_mode=validation_mode,
    )
    errors = validate_ranking_payload_for_optimizer(
        normalized_payload,
        label=label,
        contract_version=contract_version,
        validation_mode=validation_mode,
    )
    if errors:
        raise ValueError(
            "ranking output does not satisfy the optimizer-facing contract: "
            + "; ".join(errors)
        )
    surface_source = resolve_ranking_optimizer_surface_source(
        normalized_payload,
        contract_version=contract_version,
        compat_aliases_applied=aliases,
    )
    deprecation_metadata = extract_optimizer_handoff_deprecation_metadata(
        normalized_payload
    )
    return normalized_payload, build_ranking_optimizer_contract_metadata(
        validated=True,
        contract_version=contract_version,
        validation_mode=validation_mode,
        compat_aliases_applied=aliases,
        surface_source=surface_source,
        **deprecation_metadata,
    )


def validate_score_breakdown(
    score_breakdown: dict[str, Any], prefix: str, errors: list[str]
) -> None:
    for key in FEATURE_KEYS:
        value = score_breakdown.get(key)
        expect(
            isinstance(value, (int, float)),
            f"{prefix}.scoreBreakdown.{key} must be numeric",
            errors,
        )


def validate_feature_vector(
    feature_vector: dict[str, Any], prefix: str, errors: list[str]
) -> None:
    expect(
        feature_vector.get("schemaVersion") == "feature-vector.v1",
        f"{prefix}.featureVector has unexpected schemaVersion",
        errors,
    )
    for key in FEATURE_KEYS:
        feature_score = feature_vector.get(key)
        if not isinstance(feature_score, dict):
            errors.append(f"{prefix}.featureVector.{key} must be an object")
            continue
        expect(
            isinstance(feature_score.get("score"), (int, float)),
            f"{prefix}.featureVector.{key}.score must be numeric",
            errors,
        )
        expect(
            isinstance(feature_score.get("confidence"), (int, float)),
            f"{prefix}.featureVector.{key}.confidence must be numeric",
            errors,
        )
        expect(
            isinstance(feature_score.get("reason"), str) and bool(feature_score.get("reason")),
            f"{prefix}.featureVector.{key}.reason must be a non-empty string",
            errors,
        )
        expect(
            isinstance(feature_score.get("evidenceRefs"), list),
            f"{prefix}.featureVector.{key}.evidenceRefs must be a list",
            errors,
        )


def validate_optimizer_handoff_deprecation_policy(
    deprecation_policy: dict[str, Any],
    *,
    deprecated_top_level_fields: list[Any],
    label: str,
    errors: list[str],
) -> None:
    expect(
        deprecation_policy.get("schemaVersion")
        == OPTIMIZER_HANDOFF_DEPRECATION_POLICY_SCHEMA_VERSION,
        f"{label}.schemaVersion must be {OPTIMIZER_HANDOFF_DEPRECATION_POLICY_SCHEMA_VERSION}",
        errors,
    )
    expect(
        deprecation_policy.get("phase") == OPTIMIZER_HANDOFF_DEPRECATION_PHASE,
        f"{label}.phase must be {OPTIMIZER_HANDOFF_DEPRECATION_PHASE}",
        errors,
    )
    expect(
        deprecation_policy.get("canonicalSurface") == OPTIMIZER_HANDOFF_CANONICAL_SURFACE,
        f"{label}.canonicalSurface must be {OPTIMIZER_HANDOFF_CANONICAL_SURFACE}",
        errors,
    )
    expect(
        deprecation_policy.get("deprecatedTopLevelFields")
        == list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
        f"{label}.deprecatedTopLevelFields must match the canonical dual-write field list",
        errors,
    )
    expect(
        deprecation_policy.get("deprecatedTopLevelFields") == deprecated_top_level_fields,
        f"{label}.deprecatedTopLevelFields must match optimizerHandoff.deprecatedTopLevelFields",
        errors,
    )
    expect(
        deprecation_policy.get("exactPreviewRequiresTopLevelMirror") is True,
        f"{label}.exactPreviewRequiresTopLevelMirror must be true",
        errors,
    )
    expect(
        deprecation_policy.get("compatPreviewUsesLegacyFallback") is True,
        f"{label}.compatPreviewUsesLegacyFallback must be true",
        errors,
    )
    expect(
        deprecation_policy.get("nextHardFailContractVersion")
        == OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION,
        f"{label}.nextHardFailContractVersion must be {OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION}",
        errors,
    )


def validate_ranking_payload_for_optimizer(
    payload: dict[str, Any],
    label: str = "ranking",
    *,
    contract_version: str = RANKING_OPTIMIZER_CONTRACT_VERSION,
    validation_mode: str = RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
) -> list[str]:
    if contract_version not in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS:
        raise ValueError(
            f"unsupported ranking optimizer contract version `{contract_version}`"
        )
    if validation_mode not in SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES:
        raise ValueError(
            f"unsupported ranking optimizer contract validation mode `{validation_mode}`"
        )

    errors: list[str] = []
    surface_payload = payload
    surface_label = label
    if contract_version == RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION:
        expect(
            payload.get("schemaVersion") == RANKING_OUTPUT_SCHEMA_VERSION,
            f"{label}.schemaVersion must be {RANKING_OUTPUT_SCHEMA_VERSION} for vNext preview contracts",
            errors,
        )
        optimizer_handoff = require_object(
            payload.get(OPTIMIZER_HANDOFF_KEY),
            f"{label}.{OPTIMIZER_HANDOFF_KEY}",
            errors,
        )
        surface_payload = optimizer_handoff
        surface_label = f"{label}.{OPTIMIZER_HANDOFF_KEY}"
        expect(
            optimizer_handoff.get("schemaVersion") == OPTIMIZER_HANDOFF_SCHEMA_VERSION,
            f"{label}.{OPTIMIZER_HANDOFF_KEY}.schemaVersion must be {OPTIMIZER_HANDOFF_SCHEMA_VERSION}",
            errors,
        )
        deprecated_fields = require_list(
            optimizer_handoff.get("deprecatedTopLevelFields"),
            f"{label}.{OPTIMIZER_HANDOFF_KEY}.deprecatedTopLevelFields",
            errors,
        )
        expect(
            deprecated_fields == list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
            f"{label}.{OPTIMIZER_HANDOFF_KEY}.deprecatedTopLevelFields must match the canonical dual-write field list",
            errors,
        )
        deprecation_policy = require_object(
            optimizer_handoff.get(OPTIMIZER_HANDOFF_DEPRECATION_POLICY_KEY),
            f"{label}.{OPTIMIZER_HANDOFF_KEY}.{OPTIMIZER_HANDOFF_DEPRECATION_POLICY_KEY}",
            errors,
        )
        validate_optimizer_handoff_deprecation_policy(
            deprecation_policy,
            deprecated_top_level_fields=deprecated_fields,
            label=f"{label}.{OPTIMIZER_HANDOFF_KEY}.{OPTIMIZER_HANDOFF_DEPRECATION_POLICY_KEY}",
            errors=errors,
        )
        for field in OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS:
            expect(
                payload.get(field) == optimizer_handoff.get(field),
                f"{label}.{OPTIMIZER_HANDOFF_KEY}.{field} must mirror top-level {field} during dual-write preview",
                errors,
            )

    top_profile_id = surface_payload.get("profileId")
    expect(
        isinstance(top_profile_id, str) and bool(top_profile_id),
        f"{surface_label}.profileId must be a non-empty string",
        errors,
    )

    profile_selection = require_object(
        surface_payload.get("profileSelection"), f"{surface_label}.profileSelection", errors
    )
    candidate_source = require_object(
        surface_payload.get("candidateSource"), f"{surface_label}.candidateSource", errors
    )
    prediction_run = require_object(
        surface_payload.get("predictionRun"), f"{surface_label}.predictionRun", errors
    )
    ranking_summary = require_object(
        surface_payload.get("rankingSummary"), f"{surface_label}.rankingSummary", errors
    )
    scores = require_list(surface_payload.get("scores"), f"{surface_label}.scores", errors)
    rerank_diagnostics = require_list(
        surface_payload.get("rerankDiagnostics"), f"{surface_label}.rerankDiagnostics", errors
    )

    expect(
        prediction_run.get("schemaVersion") == "prediction-run.v1",
        f"{surface_label}.predictionRun has unexpected schemaVersion",
        errors,
    )
    expect(
        profile_selection.get("resolvedProfileId") == top_profile_id,
        f"{surface_label}.profileSelection.resolvedProfileId must match {surface_label}.profileId",
        errors,
    )
    expect(
        prediction_run.get("profileId") == top_profile_id,
        f"{surface_label}.predictionRun.profileId must match {surface_label}.profileId",
        errors,
    )
    expect(
        profile_selection.get("selectionSource") == prediction_run.get("profileSelectionSource"),
        f"{surface_label}.profileSelection.selectionSource must match predictionRun.profileSelectionSource",
        errors,
    )
    expect(
        candidate_source.get("topicCandidateSchemaVersion")
        == prediction_run.get("topicCandidateSchemaVersion"),
        f"{surface_label}.candidateSource.topicCandidateSchemaVersion must match predictionRun",
        errors,
    )
    expect(
        candidate_source.get("inputSchemaVersion")
        == prediction_run.get("candidateInputSchemaVersion"),
        f"{surface_label}.candidateSource.inputSchemaVersion must match predictionRun",
        errors,
    )
    expect(
        candidate_source.get("sourceKind") == prediction_run.get("candidateSourceKind"),
        f"{surface_label}.candidateSource.sourceKind must match predictionRun",
        errors,
    )
    expect(
        candidate_source.get("sourceSnapshotId")
        == prediction_run.get("candidateSourceSnapshotId"),
        f"{surface_label}.candidateSource.sourceSnapshotId must match predictionRun",
        errors,
    )
    expect(
        candidate_source.get("sourcePolicyVersion")
        == prediction_run.get("candidateSourcePolicyVersion"),
        f"{surface_label}.candidateSource.sourcePolicyVersion must match predictionRun",
        errors,
    )
    expect(
        candidate_source.get("rankingSnapshotId") == prediction_run.get("snapshotId"),
        f"{surface_label}.candidateSource.rankingSnapshotId must match predictionRun.snapshotId",
        errors,
    )
    expect(
        prediction_run.get("candidateCount") == len(scores),
        f"{surface_label}.predictionRun.candidateCount must match len(scores)",
        errors,
    )

    if contract_version == RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION:
        expect(
            isinstance(profile_selection.get("requestedProfileId"), str)
            and bool(profile_selection.get("requestedProfileId")),
            f"{surface_label}.profileSelection.requestedProfileId must be a non-empty string for vNext preview contracts",
            errors,
        )
        expect(
            isinstance(profile_selection.get("stageMode"), str)
            and bool(profile_selection.get("stageMode")),
            f"{surface_label}.profileSelection.stageMode must be a non-empty string for vNext preview contracts",
            errors,
        )
        expect(
            prediction_run.get("scoringContextSchemaVersion") == "scoring-context.v1",
            f"{surface_label}.predictionRun.scoringContextSchemaVersion must stay explicit for vNext preview contracts",
            errors,
        )
        expect(
            isinstance(prediction_run.get("createdAt"), str)
            and bool(prediction_run.get("createdAt")),
            f"{surface_label}.predictionRun.createdAt must be a non-empty string for vNext preview contracts",
            errors,
        )
        if candidate_source.get("sourceKind") == "derived_shared_fixture":
            expect(
                isinstance(candidate_source.get("sourceArtifact"), str)
                and bool(candidate_source.get("sourceArtifact")),
                f"{surface_label}.candidateSource.sourceArtifact must be a non-empty string for derived shared fixtures in vNext preview contracts",
                errors,
            )

    score_topic_ids: list[str] = []
    rejected_topic_ids_from_scores: list[str] = []
    priority_counts_from_scores = {"P0": 0, "P1": 0, "P2": 0}
    rerank_by_topic: dict[str, dict[str, Any]] = {}

    for index, score in enumerate(scores):
        prefix = f"{surface_label}.scores[{index}]"
        if not isinstance(score, dict):
            errors.append(f"{prefix} must be an object")
            continue

        expect(
            score.get("schemaVersion") == "topic-score.v1",
            f"{prefix} has unexpected schemaVersion",
            errors,
        )
        topic_id = score.get("topicId")
        expect(
            isinstance(topic_id, str) and bool(topic_id),
            f"{prefix}.topicId must be a non-empty string",
            errors,
        )
        if isinstance(topic_id, str):
            score_topic_ids.append(topic_id)
        expect(
            isinstance(score.get("topicFingerprint"), str) and bool(score.get("topicFingerprint")),
            f"{prefix}.topicFingerprint must be a non-empty string",
            errors,
        )
        expect(
            score.get("profileId") == top_profile_id,
            f"{prefix}.profileId must match {label}.profileId",
            errors,
        )
        expect(
            isinstance(score.get("recommendedUse"), str) and bool(score.get("recommendedUse")),
            f"{prefix}.recommendedUse must be a non-empty string",
            errors,
        )
        expect(
            isinstance(score.get("nextAction"), str) and bool(score.get("nextAction")),
            f"{prefix}.nextAction must be a non-empty string",
            errors,
        )
        expect(
            isinstance(score.get("scoreReason"), str) and bool(score.get("scoreReason")),
            f"{prefix}.scoreReason must be a non-empty string",
            errors,
        )
        expect(
            isinstance(score.get("riskFlags"), list),
            f"{prefix}.riskFlags must be a list",
            errors,
        )
        priority_level = score.get("priorityLevel")
        expect(
            priority_level in PRIORITY_LEVELS,
            f"{prefix}.priorityLevel must be one of {sorted(PRIORITY_LEVELS)}",
            errors,
        )
        if priority_level in PRIORITY_LEVELS:
            priority_counts_from_scores[priority_level] += 1

        score_total = score.get("scoreTotal")
        rerank_adjusted_score = score.get("rerankAdjustedScore")
        expect(
            isinstance(score_total, (int, float)),
            f"{prefix}.scoreTotal must be numeric",
            errors,
        )
        expect(
            isinstance(rerank_adjusted_score, (int, float)),
            f"{prefix}.rerankAdjustedScore must be numeric",
            errors,
        )
        if isinstance(score_total, (int, float)) and isinstance(rerank_adjusted_score, (int, float)):
            expect(
                float(rerank_adjusted_score) <= float(score_total),
                f"{prefix}.rerankAdjustedScore must not exceed scoreTotal",
                errors,
            )

        score_breakdown = require_object(score.get("scoreBreakdown"), f"{prefix}.scoreBreakdown", errors)
        validate_score_breakdown(score_breakdown, prefix, errors)
        feature_vector = require_object(score.get("featureVector"), f"{prefix}.featureVector", errors)
        validate_feature_vector(feature_vector, prefix, errors)

        is_rejected = score.get("isRejected")
        expect(
            isinstance(is_rejected, bool),
            f"{prefix}.isRejected must be a boolean",
            errors,
        )
        expect(
            isinstance(score.get("rerankReasons"), list),
            f"{prefix}.rerankReasons must be a list",
            errors,
        )
        if is_rejected is True and isinstance(topic_id, str):
            rejected_topic_ids_from_scores.append(topic_id)
        rejection_reason = score.get("rejectionReason")
        if is_rejected is True:
            expect(
                isinstance(rejection_reason, str) and bool(rejection_reason),
                f"{prefix}.rejectionReason must be a non-empty string when isRejected is true",
                errors,
            )
        if is_rejected is False:
            expect(
                rejection_reason is None,
                f"{prefix}.rejectionReason must be null when isRejected is false",
                errors,
            )

    expect(
        prediction_run.get("rankedTopicIds") == score_topic_ids,
        f"{surface_label}.predictionRun.rankedTopicIds must match scores order",
        errors,
    )

    if score_topic_ids:
        expect(
            ranking_summary.get("topTopicId") == score_topic_ids[0],
            f"{surface_label}.rankingSummary.topTopicId must match the first ranked score",
            errors,
        )
        top_title = ranking_summary.get("topTopicTitle")
        top_reason = scores[0].get("scoreReason") if isinstance(scores[0], dict) else None
        expect(
            isinstance(top_title, str) and bool(top_title),
            f"{surface_label}.rankingSummary.topTopicTitle must be a non-empty string",
            errors,
        )
        if isinstance(top_title, str) and isinstance(top_reason, str):
            expect(
                top_reason.startswith(top_title),
                f"{surface_label}.rankingSummary.topTopicTitle must align with the top scoreReason prefix",
                errors,
            )

    expect(
        ranking_summary.get("rejectedTopicIds") == rejected_topic_ids_from_scores,
        f"{surface_label}.rankingSummary.rejectedTopicIds must match rejected scores",
        errors,
    )
    expect(
        ranking_summary.get("priorityCounts") == priority_counts_from_scores,
        f"{surface_label}.rankingSummary.priorityCounts must match score priority distribution",
        errors,
    )

    for index, row in enumerate(rerank_diagnostics):
        prefix = f"{surface_label}.rerankDiagnostics[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        topic_id = row.get("topicId")
        expect(
            isinstance(topic_id, str) and bool(topic_id),
            f"{prefix}.topicId must be a non-empty string",
            errors,
        )
        if isinstance(topic_id, str):
            rerank_by_topic[topic_id] = row

        expect(
            isinstance(row.get("scoreTotal"), (int, float)),
            f"{prefix}.scoreTotal must be numeric",
            errors,
        )
        expect(
            isinstance(row.get("rerankAdjustedScore"), (int, float)),
            f"{prefix}.rerankAdjustedScore must be numeric",
            errors,
        )
        expect(
            isinstance(row.get("reasons"), list),
            f"{prefix}.reasons must be a list",
            errors,
        )
        expect(
            isinstance(row.get("isRejected"), bool),
            f"{prefix}.isRejected must be a boolean",
            errors,
        )

    expect(
        sorted(rerank_by_topic.keys()) == sorted(score_topic_ids),
        f"{surface_label}.rerankDiagnostics must cover exactly the scored topicIds",
        errors,
    )

    for score in scores:
        if not isinstance(score, dict):
            continue
        topic_id = score.get("topicId")
        if not isinstance(topic_id, str):
            continue
        rerank_row = rerank_by_topic.get(topic_id)
        expect(
            rerank_row is not None,
            f"{surface_label}.rerankDiagnostics is missing topicId `{topic_id}`",
            errors,
        )
        if rerank_row is None:
            continue
        expect(
            rerank_row.get("scoreTotal") == score.get("scoreTotal"),
            f"{surface_label}.rerankDiagnostics for `{topic_id}` must match scoreTotal",
            errors,
        )
        expect(
            rerank_row.get("rerankAdjustedScore") == score.get("rerankAdjustedScore"),
            f"{surface_label}.rerankDiagnostics for `{topic_id}` must match rerankAdjustedScore",
            errors,
        )
        expect(
            rerank_row.get("reasons") == score.get("rerankReasons"),
            f"{surface_label}.rerankDiagnostics for `{topic_id}` must match rerankReasons",
            errors,
        )
        expect(
            rerank_row.get("isRejected") == score.get("isRejected"),
            f"{surface_label}.rerankDiagnostics for `{topic_id}` must match isRejected",
            errors,
        )

    return errors


def require_ranking_payload_for_optimizer(
    payload: dict[str, Any],
    label: str = "ranking",
    *,
    contract_version: str = RANKING_OPTIMIZER_CONTRACT_VERSION,
    validation_mode: str = RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
) -> dict[str, Any]:
    normalized_payload, _ = prepare_ranking_payload_for_optimizer(
        payload,
        label=label,
        contract_version=contract_version,
        validation_mode=validation_mode,
    )
    return select_optimizer_handoff_payload(
        normalized_payload,
        contract_version=contract_version,
    )
