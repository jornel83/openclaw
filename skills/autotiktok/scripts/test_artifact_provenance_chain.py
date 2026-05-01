#!/usr/bin/env python3
"""
Smoke test for the AutoTikTok cross-artifact provenance validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestArtifactProvenanceChain(TestCase):
    def test_provenance_chain_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "skills/autotiktok/scripts/validate_artifact_provenance_chain.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AutoTikTok artifact provenance chain is consistent.", result.stdout)
        self.assertIn("ranking profile matrix", result.stdout)
        self.assertIn("optimizer stage matrix", result.stdout)


if __name__ == "__main__":
    main()
