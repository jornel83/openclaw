#!/usr/bin/env python3
"""
Smoke test for the optimizer recent compare summaries alignment validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok"
    / "scripts"
    / "validate_optimizer_recent_compare_summaries_alignment.py"
)


class TestOptimizerRecentCompareSummariesAlignment(TestCase):
    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Optimizer recent compare summaries fixture is aligned",
            result.stdout,
        )


if __name__ == "__main__":
    main()
