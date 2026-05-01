#!/usr/bin/env python3
"""
Smoke test for the preview lane consumer cutover audit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestPreviewLaneConsumerCutover(TestCase):
    def test_preview_lane_consumer_cutover_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_preview_lane_consumer_cutover.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Preview consumer cutover audit confirms downstream preview lanes read optimizerHandoff.",
            result.stdout,
        )
        self.assertIn("stage entry preview lane ignores corrupted top-level", result.stdout)
        self.assertIn("workflow summary preview lane ignores corrupted top-level", result.stdout)


if __name__ == "__main__":
    main()
