#!/usr/bin/env python3
"""
Smoke test for weekly strategy realism validation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestWeeklyStrategyRealism(TestCase):
    def test_weekly_strategy_realism_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_weekly_strategy_realism.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Weekly strategy realism fixtures", result.stdout)


if __name__ == "__main__":
    main()
