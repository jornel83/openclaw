#!/usr/bin/env python3
"""
Validate that the standalone discovery snapshot inputs still materialize the committed
snapshot-materialization and discovery sample artifacts.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_MATERIALIZATION_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "scripts"
    / "build_discovery_snapshot_materialization.py"
)
DISCOVERY_SCRIPT = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "scripts" / "discovery_dry_run.py"
)
SOURCE_SNAPSHOTS_FIXTURE = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "source-snapshots.sample.json"
)
SIGNAL_ITEMS_FIXTURE = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "signal-items.sample.json"
)
VIDEO_SAMPLES_FIXTURE = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "video-samples.sample.json"
)
COMMITTED_MATERIALIZATION = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-snapshot-materialization.sample.json"
)
COMMITTED_DISCOVERY = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)
MATERIALIZATION_ID = "discovery-materialization.autotiktok.fixture.2026-04-15"
MATERIALIZATION_SCHEMA_VERSION = "discovery-snapshot-materialization.sample.v1"


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


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-ingest-") as temp_dir:
            built_materialization = Path(temp_dir) / "discovery-snapshot-materialization.json"
            built_discovery = Path(temp_dir) / "discovery-dry-run.json"
            run_script(
                BUILD_MATERIALIZATION_SCRIPT,
                "--source-snapshots",
                str(SOURCE_SNAPSHOTS_FIXTURE),
                "--signal-items",
                str(SIGNAL_ITEMS_FIXTURE),
                "--video-samples",
                str(VIDEO_SAMPLES_FIXTURE),
                "--materialization-id",
                MATERIALIZATION_ID,
                "--schema-version",
                MATERIALIZATION_SCHEMA_VERSION,
                "--output",
                str(built_materialization),
            )
            run_script(
                DISCOVERY_SCRIPT,
                "--source-snapshots",
                str(SOURCE_SNAPSHOTS_FIXTURE),
                "--signal-items",
                str(SIGNAL_ITEMS_FIXTURE),
                "--video-samples",
                str(VIDEO_SAMPLES_FIXTURE),
                "--materialization-id",
                MATERIALIZATION_ID,
                "--materialization-schema-version",
                MATERIALIZATION_SCHEMA_VERSION,
                "--output",
                str(built_discovery),
            )
            generated_materialization = load_json(built_materialization)
            generated_discovery = load_json(built_discovery)
            committed_materialization = load_json(COMMITTED_MATERIALIZATION)
            committed_discovery = load_json(COMMITTED_DISCOVERY)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_materialization != committed_materialization:
        print("[ERROR] standalone snapshot inputs no longer match committed materialization")
        print(
            "Run: python3 skills/autotiktok/scripts/sync_discovery_snapshot_materialization_sample.py"
        )
        return 1
    if generated_discovery != committed_discovery:
        print("[ERROR] standalone snapshot ingest no longer matches committed discovery output")
        print("Run: python3 skills/autotiktok/scripts/sync_discovery_sample_output.py")
        return 1

    print("Discovery standalone snapshot ingest is aligned with committed materialization and discovery output.")
    print(f"Source snapshots: {SOURCE_SNAPSHOTS_FIXTURE}")
    print(f"Signal items: {SIGNAL_ITEMS_FIXTURE}")
    print(f"Video samples: {VIDEO_SAMPLES_FIXTURE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
