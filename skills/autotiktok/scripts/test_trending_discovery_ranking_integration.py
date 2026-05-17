#!/usr/bin/env python3
"""
Smoke test for trending metadata bootstrap through discovery and ranking.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestTrendingDiscoveryRankingIntegration(TestCase):
    def test_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_trending_discovery_ranking_integration.py",
            ],
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
        self.assertIn("Trending discovery/ranking integration is aligned.", result.stdout)
        self.assertIn("build_discovery_inputs_from_trending.py", result.stdout)


if __name__ == "__main__":
    main()
