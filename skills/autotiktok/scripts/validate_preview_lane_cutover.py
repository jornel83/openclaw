#!/usr/bin/env python3
"""
Validate that the preview optimizer handoff lane preserves current workflow semantics.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ranking_optimizer_contract_lib import (
    OPTIMIZER_HANDOFF_CANONICAL_SURFACE,
    OPTIMIZER_HANDOFF_DEPRECATION_PHASE,
    OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS,
    OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION,
    RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
    RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
    RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
)


ROOT = Path(__file__).resolve().parents[3]
MATRIX_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_optimizer_stage_matrix.py"
WORKFLOW_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_autotiktok_workflow.py"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_lane_metadata(
    generated_from: dict[str, Any],
    *,
    label: str,
    expected_contract_version: str,
    expected_surface_source: str,
    errors: list[str],
) -> None:
    expect(
        generated_from.get("rankingOptimizerContractVersion") == expected_contract_version,
        f"{label} rankingOptimizerContractVersion does not match expected lane",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerContractValidationMode")
        == RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        f"{label} rankingOptimizerContractValidationMode should stay exact in lane cutover rehearsal",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerSurfaceSource") == expected_surface_source,
        f"{label} rankingOptimizerSurfaceSource does not match expected lane surface",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerDeprecationPhase")
        == OPTIMIZER_HANDOFF_DEPRECATION_PHASE,
        f"{label} rankingOptimizerDeprecationPhase does not match the preview deprecation phase",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerCanonicalSurface")
        == OPTIMIZER_HANDOFF_CANONICAL_SURFACE,
        f"{label} rankingOptimizerCanonicalSurface does not match optimizerHandoff",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerDeprecatedTopLevelFields")
        == list(OPTIMIZER_HANDOFF_DEPRECATED_TOP_LEVEL_FIELDS),
        f"{label} rankingOptimizerDeprecatedTopLevelFields do not match the canonical deprecated field set",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerNextHardFailContractVersion")
        == OPTIMIZER_HANDOFF_NEXT_HARD_FAIL_CONTRACT_VERSION,
        f"{label} rankingOptimizerNextHardFailContractVersion does not match the next hard-fail target",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerCompatApplied") is False,
        f"{label} rankingOptimizerCompatApplied should stay false for exact lane comparison",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerCompatAliasesApplied") == [],
        f"{label} rankingOptimizerCompatAliasesApplied should stay empty for exact lane comparison",
        errors,
    )


def validate_stage_matrix_lane_cutover(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="autotiktok-lane-cutover-matrix-") as temp_dir:
        temp_root = Path(temp_dir)
        current_path = temp_root / "optimizer-stage-matrix.current.json"
        preview_path = temp_root / "optimizer-stage-matrix.preview.json"

        run_script(MATRIX_SCRIPT, "--output", str(current_path))
        run_script(
            MATRIX_SCRIPT,
            "--ranking-contract-version",
            RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
            "--ranking-contract-validation-mode",
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            "--output",
            str(preview_path),
        )

        current_payload = load_json(current_path)
        preview_payload = load_json(preview_path)

    expect(
        current_payload.get("stages") == preview_payload.get("stages"),
        "optimizer stage matrix stage semantics drift between current and preview exact lanes",
        errors,
    )

    current_generated = current_payload.get("generatedFrom", {})
    preview_generated = preview_payload.get("generatedFrom", {})
    shared_keys = (
        "contextMatrixFixtureVersion",
        "candidateInputSchemaVersion",
        "candidateSourceKind",
        "discoveryPolicyVersion",
        "rankingScoringCodeVersion",
        "optimizerPolicyVersion",
        "challengerSchemaVersion",
        "challengerInputKind",
        "rankingOptimizerDeprecationPhase",
        "rankingOptimizerCanonicalSurface",
        "rankingOptimizerDeprecatedTopLevelFields",
        "rankingOptimizerNextHardFailContractVersion",
    )
    for key in shared_keys:
        expect(
            current_generated.get(key) == preview_generated.get(key),
            f"optimizer stage matrix generatedFrom.{key} drifts between current and preview exact lanes",
            errors,
        )

    validate_lane_metadata(
        current_generated,
        label="optimizer stage matrix current lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        errors=errors,
    )
    validate_lane_metadata(
        preview_generated,
        label="optimizer stage matrix preview lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
        errors=errors,
    )


def validate_workflow_lane_cutover(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="autotiktok-lane-cutover-workflow-") as temp_dir:
        temp_root = Path(temp_dir)
        current_artifacts = temp_root / "current-artifacts"
        preview_artifacts = temp_root / "preview-artifacts"
        current_path = temp_root / "workflow.current.json"
        preview_path = temp_root / "workflow.preview.json"

        run_script(
            WORKFLOW_SCRIPT,
            "--artifacts-dir",
            str(current_artifacts),
            "--summary-output",
            str(current_path),
            "--artifact-path-style",
            "basename",
        )
        run_script(
            WORKFLOW_SCRIPT,
            "--artifacts-dir",
            str(preview_artifacts),
            "--summary-output",
            str(preview_path),
            "--artifact-path-style",
            "basename",
            "--ranking-contract-version",
            RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
            "--ranking-contract-validation-mode",
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        )

        current_payload = load_json(current_path)
        preview_payload = load_json(preview_path)

    expect(
        current_payload.get("summary") == preview_payload.get("summary"),
        "workflow summary semantics drift between current and preview exact lanes",
        errors,
    )
    expect(
        current_payload.get("artifactPaths") == preview_payload.get("artifactPaths"),
        "workflow artifact path labels drift between current and preview exact lanes",
        errors,
    )

    current_generated = current_payload.get("generatedFrom", {})
    preview_generated = preview_payload.get("generatedFrom", {})
    shared_keys = (
        "discoveryPolicyVersion",
        "candidateInputSchemaVersion",
        "rankingScoringCodeVersion",
        "optimizerPolicyVersion",
        "weeklyPolicyVersion",
        "challengerSchemaVersion",
        "challengerInputKind",
        "optimizerInputBundleSchemaVersion",
        "optimizerInputBundleId",
        "optimizerInputManifestSchemaVersion",
        "optimizerInputManifestId",
        "rankingOptimizerDeprecationPhase",
        "rankingOptimizerCanonicalSurface",
        "rankingOptimizerDeprecatedTopLevelFields",
        "rankingOptimizerNextHardFailContractVersion",
    )
    for key in shared_keys:
        expect(
            current_generated.get(key) == preview_generated.get(key),
            f"workflow generatedFrom.{key} drifts between current and preview exact lanes",
            errors,
        )

    validate_lane_metadata(
        current_generated,
        label="workflow current lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        errors=errors,
    )
    validate_lane_metadata(
        preview_generated,
        label="workflow preview lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
        errors=errors,
    )


def main() -> int:
    errors: list[str] = []
    try:
        validate_stage_matrix_lane_cutover(errors)
        validate_workflow_lane_cutover(errors)
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Preview lane cutover rehearsal found semantic drift:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Preview lane cutover rehearsal preserves current optimizer semantics.")
    print("- stage matrix: current lane vs vNext-preview/exact")
    print("- workflow summary: current lane vs vNext-preview/exact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
