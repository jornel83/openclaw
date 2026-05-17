#!/usr/bin/env python3
"""
Validate the enriched signalItems lane through discovery and ranking.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_SCRIPT_DIR = ROOT / "skills" / "autotiktok-topic-discovery" / "scripts"
RANKING_SCRIPT_DIR = ROOT / "skills" / "autotiktok-topic-ranking" / "scripts"
FIXTURE_DIR = ROOT / "skills" / "autotiktok-topic-discovery" / "fixtures"
SOURCE_SNAPSHOTS_BUILDER = DISCOVERY_SCRIPT_DIR / "build_trending_source_snapshots.py"
ENRICHED_SIGNAL_ITEMS_BUILDER = DISCOVERY_SCRIPT_DIR / "build_enriched_signal_items.py"
MATERIALIZATION_BUILDER = DISCOVERY_SCRIPT_DIR / "build_discovery_snapshot_materialization.py"
DISCOVERY_RUNNER = DISCOVERY_SCRIPT_DIR / "discovery_dry_run.py"
RANKING_RUNNER = RANKING_SCRIPT_DIR / "dry_run_ranking.py"
METADATA_SIGNAL_ITEMS = FIXTURE_DIR / "signal-items.video-content-analysis-base.sample.json"
VIDEO_SAMPLES = FIXTURE_DIR / "video-samples.download-adapter.sample.json"


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
            f"{script.relative_to(ROOT)} failed\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _candidate_by_topic(payload: dict[str, Any], topic_id: str) -> dict[str, Any]:
    for candidate in payload.get("candidates", []):
        if isinstance(candidate, dict) and candidate.get("topicId") == topic_id:
            return candidate
    raise KeyError(f"candidate not found: {topic_id}")


def _score_by_topic(payload: dict[str, Any], topic_id: str) -> dict[str, Any]:
    for score in payload.get("scores", []):
        if isinstance(score, dict) and score.get("topicId") == topic_id:
            return score
    raise KeyError(f"score not found: {topic_id}")


def _run_lane(
    *,
    temp_root: Path,
    lane: str,
    signal_items: Path,
    source_snapshots: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    materialization = temp_root / f"materialization.{lane}.json"
    discovery = temp_root / f"discovery.{lane}.json"
    ranking = temp_root / f"ranking.{lane}.json"
    run_script(
        MATERIALIZATION_BUILDER,
        "--source-snapshots",
        str(source_snapshots),
        "--signal-items",
        str(signal_items),
        "--video-samples",
        str(VIDEO_SAMPLES),
        "--materialization-id",
        f"discovery-materialization.tiktok-{lane}.us.20260502t184300z",
        "--schema-version",
        "discovery-snapshot-materialization.v1",
        "--output",
        str(materialization),
    )
    run_script(
        DISCOVERY_RUNNER,
        "--input",
        str(materialization),
        "--output",
        str(discovery),
    )
    run_script(
        RANKING_RUNNER,
        "--candidates",
        str(discovery),
        "--snapshot-id",
        f"snap.autotiktok.{lane}.20260502t184300z",
        "--run-id",
        f"run.autotiktok.{lane}.20260502t184300z",
        "--created-at",
        "2026-05-02T18:43:00Z",
        "--output",
        str(ranking),
    )
    return load_json(discovery), load_json(ranking)


def validate_outputs(
    *,
    enriched_signal_items: dict[str, Any],
    metadata_discovery: dict[str, Any],
    enriched_discovery: dict[str, Any],
    metadata_ranking: dict[str, Any],
    enriched_ranking: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    summary = enriched_signal_items.get("summary")
    expect(isinstance(summary, dict), "enriched signalItems must include summary", errors)
    if isinstance(summary, dict):
        expect(summary.get("enriched") == 1, "enriched lane should have 1 enriched item", errors)
        expect(
            summary.get("metadataOnlyFallback") == 3,
            "enriched lane should preserve 3 metadata-only fallback items",
            errors,
        )

    expect(
        enriched_discovery["generatedFrom"]["inputKind"] == "snapshot_materialization",
        "enriched discovery should consume snapshot_materialization",
        errors,
    )
    expect(
        enriched_ranking["candidateSource"]["sourceKind"] == "discovery_artifact",
        "enriched ranking should consume discovery output",
        errors,
    )
    expect(
        len(enriched_discovery.get("candidates", [])) == len(metadata_discovery.get("candidates", [])),
        "metadata and enriched lanes should preserve candidate count",
        errors,
    )
    expect(
        len(enriched_ranking.get("scores", [])) == len(enriched_discovery.get("candidates", [])),
        "enriched ranking score count should match enriched discovery candidate count",
        errors,
    )

    topic_id = "tp_trend_tiktok_nuggetice"
    metadata_candidate = _candidate_by_topic(metadata_discovery, topic_id)
    enriched_candidate = _candidate_by_topic(enriched_discovery, topic_id)
    metadata_score = _score_by_topic(metadata_ranking, topic_id)
    enriched_score = _score_by_topic(enriched_ranking, topic_id)
    expect(
        "MP4 analysis adds" not in metadata_candidate["topicSummary"],
        "metadata candidate should not contain MP4 summary",
        errors,
    )
    expect(
        "MP4 analysis adds" in enriched_candidate["topicSummary"],
        "enriched candidate should contain MP4 summary",
        errors,
    )
    expect(
        "video understanding sidecar" in enriched_candidate["executionProfile"]["requiredAssets"],
        "enriched candidate should expose video understanding sidecar asset",
        errors,
    )
    expect(
        enriched_score["scoreBreakdown"]["rewrite"] > metadata_score["scoreBreakdown"]["rewrite"],
        "enriched ranking should reflect additional video-derived angles",
        errors,
    )
    return errors


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-enriched-integration-") as temp_dir:
            temp_root = Path(temp_dir)
            source_snapshots = temp_root / "source-snapshots.json"
            enriched_signal_items = temp_root / "signal-items.enriched.json"
            run_script(
                SOURCE_SNAPSHOTS_BUILDER,
                "--schema-version",
                "discovery-source-snapshots.v1",
                "--output",
                str(source_snapshots),
            )
            run_script(
                ENRICHED_SIGNAL_ITEMS_BUILDER,
                "--schema-version",
                "discovery-signal-items.v1",
                "--output",
                str(enriched_signal_items),
            )
            metadata_discovery, metadata_ranking = _run_lane(
                temp_root=temp_root,
                lane="metadata",
                signal_items=METADATA_SIGNAL_ITEMS,
                source_snapshots=source_snapshots,
            )
            enriched_discovery, enriched_ranking = _run_lane(
                temp_root=temp_root,
                lane="enriched",
                signal_items=enriched_signal_items,
                source_snapshots=source_snapshots,
            )
            errors = validate_outputs(
                enriched_signal_items=load_json(enriched_signal_items),
                metadata_discovery=metadata_discovery,
                enriched_discovery=enriched_discovery,
                metadata_ranking=metadata_ranking,
                enriched_ranking=enriched_ranking,
            )
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] enriched discovery/ranking integration failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Enriched discovery/ranking integration is aligned.")
    print("- enriched lane candidate count: 4")
    print("- metadata-only fallback count: 3")
    print("- ranking diff: video-derived angles affect rewrite score")
    return 0


if __name__ == "__main__":
    sys.exit(main())
