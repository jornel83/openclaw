#!/usr/bin/env python3
"""
Refresh the committed workflow-summary sample from the current deterministic workflow runner.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SUMMARY_OUTPUT = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "workflow-summary.sample.json"
)
WORKFLOW_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_autotiktok_workflow.py"


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
        run_script(
            WORKFLOW_SCRIPT,
            "--summary-output",
            str(SUMMARY_OUTPUT),
            "--artifact-path-style",
            "basename",
        )
        print(f"Wrote workflow summary sample to {SUMMARY_OUTPUT}")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
