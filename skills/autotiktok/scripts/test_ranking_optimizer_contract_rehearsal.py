#!/usr/bin/env python3
"""
Smoke tests for the vNext ranking-to-optimizer contract rehearsal validator.
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


class TestRankingOptimizerContractRehearsal(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_rehearsal_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Ranking output satisfies the vNext preview optimizer-facing contract.",
            result.stdout,
        )
        self.assertIn("Validation mode: exact", result.stdout)

    def test_rehearsal_validator_accepts_legacy_aliases(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-rehearsal-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-legacy.json"
            payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
            payload.pop("optimizerHandoff", None)
            payload.pop("schemaVersion", None)
            payload["profileSelection"].pop("selectionSource", None)
            payload["candidateSource"].pop("topicCandidateSchemaVersion", None)
            payload["candidateSource"].pop("inputSchemaVersion", None)
            payload["candidateSource"].pop("sourceKind", None)
            payload["candidateSource"].pop("sourceSnapshotId", None)
            payload["candidateSource"].pop("sourcePolicyVersion", None)
            payload["candidateSource"].pop("rankingSnapshotId", None)
            ranking_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py",
                "--ranking-input",
                str(ranking_path),
                "--validation-mode",
                "compat",
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("vNext preview optimizer-facing contract", result.stdout)
            self.assertIn("Validation mode: compat", result.stdout)

    def test_rehearsal_validator_rejects_missing_stage_mode(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-rehearsal-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-bad.json"
            payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
            payload["profileSelection"].pop("stageMode", None)
            payload["optimizerHandoff"]["profileSelection"].pop("stageMode", None)
            ranking_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py",
                "--ranking-input",
                str(ranking_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("profileSelection.stageMode must be a non-empty string", result.stdout)

    def test_rehearsal_validator_rejects_missing_deprecation_policy(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-rehearsal-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-missing-policy.json"
            payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
            payload["optimizerHandoff"].pop("deprecationPolicy", None)
            ranking_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py",
                "--ranking-input",
                str(ranking_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("optimizerHandoff.deprecationPolicy must be an object", result.stdout)


if __name__ == "__main__":
    main()
