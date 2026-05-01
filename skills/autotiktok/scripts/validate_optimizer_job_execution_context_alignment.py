#!/usr/bin/env python3
"""
Validate committed optimizer job execution-context artifact against deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_JOB_EXECUTION_CONTEXT_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_execution_context.py"
)
COMMITTED_JOB_EXECUTION_CONTEXT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-execution-context.sample.json"
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-job-execution-context-alignment-"
        ) as temp_dir:
            generated_path = Path(temp_dir) / "optimizer-job-execution-context.json"
            run_script(
                BUILD_JOB_EXECUTION_CONTEXT_SCRIPT,
                "--output",
                str(generated_path),
            )
            if load_json(generated_path) != load_json(COMMITTED_JOB_EXECUTION_CONTEXT):
                raise RuntimeError(
                    "committed optimizer job execution context does not match deterministic generation"
                )
        print(
            "Optimizer job execution context fixture is aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
