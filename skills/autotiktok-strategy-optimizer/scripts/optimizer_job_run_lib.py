#!/usr/bin/env python3
"""
Helpers for scheduler-facing optimizer daily/weekly job run artifacts.
"""

from __future__ import annotations

from typing import Any


def build_optimizer_job_run_payload(
    *,
    job_run_id: str,
    job_kind: str,
    generated_at: str,
    offline_cycle_payload: dict[str, Any],
    eval_run_payload: dict[str, Any],
) -> dict[str, Any]:
    cycle_summary = offline_cycle_payload.get("summary", {})
    cycle_generated_from = offline_cycle_payload.get("generatedFrom", {})
    eval_summary = eval_run_payload.get("summary", {})
    eval_generated_from = eval_run_payload.get("generatedFrom", {})
    daily_review = offline_cycle_payload.get("artifacts", {}).get("dailyReview", {})
    daily_generated_from = daily_review.get("generatedFrom", {})
    weekly_promotion = offline_cycle_payload.get("artifacts", {}).get("weeklyPromotion")
    gate_summary = (
        weekly_promotion.get("gateSummary", {})
        if isinstance(weekly_promotion, dict)
        else {}
    )
    champion_safety_review = (
        weekly_promotion.get("championSafetyReview", {})
        if isinstance(weekly_promotion, dict)
        else {}
    )
    return {
        "schemaVersion": "optimizer-job-run.v1",
        "jobRunId": job_run_id,
        "jobKind": job_kind,
        "generatedAt": generated_at,
        "mode": offline_cycle_payload.get("mode"),
        "summary": {
            "rankingRunId": eval_summary.get("rankingRunId"),
            "rankingSnapshotId": eval_summary.get("rankingSnapshotId"),
            "rankingProfileId": eval_summary.get("rankingProfileId"),
            "evaluationWindow": eval_summary.get("evaluationWindow"),
            "dailyRecommendation": cycle_summary.get("dailyRecommendation"),
            "shadowLeaderProfileId": eval_summary.get("shadowLeaderProfileId"),
            "weeklyDecision": eval_summary.get("weeklyDecision"),
            "selectedChallengerProfileId": eval_summary.get(
                "selectedChallengerProfileId"
            ),
            "optimizerInputManifestId": eval_generated_from.get(
                "optimizerInputManifestId"
            ),
            "optimizerInputBundleId": eval_generated_from.get("optimizerInputBundleId"),
            "offlineCycleId": offline_cycle_payload.get("cycleId"),
            "evalRunId": eval_run_payload.get("evalRunId"),
        },
        "generatedFrom": {
            "optimizerOfflineCycleSchemaVersion": offline_cycle_payload.get(
                "schemaVersion"
            ),
            "optimizerOfflineCycleId": offline_cycle_payload.get("cycleId"),
            "optimizerEvalRunSchemaVersion": eval_run_payload.get("schemaVersion"),
            "optimizerEvalRunId": eval_run_payload.get("evalRunId"),
            "policyVersion": cycle_generated_from.get("policyVersion"),
            "rankingRunId": eval_generated_from.get("rankingRunId"),
            "rankingSnapshotId": eval_generated_from.get("rankingSnapshotId"),
            "rankingProfileId": eval_generated_from.get("rankingProfileId"),
            "optimizerInputBundleSchemaVersion": eval_generated_from.get(
                "optimizerInputBundleSchemaVersion"
            ),
            "optimizerInputBundleId": eval_generated_from.get(
                "optimizerInputBundleId"
            ),
            "optimizerInputManifestSchemaVersion": eval_generated_from.get(
                "optimizerInputManifestSchemaVersion"
            ),
            "optimizerInputManifestId": eval_generated_from.get(
                "optimizerInputManifestId"
            ),
            "optimizerInputSourceRegistrySchemaVersion": eval_generated_from.get(
                "optimizerInputSourceRegistrySchemaVersion"
            ),
            "optimizerInputSourceRegistryId": eval_generated_from.get(
                "optimizerInputSourceRegistryId"
            ),
            "optimizerInputArtifactResolverSchemaVersion": eval_generated_from.get(
                "optimizerInputArtifactResolverSchemaVersion"
            ),
            "optimizerInputArtifactResolverId": eval_generated_from.get(
                "optimizerInputArtifactResolverId"
            ),
            "optimizerInputSourceProviderCatalogSchemaVersion": eval_generated_from.get(
                "optimizerInputSourceProviderCatalogSchemaVersion"
            ),
            "optimizerInputSourceProviderCatalogId": eval_generated_from.get(
                "optimizerInputSourceProviderCatalogId"
            ),
            "optimizerInputSourceProviderRegistrySchemaVersion": eval_generated_from.get(
                "optimizerInputSourceProviderRegistrySchemaVersion"
            ),
            "optimizerInputSourceProviderRegistryId": eval_generated_from.get(
                "optimizerInputSourceProviderRegistryId"
            ),
            "optimizerInputSourceArtifactCatalogSchemaVersion": eval_generated_from.get(
                "optimizerInputSourceArtifactCatalogSchemaVersion"
            ),
            "optimizerInputSourceArtifactCatalogId": eval_generated_from.get(
                "optimizerInputSourceArtifactCatalogId"
            ),
            "optimizerInputSourceLane": eval_generated_from.get(
                "optimizerInputSourceLane"
            ),
            "optimizerInputSourceProviderLane": eval_generated_from.get(
                "optimizerInputSourceProviderLane"
            ),
            "optimizerInputSourceProviderKind": eval_generated_from.get(
                "optimizerInputSourceProviderKind"
            ),
            "optimizerInputSourceProviderClass": eval_generated_from.get(
                "optimizerInputSourceProviderClass"
            ),
            "optimizerInputSourceProviderHandle": eval_generated_from.get(
                "optimizerInputSourceProviderHandle"
            ),
            "optimizerInputSourceProviderLocatorKind": eval_generated_from.get(
                "optimizerInputSourceProviderLocatorKind"
            ),
            "optimizerInputSourceProviderOwner": eval_generated_from.get(
                "optimizerInputSourceProviderOwner"
            ),
            "optimizerInputArtifactLocatorKind": eval_generated_from.get(
                "optimizerInputArtifactLocatorKind"
            ),
            "optimizerInputRolloutPolicySchemaVersion": eval_generated_from.get(
                "optimizerInputRolloutPolicySchemaVersion"
            ),
            "optimizerInputRolloutPolicyId": eval_generated_from.get(
                "optimizerInputRolloutPolicyId"
            ),
            "optimizerInputRolloutClass": eval_generated_from.get(
                "optimizerInputRolloutClass"
            ),
            "optimizerInputLaneSelectionSource": eval_generated_from.get(
                "optimizerInputLaneSelectionSource"
            ),
            "optimizerInputRolloutStrategy": eval_generated_from.get(
                "optimizerInputRolloutStrategy"
            ),
            "optimizerInputSources": eval_generated_from.get(
                "optimizerInputSources",
                cycle_generated_from.get(
                    "optimizerInputSources",
                    daily_generated_from.get("optimizerInputSources", {}),
                ),
            ),
            "rankingOptimizerContractId": eval_generated_from.get(
                "rankingOptimizerContractId"
            ),
            "rankingOptimizerContractVersion": eval_generated_from.get(
                "rankingOptimizerContractVersion"
            ),
            "rankingOptimizerContractValidationMode": eval_generated_from.get(
                "rankingOptimizerContractValidationMode"
            ),
            "weeklyReviewWindowSchemaVersion": eval_generated_from.get(
                "weeklyReviewWindowSchemaVersion"
            ),
            "weeklyReviewWindowId": eval_generated_from.get(
                "weeklyReviewWindowId"
            ),
            "weeklyStageMode": gate_summary.get("weeklyStageMode"),
            "weeklyStagePolicyId": gate_summary.get("weeklyStagePolicyId"),
            "weeklyStagePolicySelectionSource": gate_summary.get(
                "weeklyStagePolicySelectionSource"
            ),
            "minimumAverageRewardDelta": gate_summary.get(
                "minimumAverageRewardDelta"
            ),
            "minimumAverageHoldoutDelta": gate_summary.get(
                "minimumAverageHoldoutDelta"
            ),
            "weeklyRollbackSeverity": champion_safety_review.get("rollbackSeverity"),
        },
        "artifacts": {
            "offlineCycle": offline_cycle_payload,
            "evalRun": eval_run_payload,
        },
    }
