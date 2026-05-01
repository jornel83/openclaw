#!/usr/bin/env python3
"""
Validate that legacy scheduler-facing optimizer artifacts are explicitly marked as compatibility-only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
COMPATIBILITY_RUNTIME_ROLE = "compatibility_rehearsal"
PREFERRED_RECURRING_RUNTIME = "openclaw_cron"
INTENDED_USES = [
    "fixture_generation",
    "deterministic_rehearsal",
    "cutover_validation",
]
ARTIFACTS = {
    "optimizer-job-schedule": ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json",
    "optimizer-job-execution-context": ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-execution-context.sample.json",
    "optimizer-job-orchestration-cycle": ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-orchestration-cycle.sample.json",
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        for artifact_name, artifact_path in ARTIFACTS.items():
            payload = load_json(artifact_path)
            if payload.get("runtimeRole") != COMPATIBILITY_RUNTIME_ROLE:
                raise RuntimeError(
                    f"{artifact_name} must declare runtimeRole={COMPATIBILITY_RUNTIME_ROLE}"
                )
            if payload.get("preferredRecurringRuntime") != PREFERRED_RECURRING_RUNTIME:
                raise RuntimeError(
                    f"{artifact_name} must declare preferredRecurringRuntime={PREFERRED_RECURRING_RUNTIME}"
                )
            if payload.get("intendedUses") != INTENDED_USES:
                raise RuntimeError(
                    f"{artifact_name} must declare intendedUses={INTENDED_USES!r}"
                )
        print(
            "Legacy optimizer scheduler-facing artifacts are explicitly marked as compatibility-only rehearsal contracts."
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
