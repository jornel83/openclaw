#!/usr/bin/env python3
"""
Refresh all committed AutoTikTok mock artifacts in dependency order.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SYNC_SCRIPTS = [
    "skills/autotiktok/scripts/sync_discovery_snapshot_materialization_sample.py",
    "skills/autotiktok/scripts/sync_discovery_sample_output.py",
    "skills/autotiktok/scripts/sync_shared_candidates_fixture.py",
    "skills/autotiktok/scripts/sync_ranking_sample_output.py",
    "skills/autotiktok/scripts/sync_ranking_profile_matrix.py",
    "skills/autotiktok/scripts/sync_optimizer_sample_outputs.py",
    "skills/autotiktok/scripts/sync_optimizer_stage_matrix.py",
    "skills/autotiktok/scripts/sync_workflow_summary_sample.py",
]


def run_script(script: str) -> None:
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> int:
    try:
        for script in SYNC_SCRIPTS:
            run_script(script)
        print("Refreshed all AutoTikTok mock artifacts in dependency order.")
        for script in SYNC_SCRIPTS:
            print(f"- {script}")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
