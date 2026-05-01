#!/usr/bin/env python3
"""
Smoke test for the ranking profile-matrix expectation validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestRankingProfileMatrixExpectations(TestCase):
    def test_ranking_profile_matrix_expectations_pass(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_ranking_profile_matrix_expectations.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Ranking profile matrix satisfies intended stage-mode expectations.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
