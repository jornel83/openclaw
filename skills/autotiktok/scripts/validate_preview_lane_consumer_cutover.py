#!/usr/bin/env python3
"""
Validate that preview-lane orchestrators read the canonical optimizer handoff surface.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from run_autotiktok_workflow import build_summary
from run_optimizer_stage_matrix import build_stage_entry


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_FIXTURE = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "fixtures" / "discovery-dry-run.sample.json"
)
RANKING_FIXTURE = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
CURRENT_DAILY_FIXTURE = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "daily-review.sample.json"
)
CURRENT_WEEKLY_FIXTURE = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "weekly-promotion.sample.json"
)
DAILY_REVIEW_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "daily_review_mock.py"
)
WEEKLY_PROMOTION_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "weekly_promotion_mock.py"
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


def build_corrupted_ranking_payload() -> dict[str, Any]:
    payload = load_json(RANKING_FIXTURE)
    payload["profileId"] = "corrupted-profile"
    payload["profileSelection"] = {
        **payload["profileSelection"],
        "resolvedProfileId": "corrupted-profile",
        "selectionSource": "corrupted_selection_source",
    }
    payload["candidateSource"] = {
        **payload["candidateSource"],
        "sourceKind": "corrupted_source_kind",
        "sourceSnapshotId": "snap.corrupted.fixture",
        "sourcePolicyVersion": "corrupted-policy.v1",
    }
    payload["predictionRun"] = {
        **payload["predictionRun"],
        "profileId": "corrupted-profile",
        "profileSelectionSource": "corrupted_selection_source",
        "candidateSourceKind": "corrupted_source_kind",
        "candidateSourceSnapshotId": "snap.corrupted.fixture",
        "candidateSourcePolicyVersion": "corrupted-policy.v1",
        "snapshotId": "snap.autotiktok.corrupted.fixture",
    }
    payload["rankingSummary"] = {
        **payload["rankingSummary"],
        "topTopicId": "tp_corrupted_top_001",
        "topTopicTitle": "Corrupted top title",
        "rejectedTopicIds": [],
        "priorityCounts": {"P0": 9, "P1": 0, "P2": 0},
    }
    return payload


def validate_stage_entry_cutover(
    corrupted_ranking: dict[str, Any],
    preview_daily: dict[str, Any],
    current_daily: dict[str, Any],
    errors: list[str],
) -> None:
    expected_surface = load_json(RANKING_FIXTURE)["optimizerHandoff"]

    preview_stage = build_stage_entry("growth", corrupted_ranking, preview_daily)
    current_stage = build_stage_entry("growth", corrupted_ranking, current_daily)

    expect(
        preview_stage["profileSelection"] == expected_surface["profileSelection"],
        "preview stage entry still depends on top-level profileSelection instead of optimizerHandoff",
        errors,
    )
    expect(
        preview_stage["topTopicId"] == expected_surface["rankingSummary"]["topTopicId"],
        "preview stage entry still depends on top-level rankingSummary.topTopicId instead of optimizerHandoff",
        errors,
    )
    expect(
        preview_stage["priorityCounts"]
        == expected_surface["rankingSummary"]["priorityCounts"],
        "preview stage entry still depends on top-level rankingSummary.priorityCounts instead of optimizerHandoff",
        errors,
    )
    expect(
        current_stage["topTopicId"] == "tp_corrupted_top_001",
        "current stage entry should still read top-level rankingSummary during the live lane",
        errors,
    )
    expect(
        current_stage["profileSelection"]["resolvedProfileId"] == "corrupted-profile",
        "current stage entry should still read top-level profileSelection during the live lane",
        errors,
    )


def validate_workflow_summary_cutover(
    corrupted_ranking: dict[str, Any],
    preview_daily_path: Path,
    preview_weekly_path: Path,
    errors: list[str],
) -> None:
    with tempfile.TemporaryDirectory(prefix="autotiktok-preview-consumer-workflow-") as temp_dir:
        temp_root = Path(temp_dir)
        ranking_path = temp_root / "ranking-corrupted.json"
        optimizer_input_manifest_path = temp_root / "optimizer-input-manifest.json"
        optimizer_input_bundle_path = temp_root / "optimizer-input-bundle.json"
        ranking_path.write_text(
            json.dumps(corrupted_ranking, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )

        preview_summary = build_summary(
            "2026-04-15T06:00:00Z",
            DISCOVERY_FIXTURE,
            ranking_path,
            optimizer_input_manifest_path,
            optimizer_input_bundle_path,
            preview_daily_path,
            preview_weekly_path,
            "basename",
        )
        current_summary = build_summary(
            "2026-04-15T06:00:00Z",
            DISCOVERY_FIXTURE,
            ranking_path,
            optimizer_input_manifest_path,
            optimizer_input_bundle_path,
            CURRENT_DAILY_FIXTURE,
            CURRENT_WEEKLY_FIXTURE,
            "basename",
        )

    expect(
        preview_summary["summary"]["resolvedProfileId"] == "growth-default",
        "preview workflow summary still depends on top-level profileSelection instead of optimizerHandoff",
        errors,
    )
    expect(
        preview_summary["summary"]["topTopicId"] == "tp_evergreen_ad_mistakes_001",
        "preview workflow summary still depends on top-level rankingSummary.topTopicId instead of optimizerHandoff",
        errors,
    )
    expect(
        preview_summary["summary"]["candidateSourceKind"] == "discovery_artifact",
        "preview workflow summary still depends on top-level candidateSource.sourceKind instead of optimizerHandoff",
        errors,
    )
    expect(
        current_summary["summary"]["resolvedProfileId"] == "corrupted-profile",
        "current workflow summary should still read top-level profileSelection during the live lane",
        errors,
    )
    expect(
        current_summary["summary"]["topTopicId"] == "tp_corrupted_top_001",
        "current workflow summary should still read top-level rankingSummary during the live lane",
        errors,
    )
    expect(
        current_summary["summary"]["candidateSourceKind"] == "corrupted_source_kind",
        "current workflow summary should still read top-level candidateSource during the live lane",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    try:
        corrupted_ranking = build_corrupted_ranking_payload()
        with tempfile.TemporaryDirectory(prefix="autotiktok-preview-consumer-cutover-") as temp_dir:
            temp_root = Path(temp_dir)
            preview_daily_path = temp_root / "daily-preview.json"
            preview_weekly_path = temp_root / "weekly-preview.json"

            run_script(
                DAILY_REVIEW_SCRIPT,
                "--ranking-input",
                str(RANKING_FIXTURE),
                "--ranking-contract-version",
                "ranking-optimizer-contract.vNext-preview",
                "--ranking-contract-validation-mode",
                "exact",
                "--output",
                str(preview_daily_path),
            )
            run_script(
                WEEKLY_PROMOTION_SCRIPT,
                "--daily-review-input",
                str(preview_daily_path),
                "--output",
                str(preview_weekly_path),
            )

            preview_daily = load_json(preview_daily_path)
            current_daily = load_json(CURRENT_DAILY_FIXTURE)
            validate_stage_entry_cutover(corrupted_ranking, preview_daily, current_daily, errors)
            validate_workflow_summary_cutover(
                corrupted_ranking,
                preview_daily_path,
                preview_weekly_path,
                errors,
            )
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] Preview consumer cutover audit found remaining legacy top-level dependencies:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Preview consumer cutover audit confirms downstream preview lanes read optimizerHandoff.")
    print("- stage entry preview lane ignores corrupted top-level ranking mirrors")
    print("- workflow summary preview lane ignores corrupted top-level ranking mirrors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
