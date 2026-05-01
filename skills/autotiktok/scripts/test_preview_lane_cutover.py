#!/usr/bin/env python3
"""
Smoke test for the preview lane cutover rehearsal validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestPreviewLaneCutover(TestCase):
    def test_preview_lane_cutover_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_preview_lane_cutover.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Preview lane cutover rehearsal preserves current optimizer semantics.",
            result.stdout,
        )
        self.assertIn("stage matrix: current lane vs vNext-preview/exact", result.stdout)
        self.assertIn("workflow summary: current lane vs vNext-preview/exact", result.stdout)


if __name__ == "__main__":
    main()
