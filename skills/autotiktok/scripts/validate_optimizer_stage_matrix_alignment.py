#!/usr/bin/env python3
"""
Validate that the committed optimizer stage-matrix sample matches current deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MATRIX_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_optimizer_stage_matrix.py"
COMMITTED_MATRIX = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "optimizer-stage-matrix.sample.json"
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
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-matrix-") as temp_dir:
            matrix_path = Path(temp_dir) / "optimizer-stage-matrix.json"
            run_script(MATRIX_SCRIPT, "--output", str(matrix_path))
            generated_matrix = load_json(matrix_path)
            committed_matrix = load_json(COMMITTED_MATRIX)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_matrix != committed_matrix:
        print("[ERROR] committed optimizer-stage-matrix.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_stage_matrix.py")
        return 1

    print("Optimizer stage matrix is aligned with current deterministic generation.")
    print(f"Optimizer matrix: {COMMITTED_MATRIX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
