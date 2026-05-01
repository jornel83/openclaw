#!/usr/bin/env python3
"""
Smoke tests for the live-lane dependency inventory helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestLiveLaneDependencyInventory(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_inventory_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_live_lane_dependency_inventory.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Live-lane dependency inventory is consistent.", result.stdout)
        self.assertIn("- preview-first wrappers:", result.stdout)
        self.assertIn("- live-lane defaults:", result.stdout)

    def test_inventory_listing_has_expected_shape(self):
        result = self.run_script("skills/autotiktok/scripts/list_live_lane_dependencies.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schemaVersion"], "live-lane-dependency-inventory.v1")
        self.assertEqual(payload["scope"], "ranking-to-optimizer lane migration")
        self.assertGreaterEqual(len(payload["previewFirstWrappers"]), 3)
        self.assertGreaterEqual(len(payload["liveLaneDefaultDependencies"]), 8)


if __name__ == "__main__":
    main()
