#!/usr/bin/env python3
"""
Validate semantic expectations for discovery merge, dedupe, and packaging output.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    try:
        payload = load_json(DISCOVERY_OUTPUT)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors: list[str] = []
    candidates = payload.get("candidates", [])
    evidence_bundles = payload.get("evidenceBundles", [])
    merge_groups = payload.get("mergeGroups", [])

    candidate_by_fingerprint = {
        candidate.get("topicFingerprint"): candidate
        for candidate in candidates
        if isinstance(candidate, dict)
    }
    bundle_by_fingerprint = {
        bundle.get("topicFingerprint"): bundle
        for bundle in evidence_bundles
        if isinstance(bundle, dict)
    }
    merge_by_fingerprint = {
        group.get("topicFingerprint"): group
        for group in merge_groups
        if isinstance(group, dict)
    }

    allowed_merge_classes = {
        "single_signal",
        "same_source_cluster",
        "cross_source_cluster",
    }
    allowed_dedupe_decisions = {
        "no_dedupe_required",
        "keep_multi_angle_cluster",
        "preserve_multi_intent_evidence",
        "collapse_duplicate_signal_variants",
    }
    allowed_packaging_risks = {
        "freshness_sensitive",
        "coordination_heavy",
        "cross_source",
        "lightweight",
    }

    for topic_fingerprint, candidate in sorted(candidate_by_fingerprint.items()):
        prefix = f"candidate[{topic_fingerprint}]"
        bundle = bundle_by_fingerprint.get(topic_fingerprint)
        merge_group = merge_by_fingerprint.get(topic_fingerprint)
        expect(bundle is not None, f"{prefix} must have a matching evidence bundle", errors)
        expect(merge_group is not None, f"{prefix} must have a matching merge group", errors)
        if bundle is None or merge_group is None:
            continue

        search_evidence = candidate.get("searchEvidence", {})
        execution_profile = candidate.get("executionProfile", {})
        search_summary = bundle.get("searchEvidenceSummary", {})
        execution_summary = bundle.get("executionEvidenceSummary", {})
        packaging_readiness = merge_group.get("packagingReadiness", {})

        expect(
            bundle.get("mergeClassification") in allowed_merge_classes,
            f"{prefix} evidence bundle mergeClassification is invalid",
            errors,
        )
        expect(
            merge_group.get("mergeClassification") in allowed_merge_classes,
            f"{prefix} merge group mergeClassification is invalid",
            errors,
        )
        expect(
            candidate.get("mergeClassification") == bundle.get("mergeClassification") == merge_group.get("mergeClassification"),
            f"{prefix} mergeClassification must align across candidate, evidence bundle, and merge group",
            errors,
        )
        expect(
            candidate.get("dedupeDecision") in allowed_dedupe_decisions,
            f"{prefix} dedupeDecision is invalid",
            errors,
        )
        expect(
            candidate.get("dedupeDecision") == merge_group.get("dedupeDecision"),
            f"{prefix} dedupeDecision must align with merge group",
            errors,
        )
        expect(
            search_summary.get("queryCount") == search_evidence.get("queryCount"),
            f"{prefix} queryCount must align between searchEvidence and searchEvidenceSummary",
            errors,
        )
        expect(
            execution_summary.get("recommendedFormatCount")
            == execution_profile.get("recommendedFormatCount"),
            f"{prefix} recommendedFormatCount must align between executionProfile and executionEvidenceSummary",
            errors,
        )
        expect(
            execution_summary.get("requiredAssetCount")
            == execution_profile.get("requiredAssetCount"),
            f"{prefix} requiredAssetCount must align between executionProfile and executionEvidenceSummary",
            errors,
        )
        expect(
            execution_summary.get("requiredCapabilityCount")
            == execution_profile.get("requiredCapabilityCount"),
            f"{prefix} requiredCapabilityCount must align between executionProfile and executionEvidenceSummary",
            errors,
        )
        expect(
            search_summary.get("coverageLabel") == search_evidence.get("coverageLabel"),
            f"{prefix} search coverage label must align between candidate and evidence bundle",
            errors,
        )
        expect(
            packaging_readiness.get("searchCoverageLabel") == search_evidence.get("coverageLabel"),
            f"{prefix} packagingReadiness searchCoverageLabel must align with candidate searchEvidence",
            errors,
        )
        expect(
            packaging_readiness.get("executionComplexityLabel")
            == execution_profile.get("complexityLabel"),
            f"{prefix} packagingReadiness executionComplexityLabel must align with candidate executionProfile",
            errors,
        )
        expect(
            execution_profile.get("packagingRisk") in allowed_packaging_risks,
            f"{prefix} packagingRisk is invalid",
            errors,
        )
        expect(
            execution_summary.get("packagingRisk") == execution_profile.get("packagingRisk"),
            f"{prefix} packagingRisk must align between executionProfile and evidence summary",
            errors,
        )
        expect(
            packaging_readiness.get("packagingRisk") == execution_profile.get("packagingRisk"),
            f"{prefix} packagingReadiness packagingRisk must align with candidate executionProfile",
            errors,
        )

    trend_candidate = candidate_by_fingerprint.get("fp.trend.consumer.wired_earbuds_comeback")
    trend_bundle = bundle_by_fingerprint.get("fp.trend.consumer.wired_earbuds_comeback")
    trend_merge = merge_by_fingerprint.get("fp.trend.consumer.wired_earbuds_comeback")
    if trend_candidate and trend_bundle and trend_merge:
        expect(
            trend_candidate["executionProfile"]["packagingRisk"] == "freshness_sensitive",
            "trend candidate should remain freshness_sensitive",
            errors,
        )
        expect(
            bool(trend_bundle.get("videoSampleIds")),
            "trend evidence bundle should keep video sample evidence",
            errors,
        )
        expect(
            trend_merge.get("packagingReadiness", {}).get("hasVideoEvidence") is True,
            "trend merge group should report video evidence",
            errors,
        )

    if errors:
        print("[ERROR] Discovery merge-packaging expectations failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Discovery merge-packaging expectations are satisfied.")
    print(f"Discovery output: {DISCOVERY_OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
