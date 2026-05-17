#!/usr/bin/env python3
"""
Validate trending metadata bootstrap through discovery materialization and ranking.
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
TRENDING_INPUT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "trending-consolidated-hot.sample.json"
)
TRENDING_INPUT_BUILDER = DISCOVERY_SCRIPT_DIR / "build_discovery_inputs_from_trending.py"
MATERIALIZATION_BUILDER = DISCOVERY_SCRIPT_DIR / "build_discovery_snapshot_materialization.py"
DISCOVERY_RUNNER = DISCOVERY_SCRIPT_DIR / "discovery_dry_run.py"
RANKING_RUNNER = RANKING_SCRIPT_DIR / "dry_run_ranking.py"


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


def validate_outputs(temp_root: Path, errors: list[str]) -> None:
    source_snapshots = load_json(temp_root / "source-snapshots.from-trending.json")
    video_samples = load_json(temp_root / "video-samples.from-trending.json")
    signal_items = load_json(temp_root / "signal-items.from-trending.synthetic.json")
    materialization = load_json(temp_root / "materialization.json")
    discovery = load_json(temp_root / "discovery.json")
    ranking = load_json(temp_root / "ranking.json")

    expect(
        source_snapshots["snapshotId"] == video_samples["snapshotId"] == signal_items["snapshotId"],
        "generated discovery input snapshotIds must match",
        errors,
    )
    expect(
        len(video_samples["videoSamples"]) == len(signal_items["signalItems"]),
        "metadata bootstrap should produce one synthetic signal per normalized video sample",
        errors,
    )
    expect(
        materialization["generatedFrom"]["materializationSource"] == "separate_snapshot_artifacts",
        "materialization should preserve separate snapshot artifact provenance",
        errors,
    )
    expect(
        discovery["schemaVersion"] == "discovery-dry-run.v1",
        "discovery dry run should produce discovery-dry-run.v1",
        errors,
    )
    expect(
        discovery["generatedFrom"]["inputKind"] == "snapshot_materialization",
        "discovery should consume the trending materialization as snapshot_materialization",
        errors,
    )
    expect(
        len(discovery.get("candidates", [])) >= 1,
        "discovery should produce at least one candidate from trending metadata",
        errors,
    )
    expect(
        ranking["schemaVersion"] == "ranking-output.v1",
        "ranking should produce ranking-output.v1",
        errors,
    )
    expect(
        ranking["candidateSource"]["sourceKind"] == "discovery_artifact",
        "ranking should consume discovery output as a discovery_artifact",
        errors,
    )
    expect(
        ranking["candidateSource"]["sourceInputKind"] == "snapshot_materialization",
        "ranking candidate source should preserve snapshot_materialization input kind",
        errors,
    )
    expect(
        len(ranking.get("scores", [])) == len(discovery.get("candidates", [])),
        "ranking score count should match discovery candidate count",
        errors,
    )


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-trending-integration-") as temp_dir:
            temp_root = Path(temp_dir)
            run_script(
                TRENDING_INPUT_BUILDER,
                "--input",
                str(TRENDING_INPUT),
                "--output-dir",
                str(temp_root),
            )
            run_script(
                MATERIALIZATION_BUILDER,
                "--source-snapshots",
                str(temp_root / "source-snapshots.from-trending.json"),
                "--signal-items",
                str(temp_root / "signal-items.from-trending.synthetic.json"),
                "--video-samples",
                str(temp_root / "video-samples.from-trending.json"),
                "--materialization-id",
                "discovery-materialization.tiktok-trending.us.20260502t183100z",
                "--schema-version",
                "discovery-snapshot-materialization.v1",
                "--output",
                str(temp_root / "materialization.json"),
            )
            run_script(
                DISCOVERY_RUNNER,
                "--input",
                str(temp_root / "materialization.json"),
                "--output",
                str(temp_root / "discovery.json"),
            )
            run_script(
                RANKING_RUNNER,
                "--candidates",
                str(temp_root / "discovery.json"),
                "--snapshot-id",
                "snap.autotiktok.trending.20260502t183100z",
                "--run-id",
                "run.autotiktok.trending.20260502t183100z",
                "--created-at",
                "2026-05-02T18:31:00Z",
                "--output",
                str(temp_root / "ranking.json"),
            )
            errors: list[str] = []
            validate_outputs(temp_root, errors)
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        print("[ERROR] trending discovery/ranking integration failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Trending discovery/ranking integration is aligned.")
    print(f"Input builder: {TRENDING_INPUT_BUILDER.relative_to(ROOT)}")
    print(f"Trending input fixture: {TRENDING_INPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
