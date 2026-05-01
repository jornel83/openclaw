#!/usr/bin/env python3
"""
Smoke test for optimizer raw-shadow input alignment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerShadowInputAlignment(TestCase):
    def test_shadow_input_alignment_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_optimizer_shadow_input_alignment.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Canonical and raw-shadow manifests normalize to the same runtime optimizer inputs.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
