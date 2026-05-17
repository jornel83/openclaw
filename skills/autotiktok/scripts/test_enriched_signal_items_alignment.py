#!/usr/bin/env python3
"""
Smoke tests for enriched signalItems validation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestEnrichedSignalItemsAlignment(TestCase):
    def test_enriched_signal_items_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_enriched_signal_items_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Enriched signalItems fixture is aligned.", result.stdout)


if __name__ == "__main__":
    main()
