#!/usr/bin/env python3
"""
Smoke tests for the ranking-to-optimizer contract validator.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]
RANKING_SAMPLE = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)


class TestRankingOptimizerContract(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_ranking_optimizer_contract_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_ranking_optimizer_contract.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Ranking output satisfies the optimizer-facing contract.",
            result.stdout,
        )

    def test_ranking_optimizer_contract_validator_rejects_mismatched_candidate_count(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-contract-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-bad.json"
            payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
            payload["predictionRun"]["candidateCount"] = payload["predictionRun"]["candidateCount"] + 1
            ranking_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok/scripts/validate_ranking_optimizer_contract.py",
                "--ranking-input",
                str(ranking_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "candidateCount must match len(scores)",
                result.stdout,
            )
            self.assertNotIn(
                "schemaVersion must be ranking-output.v1",
                result.stdout,
            )


if __name__ == "__main__":
    main()
