#!/usr/bin/env python3
"""
Refresh the committed discovery snapshot-materialization sample from the current
deterministic standalone snapshot inputs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-snapshot-materialization.sample.json"
)
BUILD_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "scripts"
    / "build_discovery_snapshot_materialization.py"
)


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
        run_script(BUILD_SCRIPT, "--output", str(OUTPUT))
        print(f"Wrote discovery snapshot materialization sample to {OUTPUT}")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
