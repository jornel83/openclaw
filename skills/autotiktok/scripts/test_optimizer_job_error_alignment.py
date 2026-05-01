#!/usr/bin/env python3
"""
Smoke test for the optimizer job-error alignment validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "validate_optimizer_job_error_alignment.py"


class TestOptimizerJobErrorAlignment(TestCase):
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
            "Optimizer job error fixture is aligned with deterministic generation.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
