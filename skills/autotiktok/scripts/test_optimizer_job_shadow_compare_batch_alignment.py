#!/usr/bin/env python3
"""
Smoke test for optimizer job shadow-compare batch alignment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerJobShadowCompareBatchAlignment(TestCase):
    def test_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_batch_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Optimizer job shadow compare batch artifacts are aligned",
            result.stdout,
        )


if __name__ == "__main__":
    main()
