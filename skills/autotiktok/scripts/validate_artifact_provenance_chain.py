#!/usr/bin/env python3
"""
Validate cross-artifact provenance consistency across the AutoTikTok mock pipeline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_ID
from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL
from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE
from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_VERSION
from ranking_optimizer_contract_lib import OPTIMIZER_HANDOFF_CANONICAL_SURFACE
from ranking_optimizer_contract_lib import OPTIMIZER_HANDOFF_DEPRECATION_PHASE
from ranking_optimizer_contract_lib import OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS
from ranking_optimizer_contract_lib import OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION
from ranking_optimizer_contract_lib import validate_ranking_optimizer_contract_metadata


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_PATH = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "fixtures" / "discovery-dry-run.sample.json"
)
SHARED_PATH = ROOT / "skills" / "autotiktok" / "fixtures" / "topic-candidates.fixture.json"
CONTEXT_MATRIX_PATH = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "scoring-context-matrix.fixture.json"
)
RANKING_PATH = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
RANKING_MATRIX_PATH = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-profile-matrix.sample.json"
)
DAILY_PATH = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "daily-review.sample.json"
)
WEEKLY_PATH = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "weekly-promotion.sample.json"
)
OPTIMIZER_MATRIX_PATH = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "optimizer-stage-matrix.sample.json"
)
WORKFLOW_PATH = ROOT / "skills" / "autotiktok" / "fixtures" / "workflow-summary.sample.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def expect_candidate_source_matches_discovery(
    candidate_source: dict[str, Any],
    discovery_payload: dict[str, Any],
    label: str,
    errors: list[str],
) -> None:
    discovery_generated = discovery_payload.get("generatedFrom", {})
    expect(
        candidate_source.get("sourceKind") == "discovery_artifact",
        f"{label} sourceKind should be discovery_artifact",
        errors,
    )
    expect(
        candidate_source.get("inputSchemaVersion") == discovery_payload.get("schemaVersion"),
        f"{label} inputSchemaVersion does not match discovery schemaVersion",
        errors,
    )
    expect(
        candidate_source.get("sourcePolicyVersion") == discovery_payload.get("policyVersion"),
        f"{label} sourcePolicyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        candidate_source.get("sourceSnapshotId") == discovery_payload.get("snapshotId"),
        f"{label} sourceSnapshotId does not match discovery snapshotId",
        errors,
    )
    expect(
        candidate_source.get("sourceInputKind") == discovery_generated.get("inputKind"),
        f"{label} sourceInputKind does not match discovery generatedFrom.inputKind",
        errors,
    )
    expect(
        candidate_source.get("sourceMaterializationId")
        == discovery_generated.get("materializationId"),
        f"{label} sourceMaterializationId does not match discovery generatedFrom.materializationId",
        errors,
    )
    expect(
        candidate_source.get("sourceNormalizationRuleVersion")
        == discovery_generated.get("normalizationRuleVersion"),
        f"{label} sourceNormalizationRuleVersion does not match discovery generatedFrom.normalizationRuleVersion",
        errors,
    )


def expect_stage_profile_consistency(
    stage_entry: dict[str, Any],
    label: str,
    errors: list[str],
) -> None:
    profile_selection = stage_entry.get("profileSelection", {})
    stage_mode = stage_entry.get("stageMode")
    profile_id = stage_entry.get("profileId")
    expect(
        profile_selection.get("stageMode") == stage_mode,
        f"{label} profileSelection.stageMode does not match stageMode",
        errors,
    )
    expect(
        profile_selection.get("resolvedProfileId") == profile_id,
        f"{label} profileSelection.resolvedProfileId does not match profileId",
        errors,
    )


def main() -> int:
    try:
        discovery = load_json(DISCOVERY_PATH)
        shared = load_json(SHARED_PATH)
        context_matrix = load_json(CONTEXT_MATRIX_PATH)
        ranking = load_json(RANKING_PATH)
        ranking_matrix = load_json(RANKING_MATRIX_PATH)
        daily = load_json(DAILY_PATH)
        weekly = load_json(WEEKLY_PATH)
        optimizer_matrix = load_json(OPTIMIZER_MATRIX_PATH)
        workflow = load_json(WORKFLOW_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors: list[str] = []

    discovery_schema = discovery.get("schemaVersion")
    discovery_policy = discovery.get("policyVersion")
    discovery_snapshot = discovery.get("snapshotId")

    shared_generated = shared.get("generatedFrom", {})
    expect(
        shared_generated.get("schemaVersion") == discovery_schema,
        "shared fixture schemaVersion does not match discovery schemaVersion",
        errors,
    )
    expect(
        shared_generated.get("policyVersion") == discovery_policy,
        "shared fixture policyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        shared_generated.get("snapshotId") == discovery_snapshot,
        "shared fixture snapshotId does not match discovery snapshotId",
        errors,
    )

    ranking_source = ranking.get("candidateSource", {})
    ranking_run = ranking.get("predictionRun", {})
    expect_candidate_source_matches_discovery(
        ranking_source,
        discovery,
        "ranking candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateInputSchemaVersion") == ranking_source.get("inputSchemaVersion"),
        "predictionRun candidateInputSchemaVersion does not match ranking candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourcePolicyVersion") == ranking_source.get("sourcePolicyVersion"),
        "predictionRun candidateSourcePolicyVersion does not match ranking candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceSnapshotId") == ranking_source.get("sourceSnapshotId"),
        "predictionRun candidateSourceSnapshotId does not match ranking candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceInputKind") == ranking_source.get("sourceInputKind"),
        "predictionRun candidateSourceInputKind does not match ranking candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceMaterializationId")
        == ranking_source.get("sourceMaterializationId"),
        "predictionRun candidateSourceMaterializationId does not match ranking candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceNormalizationRuleVersion")
        == ranking_source.get("sourceNormalizationRuleVersion"),
        "predictionRun candidateSourceNormalizationRuleVersion does not match ranking candidateSource",
        errors,
    )

    context_matrix_version = context_matrix.get("fixtureSetVersion")
    ranking_matrix_generated = ranking_matrix.get("generatedFrom", {})
    expect(
        ranking_matrix_generated.get("candidateInputSchemaVersion")
        == discovery_schema,
        "ranking profile matrix candidateInputSchemaVersion does not match discovery schemaVersion",
        errors,
    )
    expect(
        ranking_matrix_generated.get("candidateSourceKind") == ranking_source.get("sourceKind"),
        "ranking profile matrix candidateSourceKind does not match ranking candidateSource sourceKind",
        errors,
    )
    expect(
        ranking_matrix_generated.get("discoveryPolicyVersion") == discovery_policy,
        "ranking profile matrix discoveryPolicyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        ranking_matrix_generated.get("contextMatrixFixtureVersion") == context_matrix_version,
        "ranking profile matrix contextMatrixFixtureVersion does not match scoring context matrix fixture",
        errors,
    )
    ranking_matrix_stages = ranking_matrix.get("stages")
    expect(
        isinstance(ranking_matrix_stages, list) and bool(ranking_matrix_stages),
        "ranking profile matrix must include a non-empty stages list",
        errors,
    )
    ranking_matrix_stage_map: dict[str, dict[str, Any]] = {}
    if isinstance(ranking_matrix_stages, list):
        for stage_entry in ranking_matrix_stages:
            if not isinstance(stage_entry, dict):
                errors.append("ranking profile matrix stages must be objects")
                continue
            stage_mode = stage_entry.get("stageMode")
            if not isinstance(stage_mode, str):
                errors.append("ranking profile matrix stages must include stageMode")
                continue
            ranking_matrix_stage_map[stage_mode] = stage_entry
            expect_stage_profile_consistency(
                stage_entry,
                f"ranking profile matrix stage `{stage_mode}`",
                errors,
            )
            candidate_source = stage_entry.get("candidateSource", {})
            if not isinstance(candidate_source, dict):
                errors.append(
                    f"ranking profile matrix stage `{stage_mode}` candidateSource must be an object"
                )
                continue
            expect_candidate_source_matches_discovery(
                candidate_source,
                discovery,
                f"ranking profile matrix stage `{stage_mode}`",
                errors,
            )
            expect(
                stage_entry.get("rankingSnapshotId") == candidate_source.get("rankingSnapshotId"),
                f"ranking profile matrix stage `{stage_mode}` rankingSnapshotId does not match candidateSource",
                errors,
            )

    daily_generated = daily.get("generatedFrom", {})
    daily_source = daily.get("candidateSource", {})
    daily_context = daily.get("rankingContext", {})
    ranking_selection = ranking.get("profileSelection", {})
    expect(
        daily_source == ranking_source,
        "daily-review candidateSource does not match ranking candidateSource",
        errors,
    )
    expect(
        daily_generated.get("rankingSchemaVersion") == ranking.get("schemaVersion"),
        "daily-review rankingSchemaVersion does not match ranking schemaVersion",
        errors,
    )
    expect(
        daily_generated.get("rankingRunId") == ranking_run.get("runId"),
        "daily-review rankingRunId does not match ranking runId",
        errors,
    )
    expect(
        daily_generated.get("rankingSnapshotId") == ranking_run.get("snapshotId"),
        "daily-review rankingSnapshotId does not match ranking snapshotId",
        errors,
    )
    expect(
        daily_generated.get("rankingScoringCodeVersion") == ranking_run.get("scoringCodeVersion"),
        "daily-review rankingScoringCodeVersion does not match ranking scoringCodeVersion",
        errors,
    )
    expect(
        daily_generated.get("rankingRequestedProfileId") == ranking_selection.get("requestedProfileId"),
        "daily-review rankingRequestedProfileId does not match ranking profileSelection",
        errors,
    )
    expect(
        daily_generated.get("rankingResolvedProfileId") == ranking_selection.get("resolvedProfileId"),
        "daily-review rankingResolvedProfileId does not match ranking profileSelection",
        errors,
    )
    expect(
        daily_generated.get("rankingCandidateSourceKind") == ranking_source.get("sourceKind"),
        "daily-review rankingCandidateSourceKind does not match ranking candidateSource",
        errors,
    )
    errors.extend(
        validate_ranking_optimizer_contract_metadata(
            daily_generated,
            label="daily-review generatedFrom",
            expected_contract_id=RANKING_OPTIMIZER_CONTRACT_ID,
            expected_contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
            expected_validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            expected_validated=True,
            expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        )
    )
    expect(
        daily_generated.get("rankingOptimizerSurfaceSource")
        == RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        "daily-review rankingOptimizerSurfaceSource should be legacy_top_level for committed exact-path artifacts",
        errors,
    )
    expect(
        daily_generated.get("rankingOptimizerDeprecationPhase")
        == OPTIMIZER_HANDOFF_DEPRECATION_PHASE,
        "daily-review rankingOptimizerDeprecationPhase should match the preview deprecation phase",
        errors,
    )
    expect(
        daily_generated.get("rankingOptimizerCanonicalSurface")
        == OPTIMIZER_HANDOFF_CANONICAL_SURFACE,
        "daily-review rankingOptimizerCanonicalSurface should match optimizerHandoff",
        errors,
    )
    expect(
        daily_generated.get("rankingOptimizerDeprecatedTopLevelFields")
        == list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
        "daily-review rankingOptimizerDeprecatedTopLevelFields should match the canonical deprecated field set",
        errors,
    )
    expect(
        daily_generated.get("rankingOptimizerNextHardFailContractVersion")
        == OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION,
        "daily-review rankingOptimizerNextHardFailContractVersion should match the next hard-fail contract version",
        errors,
    )
    expect(
        daily_generated.get("rankingOptimizerCompatApplied") is False,
        "daily-review rankingOptimizerCompatApplied should be false for committed exact-path artifacts",
        errors,
    )
    expect(
        daily_generated.get("rankingOptimizerCompatAliasesApplied") == [],
        "daily-review rankingOptimizerCompatAliasesApplied should be empty for committed exact-path artifacts",
        errors,
    )
    expect(
        daily_context.get("snapshotId") == ranking_run.get("snapshotId"),
        "daily-review rankingContext.snapshotId does not match ranking snapshotId",
        errors,
    )

    weekly_generated = weekly.get("generatedFrom", {})
    weekly_selection = weekly.get("championProfileSelection", {})
    weekly_source = weekly.get("championCandidateSource", {})
    expect(
        weekly_selection == daily_context,
        "weekly championProfileSelection does not match daily rankingContext",
        errors,
    )
    expect(
        weekly_source == daily_source,
        "weekly championCandidateSource does not match daily candidateSource",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRunId") == daily.get("runId"),
        "weekly dailyReviewRunId does not match daily-review runId",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewCandidateSourceKind") == daily_source.get("sourceKind"),
        "weekly dailyReviewCandidateSourceKind does not match daily candidateSource",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewCandidateSourceSnapshotId") == daily_source.get("sourceSnapshotId"),
        "weekly dailyReviewCandidateSourceSnapshotId does not match daily candidateSource",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerContractId")
        == daily_generated.get("rankingOptimizerContractId"),
        "weekly dailyReviewRankingOptimizerContractId does not match daily-review contract id",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerContractVersion")
        == daily_generated.get("rankingOptimizerContractVersion"),
        "weekly dailyReviewRankingOptimizerContractVersion does not match daily-review contract version",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerContractValidationMode")
        == daily_generated.get("rankingOptimizerContractValidationMode"),
        "weekly dailyReviewRankingOptimizerContractValidationMode does not match daily-review contract validation mode",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerContractValidated")
        == daily_generated.get("rankingOptimizerContractValidated"),
        "weekly dailyReviewRankingOptimizerContractValidated does not match daily-review contract validation state",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerSurfaceSource")
        == daily_generated.get("rankingOptimizerSurfaceSource"),
        "weekly dailyReviewRankingOptimizerSurfaceSource does not match daily-review surface source",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerDeprecationPhase")
        == daily_generated.get("rankingOptimizerDeprecationPhase"),
        "weekly dailyReviewRankingOptimizerDeprecationPhase does not match daily-review deprecation phase",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerCanonicalSurface")
        == daily_generated.get("rankingOptimizerCanonicalSurface"),
        "weekly dailyReviewRankingOptimizerCanonicalSurface does not match daily-review canonical surface",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerDeprecatedTopLevelFields")
        == daily_generated.get("rankingOptimizerDeprecatedTopLevelFields"),
        "weekly dailyReviewRankingOptimizerDeprecatedTopLevelFields do not match daily-review deprecated fields",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerNextHardFailContractVersion")
        == daily_generated.get("rankingOptimizerNextHardFailContractVersion"),
        "weekly dailyReviewRankingOptimizerNextHardFailContractVersion does not match daily-review next hard-fail version",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerCompatApplied")
        == daily_generated.get("rankingOptimizerCompatApplied"),
        "weekly dailyReviewRankingOptimizerCompatApplied does not match daily-review compat state",
        errors,
    )
    expect(
        weekly_generated.get("dailyReviewRankingOptimizerCompatAliasesApplied")
        == daily_generated.get("rankingOptimizerCompatAliasesApplied"),
        "weekly dailyReviewRankingOptimizerCompatAliasesApplied does not match daily-review compat aliases",
        errors,
    )

    optimizer_matrix_generated = optimizer_matrix.get("generatedFrom", {})
    expect(
        optimizer_matrix_generated.get("candidateInputSchemaVersion")
        == discovery_schema,
        "optimizer stage matrix candidateInputSchemaVersion does not match discovery schemaVersion",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("candidateSourceKind") == ranking_source.get("sourceKind"),
        "optimizer stage matrix candidateSourceKind does not match ranking candidateSource sourceKind",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("discoveryPolicyVersion") == discovery_policy,
        "optimizer stage matrix discoveryPolicyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("contextMatrixFixtureVersion") == context_matrix_version,
        "optimizer stage matrix contextMatrixFixtureVersion does not match scoring context matrix fixture",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("contextMatrixFixtureVersion")
        == ranking_matrix_generated.get("contextMatrixFixtureVersion"),
        "optimizer stage matrix contextMatrixFixtureVersion does not match ranking profile matrix",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingScoringCodeVersion") == ranking_run.get("scoringCodeVersion"),
        "optimizer stage matrix rankingScoringCodeVersion does not match ranking scoringCodeVersion",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("optimizerPolicyVersion") == daily.get("policyVersion"),
        "optimizer stage matrix optimizerPolicyVersion does not match daily-review policyVersion",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("challengerSchemaVersion")
        == daily_generated.get("challengerSchemaVersion"),
        "optimizer stage matrix challengerSchemaVersion does not match daily-review challenger schemaVersion",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("challengerInputKind")
        == daily_generated.get("challengerInputKind"),
        "optimizer stage matrix challengerInputKind does not match daily-review challenger input kind",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerContractId")
        == daily_generated.get("rankingOptimizerContractId"),
        "optimizer stage matrix rankingOptimizerContractId does not match daily-review contract id",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerContractVersion")
        == daily_generated.get("rankingOptimizerContractVersion"),
        "optimizer stage matrix rankingOptimizerContractVersion does not match daily-review contract version",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerContractValidationMode")
        == daily_generated.get("rankingOptimizerContractValidationMode"),
        "optimizer stage matrix rankingOptimizerContractValidationMode does not match daily-review contract validation mode",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerContractValidated")
        == daily_generated.get("rankingOptimizerContractValidated"),
        "optimizer stage matrix rankingOptimizerContractValidated does not match daily-review contract validation state",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerSurfaceSource")
        == daily_generated.get("rankingOptimizerSurfaceSource"),
        "optimizer stage matrix rankingOptimizerSurfaceSource does not match daily-review surface source",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerDeprecationPhase")
        == daily_generated.get("rankingOptimizerDeprecationPhase"),
        "optimizer stage matrix rankingOptimizerDeprecationPhase does not match daily-review deprecation phase",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerCanonicalSurface")
        == daily_generated.get("rankingOptimizerCanonicalSurface"),
        "optimizer stage matrix rankingOptimizerCanonicalSurface does not match daily-review canonical surface",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerDeprecatedTopLevelFields")
        == daily_generated.get("rankingOptimizerDeprecatedTopLevelFields"),
        "optimizer stage matrix rankingOptimizerDeprecatedTopLevelFields do not match daily-review deprecated fields",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerNextHardFailContractVersion")
        == daily_generated.get("rankingOptimizerNextHardFailContractVersion"),
        "optimizer stage matrix rankingOptimizerNextHardFailContractVersion does not match daily-review next hard-fail version",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerCompatApplied")
        == daily_generated.get("rankingOptimizerCompatApplied"),
        "optimizer stage matrix rankingOptimizerCompatApplied does not match daily-review compat state",
        errors,
    )
    expect(
        optimizer_matrix_generated.get("rankingOptimizerCompatAliasesApplied")
        == daily_generated.get("rankingOptimizerCompatAliasesApplied"),
        "optimizer stage matrix rankingOptimizerCompatAliasesApplied does not match daily-review compat aliases",
        errors,
    )
    optimizer_matrix_stages = optimizer_matrix.get("stages")
    expect(
        isinstance(optimizer_matrix_stages, list) and bool(optimizer_matrix_stages),
        "optimizer stage matrix must include a non-empty stages list",
        errors,
    )
    if isinstance(optimizer_matrix_stages, list):
        for stage_entry in optimizer_matrix_stages:
            if not isinstance(stage_entry, dict):
                errors.append("optimizer stage matrix stages must be objects")
                continue
            stage_mode = stage_entry.get("stageMode")
            if not isinstance(stage_mode, str):
                errors.append("optimizer stage matrix stages must include stageMode")
                continue
            expect_stage_profile_consistency(
                stage_entry,
                f"optimizer stage matrix stage `{stage_mode}`",
                errors,
            )
            candidate_source = stage_entry.get("candidateSource", {})
            if not isinstance(candidate_source, dict):
                errors.append(
                    f"optimizer stage matrix stage `{stage_mode}` candidateSource must be an object"
                )
                continue
            expect_candidate_source_matches_discovery(
                candidate_source,
                discovery,
                f"optimizer stage matrix stage `{stage_mode}`",
                errors,
            )
            ranking_stage = ranking_matrix_stage_map.get(stage_mode)
            expect(
                ranking_stage is not None,
                f"optimizer stage matrix stage `{stage_mode}` is missing from ranking profile matrix",
                errors,
            )
            if ranking_stage is None:
                continue
            expect(
                stage_entry.get("profileSelection") == ranking_stage.get("profileSelection"),
                f"optimizer stage matrix stage `{stage_mode}` profileSelection does not match ranking profile matrix",
                errors,
            )
            expect(
                stage_entry.get("topTopicId") == ranking_stage.get("topTopicId"),
                f"optimizer stage matrix stage `{stage_mode}` topTopicId does not match ranking profile matrix",
                errors,
            )
            expect(
                stage_entry.get("rejectedTopicIds") == ranking_stage.get("rejectedTopicIds"),
                f"optimizer stage matrix stage `{stage_mode}` rejectedTopicIds do not match ranking profile matrix",
                errors,
            )
            expect(
                stage_entry.get("priorityCounts") == ranking_stage.get("priorityCounts"),
                f"optimizer stage matrix stage `{stage_mode}` priorityCounts do not match ranking profile matrix",
                errors,
            )

    workflow_generated = workflow.get("generatedFrom", {})
    workflow_summary = workflow.get("summary", {})
    expect(
        workflow_summary.get("candidateSourceKind") == "discovery_artifact",
        "workflow summary candidateSourceKind should be discovery_artifact",
        errors,
    )
    expect(
        workflow_summary.get("candidateSourceSnapshotId") == discovery_snapshot,
        "workflow summary candidateSourceSnapshotId does not match discovery snapshotId",
        errors,
    )
    expect(
        workflow_summary.get("candidateSourcePolicyVersion") == discovery_policy,
        "workflow summary candidateSourcePolicyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        workflow_generated.get("discoveryPolicyVersion") == discovery_policy,
        "workflow generatedFrom.discoveryPolicyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        workflow_generated.get("discoveryNormalizationRuleVersion")
        == discovery.get("generatedFrom", {}).get("normalizationRuleVersion"),
        "workflow discoveryNormalizationRuleVersion does not match discovery generatedFrom.normalizationRuleVersion",
        errors,
    )
    expect(
        workflow_generated.get("candidateInputSchemaVersion") == discovery_schema,
        "workflow generatedFrom.candidateInputSchemaVersion does not match discovery schemaVersion",
        errors,
    )
    expect(
        workflow_generated.get("candidateSourceInputKind")
        == discovery.get("generatedFrom", {}).get("inputKind"),
        "workflow candidateSourceInputKind does not match discovery generatedFrom.inputKind",
        errors,
    )
    expect(
        workflow_generated.get("candidateSourceMaterializationId")
        == discovery.get("generatedFrom", {}).get("materializationId"),
        "workflow candidateSourceMaterializationId does not match discovery generatedFrom.materializationId",
        errors,
    )
    expect(
        workflow_generated.get("candidateSourceNormalizationRuleVersion")
        == discovery.get("generatedFrom", {}).get("normalizationRuleVersion"),
        "workflow candidateSourceNormalizationRuleVersion does not match discovery generatedFrom.normalizationRuleVersion",
        errors,
    )
    expect(
        workflow_generated.get("rankingScoringCodeVersion") == ranking_run.get("scoringCodeVersion"),
        "workflow rankingScoringCodeVersion does not match ranking scoringCodeVersion",
        errors,
    )
    expect(
        workflow_generated.get("optimizerPolicyVersion") == daily.get("policyVersion"),
        "workflow optimizerPolicyVersion does not match daily-review policyVersion",
        errors,
    )
    expect(
        workflow_generated.get("challengerSchemaVersion")
        == daily_generated.get("challengerSchemaVersion"),
        "workflow challengerSchemaVersion does not match daily-review challenger schemaVersion",
        errors,
    )
    expect(
        workflow_generated.get("challengerInputKind")
        == daily_generated.get("challengerInputKind"),
        "workflow challengerInputKind does not match daily-review challenger input kind",
        errors,
    )
    expect(
        workflow_generated.get("optimizerInputBundleSchemaVersion")
        == daily_generated.get("optimizerInputBundleSchemaVersion"),
        "workflow optimizerInputBundleSchemaVersion does not match daily-review optimizer input bundle schemaVersion",
        errors,
    )
    expect(
        workflow_generated.get("optimizerInputBundleId")
        == daily_generated.get("optimizerInputBundleId"),
        "workflow optimizerInputBundleId does not match daily-review optimizer input bundle id",
        errors,
    )
    expect(
        workflow_generated.get("optimizerInputManifestSchemaVersion")
        == daily_generated.get("optimizerInputManifestSchemaVersion"),
        "workflow optimizerInputManifestSchemaVersion does not match daily-review optimizer input manifest schemaVersion",
        errors,
    )
    expect(
        workflow_generated.get("optimizerInputManifestId")
        == daily_generated.get("optimizerInputManifestId"),
        "workflow optimizerInputManifestId does not match daily-review optimizer input manifest id",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerContractId")
        == daily_generated.get("rankingOptimizerContractId"),
        "workflow rankingOptimizerContractId does not match daily-review contract id",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerContractVersion")
        == daily_generated.get("rankingOptimizerContractVersion"),
        "workflow rankingOptimizerContractVersion does not match daily-review contract version",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerContractValidationMode")
        == daily_generated.get("rankingOptimizerContractValidationMode"),
        "workflow rankingOptimizerContractValidationMode does not match daily-review contract validation mode",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerContractValidated")
        == daily_generated.get("rankingOptimizerContractValidated"),
        "workflow rankingOptimizerContractValidated does not match daily-review contract validation state",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerSurfaceSource")
        == daily_generated.get("rankingOptimizerSurfaceSource"),
        "workflow rankingOptimizerSurfaceSource does not match daily-review surface source",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerDeprecationPhase")
        == daily_generated.get("rankingOptimizerDeprecationPhase"),
        "workflow rankingOptimizerDeprecationPhase does not match daily-review deprecation phase",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerCanonicalSurface")
        == daily_generated.get("rankingOptimizerCanonicalSurface"),
        "workflow rankingOptimizerCanonicalSurface does not match daily-review canonical surface",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerDeprecatedTopLevelFields")
        == daily_generated.get("rankingOptimizerDeprecatedTopLevelFields"),
        "workflow rankingOptimizerDeprecatedTopLevelFields do not match daily-review deprecated fields",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerNextHardFailContractVersion")
        == daily_generated.get("rankingOptimizerNextHardFailContractVersion"),
        "workflow rankingOptimizerNextHardFailContractVersion does not match daily-review next hard-fail version",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerCompatApplied")
        == daily_generated.get("rankingOptimizerCompatApplied"),
        "workflow rankingOptimizerCompatApplied does not match daily-review compat state",
        errors,
    )
    expect(
        workflow_generated.get("rankingOptimizerCompatAliasesApplied")
        == daily_generated.get("rankingOptimizerCompatAliasesApplied"),
        "workflow rankingOptimizerCompatAliasesApplied does not match daily-review compat aliases",
        errors,
    )
    expect(
        workflow_generated.get("weeklyPolicyVersion") == weekly_generated.get("policyVersion"),
        "workflow weeklyPolicyVersion does not match weekly generated policyVersion",
        errors,
    )

    if errors:
        print("[ERROR] AutoTikTok artifact provenance chain is inconsistent:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AutoTikTok artifact provenance chain is consistent.")
    print(f"- discovery: {DISCOVERY_PATH}")
    print(f"- shared candidates: {SHARED_PATH}")
    print(f"- scoring context matrix: {CONTEXT_MATRIX_PATH}")
    print(f"- ranking: {RANKING_PATH}")
    print(f"- ranking profile matrix: {RANKING_MATRIX_PATH}")
    print(f"- daily review: {DAILY_PATH}")
    print(f"- weekly promotion: {WEEKLY_PATH}")
    print(f"- optimizer stage matrix: {OPTIMIZER_MATRIX_PATH}")
    print(f"- workflow summary: {WORKFLOW_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
