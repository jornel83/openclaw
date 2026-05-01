#!/usr/bin/env python3
"""
Reusable optimizer helpers for the AutoTikTok strategy-optimizer skill.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from typing import Any

from reward_lib import combined_reward, load_json, performance_reward, topic_reward
from optimizer_weekly_window_lib import (
    WEEKLY_REVIEW_WINDOW_SCHEMA_VERSIONS,
    validate_weekly_review_window_payload,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPT_DIR = SKILL_ROOT.parent / "autotiktok" / "scripts"
if str(SHARED_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPT_DIR))

from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_VERSION
from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_ID
from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE

DEFAULT_POLICY = SKILL_ROOT / "config" / "optimizer-policy.v1.json"


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("schemaVersion") != "optimizer-policy.v1":
        errors.append("optimizer policy has unexpected schemaVersion")
    for key in (
        "topicRewardWeights",
        "performanceRewardWeights",
        "performanceWeighting",
        "realizedStrength",
        "topicMetrics",
        "rankingReview",
        "dailyGates",
        "weeklyPromotion",
    ):
        if not isinstance(policy.get(key), dict):
            errors.append(f"optimizer policy field `{key}` must be an object")
    return errors


def load_policy(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    errors = validate_policy(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def realized_strength(item: dict[str, Any], policy: dict[str, Any]) -> float:
    weights = policy["realizedStrength"]
    return round(
        float(weights["SearchLift"]) * float(item["searchLift"])
        + float(weights["FutureVideoDensity"]) * float(item["futureVideoDensity"])
        + float(weights["ContentGapPersistence"]) * float(item["contentGapPersistence"]),
        6,
    )


def ndcg_from_scores(relevances: list[float]) -> float:
    if not relevances:
        return 0.0
    dcg = sum(rel / (math.log2(index + 2)) for index, rel in enumerate(relevances))
    ideal = sorted(relevances, reverse=True)
    ideal_dcg = sum(rel / (math.log2(index + 2)) for index, rel in enumerate(ideal))
    if ideal_dcg == 0:
        return 0.0
    return dcg / ideal_dcg


def build_topic_metrics(
    ranking_payload: dict[str, Any],
    context_payload: dict[str, Any],
    backfills_payload: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    scores = ranking_payload["scores"]
    top_k = int(policy["topicMetrics"]["topK"])
    top_ranked = scores[:top_k]
    backfill_items = backfills_payload["items"]
    strengths = {item["topicId"]: realized_strength(item, policy) for item in backfill_items}
    hit_threshold = float(policy["realizedStrength"]["hitThreshold"])
    top_ids = [item["topicId"] for item in top_ranked]
    all_ids = [item["topicId"] for item in scores]

    hit_at_3 = sum(1 for topic_id in top_ids if strengths.get(topic_id, 0.0) >= hit_threshold) / max(
        len(top_ids), 1
    )
    hit_at_10 = sum(1 for topic_id in all_ids if strengths.get(topic_id, 0.0) >= hit_threshold) / max(
        len(all_ids), 1
    )
    ndcg_at_10 = ndcg_from_scores([strengths.get(topic_id, 0.0) for topic_id in all_ids])

    recommended_uses = [item["recommendedUse"] for item in top_ranked]
    dup_rate = 1 - (len(set(recommended_uses)) / max(len(recommended_uses), 1))
    type_coverage = len(
        {
            item["topicFingerprint"].split(".")[1]
            if "." in item["topicFingerprint"]
            else item["topicFingerprint"]
            for item in top_ranked
        }
    ) / max(len(top_ranked), 1)
    historical_winners = set(
        context_payload.get("historicalPerformanceSummary", {}).get("topPerformingTopicFingerprints", [])
    )
    novelty = sum(1 for item in top_ranked if item["topicFingerprint"] not in historical_winners) / max(
        len(top_ranked), 1
    )
    executable_threshold = float(policy["topicMetrics"]["executableFeasibilityThreshold"])
    executable_rate = sum(
        1 for item in top_ranked if float(item["scoreBreakdown"]["feasibility"]) >= executable_threshold
    ) / max(len(top_ranked), 1)

    metrics = {
        "Hit@3": round(hit_at_3, 6),
        "Hit@10": round(hit_at_10, 6),
        "NDCG@10": round(ndcg_at_10, 6),
        "DupRate": round(dup_rate, 6),
        "TypeCoverage": round(type_coverage, 6),
        "Novelty": round(novelty, 6),
        "ExecutableRate": round(executable_rate, 6),
    }
    realized_rows = [
        {
            "topicId": item["topicId"],
            "topicFingerprint": item["topicFingerprint"],
            "realizedStrength": round(strengths.get(item["topicId"], 0.0), 6),
            "priorityLevel": item["priorityLevel"],
        }
        for item in scores
    ]
    return metrics, realized_rows


def build_performance_summary(
    signals_payload: dict[str, Any],
    ranked_scores: list[dict[str, Any]],
    policy: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    signal_items = signals_payload["items"]
    if not signal_items:
        return None, []
    performance_rows = []
    per_topic_seen: set[str] = set()
    rewards: list[float] = []
    for signal in signal_items:
        metrics = {
            "ViewLift": signal["viewLift"],
            "RetentionProxy": signal.get("retentionProxy"),
            "ShareSaveProxy": signal.get("shareSaveProxy"),
            "FollowConversionProxy": signal.get("followConversionProxy"),
        }
        score = performance_reward(metrics, policy=policy)
        rewards.append(score)
        per_topic_seen.add(signal["topicId"])
        performance_rows.append(
            {
                "topicId": signal["topicId"],
                "postId": signal["postId"],
                "performanceReward": round(score, 6),
                "viewLift": signal["viewLift"],
            }
        )
    top_k = int(policy["topicMetrics"]["topK"])
    coverage = len(per_topic_seen) / max(len(ranked_scores[:top_k]), 1)
    avg_reward = sum(rewards) / len(rewards)
    weighting = policy["performanceWeighting"]
    summary = {
        "performanceReward": round(avg_reward, 6),
        "postCoverageRate": round(coverage, 6),
        "performanceWeight": round(
            min(float(weighting["maxWeight"]), float(weighting["coverageMultiplier"]) * coverage), 6
        ),
    }
    return summary, performance_rows


def build_challenger_rows(
    champion_profile_id: str,
    champion_topic: dict[str, Any],
    champion_combined: dict[str, Any],
    challenger_payload: dict[str, Any],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    daily_gates = policy["dailyGates"]
    rows = []
    input_kind = challenger_payload.get("inputKind", "adjustments")
    for item in challenger_payload["challengers"]:
        if item["profileId"] == champion_profile_id:
            continue
        if input_kind == "observations":
            topic_metrics = item["topicMetrics"]
            topic_reward_value = topic_reward(topic_metrics, policy=policy)
            performance_summary = item["performanceSummary"]
            performance_reward_value = performance_summary["performanceReward"]
            performance_weight = performance_summary["performanceWeight"]
            combined_value = combined_reward(
                topic_reward_value, performance_reward_value, performance_weight
            )
            dup_rate = float(topic_metrics["DupRate"])
            type_coverage = float(topic_metrics["TypeCoverage"])
            executable_rate = float(topic_metrics["ExecutableRate"])
            post_coverage_rate = float(performance_summary["postCoverageRate"])
        else:
            topic_reward_value = max(
                -1.0, min(1.0, champion_topic["topicReward"] + item["topicRewardDelta"])
            )
            performance_reward_value = None
            if champion_combined["performanceReward"] is not None:
                performance_reward_value = max(
                    0.0,
                    min(
                        1.0,
                        champion_combined["performanceReward"]
                        + item.get("performanceRewardDelta", 0.0),
                    ),
                )
            performance_weight = champion_combined["performanceWeight"]
            combined_value = combined_reward(
                topic_reward_value, performance_reward_value, performance_weight
            )
            executable_rate = max(
                0.0,
                min(
                    1.0,
                    champion_topic["executableRate"] + item.get("executableRateDelta", 0.0),
                ),
            )
            dup_rate = max(
                0.0, min(1.0, champion_topic["dupRate"] + item.get("dupRateDelta", 0.0))
            )
            type_coverage = max(
                0.0,
                min(1.0, champion_topic["typeCoverage"] + item.get("typeCoverageDelta", 0.0)),
            )
            post_coverage_rate = champion_combined.get("postCoverageRate", 0.0)
        holdout_delta = float(item.get("holdoutDelta", 0.0))
        hard_gate_pass = (
            executable_rate
            >= champion_topic["executableRate"] - float(daily_gates["maxExecutableRateDrop"])
            and dup_rate <= champion_topic["dupRate"] + float(daily_gates["maxDupRateIncrease"])
            and type_coverage
            >= champion_topic["typeCoverage"] - float(daily_gates["maxTypeCoverageDrop"])
            and holdout_delta >= float(daily_gates["holdoutFloor"])
        )
        rows.append(
            {
                "profileId": item["profileId"],
                "topicReward": round(topic_reward_value, 6),
                "performanceReward": None if performance_reward_value is None else round(performance_reward_value, 6),
                "performanceWeight": performance_weight,
                "combinedReward": round(combined_value, 6),
                "dupRate": round(dup_rate, 6),
                "typeCoverage": round(type_coverage, 6),
                "executableRate": round(executable_rate, 6),
                "holdoutDelta": round(holdout_delta, 6),
                "combinedRewardDelta": round(
                    combined_value - champion_combined["combinedReward"], 6
                ),
                "postCoverageRate": round(post_coverage_rate, 6),
                "daysObserved": int(item.get("daysObserved", 1)),
                "sourceInputKind": input_kind,
                "hardGatePass": hard_gate_pass,
                "notes": item.get("notes", ""),
            }
        )
    rows.sort(key=lambda row: (not row["hardGatePass"], -row["combinedReward"]))
    return rows


def build_challenger_review(
    champion_profile_id: str,
    challenger_payload: dict[str, Any],
    shadow_leaderboard: list[dict[str, Any]],
) -> dict[str, Any]:
    compared_profile_ids = [
        item["profileId"]
        for item in challenger_payload.get("challengers", [])
        if item.get("profileId") != champion_profile_id
    ]
    hard_gate_pass_count = sum(1 for row in shadow_leaderboard if row["hardGatePass"])
    return {
        "inputKind": challenger_payload.get("inputKind", "adjustments"),
        "championProfileId": champion_profile_id,
        "observationWindow": challenger_payload.get("observationWindow"),
        "evaluationWindow": challenger_payload.get("evaluationWindow"),
        "candidateCount": len(compared_profile_ids),
        "hardGatePassCount": hard_gate_pass_count,
        "comparedProfileIds": compared_profile_ids,
        "leaderProfileId": shadow_leaderboard[0]["profileId"] if shadow_leaderboard else None,
    }


def build_ranking_review(
    ranking_payload: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    review_cfg = policy["rankingReview"]
    diagnostics = ranking_payload.get("rerankDiagnostics", [])
    scores = ranking_payload.get("scores", [])
    score_by_topic = {item["topicId"]: item for item in scores}
    rejected_topic_ids = list(ranking_payload.get("rankingSummary", {}).get("rejectedTopicIds", []))

    reason_counts: dict[str, int] = {}
    for row in diagnostics:
        for reason in row.get("reasons", []):
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    suppressed_rows = []
    for row in diagnostics:
        score_total = float(row.get("scoreTotal", 0.0))
        adjusted_score = float(row.get("rerankAdjustedScore", score_total))
        suppression_delta = round(score_total - adjusted_score, 6)
        score_row = score_by_topic.get(row["topicId"], {})
        suppressed_rows.append(
            {
                "topicId": row["topicId"],
                "topicTitle": score_row.get("scoreReason", "").split(" is rated ")[0] or row["topicId"],
                "suppressionDelta": suppression_delta,
                "reasons": row.get("reasons", []),
                "isRejected": bool(row.get("isRejected", False)),
            }
        )

    suppressed_rows.sort(
        key=lambda item: (not item["isRejected"], -item["suppressionDelta"], item["topicId"])
    )
    top_suppressed = suppressed_rows[: int(review_cfg["topSuppressedLimit"])]

    attention_items: list[str] = []
    if rejected_topic_ids:
        attention_items.append(
            f"review rejected topics before promotion analysis: {', '.join(rejected_topic_ids)}"
        )
    if reason_counts.get("duplicate_recommended_use", 0) > 0:
        attention_items.append("watch repeated recommended-use pressure in the top ranked set")
    if reason_counts.get("low_feasibility", 0) > 0:
        attention_items.append("low-feasibility topics are being actively pushed down by rerank")

    top_risk = (
        f"{rejected_topic_ids[0]} fell below the ranking reject threshold and should stay out of champion consideration."
        if rejected_topic_ids
        else "No ranking-layer rejection signal is currently blocking top candidates."
    )

    return {
        "rejectedTopicIds": rejected_topic_ids,
        "rejectedCount": len(rejected_topic_ids),
        "reasonCounts": reason_counts,
        "topSuppressed": top_suppressed,
        "topRisk": top_risk,
        "attentionItems": attention_items,
    }


def build_daily_recommendation(
    combined_breakdown: dict[str, Any], shadow_leaderboard: list[dict[str, Any]]
) -> dict[str, Any]:
    top_challenger = shadow_leaderboard[0] if shadow_leaderboard else None
    if (
        top_challenger
        and top_challenger["hardGatePass"]
        and top_challenger["combinedReward"] > combined_breakdown["combinedReward"]
    ):
        return {
            "kind": "observe_challenger",
            "reason": (
                f"{top_challenger['profileId']} is the current shadow leader but remains offline-only until weekly promotion."
            ),
        }
    return {
        "kind": "keep_champion",
        "reason": "Champion remains the daily default until a challenger clears weekly promotion gates.",
    }


def _infer_stage_mode_from_profile_id(profile_id: Any) -> str | None:
    if not isinstance(profile_id, str) or not profile_id:
        return None
    normalized = profile_id.replace("-", "_")
    if normalized.startswith("growth"):
        return "growth"
    if normalized.startswith("scale"):
        return "scale"
    if normalized.startswith("search_priority"):
        return "search_priority"
    return None


def _resolve_weekly_stage_policy(
    weekly_policy: dict[str, Any],
    *,
    ranking_context: dict[str, Any],
    generated_from: dict[str, Any],
    champion_profile_id: Any,
) -> tuple[dict[str, Any], str | None, str, str]:
    stage_mode = ranking_context.get("stageMode")
    selection_source = "champion_profile_selection"
    if not isinstance(stage_mode, str) or not stage_mode:
        stage_mode = generated_from.get("stageMode")
        selection_source = "weekly_generated_from"
    if not isinstance(stage_mode, str) or not stage_mode:
        stage_mode = _infer_stage_mode_from_profile_id(
            ranking_context.get("resolvedProfileId")
        )
        selection_source = "resolved_profile_inference"
    if not isinstance(stage_mode, str) or not stage_mode:
        stage_mode = _infer_stage_mode_from_profile_id(champion_profile_id)
        selection_source = "champion_profile_inference"
    if not isinstance(stage_mode, str) or not stage_mode:
        stage_mode = None
        selection_source = "default"

    resolved_policy = dict(weekly_policy)
    stage_policy_id = "weekly_promotion.default"
    stage_policies = weekly_policy.get("stagePolicies", {})
    if isinstance(stage_policies, dict) and isinstance(stage_mode, str):
        stage_policy = stage_policies.get(stage_mode)
        if isinstance(stage_policy, dict):
            overrides = stage_policy.get("overrides", {})
            if isinstance(overrides, dict):
                resolved_policy.update(overrides)
            stage_policy_id = str(
                stage_policy.get("policyId", f"weekly_promotion.{stage_mode}")
            )
    return resolved_policy, stage_mode, stage_policy_id, selection_source


def build_weekly_decision(report: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    if report.get("schemaVersion") in WEEKLY_REVIEW_WINDOW_SCHEMA_VERSIONS:
        validate_weekly_review_window_payload(report)
        return build_weekly_decision_from_window(report, policy)

    ranking_context = report.get("rankingContext", {})
    candidate_source = report.get("candidateSource", {})
    weekly, stage_mode, stage_policy_id, stage_policy_selection_source = (
        _resolve_weekly_stage_policy(
            policy["weeklyPromotion"],
            ranking_context=ranking_context,
            generated_from=report.get("generatedFrom", {}),
            champion_profile_id=report.get("profileId"),
        )
    )
    champion = report["combinedRewardBreakdown"]
    topic_breakdown = report["topicRewardBreakdown"]
    challengers = report.get("shadowLeaderboard", [])
    eligible = [
        item
        for item in challengers
        if item["hardGatePass"]
        and item["daysObserved"] >= int(weekly["minDaysObserved"])
        and item["holdoutDelta"] >= float(weekly["holdoutFloor"])
        and item["combinedReward"]
        >= champion["combinedReward"] + float(weekly["minRewardDelta"])
        and item["dupRate"] <= topic_breakdown["dupRate"] + float(weekly["maxDupRateIncrease"])
        and item["executableRate"]
        >= topic_breakdown["executableRate"] - float(weekly["maxExecutableRateDrop"])
        and item["typeCoverage"]
        >= topic_breakdown["typeCoverage"] - float(weekly["maxTypeCoverageDrop"])
    ]
    eligible.sort(key=lambda row: row["combinedReward"], reverse=True)
    winner = eligible[0] if eligible else None

    gate_summary = {
        "requiredDaysObserved": int(weekly["minDaysObserved"]),
        "minimumRewardDelta": float(weekly["minRewardDelta"]),
        "minimumAverageRewardDelta": float(
            weekly.get("minAvgRewardDelta", weekly.get("minRewardDelta", 0.02))
        ),
        "holdoutMustBeNonNegative": float(weekly["holdoutFloor"]) >= 0.0,
        "weeklyStageMode": stage_mode,
        "weeklyStagePolicyId": stage_policy_id,
        "weeklyStagePolicySelectionSource": stage_policy_selection_source,
    }
    generated_from = {
        "policyVersion": policy["schemaVersion"],
        "dailyReviewPolicyVersion": report.get("policyVersion"),
        "dailyReviewRunId": report.get("runId"),
        "dailyReviewRankingSnapshotId": ranking_context.get("snapshotId"),
        "dailyReviewRequestedProfileId": ranking_context.get("requestedProfileId"),
        "dailyReviewResolvedProfileId": ranking_context.get("resolvedProfileId"),
        "dailyReviewProfileSelectionSource": ranking_context.get("selectionSource"),
        "dailyReviewStageMode": ranking_context.get("stageMode"),
        "dailyReviewCandidateSourceKind": candidate_source.get("sourceKind"),
        "dailyReviewCandidateInputSchemaVersion": candidate_source.get("inputSchemaVersion"),
        "dailyReviewCandidateSourceSnapshotId": candidate_source.get("sourceSnapshotId"),
        "dailyReviewCandidateSourcePolicyVersion": candidate_source.get("sourcePolicyVersion"),
        "dailyReviewChallengerInputKind": report.get("generatedFrom", {}).get(
            "challengerInputKind"
        ),
        "dailyReviewRankingOptimizerContractId": report.get("generatedFrom", {}).get(
            "rankingOptimizerContractId",
            RANKING_OPTIMIZER_CONTRACT_ID,
        ),
        "dailyReviewRankingOptimizerContractVersion": report.get("generatedFrom", {}).get(
            "rankingOptimizerContractVersion",
            RANKING_OPTIMIZER_CONTRACT_VERSION,
        ),
        "dailyReviewRankingOptimizerContractValidationMode": report.get(
            "generatedFrom", {}
        ).get(
            "rankingOptimizerContractValidationMode",
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        ),
        "dailyReviewRankingOptimizerContractValidated": bool(
            report.get("generatedFrom", {}).get("rankingOptimizerContractValidated", False)
        ),
        "dailyReviewRankingOptimizerSurfaceSource": report.get("generatedFrom", {}).get(
            "rankingOptimizerSurfaceSource"
        ),
        "dailyReviewRankingOptimizerDeprecationPhase": report.get("generatedFrom", {}).get(
            "rankingOptimizerDeprecationPhase"
        ),
        "dailyReviewRankingOptimizerCanonicalSurface": report.get("generatedFrom", {}).get(
            "rankingOptimizerCanonicalSurface"
        ),
        "dailyReviewRankingOptimizerDeprecatedTopLevelFields": list(
            report.get("generatedFrom", {}).get(
                "rankingOptimizerDeprecatedTopLevelFields", []
            )
        ),
        "dailyReviewRankingOptimizerNextHardFailContractVersion": report.get(
            "generatedFrom", {}
        ).get("rankingOptimizerNextHardFailContractVersion"),
        "dailyReviewRankingOptimizerCompatApplied": bool(
            report.get("generatedFrom", {}).get("rankingOptimizerCompatApplied", False)
        ),
        "dailyReviewRankingOptimizerCompatAliasesApplied": list(
            report.get("generatedFrom", {}).get("rankingOptimizerCompatAliasesApplied", [])
        ),
        "weeklyStageMode": stage_mode,
        "weeklyStagePolicyId": stage_policy_id,
        "weeklyStagePolicySelectionSource": stage_policy_selection_source,
    }

    if winner is None:
        return {
            "schemaVersion": "weekly-promotion-decision.v1",
            "decisionId": "weekly-promotion.autotiktok.fixture.2026-04-20",
            "generatedAt": "2026-04-20T08:00:00Z",
            "sourceReportId": report["reportId"],
            "championProfileId": report["profileId"],
            "championProfileSelection": ranking_context,
            "championCandidateSource": candidate_source,
            "generatedFrom": generated_from,
            "selectedChallengerProfileId": None,
            "decision": "keep_champion",
            "combinedRewardDelta": 0.0,
            "reason": "No challenger cleared the weekly promotion gates with enough observed days and holdout safety.",
            "gateSummary": gate_summary,
        }

    return {
        "schemaVersion": "weekly-promotion-decision.v1",
        "decisionId": "weekly-promotion.autotiktok.fixture.2026-04-20",
        "generatedAt": "2026-04-20T08:00:00Z",
        "sourceReportId": report["reportId"],
        "championProfileId": report["profileId"],
        "championProfileSelection": ranking_context,
        "championCandidateSource": candidate_source,
        "generatedFrom": generated_from,
        "selectedChallengerProfileId": winner["profileId"],
        "decision": "promote",
        "combinedRewardDelta": round(winner["combinedReward"] - champion["combinedReward"], 6),
        "reason": (
            f"{winner['profileId']} clears the weekly promotion gates with non-negative holdout "
            f"performance and a meaningful combined-reward gain."
        ),
        "gateSummary": gate_summary,
    }


def build_weekly_decision_from_window(
    review_window: dict[str, Any], policy: dict[str, Any]
) -> dict[str, Any]:
    ranking_context = review_window.get("championProfileSelection", {})
    candidate_source = review_window.get("championCandidateSource", {})
    window_generated_from = review_window.get("generatedFrom", {})
    weekly, stage_mode, stage_policy_id, stage_policy_selection_source = (
        _resolve_weekly_stage_policy(
            policy["weeklyPromotion"],
            ranking_context=ranking_context,
            generated_from=window_generated_from,
            champion_profile_id=review_window.get("profileId"),
        )
    )
    champion = review_window["aggregatedChampion"]
    challengers = review_window.get("challengerSummaries", [])
    rollback_signals = review_window.get("rollbackSignals", {})

    min_window_entries = int(weekly.get("minWindowEntries", 3))
    min_winning_days = int(weekly.get("minWinningDays", 2))
    min_hard_gate_pass_days = int(
        weekly.get("minHardGatePassDays", min_winning_days)
    )
    min_avg_reward_delta = float(
        weekly.get("minAvgRewardDelta", weekly.get("minRewardDelta", 0.02))
    )
    min_avg_holdout_delta = float(
        weekly.get("minAvgHoldoutDelta", weekly.get("holdoutFloor", 0.0))
    )
    max_post_coverage_rate_drop = float(weekly.get("maxPostCoverageRateDrop", 0.01))
    rollback_min_breach_days = int(weekly.get("rollbackMinBreachDays", 2))
    rollback_holdout_floor = float(weekly.get("rollbackHoldoutFloor", -0.03))
    rollback_reward_floor = float(weekly.get("rollbackCombinedRewardFloor", 0.6))
    rollback_critical_holdout_floor = float(
        weekly.get("rollbackCriticalHoldoutFloor", -0.04)
    )
    rollback_critical_reward_floor = float(
        weekly.get("rollbackCriticalCombinedRewardFloor", 0.58)
    )
    required_reward_horizon_ids = [
        item.get("horizonId")
        for item in review_window.get("rewardHorizonPolicy", {}).get("horizons", [])
        if bool(item.get("required", False))
    ]

    def _gate_evaluation(
        *,
        gate_id: str,
        passed: bool,
        actual_value: Any,
        threshold_value: Any,
        comparator: str,
        category: str,
    ) -> dict[str, Any]:
        return {
            "gateId": gate_id,
            "category": category,
            "passed": bool(passed),
            "actualValue": actual_value,
            "thresholdValue": threshold_value,
            "comparator": comparator,
        }

    candidate_reviews = []
    for item in challengers:
        available_reward_horizon_ids = [
            summary.get("horizonId") for summary in item.get("rewardHorizonSummaries", [])
        ]
        gate_evaluations = [
            _gate_evaluation(
                gate_id="minimum_window_entries",
                passed=item["windowCount"] >= min_window_entries,
                actual_value=int(item["windowCount"]),
                threshold_value=min_window_entries,
                comparator=">=",
                category="coverage",
            ),
            _gate_evaluation(
                gate_id="minimum_days_observed",
                passed=item["daysObservedMax"] >= int(weekly["minDaysObserved"]),
                actual_value=int(item["daysObservedMax"]),
                threshold_value=int(weekly["minDaysObserved"]),
                comparator=">=",
                category="coverage",
            ),
            _gate_evaluation(
                gate_id="minimum_winning_days",
                passed=item["winningDayCount"] >= min_winning_days,
                actual_value=int(item["winningDayCount"]),
                threshold_value=min_winning_days,
                comparator=">=",
                category="performance",
            ),
            _gate_evaluation(
                gate_id="minimum_hard_gate_pass_days",
                passed=item["hardGatePassDayCount"] >= min_hard_gate_pass_days,
                actual_value=int(item["hardGatePassDayCount"]),
                threshold_value=min_hard_gate_pass_days,
                comparator=">=",
                category="safety",
            ),
            _gate_evaluation(
                gate_id="required_reward_horizon_coverage",
                passed=all(
                    horizon_id in available_reward_horizon_ids
                    for horizon_id in required_reward_horizon_ids
                ),
                actual_value=available_reward_horizon_ids,
                threshold_value=required_reward_horizon_ids,
                comparator="contains_all",
                category="coverage",
            ),
            _gate_evaluation(
                gate_id="minimum_holdout_floor",
                passed=item["minHoldoutDelta"] >= float(weekly["holdoutFloor"]),
                actual_value=round(float(item["minHoldoutDelta"]), 6),
                threshold_value=float(weekly["holdoutFloor"]),
                comparator=">=",
                category="safety",
            ),
            _gate_evaluation(
                gate_id="minimum_average_holdout_delta",
                passed=item["avgHoldoutDelta"] >= min_avg_holdout_delta,
                actual_value=round(float(item["avgHoldoutDelta"]), 6),
                threshold_value=min_avg_holdout_delta,
                comparator=">=",
                category="safety",
            ),
            _gate_evaluation(
                gate_id="minimum_average_reward_delta",
                passed=item["avgCombinedRewardDelta"] >= min_avg_reward_delta,
                actual_value=round(float(item["avgCombinedRewardDelta"]), 6),
                threshold_value=min_avg_reward_delta,
                comparator=">=",
                category="performance",
            ),
            _gate_evaluation(
                gate_id="dup_rate_budget",
                passed=item["avgDupRate"]
                <= champion["avgDupRate"] + float(weekly["maxDupRateIncrease"]),
                actual_value=round(float(item["avgDupRate"]), 6),
                threshold_value=round(
                    float(champion["avgDupRate"]) + float(weekly["maxDupRateIncrease"]), 6
                ),
                comparator="<=",
                category="safety",
            ),
            _gate_evaluation(
                gate_id="executable_rate_budget",
                passed=item["avgExecutableRate"]
                >= champion["avgExecutableRate"] - float(weekly["maxExecutableRateDrop"]),
                actual_value=round(float(item["avgExecutableRate"]), 6),
                threshold_value=round(
                    float(champion["avgExecutableRate"])
                    - float(weekly["maxExecutableRateDrop"]),
                    6,
                ),
                comparator=">=",
                category="safety",
            ),
            _gate_evaluation(
                gate_id="type_coverage_budget",
                passed=item["avgTypeCoverage"]
                >= champion["avgTypeCoverage"] - float(weekly["maxTypeCoverageDrop"]),
                actual_value=round(float(item["avgTypeCoverage"]), 6),
                threshold_value=round(
                    float(champion["avgTypeCoverage"])
                    - float(weekly["maxTypeCoverageDrop"]),
                    6,
                ),
                comparator=">=",
                category="safety",
            ),
            _gate_evaluation(
                gate_id="post_coverage_budget",
                passed=item["avgPostCoverageRate"]
                >= champion["avgPostCoverageRate"] - max_post_coverage_rate_drop,
                actual_value=round(float(item["avgPostCoverageRate"]), 6),
                threshold_value=round(
                    float(champion["avgPostCoverageRate"]) - max_post_coverage_rate_drop,
                    6,
                ),
                comparator=">=",
                category="safety",
            ),
        ]
        failed_gate_ids = [
            gate["gateId"] for gate in gate_evaluations if not bool(gate["passed"])
        ]
        candidate_reviews.append(
            {
                "profileId": item["profileId"],
                "avgCombinedReward": round(float(item["avgCombinedReward"]), 6),
                "avgCombinedRewardDelta": round(
                    float(item["avgCombinedRewardDelta"]), 6
                ),
                "avgHoldoutDelta": round(float(item["avgHoldoutDelta"]), 6),
                "daysObservedMax": int(item["daysObservedMax"]),
                "hardGatePassDayCount": int(item["hardGatePassDayCount"]),
                "eligibleForPromotion": len(failed_gate_ids) == 0,
                "failedGateIds": failed_gate_ids,
                "gateEvaluations": gate_evaluations,
            }
        )

    candidate_reviews.sort(
        key=lambda row: (row["avgCombinedRewardDelta"], row["avgCombinedReward"]),
        reverse=True,
    )
    candidate_review_by_profile = {
        row["profileId"]: row for row in candidate_reviews
    }
    eligible = [
        item
        for item in challengers
        if candidate_review_by_profile.get(item["profileId"], {}).get(
            "eligibleForPromotion"
        )
    ]
    eligible.sort(
        key=lambda row: (row["avgCombinedRewardDelta"], row["avgCombinedReward"]),
        reverse=True,
    )
    winner = eligible[0] if eligible else None
    top_candidate_review = candidate_reviews[0] if candidate_reviews else None

    rollback_triggered = bool(rollback_signals.get("rollbackTriggered", False))
    rollback_eligible = bool(rollback_signals.get("rollbackEligible", False))
    rollback_severity = str(rollback_signals.get("rollbackSeverity", "none"))
    rollback_reason_codes = list(rollback_signals.get("rollbackReasonCodes", []))
    holdout_breach_count = int(champion.get("holdoutFloorBreachCount", 0))
    reward_breach_count = int(champion.get("combinedRewardFloorBreachCount", 0))
    rollback_triggered = rollback_triggered or (
        holdout_breach_count >= rollback_min_breach_days
        or reward_breach_count >= rollback_min_breach_days
    )
    reward_horizon_policy = review_window.get("rewardHorizonPolicy", {})
    reward_horizons = reward_horizon_policy.get("horizons", [])

    gate_summary = {
        "requiredDaysObserved": int(weekly["minDaysObserved"]),
        "minimumWindowEntries": min_window_entries,
        "minimumWinningDays": min_winning_days,
        "minimumHardGatePassDays": min_hard_gate_pass_days,
        "minimumRewardDelta": min_avg_reward_delta,
        "minimumAverageRewardDelta": min_avg_reward_delta,
        "minimumAverageHoldoutDelta": min_avg_holdout_delta,
        "holdoutMustBeNonNegative": float(weekly["holdoutFloor"]) >= 0.0,
        "maximumPostCoverageRateDrop": max_post_coverage_rate_drop,
        "rollbackMinBreachDays": rollback_min_breach_days,
        "rollbackHoldoutFloor": rollback_holdout_floor,
        "rollbackCombinedRewardFloor": rollback_reward_floor,
        "rollbackCriticalHoldoutFloor": rollback_critical_holdout_floor,
        "rollbackCriticalCombinedRewardFloor": rollback_critical_reward_floor,
        "weeklyStageMode": stage_mode,
        "weeklyStagePolicyId": stage_policy_id,
        "weeklyStagePolicySelectionSource": stage_policy_selection_source,
        "rewardHorizonIds": [item.get("horizonId") for item in reward_horizons],
        "requiredRewardHorizonIds": [
            item.get("horizonId")
            for item in reward_horizons
            if bool(item.get("required", False))
        ],
        "optionalRewardHorizonIds": [
            item.get("horizonId")
            for item in reward_horizons
            if not bool(item.get("required", False))
        ],
    }
    generated_from = {
        "policyVersion": policy["schemaVersion"],
        "weeklyReviewWindowSchemaVersion": review_window.get("schemaVersion"),
        "weeklyReviewWindowId": review_window.get("reviewWindowId"),
        "weeklyReviewWindowScenarioId": window_generated_from.get("scenarioId"),
        "weeklyReviewWindowEntryCount": len(review_window.get("windows", [])),
        "dailyReviewPolicyVersion": window_generated_from.get("policyVersion"),
        "dailyReviewRunId": window_generated_from.get("rankingRunId"),
        "dailyReviewRankingSnapshotId": window_generated_from.get("rankingSnapshotId"),
        "dailyReviewRequestedProfileId": window_generated_from.get(
            "requestedProfileId"
        ),
        "dailyReviewResolvedProfileId": window_generated_from.get("resolvedProfileId"),
        "dailyReviewProfileSelectionSource": window_generated_from.get(
            "profileSelectionSource"
        ),
        "dailyReviewStageMode": window_generated_from.get("stageMode"),
        "dailyReviewCandidateSourceKind": window_generated_from.get(
            "candidateSourceKind"
        ),
        "dailyReviewCandidateInputSchemaVersion": window_generated_from.get(
            "candidateInputSchemaVersion"
        ),
        "dailyReviewCandidateSourceSnapshotId": window_generated_from.get(
            "candidateSourceSnapshotId"
        ),
        "dailyReviewCandidateSourcePolicyVersion": window_generated_from.get(
            "candidateSourcePolicyVersion"
        ),
        "dailyReviewChallengerInputKind": window_generated_from.get(
            "challengerInputKind"
        ),
        "dailyReviewRankingOptimizerContractId": window_generated_from.get(
            "rankingOptimizerContractId",
            RANKING_OPTIMIZER_CONTRACT_ID,
        ),
        "dailyReviewRankingOptimizerContractVersion": window_generated_from.get(
            "rankingOptimizerContractVersion",
            RANKING_OPTIMIZER_CONTRACT_VERSION,
        ),
        "dailyReviewRankingOptimizerContractValidationMode": window_generated_from.get(
            "rankingOptimizerContractValidationMode",
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        ),
        "dailyReviewRankingOptimizerContractValidated": bool(
            window_generated_from.get("rankingOptimizerContractValidated", False)
        ),
        "dailyReviewRankingOptimizerSurfaceSource": window_generated_from.get(
            "rankingOptimizerSurfaceSource"
        ),
        "dailyReviewRankingOptimizerDeprecationPhase": window_generated_from.get(
            "rankingOptimizerDeprecationPhase"
        ),
        "dailyReviewRankingOptimizerCanonicalSurface": window_generated_from.get(
            "rankingOptimizerCanonicalSurface"
        ),
        "dailyReviewRankingOptimizerDeprecatedTopLevelFields": list(
            window_generated_from.get("rankingOptimizerDeprecatedTopLevelFields", [])
        ),
        "dailyReviewRankingOptimizerNextHardFailContractVersion": window_generated_from.get(
            "rankingOptimizerNextHardFailContractVersion"
        ),
        "dailyReviewRankingOptimizerCompatApplied": bool(
            window_generated_from.get("rankingOptimizerCompatApplied", False)
        ),
        "dailyReviewRankingOptimizerCompatAliasesApplied": list(
            window_generated_from.get("rankingOptimizerCompatAliasesApplied", [])
        ),
        "weeklyStageMode": stage_mode,
        "weeklyStagePolicyId": stage_policy_id,
        "weeklyStagePolicySelectionSource": stage_policy_selection_source,
    }
    champion_safety_gate_evaluations = [
        _gate_evaluation(
            gate_id="window_level_rollback_signal",
            passed=not bool(rollback_signals.get("rollbackTriggered", False)),
            actual_value=bool(rollback_signals.get("rollbackTriggered", False)),
            threshold_value=False,
            comparator="==",
            category="rollback",
        ),
        _gate_evaluation(
            gate_id="rollback_eligibility",
            passed=not rollback_eligible,
            actual_value=rollback_eligible,
            threshold_value=False,
            comparator="==",
            category="rollback",
        ),
        _gate_evaluation(
            gate_id="holdout_floor_breach_days",
            passed=holdout_breach_count < rollback_min_breach_days,
            actual_value=holdout_breach_count,
            threshold_value=rollback_min_breach_days,
            comparator="<",
            category="rollback",
        ),
        _gate_evaluation(
            gate_id="combined_reward_floor_breach_days",
            passed=reward_breach_count < rollback_min_breach_days,
            actual_value=reward_breach_count,
            threshold_value=rollback_min_breach_days,
            comparator="<",
            category="rollback",
        ),
    ]
    champion_safety_review = {
        "rollbackEligible": rollback_eligible,
        "rollbackTriggered": rollback_triggered,
        "rollbackSeverity": rollback_severity,
        "rollbackReasonCodes": rollback_reason_codes,
        "failedGateIds": [
            gate["gateId"] for gate in champion_safety_gate_evaluations
            if not bool(gate["passed"])
        ],
        "gateEvaluations": champion_safety_gate_evaluations,
    }
    rollback_reason_suffix = ""
    if rollback_reason_codes:
        rollback_reason_suffix = (
            f" Reason codes: {', '.join(rollback_reason_codes)}."
        )

    base_payload = {
        "schemaVersion": "weekly-promotion-decision.v1",
        "decisionId": "weekly-promotion.autotiktok.fixture.2026-04-20",
        "generatedAt": "2026-04-20T08:00:00Z",
        "sourceReportId": window_generated_from.get("sourceReportId"),
        "sourceReviewWindowId": review_window.get("reviewWindowId"),
        "championProfileId": review_window["profileId"],
        "championProfileSelection": ranking_context,
        "championCandidateSource": candidate_source,
        "generatedFrom": generated_from,
        "gateSummary": gate_summary,
        "championSafetyReview": champion_safety_review,
        "promotionCandidateReviews": candidate_reviews,
    }
    if winner is not None:
        return {
            **base_payload,
            "selectedChallengerProfileId": winner["profileId"],
            "decision": "promote",
            "combinedRewardDelta": round(winner["avgCombinedRewardDelta"], 6),
            "reason": (
                f"{winner['profileId']} wins across the weekly review window, clears the "
                "multi-day promotion gates, and does not regress holdout safety."
                if not rollback_eligible
                else f"{winner['profileId']} wins across the weekly review window, clears "
                "the multi-day promotion gates, and replaces a champion already under "
                f"{rollback_severity} rollback review.{rollback_reason_suffix}"
            ),
        }
    if rollback_triggered:
        return {
            **base_payload,
            "selectedChallengerProfileId": None,
            "decision": "rollback_champion",
            "combinedRewardDelta": 0.0,
            "reason": (
                "Champion regressed across the weekly review window and breached the "
                "rollback safety floors before any challenger cleared promotion gates."
                f"{rollback_reason_suffix}"
            ),
        }
    return {
        **base_payload,
        "selectedChallengerProfileId": None,
        "decision": "keep_champion",
        "combinedRewardDelta": 0.0,
        "reason": (
            (
                "No challenger cleared the weekly multi-day promotion gates, and the "
                "champion did not trigger rollback conditions."
            )
            if top_candidate_review is None and not rollback_eligible
            else (
                "No challenger cleared the weekly multi-day promotion gates, and the "
                f"champion remains under {rollback_severity} rollback review."
                f"{rollback_reason_suffix}"
            )
            if top_candidate_review is None
            else (
                f"{top_candidate_review['profileId']} led the challenger slate but failed "
                f"weekly gates: {', '.join(top_candidate_review['failedGateIds'])}."
            )
            if not rollback_eligible
            else (
                f"{top_candidate_review['profileId']} led the challenger slate but failed "
                f"weekly gates: {', '.join(top_candidate_review['failedGateIds'])}. "
                f"Champion remains under {rollback_severity} rollback review."
                f"{rollback_reason_suffix}"
            )
        ),
    }
