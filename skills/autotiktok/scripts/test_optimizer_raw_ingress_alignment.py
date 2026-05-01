#!/usr/bin/env python3
"""
Smoke test for raw optimizer ingress alignment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerRawIngressAlignment(TestCase):
    def test_raw_ingress_alignment_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_optimizer_raw_ingress_alignment.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Validated optimizer raw ingress alignment",
            result.stdout,
        )


if __name__ == "__main__":
    main()
