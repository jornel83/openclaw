#!/usr/bin/env python3
"""
Refresh the committed ranking sample output from the current deterministic ranking runner.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RANKING_OUTPUT = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
RANKING_SCRIPT = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "scripts" / "dry_run_ranking.py"
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
        run_script(RANKING_SCRIPT, "--output", str(RANKING_OUTPUT))
        print(f"Wrote ranking sample output to {RANKING_OUTPUT}")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
