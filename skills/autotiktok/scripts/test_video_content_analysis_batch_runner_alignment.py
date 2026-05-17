#!/usr/bin/env python3
"""
Smoke tests for the video-content analysis batch runner validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestVideoContentAnalysisBatchRunnerAlignment(TestCase):
    def test_video_content_analysis_batch_runner_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_video_content_analysis_batch_runner_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Video content analysis batch runner is aligned.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
