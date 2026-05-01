#!/usr/bin/env python3
"""
Refresh the committed optimizer stage-matrix sample from the current deterministic runner.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MATRIX_OUTPUT = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "optimizer-stage-matrix.sample.json"
)
MATRIX_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_optimizer_stage_matrix.py"


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
        run_script(MATRIX_SCRIPT, "--output", str(MATRIX_OUTPUT))
        print(f"Wrote optimizer stage matrix to {MATRIX_OUTPUT}")
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
