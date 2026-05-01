#!/usr/bin/env python3
"""
Reusable ranking helpers for the AutoTikTok topic-ranking skill.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARED_FIXTURE_ROOT = SKILL_ROOT.parent / "autotiktok" / "fixtures"
DEFAULT_DISCOVERY_ARTIFACT = (
    SKILL_ROOT.parent
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)
DEFAULT_RUBRIC = SKILL_ROOT / "config" / "feature-rubric.v1.json"

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

STAGE_MODE_TO_PROFILE = {
    "growth": "growth-default",
    "scale": "scale-default",
    "search_priority": "search-priority-default",
}

OPTIMIZER_HANDOFF_SCHEMA_VERSION = "ranking-optimizer-handoff.v2-preview"
OPTIMIZER_HANDOFF_DEPRECATION_POLICY_SCHEMA_VERSION = (
    "ranking-optimizer-deprecation-policy.v1"
)
OPTIMIZER_HANDOFF_DEPRECATION_PHASE = "dual_write_preview"
OPTIMIZER_HANDOFF_CANONICAL_SURFACE = "optimizerHandoff"
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


def resolve_candidate_source(
    candidates_payload: dict[str, Any], ranking_snapshot_id: str
) -> dict[str, Any]:
    generated_from = candidates_payload.get("generatedFrom", {})
    if not isinstance(generated_from, dict):
        generated_from = {}

    if "schemaVersion" in candidates_payload and "policyVersion" in candidates_payload:
        return {
            "sourceKind": "discovery_artifact",
            "inputSchemaVersion": candidates_payload.get("schemaVersion"),
            "topicCandidateSchemaVersion": "topic-candidate.v1",
            "sourceSnapshotId": candidates_payload.get("snapshotId"),
            "sourcePolicyVersion": candidates_payload.get("policyVersion"),
            "sourceArtifact": None,
            "sourceInputKind": generated_from.get("inputKind"),
            "sourceMaterializationId": generated_from.get("materializationId"),
            "sourceMaterializationSource": generated_from.get("materializationSource"),
            "sourceNormalizationRuleVersion": generated_from.get("normalizationRuleVersion"),
            "sourceTopicAbstractionCount": generated_from.get("topicAbstractionCount"),
            "rankingSnapshotId": ranking_snapshot_id,
        }

    if generated_from:
        return {
            "sourceKind": "derived_shared_fixture",
            "inputSchemaVersion": generated_from.get("schemaVersion"),
            "topicCandidateSchemaVersion": "topic-candidate.v1",
            "sourceSnapshotId": generated_from.get("snapshotId"),
            "sourcePolicyVersion": generated_from.get("policyVersion"),
            "sourceArtifact": generated_from.get("sourceArtifact"),
            "sourceInputKind": None,
            "sourceMaterializationId": None,
            "sourceMaterializationSource": None,
            "sourceNormalizationRuleVersion": None,
            "sourceTopicAbstractionCount": None,
            "rankingSnapshotId": ranking_snapshot_id,
        }

    return {
        "sourceKind": "standalone_candidate_fixture",
        "inputSchemaVersion": candidates_payload.get("fixtureSetVersion"),
        "topicCandidateSchemaVersion": "topic-candidate.v1",
        "sourceSnapshotId": candidates_payload.get("snapshotId"),
        "sourcePolicyVersion": candidates_payload.get("policyVersion"),
        "sourceArtifact": None,
        "sourceInputKind": None,
        "sourceMaterializationId": None,
        "sourceMaterializationSource": None,
        "sourceNormalizationRuleVersion": None,
        "sourceTopicAbstractionCount": None,
        "rankingSnapshotId": ranking_snapshot_id,
    }


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def round2(value: float) -> float:
    return round(value + 1e-9, 2)


def unique_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def normalize_token(value: str) -> str:
    normalized = "".join(
        character.lower() if character.isalnum() else " " for character in value
    )
    return " ".join(part for part in normalized.split() if part)


def feature_score(score: float, confidence: float, evidence_refs: list[str], reason: str) -> dict[str, Any]:
    return {
        "score": round2(clamp(score, 1.0, 5.0)),
        "confidence": round2(clamp(confidence, 0.0, 1.0)),
        "evidenceRefs": unique_preserve([item for item in evidence_refs if item]),
        "reason": reason,
    }


def keyword_overlap(candidate: dict[str, Any], context: dict[str, Any]) -> float:
    candidate_text = " ".join(
        [
            candidate.get("topicTitle", ""),
            candidate.get("topicSummary", ""),
            " ".join(candidate.get("keywords", [])),
        ]
    ).lower()
    niche = str(context.get("niche", "")).lower()
    if not niche:
        return 0.0
    niche_terms = {part for part in niche.replace("-", " ").split() if len(part) > 2}
    matches = sum(1 for term in niche_terms if term in candidate_text)
    return matches / max(len(niche_terms), 1)


def format_overlap(candidate_formats: list[str], accepted_formats: list[str]) -> float:
    if not candidate_formats:
        return 0.0
    accepted = set(accepted_formats)
    overlap = sum(1 for item in candidate_formats if item in accepted)
    return overlap / len(candidate_formats)


def capability_overlap(candidate_caps: list[str], context_assets: list[str]) -> float:
    if not candidate_caps:
        return 0.0
    normalized_assets = " ".join(context_assets).lower()
    hits = 0
    for capability in candidate_caps:
        words = [word for word in capability.lower().split() if len(word) > 2]
        if any(word in normalized_assets for word in words):
            hits += 1
    return hits / len(candidate_caps)


def _dimension_config(rubric: dict[str, Any], name: str) -> dict[str, Any]:
    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, dict) or name not in dimensions:
        raise ValueError(f"rubric missing dimension config for `{name}`")
    config = dimensions[name]
    if not isinstance(config, dict):
        raise ValueError(f"rubric dimension `{name}` must be an object")
    return config


def validate_rubric(rubric: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if rubric.get("schemaVersion") != "feature-rubric.v1":
        errors.append("rubric has unexpected schemaVersion")
    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, dict):
        return [*errors, "rubric.dimensions must be an object"]
    missing_dimensions = set(FEATURE_KEYS) - set(dimensions.keys())
    if missing_dimensions:
        errors.append(
            "rubric.dimensions missing keys: " + ", ".join(sorted(missing_dimensions))
        )
    rerank = rubric.get("rerank")
    if not isinstance(rerank, dict):
        errors.append("rubric.rerank must be an object")
    return errors


def resolve_profile(
    requested_profile_id: str, context: dict[str, Any], profiles_payload: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    profiles = profiles_payload.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("profiles payload must include a non-empty `profiles` list")

    stage_mode = str(context.get("stageMode", "")).strip()
    if requested_profile_id in {"", "auto", "context"}:
        if stage_mode not in STAGE_MODE_TO_PROFILE:
            raise ValueError(
                f"cannot auto-select profile for unknown stageMode `{stage_mode}`"
            )
        resolved_profile_id = STAGE_MODE_TO_PROFILE[stage_mode]
        selection_source = "context_stage_mode"
    else:
        resolved_profile_id = requested_profile_id
        selection_source = "explicit"

    profile = next(
        (item for item in profiles if item.get("profileId") == resolved_profile_id),
        None,
    )
    if profile is None:
        raise ValueError(f"unknown profileId `{resolved_profile_id}`")

    return profile, {
        "requestedProfileId": requested_profile_id,
        "resolvedProfileId": resolved_profile_id,
        "stageMode": stage_mode,
        "selectionSource": selection_source,
    }


def build_feature_vector(candidate: dict[str, Any], context: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    source_refs = candidate.get("sourceRef", [])
    source_count = len(source_refs)
    search = candidate.get("searchEvidence", {})
    execution = candidate.get("executionProfile", {})
    seed_queries = search.get("seedQueries", [])
    related_queries = search.get("relatedQueries", [])
    content_gap_queries = search.get("contentGapQueries", [])
    content_angles = candidate.get("contentAngle", [])
    recommended_formats = execution.get("recommendedFormats", [])
    required_assets = execution.get("requiredAssets", [])
    required_capabilities = execution.get("requiredCapabilities", [])
    expandability = float(candidate.get("expandability", 0.0))
    complexity = float(execution.get("productionComplexity", 1.0))
    dependency_risk = execution.get("dependencyRisk", "medium")
    freshness = candidate.get("freshnessWindow", "weekly")
    topic_type = candidate.get("topicType", "trend")
    recommended_mode = candidate.get("recommendedMode", "growth")
    title = str(candidate.get("topicTitle", "")).lower()

    search_signal_count = len(seed_queries) + len(related_queries) + len(content_gap_queries)

    demand_cfg = _dimension_config(rubric, "demand")
    demand_score = float(demand_cfg["base"])
    demand_score += float(demand_cfg["searchSignalWeight"]) * min(
        search_signal_count, int(demand_cfg["searchSignalCap"])
    )
    demand_score += float(demand_cfg["sourceWeight"]) * min(
        source_count, int(demand_cfg["sourceCap"])
    )
    demand_score += float(demand_cfg["topicTypeBonus"].get(topic_type, 0.0))
    demand_score += float(demand_cfg["freshnessBonus"].get(freshness, 0.0))
    demand = feature_score(
        demand_score,
        float(
            demand_cfg["richSignalConfidence"]
            if search_signal_count >= 3
            else demand_cfg["sparseSignalConfidence"]
        ),
        list(source_refs[:3]),
        f"{search_signal_count} search signals and {source_count} supporting sources indicate sustained demand.",
    )

    competition_cfg = _dimension_config(rubric, "competition")
    competition_score = float(competition_cfg["base"])
    competition_score += float(competition_cfg["topicTypeBonus"].get(topic_type, 0.0))
    competition_score += float(competition_cfg["freshnessBonus"].get(freshness, 0.0))
    if source_count >= int(competition_cfg["sourceDensityThreshold"]):
        competition_score += float(competition_cfg["sourceDensityBonus"])
    competition = feature_score(
        competition_score,
        float(competition_cfg["confidence"]),
        list(source_refs[:2]),
        "Fresh trend density and broad source support imply higher crowding pressure."
        if topic_type == "trend"
        else "Practical or evergreen framing reduces crowding pressure compared with trend reactions.",
    )

    fit_cfg = _dimension_config(rubric, "fit")
    fit_score = float(fit_cfg["base"])
    fit_score += float(fit_cfg["keywordOverlapWeight"]) * keyword_overlap(candidate, context)
    fit_score += float(fit_cfg["formatOverlapWeight"]) * format_overlap(
        recommended_formats, context.get("acceptedFormats", [])
    )
    historical_summary = context.get("historicalPerformanceSummary", {})
    if candidate.get("topicFingerprint") in historical_summary.get("topPerformingTopicFingerprints", []):
        fit_score += float(fit_cfg["historicalWinBonus"])
    if candidate.get("topicFingerprint") in historical_summary.get("weakTopicFingerprints", []):
        fit_score -= float(fit_cfg["historicalWeakPenalty"])
    fit = feature_score(
        fit_score,
        float(fit_cfg["confidence"]),
        [candidate.get("topicFingerprint", "")],
        "Niche match, accepted format overlap, and historical account behavior determine fit.",
    )

    rewrite_cfg = _dimension_config(rubric, "rewrite")
    rewrite_score = float(rewrite_cfg["base"])
    rewrite_score += float(rewrite_cfg["contentAngleWeight"]) * min(
        len(content_angles), int(rewrite_cfg["contentAngleCap"])
    )
    if any(keyword in title for keyword in rewrite_cfg.get("framingKeywords", [])):
        rewrite_score += float(rewrite_cfg["framingBonus"])
    rewrite = feature_score(
        rewrite_score,
        float(rewrite_cfg["confidence"]),
        list(candidate.get("sourceRef", [])[:2]),
        f"{len(content_angles)} distinct angles create room for original packaging.",
    )

    series_cfg = _dimension_config(rubric, "series")
    series_score = float(series_cfg["base"]) + float(series_cfg["expandabilityWeight"]) * expandability
    if recommended_mode == "series":
        series_score += float(series_cfg["seriesModeBonus"])
    if freshness == "evergreen":
        series_score += float(series_cfg["evergreenBonus"])
    series = feature_score(
        series_score,
        float(series_cfg["confidence"]),
        [candidate.get("topicFingerprint", "")],
        "Expandability and mode intent drive whether the topic can support a repeatable series.",
    )

    search_capture_cfg = _dimension_config(rubric, "searchCapture")
    search_capture_score = float(search_capture_cfg["base"])
    search_capture_score += float(search_capture_cfg["searchSignalWeight"]) * min(
        search_signal_count, int(search_capture_cfg["searchSignalCap"])
    )
    search_capture_score += float(
        search_capture_cfg["persistenceBonus"].get(search.get("searchPersistenceHint"), 0.0)
    )
    if content_gap_queries:
        search_capture_score += float(search_capture_cfg["contentGapBonus"])
    search_capture = feature_score(
        search_capture_score,
        float(
            search_capture_cfg["richSignalConfidence"]
            if search_signal_count >= 2
            else search_capture_cfg["sparseSignalConfidence"]
        ),
        list(seed_queries[:2]) + list(related_queries[:1]),
        "Query richness, persistence, and content-gap support determine search capture strength.",
    )

    longform_cfg = _dimension_config(rubric, "longform")
    longform_score = float(longform_cfg["base"]) + float(longform_cfg["expandabilityWeight"]) * expandability
    if topic_type == "evergreen":
        longform_score += float(longform_cfg["evergreenBonus"])
    longform_score += float(longform_cfg.get("searchIntentBonus", {}).get(search.get("searchIntentType"), 0.0))
    longform = feature_score(
        longform_score,
        float(longform_cfg["confidence"]),
        [candidate.get("topicFingerprint", "")],
        "Expandability plus evergreen or analytical framing drives longform potential.",
    )

    feasibility_cfg = _dimension_config(rubric, "feasibility")
    feasibility_score = float(feasibility_cfg["base"])
    feasibility_score -= float(feasibility_cfg["productionComplexityWeight"]) * complexity
    feasibility_score += float(feasibility_cfg["formatOverlapWeight"]) * format_overlap(
        recommended_formats, context.get("acceptedFormats", [])
    )
    feasibility_score += float(feasibility_cfg["capabilityOverlapWeight"]) * capability_overlap(
        required_capabilities, context.get("availableAssetTypes", [])
    )
    if execution.get("fastTurnaround"):
        feasibility_score += float(feasibility_cfg["fastTurnaroundBonus"])
    feasibility_score += float(feasibility_cfg["dependencyRiskBonus"].get(dependency_risk, 0.0))
    feasibility = feature_score(
        feasibility_score,
        float(feasibility_cfg["confidence"]),
        list(recommended_formats[:2]) + list(required_assets[:1]),
        "Complexity, turnaround speed, format overlap, and dependency risk determine feasibility.",
    )

    return {
        "schemaVersion": "feature-vector.v1",
        "demand": demand,
        "competition": competition,
        "fit": fit,
        "rewrite": rewrite,
        "series": series,
        "searchCapture": search_capture,
        "longform": longform,
        "feasibility": feasibility,
    }


def choose_priority(score_total: float, profile: dict[str, Any]) -> str:
    if score_total >= float(profile.get("p0Threshold", 4.0)):
        return "P0"
    if score_total >= float(profile.get("p1Threshold", 3.0)):
        return "P1"
    return "P2"


def choose_recommended_use(candidate: dict[str, Any], feature_vector: dict[str, Any], rubric: dict[str, Any]) -> str:
    use_cfg = rubric["recommendedUse"]
    if feature_vector["searchCapture"]["score"] >= float(use_cfg["searchCaptureThreshold"]):
        return "search_capture"
    if candidate.get("recommendedMode") == "series" or feature_vector["series"]["score"] >= float(
        use_cfg["seriesThreshold"]
    ):
        return "series_seed"
    if feature_vector["longform"]["score"] >= float(use_cfg["longformThreshold"]):
        return "longform_expand"
    return "growth"


def choose_next_action(priority: str, feasibility_score: float, rubric: dict[str, Any]) -> str:
    action_cfg = rubric["nextAction"]
    if priority == action_cfg["generateScriptPriority"] and feasibility_score >= float(
        action_cfg["generateScriptFeasibilityThreshold"]
    ):
        return "generate_script"
    if priority in set(action_cfg["backupPriorities"]):
        return "hold_as_backup"
    return "not_recommended"


def build_risk_flags(candidate: dict[str, Any], feature_vector: dict[str, Any], rubric: dict[str, Any]) -> list[str]:
    risk_cfg = rubric["riskFlags"]
    flags: list[str] = []
    if feature_vector["competition"]["score"] >= float(risk_cfg["highCompetitionThreshold"]):
        flags.append("high_competition_density")
    if feature_vector["feasibility"]["score"] <= float(risk_cfg["executionRiskThreshold"]):
        flags.append("execution_risk")
    if feature_vector["searchCapture"]["score"] <= float(risk_cfg["weakSearchCaptureThreshold"]):
        flags.append("weak_search_capture")
    if candidate.get("freshnessWindow") == risk_cfg["dailyFreshnessValue"]:
        flags.append("short_freshness_window")
    return flags


def build_score_reason(candidate: dict[str, Any], feature_vector: dict[str, Any], priority: str) -> str:
    return (
        f"{candidate['topicTitle']} is rated {priority} because demand, fit, and feasibility "
        f"outweigh competition, with searchCapture={feature_vector['searchCapture']['score']} "
        f"and series={feature_vector['series']['score']}."
    )


def score_candidate(
    candidate: dict[str, Any], context: dict[str, Any], profile: dict[str, Any], rubric: dict[str, Any]
) -> dict[str, Any]:
    feature_vector = build_feature_vector(candidate, context, rubric)
    weights = profile["weights"]
    weighted_total = (
        feature_vector["demand"]["score"] * weights["demand"]
        + feature_vector["fit"]["score"] * weights["fit"]
        + feature_vector["rewrite"]["score"] * weights["rewrite"]
        + feature_vector["series"]["score"] * weights["series"]
        + feature_vector["searchCapture"]["score"] * weights["searchCapture"]
        + feature_vector["longform"]["score"] * weights["longform"]
        + feature_vector["feasibility"]["score"] * weights["feasibility"]
        - feature_vector["competition"]["score"] * weights["competition"]
    )
    score_total = round2(clamp(weighted_total, 0.0, 5.0))
    priority = choose_priority(score_total, profile)
    recommended_use = choose_recommended_use(candidate, feature_vector, rubric)
    risk_flags = build_risk_flags(candidate, feature_vector, rubric)
    next_action = choose_next_action(priority, feature_vector["feasibility"]["score"], rubric)
    reject_below = float(profile.get("rejectBelow", 0.0))
    is_rejected = score_total < reject_below
    primary_angle = normalize_token(
        candidate.get("contentAngle", [""])[0] if candidate.get("contentAngle") else ""
    )
    return {
        "schemaVersion": "topic-score.v1",
        "topicId": candidate["topicId"],
        "topicFingerprint": candidate["topicFingerprint"],
        "profileId": profile["profileId"],
        "topicType": candidate.get("topicType"),
        "recommendedMode": candidate.get("recommendedMode"),
        "freshnessWindow": candidate.get("freshnessWindow"),
        "scoreTotal": score_total,
        "scoreBreakdown": {key: feature_vector[key]["score"] for key in FEATURE_KEYS},
        "priorityLevel": priority,
        "recommendedUse": recommended_use,
        "scoreReason": build_score_reason(candidate, feature_vector, priority),
        "riskFlags": risk_flags,
        "nextAction": next_action,
        "isRejected": is_rejected,
        "rejectionReason": (
            f"scoreTotal {score_total} is below rejectBelow {reject_below}"
            if is_rejected
            else None
        ),
        "primaryContentAngle": primary_angle,
        "featureVector": feature_vector,
    }


def rerank_scores(
    scored: list[dict[str, Any]], rubric: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rerank_cfg = rubric["rerank"]
    ordered = sorted(scored, key=lambda item: item["scoreTotal"], reverse=True)
    final: list[dict[str, Any]] = []
    used_uses: set[str] = set()
    used_topic_types: set[str] = set()
    used_primary_angles: set[str] = set()
    remaining = ordered[:]
    diagnostics: list[dict[str, Any]] = []
    while remaining:
        best_index = 0
        best_adjusted = -999.0
        best_reasons: list[str] = []
        for index, item in enumerate(remaining):
            adjusted = float(item["scoreTotal"])
            reasons: list[str] = []
            if item["recommendedUse"] in used_uses:
                adjusted -= float(rerank_cfg["duplicateRecommendedUsePenalty"])
                reasons.append("duplicate_recommended_use")
            if item.get("topicType") in used_topic_types:
                adjusted -= float(rerank_cfg["duplicateTopicTypePenalty"])
                reasons.append("duplicate_topic_type")
            if item.get("primaryContentAngle") and item["primaryContentAngle"] in used_primary_angles:
                adjusted -= float(rerank_cfg["duplicatePrimaryAnglePenalty"])
                reasons.append("duplicate_primary_angle")
            if item["scoreBreakdown"]["feasibility"] < float(rerank_cfg["lowFeasibilityThreshold"]):
                adjusted -= float(rerank_cfg["lowFeasibilityPenalty"])
                reasons.append("low_feasibility")
            if item.get("isRejected"):
                adjusted -= float(rerank_cfg["rejectedPenalty"])
                reasons.append("below_reject_threshold")
            if adjusted > best_adjusted:
                best_adjusted = adjusted
                best_index = index
                best_reasons = reasons
        chosen = remaining.pop(best_index)
        chosen["rerankAdjustedScore"] = round2(best_adjusted)
        chosen["rerankReasons"] = best_reasons
        final.append(chosen)
        used_uses.add(chosen["recommendedUse"])
        if chosen.get("topicType"):
            used_topic_types.add(chosen["topicType"])
        if chosen.get("primaryContentAngle"):
            used_primary_angles.add(chosen["primaryContentAngle"])
        diagnostics.append(
            {
                "topicId": chosen["topicId"],
                "scoreTotal": chosen["scoreTotal"],
                "rerankAdjustedScore": chosen["rerankAdjustedScore"],
                "reasons": best_reasons,
                "isRejected": chosen.get("isRejected", False),
            }
        )
    return final, diagnostics


def build_prediction_run(
    run_id: str,
    snapshot_id: str,
    created_at: str,
    context: dict[str, Any],
    profile: dict[str, Any],
    profile_selection: dict[str, Any],
    candidate_source: dict[str, Any],
    ranked_scores: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": "prediction-run.v1",
        "runId": run_id,
        "snapshotId": snapshot_id,
        "accountId": context["accountId"],
        "profileId": profile["profileId"],
        "profileSelectionSource": profile_selection["selectionSource"],
        "topicCandidateSchemaVersion": candidate_source["topicCandidateSchemaVersion"],
        "candidateInputSchemaVersion": candidate_source["inputSchemaVersion"],
        "candidateSourceKind": candidate_source["sourceKind"],
        "candidateSourceSnapshotId": candidate_source["sourceSnapshotId"],
        "candidateSourcePolicyVersion": candidate_source["sourcePolicyVersion"],
        "candidateSourceInputKind": candidate_source.get("sourceInputKind"),
        "candidateSourceMaterializationId": candidate_source.get("sourceMaterializationId"),
        "candidateSourceNormalizationRuleVersion": candidate_source.get(
            "sourceNormalizationRuleVersion"
        ),
        "scoringContextSchemaVersion": "scoring-context.v1",
        "scoringCodeVersion": "dry-run-ranking.v2",
        "createdAt": created_at,
        "candidateCount": len(ranked_scores),
        "rankedTopicIds": [item["topicId"] for item in ranked_scores],
    }


def build_optimizer_handoff(
    *,
    profile_id: str,
    profile_selection: dict[str, Any],
    candidate_source: dict[str, Any],
    scores: list[dict[str, Any]],
    prediction_run: dict[str, Any],
    ranking_summary: dict[str, Any],
    rerank_diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": OPTIMIZER_HANDOFF_SCHEMA_VERSION,
        "deprecatedTopLevelFields": list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
        "deprecationPolicy": {
            "schemaVersion": OPTIMIZER_HANDOFF_DEPRECATION_POLICY_SCHEMA_VERSION,
            "phase": OPTIMIZER_HANDOFF_DEPRECATION_PHASE,
            "canonicalSurface": OPTIMIZER_HANDOFF_CANONICAL_SURFACE,
            "deprecatedTopLevelFields": list(
                OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS
            ),
            "exactPreviewRequiresTopLevelMirror": True,
            "compatPreviewUsesLegacyFallback": True,
            "nextHardFailContractVersion": OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION,
        },
        "profileId": profile_id,
        "profileSelection": profile_selection,
        "candidateSource": candidate_source,
        "scores": scores,
        "predictionRun": prediction_run,
        "rankingSummary": ranking_summary,
        "rerankDiagnostics": rerank_diagnostics,
    }


def build_output(
    candidates_payload: dict[str, Any],
    context: dict[str, Any],
    profiles_payload: dict[str, Any],
    rubric: dict[str, Any],
    profile_id: str,
    snapshot_id: str,
    run_id: str,
    created_at: str,
) -> dict[str, Any]:
    candidates = candidates_payload["candidates"]
    profile, profile_selection = resolve_profile(profile_id, context, profiles_payload)
    candidate_source = resolve_candidate_source(candidates_payload, snapshot_id)

    scored = [score_candidate(candidate, context, profile, rubric) for candidate in candidates]
    reranked, rerank_diagnostics = rerank_scores(scored, rubric)
    prediction_run = build_prediction_run(
        run_id,
        snapshot_id,
        created_at,
        context,
        profile,
        profile_selection,
        candidate_source,
        reranked,
    )

    candidate_titles = {item["topicId"]: item["topicTitle"] for item in candidates}
    ranking_summary = {
        "topTopicId": reranked[0]["topicId"] if reranked else None,
        "topTopicTitle": candidate_titles.get(reranked[0]["topicId"]) if reranked else None,
        "priorityCounts": {
            level: sum(1 for item in reranked if item["priorityLevel"] == level)
            for level in ("P0", "P1", "P2")
        },
        "rejectedTopicIds": [item["topicId"] for item in reranked if item.get("isRejected")],
    }
    optimizer_handoff = build_optimizer_handoff(
        profile_id=profile["profileId"],
        profile_selection=profile_selection,
        candidate_source=candidate_source,
        scores=reranked,
        prediction_run=prediction_run,
        ranking_summary=ranking_summary,
        rerank_diagnostics=rerank_diagnostics,
    )
    return {
        "schemaVersion": "ranking-output.v1",
        "profileId": profile["profileId"],
        "profileSelection": profile_selection,
        "candidateSource": candidate_source,
        "scores": reranked,
        "predictionRun": prediction_run,
        "rankingSummary": ranking_summary,
        "rerankDiagnostics": rerank_diagnostics,
        "optimizerHandoff": optimizer_handoff,
    }
