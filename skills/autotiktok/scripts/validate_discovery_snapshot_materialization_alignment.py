#!/usr/bin/env python3
"""
Validate that the committed discovery snapshot-materialization fixture still drives the
current deterministic discovery sample output.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_SCRIPT = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "scripts" / "discovery_dry_run.py"
)
SNAPSHOT_VALIDATOR = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "scripts"
    / "validate_discovery_snapshot_materialization.py"
)
SNAPSHOT_FIXTURE = (
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
        run_script(SNAPSHOT_VALIDATOR, "--input", str(SNAPSHOT_FIXTURE))
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-snapshot-") as temp_dir:
            discovery_path = Path(temp_dir) / "discovery.json"
            run_script(
                DISCOVERY_SCRIPT,
                "--input",
                str(SNAPSHOT_FIXTURE),
                "--output",
                str(discovery_path),
            )
            generated_discovery = load_json(discovery_path)
            committed_discovery = load_json(COMMITTED_DISCOVERY)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_discovery != committed_discovery:
        print("[ERROR] snapshot-materialization fixture no longer matches committed discovery output")
        print("Run: python3 skills/autotiktok/scripts/sync_discovery_sample_output.py")
        return 1

    print("Discovery snapshot-materialization fixture is aligned with committed discovery output.")
    print(f"Snapshot fixture: {SNAPSHOT_FIXTURE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
