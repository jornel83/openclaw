#!/usr/bin/env python3
"""
Refresh the committed discovery sample output from the current deterministic discovery runner.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)
DISCOVERY_SCRIPT = (
    ROOT / "skills" / "autotiktok-topic-discovery" / "scripts" / "discovery_dry_run.py"
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
        run_script(DISCOVERY_SCRIPT, "--output", str(DISCOVERY_OUTPUT))
        print(f"Wrote discovery sample output to {DISCOVERY_OUTPUT}")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
