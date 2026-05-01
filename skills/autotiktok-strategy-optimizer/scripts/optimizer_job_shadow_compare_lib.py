#!/usr/bin/env python3
"""
Helpers for scheduler-facing optimizer shadow-compare artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reward_lib import load_json


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SKILL_ROOT.parents[1]

OPTIMIZER_JOB_SHADOW_COMPARE_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare.sample.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_SCHEMA_VERSION = "optimizer-job-shadow-compare.v1"
OPTIMIZER_JOB_SHADOW_COMPARE_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_SHADOW_COMPARE_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_SHADOW_COMPARE_SCHEMA_VERSION,
}
OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare-plan.sample.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare-plan.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SCHEMA_VERSION,
}
OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare-batch-manifest.sample.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare-batch-manifest.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCHEMA_VERSION,
}
OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SAMPLE_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare-batch.sample.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SCHEMA_VERSION = (
    "optimizer-job-shadow-compare-batch.v1"
)
OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SCHEMA_VERSIONS = {
    OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SCHEMA_VERSION,
}
JOB_SHADOW_COMPARISON_DIMENSIONS = (
    "scheduleId",
    "candidateSchedulerRolloutIntent",
    "candidateRolloutClass",
    "candidateRuntimeProfileRolloutClass",
    "candidateWindowSetPurpose",
    "candidateComparisonDimension",
    "candidateSourceLane",
    "cadenceKind",
    "jobKind",
    "comparisonId",
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


def resolve_optimizer_job_shadow_compare_path(
    label: str, *, manifest_path: Path
) -> Path:
    return _resolve_path_from_label(label, manifest_path=manifest_path)


def build_optimizer_job_run_semantic_view(payload: dict[str, Any]) -> dict[str, Any]:
    offline_cycle = payload.get("artifacts", {}).get("offlineCycle", {})
    daily_review = offline_cycle.get("artifacts", {}).get("dailyReview", {})
    weekly_promotion = offline_cycle.get("artifacts", {}).get("weeklyPromotion")
    combined_breakdown = daily_review.get("combinedRewardBreakdown", {})
    recommendation = daily_review.get("recommendation", {})
    return {
        "jobKind": payload.get("jobKind"),
        "mode": payload.get("mode"),
        "rankingProfileId": payload.get("summary", {}).get("rankingProfileId"),
        "dailyRecommendation": payload.get("summary", {}).get("dailyRecommendation"),
        "shadowLeaderProfileId": payload.get("summary", {}).get(
            "shadowLeaderProfileId"
        ),
        "selectedChallengerProfileId": payload.get("summary", {}).get(
            "selectedChallengerProfileId"
        ),
        "weeklyDecision": payload.get("summary", {}).get("weeklyDecision"),
        "dailyRecommendationReason": recommendation.get("reason"),
        "combinedReward": combined_breakdown.get("combinedReward"),
        "postCoverageRate": combined_breakdown.get("postCoverageRate"),
        "weeklyDecisionReason": None
        if weekly_promotion is None
        else weekly_promotion.get("reason"),
    }


def build_optimizer_job_run_input_provenance(
    payload: dict[str, Any],
) -> dict[str, Any]:
    generated_from = payload.get("generatedFrom", {})
    return {
        "optimizerJobSchedulerRolloutIntent": generated_from.get(
            "optimizerJobSchedulerRolloutIntent"
        ),
        "optimizerJobSchedulerRolloutIntentSelectionSource": generated_from.get(
            "optimizerJobSchedulerRolloutIntentSelectionSource"
        ),
        "optimizerJobRuntimeProfileRolloutClass": generated_from.get(
            "optimizerJobRuntimeProfileRolloutClass"
        ),
        "optimizerJobWindowSetPurpose": generated_from.get(
            "optimizerJobWindowSetPurpose"
        ),
        "optimizerJobComparisonDimension": generated_from.get(
            "optimizerJobComparisonDimension"
        ),
        "optimizerInputSourceLane": generated_from.get("optimizerInputSourceLane"),
        "optimizerInputRolloutClass": generated_from.get("optimizerInputRolloutClass"),
        "optimizerInputLaneSelectionSource": generated_from.get(
            "optimizerInputLaneSelectionSource"
        ),
        "optimizerInputRolloutStrategy": generated_from.get(
            "optimizerInputRolloutStrategy"
        ),
        "optimizerInputSourceRegistrySchemaVersion": generated_from.get(
            "optimizerInputSourceRegistrySchemaVersion"
        ),
        "optimizerInputSourceRegistryId": generated_from.get(
            "optimizerInputSourceRegistryId"
        ),
        "optimizerInputArtifactResolverSchemaVersion": generated_from.get(
            "optimizerInputArtifactResolverSchemaVersion"
        ),
        "optimizerInputArtifactResolverId": generated_from.get(
            "optimizerInputArtifactResolverId"
        ),
        "optimizerInputSourceProviderCatalogSchemaVersion": generated_from.get(
            "optimizerInputSourceProviderCatalogSchemaVersion"
        ),
        "optimizerInputSourceProviderCatalogId": generated_from.get(
            "optimizerInputSourceProviderCatalogId"
        ),
        "optimizerInputSourceProviderRegistrySchemaVersion": generated_from.get(
            "optimizerInputSourceProviderRegistrySchemaVersion"
        ),
        "optimizerInputSourceProviderRegistryId": generated_from.get(
            "optimizerInputSourceProviderRegistryId"
        ),
        "optimizerInputSourceArtifactCatalogSchemaVersion": generated_from.get(
            "optimizerInputSourceArtifactCatalogSchemaVersion"
        ),
        "optimizerInputSourceArtifactCatalogId": generated_from.get(
            "optimizerInputSourceArtifactCatalogId"
        ),
        "optimizerInputRolloutPolicySchemaVersion": generated_from.get(
            "optimizerInputRolloutPolicySchemaVersion"
        ),
        "optimizerInputRolloutPolicyId": generated_from.get(
            "optimizerInputRolloutPolicyId"
        ),
        "optimizerInputSourceProviderLane": generated_from.get(
            "optimizerInputSourceProviderLane"
        ),
        "optimizerInputSourceProviderKind": generated_from.get(
            "optimizerInputSourceProviderKind"
        ),
        "optimizerInputSourceProviderClass": generated_from.get(
            "optimizerInputSourceProviderClass"
        ),
        "optimizerInputSourceProviderHandle": generated_from.get(
            "optimizerInputSourceProviderHandle"
        ),
        "optimizerInputSourceProviderLocatorKind": generated_from.get(
            "optimizerInputSourceProviderLocatorKind"
        ),
        "optimizerInputSourceProviderOwner": generated_from.get(
            "optimizerInputSourceProviderOwner"
        ),
        "optimizerInputArtifactLocatorKind": generated_from.get(
            "optimizerInputArtifactLocatorKind"
        ),
    }


def _build_semantic_diff_keys(
    baseline_view: dict[str, Any], candidate_view: dict[str, Any]
) -> list[str]:
    diff_keys: list[str] = []
    for key in baseline_view.keys():
        if baseline_view.get(key) != candidate_view.get(key):
            diff_keys.append(key)
    return diff_keys


def build_optimizer_job_shadow_compare_entry(
    *,
    comparison_id: str,
    schedule: dict[str, Any],
    baseline_scheduler_rollout_intent: str | None,
    baseline_rollout_class: str,
    candidate_scheduler_rollout_intent: str | None,
    candidate_rollout_class: str,
    baseline_payload: dict[str, Any],
    candidate_payload: dict[str, Any],
) -> dict[str, Any]:
    baseline_view = build_optimizer_job_run_semantic_view(baseline_payload)
    candidate_view = build_optimizer_job_run_semantic_view(candidate_payload)
    baseline_input_provenance = build_optimizer_job_run_input_provenance(
        baseline_payload
    )
    candidate_input_provenance = build_optimizer_job_run_input_provenance(
        candidate_payload
    )
    semantic_diff_keys = _build_semantic_diff_keys(baseline_view, candidate_view)
    return {
        "comparisonId": comparison_id,
        "scheduleId": schedule.get("scheduleId"),
        "cadenceKind": schedule.get("cadenceKind"),
        "jobKind": schedule.get("jobKind"),
        "baseline": {
            "schedulerRolloutIntent": baseline_scheduler_rollout_intent,
            "rolloutClass": baseline_rollout_class,
            "runtimeProfileRolloutClass": baseline_input_provenance.get(
                "optimizerJobRuntimeProfileRolloutClass"
            ),
            "windowSetPurpose": baseline_input_provenance.get(
                "optimizerJobWindowSetPurpose"
            ),
            "comparisonDimension": baseline_input_provenance.get(
                "optimizerJobComparisonDimension"
            ),
            "jobRunId": baseline_payload.get("jobRunId"),
            "semanticView": baseline_view,
            "inputProvenance": baseline_input_provenance,
        },
        "candidate": {
            "schedulerRolloutIntent": candidate_scheduler_rollout_intent,
            "rolloutClass": candidate_rollout_class,
            "runtimeProfileRolloutClass": candidate_input_provenance.get(
                "optimizerJobRuntimeProfileRolloutClass"
            ),
            "windowSetPurpose": candidate_input_provenance.get(
                "optimizerJobWindowSetPurpose"
            ),
            "comparisonDimension": candidate_input_provenance.get(
                "optimizerJobComparisonDimension"
            ),
            "jobRunId": candidate_payload.get("jobRunId"),
            "semanticView": candidate_view,
            "inputProvenance": candidate_input_provenance,
        },
        "semanticMatch": not semantic_diff_keys,
        "semanticDiffKeys": semantic_diff_keys,
    }


def build_optimizer_job_shadow_compare_plan_payload(
    *,
    compare_plan_id: str,
    generated_at: str,
    schedule_plan_payload: dict[str, Any],
    input_rollout_policy_payload: dict[str, Any],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SAMPLE_SCHEMA_VERSION,
        "comparePlanId": compare_plan_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "optimizerJobScheduleSchemaVersion": schedule_plan_payload.get(
                "schemaVersion"
            ),
            "optimizerJobSchedulePlanId": schedule_plan_payload.get("schedulePlanId"),
            "optimizerInputRolloutPolicySchemaVersion": input_rollout_policy_payload.get(
                "schemaVersion"
            ),
            "optimizerInputRolloutPolicyId": input_rollout_policy_payload.get(
                "policyId"
            ),
            "comparisonCount": len(comparisons),
        },
        "comparisons": comparisons,
    }


def build_optimizer_job_shadow_compare_payload(
    *,
    compare_id: str,
    generated_at: str,
    compare_plan_payload: dict[str, Any],
    schedule_plan_payload: dict[str, Any],
    input_rollout_policy_payload: dict[str, Any],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    rollout_classes = sorted(
        {
            entry[side]["rolloutClass"]
            for entry in comparisons
            for side in ("baseline", "candidate")
        }
    )
    scheduler_rollout_intents = sorted(
        {
            entry[side]["schedulerRolloutIntent"]
            for entry in comparisons
            for side in ("baseline", "candidate")
            if entry[side].get("schedulerRolloutIntent")
        }
    )
    runtime_profile_rollout_classes = sorted(
        {
            entry[side]["runtimeProfileRolloutClass"]
            for entry in comparisons
            for side in ("baseline", "candidate")
            if entry[side].get("runtimeProfileRolloutClass")
        }
    )
    window_set_purposes = sorted(
        {
            entry[side]["windowSetPurpose"]
            for entry in comparisons
            for side in ("baseline", "candidate")
            if entry[side].get("windowSetPurpose")
        }
    )
    comparison_dimensions = sorted(
        {
            entry[side]["comparisonDimension"]
            for entry in comparisons
            for side in ("baseline", "candidate")
            if entry[side].get("comparisonDimension")
        }
    )
    source_lanes = sorted(
        {
            entry[side]["inputProvenance"].get("optimizerInputSourceLane")
            for entry in comparisons
            for side in ("baseline", "candidate")
            if entry[side]["inputProvenance"].get("optimizerInputSourceLane")
        }
    )
    matched_count = sum(1 for entry in comparisons if entry.get("semanticMatch"))
    return {
        "schemaVersion": OPTIMIZER_JOB_SHADOW_COMPARE_SAMPLE_SCHEMA_VERSION,
        "compareId": compare_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "optimizerJobShadowComparePlanSchemaVersion": compare_plan_payload.get(
                "schemaVersion"
            ),
            "optimizerJobShadowComparePlanId": compare_plan_payload.get(
                "comparePlanId"
            ),
            "optimizerJobScheduleSchemaVersion": schedule_plan_payload.get(
                "schemaVersion"
            ),
            "optimizerJobSchedulePlanId": schedule_plan_payload.get("schedulePlanId"),
            "optimizerInputRolloutPolicySchemaVersion": input_rollout_policy_payload.get(
                "schemaVersion"
            ),
            "optimizerInputRolloutPolicyId": input_rollout_policy_payload.get(
                "policyId"
            ),
            "comparisonCount": len(comparisons),
        },
        "summary": {
            "comparisonCount": len(comparisons),
            "matchedComparisonCount": matched_count,
            "mismatchedComparisonCount": len(comparisons) - matched_count,
            "comparedScheduleIds": sorted(
                {entry.get("scheduleId") for entry in comparisons if entry.get("scheduleId")}
            ),
            "comparedSchedulerRolloutIntents": scheduler_rollout_intents,
            "comparedRolloutClasses": rollout_classes,
            "comparedRuntimeProfileRolloutClasses": runtime_profile_rollout_classes,
            "comparedWindowSetPurposes": window_set_purposes,
            "comparedComparisonDimensions": comparison_dimensions,
            "comparedSourceLanes": source_lanes,
        },
        "comparisons": comparisons,
    }


def build_optimizer_job_shadow_compare_batch_manifest_payload(
    *,
    compare_paths: list[Path],
    schema_version: str,
    manifest_id: str,
    generated_at: str,
    comparison_dimension: str,
    batch_window_label: str,
    path_style: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "manifestId": manifest_id,
        "generatedAt": generated_at,
        "comparisonDimension": comparison_dimension,
        "batchWindowLabel": batch_window_label,
        "generatedFrom": {
            "compareArtifactCount": len(compare_paths),
        },
        "compareArtifactPaths": [
            _path_label(path, style=path_style) for path in compare_paths
        ],
    }


def _build_shadow_compare_batch_item(
    *,
    compare_payload: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    candidate = comparison.get("candidate", {})
    candidate_input = candidate.get("inputProvenance", {})
    baseline = comparison.get("baseline", {})
    baseline_input = baseline.get("inputProvenance", {})
    return {
        "compareId": compare_payload.get("compareId"),
        "compareSchemaVersion": compare_payload.get("schemaVersion"),
        "comparePlanId": compare_payload.get("generatedFrom", {}).get(
            "optimizerJobShadowComparePlanId"
        ),
        "comparisonId": comparison.get("comparisonId"),
        "scheduleId": comparison.get("scheduleId"),
        "cadenceKind": comparison.get("cadenceKind"),
        "jobKind": comparison.get("jobKind"),
        "baselineSchedulerRolloutIntent": baseline.get("schedulerRolloutIntent"),
        "baselineRolloutClass": baseline.get("rolloutClass"),
        "baselineRuntimeProfileRolloutClass": baseline.get(
            "runtimeProfileRolloutClass"
        ),
        "baselineWindowSetPurpose": baseline.get("windowSetPurpose"),
        "baselineComparisonDimension": baseline.get("comparisonDimension"),
        "candidateSchedulerRolloutIntent": candidate.get("schedulerRolloutIntent"),
        "candidateRolloutClass": candidate.get("rolloutClass"),
        "candidateRuntimeProfileRolloutClass": candidate.get(
            "runtimeProfileRolloutClass"
        ),
        "candidateWindowSetPurpose": candidate.get("windowSetPurpose"),
        "candidateComparisonDimension": candidate.get("comparisonDimension"),
        "baselineSourceLane": baseline_input.get("optimizerInputSourceLane"),
        "candidateSourceLane": candidate_input.get("optimizerInputSourceLane"),
        "semanticMatch": comparison.get("semanticMatch"),
        "semanticDiffKeys": comparison.get("semanticDiffKeys", []),
    }


def build_optimizer_job_shadow_compare_batch_payload(
    *,
    compare_payloads: list[dict[str, Any]],
    batch_id: str,
    generated_at: str,
    source_mode: str,
    source_descriptor: dict[str, Any],
    comparison_dimension: str,
    batch_window_label: str,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for compare_payload in compare_payloads:
        for comparison in compare_payload.get("comparisons", []):
            items.append(
                _build_shadow_compare_batch_item(
                    compare_payload=compare_payload,
                    comparison=comparison,
                )
            )

    matched_count = sum(1 for item in items if item.get("semanticMatch"))
    compared_compare_ids = sorted(
        {
            item["compareId"]
            for item in items
            if isinstance(item.get("compareId"), str) and item.get("compareId")
        }
    )
    compared_plan_ids = sorted(
        {
            item["comparePlanId"]
            for item in items
            if isinstance(item.get("comparePlanId"), str) and item.get("comparePlanId")
        }
    )
    compared_schedule_ids = sorted(
        {
            item["scheduleId"]
            for item in items
            if isinstance(item.get("scheduleId"), str) and item.get("scheduleId")
        }
    )
    compared_candidate_rollout_classes = sorted(
        {
            item["candidateRolloutClass"]
            for item in items
            if isinstance(item.get("candidateRolloutClass"), str)
            and item.get("candidateRolloutClass")
        }
    )
    compared_candidate_scheduler_rollout_intents = sorted(
        {
            item["candidateSchedulerRolloutIntent"]
            for item in items
            if isinstance(item.get("candidateSchedulerRolloutIntent"), str)
            and item.get("candidateSchedulerRolloutIntent")
        }
    )
    compared_candidate_source_lanes = sorted(
        {
            item["candidateSourceLane"]
            for item in items
            if isinstance(item.get("candidateSourceLane"), str)
            and item.get("candidateSourceLane")
        }
    )
    compared_candidate_runtime_profile_rollout_classes = sorted(
        {
            item["candidateRuntimeProfileRolloutClass"]
            for item in items
            if isinstance(item.get("candidateRuntimeProfileRolloutClass"), str)
            and item.get("candidateRuntimeProfileRolloutClass")
        }
    )
    compared_candidate_window_set_purposes = sorted(
        {
            item["candidateWindowSetPurpose"]
            for item in items
            if isinstance(item.get("candidateWindowSetPurpose"), str)
            and item.get("candidateWindowSetPurpose")
        }
    )
    compared_candidate_comparison_dimensions = sorted(
        {
            item["candidateComparisonDimension"]
            for item in items
            if isinstance(item.get("candidateComparisonDimension"), str)
            and item.get("candidateComparisonDimension")
        }
    )

    grouped_items: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        value = item.get(comparison_dimension)
        group_key = value if isinstance(value, str) and value else "__missing__"
        grouped_items.setdefault(group_key, []).append(item)

    group_summaries: list[dict[str, Any]] = []
    for group_key in sorted(grouped_items):
        group = grouped_items[group_key]
        group_match_count = sum(1 for item in group if item.get("semanticMatch"))
        group_summaries.append(
            {
                "groupValue": None if group_key == "__missing__" else group_key,
                "comparisonCount": len(group),
                "matchedComparisonCount": group_match_count,
                "mismatchedComparisonCount": len(group) - group_match_count,
                "comparedCompareIds": sorted(
                    {
                        item["compareId"]
                        for item in group
                        if isinstance(item.get("compareId"), str)
                        and item.get("compareId")
                    }
                ),
                "candidateRolloutClasses": sorted(
                    {
                        item["candidateRolloutClass"]
                        for item in group
                        if isinstance(item.get("candidateRolloutClass"), str)
                        and item.get("candidateRolloutClass")
                    }
                ),
                "candidateSchedulerRolloutIntents": sorted(
                    {
                        item["candidateSchedulerRolloutIntent"]
                        for item in group
                        if isinstance(item.get("candidateSchedulerRolloutIntent"), str)
                        and item.get("candidateSchedulerRolloutIntent")
                    }
                ),
                "candidateSourceLanes": sorted(
                    {
                        item["candidateSourceLane"]
                        for item in group
                        if isinstance(item.get("candidateSourceLane"), str)
                        and item.get("candidateSourceLane")
                    }
                ),
                "candidateRuntimeProfileRolloutClasses": sorted(
                    {
                        item["candidateRuntimeProfileRolloutClass"]
                        for item in group
                        if isinstance(
                            item.get("candidateRuntimeProfileRolloutClass"), str
                        )
                        and item.get("candidateRuntimeProfileRolloutClass")
                    }
                ),
                "candidateWindowSetPurposes": sorted(
                    {
                        item["candidateWindowSetPurpose"]
                        for item in group
                        if isinstance(item.get("candidateWindowSetPurpose"), str)
                        and item.get("candidateWindowSetPurpose")
                    }
                ),
                "candidateComparisonDimensions": sorted(
                    {
                        item["candidateComparisonDimension"]
                        for item in group
                        if isinstance(item.get("candidateComparisonDimension"), str)
                        and item.get("candidateComparisonDimension")
                    }
                ),
            }
        )

    return {
        "schemaVersion": OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SAMPLE_SCHEMA_VERSION,
        "batchId": batch_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "sourceMode": source_mode,
            "sourceDescriptor": source_descriptor,
            "compareArtifactCount": len(compare_payloads),
        },
        "summary": {
            "compareArtifactCount": len(compare_payloads),
            "comparisonCount": len(items),
            "matchedComparisonCount": matched_count,
            "mismatchedComparisonCount": len(items) - matched_count,
            "comparisonDimension": comparison_dimension,
            "batchWindowLabel": batch_window_label,
            "comparedCompareIds": compared_compare_ids,
            "comparedPlanIds": compared_plan_ids,
            "comparedScheduleIds": compared_schedule_ids,
            "comparedCandidateSchedulerRolloutIntents": compared_candidate_scheduler_rollout_intents,
            "comparedCandidateRolloutClasses": compared_candidate_rollout_classes,
            "comparedCandidateRuntimeProfileRolloutClasses": compared_candidate_runtime_profile_rollout_classes,
            "comparedCandidateWindowSetPurposes": compared_candidate_window_set_purposes,
            "comparedCandidateComparisonDimensions": compared_candidate_comparison_dimensions,
            "comparedCandidateSourceLanes": compared_candidate_source_lanes,
            "groupCount": len(group_summaries),
        },
        "groupSummaries": group_summaries,
        "items": items,
    }


def validate_optimizer_job_shadow_compare_plan_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_JOB_SHADOW_COMPARE_PLAN_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer job shadow compare plan payload must declare a supported schemaVersion"
        )
    if not isinstance(payload.get("comparePlanId"), str) or not payload["comparePlanId"]:
        raise ValueError(
            "optimizer job shadow compare plan payload must declare comparePlanId"
        )
    if not isinstance(payload.get("generatedAt"), str) or not payload["generatedAt"]:
        raise ValueError(
            "optimizer job shadow compare plan payload must declare generatedAt"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job shadow compare plan payload must declare generatedFrom"
        )
    comparisons = payload.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError(
            "optimizer job shadow compare plan payload must declare comparisons"
        )
    if generated_from.get("comparisonCount") != len(comparisons):
        raise ValueError(
            "optimizer job shadow compare plan payload comparisonCount mismatch"
        )
    for index, comparison in enumerate(comparisons):
        if not isinstance(comparison, dict):
            raise ValueError(
                "optimizer job shadow compare plan comparison entries must be objects"
            )
        label = f"optimizer job shadow compare plan comparisons[{index}]"
        for field_name in (
            "comparisonId",
            "scheduleId",
            "baselineSchedulerRolloutIntent",
            "baselineRolloutClass",
            "baselineRuntimeProfileRolloutClass",
            "candidateSchedulerRolloutIntent",
            "candidateRolloutClass",
            "candidateRuntimeProfileRolloutClass",
        ):
            if not isinstance(comparison.get(field_name), str) or not comparison[
                field_name
            ]:
                raise ValueError(f"{label} must declare {field_name}")
        for optional_field_name in (
            "baselineWindowSetPurpose",
            "candidateWindowSetPurpose",
            "baselineComparisonDimension",
            "candidateComparisonDimension",
        ):
            optional_value = comparison.get(optional_field_name)
            if optional_value is not None and (
                not isinstance(optional_value, str) or not optional_value
            ):
                raise ValueError(
                    f"{label} {optional_field_name} must be null or a non-empty string"
                )


def validate_optimizer_job_shadow_compare_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_JOB_SHADOW_COMPARE_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer job shadow compare payload must declare a supported schemaVersion"
        )
    if not isinstance(payload.get("compareId"), str) or not payload["compareId"]:
        raise ValueError("optimizer job shadow compare payload must declare compareId")
    if not isinstance(payload.get("generatedAt"), str) or not payload["generatedAt"]:
        raise ValueError(
            "optimizer job shadow compare payload must declare generatedAt"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job shadow compare payload must declare generatedFrom"
        )
    if not isinstance(
        generated_from.get("optimizerJobShadowComparePlanSchemaVersion"), str
    ) or not generated_from.get("optimizerJobShadowComparePlanSchemaVersion"):
        raise ValueError(
            "optimizer job shadow compare payload must declare optimizerJobShadowComparePlanSchemaVersion"
        )
    if not isinstance(generated_from.get("optimizerJobShadowComparePlanId"), str) or not generated_from.get(
        "optimizerJobShadowComparePlanId"
    ):
        raise ValueError(
            "optimizer job shadow compare payload must declare optimizerJobShadowComparePlanId"
        )
    comparisons = payload.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError(
            "optimizer job shadow compare payload must declare comparisons"
        )
    if generated_from.get("comparisonCount") != len(comparisons):
        raise ValueError(
            "optimizer job shadow compare payload comparisonCount mismatch"
        )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("optimizer job shadow compare payload must declare summary")
    if summary.get("comparisonCount") != len(comparisons):
        raise ValueError(
            "optimizer job shadow compare summary comparisonCount mismatch"
        )

    matched_count = 0
    compared_schedule_ids: set[str] = set()
    compared_scheduler_rollout_intents: set[str] = set()
    compared_rollout_classes: set[str] = set()
    compared_runtime_profile_rollout_classes: set[str] = set()
    compared_window_set_purposes: set[str] = set()
    compared_comparison_dimensions: set[str] = set()
    compared_source_lanes: set[str] = set()
    for index, entry in enumerate(comparisons):
        if not isinstance(entry, dict):
            raise ValueError("optimizer job shadow compare entries must be objects")
        label = f"optimizer job shadow compare comparisons[{index}]"
        for field_name in ("comparisonId", "scheduleId", "cadenceKind", "jobKind"):
            if not isinstance(entry.get(field_name), str) or not entry[field_name]:
                raise ValueError(f"{label} must declare {field_name}")
        compared_schedule_ids.add(entry["scheduleId"])
        semantic_match = entry.get("semanticMatch")
        if not isinstance(semantic_match, bool):
            raise ValueError(f"{label} must declare semanticMatch")
        diff_keys = entry.get("semanticDiffKeys")
        if not isinstance(diff_keys, list):
            raise ValueError(f"{label} must declare semanticDiffKeys")
        if semantic_match != (len(diff_keys) == 0):
            raise ValueError(
                f"{label} semanticMatch must agree with semanticDiffKeys"
            )
        if semantic_match:
            matched_count += 1
        for side in ("baseline", "candidate"):
            payload_side = entry.get(side)
            if not isinstance(payload_side, dict):
                raise ValueError(f"{label} must declare {side}")
            scheduler_rollout_intent = payload_side.get("schedulerRolloutIntent")
            if (
                not isinstance(scheduler_rollout_intent, str)
                or not scheduler_rollout_intent
            ):
                raise ValueError(
                    f"{label} {side} must declare schedulerRolloutIntent"
                )
            compared_scheduler_rollout_intents.add(scheduler_rollout_intent)
            rollout_class = payload_side.get("rolloutClass")
            if not isinstance(rollout_class, str) or not rollout_class:
                raise ValueError(f"{label} {side} must declare rolloutClass")
            compared_rollout_classes.add(rollout_class)
            runtime_profile_rollout_class = payload_side.get(
                "runtimeProfileRolloutClass"
            )
            if runtime_profile_rollout_class is not None:
                if (
                    not isinstance(runtime_profile_rollout_class, str)
                    or not runtime_profile_rollout_class
                ):
                    raise ValueError(
                        f"{label} {side} runtimeProfileRolloutClass must be a non-empty string when present"
                    )
                compared_runtime_profile_rollout_classes.add(
                    runtime_profile_rollout_class
                )
            window_set_purpose = payload_side.get("windowSetPurpose")
            if window_set_purpose is not None:
                if not isinstance(window_set_purpose, str) or not window_set_purpose:
                    raise ValueError(
                        f"{label} {side} windowSetPurpose must be a non-empty string when present"
                    )
                compared_window_set_purposes.add(window_set_purpose)
            comparison_dimension = payload_side.get("comparisonDimension")
            if comparison_dimension is not None:
                if (
                    not isinstance(comparison_dimension, str)
                    or not comparison_dimension
                ):
                    raise ValueError(
                        f"{label} {side} comparisonDimension must be a non-empty string when present"
                    )
                compared_comparison_dimensions.add(comparison_dimension)
            if not isinstance(payload_side.get("jobRunId"), str) or not payload_side[
                "jobRunId"
            ]:
                raise ValueError(f"{label} {side} must declare jobRunId")
            semantic_view = payload_side.get("semanticView")
            if not isinstance(semantic_view, dict):
                raise ValueError(f"{label} {side} must declare semanticView")
            input_provenance = payload_side.get("inputProvenance")
            if not isinstance(input_provenance, dict):
                raise ValueError(f"{label} {side} must declare inputProvenance")
            source_lane = input_provenance.get("optimizerInputSourceLane")
            if source_lane is not None:
                if not isinstance(source_lane, str) or not source_lane:
                    raise ValueError(
                        f"{label} {side} optimizerInputSourceLane must be a non-empty string when present"
                    )
                compared_source_lanes.add(source_lane)

    if summary.get("matchedComparisonCount") != matched_count:
        raise ValueError(
            "optimizer job shadow compare summary matchedComparisonCount mismatch"
        )
    if summary.get("mismatchedComparisonCount") != len(comparisons) - matched_count:
        raise ValueError(
            "optimizer job shadow compare summary mismatchedComparisonCount mismatch"
        )
    if summary.get("comparedScheduleIds") != sorted(compared_schedule_ids):
        raise ValueError(
            "optimizer job shadow compare summary comparedScheduleIds mismatch"
        )
    if summary.get("comparedSchedulerRolloutIntents") != sorted(
        compared_scheduler_rollout_intents
    ):
        raise ValueError(
            "optimizer job shadow compare summary comparedSchedulerRolloutIntents mismatch"
        )
    if summary.get("comparedRolloutClasses") != sorted(compared_rollout_classes):
        raise ValueError(
            "optimizer job shadow compare summary comparedRolloutClasses mismatch"
        )
    if summary.get("comparedRuntimeProfileRolloutClasses") != sorted(
        compared_runtime_profile_rollout_classes
    ):
        raise ValueError(
            "optimizer job shadow compare summary comparedRuntimeProfileRolloutClasses mismatch"
        )
    if summary.get("comparedWindowSetPurposes") != sorted(
        compared_window_set_purposes
    ):
        raise ValueError(
            "optimizer job shadow compare summary comparedWindowSetPurposes mismatch"
        )
    if summary.get("comparedComparisonDimensions") != sorted(
        compared_comparison_dimensions
    ):
        raise ValueError(
            "optimizer job shadow compare summary comparedComparisonDimensions mismatch"
        )
    if summary.get("comparedSourceLanes") != sorted(compared_source_lanes):
        raise ValueError(
            "optimizer job shadow compare summary comparedSourceLanes mismatch"
        )


def validate_optimizer_job_shadow_compare_batch_manifest_payload(
    payload: dict[str, Any]
) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare a supported schemaVersion"
        )
    if not isinstance(payload.get("manifestId"), str) or not payload["manifestId"]:
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare manifestId"
        )
    if not isinstance(payload.get("generatedAt"), str) or not payload["generatedAt"]:
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare generatedAt"
        )
    comparison_dimension = payload.get("comparisonDimension")
    if comparison_dimension not in JOB_SHADOW_COMPARISON_DIMENSIONS:
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare a supported comparisonDimension"
        )
    if (
        not isinstance(payload.get("batchWindowLabel"), str)
        or not payload["batchWindowLabel"]
    ):
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare batchWindowLabel"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare generatedFrom"
        )
    compare_artifact_paths = payload.get("compareArtifactPaths")
    if not isinstance(compare_artifact_paths, list) or not compare_artifact_paths:
        raise ValueError(
            "optimizer job shadow compare batch manifest must declare compareArtifactPaths"
        )
    if generated_from.get("compareArtifactCount") != len(compare_artifact_paths):
        raise ValueError(
            "optimizer job shadow compare batch manifest compareArtifactCount mismatch"
        )
    for index, path_label in enumerate(compare_artifact_paths):
        if not isinstance(path_label, str) or not path_label:
            raise ValueError(
                f"optimizer job shadow compare batch manifest compareArtifactPaths[{index}] must be a non-empty string"
            )


def validate_optimizer_job_shadow_compare_batch_payload(
    payload: dict[str, Any]
) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_JOB_SHADOW_COMPARE_BATCH_SCHEMA_VERSIONS:
        raise ValueError(
            "optimizer job shadow compare batch must declare a supported schemaVersion"
        )
    if not isinstance(payload.get("batchId"), str) or not payload["batchId"]:
        raise ValueError("optimizer job shadow compare batch must declare batchId")
    if not isinstance(payload.get("generatedAt"), str) or not payload["generatedAt"]:
        raise ValueError(
            "optimizer job shadow compare batch must declare generatedAt"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer job shadow compare batch must declare generatedFrom"
        )
    if not isinstance(generated_from.get("sourceMode"), str) or not generated_from.get(
        "sourceMode"
    ):
        raise ValueError(
            "optimizer job shadow compare batch must declare generatedFrom.sourceMode"
        )
    if not isinstance(generated_from.get("sourceDescriptor"), dict):
        raise ValueError(
            "optimizer job shadow compare batch must declare generatedFrom.sourceDescriptor"
        )
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("optimizer job shadow compare batch must declare items")
    if generated_from.get("compareArtifactCount") is None:
        raise ValueError(
            "optimizer job shadow compare batch must declare generatedFrom.compareArtifactCount"
        )
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("optimizer job shadow compare batch must declare summary")
    comparison_dimension = summary.get("comparisonDimension")
    if comparison_dimension not in JOB_SHADOW_COMPARISON_DIMENSIONS:
        raise ValueError(
            "optimizer job shadow compare batch summary must declare a supported comparisonDimension"
        )
    if (
        not isinstance(summary.get("batchWindowLabel"), str)
        or not summary.get("batchWindowLabel")
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary must declare batchWindowLabel"
        )

    matched_count = 0
    compared_compare_ids: set[str] = set()
    compared_plan_ids: set[str] = set()
    compared_schedule_ids: set[str] = set()
    compared_candidate_scheduler_rollout_intents: set[str] = set()
    compared_candidate_rollout_classes: set[str] = set()
    compared_candidate_runtime_profile_rollout_classes: set[str] = set()
    compared_candidate_window_set_purposes: set[str] = set()
    compared_candidate_comparison_dimensions: set[str] = set()
    compared_candidate_source_lanes: set[str] = set()
    grouped_items: dict[str, list[dict[str, Any]]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("optimizer job shadow compare batch items must be objects")
        label = f"optimizer job shadow compare batch items[{index}]"
        for field_name in (
            "compareId",
            "compareSchemaVersion",
            "comparePlanId",
            "comparisonId",
            "scheduleId",
            "cadenceKind",
            "jobKind",
            "baselineSchedulerRolloutIntent",
            "baselineRolloutClass",
            "candidateSchedulerRolloutIntent",
            "candidateRolloutClass",
            "candidateRuntimeProfileRolloutClass",
            "candidateSourceLane",
        ):
            if not isinstance(item.get(field_name), str) or not item[field_name]:
                raise ValueError(f"{label} must declare {field_name}")
        for optional_field_name in (
            "baselineRuntimeProfileRolloutClass",
            "baselineWindowSetPurpose",
            "baselineComparisonDimension",
            "candidateWindowSetPurpose",
            "candidateComparisonDimension",
        ):
            optional_value = item.get(optional_field_name)
            if optional_value is not None and (
                not isinstance(optional_value, str) or not optional_value
            ):
                raise ValueError(
                    f"{label} {optional_field_name} must be a non-empty string when present"
                )
        baseline_source_lane = item.get("baselineSourceLane")
        if baseline_source_lane is not None and (
            not isinstance(baseline_source_lane, str) or not baseline_source_lane
        ):
            raise ValueError(
                f"{label} baselineSourceLane must be a non-empty string when present"
            )
        semantic_match = item.get("semanticMatch")
        if not isinstance(semantic_match, bool):
            raise ValueError(f"{label} must declare semanticMatch")
        semantic_diff_keys = item.get("semanticDiffKeys")
        if not isinstance(semantic_diff_keys, list):
            raise ValueError(f"{label} must declare semanticDiffKeys")
        if semantic_match != (len(semantic_diff_keys) == 0):
            raise ValueError(
                f"{label} semanticMatch must agree with semanticDiffKeys"
            )
        if semantic_match:
            matched_count += 1
        compared_compare_ids.add(item["compareId"])
        compared_plan_ids.add(item["comparePlanId"])
        compared_schedule_ids.add(item["scheduleId"])
        compared_candidate_scheduler_rollout_intents.add(
            item["candidateSchedulerRolloutIntent"]
        )
        compared_candidate_rollout_classes.add(item["candidateRolloutClass"])
        compared_candidate_runtime_profile_rollout_classes.add(
            item["candidateRuntimeProfileRolloutClass"]
        )
        if item.get("candidateWindowSetPurpose"):
            compared_candidate_window_set_purposes.add(
                item["candidateWindowSetPurpose"]
            )
        if item.get("candidateComparisonDimension"):
            compared_candidate_comparison_dimensions.add(
                item["candidateComparisonDimension"]
            )
        compared_candidate_source_lanes.add(item["candidateSourceLane"])
        group_value = item.get(comparison_dimension)
        group_key = group_value if isinstance(group_value, str) and group_value else "__missing__"
        grouped_items.setdefault(group_key, []).append(item)

    if summary.get("compareArtifactCount") != generated_from.get("compareArtifactCount"):
        raise ValueError(
            "optimizer job shadow compare batch summary compareArtifactCount mismatch"
        )
    if summary.get("comparisonCount") != len(items):
        raise ValueError(
            "optimizer job shadow compare batch summary comparisonCount mismatch"
        )
    if summary.get("matchedComparisonCount") != matched_count:
        raise ValueError(
            "optimizer job shadow compare batch summary matchedComparisonCount mismatch"
        )
    if summary.get("mismatchedComparisonCount") != len(items) - matched_count:
        raise ValueError(
            "optimizer job shadow compare batch summary mismatchedComparisonCount mismatch"
        )
    if summary.get("comparedCompareIds") != sorted(compared_compare_ids):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCompareIds mismatch"
        )
    if summary.get("comparedPlanIds") != sorted(compared_plan_ids):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedPlanIds mismatch"
        )
    if summary.get("comparedScheduleIds") != sorted(compared_schedule_ids):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedScheduleIds mismatch"
        )
    if summary.get("comparedCandidateSchedulerRolloutIntents") != sorted(
        compared_candidate_scheduler_rollout_intents
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCandidateSchedulerRolloutIntents mismatch"
        )
    if summary.get("comparedCandidateRolloutClasses") != sorted(
        compared_candidate_rollout_classes
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCandidateRolloutClasses mismatch"
        )
    if summary.get("comparedCandidateRuntimeProfileRolloutClasses") != sorted(
        compared_candidate_runtime_profile_rollout_classes
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCandidateRuntimeProfileRolloutClasses mismatch"
        )
    if summary.get("comparedCandidateWindowSetPurposes") != sorted(
        compared_candidate_window_set_purposes
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCandidateWindowSetPurposes mismatch"
        )
    if summary.get("comparedCandidateComparisonDimensions") != sorted(
        compared_candidate_comparison_dimensions
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCandidateComparisonDimensions mismatch"
        )
    if summary.get("comparedCandidateSourceLanes") != sorted(
        compared_candidate_source_lanes
    ):
        raise ValueError(
            "optimizer job shadow compare batch summary comparedCandidateSourceLanes mismatch"
        )
    group_summaries = payload.get("groupSummaries")
    if not isinstance(group_summaries, list):
        raise ValueError(
            "optimizer job shadow compare batch must declare groupSummaries"
        )
    if summary.get("groupCount") != len(group_summaries):
        raise ValueError(
            "optimizer job shadow compare batch summary groupCount mismatch"
        )
    expected_group_summaries: list[dict[str, Any]] = []
    for group_key in sorted(grouped_items):
        group = grouped_items[group_key]
        group_match_count = sum(1 for item in group if item.get("semanticMatch"))
        expected_group_summaries.append(
            {
                "groupValue": None if group_key == "__missing__" else group_key,
                "comparisonCount": len(group),
                "matchedComparisonCount": group_match_count,
                "mismatchedComparisonCount": len(group) - group_match_count,
                "comparedCompareIds": sorted(
                    {
                        item["compareId"]
                        for item in group
                        if isinstance(item.get("compareId"), str)
                        and item.get("compareId")
                    }
                ),
                "candidateRolloutClasses": sorted(
                    {
                        item["candidateRolloutClass"]
                        for item in group
                        if isinstance(item.get("candidateRolloutClass"), str)
                        and item.get("candidateRolloutClass")
                    }
                ),
                "candidateSchedulerRolloutIntents": sorted(
                    {
                        item["candidateSchedulerRolloutIntent"]
                        for item in group
                        if isinstance(item.get("candidateSchedulerRolloutIntent"), str)
                        and item.get("candidateSchedulerRolloutIntent")
                    }
                ),
                "candidateRuntimeProfileRolloutClasses": sorted(
                    {
                        item["candidateRuntimeProfileRolloutClass"]
                        for item in group
                        if isinstance(
                            item.get("candidateRuntimeProfileRolloutClass"), str
                        )
                        and item.get("candidateRuntimeProfileRolloutClass")
                    }
                ),
                "candidateWindowSetPurposes": sorted(
                    {
                        item["candidateWindowSetPurpose"]
                        for item in group
                        if isinstance(item.get("candidateWindowSetPurpose"), str)
                        and item.get("candidateWindowSetPurpose")
                    }
                ),
                "candidateComparisonDimensions": sorted(
                    {
                        item["candidateComparisonDimension"]
                        for item in group
                        if isinstance(item.get("candidateComparisonDimension"), str)
                        and item.get("candidateComparisonDimension")
                    }
                ),
                "candidateSourceLanes": sorted(
                    {
                        item["candidateSourceLane"]
                        for item in group
                        if isinstance(item.get("candidateSourceLane"), str)
                        and item.get("candidateSourceLane")
                    }
                ),
            }
        )
    if group_summaries != expected_group_summaries:
        raise ValueError(
            "optimizer job shadow compare batch groupSummaries mismatch"
        )


def load_optimizer_job_shadow_compare(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("optimizer job shadow compare payload must be a JSON object")
    validate_optimizer_job_shadow_compare_payload(payload)
    return payload


def load_optimizer_job_shadow_compare_batch_manifest(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(
            "optimizer job shadow compare batch manifest must be a JSON object"
        )
    validate_optimizer_job_shadow_compare_batch_manifest_payload(payload)
    return payload


def load_optimizer_job_shadow_compare_batch(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(
            "optimizer job shadow compare batch payload must be a JSON object"
        )
    validate_optimizer_job_shadow_compare_batch_payload(payload)
    return payload
