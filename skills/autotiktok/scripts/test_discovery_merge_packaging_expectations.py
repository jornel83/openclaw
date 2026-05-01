#!/usr/bin/env python3
"""
Smoke tests for discovery merge/dedupe/packaging expectation checks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestDiscoveryMergePackagingExpectations(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_merge_packaging_expectations_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_discovery_merge_packaging_expectations.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Discovery merge-packaging expectations are satisfied.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
