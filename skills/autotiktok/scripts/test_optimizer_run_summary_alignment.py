#!/usr/bin/env python3
"""
Smoke test for the optimizer run-summary alignment validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "validate_optimizer_run_summary_alignment.py"


class TestOptimizerRunSummaryAlignment(TestCase):
    def test_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Optimizer run summary fixture is aligned with deterministic generation.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
