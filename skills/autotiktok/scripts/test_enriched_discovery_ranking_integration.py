#!/usr/bin/env python3
"""
Smoke test for enriched signalItems through discovery and ranking.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestEnrichedDiscoveryRankingIntegration(TestCase):
    def test_enriched_discovery_ranking_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_enriched_discovery_ranking_integration.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Enriched discovery/ranking integration is aligned.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
