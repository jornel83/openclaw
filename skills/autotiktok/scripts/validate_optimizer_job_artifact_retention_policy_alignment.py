#!/usr/bin/env python3
"""
Validate committed optimizer job artifact retention policy against deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_RETENTION_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_artifact_retention_policy.py"
)
COMMITTED_RETENTION_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-artifact-retention-policy.sample.json"
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
            prefix="autotiktok-job-artifact-retention-policy-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            generated_path = temp_root / "optimizer-job-artifact-retention-policy.json"
            run_script(BUILD_RETENTION_POLICY_SCRIPT, "--output", str(generated_path))
            generated = load_json(generated_path)
            committed = load_json(COMMITTED_RETENTION_POLICY)
            if generated != committed:
                raise RuntimeError(
                    "committed optimizer job artifact retention policy does not match deterministic generation"
                )
            if generated["generatedFrom"]["artifactPolicyCount"] != 11:
                raise RuntimeError(
                    "optimizer job artifact retention policy should declare eleven artifact policy rows"
                )
            policy_rows = {
                entry["artifactKind"]: entry for entry in generated["artifactPolicies"]
            }
            if policy_rows["job_run"]["retentionTier"] != "operational":
                raise RuntimeError(
                    "job_run retention tier should remain operational"
                )
            if policy_rows["job_error"]["retentionTier"] != "failure_audit":
                raise RuntimeError(
                    "job_error retention tier should remain failure_audit"
                )
            if policy_rows["recent_failure_summaries"]["retentionTier"] != "failure_audit":
                raise RuntimeError(
                    "recent_failure_summaries retention tier should remain failure_audit"
                )
        print(
            "Optimizer job artifact retention policy is aligned with deterministic generation."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
