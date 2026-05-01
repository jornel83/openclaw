#!/usr/bin/env python3
"""
Validate that rollout-policy rules can route a window set onto the preview class by
purpose, batch type, and comparison dimension together.
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


def validate_rollout_policy_dimension_routing(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(
        prefix="autotiktok-runtime-profile-rollout-policy-dimension-"
    ) as temp_dir:
        temp_root = Path(temp_dir)
        current_catalog_path = temp_root / "runtime-profile-catalog.current.json"
        preview_catalog_path = temp_root / "runtime-profile-catalog.preview.json"
        family_registry_path = temp_root / "runtime-profile-family-registry.json"
        rollout_policy_path = temp_root / "runtime-profile-rollout-policy.current.json"
        artifact_registry_path = temp_root / "runtime-artifact-registry.json"
        materialization_plan_path = temp_root / "runtime-materialization-plan.json"
        current_window_set_path = temp_root / "window-set.current.json"
        rule_window_set_path = temp_root / "window-set.profile-compare.json"
        current_manifest_path = temp_root / "history-manifest.current.json"
        rule_manifest_path = temp_root / "history-manifest.profile-compare.json"
        current_batch_path = temp_root / "eval-batch.current.json"
        rule_batch_path = temp_root / "eval-batch.profile-compare.json"

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
            "profile_compare_validation",
            "--output",
            str(rule_window_set_path),
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
            str(rule_window_set_path),
            "--input-artifact-registry",
            str(artifact_registry_path),
            "--input-runtime-profile-catalog",
            str(preview_catalog_path),
            "--input-materialization-plan",
            str(materialization_plan_path),
            "--output",
            str(rule_manifest_path),
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
            str(rule_manifest_path),
            "--output",
            str(rule_batch_path),
        )

        current_window_set = load_json(current_window_set_path)
        rule_window_set = load_json(rule_window_set_path)
        rule_manifest = load_json(rule_manifest_path)
        current_batch = load_json(current_batch_path)
        rule_batch = load_json(rule_batch_path)

    current_summary = current_batch.get("summary", {})
    rule_summary = rule_batch.get("summary", {})
    expect(
        _normalized_summary(current_summary) != _normalized_summary(rule_summary),
        "dimension-routed rollout path should change eval-batch grouping semantics when comparisonDimension changes",
        errors,
    )

    preview_profile_ids = sorted(
        profile["profileId"]
        for profile in preview_catalog["profiles"]
        if isinstance(profile, dict) and isinstance(profile.get("profileId"), str)
    )
    preview_alias_ids = _sorted_alias_ids(preview_catalog)

    expect(
        current_window_set["generatedFrom"].get("runtimeProfileLaneSelectionSource")
        == "policy_default",
        "default rollout policy path should use policy_default",
        errors,
    )
    expect(
        rule_window_set.get("windowSetPurpose") == "profile_compare_validation",
        "dimension-routed rollout path should declare profile_compare_validation purpose",
        errors,
    )
    expect(
        rule_window_set.get("windowSetBatchType") == "cross_profile_comparison",
        "dimension-routed rollout path should declare cross_profile_comparison batch type",
        errors,
    )
    expect(
        rule_window_set.get("comparisonDimension") == "rankingProfileId",
        "dimension-routed rollout path should switch comparisonDimension to rankingProfileId",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("windowSetBatchTypeSelectionSource")
        == "metadata_policy_default",
        "dimension-routed rollout path should report metadata_policy_default for windowSetBatchTypeSelectionSource",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("comparisonDimensionSelectionSource")
        == "metadata_policy_default",
        "dimension-routed rollout path should report metadata_policy_default for comparisonDimensionSelectionSource",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfilePlannerMetadataPolicyId")
        == "cross_profile_compare_metadata_policy",
        "dimension-routed rollout path should report the cross_profile_compare_metadata_policy id",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get(
            "runtimeProfilePlannerMetadataContractFamilyId"
        )
        == "cross_profile_compare_metadata_contract_family",
        "dimension-routed rollout path should report the cross_profile_compare_metadata_contract_family id",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfilePlannerMetadataContractId")
        == "cross_profile_compare_metadata_contract",
        "dimension-routed rollout path should report the cross_profile_compare_metadata_contract id",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfileLaneSelectionSource")
        == "policy_purpose",
        "dimension-routed rollout path should use policy_purpose",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfilePurposePolicyId")
        == "profile_compare_validation_default",
        "dimension-routed rollout path should report the profile_compare_validation_default purpose policy id",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfilePurposeTemplateId")
        == "profile_compare_validation_template",
        "dimension-routed rollout path should report the profile_compare_validation_template purpose template id",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfilePurposeTemplateFamilyId")
        == "cross_profile_validation_family",
        "dimension-routed rollout path should report the cross_profile_validation_family purpose template family id",
        errors,
    )
    expect(
        rule_window_set["generatedFrom"].get("runtimeProfileCatalogLane") == "preview",
        "dimension-routed rollout path should resolve the preview catalog lane",
        errors,
    )
    expect(
        rule_manifest.get("windowSetPurpose") == "profile_compare_validation",
        "dimension-routed history manifest should retain windowSetPurpose",
        errors,
    )
    expect(
        rule_manifest.get("windowSetBatchType") == "cross_profile_comparison",
        "dimension-routed history manifest should retain windowSetBatchType",
        errors,
    )
    expect(
        rule_manifest.get("runtimeProfilePurposePolicyId")
        == "profile_compare_validation_default",
        "dimension-routed history manifest should retain runtimeProfilePurposePolicyId",
        errors,
    )
    expect(
        rule_manifest.get("runtimeProfilePurposeTemplateId")
        == "profile_compare_validation_template",
        "dimension-routed history manifest should retain runtimeProfilePurposeTemplateId",
        errors,
    )
    expect(
        rule_manifest.get("runtimeProfilePurposeTemplateFamilyId")
        == "cross_profile_validation_family",
        "dimension-routed history manifest should retain runtimeProfilePurposeTemplateFamilyId",
        errors,
    )
    expect(
        rule_manifest.get("runtimeProfilePlannerMetadataPolicyId")
        == "cross_profile_compare_metadata_policy",
        "dimension-routed history manifest should retain runtimeProfilePlannerMetadataPolicyId",
        errors,
    )
    expect(
        rule_manifest.get("runtimeProfilePlannerMetadataContractFamilyId")
        == "cross_profile_compare_metadata_contract_family",
        "dimension-routed history manifest should retain runtimeProfilePlannerMetadataContractFamilyId",
        errors,
    )
    expect(
        rule_manifest.get("runtimeProfilePlannerMetadataContractId")
        == "cross_profile_compare_metadata_contract",
        "dimension-routed history manifest should retain runtimeProfilePlannerMetadataContractId",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {}).get("windowSetPurpose")
        == "profile_compare_validation",
        "dimension-routed eval batch should retain windowSetPurpose in generatedFrom",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {}).get("windowSetBatchType")
        == "cross_profile_comparison",
        "dimension-routed eval batch should retain windowSetBatchType in generatedFrom",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("windowSetBatchType")
        == "cross_profile_comparison",
        "dimension-routed eval batch sourceDescriptor should retain windowSetBatchType",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePurposePolicyId")
        == "profile_compare_validation_default",
        "dimension-routed eval batch sourceDescriptor should retain runtimeProfilePurposePolicyId",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePurposeTemplateId")
        == "profile_compare_validation_template",
        "dimension-routed eval batch sourceDescriptor should retain runtimeProfilePurposeTemplateId",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePurposeTemplateFamilyId")
        == "cross_profile_validation_family",
        "dimension-routed eval batch sourceDescriptor should retain runtimeProfilePurposeTemplateFamilyId",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("windowSetBatchTypeSelectionSource")
        == "metadata_policy_default",
        "dimension-routed eval batch sourceDescriptor should retain windowSetBatchTypeSelectionSource",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("comparisonDimensionSelectionSource")
        == "metadata_policy_default",
        "dimension-routed eval batch sourceDescriptor should retain comparisonDimensionSelectionSource",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePlannerMetadataPolicyId")
        == "cross_profile_compare_metadata_policy",
        "dimension-routed eval batch sourceDescriptor should retain runtimeProfilePlannerMetadataPolicyId",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePlannerMetadataContractFamilyId")
        == "cross_profile_compare_metadata_contract_family",
        "dimension-routed eval batch sourceDescriptor should retain runtimeProfilePlannerMetadataContractFamilyId",
        errors,
    )
    expect(
        rule_batch.get("generatedFrom", {})
        .get("sourceDescriptor", {})
        .get("runtimeProfilePlannerMetadataContractId")
        == "cross_profile_compare_metadata_contract",
        "dimension-routed eval batch sourceDescriptor should retain runtimeProfilePlannerMetadataContractId",
        errors,
    )

    expect(
        rule_summary.get("runtimeProfileIds") == preview_profile_ids,
        "dimension-routed rollout path should use preview canonical runtimeProfileIds",
        errors,
    )
    expect(
        rule_summary.get("runtimeProfileRequestedIds") == preview_alias_ids,
        "dimension-routed rollout path should preserve legacy planner ids as requested ids",
        errors,
    )
    expect(
        rule_summary.get("runtimeProfileAliasAppliedCount")
        == len(rule_summary.get("runtimeProfileIds", [])),
        "dimension-routed rollout path should apply alias resolution for every runtime profile",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    try:
        validate_rollout_policy_dimension_routing(errors)
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] unexpected failure: {exc}")
        return 1
    if errors:
        print("[ERROR] runtime profile rollout policy dimension routing validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Runtime profile rollout policy dimension routing validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
