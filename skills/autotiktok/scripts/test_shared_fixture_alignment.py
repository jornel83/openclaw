#!/usr/bin/env python3
"""
Smoke test for shared fixture alignment between discovery and ranking.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestSharedFixtureAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sync_script_matches_shared_fixture_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-shared-fixture-") as temp_dir:
            out_path = Path(temp_dir) / "topic-candidates.json"
            result = self.run_script(
                "skills/autotiktok/scripts/sync_shared_candidates_fixture.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["fixtureSetVersion"], "topic-candidates.fixture.v1")
            self.assertIn("generatedFrom", payload)
            self.assertEqual(len(payload["candidates"]), 3)

    def test_shared_fixture_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_shared_fixture_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Shared topic-candidates fixture is aligned", result.stdout)


if __name__ == "__main__":
    main()
