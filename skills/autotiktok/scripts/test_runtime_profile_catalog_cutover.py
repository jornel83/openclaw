#!/usr/bin/env python3
"""
Smoke test for the runtime profile catalog cutover rehearsal validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestRuntimeProfileCatalogCutover(TestCase):
    def test_runtime_profile_catalog_cutover_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_runtime_profile_catalog_cutover.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Runtime profile catalog cutover rehearsal preserves optimizer semantics.",
            result.stdout,
        )
        self.assertIn(
            "preview catalog lane resolves legacy requested ids through preview aliases",
            result.stdout,
        )


if __name__ == "__main__":
    main()
