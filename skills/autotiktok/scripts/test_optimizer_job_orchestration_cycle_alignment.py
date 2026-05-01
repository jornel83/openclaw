#!/usr/bin/env python3
"""
Smoke test for optimizer job orchestration-cycle alignment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerJobOrchestrationCycleAlignment(TestCase):
    def test_orchestration_cycle_alignment_validator_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_optimizer_job_orchestration_cycle_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Optimizer job orchestration cycle fixture is aligned",
            result.stdout,
        )


if __name__ == "__main__":
    main()
