#!/usr/bin/env python3
"""
Smoke tests for ranking sample-output alignment helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestRankingOutputAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sync_script_produces_expected_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-sync-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-dry-run.sample.json"
            result = self.run_script(
                "skills/autotiktok-topic-ranking/scripts/dry_run_ranking.py",
                "--output",
                str(ranking_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(ranking_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["profileId"], "growth-default")
            self.assertEqual(payload["candidateSource"]["sourceKind"], "discovery_artifact")
            self.assertEqual(
                payload["predictionRun"]["candidateInputSchemaVersion"], "discovery-dry-run.v1"
            )

    def test_ranking_output_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_ranking_output_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ranking sample output is aligned", result.stdout)


if __name__ == "__main__":
    main()
