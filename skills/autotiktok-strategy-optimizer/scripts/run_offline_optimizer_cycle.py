#!/usr/bin/env python3
"""
Run an offline optimizer cycle and optionally include a weekly promotion decision.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from daily_review_service import build_daily_review_report
from optimizer_input_adapters import load_daily_review_runtime_inputs
from optimizer_lib import DEFAULT_POLICY, build_weekly_decision
from reward_lib import load_json
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING_OUTPUT = (
    DEFAULT_ROOT.parent / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
DEFAULT_CONTEXT = DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
DEFAULT_BACKFILLS = DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-run.sample.json"
DEFAULT_PERFORMANCE = DEFAULT_ROOT / "fixtures" / "post-performance-signal-run.sample.json"
DEFAULT_CHALLENGER_INPUT = DEFAULT_ROOT / "fixtures" / "challenger-evaluation-run.sample.json"


def build_cycle_payload(args: argparse.Namespace) -> dict[str, object]:
    inputs = load_daily_review_runtime_inputs(
        input_manifest=args.input_manifest,
        input_bundle=args.input_bundle,
        ranking_input=args.ranking_input,
        context_input=args.context_input,
        backfills_input=args.backfills_input,
        performance_input=args.performance_input,
        challenger_input=args.challenger_input,
        policy_input=args.policy,
        contract_version=args.ranking_contract_version,
        validation_mode=args.ranking_contract_validation_mode,
    )
    daily_review = build_daily_review_report(
        inputs,
        report_id=args.report_id,
        generated_at=args.generated_at,
    )
    weekly_promotion = None
    if args.include_weekly_promotion:
        weekly_review_window_input = getattr(args, "weekly_review_window_input", None)
        weekly_input = (
            load_json(weekly_review_window_input)
            if weekly_review_window_input is not None
            else daily_review
        )
        weekly_promotion = build_weekly_decision(weekly_input, inputs.policy)

    shadow_rows = daily_review.get("shadowLeaderboard", [])
    leader_profile_id = shadow_rows[0]["profileId"] if shadow_rows else None
    manifest_generated_from = daily_review.get("generatedFrom", {}).get(
        "optimizerInputManifestGeneratedFrom",
        {},
    )
    return {
        "schemaVersion": "optimizer-offline-cycle.v1",
        "cycleId": args.cycle_id,
        "generatedAt": args.generated_at,
        "mode": "daily_with_weekly_promotion"
        if args.include_weekly_promotion
        else "daily_review_only",
        "summary": {
            "profileId": daily_review.get("profileId"),
            "dailyRecommendation": daily_review.get("recommendation", {}).get("kind"),
            "shadowLeaderProfileId": leader_profile_id,
            "challengerInputKind": daily_review.get("generatedFrom", {}).get(
                "challengerInputKind"
            ),
            "weeklyDecision": None
            if weekly_promotion is None
            else weekly_promotion.get("decision"),
            "selectedChallengerProfileId": None
            if weekly_promotion is None
            else weekly_promotion.get("selectedChallengerProfileId"),
        },
        "generatedFrom": {
            "policyVersion": inputs.policy.get("schemaVersion"),
            "rankingRunId": daily_review.get("runId"),
            "rankingSnapshotId": daily_review.get("generatedFrom", {}).get(
                "rankingSnapshotId"
            ),
            "rankingProfileId": daily_review.get("generatedFrom", {}).get(
                "rankingProfileId"
            ),
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
            "optimizerInputManifestSchemaVersion": daily_review.get("generatedFrom", {}).get(
                "optimizerInputManifestSchemaVersion"
            ),
            "optimizerInputManifestId": daily_review.get("generatedFrom", {}).get(
                "optimizerInputManifestId"
            ),
            "optimizerInputSourceRegistrySchemaVersion": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceRegistrySchemaVersion"),
            "optimizerInputSourceRegistryId": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSourceRegistryId"
            ),
            "optimizerInputArtifactResolverSchemaVersion": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputArtifactResolverSchemaVersion"),
            "optimizerInputArtifactResolverId": daily_review.get("generatedFrom", {}).get(
                "optimizerInputArtifactResolverId"
            ),
            "optimizerInputSourceProviderCatalogSchemaVersion": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderCatalogSchemaVersion"),
            "optimizerInputSourceProviderCatalogId": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderCatalogId"),
            "optimizerInputSourceProviderRegistrySchemaVersion": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderRegistrySchemaVersion"),
            "optimizerInputSourceProviderRegistryId": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderRegistryId"),
            "optimizerInputSourceArtifactCatalogSchemaVersion": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceArtifactCatalogSchemaVersion"),
            "optimizerInputSourceArtifactCatalogId": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceArtifactCatalogId"),
            "optimizerInputSourceLane": manifest_generated_from.get("sourceLane"),
            "optimizerInputSourceProviderLane": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSourceProviderLane"
            ),
            "optimizerInputSourceProviderKind": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSourceProviderKind"
            ),
            "optimizerInputSourceProviderClass": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSourceProviderClass"
            ),
            "optimizerInputSourceProviderHandle": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSourceProviderHandle"
            ),
            "optimizerInputSourceProviderLocatorKind": daily_review.get(
                "generatedFrom", {}
            ).get("optimizerInputSourceProviderLocatorKind"),
            "optimizerInputSourceProviderOwner": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSourceProviderOwner"
            ),
            "optimizerInputArtifactLocatorKind": daily_review.get("generatedFrom", {}).get(
                "optimizerInputArtifactLocatorKind"
            ),
            "optimizerInputRolloutPolicySchemaVersion": manifest_generated_from.get(
                "inputRolloutPolicySchemaVersion"
            ),
            "optimizerInputRolloutPolicyId": manifest_generated_from.get(
                "inputRolloutPolicyId"
            ),
            "optimizerInputRolloutClass": manifest_generated_from.get(
                "inputRolloutClass"
            ),
            "optimizerInputLaneSelectionSource": manifest_generated_from.get(
                "inputLaneSelectionSource"
            ),
            "optimizerInputRolloutStrategy": manifest_generated_from.get(
                "inputRolloutStrategy"
            ),
            "optimizerInputSources": daily_review.get("generatedFrom", {}).get(
                "optimizerInputSources", {}
            ),
            "rankingOptimizerContractId": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerContractId"
            ),
            "rankingOptimizerContractVersion": daily_review.get("generatedFrom", {}).get(
                "rankingOptimizerContractVersion"
            ),
            "rankingOptimizerContractValidationMode": daily_review.get(
                "generatedFrom", {}
            ).get("rankingOptimizerContractValidationMode"),
            "weeklyReviewWindowSchemaVersion": None
            if weekly_promotion is None
            else weekly_promotion.get("generatedFrom", {}).get(
                "weeklyReviewWindowSchemaVersion"
            ),
            "weeklyReviewWindowId": None
            if weekly_promotion is None
            else weekly_promotion.get("generatedFrom", {}).get(
                "weeklyReviewWindowId"
            ),
        },
        "artifacts": {
            "dailyReview": daily_review,
            "weeklyPromotion": weekly_promotion,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--input-bundle", type=Path)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING_OUTPUT)
    parser.add_argument("--context-input", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--backfills-input", type=Path, default=DEFAULT_BACKFILLS)
    parser.add_argument("--performance-input", type=Path, default=DEFAULT_PERFORMANCE)
    parser.add_argument(
        "--challenger-input", dest="challenger_input", type=Path, default=DEFAULT_CHALLENGER_INPUT
    )
    parser.add_argument("--challenger-adjustments", dest="challenger_input", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--ranking-contract-version",
        default=RANKING_OPTIMIZER_CONTRACT_VERSION,
    )
    parser.add_argument(
        "--ranking-contract-validation-mode",
        default=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        choices=(
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
        ),
    )
    parser.add_argument("--cycle-id", default="optimizer-offline-cycle.autotiktok.fixture.2026-04-15")
    parser.add_argument("--report-id", default="daily-review.autotiktok.fixture.2026-04-15")
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--include-weekly-promotion", action="store_true")
    parser.add_argument("--weekly-review-window-input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = build_cycle_payload(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote offline optimizer cycle to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
