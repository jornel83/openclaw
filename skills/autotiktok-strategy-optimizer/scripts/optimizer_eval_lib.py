#!/usr/bin/env python3
"""
Helpers for optimizer eval-run artifacts.
"""

from __future__ import annotations

from typing import Any


def build_optimizer_eval_run_payload(
    *,
    offline_cycle_payload: dict[str, Any],
    eval_run_id: str,
    generated_at: str,
) -> dict[str, Any]:
    cycle_generated_from = offline_cycle_payload.get("generatedFrom", {})
    daily_review = offline_cycle_payload.get("artifacts", {}).get("dailyReview", {})
    weekly_promotion = offline_cycle_payload.get("artifacts", {}).get("weeklyPromotion")
    daily_generated_from = daily_review.get("generatedFrom", {})
    topic_breakdown = daily_review.get("topicRewardBreakdown", {})
    combined_breakdown = daily_review.get("combinedRewardBreakdown", {})
    ranking_review = daily_review.get("rankingReview", {})
    shadow_leaderboard = daily_review.get("shadowLeaderboard", [])
    leader_profile_id = shadow_leaderboard[0]["profileId"] if shadow_leaderboard else None

    return {
        "schemaVersion": "optimizer-eval-run.v1",
        "evalRunId": eval_run_id,
        "generatedAt": generated_at,
        "mode": offline_cycle_payload.get("mode"),
        "summary": {
            "rankingRunId": cycle_generated_from.get("rankingRunId"),
            "rankingSnapshotId": cycle_generated_from.get("rankingSnapshotId"),
            "rankingProfileId": cycle_generated_from.get("rankingProfileId"),
            "evaluationWindow": daily_review.get("evaluationWindow"),
            "topicReward": topic_breakdown.get("topicReward"),
            "performanceReward": combined_breakdown.get("performanceReward"),
            "performanceWeight": combined_breakdown.get("performanceWeight"),
            "combinedReward": combined_breakdown.get("combinedReward"),
            "postCoverageRate": combined_breakdown.get("postCoverageRate"),
            "rejectedCount": ranking_review.get("rejectedCount"),
            "shadowLeaderProfileId": leader_profile_id,
            "challengerInputKind": cycle_generated_from.get("challengerInputKind"),
            "weeklyDecision": None
            if weekly_promotion is None
            else weekly_promotion.get("decision"),
            "selectedChallengerProfileId": None
            if weekly_promotion is None
            else weekly_promotion.get("selectedChallengerProfileId"),
        },
        "metrics": {
            "topicRewardBreakdown": topic_breakdown,
            "combinedRewardBreakdown": combined_breakdown,
            "challengerReview": daily_review.get("challengerReview"),
            "rankingReview": ranking_review,
        },
        "generatedFrom": {
            "optimizerOfflineCycleSchemaVersion": offline_cycle_payload.get(
                "schemaVersion"
            ),
            "optimizerOfflineCycleId": offline_cycle_payload.get("cycleId"),
            "policyVersion": cycle_generated_from.get("policyVersion"),
            "rankingRunId": cycle_generated_from.get("rankingRunId"),
            "rankingSnapshotId": cycle_generated_from.get("rankingSnapshotId"),
            "rankingProfileId": cycle_generated_from.get("rankingProfileId"),
            "challengerSchemaVersion": cycle_generated_from.get(
                "challengerSchemaVersion"
            ),
            "challengerInputKind": cycle_generated_from.get("challengerInputKind"),
            "optimizerInputBundleSchemaVersion": cycle_generated_from.get(
                "optimizerInputBundleSchemaVersion"
            ),
            "optimizerInputBundleId": cycle_generated_from.get("optimizerInputBundleId"),
            "optimizerInputManifestSchemaVersion": cycle_generated_from.get(
                "optimizerInputManifestSchemaVersion"
            ),
            "optimizerInputManifestId": cycle_generated_from.get(
                "optimizerInputManifestId"
            ),
            "optimizerInputSourceRegistrySchemaVersion": cycle_generated_from.get(
                "optimizerInputSourceRegistrySchemaVersion"
            ),
            "optimizerInputSourceRegistryId": cycle_generated_from.get(
                "optimizerInputSourceRegistryId"
            ),
            "optimizerInputArtifactResolverSchemaVersion": cycle_generated_from.get(
                "optimizerInputArtifactResolverSchemaVersion"
            ),
            "optimizerInputArtifactResolverId": cycle_generated_from.get(
                "optimizerInputArtifactResolverId"
            ),
            "optimizerInputSourceProviderCatalogSchemaVersion": cycle_generated_from.get(
                "optimizerInputSourceProviderCatalogSchemaVersion"
            ),
            "optimizerInputSourceProviderCatalogId": cycle_generated_from.get(
                "optimizerInputSourceProviderCatalogId"
            ),
            "optimizerInputSourceProviderRegistrySchemaVersion": cycle_generated_from.get(
                "optimizerInputSourceProviderRegistrySchemaVersion"
            ),
            "optimizerInputSourceProviderRegistryId": cycle_generated_from.get(
                "optimizerInputSourceProviderRegistryId"
            ),
            "optimizerInputSourceArtifactCatalogSchemaVersion": cycle_generated_from.get(
                "optimizerInputSourceArtifactCatalogSchemaVersion"
            ),
            "optimizerInputSourceArtifactCatalogId": cycle_generated_from.get(
                "optimizerInputSourceArtifactCatalogId"
            ),
            "optimizerInputSourceLane": cycle_generated_from.get(
                "optimizerInputSourceLane"
            ),
            "optimizerInputSourceProviderLane": cycle_generated_from.get(
                "optimizerInputSourceProviderLane"
            ),
            "optimizerInputSourceProviderKind": cycle_generated_from.get(
                "optimizerInputSourceProviderKind"
            ),
            "optimizerInputSourceProviderClass": cycle_generated_from.get(
                "optimizerInputSourceProviderClass"
            ),
            "optimizerInputSourceProviderHandle": cycle_generated_from.get(
                "optimizerInputSourceProviderHandle"
            ),
            "optimizerInputSourceProviderLocatorKind": cycle_generated_from.get(
                "optimizerInputSourceProviderLocatorKind"
            ),
            "optimizerInputSourceProviderOwner": cycle_generated_from.get(
                "optimizerInputSourceProviderOwner"
            ),
            "optimizerInputArtifactLocatorKind": cycle_generated_from.get(
                "optimizerInputArtifactLocatorKind"
            ),
            "optimizerInputRolloutPolicySchemaVersion": cycle_generated_from.get(
                "optimizerInputRolloutPolicySchemaVersion"
            ),
            "optimizerInputRolloutPolicyId": cycle_generated_from.get(
                "optimizerInputRolloutPolicyId"
            ),
            "optimizerInputRolloutClass": cycle_generated_from.get(
                "optimizerInputRolloutClass"
            ),
            "optimizerInputLaneSelectionSource": cycle_generated_from.get(
                "optimizerInputLaneSelectionSource"
            ),
            "optimizerInputRolloutStrategy": cycle_generated_from.get(
                "optimizerInputRolloutStrategy"
            ),
            "optimizerInputSources": cycle_generated_from.get(
                "optimizerInputSources",
                daily_generated_from.get("optimizerInputSources", {}),
            ),
            "rankingOptimizerContractId": cycle_generated_from.get(
                "rankingOptimizerContractId"
            ),
            "rankingOptimizerContractVersion": cycle_generated_from.get(
                "rankingOptimizerContractVersion"
            ),
            "rankingOptimizerContractValidationMode": cycle_generated_from.get(
                "rankingOptimizerContractValidationMode"
            ),
            "weeklyReviewWindowSchemaVersion": cycle_generated_from.get(
                "weeklyReviewWindowSchemaVersion"
            ),
            "weeklyReviewWindowId": cycle_generated_from.get(
                "weeklyReviewWindowId"
            ),
        },
        "artifacts": {
            "offlineCycle": offline_cycle_payload,
        },
    }
