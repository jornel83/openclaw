#!/usr/bin/env python3
"""
Validate that rollout-policy rules can route a window set onto the preview class by purpose.
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
PROFILE_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_catalog.py"
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
ARTIFACT_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_artifact_registry.py"
)
MATERIALIZATION_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_materialization_plan.py"
)
HISTORY_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch_history_manifest.py"
)
EVAL_BATCH_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch.py"
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


def _sorted_alias_ids(catalog_payload: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    for profile in catalog_payload.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        alias_ids = profile.get("aliasProfileIds")
        if not isinstance(alias_ids, list):
            continue
        aliases.extend(
            alias_id for alias_id in alias_ids if isinstance(alias_id, str) and alias_id
        )
    return sorted(set(aliases))


def _normalized_summary(summary: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "evalRunCount",
        "comparisonDimension",
        "comparisonGroupCount",
        "modeCounts",
        "weeklyDecisionCounts",
        "rankingRunIds",
        "rankingProfileIds",
        "evaluationWindows",
        "runtimeSourceKinds",
        "runtimeSourceIds",
        "runtimeProfileRequestedIds",
        "materializationPlanIds",
        "jobFamilyGroups",
        "materializationProfiles",
        "materializationStrategies",
        "requiredArtifactKinds",
        "upstreamJobFamilies",
        "historyBatchLabels",
        "historyWindowLabels",
        "scenarioLabels",
        "challengerInputKinds",
        "rankingOptimizerContractVersions",
        "inputSourceKinds",
        "averageTopicReward",
        "averageCombinedReward",
        "averagePostCoverageRate",
        "bestEvalRunId",
        "bestProfileId",
        "bestCombinedReward",
    )
    return {key: summary.get(key) for key in keys}


def validate_rollout_policy_purpose_routing(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(
        prefix="autotiktok-runtime-profile-rollout-policy-purpose-"
    ) as temp_dir:
        temp_root = Path(temp_dir)
        current_catalog_path = temp_root / "runtime-profile-catalog.current.json"
        preview_catalog_path = temp_root / "runtime-profile-catalog.preview.json"
        family_registry_path = temp_root / "runtime-profile-family-registry.json"
        rollout_policy_path = temp_root / "runtime-profile-rollout-policy.current.json"
        artifact_registry_path = temp_root / "runtime-artifact-registry.json"
        materialization_plan_path = temp_root / "runtime-materialization-plan.json"
        current_window_set_path = temp_root / "window-set.current.json"
        purpose_window_set_path = temp_root / "window-set.preview-purpose.json"
        current_manifest_path = temp_root / "history-manifest.current.json"
        purpose_manifest_path = temp_root / "history-manifest.preview-purpose.json"
        current_batch_path = temp_root / "eval-batch.current.json"
        purpose_batch_path = temp_root / "eval-batch.preview-purpose.json"

        run_script(PROFILE_CATALOG_SCRIPT, "--output", str(current_catalog_path))
        run_script(
            PROFILE_CATALOG_SCRIPT,
            "--catalog-lane",
            "preview",
            "--output",
            str(preview_catalog_path),
        )
        current_catalog = load_json(current_catalog_path)
        preview_catalog = load_json(preview_catalog_path)
        run_script(FAMILY_REGISTRY_SCRIPT, "--output", str(family_registry_path))
        run_script(ARTIFACT_REGISTRY_SCRIPT, "--output", str(artifact_registry_path))
        run_script(MATERIALIZATION_PLAN_SCRIPT, "--output", str(materialization_plan_path))
        run_script(
            ROLLOUT_POLICY_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--output",
            str(rollout_policy_path),
        )

        run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--input-runtime-profile-rollout-policy",
            str(rollout_policy_path),
            "--output",
            str(current_window_set_path),
        )
        run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--input-runtime-profile-rollout-policy",
            str(rollout_policy_path),
            "--window-set-purpose",
            "preview_validation",
            "--output",
            str(purpose_window_set_path),
        )

        run_script(
            HISTORY_MANIFEST_SCRIPT,
            "--input-window-set",
            str(current_window_set_path),
            "--input-artifact-registry",
            str(artifact_registry_path),
            "--input-runtime-profile-catalog",
            str(current_catalog_path),
            "--input-materialization-plan",
            str(materialization_plan_path),
            "--output",
            str(current_manifest_path),
        )
        run_script(
            HISTORY_MANIFEST_SCRIPT,
            "--input-window-set",
            str(purpose_window_set_path),
            "--input-artifact-registry",
            str(artifact_registry_path),
            "--input-runtime-profile-catalog",
            str(preview_catalog_path),
            "--input-materialization-plan",
            str(materialization_plan_path),
            "--output",
            str(purpose_manifest_path),
        )

        run_script(
            EVAL_BATCH_SCRIPT,
            "--input-eval-batch-manifest",
            str(current_manifest_path),
            "--output",
            str(current_batch_path),
        )
        run_script(
            EVAL_BATCH_SCRIPT,
            "--input-eval-batch-manifest",
            str(purpose_manifest_path),
            "--output",
            str(purpose_batch_path),
        )

        current_window_set = load_json(current_window_set_path)
        purpose_window_set = load_json(purpose_window_set_path)
        current_manifest = load_json(current_manifest_path)
        purpose_manifest = load_json(purpose_manifest_path)
        current_batch = load_json(current_batch_path)
        purpose_batch = load_json(purpose_batch_path)

    current_summary = current_batch.get("summary", {})
    purpose_summary = purpose_batch.get("summary", {})
    expect(
        _normalized_summary(current_summary) == _normalized_summary(purpose_summary),
        "optimizer eval batch summary semantics drift between policy-default and purpose-routed routing",
        errors,
    )

    preview_profile_ids = sorted(
        profile["profileId"]
        for profile in preview_catalog["profiles"]
        if isinstance(profile, dict) and isinstance(profile.get("profileId"), str)
    )
    preview_alias_ids = _sorted_alias_ids(preview_catalog)

    expect(
        current_window_set.get("windowSetPurpose") == "production_replay",
        "default rollout policy path should keep the production_replay purpose",
        errors,
    )
    expect(
        current_window_set["generatedFrom"].get("runtimeProfileLaneSelectionSource")
        == "policy_default",
        "default rollout policy path should use policy_default",
        errors,
    )
    expect(
        purpose_window_set.get("windowSetPurpose") == "preview_validation",
        "purpose-routed rollout path should declare preview_validation purpose",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfileLaneSelectionSource")
        == "policy_purpose",
        "purpose-routed rollout path should use policy_purpose",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfileRolloutClass")
        == "preview_canary",
        "purpose-routed rollout path should switch to preview_canary",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfilePurposePolicyId")
        == "preview_validation_default",
        "purpose-routed rollout path should report the preview_validation_default purpose policy id",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfilePurposeTemplateId")
        == "preview_validation_template",
        "purpose-routed rollout path should report the preview_validation_template purpose template id",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfilePurposeTemplateFamilyId")
        == "preview_validation_family",
        "purpose-routed rollout path should report the preview_validation_family purpose template family id",
        errors,
    )
    expect(
        purpose_window_set.get("windowSetBatchType") == "standard_replay",
        "purpose-routed rollout path should keep the default standard_replay batch type",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("windowSetBatchTypeSelectionSource")
        == "metadata_policy_default",
        "purpose-routed rollout path should report metadata_policy_default for windowSetBatchTypeSelectionSource",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("comparisonDimensionSelectionSource")
        == "metadata_policy_default",
        "purpose-routed rollout path should report metadata_policy_default for comparisonDimensionSelectionSource",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfilePlannerMetadataPolicyId")
        == "standard_replay_metadata_policy",
        "purpose-routed rollout path should report the standard_replay_metadata_policy id",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get(
            "runtimeProfilePlannerMetadataContractFamilyId"
        )
        == "standard_replay_metadata_contract_family",
        "purpose-routed rollout path should report the standard_replay_metadata_contract_family id",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfilePlannerMetadataContractId")
        == "standard_replay_metadata_contract",
        "purpose-routed rollout path should report the standard_replay_metadata_contract id",
        errors,
    )
    expect(
        purpose_window_set["generatedFrom"].get("runtimeProfileCatalogLane")
        == "preview",
        "purpose-routed rollout path should resolve the preview catalog lane",
        errors,
    )

    expect(
        purpose_manifest.get("windowSetPurpose") == "preview_validation",
        "purpose-routed history manifest should retain windowSetPurpose",
        errors,
    )
    expect(
        purpose_manifest.get("runtimeProfilePurposePolicyId")
        == "preview_validation_default",
        "purpose-routed history manifest should retain runtimeProfilePurposePolicyId",
        errors,
    )
    expect(
        purpose_manifest.get("runtimeProfilePurposeTemplateId")
        == "preview_validation_template",
        "purpose-routed history manifest should retain runtimeProfilePurposeTemplateId",
        errors,
    )
    expect(
        purpose_manifest.get("runtimeProfilePurposeTemplateFamilyId")
        == "preview_validation_family",
        "purpose-routed history manifest should retain runtimeProfilePurposeTemplateFamilyId",
        errors,
    )
    expect(
        purpose_manifest.get("runtimeProfilePlannerMetadataPolicyId")
        == "standard_replay_metadata_policy",
        "purpose-routed history manifest should retain runtimeProfilePlannerMetadataPolicyId",
        errors,
    )
    expect(
        purpose_manifest.get("runtimeProfilePlannerMetadataContractFamilyId")
        == "standard_replay_metadata_contract_family",
        "purpose-routed history manifest should retain runtimeProfilePlannerMetadataContractFamilyId",
        errors,
    )
    expect(
        purpose_manifest.get("runtimeProfilePlannerMetadataContractId")
        == "standard_replay_metadata_contract",
        "purpose-routed history manifest should retain runtimeProfilePlannerMetadataContractId",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {}).get("windowSetPurpose")
        == "preview_validation",
        "purpose-routed eval batch should retain windowSetPurpose in generatedFrom",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("windowSetPurpose")
        == "preview_validation",
        "purpose-routed eval batch sourceDescriptor should retain windowSetPurpose",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePurposePolicyId")
        == "preview_validation_default",
        "purpose-routed eval batch sourceDescriptor should retain runtimeProfilePurposePolicyId",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePurposeTemplateId")
        == "preview_validation_template",
        "purpose-routed eval batch sourceDescriptor should retain runtimeProfilePurposeTemplateId",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePurposeTemplateFamilyId")
        == "preview_validation_family",
        "purpose-routed eval batch sourceDescriptor should retain runtimeProfilePurposeTemplateFamilyId",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("windowSetBatchTypeSelectionSource")
        == "metadata_policy_default",
        "purpose-routed eval batch sourceDescriptor should retain windowSetBatchTypeSelectionSource",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("comparisonDimensionSelectionSource")
        == "metadata_policy_default",
        "purpose-routed eval batch sourceDescriptor should retain comparisonDimensionSelectionSource",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePlannerMetadataPolicyId")
        == "standard_replay_metadata_policy",
        "purpose-routed eval batch sourceDescriptor should retain runtimeProfilePlannerMetadataPolicyId",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePlannerMetadataContractFamilyId")
        == "standard_replay_metadata_contract_family",
        "purpose-routed eval batch sourceDescriptor should retain runtimeProfilePlannerMetadataContractFamilyId",
        errors,
    )
    expect(
        purpose_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePlannerMetadataContractId")
        == "standard_replay_metadata_contract",
        "purpose-routed eval batch sourceDescriptor should retain runtimeProfilePlannerMetadataContractId",
        errors,
    )

    expect(
        purpose_summary.get("runtimeProfileIds") == preview_profile_ids,
        "purpose-routed rollout path should use preview canonical runtimeProfileIds",
        errors,
    )
    expect(
        purpose_summary.get("runtimeProfileRequestedIds") == preview_alias_ids,
        "purpose-routed rollout path should preserve legacy planner ids as requested ids",
        errors,
    )
    expect(
        purpose_summary.get("runtimeProfileAliasAppliedCount")
        == len(purpose_summary.get("runtimeProfileIds", [])),
        "purpose-routed rollout path should apply alias resolution for every runtime profile",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    try:
        validate_rollout_policy_purpose_routing(errors)
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] unexpected failure: {exc}")
        return 1
    if errors:
        print("[ERROR] runtime profile rollout policy purpose routing validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Runtime profile rollout policy purpose routing validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
