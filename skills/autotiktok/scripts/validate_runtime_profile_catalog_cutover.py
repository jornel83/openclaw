#!/usr/bin/env python3
"""
Validate that the preview runtime profile catalog lane preserves optimizer semantics.
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
        "batchWindowLabel",
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


def _normalized_group_summaries(group_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "groupValue",
        "evalRunCount",
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
        "averageTopicReward",
        "averageCombinedReward",
        "averagePostCoverageRate",
        "bestEvalRunId",
        "bestCombinedReward",
    )
    normalized: list[dict[str, Any]] = []
    for group in group_summaries:
        normalized.append({key: group.get(key) for key in keys})
    return normalized


def validate_catalog_cutover(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="autotiktok-runtime-profile-cutover-") as temp_dir:
        temp_root = Path(temp_dir)
        current_catalog_path = temp_root / "runtime-profile-catalog.current.json"
        preview_catalog_path = temp_root / "runtime-profile-catalog.preview.json"
        family_registry_path = temp_root / "runtime-profile-family-registry.json"
        artifact_registry_path = temp_root / "runtime-artifact-registry.json"
        materialization_plan_path = temp_root / "runtime-materialization-plan.json"
        current_window_set_path = temp_root / "window-set.current.json"
        preview_window_set_path = temp_root / "window-set.preview.json"
        current_manifest_path = temp_root / "history-manifest.current.json"
        preview_manifest_path = temp_root / "history-manifest.preview.json"
        current_batch_path = temp_root / "eval-batch.current.json"
        preview_batch_path = temp_root / "eval-batch.preview.json"

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
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--runtime-profile-lane",
            "current",
            "--output",
            str(current_window_set_path),
        )
        run_script(
            WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(family_registry_path),
            "--runtime-profile-lane",
            "preview",
            "--output",
            str(preview_window_set_path),
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
            str(preview_window_set_path),
            "--input-artifact-registry",
            str(artifact_registry_path),
            "--input-runtime-profile-catalog",
            str(preview_catalog_path),
            "--input-materialization-plan",
            str(materialization_plan_path),
            "--output",
            str(preview_manifest_path),
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
            str(preview_manifest_path),
            "--output",
            str(preview_batch_path),
        )

        current_batch = load_json(current_batch_path)
        preview_batch = load_json(preview_batch_path)
        preview_manifest = load_json(preview_manifest_path)

    current_summary = current_batch.get("summary", {})
    preview_summary = preview_batch.get("summary", {})
    expect(
        _normalized_summary(current_summary) == _normalized_summary(preview_summary),
        "optimizer eval batch summary semantics drift between current and preview runtime profile catalogs",
        errors,
    )
    expect(
        _normalized_group_summaries(current_batch.get("groupSummaries", []))
        == _normalized_group_summaries(preview_batch.get("groupSummaries", [])),
        "optimizer eval batch group summary semantics drift between current and preview runtime profile catalogs",
        errors,
    )

    current_profile_ids = sorted(
        profile["profileId"]
        for profile in current_catalog["profiles"]
        if isinstance(profile, dict) and isinstance(profile.get("profileId"), str)
    )
    preview_profile_ids = sorted(
        profile["profileId"]
        for profile in preview_catalog["profiles"]
        if isinstance(profile, dict) and isinstance(profile.get("profileId"), str)
    )
    preview_alias_ids = _sorted_alias_ids(preview_catalog)

    expect(
        current_summary.get("runtimeProfileIds") == current_profile_ids,
        "current runtime profile catalog cutover lane should keep current canonical runtimeProfileIds",
        errors,
    )
    expect(
        current_summary.get("runtimeProfileRequestedIds") == current_profile_ids,
        "current runtime profile catalog cutover lane should keep requested ids aligned with canonical ids",
        errors,
    )
    expect(
        current_summary.get("runtimeProfileAliasAppliedCount") == 0,
        "current runtime profile catalog cutover lane should not apply alias resolution",
        errors,
    )
    expect(
        current_summary.get("runtimeProfileCatalogIds") == [current_catalog["catalogId"]],
        "current runtime profile catalog cutover lane should record the current catalog id",
        errors,
    )

    expect(
        preview_summary.get("runtimeProfileIds") == preview_profile_ids,
        "preview runtime profile catalog cutover lane should promote preview canonical runtimeProfileIds",
        errors,
    )
    expect(
        preview_summary.get("runtimeProfileRequestedIds") == preview_alias_ids,
        "preview runtime profile catalog cutover lane should keep legacy requested ids in runtimeProfileRequestedIds",
        errors,
    )
    expect(
        preview_summary.get("runtimeProfileAliasAppliedCount")
        == preview_summary.get("evalRunCount"),
        "preview runtime profile catalog cutover lane should resolve every runtime profile through an alias",
        errors,
    )
    expect(
        preview_summary.get("runtimeProfileCatalogIds") == [preview_catalog["catalogId"]],
        "preview runtime profile catalog cutover lane should record the preview catalog id",
        errors,
    )
    expect(
        preview_summary.get("runtimeProfileCatalogFamilies")
        == [preview_catalog["catalogFamily"]],
        "preview runtime profile catalog cutover lane should record the preview catalog family",
        errors,
    )
    expect(
        preview_summary.get("runtimeProfileCatalogVersions")
        == [preview_catalog["catalogVersion"]],
        "preview runtime profile catalog cutover lane should record the preview catalog version",
        errors,
    )

    preview_runtime_source = preview_manifest["evalRunEntries"][0]["runtimeSource"]
    expect(
        preview_runtime_source.get("runtimeProfileRequestedId") in preview_alias_ids,
        "preview history manifest should retain the legacy requested runtime profile id",
        errors,
    )
    expect(
        preview_runtime_source.get("runtimeProfileId") in preview_profile_ids,
        "preview history manifest should materialize the preview canonical runtime profile id",
        errors,
    )
    expect(
        preview_runtime_source.get("runtimeProfileAliasApplied") is True,
        "preview history manifest should mark alias-based runtime profile resolution",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    try:
        validate_catalog_cutover(errors)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Runtime profile catalog cutover rehearsal found semantic drift:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Runtime profile catalog cutover rehearsal preserves optimizer semantics.")
    print("- current catalog lane keeps current canonical runtimeProfileIds")
    print("- preview catalog lane resolves legacy requested ids through preview aliases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
