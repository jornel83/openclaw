#!/usr/bin/env python3
"""
Smoke tests for ranking profile-matrix alignment helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestRankingProfileMatrixAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_matrix_runner_produces_expected_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-matrix-") as temp_dir:
            matrix_path = Path(temp_dir) / "ranking-profile-matrix.sample.json"
            result = self.run_script(
                "skills/autotiktok-topic-ranking/scripts/ranking_profile_matrix.py",
                "--output",
                str(matrix_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(matrix_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "ranking-profile-matrix.v1")
            self.assertEqual(payload["generatedFrom"]["candidateSourceKind"], "discovery_artifact")
            self.assertEqual(len(payload["stages"]), 3)
            stages = {item["stageMode"]: item for item in payload["stages"]}
            self.assertEqual(stages["growth"]["profileId"], "growth-default")
            self.assertEqual(stages["scale"]["profileId"], "scale-default")
            self.assertEqual(stages["search_priority"]["profileId"], "search-priority-default")
            self.assertEqual(stages["growth"]["scores"][1]["priorityLevel"], "P2")
            self.assertEqual(stages["scale"]["scores"][1]["priorityLevel"], "P1")
            self.assertEqual(stages["search_priority"]["scores"][1]["priorityLevel"], "P1")

    def test_ranking_profile_matrix_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_ranking_profile_matrix_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ranking profile matrix is aligned", result.stdout)


if __name__ == "__main__":
    main()
