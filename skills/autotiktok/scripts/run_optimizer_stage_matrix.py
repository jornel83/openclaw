#!/usr/bin/env python3
"""
Run deterministic ranking + daily-review replays across multiple stage modes and emit a compact optimizer matrix.
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

RANKING_SCRIPT = ROOT / "skills" / "autotiktok-topic-ranking" / "scripts" / "dry_run_ranking.py"
DAILY_REVIEW_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "daily_review_mock.py"
)

DEFAULT_CANDIDATES = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)
DEFAULT_CONTEXT_MATRIX = SHARED_FIXTURES / "scoring-context-matrix.fixture.json"
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


def resolve_stage_contexts(
    context_matrix_payload: dict[str, Any], requested_stage_modes: list[str]
) -> list[tuple[str, dict[str, Any]]]:
    stages = context_matrix_payload.get("stages")
    if not isinstance(stages, list) or not stages:
        raise ValueError("context matrix payload must include a non-empty `stages` list")

    stage_map: dict[str, dict[str, Any]] = {}
    for stage_entry in stages:
        if not isinstance(stage_entry, dict):
            raise ValueError("context matrix entries must be objects")
        stage_mode = stage_entry.get("stageMode")
        context = stage_entry.get("context")
        if not isinstance(stage_mode, str) or not isinstance(context, dict):
            raise ValueError("context matrix entries must include `stageMode` and `context`")
        stage_map[stage_mode] = context

    resolved: list[tuple[str, dict[str, Any]]] = []
    for stage_mode in requested_stage_modes:
        if stage_mode not in stage_map:
            raise ValueError(f"context matrix missing requested stageMode `{stage_mode}`")
        resolved.append((stage_mode, stage_map[stage_mode]))
    return resolved


def build_stage_entry(
    stage_mode: str,
    ranking_payload: dict[str, Any],
    daily_review_payload: dict[str, Any],
) -> dict[str, Any]:
    ranking_contract_version = (
        daily_review_payload.get("generatedFrom", {}).get(
            "rankingOptimizerContractVersion",
            RANKING_OPTIMIZER_CONTRACT_VERSION,
        )
    )
    ranking_surface_payload = select_optimizer_handoff_payload(
        ranking_payload,
        contract_version=ranking_contract_version,
    )
    shadow_rows = daily_review_payload.get("shadowLeaderboard", [])
    shadow_leader = shadow_rows[0]["profileId"] if shadow_rows else None
    return {
        "stageMode": stage_mode,
        "profileId": daily_review_payload["profileId"],
        "profileSelection": ranking_surface_payload["profileSelection"],
        "candidateSource": daily_review_payload["candidateSource"],
        "topTopicId": ranking_surface_payload["rankingSummary"]["topTopicId"],
        "topTopicTitle": ranking_surface_payload["rankingSummary"]["topTopicTitle"],
        "rejectedTopicIds": ranking_surface_payload["rankingSummary"]["rejectedTopicIds"],
        "priorityCounts": ranking_surface_payload["rankingSummary"]["priorityCounts"],
        "topicReward": daily_review_payload["topicRewardBreakdown"]["topicReward"],
        "combinedReward": daily_review_payload["combinedRewardBreakdown"]["combinedReward"],
        "performanceWeight": daily_review_payload["combinedRewardBreakdown"]["performanceWeight"],
        "recommendationKind": daily_review_payload["recommendation"]["kind"],
        "shadowLeaderProfileId": shadow_leader,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--context-matrix", type=Path, default=DEFAULT_CONTEXT_MATRIX)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--backfills-input", type=Path, default=DEFAULT_BACKFILLS)
    parser.add_argument("--performance-input", type=Path, default=DEFAULT_PERFORMANCE)
    parser.add_argument("--challenger-input", dest="challenger_input", type=Path, default=DEFAULT_CHALLENGERS)
    parser.add_argument("--challenger-adjustments", dest="challenger_input", type=Path)
    parser.add_argument(
        "--stage-modes",
        nargs="+",
        default=["growth", "scale", "search_priority"],
    )
    parser.add_argument("--matrix-id", default="optimizer-stage-matrix.autotiktok.fixture.2026-04-15")
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
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        context_matrix_payload = load_json(args.context_matrix)
        stage_contexts = resolve_stage_contexts(context_matrix_payload, args.stage_modes)

        stage_entries: list[dict[str, Any]] = []
        generated_from: dict[str, Any] | None = None

        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-matrix-") as temp_dir:
            temp_root = Path(temp_dir)
            for stage_mode, context_payload in stage_contexts:
                context_path = temp_root / f"context-{stage_mode}.json"
                ranking_path = temp_root / f"ranking-{stage_mode}.json"
                daily_review_path = temp_root / f"daily-review-{stage_mode}.json"
                context_path.write_text(
                    json.dumps(context_payload, ensure_ascii=True, indent=2) + "\n",
                    encoding="utf-8",
                )

                run_script(
                    RANKING_SCRIPT,
                    "--candidates",
                    str(args.candidates),
                    "--context",
                    str(context_path),
                    "--profiles",
                    str(args.profiles),
                    "--profile-id",
                    "auto",
                    "--snapshot-id",
                    f"snap.autotiktok.optimizer-matrix.{stage_mode}.fixture.2026-04-15",
                    "--run-id",
                    f"run.autotiktok.optimizer-matrix.{stage_mode}.fixture.2026-04-15",
                    "--created-at",
                    args.generated_at,
                    "--output",
                    str(ranking_path),
                )
                run_script(
                    DAILY_REVIEW_SCRIPT,
                    "--ranking-input",
                    str(ranking_path),
                    "--context-input",
                    str(context_path),
                    "--backfills-input",
                    str(args.backfills_input),
                    "--performance-input",
                    str(args.performance_input),
                    "--challenger-input",
                    str(args.challenger_input),
                    "--ranking-contract-version",
                    args.ranking_contract_version,
                    "--ranking-contract-validation-mode",
                    args.ranking_contract_validation_mode,
                    "--report-id",
                    f"daily-review.autotiktok.optimizer-matrix.{stage_mode}.fixture.2026-04-15",
                    "--generated-at",
                    args.generated_at,
                    "--output",
                    str(daily_review_path),
                )

                ranking_payload = load_json(ranking_path)
                daily_review_payload = load_json(daily_review_path)
                ranking_surface_payload = select_optimizer_handoff_payload(
                    ranking_payload,
                    contract_version=daily_review_payload.get("generatedFrom", {}).get(
                        "rankingOptimizerContractVersion",
                        args.ranking_contract_version,
                    ),
                )
                stage_entries.append(
                    build_stage_entry(stage_mode, ranking_payload, daily_review_payload)
                )

                if generated_from is None:
                    generated_from = {
                        "contextMatrixFixtureVersion": context_matrix_payload.get("fixtureSetVersion"),
                        "candidateInputSchemaVersion": ranking_surface_payload["predictionRun"].get(
                            "candidateInputSchemaVersion"
                        ),
                        "candidateSourceKind": ranking_surface_payload["candidateSource"].get("sourceKind"),
                        "candidateSourceInputKind": ranking_surface_payload["candidateSource"].get(
                            "sourceInputKind"
                        ),
                        "candidateSourceMaterializationId": ranking_surface_payload[
                            "candidateSource"
                        ].get("sourceMaterializationId"),
                        "candidateSourceNormalizationRuleVersion": ranking_surface_payload[
                            "candidateSource"
                        ].get("sourceNormalizationRuleVersion"),
                        "discoveryPolicyVersion": ranking_surface_payload["candidateSource"].get(
                            "sourcePolicyVersion"
                        ),
                        "rankingScoringCodeVersion": ranking_surface_payload["predictionRun"].get(
                            "scoringCodeVersion"
                        ),
                        "optimizerPolicyVersion": daily_review_payload.get("policyVersion"),
                        "challengerSchemaVersion": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("challengerSchemaVersion"),
                        "challengerInputKind": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("challengerInputKind"),
                        "rankingOptimizerContractId": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerContractId"),
                        "rankingOptimizerContractVersion": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerContractVersion"),
                        "rankingOptimizerContractValidationMode": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerContractValidationMode"),
                        "rankingOptimizerContractValidated": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerContractValidated"),
                        "rankingOptimizerSurfaceSource": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerSurfaceSource"),
                        "rankingOptimizerDeprecationPhase": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerDeprecationPhase"),
                        "rankingOptimizerCanonicalSurface": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerCanonicalSurface"),
                        "rankingOptimizerDeprecatedTopLevelFields": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerDeprecatedTopLevelFields"),
                        "rankingOptimizerNextHardFailContractVersion": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerNextHardFailContractVersion"),
                        "rankingOptimizerCompatApplied": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerCompatApplied"),
                        "rankingOptimizerCompatAliasesApplied": daily_review_payload.get(
                            "generatedFrom", {}
                        ).get("rankingOptimizerCompatAliasesApplied"),
                    }

        payload = {
            "schemaVersion": "optimizer-stage-matrix.v1",
            "matrixId": args.matrix_id,
            "generatedAt": args.generated_at,
            "generatedFrom": generated_from or {},
            "stages": stage_entries,
        }
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote optimizer stage matrix to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
