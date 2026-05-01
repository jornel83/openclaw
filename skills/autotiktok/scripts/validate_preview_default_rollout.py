#!/usr/bin/env python3
"""
Validate the preview-first wrapper commands and their live-lane fallbacks.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
    RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
    RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
)


ROOT = Path(__file__).resolve().parents[3]
PREVIEW_MATRIX_WRAPPER = (
    ROOT / "skills" / "autotiktok" / "scripts" / "run_preview_optimizer_stage_matrix.py"
)
PREVIEW_WORKFLOW_WRAPPER = (
    ROOT / "skills" / "autotiktok" / "scripts" / "run_preview_autotiktok_workflow.py"
)
PREVIEW_DAILY_REVIEW_WRAPPER = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_preview_daily_review.py"
)


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
    payload: dict[str, Any],
    *,
    label: str,
    expected_contract_version: str,
    expected_surface_source: str,
    errors: list[str],
) -> None:
    generated_from = payload.get("generatedFrom", {})
    expect(
        generated_from.get("rankingOptimizerContractVersion") == expected_contract_version,
        f"{label} rankingOptimizerContractVersion does not match expected wrapper lane",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerContractValidationMode")
        == RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        f"{label} rankingOptimizerContractValidationMode should stay exact",
        errors,
    )
    expect(
        generated_from.get("rankingOptimizerSurfaceSource") == expected_surface_source,
        f"{label} rankingOptimizerSurfaceSource does not match expected wrapper lane",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-preview-default-rollout-") as temp_dir:
            temp_root = Path(temp_dir)
            preview_matrix_path = temp_root / "matrix.preview.json"
            current_matrix_path = temp_root / "matrix.current.json"
            preview_workflow_path = temp_root / "workflow.preview.json"
            current_workflow_path = temp_root / "workflow.current.json"
            preview_daily_path = temp_root / "daily.preview.json"
            current_daily_path = temp_root / "daily.current.json"

            run_script(PREVIEW_MATRIX_WRAPPER, "--output", str(preview_matrix_path))
            run_script(
                PREVIEW_MATRIX_WRAPPER,
                "--use-current-lane",
                "--output",
                str(current_matrix_path),
            )
            run_script(
                PREVIEW_WORKFLOW_WRAPPER,
                "--summary-output",
                str(preview_workflow_path),
                "--artifact-path-style",
                "basename",
            )
            run_script(
                PREVIEW_WORKFLOW_WRAPPER,
                "--use-current-lane",
                "--summary-output",
                str(current_workflow_path),
                "--artifact-path-style",
                "basename",
            )
            run_script(
                PREVIEW_DAILY_REVIEW_WRAPPER,
                "--output",
                str(preview_daily_path),
            )
            run_script(
                PREVIEW_DAILY_REVIEW_WRAPPER,
                "--use-current-lane",
                "--output",
                str(current_daily_path),
            )

            preview_matrix = load_json(preview_matrix_path)
            current_matrix = load_json(current_matrix_path)
            preview_workflow = load_json(preview_workflow_path)
            current_workflow = load_json(current_workflow_path)
            preview_daily = load_json(preview_daily_path)
            current_daily = load_json(current_daily_path)

    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    validate_lane_metadata(
        preview_matrix,
        label="preview matrix wrapper default lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
        errors=errors,
    )
    validate_lane_metadata(
        current_matrix,
        label="preview matrix wrapper current fallback lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        errors=errors,
    )
    validate_lane_metadata(
        preview_workflow,
        label="preview workflow wrapper default lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
        errors=errors,
    )
    validate_lane_metadata(
        current_workflow,
        label="preview workflow wrapper current fallback lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        errors=errors,
    )
    validate_lane_metadata(
        preview_daily,
        label="preview daily-review wrapper default lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_OPTIMIZER_HANDOFF,
        errors=errors,
    )
    validate_lane_metadata(
        current_daily,
        label="preview daily-review wrapper current fallback lane",
        expected_contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
        expected_surface_source=RANKING_OPTIMIZER_SURFACE_SOURCE_LEGACY_TOP_LEVEL,
        errors=errors,
    )

    if errors:
        print("[ERROR] Preview-default rollout validator found lane mismatches:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Preview-default wrappers now default to the preview canonical lane.")
    print("- run_preview_optimizer_stage_matrix.py defaults to vNext-preview/exact")
    print("- run_preview_autotiktok_workflow.py defaults to vNext-preview/exact")
    print("- run_preview_daily_review.py defaults to vNext-preview/exact")
    print("- --use-current-lane fallback still preserves the live lane")
    return 0


if __name__ == "__main__":
    sys.exit(main())
