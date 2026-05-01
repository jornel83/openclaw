#!/usr/bin/env python3
"""
Smoke tests for discovery snapshot-materialization alignment helpers.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestDiscoverySnapshotMaterializationAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_snapshot_materialization_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_discovery_snapshot_materialization_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Discovery snapshot-materialization fixture is aligned",
            result.stdout,
        )


if __name__ == "__main__":
    main()
