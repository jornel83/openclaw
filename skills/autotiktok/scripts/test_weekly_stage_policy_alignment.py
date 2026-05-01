#!/usr/bin/env python3
"""
Smoke test for weekly stage policy fixture validation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestWeeklyStagePolicyAlignment(TestCase):
    def test_weekly_stage_policy_alignment_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_weekly_stage_policy_alignment.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Weekly stage policy fixtures", result.stdout)


if __name__ == "__main__":
    main()
