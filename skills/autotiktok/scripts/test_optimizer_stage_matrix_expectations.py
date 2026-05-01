#!/usr/bin/env python3
"""
Smoke test for the optimizer stage-matrix expectations validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerStageMatrixExpectations(TestCase):
    def test_optimizer_stage_matrix_expectations_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_optimizer_stage_matrix_expectations.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Optimizer stage matrix satisfies intended stage-mode expectations.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
