#!/usr/bin/env python3
"""
Smoke tests for the trending discovery adapter contract validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestTrendingDiscoveryAdapterContractAlignment(TestCase):
    def test_trending_discovery_adapter_contract_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_trending_discovery_adapter_contract_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Trending discovery adapter contract fixtures are aligned.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
