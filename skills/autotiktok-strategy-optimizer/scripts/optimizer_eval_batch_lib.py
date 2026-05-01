#!/usr/bin/env python3
"""
Helpers for optimizer eval-batch artifacts and manifests.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from reward_lib import load_json


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SKILL_ROOT.parents[1]

OPTIMIZER_EVAL_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION = (
    "optimizer-eval-batch-manifest.sample.v1"
)
OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSION = "optimizer-eval-batch-manifest.v1"
OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSIONS = {
    OPTIMIZER_EVAL_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSION,
}

COMPARISON_DIMENSIONS = (
    "mode",
    "rankingProfileId",
    "rankingSnapshotId",
    "evaluationWindow",
    "weeklyDecision",
    "challengerInputKind",
    "historyBatchLabel",
    "historyWindowLabel",
    "scenarioLabel",
)

ENTRY_METADATA_KEYS = (
    "historyBatchLabel",
    "historyWindowLabel",
    "scenarioLabel",
)

ENTRY_SUMMARY_OVERRIDE_KEYS = {
    "evaluationWindow",
    "topicReward",
    "performanceReward",
    "performanceWeight",
    "combinedReward",
    "postCoverageRate",
    "rejectedCount",
    "shadowLeaderProfileId",
    "challengerInputKind",
    "weeklyDecision",
    "selectedChallengerProfileId",
}


def classify_runtime_source_kind(source: dict[str, Any]) -> str:
    if isinstance(source.get("inputManifestPath"), str) and source.get("inputManifestPath"):
        return "input_manifest"
    if isinstance(source.get("inputBundlePath"), str) and source.get("inputBundlePath"):
        return "input_bundle"
    if isinstance(source.get("inputOfflineCyclePath"), str) and source.get("inputOfflineCyclePath"):
        return "offline_cycle"
    return "unknown"


def _round_metric(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _count_by(values: list[str | None]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if value is None:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def _sorted_unique(values: list[str | None]) -> list[str]:
    return sorted({value for value in values if isinstance(value, str) and value})


def _sorted_unique_nested(values: list[list[str] | None]) -> list[str]:
    flattened: set[str] = set()
    for group in values:
        if not isinstance(group, list):
            continue
        for value in group:
            if isinstance(value, str) and value:
                flattened.add(value)
    return sorted(flattened)


def _average(values: list[float | None]) -> float | None:
    numeric_values = [float(value) for value in values if value is not None]
    if not numeric_values:
        return None
    return round(sum(numeric_values) / len(numeric_values), 6)


def _select_best_eval_run(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    return max(
        items,
        key=lambda item: (
            float(item.get("combinedReward") or 0.0),
            float(item.get("topicReward") or 0.0),
            item.get("evalRunId") or "",
        ),
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


def _resolve_path_from_label(label: str, *, manifest_path: Path) -> Path:
    candidate = Path(label)
    if candidate.is_absolute():
        return candidate
    repo_candidate = REPO_ROOT / candidate
    if repo_candidate.exists():
        return repo_candidate
    return (manifest_path.parent / candidate).resolve()


def _ensure_dict(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if isinstance(value, dict):
        return value
    replacement: dict[str, Any] = {}
    parent[key] = replacement
    return replacement


def build_optimizer_eval_batch_manifest_entry(
    *,
    eval_run_path: Path | None = None,
    path_style: str = "repo",
    entry_id: str | None = None,
    eval_run_id: str | None = None,
    generated_at: str | None = None,
    mode: str | None = None,
    cycle_id: str | None = None,
    report_id: str | None = None,
    history_batch_label: str | None = None,
    history_window_label: str | None = None,
    scenario_label: str | None = None,
    summary_overrides: dict[str, Any] | None = None,
    runtime_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if eval_run_path is not None:
        payload["path"] = _path_label(eval_run_path, style=path_style)
    if runtime_source is not None:
        payload["runtimeSource"] = runtime_source
    if entry_id is not None:
        payload["entryId"] = entry_id
    if eval_run_id is not None:
        payload["evalRunId"] = eval_run_id
    if generated_at is not None:
        payload["generatedAt"] = generated_at
    if mode is not None:
        payload["mode"] = mode
    if cycle_id is not None:
        payload["cycleId"] = cycle_id
    if report_id is not None:
        payload["reportId"] = report_id
    if history_batch_label is not None:
        payload["historyBatchLabel"] = history_batch_label
    if history_window_label is not None:
        payload["historyWindowLabel"] = history_window_label
    if scenario_label is not None:
        payload["scenarioLabel"] = scenario_label
    if summary_overrides:
        payload["summaryOverrides"] = summary_overrides
    return payload


def build_optimizer_eval_batch_manifest_payload(
    *,
    eval_run_paths: list[Path] | None,
    schema_version: str,
    manifest_id: str,
    generated_at: str,
    comparison_dimension: str,
    batch_window_label: str,
    path_style: str,
    eval_run_entries: list[dict[str, Any]] | None = None,
    window_set_purpose: str | None = None,
    window_set_batch_type: str | None = None,
    window_set_batch_type_selection_source: str | None = None,
    comparison_dimension_selection_source: str | None = None,
    runtime_profile_purpose_policy_id: str | None = None,
    runtime_profile_purpose_template_id: str | None = None,
    runtime_profile_purpose_template_family_id: str | None = None,
    runtime_profile_planner_metadata_contract_family_id: str | None = None,
    runtime_profile_planner_metadata_policy_id: str | None = None,
    runtime_profile_planner_metadata_contract_id: str | None = None,
) -> dict[str, Any]:
    payload = {
        "schemaVersion": schema_version,
        "manifestId": manifest_id,
        "generatedAt": generated_at,
        "comparisonDimension": comparison_dimension,
        "batchWindowLabel": batch_window_label,
        "generatedFrom": {
            "evalRunCount": len(eval_run_entries or eval_run_paths or []),
        },
    }
    if window_set_purpose is not None:
        payload["windowSetPurpose"] = window_set_purpose
        payload["generatedFrom"]["windowSetPurpose"] = window_set_purpose
    if window_set_batch_type is not None:
        payload["windowSetBatchType"] = window_set_batch_type
        payload["generatedFrom"]["windowSetBatchType"] = window_set_batch_type
    if window_set_batch_type_selection_source is not None:
        payload["windowSetBatchTypeSelectionSource"] = (
            window_set_batch_type_selection_source
        )
        payload["generatedFrom"]["windowSetBatchTypeSelectionSource"] = (
            window_set_batch_type_selection_source
        )
    if comparison_dimension_selection_source is not None:
        payload["comparisonDimensionSelectionSource"] = (
            comparison_dimension_selection_source
        )
        payload["generatedFrom"]["comparisonDimensionSelectionSource"] = (
            comparison_dimension_selection_source
        )
    if runtime_profile_purpose_policy_id is not None:
        payload["runtimeProfilePurposePolicyId"] = runtime_profile_purpose_policy_id
        payload["generatedFrom"]["runtimeProfilePurposePolicyId"] = (
            runtime_profile_purpose_policy_id
        )
    if runtime_profile_purpose_template_id is not None:
        payload["runtimeProfilePurposeTemplateId"] = (
            runtime_profile_purpose_template_id
        )
        payload["generatedFrom"]["runtimeProfilePurposeTemplateId"] = (
            runtime_profile_purpose_template_id
        )
    if runtime_profile_purpose_template_family_id is not None:
        payload["runtimeProfilePurposeTemplateFamilyId"] = (
            runtime_profile_purpose_template_family_id
        )
        payload["generatedFrom"]["runtimeProfilePurposeTemplateFamilyId"] = (
            runtime_profile_purpose_template_family_id
        )
    if runtime_profile_planner_metadata_contract_family_id is not None:
        payload["runtimeProfilePlannerMetadataContractFamilyId"] = (
            runtime_profile_planner_metadata_contract_family_id
        )
        payload["generatedFrom"]["runtimeProfilePlannerMetadataContractFamilyId"] = (
            runtime_profile_planner_metadata_contract_family_id
        )
    if runtime_profile_planner_metadata_policy_id is not None:
        payload["runtimeProfilePlannerMetadataPolicyId"] = (
            runtime_profile_planner_metadata_policy_id
        )
        payload["generatedFrom"]["runtimeProfilePlannerMetadataPolicyId"] = (
            runtime_profile_planner_metadata_policy_id
        )
    if runtime_profile_planner_metadata_contract_id is not None:
        payload["runtimeProfilePlannerMetadataContractId"] = (
            runtime_profile_planner_metadata_contract_id
        )
        payload["generatedFrom"]["runtimeProfilePlannerMetadataContractId"] = (
            runtime_profile_planner_metadata_contract_id
        )
    if eval_run_entries is not None:
        payload["evalRunEntries"] = eval_run_entries
    else:
        payload["evalRunPaths"] = [
            _path_label(path, style=path_style) for path in (eval_run_paths or [])
        ]
    return payload


def _validate_eval_run_entry(entry: dict[str, Any], *, index: int) -> None:
    label = f"optimizer eval batch manifest evalRunEntries[{index}]"
    path = entry.get("path")
    runtime_source = entry.get("runtimeSource")
    has_path = isinstance(path, str) and bool(path)
    has_runtime_source = isinstance(runtime_source, dict) and bool(runtime_source)
    if has_path == has_runtime_source:
        raise ValueError(
            f"{label} must include exactly one source: `path` or `runtimeSource`"
        )
    if has_path:
        if not isinstance(path, str) or not path:
            raise ValueError(f"{label}.path must be a non-empty string")
    else:
        _validate_runtime_source(runtime_source, label=label)
    for key in (
        "entryId",
        "evalRunId",
        "generatedAt",
        "mode",
        "cycleId",
        "reportId",
        *ENTRY_METADATA_KEYS,
    ):
        value = entry.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label}.{key} must be a non-empty string when present")
    summary_overrides = entry.get("summaryOverrides")
    if summary_overrides is None:
        return
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


def _validate_runtime_source(source: dict[str, Any], *, label: str) -> None:
    input_keys = (
        "inputManifestPath",
        "inputBundlePath",
        "inputOfflineCyclePath",
    )
    present_input_keys = [
        key for key in input_keys if isinstance(source.get(key), str) and source.get(key)
    ]
    if len(present_input_keys) != 1:
        allowed = ", ".join(input_keys)
        raise ValueError(
            f"{label}.runtimeSource must include exactly one primary input path from [{allowed}]"
        )
    include_weekly_promotion = source.get("includeWeeklyPromotion")
    if not isinstance(include_weekly_promotion, bool):
        raise ValueError(
            f"{label}.runtimeSource.includeWeeklyPromotion must be a boolean"
        )
    runtime_source_id = source.get("runtimeSourceId")
    if runtime_source_id is not None and (
        not isinstance(runtime_source_id, str) or not runtime_source_id
    ):
        raise ValueError(
            f"{label}.runtimeSource.runtimeSourceId must be a non-empty string when present"
        )
    for key in (
        "rankingContractVersion",
        "rankingContractValidationMode",
        "rankingInputPath",
        "contextInputPath",
        "backfillsInputPath",
        "performanceInputPath",
        "challengerInputPath",
        "policyPath",
    ):
        value = source.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value:
            raise ValueError(
                f"{label}.runtimeSource.{key} must be a non-empty string when present"
            )


def validate_optimizer_eval_batch_manifest_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_EVAL_BATCH_MANIFEST_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer eval batch manifest schemaVersion must be one of [{allowed}], got {schema_version!r}"
        )
    comparison_dimension = payload.get("comparisonDimension")
    if comparison_dimension not in COMPARISON_DIMENSIONS:
        allowed = ", ".join(COMPARISON_DIMENSIONS)
        raise ValueError(
            "optimizer eval batch manifest comparisonDimension must be one of "
            f"[{allowed}], got {comparison_dimension!r}"
        )
    batch_window_label = payload.get("batchWindowLabel")
    if not isinstance(batch_window_label, str) or not batch_window_label:
        raise ValueError(
            "optimizer eval batch manifest batchWindowLabel must be a non-empty string"
        )
    window_set_purpose = payload.get("windowSetPurpose")
    if window_set_purpose is not None and (
        not isinstance(window_set_purpose, str) or not window_set_purpose
    ):
        raise ValueError(
            "optimizer eval batch manifest windowSetPurpose must be a non-empty string when present"
        )
    window_set_batch_type = payload.get("windowSetBatchType")
    if window_set_batch_type is not None and (
        not isinstance(window_set_batch_type, str) or not window_set_batch_type
    ):
        raise ValueError(
            "optimizer eval batch manifest windowSetBatchType must be a non-empty string when present"
        )
    window_set_batch_type_selection_source = payload.get(
        "windowSetBatchTypeSelectionSource"
    )
    if window_set_batch_type_selection_source is not None and (
        not isinstance(window_set_batch_type_selection_source, str)
        or not window_set_batch_type_selection_source
    ):
        raise ValueError(
            "optimizer eval batch manifest windowSetBatchTypeSelectionSource must be a non-empty string when present"
        )
    comparison_dimension_selection_source = payload.get(
        "comparisonDimensionSelectionSource"
    )
    if comparison_dimension_selection_source is not None and (
        not isinstance(comparison_dimension_selection_source, str)
        or not comparison_dimension_selection_source
    ):
        raise ValueError(
            "optimizer eval batch manifest comparisonDimensionSelectionSource must be a non-empty string when present"
        )
    runtime_profile_purpose_policy_id = payload.get("runtimeProfilePurposePolicyId")
    if runtime_profile_purpose_policy_id is not None and (
        not isinstance(runtime_profile_purpose_policy_id, str)
        or not runtime_profile_purpose_policy_id
    ):
        raise ValueError(
            "optimizer eval batch manifest runtimeProfilePurposePolicyId must be a non-empty string when present"
        )
    runtime_profile_purpose_template_id = payload.get(
        "runtimeProfilePurposeTemplateId"
    )
    if runtime_profile_purpose_template_id is not None and (
        not isinstance(runtime_profile_purpose_template_id, str)
        or not runtime_profile_purpose_template_id
    ):
        raise ValueError(
            "optimizer eval batch manifest runtimeProfilePurposeTemplateId must be a non-empty string when present"
        )
    runtime_profile_purpose_template_family_id = payload.get(
        "runtimeProfilePurposeTemplateFamilyId"
    )
    if runtime_profile_purpose_template_family_id is not None and (
        not isinstance(runtime_profile_purpose_template_family_id, str)
        or not runtime_profile_purpose_template_family_id
    ):
        raise ValueError(
            "optimizer eval batch manifest runtimeProfilePurposeTemplateFamilyId must be a non-empty string when present"
        )
    runtime_profile_planner_metadata_contract_family_id = payload.get(
        "runtimeProfilePlannerMetadataContractFamilyId"
    )
    if runtime_profile_planner_metadata_contract_family_id is not None and (
        not isinstance(runtime_profile_planner_metadata_contract_family_id, str)
        or not runtime_profile_planner_metadata_contract_family_id
    ):
        raise ValueError(
            "optimizer eval batch manifest runtimeProfilePlannerMetadataContractFamilyId must be a non-empty string when present"
        )
    runtime_profile_planner_metadata_policy_id = payload.get(
        "runtimeProfilePlannerMetadataPolicyId"
    )
    if runtime_profile_planner_metadata_policy_id is not None and (
        not isinstance(runtime_profile_planner_metadata_policy_id, str)
        or not runtime_profile_planner_metadata_policy_id
    ):
        raise ValueError(
            "optimizer eval batch manifest runtimeProfilePlannerMetadataPolicyId must be a non-empty string when present"
        )
    runtime_profile_planner_metadata_contract_id = payload.get(
        "runtimeProfilePlannerMetadataContractId"
    )
    if runtime_profile_planner_metadata_contract_id is not None and (
        not isinstance(runtime_profile_planner_metadata_contract_id, str)
        or not runtime_profile_planner_metadata_contract_id
    ):
        raise ValueError(
            "optimizer eval batch manifest runtimeProfilePlannerMetadataContractId must be a non-empty string when present"
        )

    eval_run_paths = payload.get("evalRunPaths")
    eval_run_entries = payload.get("evalRunEntries")
    has_paths = isinstance(eval_run_paths, list) and bool(eval_run_paths)
    has_entries = isinstance(eval_run_entries, list) and bool(eval_run_entries)
    if has_paths == has_entries:
        raise ValueError(
            "optimizer eval batch manifest must include exactly one non-empty input list: `evalRunPaths` or `evalRunEntries`"
        )
    if has_paths:
        for index, value in enumerate(eval_run_paths):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"optimizer eval batch manifest evalRunPaths[{index}] must be a non-empty string"
                )
        return
    for index, value in enumerate(eval_run_entries):
        if not isinstance(value, dict):
            raise ValueError(
                f"optimizer eval batch manifest evalRunEntries[{index}] must be an object"
            )
        _validate_eval_run_entry(value, index=index)


def _apply_eval_run_entry_overrides(
    *,
    base_eval_run: dict[str, Any],
    entry: dict[str, Any],
) -> dict[str, Any]:
    payload = deepcopy(base_eval_run)
    generated_from = _ensure_dict(payload, "generatedFrom")
    summary = _ensure_dict(payload, "summary")
    metrics = _ensure_dict(payload, "metrics")
    artifacts = _ensure_dict(payload, "artifacts")
    offline_cycle = _ensure_dict(artifacts, "offlineCycle")
    offline_summary = _ensure_dict(offline_cycle, "summary")
    offline_generated_from = _ensure_dict(offline_cycle, "generatedFrom")
    offline_artifacts = _ensure_dict(offline_cycle, "artifacts")
    daily_review = _ensure_dict(offline_artifacts, "dailyReview")
    daily_generated_from = _ensure_dict(daily_review, "generatedFrom")
    weekly_promotion = offline_artifacts.get("weeklyPromotion")

    eval_run_id = entry.get("evalRunId")
    if isinstance(eval_run_id, str) and eval_run_id:
        payload["evalRunId"] = eval_run_id

    generated_at = entry.get("generatedAt")
    if isinstance(generated_at, str) and generated_at:
        payload["generatedAt"] = generated_at
        offline_cycle["generatedAt"] = generated_at
        daily_review["generatedAt"] = generated_at
        if isinstance(weekly_promotion, dict):
            weekly_promotion["generatedAt"] = generated_at

    mode = entry.get("mode")
    if isinstance(mode, str) and mode:
        payload["mode"] = mode
        offline_cycle["mode"] = mode

    cycle_id = entry.get("cycleId")
    if isinstance(cycle_id, str) and cycle_id:
        offline_cycle["cycleId"] = cycle_id
        generated_from["optimizerOfflineCycleId"] = cycle_id

    report_id = entry.get("reportId")
    if isinstance(report_id, str) and report_id:
        daily_review["reportId"] = report_id
        if isinstance(weekly_promotion, dict):
            weekly_promotion["sourceReportId"] = report_id

    for metadata_key in ENTRY_METADATA_KEYS:
        metadata_value = entry.get(metadata_key)
        if not isinstance(metadata_value, str) or not metadata_value:
            continue
        generated_from[metadata_key] = metadata_value
        offline_generated_from[metadata_key] = metadata_value
        daily_generated_from[metadata_key] = metadata_value
        if isinstance(weekly_promotion, dict):
            weekly_generated_from = _ensure_dict(weekly_promotion, "generatedFrom")
            weekly_generated_from[
                f"dailyReview{metadata_key[0].upper()}{metadata_key[1:]}"
            ] = metadata_value

    summary_overrides = entry.get("summaryOverrides")
    if not isinstance(summary_overrides, dict):
        return payload

    topic_breakdown = metrics.get("topicRewardBreakdown")
    combined_breakdown = metrics.get("combinedRewardBreakdown")
    challenger_review = metrics.get("challengerReview")
    ranking_review = metrics.get("rankingReview")
    daily_topic_breakdown = daily_review.get("topicRewardBreakdown")
    daily_combined_breakdown = daily_review.get("combinedRewardBreakdown")
    daily_challenger_review = daily_review.get("challengerReview")
    daily_ranking_review = daily_review.get("rankingReview")

    for key, value in summary_overrides.items():
        summary[key] = value
        offline_summary[key] = value
        if key == "evaluationWindow":
            daily_review["evaluationWindow"] = value
            if isinstance(topic_breakdown, dict):
                topic_breakdown["evaluationWindow"] = value
            if isinstance(combined_breakdown, dict):
                combined_breakdown["evaluationWindow"] = value
            if isinstance(daily_topic_breakdown, dict):
                daily_topic_breakdown["evaluationWindow"] = value
            if isinstance(daily_combined_breakdown, dict):
                daily_combined_breakdown["evaluationWindow"] = value
            if isinstance(challenger_review, dict):
                challenger_review["evaluationWindow"] = value
            if isinstance(daily_challenger_review, dict):
                daily_challenger_review["evaluationWindow"] = value
        elif key == "topicReward":
            if isinstance(topic_breakdown, dict):
                topic_breakdown["topicReward"] = value
            if isinstance(daily_topic_breakdown, dict):
                daily_topic_breakdown["topicReward"] = value
        elif key in {
            "performanceReward",
            "performanceWeight",
            "combinedReward",
            "postCoverageRate",
        }:
            if isinstance(combined_breakdown, dict):
                combined_breakdown[key] = value
            if isinstance(daily_combined_breakdown, dict):
                daily_combined_breakdown[key] = value
        elif key == "rejectedCount":
            if isinstance(ranking_review, dict):
                ranking_review["rejectedCount"] = value
            if isinstance(daily_ranking_review, dict):
                daily_ranking_review["rejectedCount"] = value
        elif key == "shadowLeaderProfileId":
            if isinstance(challenger_review, dict):
                challenger_review["leaderProfileId"] = value
            if isinstance(daily_challenger_review, dict):
                daily_challenger_review["leaderProfileId"] = value
            shadow_leaderboard = daily_review.get("shadowLeaderboard")
            if isinstance(shadow_leaderboard, list) and shadow_leaderboard:
                first_row = shadow_leaderboard[0]
                if isinstance(first_row, dict):
                    first_row["profileId"] = value
        elif key == "challengerInputKind":
            generated_from["challengerInputKind"] = value
            offline_generated_from["challengerInputKind"] = value
            daily_generated_from["challengerInputKind"] = value
            if isinstance(challenger_review, dict):
                challenger_review["inputKind"] = value
            if isinstance(daily_challenger_review, dict):
                daily_challenger_review["inputKind"] = value
        elif key == "weeklyDecision" and isinstance(weekly_promotion, dict):
            weekly_promotion["decision"] = value
        elif (
            key == "selectedChallengerProfileId"
            and isinstance(weekly_promotion, dict)
        ):
            weekly_promotion["selectedChallengerProfileId"] = value
    return payload


def _resolve_optional_runtime_source_path(
    source: dict[str, Any], key: str, *, manifest_path: Path
) -> Path | None:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        return None
    return _resolve_path_from_label(value, manifest_path=manifest_path)


def _build_eval_run_from_runtime_source(
    *,
    entry: dict[str, Any],
    runtime_source: dict[str, Any],
    manifest_path: Path,
) -> dict[str, Any]:
    from build_optimizer_eval_run import build_eval_run
    from optimizer_lib import DEFAULT_POLICY
    from ranking_optimizer_contract_lib import (
        RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        RANKING_OPTIMIZER_CONTRACT_VERSION,
    )
    from run_offline_optimizer_cycle import (
        DEFAULT_BACKFILLS,
        DEFAULT_CHALLENGER_INPUT,
        DEFAULT_CONTEXT,
        DEFAULT_PERFORMANCE,
        DEFAULT_RANKING_OUTPUT,
    )

    args = SimpleNamespace(
        input_offline_cycle=_resolve_optional_runtime_source_path(
            runtime_source, "inputOfflineCyclePath", manifest_path=manifest_path
        ),
        input_manifest=_resolve_optional_runtime_source_path(
            runtime_source, "inputManifestPath", manifest_path=manifest_path
        ),
        input_bundle=_resolve_optional_runtime_source_path(
            runtime_source, "inputBundlePath", manifest_path=manifest_path
        ),
        ranking_input=_resolve_optional_runtime_source_path(
            runtime_source, "rankingInputPath", manifest_path=manifest_path
        )
        or DEFAULT_RANKING_OUTPUT,
        context_input=_resolve_optional_runtime_source_path(
            runtime_source, "contextInputPath", manifest_path=manifest_path
        )
        or DEFAULT_CONTEXT,
        backfills_input=_resolve_optional_runtime_source_path(
            runtime_source, "backfillsInputPath", manifest_path=manifest_path
        )
        or DEFAULT_BACKFILLS,
        performance_input=_resolve_optional_runtime_source_path(
            runtime_source, "performanceInputPath", manifest_path=manifest_path
        )
        or DEFAULT_PERFORMANCE,
        challenger_input=_resolve_optional_runtime_source_path(
            runtime_source, "challengerInputPath", manifest_path=manifest_path
        )
        or DEFAULT_CHALLENGER_INPUT,
        policy=_resolve_optional_runtime_source_path(
            runtime_source, "policyPath", manifest_path=manifest_path
        )
        or DEFAULT_POLICY,
        ranking_contract_version=runtime_source.get("rankingContractVersion")
        or RANKING_OPTIMIZER_CONTRACT_VERSION,
        ranking_contract_validation_mode=runtime_source.get(
            "rankingContractValidationMode"
        )
        or RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        cycle_id=entry.get("cycleId"),
        eval_run_id=entry.get("evalRunId"),
        report_id=entry.get("reportId"),
        generated_at=entry.get("generatedAt"),
        include_weekly_promotion=runtime_source["includeWeeklyPromotion"],
    )
    payload = build_eval_run(args)
    generated_from = _ensure_dict(payload, "generatedFrom")
    generated_from["evalBatchRuntimeSourceKind"] = classify_runtime_source_kind(
        runtime_source
    )
    runtime_source_id = runtime_source.get("runtimeSourceId")
    if isinstance(runtime_source_id, str) and runtime_source_id:
        generated_from["evalBatchRuntimeSourceId"] = runtime_source_id
    runtime_profile_id = runtime_source.get("runtimeProfileId")
    if isinstance(runtime_profile_id, str) and runtime_profile_id:
        generated_from["evalBatchRuntimeProfileId"] = runtime_profile_id
    runtime_profile_requested_id = runtime_source.get("runtimeProfileRequestedId")
    if (
        isinstance(runtime_profile_requested_id, str)
        and runtime_profile_requested_id
    ):
        generated_from["evalBatchRuntimeProfileRequestedId"] = (
            runtime_profile_requested_id
        )
    runtime_profile_alias_applied = runtime_source.get("runtimeProfileAliasApplied")
    if isinstance(runtime_profile_alias_applied, bool):
        generated_from["evalBatchRuntimeProfileAliasApplied"] = (
            runtime_profile_alias_applied
        )
    runtime_profile_catalog_id = runtime_source.get("runtimeProfileCatalogId")
    if isinstance(runtime_profile_catalog_id, str) and runtime_profile_catalog_id:
        generated_from["evalBatchRuntimeProfileCatalogId"] = runtime_profile_catalog_id
    runtime_profile_catalog_family = runtime_source.get("runtimeProfileCatalogFamily")
    if (
        isinstance(runtime_profile_catalog_family, str)
        and runtime_profile_catalog_family
    ):
        generated_from["evalBatchRuntimeProfileCatalogFamily"] = (
            runtime_profile_catalog_family
        )
    runtime_profile_catalog_version = runtime_source.get(
        "runtimeProfileCatalogVersion"
    )
    if (
        isinstance(runtime_profile_catalog_version, str)
        and runtime_profile_catalog_version
    ):
        generated_from["evalBatchRuntimeProfileCatalogVersion"] = (
            runtime_profile_catalog_version
        )
    runtime_profile_catalog_schema_version = runtime_source.get(
        "runtimeProfileCatalogSchemaVersion"
    )
    if (
        isinstance(runtime_profile_catalog_schema_version, str)
        and runtime_profile_catalog_schema_version
    ):
        generated_from["evalBatchRuntimeProfileCatalogSchemaVersion"] = (
            runtime_profile_catalog_schema_version
        )
    materialization_plan_id = runtime_source.get("materializationPlanId")
    if isinstance(materialization_plan_id, str) and materialization_plan_id:
        generated_from["evalBatchMaterializationPlanId"] = materialization_plan_id
    job_family_group = runtime_source.get("jobFamilyGroup")
    if isinstance(job_family_group, str) and job_family_group:
        generated_from["evalBatchJobFamilyGroup"] = job_family_group
    materialization_profile = runtime_source.get("materializationProfile")
    if isinstance(materialization_profile, str) and materialization_profile:
        generated_from["evalBatchMaterializationProfile"] = materialization_profile
    materialization_strategy = runtime_source.get("materializationStrategy")
    if isinstance(materialization_strategy, str) and materialization_strategy:
        generated_from["evalBatchMaterializationStrategy"] = materialization_strategy
    required_artifact_kinds = runtime_source.get("requiredArtifactKinds")
    if isinstance(required_artifact_kinds, list):
        generated_from["evalBatchRequiredArtifactKinds"] = [
            value
            for value in required_artifact_kinds
            if isinstance(value, str) and value
        ]
    upstream_job_families = runtime_source.get("upstreamJobFamilies")
    if isinstance(upstream_job_families, list):
        generated_from["evalBatchUpstreamJobFamilies"] = [
            value for value in upstream_job_families if isinstance(value, str) and value
        ]
    plan_include_weekly_promotion = runtime_source.get("planIncludeWeeklyPromotion")
    if isinstance(plan_include_weekly_promotion, bool):
        generated_from["evalBatchPlanIncludeWeeklyPromotion"] = (
            plan_include_weekly_promotion
        )
    return payload


def load_optimizer_eval_batch_manifest(
    manifest_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = load_json(manifest_path)
    validate_optimizer_eval_batch_manifest_payload(payload)

    eval_run_paths = payload.get("evalRunPaths")
    if isinstance(eval_run_paths, list) and eval_run_paths:
        resolved_paths = [
            _resolve_path_from_label(path_label, manifest_path=manifest_path)
            for path_label in eval_run_paths
        ]
        return payload, [load_json(path) for path in resolved_paths]

    eval_runs: list[dict[str, Any]] = []
    for entry in payload["evalRunEntries"]:
        runtime_source = entry.get("runtimeSource")
        if isinstance(runtime_source, dict) and runtime_source:
            base_eval_run = _build_eval_run_from_runtime_source(
                entry=entry,
                runtime_source=runtime_source,
                manifest_path=manifest_path,
            )
        else:
            base_path = _resolve_path_from_label(
                entry["path"], manifest_path=manifest_path
            )
            base_eval_run = load_json(base_path)
        eval_runs.append(
            _apply_eval_run_entry_overrides(base_eval_run=base_eval_run, entry=entry)
        )
    return payload, eval_runs


def _build_batch_item(eval_run: dict[str, Any]) -> dict[str, Any]:
    summary = eval_run.get("summary", {})
    generated_from = eval_run.get("generatedFrom", {})
    return {
        "evalRunId": eval_run.get("evalRunId"),
        "mode": eval_run.get("mode"),
        "rankingRunId": summary.get("rankingRunId"),
        "rankingSnapshotId": summary.get("rankingSnapshotId"),
        "rankingProfileId": summary.get("rankingProfileId"),
        "evaluationWindow": summary.get("evaluationWindow"),
        "topicReward": _round_metric(summary.get("topicReward")),
        "performanceReward": _round_metric(summary.get("performanceReward")),
        "performanceWeight": _round_metric(summary.get("performanceWeight")),
        "combinedReward": _round_metric(summary.get("combinedReward")),
        "postCoverageRate": _round_metric(summary.get("postCoverageRate")),
        "rejectedCount": summary.get("rejectedCount"),
        "shadowLeaderProfileId": summary.get("shadowLeaderProfileId"),
        "challengerInputKind": summary.get("challengerInputKind"),
        "weeklyDecision": summary.get("weeklyDecision"),
        "selectedChallengerProfileId": summary.get("selectedChallengerProfileId"),
        "rankingOptimizerContractVersion": generated_from.get(
            "rankingOptimizerContractVersion"
        ),
        "runtimeSourceKind": generated_from.get("evalBatchRuntimeSourceKind"),
        "runtimeSourceId": generated_from.get("evalBatchRuntimeSourceId"),
        "runtimeProfileId": generated_from.get("evalBatchRuntimeProfileId"),
        "runtimeProfileRequestedId": generated_from.get(
            "evalBatchRuntimeProfileRequestedId"
        ),
        "runtimeProfileAliasApplied": generated_from.get(
            "evalBatchRuntimeProfileAliasApplied"
        ),
        "runtimeProfileCatalogId": generated_from.get(
            "evalBatchRuntimeProfileCatalogId"
        ),
        "runtimeProfileCatalogFamily": generated_from.get(
            "evalBatchRuntimeProfileCatalogFamily"
        ),
        "runtimeProfileCatalogVersion": generated_from.get(
            "evalBatchRuntimeProfileCatalogVersion"
        ),
        "runtimeProfileCatalogSchemaVersion": generated_from.get(
            "evalBatchRuntimeProfileCatalogSchemaVersion"
        ),
        "materializationPlanId": generated_from.get("evalBatchMaterializationPlanId"),
        "jobFamilyGroup": generated_from.get("evalBatchJobFamilyGroup"),
        "materializationProfile": generated_from.get(
            "evalBatchMaterializationProfile"
        ),
        "materializationStrategy": generated_from.get(
            "evalBatchMaterializationStrategy"
        ),
        "requiredArtifactKinds": generated_from.get("evalBatchRequiredArtifactKinds"),
        "upstreamJobFamilies": generated_from.get("evalBatchUpstreamJobFamilies"),
        "historyBatchLabel": generated_from.get("historyBatchLabel"),
        "historyWindowLabel": generated_from.get("historyWindowLabel"),
        "scenarioLabel": generated_from.get("scenarioLabel"),
    }


def _get_comparison_value(item: dict[str, Any], comparison_dimension: str) -> str | None:
    return item.get(comparison_dimension)


def _build_group_summary(
    *,
    group_value: str | None,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    best_eval_run = _select_best_eval_run(items)
    return {
        "groupValue": group_value,
        "evalRunCount": len(items),
        "modeCounts": _count_by([item.get("mode") for item in items]),
        "weeklyDecisionCounts": _count_by(
            [item.get("weeklyDecision") for item in items]
        ),
        "rankingRunIds": _sorted_unique([item.get("rankingRunId") for item in items]),
        "rankingProfileIds": _sorted_unique(
            [item.get("rankingProfileId") for item in items]
        ),
        "evaluationWindows": _sorted_unique(
            [item.get("evaluationWindow") for item in items]
        ),
        "runtimeSourceKinds": _sorted_unique(
            [item.get("runtimeSourceKind") for item in items]
        ),
        "runtimeSourceIds": _sorted_unique(
            [item.get("runtimeSourceId") for item in items]
        ),
        "runtimeProfileIds": _sorted_unique(
            [item.get("runtimeProfileId") for item in items]
        ),
        "runtimeProfileRequestedIds": _sorted_unique(
            [item.get("runtimeProfileRequestedId") for item in items]
        ),
        "runtimeProfileAliasAppliedCount": sum(
            1 for item in items if item.get("runtimeProfileAliasApplied") is True
        ),
        "runtimeProfileCatalogIds": _sorted_unique(
            [item.get("runtimeProfileCatalogId") for item in items]
        ),
        "runtimeProfileCatalogFamilies": _sorted_unique(
            [item.get("runtimeProfileCatalogFamily") for item in items]
        ),
        "runtimeProfileCatalogVersions": _sorted_unique(
            [item.get("runtimeProfileCatalogVersion") for item in items]
        ),
        "runtimeProfileCatalogSchemaVersions": _sorted_unique(
            [item.get("runtimeProfileCatalogSchemaVersion") for item in items]
        ),
        "materializationPlanIds": _sorted_unique(
            [item.get("materializationPlanId") for item in items]
        ),
        "jobFamilyGroups": _sorted_unique(
            [item.get("jobFamilyGroup") for item in items]
        ),
        "materializationProfiles": _sorted_unique(
            [item.get("materializationProfile") for item in items]
        ),
        "materializationStrategies": _sorted_unique(
            [item.get("materializationStrategy") for item in items]
        ),
        "requiredArtifactKinds": _sorted_unique_nested(
            [item.get("requiredArtifactKinds") for item in items]
        ),
        "upstreamJobFamilies": _sorted_unique_nested(
            [item.get("upstreamJobFamilies") for item in items]
        ),
        "historyBatchLabels": _sorted_unique(
            [item.get("historyBatchLabel") for item in items]
        ),
        "historyWindowLabels": _sorted_unique(
            [item.get("historyWindowLabel") for item in items]
        ),
        "scenarioLabels": _sorted_unique([item.get("scenarioLabel") for item in items]),
        "averageTopicReward": _average([item.get("topicReward") for item in items]),
        "averageCombinedReward": _average(
            [item.get("combinedReward") for item in items]
        ),
        "averagePostCoverageRate": _average(
            [item.get("postCoverageRate") for item in items]
        ),
        "bestEvalRunId": None if best_eval_run is None else best_eval_run["evalRunId"],
        "bestCombinedReward": None
        if best_eval_run is None
        else best_eval_run["combinedReward"],
    }


def build_optimizer_eval_batch_payload(
    *,
    eval_runs: list[dict[str, Any]],
    batch_id: str,
    generated_at: str,
    source_mode: str,
    source_descriptor: dict[str, Any],
    comparison_dimension: str,
    batch_window_label: str,
    window_set_purpose: str | None = None,
    window_set_batch_type: str | None = None,
    window_set_batch_type_selection_source: str | None = None,
    comparison_dimension_selection_source: str | None = None,
    runtime_profile_purpose_policy_id: str | None = None,
    runtime_profile_purpose_template_id: str | None = None,
    runtime_profile_purpose_template_family_id: str | None = None,
    runtime_profile_planner_metadata_contract_family_id: str | None = None,
    runtime_profile_planner_metadata_policy_id: str | None = None,
    runtime_profile_planner_metadata_contract_id: str | None = None,
) -> dict[str, Any]:
    items = [_build_batch_item(eval_run) for eval_run in eval_runs]
    best_eval_run = _select_best_eval_run(items)
    combined_rewards = [item.get("combinedReward") for item in items]
    topic_rewards = [item.get("topicReward") for item in items]
    post_coverage_rates = [item.get("postCoverageRate") for item in items]

    input_source_kind_summary: dict[str, list[str]] = {}
    for key in ("backfills", "performance", "challengerInput"):
        input_source_kind_summary[key] = _sorted_unique(
            [
                eval_run.get("generatedFrom", {})
                .get("optimizerInputSources", {})
                .get(key, {})
                .get("sourceKind")
                for eval_run in eval_runs
            ]
        )

    groups: dict[str | None, list[dict[str, Any]]] = {}
    for item in items:
        group_value = _get_comparison_value(item, comparison_dimension)
        groups.setdefault(group_value, []).append(item)
    group_summaries = [
        _build_group_summary(group_value=group_value, items=group_items)
        for group_value, group_items in sorted(
            groups.items(),
            key=lambda pair: "" if pair[0] is None else str(pair[0]),
        )
    ]

    payload = {
        "schemaVersion": "optimizer-eval-batch.v1",
        "batchId": batch_id,
        "generatedAt": generated_at,
        "summary": {
            "evalRunCount": len(items),
            "comparisonDimension": comparison_dimension,
            "comparisonGroupCount": len(group_summaries),
            "batchWindowLabel": batch_window_label,
            "modeCounts": _count_by([item.get("mode") for item in items]),
            "weeklyDecisionCounts": _count_by(
                [item.get("weeklyDecision") for item in items]
            ),
            "rankingRunIds": _sorted_unique(
                [item.get("rankingRunId") for item in items]
            ),
            "rankingProfileIds": _sorted_unique(
                [item.get("rankingProfileId") for item in items]
            ),
            "evaluationWindows": _sorted_unique(
                [item.get("evaluationWindow") for item in items]
            ),
            "runtimeSourceKinds": _sorted_unique(
                [item.get("runtimeSourceKind") for item in items]
            ),
            "runtimeSourceIds": _sorted_unique(
                [item.get("runtimeSourceId") for item in items]
            ),
            "runtimeProfileIds": _sorted_unique(
                [item.get("runtimeProfileId") for item in items]
            ),
            "runtimeProfileRequestedIds": _sorted_unique(
                [item.get("runtimeProfileRequestedId") for item in items]
            ),
            "runtimeProfileAliasAppliedCount": sum(
                1 for item in items if item.get("runtimeProfileAliasApplied") is True
            ),
            "runtimeProfileCatalogIds": _sorted_unique(
                [item.get("runtimeProfileCatalogId") for item in items]
            ),
            "runtimeProfileCatalogFamilies": _sorted_unique(
                [item.get("runtimeProfileCatalogFamily") for item in items]
            ),
            "runtimeProfileCatalogVersions": _sorted_unique(
                [item.get("runtimeProfileCatalogVersion") for item in items]
            ),
            "runtimeProfileCatalogSchemaVersions": _sorted_unique(
                [item.get("runtimeProfileCatalogSchemaVersion") for item in items]
            ),
            "materializationPlanIds": _sorted_unique(
                [item.get("materializationPlanId") for item in items]
            ),
            "jobFamilyGroups": _sorted_unique(
                [item.get("jobFamilyGroup") for item in items]
            ),
            "materializationProfiles": _sorted_unique(
                [item.get("materializationProfile") for item in items]
            ),
            "materializationStrategies": _sorted_unique(
                [item.get("materializationStrategy") for item in items]
            ),
            "requiredArtifactKinds": _sorted_unique_nested(
                [item.get("requiredArtifactKinds") for item in items]
            ),
            "upstreamJobFamilies": _sorted_unique_nested(
                [item.get("upstreamJobFamilies") for item in items]
            ),
            "historyBatchLabels": _sorted_unique(
                [item.get("historyBatchLabel") for item in items]
            ),
            "historyWindowLabels": _sorted_unique(
                [item.get("historyWindowLabel") for item in items]
            ),
            "scenarioLabels": _sorted_unique(
                [item.get("scenarioLabel") for item in items]
            ),
            "challengerInputKinds": _sorted_unique(
                [item.get("challengerInputKind") for item in items]
            ),
            "rankingOptimizerContractVersions": _sorted_unique(
                [item.get("rankingOptimizerContractVersion") for item in items]
            ),
            "inputSourceKinds": input_source_kind_summary,
            "averageTopicReward": _average(topic_rewards),
            "averageCombinedReward": _average(combined_rewards),
            "averagePostCoverageRate": _average(post_coverage_rates),
            "bestEvalRunId": None if best_eval_run is None else best_eval_run["evalRunId"],
            "bestProfileId": None
            if best_eval_run is None
            else best_eval_run["rankingProfileId"],
            "bestCombinedReward": None
            if best_eval_run is None
            else best_eval_run["combinedReward"],
        },
        "generatedFrom": {
            "sourceMode": source_mode,
            "sourceDescriptor": source_descriptor,
            "comparisonDimension": comparison_dimension,
            "batchWindowLabel": batch_window_label,
            "evalRunIds": [item.get("evalRunId") for item in items],
        },
        "groupSummaries": group_summaries,
        "items": items,
        "artifacts": {
            "evalRuns": eval_runs,
        },
    }
    if window_set_purpose is not None:
        payload["generatedFrom"]["windowSetPurpose"] = window_set_purpose
        payload["generatedFrom"]["sourceDescriptor"]["windowSetPurpose"] = (
            window_set_purpose
        )
    if window_set_batch_type is not None:
        payload["generatedFrom"]["windowSetBatchType"] = window_set_batch_type
        payload["generatedFrom"]["sourceDescriptor"]["windowSetBatchType"] = (
            window_set_batch_type
        )
    if window_set_batch_type_selection_source is not None:
        payload["generatedFrom"]["windowSetBatchTypeSelectionSource"] = (
            window_set_batch_type_selection_source
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "windowSetBatchTypeSelectionSource"
        ] = window_set_batch_type_selection_source
    if comparison_dimension_selection_source is not None:
        payload["generatedFrom"]["comparisonDimensionSelectionSource"] = (
            comparison_dimension_selection_source
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "comparisonDimensionSelectionSource"
        ] = comparison_dimension_selection_source
    if runtime_profile_purpose_policy_id is not None:
        payload["generatedFrom"]["runtimeProfilePurposePolicyId"] = (
            runtime_profile_purpose_policy_id
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "runtimeProfilePurposePolicyId"
        ] = runtime_profile_purpose_policy_id
    if runtime_profile_purpose_template_id is not None:
        payload["generatedFrom"]["runtimeProfilePurposeTemplateId"] = (
            runtime_profile_purpose_template_id
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "runtimeProfilePurposeTemplateId"
        ] = runtime_profile_purpose_template_id
    if runtime_profile_purpose_template_family_id is not None:
        payload["generatedFrom"]["runtimeProfilePurposeTemplateFamilyId"] = (
            runtime_profile_purpose_template_family_id
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "runtimeProfilePurposeTemplateFamilyId"
        ] = runtime_profile_purpose_template_family_id
    if runtime_profile_planner_metadata_contract_family_id is not None:
        payload["generatedFrom"]["runtimeProfilePlannerMetadataContractFamilyId"] = (
            runtime_profile_planner_metadata_contract_family_id
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "runtimeProfilePlannerMetadataContractFamilyId"
        ] = runtime_profile_planner_metadata_contract_family_id
    if runtime_profile_planner_metadata_policy_id is not None:
        payload["generatedFrom"]["runtimeProfilePlannerMetadataPolicyId"] = (
            runtime_profile_planner_metadata_policy_id
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "runtimeProfilePlannerMetadataPolicyId"
        ] = runtime_profile_planner_metadata_policy_id
    if runtime_profile_planner_metadata_contract_id is not None:
        payload["generatedFrom"]["runtimeProfilePlannerMetadataContractId"] = (
            runtime_profile_planner_metadata_contract_id
        )
        payload["generatedFrom"]["sourceDescriptor"][
            "runtimeProfilePlannerMetadataContractId"
        ] = runtime_profile_planner_metadata_contract_id
    return payload
