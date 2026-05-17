#!/usr/bin/env python3
"""
Test AutoTikTok video-understanding routing guardrails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "skills" / "autotiktok" / "scripts" / "validate_video_understanding_routing_guardrails.py"


class TestVideoUnderstandingRoutingGuardrails(TestCase):
    def test_guardrails_are_valid(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertIn("Video understanding routing guardrails are valid.", result.stdout)


if __name__ == "__main__":
    main()
