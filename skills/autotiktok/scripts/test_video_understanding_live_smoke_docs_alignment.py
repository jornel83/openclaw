#!/usr/bin/env python3
"""
Smoke test for video understanding live-ish smoke docs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestVideoUnderstandingLiveSmokeDocsAlignment(TestCase):
    def test_video_understanding_live_smoke_docs_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_video_understanding_live_smoke_docs_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Video understanding live-ish smoke docs are aligned.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
