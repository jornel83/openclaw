#!/usr/bin/env python3
"""
Validate that planner metadata contracts reject disallowed window-set batch type and
comparison-dimension combinations before history-manifest materialization.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
WINDOW_SET_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_window_set.py"
)
FAMILY_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_family_registry.py"
)
ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_rollout_policy.py"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _expect_command_failure(
    result: subprocess.CompletedProcess[str],
    *,
    expected_text: str,
    label: str,
    errors: list[str],
) -> None:
    combined = f"{result.stdout}\n{result.stderr}"
    expect(result.returncode != 0, f"{label} should fail", errors)
    expect(
        expected_text in combined,
        f"{label} should mention {expected_text!r}, got:\n{combined}",
        errors,
    )


def validate_runtime_profile_planner_metadata_contract_enforcement(
    errors: list[str],
) -> None:
    with tempfile.TemporaryDirectory(
        prefix="autotiktok-runtime-profile-planner-metadata-contract-"
    ) as temp_dir:
        temp_root = Path(temp_dir)
        family_registry_path = temp_root / "runtime-profile-family-registry.json"
        rollout_policy_path = temp_root / "runtime-profile-rollout-policy.json"
        valid_window_set_path = temp_root / "window-set.profile-compare.valid.json"
        valid_standard_window_set_path = temp_root / "window-set.preview-validation.json"

        family_registry_result = run_script(
            FAMILY_REGISTRY_SCRIPT,
            "--output",
            str(family_registry_path),
        )
        if family_registry_result.returncode != 0:
            errors.append(
                "family registry build failed\n"
                f"STDOUT:\n{family_registry_result.stdout}\n"
                f"STDERR:\n{family_registry_result.stderr}"
            )
            return

        rollout_policy_result = run_script(
            ROLLOUT_POLICY_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--output",
            str(rollout_policy_path),
        )
        if rollout_policy_result.returncode != 0:
            errors.append(
                "rollout policy build failed\n"
                f"STDOUT:\n{rollout_policy_result.stdout}\n"
                f"STDERR:\n{rollout_policy_result.stderr}"
            )
            return

        valid_compare_result = run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--input-runtime-profile-rollout-policy",
            str(rollout_policy_path),
            "--window-set-purpose",
            "profile_compare_validation",
            "--output",
            str(valid_window_set_path),
        )
        if valid_compare_result.returncode != 0:
            errors.append(
                "valid profile-compare window set failed\n"
                f"STDOUT:\n{valid_compare_result.stdout}\n"
                f"STDERR:\n{valid_compare_result.stderr}"
            )
            return
        valid_compare_payload = load_json(valid_window_set_path)
        generated_from = valid_compare_payload.get("generatedFrom", {})
        expect(
            generated_from.get("runtimeProfilePlannerMetadataPolicyId")
            == "cross_profile_compare_metadata_policy",
            "profile_compare_validation should resolve cross-profile metadata policy",
            errors,
        )
        expect(
            generated_from.get("runtimeProfilePlannerMetadataContractFamilyId")
            == "cross_profile_compare_metadata_contract_family",
            "profile_compare_validation should resolve cross-profile metadata contract family",
            errors,
        )
        expect(
            generated_from.get("runtimeProfilePlannerMetadataContractId")
            == "cross_profile_compare_metadata_contract",
            "profile_compare_validation should resolve cross-profile metadata contract",
            errors,
        )
        expect(
            valid_compare_payload.get("windowSetBatchType")
            == "cross_profile_comparison",
            "profile_compare_validation should resolve cross_profile_comparison batch type",
            errors,
        )
        expect(
            valid_compare_payload.get("comparisonDimension") == "rankingProfileId",
            "profile_compare_validation should resolve rankingProfileId dimension",
            errors,
        )

        valid_standard_result = run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--input-runtime-profile-rollout-policy",
            str(rollout_policy_path),
            "--window-set-purpose",
            "preview_validation",
            "--output",
            str(valid_standard_window_set_path),
        )
        if valid_standard_result.returncode != 0:
            errors.append(
                "valid preview-validation window set failed\n"
                f"STDOUT:\n{valid_standard_result.stdout}\n"
                f"STDERR:\n{valid_standard_result.stderr}"
            )
            return
        valid_standard_payload = load_json(valid_standard_window_set_path)
        standard_generated_from = valid_standard_payload.get("generatedFrom", {})
        expect(
            standard_generated_from.get("runtimeProfilePlannerMetadataPolicyId")
            == "standard_replay_metadata_policy",
            "preview_validation should resolve standard replay metadata policy",
            errors,
        )
        expect(
            standard_generated_from.get("runtimeProfilePlannerMetadataContractFamilyId")
            == "standard_replay_metadata_contract_family",
            "preview_validation should resolve standard replay metadata contract family",
            errors,
        )
        expect(
            standard_generated_from.get("runtimeProfilePlannerMetadataContractId")
            == "standard_replay_metadata_contract",
            "preview_validation should resolve standard replay metadata contract",
            errors,
        )

        invalid_batch_type_result = run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--input-runtime-profile-rollout-policy",
            str(rollout_policy_path),
            "--window-set-purpose",
            "profile_compare_validation",
            "--window-set-batch-type",
            "standard_replay",
            "--output",
            str(temp_root / "window-set.invalid-batch-type.json"),
        )
        _expect_command_failure(
            invalid_batch_type_result,
            expected_text="does not allow windowSetBatchType",
            label="invalid batch-type override",
            errors=errors,
        )

        invalid_dimension_result = run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--input-runtime-profile-rollout-policy",
            str(rollout_policy_path),
            "--window-set-purpose",
            "profile_compare_validation",
            "--comparison-dimension",
            "historyBatchLabel",
            "--output",
            str(temp_root / "window-set.invalid-dimension.json"),
        )
        _expect_command_failure(
            invalid_dimension_result,
            expected_text="does not allow comparisonDimension",
            label="invalid comparison-dimension override",
            errors=errors,
        )


def main() -> int:
    errors: list[str] = []
    validate_runtime_profile_planner_metadata_contract_enforcement(errors)
    if errors:
        print("Runtime profile planner metadata contract enforcement validation failed.")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Runtime profile planner metadata contract enforcement validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
