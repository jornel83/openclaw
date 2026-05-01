#!/usr/bin/env python3
"""
Helpers for scheduler-facing optimizer daily/weekly job schedule artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from optimizer_input_rollout_lib import resolve_optimizer_input_rollout_selection
from optimizer_runtime_profile_lib import DEFAULT_RUNTIME_PROFILE_FAMILY_ID
from optimizer_runtime_profile_rollout_lib import (
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS,
    resolve_runtime_profile_eval_purpose_policy,
)

OPTIMIZER_JOB_SCHEDULE_SAMPLE_SCHEMA_VERSION = "optimizer-job-schedule.sample.v1"
OPTIMIZER_JOB_SCHEDULE_SCHEMA_VERSION = "optimizer-job-schedule.v1"
OPTIMIZER_JOB_SCHEDULE_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_SCHEDULE_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_SCHEDULE_SCHEMA_VERSION,
}
OPTIMIZER_JOB_SCHEDULE_JOB_KINDS = {
    "daily_optimizer_job",
    "weekly_optimizer_job",
}
OPTIMIZER_JOB_SCHEDULE_INPUT_MODES = {"manifest", "bundle"}
OPTIMIZER_JOB_SCHEDULE_CADENCE_KINDS = {"daily", "weekly"}
OPTIMIZER_JOB_SCHEDULE_PROFILES = {"fixture_replay", "external_scheduler"}
OPTIMIZER_JOB_SCHEDULE_PATH_RESOLUTION_MODES = {
    "repo_relative",
    "scheduler_supplied",
}
OPTIMIZER_JOB_SCHEDULE_OUTPUT_EMISSION_MODES = {
    "direct_output_path",
    "output_root",
}
OPTIMIZER_JOB_SCHEDULE_TRIGGER_KINDS = {"manual", "cron", "planner"}
OPTIMIZER_JOB_SCHEDULE_EXECUTION_ENVIRONMENTS = {
    "repo_local",
    "scheduler_managed",
}
OPTIMIZER_JOB_SCHEDULE_INTENT_SELECTION_SOURCES = {
    "schedule_default",
    "explicit_scheduler_intent",
    "mapped_from_explicit_rollout_class",
}
OPTIMIZER_JOB_SCHEDULE_EXECUTION_SELECTION_SOURCES = {
    "schedule_default",
    "explicit_scheduler_intent",
    "mapped_from_explicit_rollout_class",
}
OPTIMIZER_JOB_SCHEDULE_RUNTIME_ROLE = "compatibility_rehearsal"
OPTIMIZER_JOB_SCHEDULE_PREFERRED_RECURRING_RUNTIME = "openclaw_cron"
OPTIMIZER_JOB_SCHEDULE_INTENDED_USES = [
    "fixture_generation",
    "deterministic_rehearsal",
    "cutover_validation",
]

PRODUCTION_SCHEDULER_ROLLOUT_INTENT = "production"
RAW_SHADOW_SCHEDULER_ROLLOUT_INTENT = "raw_shadow_validation"
REAL_PROVIDER_SHADOW_SCHEDULER_ROLLOUT_INTENT = "real_provider_shadow_validation"
PREVIEW_VALIDATION_SCHEDULER_ROLLOUT_INTENT = "preview_validation"
PROFILE_COMPARE_VALIDATION_SCHEDULER_ROLLOUT_INTENT = "profile_compare_validation"

OPTIMIZER_JOB_SCHEDULE_ROLLOUT_INTENTS = {
    PRODUCTION_SCHEDULER_ROLLOUT_INTENT,
    RAW_SHADOW_SCHEDULER_ROLLOUT_INTENT,
    REAL_PROVIDER_SHADOW_SCHEDULER_ROLLOUT_INTENT,
    PREVIEW_VALIDATION_SCHEDULER_ROLLOUT_INTENT,
    PROFILE_COMPARE_VALIDATION_SCHEDULER_ROLLOUT_INTENT,
}


def _build_scheduler_intent_runtime_profile_defaults(
    *,
    scheduler_rollout_intent: str,
    runtime_profile_rollout_policy_payload: dict[str, Any] | None,
) -> dict[str, str | None]:
    if scheduler_rollout_intent in {
        PRODUCTION_SCHEDULER_ROLLOUT_INTENT,
        RAW_SHADOW_SCHEDULER_ROLLOUT_INTENT,
        REAL_PROVIDER_SHADOW_SCHEDULER_ROLLOUT_INTENT,
    }:
        return {
            "runtimeProfileRolloutClass": DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS,
            "windowSetPurpose": None,
            "comparisonDimension": None,
        }
    if scheduler_rollout_intent == PREVIEW_VALIDATION_SCHEDULER_ROLLOUT_INTENT:
        window_set_purpose = "preview_validation"
        fallback_comparison_dimension = None
    elif scheduler_rollout_intent == PROFILE_COMPARE_VALIDATION_SCHEDULER_ROLLOUT_INTENT:
        window_set_purpose = "profile_compare_validation"
        fallback_comparison_dimension = "rankingProfileId"
    else:
        raise ValueError(
            f"unsupported optimizer job schedulerRolloutIntent {scheduler_rollout_intent!r}"
        )

    if runtime_profile_rollout_policy_payload is None:
        return {
            "runtimeProfileRolloutClass": "preview_canary",
            "windowSetPurpose": window_set_purpose,
            "comparisonDimension": fallback_comparison_dimension,
        }

    purpose_resolution = resolve_runtime_profile_eval_purpose_policy(
        window_set_purpose=window_set_purpose,
        requested_family_id=DEFAULT_RUNTIME_PROFILE_FAMILY_ID,
        rollout_policy=runtime_profile_rollout_policy_payload,
    )
    if purpose_resolution is None:
        raise ValueError(
            f"optimizer runtime profile rollout policy does not define windowSetPurpose {window_set_purpose!r}"
        )
    return {
        "runtimeProfileRolloutClass": purpose_resolution["defaultRolloutClass"],
        "windowSetPurpose": purpose_resolution["windowSetPurpose"],
        "comparisonDimension": purpose_resolution.get("defaultComparisonDimension"),
    }


def build_optimizer_job_schedule_rollout_intent_entry(
    *,
    scheduler_rollout_intent: str,
    input_rollout_intent: str,
    input_rollout_class: str,
    runtime_profile_rollout_class: str,
    window_set_purpose: str | None = None,
    comparison_dimension: str | None = None,
) -> dict[str, str]:
    payload = {
        "schedulerRolloutIntent": scheduler_rollout_intent,
        "inputRolloutIntent": input_rollout_intent,
        "inputRolloutClass": input_rollout_class,
        "runtimeProfileRolloutClass": runtime_profile_rollout_class,
    }
    if window_set_purpose is not None:
        payload["windowSetPurpose"] = window_set_purpose
    if comparison_dimension is not None:
        payload["comparisonDimension"] = comparison_dimension
    return payload


def build_default_optimizer_job_schedule_rollout_intents(
    *,
    runtime_profile_rollout_policy_payload: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    preview_defaults = _build_scheduler_intent_runtime_profile_defaults(
        scheduler_rollout_intent=PREVIEW_VALIDATION_SCHEDULER_ROLLOUT_INTENT,
        runtime_profile_rollout_policy_payload=runtime_profile_rollout_policy_payload,
    )
    profile_compare_defaults = _build_scheduler_intent_runtime_profile_defaults(
        scheduler_rollout_intent=PROFILE_COMPARE_VALIDATION_SCHEDULER_ROLLOUT_INTENT,
        runtime_profile_rollout_policy_payload=runtime_profile_rollout_policy_payload,
    )
    return [
        build_optimizer_job_schedule_rollout_intent_entry(
            scheduler_rollout_intent=PRODUCTION_SCHEDULER_ROLLOUT_INTENT,
            input_rollout_intent="production_run",
            input_rollout_class="production",
            runtime_profile_rollout_class="production",
        ),
        build_optimizer_job_schedule_rollout_intent_entry(
            scheduler_rollout_intent=RAW_SHADOW_SCHEDULER_ROLLOUT_INTENT,
            input_rollout_intent="raw_shadow_validation",
            input_rollout_class="raw_shadow_validation",
            runtime_profile_rollout_class="production",
        ),
        build_optimizer_job_schedule_rollout_intent_entry(
            scheduler_rollout_intent=REAL_PROVIDER_SHADOW_SCHEDULER_ROLLOUT_INTENT,
            input_rollout_intent="real_provider_shadow_validation",
            input_rollout_class="real_shadow_validation",
            runtime_profile_rollout_class="production",
        ),
        build_optimizer_job_schedule_rollout_intent_entry(
            scheduler_rollout_intent=PREVIEW_VALIDATION_SCHEDULER_ROLLOUT_INTENT,
            input_rollout_intent="production_run",
            input_rollout_class="production",
            runtime_profile_rollout_class=preview_defaults[
                "runtimeProfileRolloutClass"
            ],
            window_set_purpose=preview_defaults["windowSetPurpose"],
            comparison_dimension=preview_defaults["comparisonDimension"],
        ),
        build_optimizer_job_schedule_rollout_intent_entry(
            scheduler_rollout_intent=PROFILE_COMPARE_VALIDATION_SCHEDULER_ROLLOUT_INTENT,
            input_rollout_intent="production_run",
            input_rollout_class="production",
            runtime_profile_rollout_class=profile_compare_defaults[
                "runtimeProfileRolloutClass"
            ],
            window_set_purpose=profile_compare_defaults["windowSetPurpose"],
            comparison_dimension=profile_compare_defaults["comparisonDimension"],
        ),
    ]


def _build_default_schedule_entries(
    *,
    schedule_profile: str,
    input_manifest_path: str | None,
    weekly_review_window_path: str | None,
    input_source_registry_path: str | None,
    input_rollout_policy_payload: dict[str, Any] | None,
    rollout_intent_catalog: list[dict[str, Any]],
    policy_path: str | None,
    ranking_contract_version: str,
    ranking_contract_validation_mode: str,
    default_output_root: str | None,
) -> list[dict[str, Any]]:
    scheduler_rollout_intent_catalog = {
        entry["schedulerRolloutIntent"]: entry
        for entry in rollout_intent_catalog
        if isinstance(entry, dict)
        and isinstance(entry.get("schedulerRolloutIntent"), str)
        and entry.get("schedulerRolloutIntent")
    }
    default_daily_rollout = (
        resolve_optimizer_input_rollout_selection(
            input_rollout_policy_payload,
            schedule_id="daily_optimizer_job",
        )
        if input_rollout_policy_payload is not None
        else None
    )
    default_weekly_rollout = (
        resolve_optimizer_input_rollout_selection(
            input_rollout_policy_payload,
            schedule_id="weekly_optimizer_job",
        )
        if input_rollout_policy_payload is not None
        else None
    )
    schedule_policies = (
        {
            entry["scheduleId"]: entry
            for entry in input_rollout_policy_payload.get("schedulePolicies", [])
        }
        if input_rollout_policy_payload is not None
        else {}
    )
    is_external_profile = schedule_profile == "external_scheduler"
    path_resolution_mode = (
        "scheduler_supplied" if is_external_profile else "repo_relative"
    )
    output_emission_mode = (
        "output_root" if is_external_profile else "direct_output_path"
    )
    execution_environment = (
        "scheduler_managed" if is_external_profile else "repo_local"
    )
    trigger_kind = "cron" if is_external_profile else "manual"
    scheduler_owner = (
        "external_scheduler" if is_external_profile else "repo_fixture"
    )
    allowed_scheduler_rollout_intents = sorted(scheduler_rollout_intent_catalog.keys())
    default_scheduler_rollout_intent = PRODUCTION_SCHEDULER_ROLLOUT_INTENT
    default_scheduler_rollout_entry = scheduler_rollout_intent_catalog.get(
        default_scheduler_rollout_intent, {}
    )
    allowed_runtime_profile_rollout_classes = sorted(
        {
            entry["runtimeProfileRolloutClass"]
            for intent, entry in scheduler_rollout_intent_catalog.items()
            if intent in allowed_scheduler_rollout_intents
            and isinstance(entry.get("runtimeProfileRolloutClass"), str)
            and entry.get("runtimeProfileRolloutClass")
        }
    )
    allowed_window_set_purposes = sorted(
        {
            entry["windowSetPurpose"]
            for intent, entry in scheduler_rollout_intent_catalog.items()
            if intent in allowed_scheduler_rollout_intents
            and isinstance(entry.get("windowSetPurpose"), str)
            and entry.get("windowSetPurpose")
        }
    )
    allowed_comparison_dimensions = sorted(
        {
            entry["comparisonDimension"]
            for intent, entry in scheduler_rollout_intent_catalog.items()
            if intent in allowed_scheduler_rollout_intents
            and isinstance(entry.get("comparisonDimension"), str)
            and entry.get("comparisonDimension")
        }
    )
    return [
        {
            "scheduleId": "daily_optimizer_job",
            "cadenceKind": "daily",
            "scheduleHint": "daily@04:00Z",
            "jobKind": "daily_optimizer_job",
            "entryPoint": "skills/autotiktok-strategy-optimizer/scripts/run_daily_optimizer_job.py",
            "defaultInputMode": "manifest",
            "pathResolutionMode": path_resolution_mode,
            "outputEmissionMode": output_emission_mode,
            "defaultInputPath": None if is_external_profile else input_manifest_path,
            "defaultPolicyPath": None if is_external_profile else policy_path,
            "defaultOutputPath": None
            if is_external_profile
            else "skills/autotiktok-strategy-optimizer/fixtures/optimizer-daily-job-run.sample.json",
            "defaultOutputRoot": default_output_root if is_external_profile else None,
            "outputSubdir": "daily_optimizer_job",
            "defaultTriggerKind": trigger_kind,
            "defaultSchedulerOwner": scheduler_owner,
            "defaultExecutionEnvironment": execution_environment,
            "rankingContractVersion": ranking_contract_version,
            "rankingContractValidationMode": ranking_contract_validation_mode,
            "includeWeeklyPromotion": False,
            "defaultWeeklyReviewWindowPath": None,
            "defaultInputSourceRegistryPath": None
            if is_external_profile
            else input_source_registry_path,
            "defaultSchedulerRolloutIntent": default_scheduler_rollout_intent,
            "allowedSchedulerRolloutIntents": allowed_scheduler_rollout_intents,
            "defaultRuntimeProfileRolloutClass": default_scheduler_rollout_entry.get(
                "runtimeProfileRolloutClass"
            ),
            "defaultWindowSetPurpose": default_scheduler_rollout_entry.get(
                "windowSetPurpose"
            ),
            "defaultComparisonDimension": default_scheduler_rollout_entry.get(
                "comparisonDimension"
            ),
            "allowedRuntimeProfileRolloutClasses": allowed_runtime_profile_rollout_classes,
            "allowedWindowSetPurposes": allowed_window_set_purposes,
            "allowedComparisonDimensions": allowed_comparison_dimensions,
            "defaultInputRolloutClass": None
            if default_daily_rollout is None
            else default_daily_rollout["rolloutClass"],
            "defaultInputRolloutIntent": None
            if default_daily_rollout is None
            else default_daily_rollout["rolloutIntent"],
            "defaultInputRolloutSelectionSource": None
            if default_daily_rollout is None
            else default_daily_rollout["selectionSource"],
            "defaultInputRolloutIntentSelectionSource": None
            if default_daily_rollout is None
            else default_daily_rollout["rolloutIntentSelectionSource"],
            "defaultInputRolloutClassSelectionSource": None
            if default_daily_rollout is None
            else default_daily_rollout["rolloutClassSelectionSource"],
            "defaultInputSourceLane": None
            if default_daily_rollout is None
            else default_daily_rollout["sourceLane"],
            "allowedInputRolloutIntents": None
            if "daily_optimizer_job" not in schedule_policies
            else schedule_policies["daily_optimizer_job"]["allowedRolloutIntents"],
            "allowedInputRolloutClasses": None
            if "daily_optimizer_job" not in schedule_policies
            else schedule_policies["daily_optimizer_job"]["allowedRolloutClasses"],
            "defaultJobRunId": "optimizer-daily-job-run.autotiktok.fixture.2026-04-18",
            "defaultCycleId": "optimizer-offline-cycle.autotiktok.fixture.2026-04-18.daily-job",
            "defaultEvalRunId": "optimizer-eval-run.autotiktok.fixture.2026-04-18.daily-job",
            "defaultReportId": "daily-review.autotiktok.fixture.2026-04-18.daily-job",
            "defaultGeneratedAt": "2026-04-18T04:00:00Z",
        },
        {
            "scheduleId": "weekly_optimizer_job",
            "cadenceKind": "weekly",
            "scheduleHint": "weekly@Sun-04:15Z",
            "jobKind": "weekly_optimizer_job",
            "entryPoint": "skills/autotiktok-strategy-optimizer/scripts/run_weekly_optimizer_job.py",
            "defaultInputMode": "manifest",
            "pathResolutionMode": path_resolution_mode,
            "outputEmissionMode": output_emission_mode,
            "defaultInputPath": None if is_external_profile else input_manifest_path,
            "defaultPolicyPath": None if is_external_profile else policy_path,
            "defaultOutputPath": None
            if is_external_profile
            else "skills/autotiktok-strategy-optimizer/fixtures/optimizer-weekly-job-run.sample.json",
            "defaultOutputRoot": default_output_root if is_external_profile else None,
            "outputSubdir": "weekly_optimizer_job",
            "defaultTriggerKind": trigger_kind,
            "defaultSchedulerOwner": scheduler_owner,
            "defaultExecutionEnvironment": execution_environment,
            "rankingContractVersion": ranking_contract_version,
            "rankingContractValidationMode": ranking_contract_validation_mode,
            "includeWeeklyPromotion": True,
            "defaultWeeklyReviewWindowPath": None
            if is_external_profile
            else weekly_review_window_path,
            "defaultInputSourceRegistryPath": None
            if is_external_profile
            else input_source_registry_path,
            "defaultSchedulerRolloutIntent": default_scheduler_rollout_intent,
            "allowedSchedulerRolloutIntents": allowed_scheduler_rollout_intents,
            "defaultRuntimeProfileRolloutClass": default_scheduler_rollout_entry.get(
                "runtimeProfileRolloutClass"
            ),
            "defaultWindowSetPurpose": default_scheduler_rollout_entry.get(
                "windowSetPurpose"
            ),
            "defaultComparisonDimension": default_scheduler_rollout_entry.get(
                "comparisonDimension"
            ),
            "allowedRuntimeProfileRolloutClasses": allowed_runtime_profile_rollout_classes,
            "allowedWindowSetPurposes": allowed_window_set_purposes,
            "allowedComparisonDimensions": allowed_comparison_dimensions,
            "defaultInputRolloutClass": None
            if default_weekly_rollout is None
            else default_weekly_rollout["rolloutClass"],
            "defaultInputRolloutIntent": None
            if default_weekly_rollout is None
            else default_weekly_rollout["rolloutIntent"],
            "defaultInputRolloutSelectionSource": None
            if default_weekly_rollout is None
            else default_weekly_rollout["selectionSource"],
            "defaultInputRolloutIntentSelectionSource": None
            if default_weekly_rollout is None
            else default_weekly_rollout["rolloutIntentSelectionSource"],
            "defaultInputRolloutClassSelectionSource": None
            if default_weekly_rollout is None
            else default_weekly_rollout["rolloutClassSelectionSource"],
            "defaultInputSourceLane": None
            if default_weekly_rollout is None
            else default_weekly_rollout["sourceLane"],
            "allowedInputRolloutIntents": None
            if "weekly_optimizer_job" not in schedule_policies
            else schedule_policies["weekly_optimizer_job"]["allowedRolloutIntents"],
            "allowedInputRolloutClasses": None
            if "weekly_optimizer_job" not in schedule_policies
            else schedule_policies["weekly_optimizer_job"]["allowedRolloutClasses"],
            "defaultJobRunId": "optimizer-weekly-job-run.autotiktok.fixture.2026-04-18",
            "defaultCycleId": "optimizer-offline-cycle.autotiktok.fixture.2026-04-18.weekly-job",
            "defaultEvalRunId": "optimizer-eval-run.autotiktok.fixture.2026-04-18.weekly-job",
            "defaultReportId": "daily-review.autotiktok.fixture.2026-04-18.weekly-job",
            "defaultGeneratedAt": "2026-04-18T04:15:00Z",
        },
    ]


def build_optimizer_job_schedule_payload(
    *,
    schedule_plan_id: str,
    generated_at: str,
    schedule_profile: str,
    input_manifest_path: str | None,
    weekly_review_window_path: str | None,
    input_source_registry_path: str | None,
    input_manifest_payload: dict[str, Any],
    input_rollout_policy_payload: dict[str, Any] | None,
    runtime_profile_rollout_policy_payload: dict[str, Any] | None,
    rollout_intent_catalog: list[dict[str, Any]] | None,
    input_rollout_policy_path: str | None,
    runtime_profile_rollout_policy_path: str | None,
    policy_path: str | None,
    ranking_contract_version: str,
    ranking_contract_validation_mode: str,
    default_output_root: str | None = None,
    schedules: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    manifest_generated_from = input_manifest_payload.get("generatedFrom", {})
    resolved_sources = manifest_generated_from.get("resolvedSources", {})
    effective_schedules = schedules or _build_default_schedule_entries(
        schedule_profile=schedule_profile,
        input_manifest_path=input_manifest_path,
        weekly_review_window_path=weekly_review_window_path,
        input_source_registry_path=input_source_registry_path,
        input_rollout_policy_payload=input_rollout_policy_payload,
        rollout_intent_catalog=rollout_intent_catalog or [],
        policy_path=policy_path,
        ranking_contract_version=ranking_contract_version,
        ranking_contract_validation_mode=ranking_contract_validation_mode,
        default_output_root=default_output_root,
    )
    effective_rollout_intent_catalog = (
        list(rollout_intent_catalog) if rollout_intent_catalog is not None else []
    )
    path_resolution_mode = (
        "scheduler_supplied"
        if schedule_profile == "external_scheduler"
        else "repo_relative"
    )
    output_emission_mode = (
        "output_root"
        if schedule_profile == "external_scheduler"
        else "direct_output_path"
    )
    execution_environment = (
        "scheduler_managed"
        if schedule_profile == "external_scheduler"
        else "repo_local"
    )
    trigger_kind = "cron" if schedule_profile == "external_scheduler" else "manual"
    scheduler_owner = (
        "external_scheduler"
        if schedule_profile == "external_scheduler"
        else "repo_fixture"
    )
    return {
        "schemaVersion": OPTIMIZER_JOB_SCHEDULE_SAMPLE_SCHEMA_VERSION,
        "schedulePlanId": schedule_plan_id,
        "generatedAt": generated_at,
        "scheduleProfile": schedule_profile,
        "runtimeRole": OPTIMIZER_JOB_SCHEDULE_RUNTIME_ROLE,
        "preferredRecurringRuntime": OPTIMIZER_JOB_SCHEDULE_PREFERRED_RECURRING_RUNTIME,
        "intendedUses": list(OPTIMIZER_JOB_SCHEDULE_INTENDED_USES),
        "defaultPathResolutionMode": path_resolution_mode,
        "defaultOutputEmissionMode": output_emission_mode,
        "defaultOutputRoot": default_output_root,
        "defaultTriggerKind": trigger_kind,
        "defaultSchedulerOwner": scheduler_owner,
        "defaultExecutionEnvironment": execution_environment,
        "generatedFrom": {
            "optimizerInputManifestSchemaVersion": input_manifest_payload.get(
                "schemaVersion"
            ),
            "optimizerInputManifestId": input_manifest_payload.get("manifestId"),
            "optimizerInputManifestPath": input_manifest_path,
            "optimizerInputSourceRegistrySchemaVersion": manifest_generated_from.get(
                "optimizerInputSourceRegistrySchemaVersion"
            ),
            "optimizerInputSourceRegistryId": manifest_generated_from.get(
                "optimizerInputSourceRegistryId"
            ),
            "optimizerInputArtifactResolverSchemaVersion": manifest_generated_from.get(
                "optimizerInputArtifactResolverSchemaVersion",
                input_manifest_payload.get("resolvedInputArtifactResolverSchemaVersion"),
            ),
            "optimizerInputArtifactResolverId": manifest_generated_from.get(
                "optimizerInputArtifactResolverId",
                input_manifest_payload.get("resolvedInputArtifactResolverId"),
            ),
            "optimizerInputSourceProviderCatalogSchemaVersion": manifest_generated_from.get(
                "optimizerInputSourceProviderCatalogSchemaVersion",
                input_manifest_payload.get("resolvedInputSourceProviderCatalogSchemaVersion"),
            ),
            "optimizerInputSourceProviderCatalogId": manifest_generated_from.get(
                "optimizerInputSourceProviderCatalogId",
                input_manifest_payload.get("resolvedInputSourceProviderCatalogId"),
            ),
            "optimizerInputSourceProviderRegistrySchemaVersion": manifest_generated_from.get(
                "optimizerInputSourceProviderRegistrySchemaVersion",
                input_manifest_payload.get("resolvedInputSourceProviderRegistrySchemaVersion"),
            ),
            "optimizerInputSourceProviderRegistryId": manifest_generated_from.get(
                "optimizerInputSourceProviderRegistryId",
                input_manifest_payload.get("resolvedInputSourceProviderRegistryId"),
            ),
            "optimizerInputSourceArtifactCatalogSchemaVersion": manifest_generated_from.get(
                "optimizerInputSourceArtifactCatalogSchemaVersion",
                input_manifest_payload.get("resolvedInputSourceArtifactCatalogSchemaVersion"),
            ),
            "optimizerInputSourceArtifactCatalogId": manifest_generated_from.get(
                "optimizerInputSourceArtifactCatalogId",
                input_manifest_payload.get("resolvedInputSourceArtifactCatalogId"),
            ),
            "resolvedSourceLane": manifest_generated_from.get("sourceLane"),
            "optimizerInputSourceProviderLane": manifest_generated_from.get(
                "optimizerInputSourceProviderLane"
            ),
            "optimizerInputSourceProviderKind": manifest_generated_from.get(
                "optimizerInputSourceProviderKind"
            ),
            "optimizerInputSourceProviderClass": manifest_generated_from.get(
                "optimizerInputSourceProviderClass"
            ),
            "optimizerInputSourceProviderHandle": manifest_generated_from.get(
                "optimizerInputSourceProviderHandle"
            ),
            "optimizerInputSourceProviderLocatorKind": manifest_generated_from.get(
                "optimizerInputSourceProviderLocatorKind"
            ),
            "optimizerInputSourceProviderOwner": manifest_generated_from.get(
                "optimizerInputSourceProviderOwner"
            ),
            "optimizerInputArtifactLocatorKind": manifest_generated_from.get(
                "optimizerInputArtifactLocatorKind"
            ),
            "optimizerInputSourceRegistryPath": input_source_registry_path,
            "optimizerInputRolloutPolicySchemaVersion": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("schemaVersion"),
            "optimizerInputRolloutPolicyId": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("policyId"),
            "optimizerInputRolloutPolicyFamily": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("policyFamily"),
            "optimizerInputRolloutPolicyVersion": None
            if input_rollout_policy_payload is None
            else input_rollout_policy_payload.get("policyVersion"),
            "optimizerInputRolloutPolicyPath": input_rollout_policy_path,
            "optimizerRuntimeProfileRolloutPolicySchemaVersion": None
            if runtime_profile_rollout_policy_payload is None
            else runtime_profile_rollout_policy_payload.get("schemaVersion"),
            "optimizerRuntimeProfileRolloutPolicyId": None
            if runtime_profile_rollout_policy_payload is None
            else runtime_profile_rollout_policy_payload.get("policyId"),
            "optimizerRuntimeProfileRolloutPolicyFamily": None
            if runtime_profile_rollout_policy_payload is None
            else runtime_profile_rollout_policy_payload.get("policyFamily"),
            "optimizerRuntimeProfileRolloutPolicyVersion": None
            if runtime_profile_rollout_policy_payload is None
            else runtime_profile_rollout_policy_payload.get("policyVersion"),
            "optimizerRuntimeProfileRolloutPolicyPath": runtime_profile_rollout_policy_path,
            "resolvedSourceBindingCount": len(resolved_sources),
            "policyPath": policy_path,
            "schedulerRolloutIntentCount": len(effective_rollout_intent_catalog),
            "scheduleCount": len(effective_schedules),
        },
        "schedulerRolloutIntents": effective_rollout_intent_catalog,
        "schedules": effective_schedules,
    }


def validate_optimizer_job_schedule_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_JOB_SCHEDULE_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer job schedule payload must declare a supported schemaVersion"
        )
    schedule_profile = payload.get("scheduleProfile")
    if schedule_profile not in OPTIMIZER_JOB_SCHEDULE_PROFILES:
        raise ValueError(
            "optimizer job schedule payload must declare a supported scheduleProfile"
        )
    default_path_resolution_mode = payload.get("defaultPathResolutionMode")
    if default_path_resolution_mode not in OPTIMIZER_JOB_SCHEDULE_PATH_RESOLUTION_MODES:
        raise ValueError(
            "optimizer job schedule payload must declare a supported defaultPathResolutionMode"
        )
    default_output_emission_mode = payload.get("defaultOutputEmissionMode")
    if default_output_emission_mode not in OPTIMIZER_JOB_SCHEDULE_OUTPUT_EMISSION_MODES:
        raise ValueError(
            "optimizer job schedule payload must declare a supported defaultOutputEmissionMode"
        )
    default_trigger_kind = payload.get("defaultTriggerKind")
    if default_trigger_kind not in OPTIMIZER_JOB_SCHEDULE_TRIGGER_KINDS:
        raise ValueError(
            "optimizer job schedule payload must declare a supported defaultTriggerKind"
        )
    default_execution_environment = payload.get("defaultExecutionEnvironment")
    if (
        default_execution_environment
        not in OPTIMIZER_JOB_SCHEDULE_EXECUTION_ENVIRONMENTS
    ):
        raise ValueError(
            "optimizer job schedule payload must declare a supported defaultExecutionEnvironment"
        )
    default_scheduler_owner = payload.get("defaultSchedulerOwner")
    if not isinstance(default_scheduler_owner, str) or not default_scheduler_owner:
        raise ValueError(
            "optimizer job schedule payload must declare defaultSchedulerOwner"
        )
    if payload.get("runtimeRole") != OPTIMIZER_JOB_SCHEDULE_RUNTIME_ROLE:
        raise ValueError(
            "optimizer job schedule payload must declare compatibility_rehearsal runtimeRole"
        )
    if (
        payload.get("preferredRecurringRuntime")
        != OPTIMIZER_JOB_SCHEDULE_PREFERRED_RECURRING_RUNTIME
    ):
        raise ValueError(
            "optimizer job schedule payload must declare openclaw_cron as preferredRecurringRuntime"
        )
    if payload.get("intendedUses") != OPTIMIZER_JOB_SCHEDULE_INTENDED_USES:
        raise ValueError(
            "optimizer job schedule payload must declare the committed compatibility intendedUses"
        )
    if not isinstance(payload.get("schedulePlanId"), str) or not payload["schedulePlanId"]:
        raise ValueError("optimizer job schedule payload must declare schedulePlanId")
    if not isinstance(payload.get("generatedAt"), str) or not payload["generatedAt"]:
        raise ValueError("optimizer job schedule payload must declare generatedAt")
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError("optimizer job schedule payload must declare generatedFrom")
    scheduler_rollout_intents = payload.get("schedulerRolloutIntents")
    if not isinstance(scheduler_rollout_intents, list) or not scheduler_rollout_intents:
        raise ValueError(
            "optimizer job schedule payload must declare schedulerRolloutIntents"
        )
    schedules = payload.get("schedules")
    if not isinstance(schedules, list) or not schedules:
        raise ValueError("optimizer job schedule payload must declare schedules")
    expected_count = generated_from.get("scheduleCount")
    if expected_count != len(schedules):
        raise ValueError("optimizer job schedule payload scheduleCount mismatch")
    if generated_from.get("schedulerRolloutIntentCount") != len(
        scheduler_rollout_intents
    ):
        raise ValueError(
            "optimizer job schedule payload schedulerRolloutIntentCount mismatch"
        )

    seen_scheduler_rollout_intents: set[str] = set()
    scheduler_intent_catalog: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(scheduler_rollout_intents):
        if not isinstance(entry, dict):
            raise ValueError(
                "optimizer job schedule schedulerRolloutIntents entries must be objects"
            )
        label = f"schedulerRolloutIntents[{index}]"
        scheduler_rollout_intent = entry.get("schedulerRolloutIntent")
        if (
            not isinstance(scheduler_rollout_intent, str)
            or not scheduler_rollout_intent
        ):
            raise ValueError(f"{label}.schedulerRolloutIntent must be a non-empty string")
        if scheduler_rollout_intent not in OPTIMIZER_JOB_SCHEDULE_ROLLOUT_INTENTS:
            raise ValueError(
                f"{label}.schedulerRolloutIntent must be a supported intent"
            )
        if scheduler_rollout_intent in seen_scheduler_rollout_intents:
            raise ValueError(
                f"duplicate optimizer job schedulerRolloutIntent {scheduler_rollout_intent}"
            )
        seen_scheduler_rollout_intents.add(scheduler_rollout_intent)
        for field_name in (
            "inputRolloutIntent",
            "inputRolloutClass",
            "runtimeProfileRolloutClass",
        ):
            field_value = entry.get(field_name)
            if not isinstance(field_value, str) or not field_value:
                raise ValueError(f"{label}.{field_name} must be a non-empty string")
        window_set_purpose = entry.get("windowSetPurpose")
        if window_set_purpose is not None and (
            not isinstance(window_set_purpose, str) or not window_set_purpose
        ):
            raise ValueError(
                f"{label}.windowSetPurpose must be null or a non-empty string"
            )
        comparison_dimension = entry.get("comparisonDimension")
        if comparison_dimension is not None and (
            not isinstance(comparison_dimension, str) or not comparison_dimension
        ):
            raise ValueError(
                f"{label}.comparisonDimension must be null or a non-empty string"
            )
        scheduler_intent_catalog[scheduler_rollout_intent] = entry

    seen_schedule_ids: set[str] = set()
    for schedule in schedules:
        if not isinstance(schedule, dict):
            raise ValueError("optimizer job schedule entries must be objects")
        schedule_id = schedule.get("scheduleId")
        if not isinstance(schedule_id, str) or not schedule_id:
            raise ValueError("optimizer job schedule entry must declare scheduleId")
        if schedule_id in seen_schedule_ids:
            raise ValueError(f"duplicate optimizer job scheduleId {schedule_id}")
        seen_schedule_ids.add(schedule_id)
        cadence_kind = schedule.get("cadenceKind")
        if cadence_kind not in OPTIMIZER_JOB_SCHEDULE_CADENCE_KINDS:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported cadenceKind"
            )
        job_kind = schedule.get("jobKind")
        if job_kind not in OPTIMIZER_JOB_SCHEDULE_JOB_KINDS:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported jobKind"
            )
        input_mode = schedule.get("defaultInputMode")
        if input_mode not in OPTIMIZER_JOB_SCHEDULE_INPUT_MODES:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported defaultInputMode"
            )
        path_resolution_mode = schedule.get(
            "pathResolutionMode", default_path_resolution_mode
        )
        if path_resolution_mode not in OPTIMIZER_JOB_SCHEDULE_PATH_RESOLUTION_MODES:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported pathResolutionMode"
            )
        output_emission_mode = schedule.get(
            "outputEmissionMode", default_output_emission_mode
        )
        if output_emission_mode not in OPTIMIZER_JOB_SCHEDULE_OUTPUT_EMISSION_MODES:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported outputEmissionMode"
            )
        trigger_kind = schedule.get("defaultTriggerKind", default_trigger_kind)
        if trigger_kind not in OPTIMIZER_JOB_SCHEDULE_TRIGGER_KINDS:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported defaultTriggerKind"
            )
        scheduler_owner = schedule.get(
            "defaultSchedulerOwner", default_scheduler_owner
        )
        if not isinstance(scheduler_owner, str) or not scheduler_owner:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must declare defaultSchedulerOwner"
            )
        execution_environment = schedule.get(
            "defaultExecutionEnvironment", default_execution_environment
        )
        if execution_environment not in OPTIMIZER_JOB_SCHEDULE_EXECUTION_ENVIRONMENTS:
            raise ValueError(
                f"optimizer job schedule {schedule_id} must use a supported defaultExecutionEnvironment"
            )
        for field_name in (
            "entryPoint",
            "rankingContractVersion",
            "rankingContractValidationMode",
            "defaultJobRunId",
            "defaultCycleId",
            "defaultEvalRunId",
            "defaultReportId",
            "defaultGeneratedAt",
        ):
            value = schedule.get(field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} must declare {field_name}"
                )
        default_input_path = schedule.get("defaultInputPath")
        if path_resolution_mode == "repo_relative":
            if not isinstance(default_input_path, str) or not default_input_path:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} must declare defaultInputPath"
                )
        elif default_input_path is not None and (
            not isinstance(default_input_path, str) or not default_input_path
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultInputPath must be null or a non-empty string"
            )
        default_policy_path = schedule.get("defaultPolicyPath")
        if path_resolution_mode == "repo_relative":
            if not isinstance(default_policy_path, str) or not default_policy_path:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} must declare defaultPolicyPath"
                )
        elif default_policy_path is not None and (
            not isinstance(default_policy_path, str) or not default_policy_path
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultPolicyPath must be null or a non-empty string"
            )
        default_output_path = schedule.get("defaultOutputPath")
        if output_emission_mode == "direct_output_path":
            if not isinstance(default_output_path, str) or not default_output_path:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} must declare defaultOutputPath"
                )
        elif default_output_path is not None and (
            not isinstance(default_output_path, str) or not default_output_path
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultOutputPath must be null or a non-empty string"
            )
        default_output_root = schedule.get("defaultOutputRoot", payload.get("defaultOutputRoot"))
        if output_emission_mode == "output_root":
            if not isinstance(default_output_root, str) or not default_output_root:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} must declare defaultOutputRoot"
                )
        elif default_output_root is not None and (
            not isinstance(default_output_root, str) or not default_output_root
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultOutputRoot must be null or a non-empty string"
            )
        output_subdir = schedule.get("outputSubdir")
        if output_emission_mode == "output_root":
            if not isinstance(output_subdir, str) or not output_subdir:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} must declare outputSubdir"
                )
        elif output_subdir is not None and (
            not isinstance(output_subdir, str) or not output_subdir
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} outputSubdir must be null or a non-empty string"
            )
        include_weekly_promotion = schedule.get("includeWeeklyPromotion")
        if not isinstance(include_weekly_promotion, bool):
            raise ValueError(
                f"optimizer job schedule {schedule_id} must declare includeWeeklyPromotion"
            )
        weekly_window_path = schedule.get("defaultWeeklyReviewWindowPath")
        if job_kind == "weekly_optimizer_job" and path_resolution_mode == "repo_relative":
            if not isinstance(weekly_window_path, str) or not weekly_window_path:
                raise ValueError(
                    "weekly optimizer job schedule must declare defaultWeeklyReviewWindowPath"
                )
        elif weekly_window_path is not None and (
            not isinstance(weekly_window_path, str) or not weekly_window_path
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultWeeklyReviewWindowPath must be null or a non-empty string"
            )
        default_input_source_registry_path = schedule.get(
            "defaultInputSourceRegistryPath"
        )
        if default_input_source_registry_path is not None and (
            not isinstance(default_input_source_registry_path, str)
            or not default_input_source_registry_path
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultInputSourceRegistryPath must be null or a non-empty string"
            )
        default_scheduler_rollout_intent = schedule.get("defaultSchedulerRolloutIntent")
        if default_scheduler_rollout_intent is not None and (
            not isinstance(default_scheduler_rollout_intent, str)
            or not default_scheduler_rollout_intent
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultSchedulerRolloutIntent must be null or a non-empty string"
            )
        allowed_scheduler_rollout_intents = schedule.get(
            "allowedSchedulerRolloutIntents"
        )
        normalized_allowed_scheduler_rollout_intents: set[str] | None = None
        if allowed_scheduler_rollout_intents is not None:
            if (
                not isinstance(allowed_scheduler_rollout_intents, list)
                or not allowed_scheduler_rollout_intents
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} allowedSchedulerRolloutIntents must be null or a non-empty list"
                )
            normalized_allowed_scheduler_rollout_intents = set()
            for allowed_index, scheduler_rollout_intent in enumerate(
                allowed_scheduler_rollout_intents
            ):
                if (
                    not isinstance(scheduler_rollout_intent, str)
                    or not scheduler_rollout_intent
                ):
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedSchedulerRolloutIntents[{allowed_index}] must be a non-empty string"
                    )
                if scheduler_rollout_intent not in scheduler_intent_catalog:
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedSchedulerRolloutIntents[{allowed_index}] references unknown scheduler intent"
                    )
                normalized_allowed_scheduler_rollout_intents.add(
                    scheduler_rollout_intent
                )
            if (
                default_scheduler_rollout_intent is not None
                and default_scheduler_rollout_intent
                not in normalized_allowed_scheduler_rollout_intents
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultSchedulerRolloutIntent must be allowed"
                )
        default_runtime_profile_rollout_class = schedule.get(
            "defaultRuntimeProfileRolloutClass"
        )
        if default_runtime_profile_rollout_class is not None and (
            not isinstance(default_runtime_profile_rollout_class, str)
            or not default_runtime_profile_rollout_class
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultRuntimeProfileRolloutClass must be null or a non-empty string"
            )
        default_window_set_purpose = schedule.get("defaultWindowSetPurpose")
        if default_window_set_purpose is not None and (
            not isinstance(default_window_set_purpose, str)
            or not default_window_set_purpose
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultWindowSetPurpose must be null or a non-empty string"
            )
        default_comparison_dimension = schedule.get("defaultComparisonDimension")
        if default_comparison_dimension is not None and (
            not isinstance(default_comparison_dimension, str)
            or not default_comparison_dimension
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultComparisonDimension must be null or a non-empty string"
            )
        for field_name in (
            "allowedRuntimeProfileRolloutClasses",
            "allowedWindowSetPurposes",
            "allowedComparisonDimensions",
        ):
            values = schedule.get(field_name)
            if values is not None:
                if not isinstance(values, list):
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} {field_name} must be null or a list"
                    )
                for value_index, value in enumerate(values):
                    if not isinstance(value, str) or not value:
                        raise ValueError(
                            f"optimizer job schedule {schedule_id} {field_name}[{value_index}] must be a non-empty string"
                        )
        default_input_rollout_class = schedule.get("defaultInputRolloutClass")
        if default_input_rollout_class is not None and (
            not isinstance(default_input_rollout_class, str)
            or not default_input_rollout_class
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultInputRolloutClass must be null or a non-empty string"
            )
        default_input_rollout_intent = schedule.get("defaultInputRolloutIntent")
        if default_input_rollout_intent is not None and (
            not isinstance(default_input_rollout_intent, str)
            or not default_input_rollout_intent
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultInputRolloutIntent must be null or a non-empty string"
            )
        for field_name in (
            "defaultInputRolloutSelectionSource",
            "defaultInputRolloutIntentSelectionSource",
            "defaultInputRolloutClassSelectionSource",
        ):
            field_value = schedule.get(field_name)
            if field_value is not None and (
                not isinstance(field_value, str) or not field_value
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} {field_name} must be null or a non-empty string"
                )
        default_input_source_lane = schedule.get("defaultInputSourceLane")
        if default_input_source_lane is not None and (
            not isinstance(default_input_source_lane, str)
            or not default_input_source_lane
        ):
            raise ValueError(
                f"optimizer job schedule {schedule_id} defaultInputSourceLane must be null or a non-empty string"
            )
        allowed_input_rollout_intents = schedule.get("allowedInputRolloutIntents")
        if allowed_input_rollout_intents is not None:
            if (
                not isinstance(allowed_input_rollout_intents, list)
                or not allowed_input_rollout_intents
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} allowedInputRolloutIntents must be null or a non-empty list"
                )
            normalized_allowed_intents: set[str] = set()
            for allowed_index, rollout_intent in enumerate(allowed_input_rollout_intents):
                if not isinstance(rollout_intent, str) or not rollout_intent:
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedInputRolloutIntents[{allowed_index}] must be a non-empty string"
                    )
                normalized_allowed_intents.add(rollout_intent)
            if (
                default_input_rollout_intent is not None
                and default_input_rollout_intent not in normalized_allowed_intents
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultInputRolloutIntent must be allowed"
                )
        allowed_input_rollout_classes = schedule.get("allowedInputRolloutClasses")
        if allowed_input_rollout_classes is not None:
            if (
                not isinstance(allowed_input_rollout_classes, list)
                or not allowed_input_rollout_classes
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} allowedInputRolloutClasses must be null or a non-empty list"
                )
            normalized_allowed: set[str] = set()
            for allowed_index, rollout_class in enumerate(allowed_input_rollout_classes):
                if not isinstance(rollout_class, str) or not rollout_class:
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedInputRolloutClasses[{allowed_index}] must be a non-empty string"
                    )
                normalized_allowed.add(rollout_class)
            if (
                default_input_rollout_class is not None
                and default_input_rollout_class not in normalized_allowed
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultInputRolloutClass must be allowed"
                )
        if default_scheduler_rollout_intent is not None:
            scheduler_intent_entry = scheduler_intent_catalog.get(
                default_scheduler_rollout_intent
            )
            if scheduler_intent_entry is None:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultSchedulerRolloutIntent must exist in schedulerRolloutIntents"
                )
            expected_input_rollout_intent = scheduler_intent_entry["inputRolloutIntent"]
            expected_input_rollout_class = scheduler_intent_entry["inputRolloutClass"]
            if (
                default_input_rollout_intent is not None
                and default_input_rollout_intent != expected_input_rollout_intent
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultInputRolloutIntent must match defaultSchedulerRolloutIntent mapping"
                )
            if (
                default_input_rollout_class is not None
                and default_input_rollout_class != expected_input_rollout_class
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultInputRolloutClass must match defaultSchedulerRolloutIntent mapping"
                )
            expected_runtime_profile_rollout_class = scheduler_intent_entry.get(
                "runtimeProfileRolloutClass"
            )
            if (
                default_runtime_profile_rollout_class is not None
                and default_runtime_profile_rollout_class
                != expected_runtime_profile_rollout_class
            ):
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultRuntimeProfileRolloutClass must match defaultSchedulerRolloutIntent mapping"
                )
            expected_window_set_purpose = scheduler_intent_entry.get(
                "windowSetPurpose"
            )
            if default_window_set_purpose != expected_window_set_purpose:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultWindowSetPurpose must match defaultSchedulerRolloutIntent mapping"
                )
            expected_comparison_dimension = scheduler_intent_entry.get(
                "comparisonDimension"
            )
            if default_comparison_dimension != expected_comparison_dimension:
                raise ValueError(
                    f"optimizer job schedule {schedule_id} defaultComparisonDimension must match defaultSchedulerRolloutIntent mapping"
                )
            if normalized_allowed_scheduler_rollout_intents is not None:
                expected_allowed_input_rollout_intents = {
                    scheduler_intent_catalog[scheduler_rollout_intent][
                        "inputRolloutIntent"
                    ]
                    for scheduler_rollout_intent in normalized_allowed_scheduler_rollout_intents
                }
                expected_allowed_input_rollout_classes = {
                    scheduler_intent_catalog[scheduler_rollout_intent][
                        "inputRolloutClass"
                    ]
                    for scheduler_rollout_intent in normalized_allowed_scheduler_rollout_intents
                }
                if allowed_input_rollout_intents is not None and set(
                    allowed_input_rollout_intents
                ) != expected_allowed_input_rollout_intents:
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedInputRolloutIntents must match allowedSchedulerRolloutIntents"
                    )
                if allowed_input_rollout_classes is not None and set(
                    allowed_input_rollout_classes
                ) != expected_allowed_input_rollout_classes:
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedInputRolloutClasses must match allowedSchedulerRolloutIntents"
                    )
                expected_allowed_runtime_profile_rollout_classes = sorted(
                    {
                        scheduler_intent_catalog[scheduler_rollout_intent][
                            "runtimeProfileRolloutClass"
                        ]
                        for scheduler_rollout_intent in normalized_allowed_scheduler_rollout_intents
                        if isinstance(
                            scheduler_intent_catalog[scheduler_rollout_intent].get(
                                "runtimeProfileRolloutClass"
                            ),
                            str,
                        )
                        and scheduler_intent_catalog[scheduler_rollout_intent].get(
                            "runtimeProfileRolloutClass"
                        )
                    }
                )
                expected_allowed_window_set_purposes = sorted(
                    {
                        scheduler_intent_catalog[scheduler_rollout_intent][
                            "windowSetPurpose"
                        ]
                        for scheduler_rollout_intent in normalized_allowed_scheduler_rollout_intents
                        if isinstance(
                            scheduler_intent_catalog[scheduler_rollout_intent].get(
                                "windowSetPurpose"
                            ),
                            str,
                        )
                        and scheduler_intent_catalog[scheduler_rollout_intent].get(
                            "windowSetPurpose"
                        )
                    }
                )
                expected_allowed_comparison_dimensions = sorted(
                    {
                        scheduler_intent_catalog[scheduler_rollout_intent][
                            "comparisonDimension"
                        ]
                        for scheduler_rollout_intent in normalized_allowed_scheduler_rollout_intents
                        if isinstance(
                            scheduler_intent_catalog[scheduler_rollout_intent].get(
                                "comparisonDimension"
                            ),
                            str,
                        )
                        and scheduler_intent_catalog[scheduler_rollout_intent].get(
                            "comparisonDimension"
                        )
                    }
                )
                if schedule.get("allowedRuntimeProfileRolloutClasses") not in (
                    None,
                    expected_allowed_runtime_profile_rollout_classes,
                ):
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedRuntimeProfileRolloutClasses must match allowedSchedulerRolloutIntents"
                    )
                if schedule.get("allowedWindowSetPurposes") not in (
                    None,
                    expected_allowed_window_set_purposes,
                ):
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedWindowSetPurposes must match allowedSchedulerRolloutIntents"
                    )
                if schedule.get("allowedComparisonDimensions") not in (
                    None,
                    expected_allowed_comparison_dimensions,
                ):
                    raise ValueError(
                        f"optimizer job schedule {schedule_id} allowedComparisonDimensions must match allowedSchedulerRolloutIntents"
                    )
        if job_kind == "daily_optimizer_job" and include_weekly_promotion:
            raise ValueError(
                "daily optimizer job schedule cannot set includeWeeklyPromotion=true"
            )
        if job_kind == "weekly_optimizer_job" and not include_weekly_promotion:
            raise ValueError(
                "weekly optimizer job schedule cannot set includeWeeklyPromotion=false"
            )


def load_optimizer_job_schedule(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"optimizer job schedule not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"optimizer job schedule is not valid JSON: {path}") from exc
    validate_optimizer_job_schedule_payload(payload)
    return payload


def resolve_optimizer_job_scheduler_rollout_intent(
    payload: dict[str, Any],
    *,
    schedule_id: str | None = None,
    explicit_scheduler_rollout_intent: str | None = None,
    explicit_rollout_class: str | None = None,
) -> dict[str, str]:
    validate_optimizer_job_schedule_payload(payload)
    schedule_catalog = {
        entry["scheduleId"]: entry
        for entry in payload.get("schedules", [])
        if isinstance(entry, dict)
    }
    intent_catalog = {
        entry["schedulerRolloutIntent"]: entry
        for entry in payload.get("schedulerRolloutIntents", [])
        if isinstance(entry, dict)
    }
    if explicit_scheduler_rollout_intent is not None:
        if explicit_scheduler_rollout_intent not in intent_catalog:
            raise ValueError(
                f"optimizer job schedulerRolloutIntent not found: {explicit_scheduler_rollout_intent!r}"
            )
        intent_entry = intent_catalog[explicit_scheduler_rollout_intent]
        if (
            explicit_rollout_class is not None
            and intent_entry.get("inputRolloutClass") != explicit_rollout_class
        ):
            raise ValueError(
                "optimizer job scheduler rollout intent and rolloutClass must agree when both are provided"
            )
        if schedule_id is not None:
            schedule = schedule_catalog.get(schedule_id)
            if schedule is None:
                raise ValueError(
                    f"optimizer job scheduleId not found: {schedule_id!r}"
                )
            allowed_scheduler_rollout_intents = schedule.get(
                "allowedSchedulerRolloutIntents"
            )
            if (
                isinstance(allowed_scheduler_rollout_intents, list)
                and explicit_scheduler_rollout_intent
                not in allowed_scheduler_rollout_intents
            ):
                raise ValueError(
                    f"optimizer job schedulerRolloutIntent {explicit_scheduler_rollout_intent!r} is not allowed for scheduleId {schedule_id!r}"
                )
        scheduler_rollout_intent = explicit_scheduler_rollout_intent
        selection_source = "explicit_scheduler_intent"
    elif explicit_rollout_class is not None:
        scheduler_rollout_intent = next(
            (
                entry["schedulerRolloutIntent"]
                for entry in intent_catalog.values()
                if entry.get("inputRolloutClass") == explicit_rollout_class
            ),
            None,
        )
        if scheduler_rollout_intent is None:
            raise ValueError(
                f"optimizer job scheduler rollout intent could not be mapped from rolloutClass {explicit_rollout_class!r}"
            )
        selection_source = "mapped_from_explicit_rollout_class"
    else:
        if schedule_id is None:
            raise ValueError(
                "optimizer job scheduler rollout intent resolution requires schedule_id when no explicit override is provided"
            )
        schedule = schedule_catalog.get(schedule_id)
        if schedule is None:
            raise ValueError(f"optimizer job scheduleId not found: {schedule_id!r}")
        scheduler_rollout_intent = schedule.get("defaultSchedulerRolloutIntent")
        if not isinstance(scheduler_rollout_intent, str) or not scheduler_rollout_intent:
            raise ValueError(
                f"optimizer job schedule {schedule_id!r} is missing defaultSchedulerRolloutIntent"
            )
        selection_source = "schedule_default"
    entry = intent_catalog.get(scheduler_rollout_intent)
    if entry is None:
        raise ValueError(
            f"optimizer job scheduler rollout intent catalog is missing {scheduler_rollout_intent!r}"
        )
    return {
        "schedulerRolloutIntent": scheduler_rollout_intent,
        "selectionSource": selection_source,
        "inputRolloutIntent": entry["inputRolloutIntent"],
        "inputRolloutClass": entry["inputRolloutClass"],
        "runtimeProfileRolloutClass": entry["runtimeProfileRolloutClass"],
        "windowSetPurpose": entry.get("windowSetPurpose"),
        "comparisonDimension": entry.get("comparisonDimension"),
    }


def resolve_optimizer_job_schedule_execution_policy(
    payload: dict[str, Any],
    *,
    input_rollout_policy_payload: dict[str, Any] | None,
    schedule_id: str,
    explicit_scheduler_rollout_intent: str | None = None,
    explicit_rollout_class: str | None = None,
) -> dict[str, str | None]:
    scheduler_selection = resolve_optimizer_job_scheduler_rollout_intent(
        payload,
        schedule_id=schedule_id,
        explicit_scheduler_rollout_intent=explicit_scheduler_rollout_intent,
        explicit_rollout_class=explicit_rollout_class,
    )
    if input_rollout_policy_payload is None:
        return {
            **scheduler_selection,
            "sourceLane": None,
            "inputLaneSelectionSource": None,
            "inputRolloutStrategy": None,
            "inputRolloutIntentSelectionSource": None,
            "inputRolloutClassSelectionSource": None,
        }

    if explicit_rollout_class is not None:
        rollout_selection = resolve_optimizer_input_rollout_selection(
            input_rollout_policy_payload,
            schedule_id=schedule_id,
            explicit_rollout_class=explicit_rollout_class,
        )
    elif explicit_scheduler_rollout_intent is not None:
        rollout_selection = resolve_optimizer_input_rollout_selection(
            input_rollout_policy_payload,
            schedule_id=schedule_id,
            explicit_rollout_intent=scheduler_selection["inputRolloutIntent"],
        )
    else:
        rollout_selection = resolve_optimizer_input_rollout_selection(
            input_rollout_policy_payload,
            schedule_id=schedule_id,
        )

    if rollout_selection["rolloutIntent"] != scheduler_selection["inputRolloutIntent"]:
        raise ValueError(
            "optimizer job scheduler rollout intent resolved to an input rollout intent that does not match the input rollout policy selection"
        )
    if rollout_selection["rolloutClass"] != scheduler_selection["inputRolloutClass"]:
        raise ValueError(
            "optimizer job scheduler rollout intent resolved to an input rollout class that does not match the input rollout policy selection"
        )

    return {
        **scheduler_selection,
        "sourceLane": rollout_selection["sourceLane"],
        "inputLaneSelectionSource": rollout_selection["selectionSource"],
        "inputRolloutStrategy": rollout_selection["rolloutStrategy"],
        "inputRolloutIntentSelectionSource": rollout_selection[
            "rolloutIntentSelectionSource"
        ],
        "inputRolloutClassSelectionSource": rollout_selection[
            "rolloutClassSelectionSource"
        ],
    }
