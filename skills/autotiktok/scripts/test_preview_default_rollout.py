#!/usr/bin/env python3
"""
Smoke test for the preview-default rollout validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestPreviewDefaultRollout(TestCase):
    def test_preview_default_rollout_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_preview_default_rollout.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Preview-default wrappers now default to the preview canonical lane.",
            result.stdout,
        )
        self.assertIn("run_preview_optimizer_stage_matrix.py defaults", result.stdout)
        self.assertIn("run_preview_autotiktok_workflow.py defaults", result.stdout)
        self.assertIn("run_preview_daily_review.py defaults", result.stdout)
        self.assertIn("--use-current-lane fallback", result.stdout)


if __name__ == "__main__":
    main()
