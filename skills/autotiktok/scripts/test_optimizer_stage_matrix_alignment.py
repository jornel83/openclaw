#!/usr/bin/env python3
"""
Smoke tests for optimizer stage-matrix alignment helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerStageMatrixAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_optimizer_stage_matrix_runner_produces_expected_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-matrix-") as temp_dir:
            matrix_path = Path(temp_dir) / "optimizer-stage-matrix.sample.json"
            result = self.run_script(
                "skills/autotiktok/scripts/run_optimizer_stage_matrix.py",
                "--output",
                str(matrix_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(matrix_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-stage-matrix.v1")
            self.assertEqual(payload["generatedFrom"]["contextMatrixFixtureVersion"], "scoring-context-matrix.fixture.v1")
            self.assertEqual(payload["generatedFrom"]["optimizerPolicyVersion"], "optimizer-policy.v1")
            self.assertEqual(
                payload["generatedFrom"]["challengerSchemaVersion"],
                "challenger-observations.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["challengerInputKind"],
                "observations",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerContractId"],
                "ranking_optimizer_handoff",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerContractValidationMode"],
                "exact",
            )
            self.assertTrue(payload["generatedFrom"]["rankingOptimizerContractValidated"])
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "legacy_top_level",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerDeprecationPhase"],
                "dual_write_preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerCanonicalSurface"],
                "optimizerHandoff",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerNextHardFailContractVersion"],
                "ranking-optimizer-contract.v2",
            )
            self.assertFalse(payload["generatedFrom"]["rankingOptimizerCompatApplied"])
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerCompatAliasesApplied"],
                [],
            )
            self.assertEqual(len(payload["stages"]), 3)
            stages = {item["stageMode"]: item for item in payload["stages"]}
            self.assertEqual(stages["growth"]["profileId"], "growth-default")
            self.assertEqual(stages["scale"]["profileId"], "scale-default")
            self.assertEqual(stages["search_priority"]["profileId"], "search-priority-default")
            self.assertEqual(stages["growth"]["shadowLeaderProfileId"], "search-priority-default")
            self.assertEqual(stages["growth"]["recommendationKind"], "observe_challenger")
            self.assertEqual(stages["search_priority"]["shadowLeaderProfileId"], "scale-default")
            self.assertEqual(stages["search_priority"]["recommendationKind"], "keep_champion")

    def test_optimizer_stage_matrix_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_optimizer_stage_matrix_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Optimizer stage matrix is aligned", result.stdout)

    def test_optimizer_stage_matrix_supports_preview_exact_lane(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-matrix-preview-") as temp_dir:
            matrix_path = Path(temp_dir) / "optimizer-stage-matrix.preview.json"
            result = self.run_script(
                "skills/autotiktok/scripts/run_optimizer_stage_matrix.py",
                "--ranking-contract-version",
                "ranking-optimizer-contract.vNext-preview",
                "--ranking-contract-validation-mode",
                "exact",
                "--output",
                str(matrix_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(matrix_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.vNext-preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerContractValidationMode"],
                "exact",
            )
            self.assertEqual(
                payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "optimizer_handoff",
            )
            self.assertFalse(payload["generatedFrom"]["rankingOptimizerCompatApplied"])


if __name__ == "__main__":
    main()
