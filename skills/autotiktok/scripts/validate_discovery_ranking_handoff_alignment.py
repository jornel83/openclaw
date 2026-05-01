#!/usr/bin/env python3
"""
Validate that discovery-owned artifacts remain the direct default input surface for ranking.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_PATH = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "fixtures" / "discovery-dry-run.sample.json"
)
RANKING_PATH = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
RANKING_MATRIX_PATH = (
    ROOT
    / "skills"
    / "autotiktok-topic-ranking"
    / "fixtures"
    / "ranking-profile-matrix.sample.json"
)
WORKFLOW_PATH = ROOT / "skills" / "autotiktok" / "fixtures" / "workflow-summary.sample.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    try:
        discovery = load_json(DISCOVERY_PATH)
        ranking = load_json(RANKING_PATH)
        ranking_matrix = load_json(RANKING_MATRIX_PATH)
        workflow = load_json(WORKFLOW_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors: list[str] = []
    discovery_generated = discovery.get("generatedFrom", {})
    ranking_source = ranking.get("candidateSource", {})
    ranking_run = ranking.get("predictionRun", {})
    ranking_matrix_generated = ranking_matrix.get("generatedFrom", {})
    workflow_summary = workflow.get("summary", {})
    workflow_generated = workflow.get("generatedFrom", {})

    expect(
        ranking_source.get("sourceKind") == "discovery_artifact",
        "ranking candidateSource should default to discovery_artifact",
        errors,
    )
    expect(
        ranking_source.get("inputSchemaVersion") == discovery.get("schemaVersion"),
        "ranking candidateSource.inputSchemaVersion does not match discovery schemaVersion",
        errors,
    )
    expect(
        ranking_source.get("sourceSnapshotId") == discovery.get("snapshotId"),
        "ranking candidateSource.sourceSnapshotId does not match discovery snapshotId",
        errors,
    )
    expect(
        ranking_source.get("sourcePolicyVersion") == discovery.get("policyVersion"),
        "ranking candidateSource.sourcePolicyVersion does not match discovery policyVersion",
        errors,
    )
    expect(
        ranking_source.get("sourceInputKind") == discovery_generated.get("inputKind"),
        "ranking candidateSource.sourceInputKind does not match discovery inputKind",
        errors,
    )
    expect(
        ranking_source.get("sourceMaterializationId")
        == discovery_generated.get("materializationId"),
        "ranking candidateSource.sourceMaterializationId does not match discovery materializationId",
        errors,
    )
    expect(
        ranking_source.get("sourceNormalizationRuleVersion")
        == discovery_generated.get("normalizationRuleVersion"),
        "ranking candidateSource.sourceNormalizationRuleVersion does not match discovery normalizationRuleVersion",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceKind") == ranking_source.get("sourceKind"),
        "ranking predictionRun candidateSourceKind does not match candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceInputKind") == ranking_source.get("sourceInputKind"),
        "ranking predictionRun candidateSourceInputKind does not match candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceMaterializationId")
        == ranking_source.get("sourceMaterializationId"),
        "ranking predictionRun candidateSourceMaterializationId does not match candidateSource",
        errors,
    )
    expect(
        ranking_run.get("candidateSourceNormalizationRuleVersion")
        == ranking_source.get("sourceNormalizationRuleVersion"),
        "ranking predictionRun candidateSourceNormalizationRuleVersion does not match candidateSource",
        errors,
    )

    expect(
        ranking_matrix_generated.get("candidateSourceKind") == "discovery_artifact",
        "ranking profile matrix should default to discovery_artifact inputs",
        errors,
    )
    for index, stage_entry in enumerate(ranking_matrix.get("stages", [])):
        if not isinstance(stage_entry, dict):
            errors.append(f"ranking profile matrix stages[{index}] must be an object")
            continue
        candidate_source = stage_entry.get("candidateSource", {})
        if not isinstance(candidate_source, dict):
            errors.append(
                f"ranking profile matrix stages[{index}].candidateSource must be an object"
            )
            continue
        expect(
            candidate_source.get("sourceKind") == "discovery_artifact",
            f"ranking profile matrix stages[{index}] should use discovery_artifact",
            errors,
        )
        expect(
            candidate_source.get("sourceMaterializationId")
            == discovery_generated.get("materializationId"),
            f"ranking profile matrix stages[{index}] sourceMaterializationId does not match discovery",
            errors,
        )

    expect(
        workflow_summary.get("candidateSourceKind") == "discovery_artifact",
        "workflow summary should report discovery_artifact as the ranking candidate source",
        errors,
    )
    expect(
        workflow_generated.get("candidateSourceInputKind")
        == discovery_generated.get("inputKind"),
        "workflow generatedFrom.candidateSourceInputKind does not match discovery inputKind",
        errors,
    )
    expect(
        workflow_generated.get("candidateSourceMaterializationId")
        == discovery_generated.get("materializationId"),
        "workflow generatedFrom.candidateSourceMaterializationId does not match discovery materializationId",
        errors,
    )
    expect(
        workflow_generated.get("candidateSourceNormalizationRuleVersion")
        == discovery_generated.get("normalizationRuleVersion"),
        "workflow generatedFrom.candidateSourceNormalizationRuleVersion does not match discovery normalizationRuleVersion",
        errors,
    )

    if errors:
        print("[ERROR] discovery -> ranking handoff alignment failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Discovery -> ranking handoff is aligned with the committed direct-artifact contract.")
    print(f"Discovery artifact: {DISCOVERY_PATH}")
    print(f"Ranking artifact: {RANKING_PATH}")
    print(f"Ranking profile matrix: {RANKING_MATRIX_PATH}")
    print(f"Workflow summary: {WORKFLOW_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
