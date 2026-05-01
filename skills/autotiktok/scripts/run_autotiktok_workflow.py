#!/usr/bin/env python3
"""
Run the three AutoTikTok skills as one end-to-end mock workflow.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE
from ranking_optimizer_contract_lib import RANKING_OPTIMIZER_CONTRACT_VERSION
from ranking_optimizer_contract_lib import SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES
from ranking_optimizer_contract_lib import SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS
from ranking_optimizer_contract_lib import select_optimizer_handoff_payload


ROOT = Path(__file__).resolve().parents[3]
HUB_DIR = Path(__file__).resolve().parents[1]
SHARED_FIXTURES = HUB_DIR / "fixtures"

DISCOVERY_SCRIPT = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "scripts" / "discovery_dry_run.py"
)
DISCOVERY_CONTRACT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "scripts"
    / "check_topic_candidate_contract.py"
)
RANKING_SCRIPT = ROOT / "skills" / "autotiktok-topic-ranking" / "scripts" / "dry_run_ranking.py"
DAILY_REVIEW_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "daily_review_mock.py"
)
BUILD_BUNDLE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "materialize_optimizer_input_bundle.py"
)
BUILD_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_manifest.py"
)
WEEKLY_PROMOTION_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "weekly_promotion_mock.py"
)

DEFAULT_DISCOVERY_SOURCE_SNAPSHOTS = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "source-snapshots.sample.json"
)
DEFAULT_DISCOVERY_SIGNAL_ITEMS = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "signal-items.sample.json"
)
DEFAULT_DISCOVERY_VIDEO_SAMPLES = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "video-samples.sample.json"
)
DEFAULT_DISCOVERY_MATERIALIZATION_ID = "discovery-materialization.autotiktok.fixture.2026-04-15"
DEFAULT_DISCOVERY_MATERIALIZATION_SCHEMA_VERSION = "discovery-snapshot-materialization.sample.v1"
DEFAULT_CONTEXT = SHARED_FIXTURES / "scoring-context.fixture.json"
DEFAULT_PROFILES = SHARED_FIXTURES / "scoring-profiles.fixture.json"
DEFAULT_BACKFILLS = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "topic-outcome-backfill-run.sample.json"
)
DEFAULT_PERFORMANCE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "post-performance-signal-run.sample.json"
)
DEFAULT_CHALLENGERS = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "challenger-evaluation-run.sample.json"
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


def path_label(path: Path, style: str) -> str:
    if style == "basename":
        return path.name
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def build_summary(
    generated_at: str,
    discovery_path: Path,
    ranking_path: Path,
    optimizer_input_manifest_path: Path,
    optimizer_input_bundle_path: Path,
    daily_review_path: Path,
    weekly_promotion_path: Path,
    artifact_path_style: str,
) -> dict[str, Any]:
    discovery = load_json(discovery_path)
    ranking = load_json(ranking_path)
    daily_review = load_json(daily_review_path)
    weekly_promotion = load_json(weekly_promotion_path)
    ranking_surface_payload = select_optimizer_handoff_payload(
        ranking,
        contract_version=daily_review.get("generatedFrom", {}).get(
            "rankingOptimizerContractVersion",
            RANKING_OPTIMIZER_CONTRACT_VERSION,
        ),
    )

    return {
        "schemaVersion": "autotiktok-workflow-run.v1",
        "generatedAt": generated_at,
        "artifactPaths": {
            "discovery": path_label(discovery_path, artifact_path_style),
            "ranking": path_label(ranking_path, artifact_path_style),
            "optimizerInputManifest": path_label(
                optimizer_input_manifest_path, artifact_path_style
            ),
            "optimizerInputBundle": path_label(
                optimizer_input_bundle_path, artifact_path_style
            ),
            "dailyReview": path_label(daily_review_path, artifact_path_style),
            "weeklyPromotion": path_label(weekly_promotion_path, artifact_path_style),
        },
        "summary": {
            "candidateCount": len(discovery.get("candidates", [])),
            "profileId": ranking_surface_payload.get("profileId"),
            "requestedProfileId": ranking_surface_payload.get("profileSelection", {}).get("requestedProfileId"),
            "resolvedProfileId": ranking_surface_payload.get("profileSelection", {}).get("resolvedProfileId"),
            "profileSelectionSource": ranking_surface_payload.get("profileSelection", {}).get("selectionSource"),
            "rankingSnapshotId": ranking_surface_payload.get("predictionRun", {}).get("snapshotId"),
            "candidateSourceKind": ranking_surface_payload.get("candidateSource", {}).get("sourceKind"),
            "candidateSourceSnapshotId": ranking_surface_payload.get("candidateSource", {}).get("sourceSnapshotId"),
            "candidateSourcePolicyVersion": ranking_surface_payload.get("candidateSource", {}).get("sourcePolicyVersion"),
            "topTopicId": ranking_surface_payload.get("rankingSummary", {}).get("topTopicId"),
            "topTopicTitle": ranking_surface_payload.get("rankingSummary", {}).get("topTopicTitle"),
            "combinedReward": daily_review.get("combinedRewardBreakdown", {}).get("combinedReward"),
            "dailyRecommendation": daily_review.get("recommendation", {}).get("kind"),
            "weeklyDecision": weekly_promotion.get("decision"),
            "selectedChallengerProfileId": weekly_promotion.get("selectedChallengerProfileId"),
        },
        "generatedFrom": {
            "discoveryPolicyVersion": discovery.get("policyVersion"),
            "discoveryInputKind": discovery.get("generatedFrom", {}).get("inputKind"),
            "discoveryInputSchemaVersion": discovery.get("generatedFrom", {}).get(
                "inputSchemaVersion"
            ),
            "discoveryNormalizationRuleVersion": discovery.get("generatedFrom", {}).get(
                "normalizationRuleVersion"
            ),
            "discoveryMaterializationId": discovery.get("generatedFrom", {}).get(
                "materializationId"
            ),
            "discoveryMaterializationSource": discovery.get("generatedFrom", {}).get(
                "materializationSource"
            ),
            "sourceSnapshotSchemaVersion": discovery.get("generatedFrom", {}).get(
                "sourceSnapshotSchemaVersion"
            ),
            "signalItemsSchemaVersion": discovery.get("generatedFrom", {}).get(
                "signalItemsSchemaVersion"
            ),
            "videoSamplesSchemaVersion": discovery.get("generatedFrom", {}).get(
                "videoSamplesSchemaVersion"
            ),
            "candidateSourceInputKind": ranking_surface_payload.get("candidateSource", {}).get(
                "sourceInputKind"
            ),
            "candidateSourceMaterializationId": ranking_surface_payload.get(
                "candidateSource", {}
            ).get("sourceMaterializationId"),
            "candidateSourceNormalizationRuleVersion": ranking_surface_payload.get(
                "candidateSource", {}
            ).get("sourceNormalizationRuleVersion"),
            "candidateInputSchemaVersion": ranking_surface_payload.get("predictionRun", {}).get(
                "candidateInputSchemaVersion"
            ),
            "rankingScoringCodeVersion": ranking_surface_payload.get("predictionRun", {}).get(
                "scoringCodeVersion"
            ),
            "optimizerPolicyVersion": daily_review.get("policyVersion"),
            "weeklyPolicyVersion": weekly_promotion.get("generatedFrom", {}).get("policyVersion"),
            "challengerSchemaVersion": daily_review.get("generatedFrom", {}).get(
                "challengerSchemaVersion"
            ),
            "challengerInputKind": daily_review.get("generatedFrom", {}).get(
                "challengerInputKind"
            ),
            "optimizerInputBundleSchemaVersion": daily_review.get("generatedFrom", {}).get(
                "optimizerInputBundleSchemaVersion"
            ),
            "optimizerInputBundleId": daily_review.get("generatedFrom", {}).get(
                "optimizerInputBundleId"
            ),
            "optimizerInputManifestSchemaVersion": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputManifestSchemaVersion"),
            "optimizerInputManifestId": daily_review.get("generatedFrom", {}).get(
                "optimizerInputManifestId"
            ),
            "rankingOptimizerContractId": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerContractId"
            ),
            "rankingOptimizerContractVersion": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerContractVersion"
            ),
            "rankingOptimizerContractValidationMode": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerContractValidationMode"
            ),
            "rankingOptimizerContractValidated": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerContractValidated"
            ),
            "rankingOptimizerSurfaceSource": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerSurfaceSource"
            ),
            "rankingOptimizerDeprecationPhase": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerDeprecationPhase"
            ),
            "rankingOptimizerCanonicalSurface": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerCanonicalSurface"
            ),
            "rankingOptimizerDeprecatedTopLevelFields": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerDeprecatedTopLevelFields"
            ),
            "rankingOptimizerNextHardFailContractVersion": daily_review.get(
                "generatedFrom", {}
            ).get("rankingOptimizerNextHardFailContractVersion"),
            "rankingOptimizerCompatApplied": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerCompatApplied"
            ),
            "rankingOptimizerCompatAliasesApplied": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerCompatAliasesApplied"
            ),
        },
    }


def run_workflow(args: argparse.Namespace, artifacts_dir: Path) -> dict[str, Any]:
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    discovery_path = artifacts_dir / "discovery.json"
    ranking_path = artifacts_dir / "ranking.json"
    optimizer_input_manifest_path = artifacts_dir / "optimizer-input-manifest.json"
    optimizer_input_bundle_path = artifacts_dir / "optimizer-input-bundle.json"
    daily_review_path = artifacts_dir / "daily-review.json"
    weekly_promotion_path = artifacts_dir / "weekly-promotion.json"

    discovery_args = ["--output", str(discovery_path)]
    if args.discovery_input is not None:
        discovery_args[:0] = ["--input", str(args.discovery_input)]
    else:
        discovery_args[:0] = [
            "--source-snapshots",
            str(args.discovery_source_snapshots),
            "--signal-items",
            str(args.discovery_signal_items),
            "--video-samples",
            str(args.discovery_video_samples),
            "--materialization-id",
            args.discovery_materialization_id,
            "--materialization-schema-version",
            args.discovery_materialization_schema_version,
        ]
    run_script(DISCOVERY_SCRIPT, *discovery_args)
    run_script(DISCOVERY_CONTRACT, "--input", str(discovery_path))
    run_script(
        RANKING_SCRIPT,
        "--candidates",
        str(discovery_path),
        "--context",
        str(args.context),
        "--profiles",
        str(args.profiles),
        "--profile-id",
        args.profile_id,
        "--snapshot-id",
        args.snapshot_id,
        "--run-id",
        args.run_id,
        "--created-at",
        args.created_at,
        "--output",
        str(ranking_path),
    )
    run_script(
        BUILD_MANIFEST_SCRIPT,
        "--ranking-input",
        str(ranking_path),
        "--context-input",
        str(args.context),
        "--backfills-input",
        str(args.backfills_input),
        "--performance-input",
        str(args.performance_input),
        "--challenger-input",
        str(args.challenger_input),
        "--output",
        str(optimizer_input_manifest_path),
    )
    run_script(
        BUILD_BUNDLE_SCRIPT,
        "--input-manifest",
        str(optimizer_input_manifest_path),
        "--output",
        str(optimizer_input_bundle_path),
    )
    run_script(
        DAILY_REVIEW_SCRIPT,
        "--input-bundle",
        str(optimizer_input_bundle_path),
        "--ranking-contract-version",
        args.ranking_contract_version,
        "--ranking-contract-validation-mode",
        args.ranking_contract_validation_mode,
        "--report-id",
        args.report_id,
        "--generated-at",
        args.generated_at,
        "--output",
        str(daily_review_path),
    )
    run_script(
        WEEKLY_PROMOTION_SCRIPT,
        "--daily-review-input",
        str(daily_review_path),
        "--output",
        str(weekly_promotion_path),
    )

    return build_summary(
        args.generated_at,
        discovery_path,
        ranking_path,
        optimizer_input_manifest_path,
        optimizer_input_bundle_path,
        daily_review_path,
        weekly_promotion_path,
        args.artifact_path_style,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--discovery-input",
        "--signals",
        dest="discovery_input",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--discovery-source-snapshots",
        type=Path,
        default=DEFAULT_DISCOVERY_SOURCE_SNAPSHOTS,
    )
    parser.add_argument(
        "--discovery-signal-items",
        type=Path,
        default=DEFAULT_DISCOVERY_SIGNAL_ITEMS,
    )
    parser.add_argument(
        "--discovery-video-samples",
        type=Path,
        default=DEFAULT_DISCOVERY_VIDEO_SAMPLES,
    )
    parser.add_argument(
        "--discovery-materialization-id",
        default=DEFAULT_DISCOVERY_MATERIALIZATION_ID,
    )
    parser.add_argument(
        "--discovery-materialization-schema-version",
        default=DEFAULT_DISCOVERY_MATERIALIZATION_SCHEMA_VERSION,
    )
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--backfills-input", type=Path, default=DEFAULT_BACKFILLS)
    parser.add_argument("--performance-input", type=Path, default=DEFAULT_PERFORMANCE)
    parser.add_argument("--challenger-input", dest="challenger_input", type=Path, default=DEFAULT_CHALLENGERS)
    parser.add_argument("--challenger-adjustments", dest="challenger_input", type=Path)
    parser.add_argument("--profile-id", default="auto")
    parser.add_argument("--snapshot-id", default="snap.autotiktok.workflow.fixture.2026-04-15")
    parser.add_argument("--run-id", default="run.autotiktok.workflow.fixture.2026-04-15")
    parser.add_argument("--created-at", default="2026-04-15T00:00:00Z")
    parser.add_argument("--report-id", default="daily-review.autotiktok.workflow.fixture.2026-04-15")
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--ranking-contract-version",
        default=RANKING_OPTIMIZER_CONTRACT_VERSION,
        choices=SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VERSIONS,
    )
    parser.add_argument(
        "--ranking-contract-validation-mode",
        default=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        choices=SUPPORTED_RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODES,
    )
    parser.add_argument("--artifacts-dir", type=Path)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument(
        "--artifact-path-style",
        choices=("repo", "basename"),
        default="repo",
    )
    args = parser.parse_args()

    try:
        if args.artifacts_dir is not None:
            summary = run_workflow(args, args.artifacts_dir)
        else:
            with tempfile.TemporaryDirectory(prefix="autotiktok-workflow-") as temp_dir:
                summary = run_workflow(args, Path(temp_dir))
        rendered = json.dumps(summary, ensure_ascii=True, indent=2)
        if args.summary_output:
            args.summary_output.parent.mkdir(parents=True, exist_ok=True)
            args.summary_output.write_text(rendered + "\n", encoding="utf-8")
            print(f"Wrote workflow summary to {args.summary_output}")
            return 0
        print(rendered)
        return 0
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
