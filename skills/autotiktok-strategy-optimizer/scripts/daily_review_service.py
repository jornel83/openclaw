#!/usr/bin/env python3
"""
Service helpers for assembling daily review artifacts.
"""

from __future__ import annotations

from typing import Any

from optimizer_input_adapters import DailyReviewRuntimeInputs
from optimizer_lib import (
    build_challenger_review,
    build_challenger_rows,
    build_daily_recommendation,
    build_performance_summary,
    build_ranking_review,
    build_topic_metrics,
)
from reward_lib import combined_reward, topic_reward


def _build_candidate_source(ranking_payload: dict[str, Any]) -> dict[str, Any]:
    ranking_candidate_source = ranking_payload.get("candidateSource", {})
    if not isinstance(ranking_candidate_source, dict):
        ranking_candidate_source = {}
    prediction_run = ranking_payload["predictionRun"]
    return {
        "sourceKind": ranking_candidate_source.get(
            "sourceKind", prediction_run.get("candidateSourceKind")
        ),
        "inputSchemaVersion": ranking_candidate_source.get(
            "inputSchemaVersion", prediction_run.get("candidateInputSchemaVersion")
        ),
        "topicCandidateSchemaVersion": ranking_candidate_source.get(
            "topicCandidateSchemaVersion",
            prediction_run.get("topicCandidateSchemaVersion"),
        ),
        "sourceSnapshotId": ranking_candidate_source.get(
            "sourceSnapshotId", prediction_run.get("candidateSourceSnapshotId")
        ),
        "sourcePolicyVersion": ranking_candidate_source.get(
            "sourcePolicyVersion", prediction_run.get("candidateSourcePolicyVersion")
        ),
        "sourceArtifact": ranking_candidate_source.get("sourceArtifact"),
        "sourceInputKind": ranking_candidate_source.get(
            "sourceInputKind", prediction_run.get("candidateSourceInputKind")
        ),
        "sourceMaterializationId": ranking_candidate_source.get(
            "sourceMaterializationId",
            prediction_run.get("candidateSourceMaterializationId"),
        ),
        "sourceMaterializationSource": ranking_candidate_source.get(
            "sourceMaterializationSource"
        ),
        "sourceNormalizationRuleVersion": ranking_candidate_source.get(
            "sourceNormalizationRuleVersion",
            prediction_run.get("candidateSourceNormalizationRuleVersion"),
        ),
        "sourceTopicAbstractionCount": ranking_candidate_source.get(
            "sourceTopicAbstractionCount"
        ),
        "rankingSnapshotId": ranking_candidate_source.get(
            "rankingSnapshotId", prediction_run["snapshotId"]
        ),
    }


def _build_ranking_context(ranking_payload: dict[str, Any]) -> dict[str, Any]:
    profile_selection = ranking_payload.get("profileSelection", {})
    if not isinstance(profile_selection, dict):
        profile_selection = {}
    prediction_run = ranking_payload["predictionRun"]
    resolved_profile_id = profile_selection.get(
        "resolvedProfileId", prediction_run["profileId"]
    )
    selection_source = prediction_run.get(
        "profileSelectionSource", profile_selection.get("selectionSource")
    )
    return {
        "snapshotId": prediction_run["snapshotId"],
        "requestedProfileId": profile_selection.get(
            "requestedProfileId", resolved_profile_id
        ),
        "resolvedProfileId": resolved_profile_id,
        "selectionSource": selection_source,
        "stageMode": profile_selection.get("stageMode"),
    }


def build_daily_review_report(
    inputs: DailyReviewRuntimeInputs, *, report_id: str, generated_at: str
) -> dict[str, Any]:
    ranking_payload = inputs.ranking_payload
    ranking_artifact = inputs.ranking_artifact
    policy = inputs.policy
    ranking_context = _build_ranking_context(ranking_payload)
    candidate_source = _build_candidate_source(ranking_payload)
    ranking_schema_version = ranking_artifact.get(
        "schemaVersion",
        ranking_payload["predictionRun"].get("schemaVersion"),
    )

    topic_metrics, realized_outcomes = build_topic_metrics(
        ranking_payload,
        inputs.context_payload,
        inputs.backfills_payload,
        policy,
    )
    topic_reward_value = topic_reward(topic_metrics, policy=policy)
    topic_breakdown = {
        "schemaVersion": "topic-reward-breakdown.v1",
        "rewardId": "topic-reward.autotiktok.daily-review.fixture",
        "runId": ranking_payload["predictionRun"]["runId"],
        "evaluationWindow": inputs.backfills_payload["evaluationWindow"],
        "hitAt3": topic_metrics["Hit@3"],
        "hitAt10": topic_metrics["Hit@10"],
        "ndcgAt10": topic_metrics["NDCG@10"],
        "dupRate": topic_metrics["DupRate"],
        "typeCoverage": topic_metrics["TypeCoverage"],
        "novelty": topic_metrics["Novelty"],
        "executableRate": topic_metrics["ExecutableRate"],
        "topicReward": round(topic_reward_value, 6),
    }

    performance_summary, performance_rows = build_performance_summary(
        inputs.performance_payload,
        ranking_payload["scores"],
        policy,
    )
    performance_reward_value = (
        None
        if performance_summary is None
        else performance_summary["performanceReward"]
    )
    performance_weight = (
        0.0 if performance_summary is None else performance_summary["performanceWeight"]
    )
    combined_breakdown = {
        "schemaVersion": "combined-reward-breakdown.v1",
        "rewardId": "combined-reward.autotiktok.daily-review.fixture",
        "runId": ranking_payload["predictionRun"]["runId"],
        "evaluationWindow": inputs.backfills_payload["evaluationWindow"],
        "topicReward": round(topic_reward_value, 6),
        "performanceReward": performance_reward_value,
        "performanceWeight": performance_weight,
        "postCoverageRate": (
            0.0 if performance_summary is None else performance_summary["postCoverageRate"]
        ),
        "combinedReward": round(
            combined_reward(
                topic_reward_value, performance_reward_value, performance_weight
            ),
            6,
        ),
    }

    ranking_review = build_ranking_review(ranking_payload, policy)
    shadow_leaderboard = build_challenger_rows(
        ranking_payload["predictionRun"]["profileId"],
        topic_breakdown,
        combined_breakdown,
        inputs.challenger_payload,
        policy,
    )
    challenger_review = build_challenger_review(
        ranking_payload["predictionRun"]["profileId"],
        inputs.challenger_payload,
        shadow_leaderboard,
    )
    recommendation = build_daily_recommendation(
        combined_breakdown, shadow_leaderboard
    )

    return {
        "schemaVersion": "daily-review-report.v1",
        "reportId": report_id,
        "generatedAt": generated_at,
        "runId": ranking_payload["predictionRun"]["runId"],
        "profileId": ranking_payload["predictionRun"]["profileId"],
        "policyVersion": policy["schemaVersion"],
        "rankingContext": ranking_context,
        "candidateSource": candidate_source,
        "generatedFrom": {
            "rankingSchemaVersion": ranking_schema_version,
            "rankingRunId": ranking_payload["predictionRun"]["runId"],
            "rankingSnapshotId": ranking_payload["predictionRun"]["snapshotId"],
            "rankingProfileId": ranking_payload["predictionRun"]["profileId"],
            "rankingRequestedProfileId": ranking_context["requestedProfileId"],
            "rankingResolvedProfileId": ranking_context["resolvedProfileId"],
            "rankingProfileSelectionSource": ranking_context["selectionSource"],
            "rankingStageMode": ranking_context["stageMode"],
            "rankingScoringCodeVersion": ranking_payload["predictionRun"][
                "scoringCodeVersion"
            ],
            "rankingCandidateSourceKind": candidate_source["sourceKind"],
            "rankingCandidateInputSchemaVersion": candidate_source[
                "inputSchemaVersion"
            ],
            "rankingCandidateSourceSnapshotId": candidate_source["sourceSnapshotId"],
            "rankingCandidateSourcePolicyVersion": candidate_source[
                "sourcePolicyVersion"
            ],
            "rankingCandidateSourceInputKind": candidate_source["sourceInputKind"],
            "rankingCandidateSourceMaterializationId": candidate_source[
                "sourceMaterializationId"
            ],
            "rankingCandidateSourceMaterializationSource": candidate_source[
                "sourceMaterializationSource"
            ],
            "rankingCandidateSourceNormalizationRuleVersion": candidate_source[
                "sourceNormalizationRuleVersion"
            ],
            "rankingCandidateSourceTopicAbstractionCount": candidate_source[
                "sourceTopicAbstractionCount"
            ],
            **inputs.contract_metadata,
            "backfillsSchemaVersion": inputs.backfills_payload["schemaVersion"],
            "performanceSchemaVersion": inputs.performance_payload["schemaVersion"],
            "challengerSchemaVersion": inputs.challenger_payload["schemaVersion"],
            "challengerInputKind": inputs.challenger_payload.get("inputKind"),
            "optimizerInputBundleSchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputBundleSchemaVersion"
            ),
            "optimizerInputBundleId": inputs.bundle_metadata.get(
                "optimizerInputBundleId"
            ),
            "optimizerInputBundleGeneratedAt": inputs.bundle_metadata.get(
                "optimizerInputBundleGeneratedAt"
            ),
            "optimizerInputBundleGeneratedFrom": inputs.bundle_metadata.get(
                "optimizerInputBundleGeneratedFrom", {}
            ),
            "optimizerInputManifestSchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputManifestSchemaVersion"
            ),
            "optimizerInputManifestId": inputs.bundle_metadata.get(
                "optimizerInputManifestId"
            ),
            "optimizerInputManifestGeneratedAt": inputs.bundle_metadata.get(
                "optimizerInputManifestGeneratedAt"
            ),
            "optimizerInputManifestGeneratedFrom": inputs.bundle_metadata.get(
                "optimizerInputManifestGeneratedFrom", {}
            ),
            "optimizerInputSourceRegistrySchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputSourceRegistrySchemaVersion"
            ),
            "optimizerInputSourceRegistryId": inputs.bundle_metadata.get(
                "optimizerInputSourceRegistryId"
            ),
            "optimizerInputArtifactResolverSchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputArtifactResolverSchemaVersion"
            ),
            "optimizerInputArtifactResolverId": inputs.bundle_metadata.get(
                "optimizerInputArtifactResolverId"
            ),
            "optimizerInputSourceProviderCatalogSchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderCatalogSchemaVersion"
            ),
            "optimizerInputSourceProviderCatalogId": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderCatalogId"
            ),
            "optimizerInputSourceProviderRegistrySchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderRegistrySchemaVersion"
            ),
            "optimizerInputSourceProviderRegistryId": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderRegistryId"
            ),
            "optimizerInputSourceArtifactCatalogSchemaVersion": inputs.bundle_metadata.get(
                "optimizerInputSourceArtifactCatalogSchemaVersion"
            ),
            "optimizerInputSourceArtifactCatalogId": inputs.bundle_metadata.get(
                "optimizerInputSourceArtifactCatalogId"
            ),
            "optimizerInputSourceProviderLane": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderLane"
            ),
            "optimizerInputSourceProviderKind": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderKind"
            ),
            "optimizerInputSourceProviderClass": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderClass"
            ),
            "optimizerInputSourceProviderHandle": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderHandle"
            ),
            "optimizerInputSourceProviderLocatorKind": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderLocatorKind"
            ),
            "optimizerInputSourceProviderOwner": inputs.bundle_metadata.get(
                "optimizerInputSourceProviderOwner"
            ),
            "optimizerInputArtifactLocatorKind": inputs.bundle_metadata.get(
                "optimizerInputArtifactLocatorKind"
            ),
            "optimizerInputSources": inputs.input_source_metadata,
        },
        "evaluationWindow": inputs.backfills_payload["evaluationWindow"],
        "topicRewardBreakdown": topic_breakdown,
        "combinedRewardBreakdown": combined_breakdown,
        "rankingReview": ranking_review,
        "challengerReview": challenger_review,
        "realizedOutcomes": realized_outcomes,
        "postPerformanceRows": performance_rows,
        "diagnostics": {
            "topRisk": ranking_review["topRisk"],
            "topStrength": (
                "search-led and evergreen candidates convert into stronger demand "
                "plus execution scores."
            ),
            "needsAttention": ranking_review["attentionItems"]
            + ["keep post coverage high enough for performance-weighted comparisons"],
        },
        "shadowLeaderboard": shadow_leaderboard,
        "recommendation": recommendation,
    }
