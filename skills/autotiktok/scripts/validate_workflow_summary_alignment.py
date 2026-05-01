#!/usr/bin/env python3
"""
Validate that the committed workflow summary sample matches current deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_autotiktok_workflow.py"
COMMITTED_SUMMARY = ROOT / "skills" / "autotiktok" / "fixtures" / "workflow-summary.sample.json"


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
        with tempfile.TemporaryDirectory(prefix="autotiktok-workflow-summary-") as temp_dir:
            summary_path = Path(temp_dir) / "workflow-summary.json"
            run_script(
                WORKFLOW_SCRIPT,
                "--summary-output",
                str(summary_path),
                "--artifact-path-style",
                "basename",
            )
            generated_summary = load_json(summary_path)
            committed_summary = load_json(COMMITTED_SUMMARY)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_summary != committed_summary:
        print("[ERROR] committed workflow-summary.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_workflow_summary_sample.py")
        return 1

    print("Workflow summary sample is aligned with current deterministic generation.")
    print(f"Workflow summary: {COMMITTED_SUMMARY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
