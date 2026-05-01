#!/usr/bin/env python3
"""
Smoke tests for optimizer sample-output alignment helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestOptimizerOutputAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sync_script_produces_expected_shapes(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-sync-") as temp_dir:
            temp_root = Path(temp_dir)
            daily_path = temp_root / "daily-review.sample.json"
            weekly_path = temp_root / "weekly-promotion.sample.json"

            daily = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--output",
                str(daily_path),
            )
            self.assertEqual(daily.returncode, 0, daily.stderr)
            weekly = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--daily-review-input",
                str(daily_path),
                "--output",
                str(weekly_path),
            )
            self.assertEqual(weekly.returncode, 0, weekly.stderr)
            daily_payload = json.loads(daily_path.read_text(encoding="utf-8"))
            weekly_payload = json.loads(weekly_path.read_text(encoding="utf-8"))
            self.assertEqual(daily_payload["schemaVersion"], "daily-review-report.v1")
            self.assertIn("generatedFrom", daily_payload)
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingSchemaVersion"],
                "ranking-output.v1",
            )
            self.assertEqual(daily_payload["candidateSource"]["sourceKind"], "discovery_artifact")
            self.assertEqual(daily_payload["generatedFrom"]["rankingRequestedProfileId"], "auto")
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingProfileSelectionSource"],
                "context_stage_mode",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingCandidateSourceKind"],
                "discovery_artifact",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractId"],
                "ranking_optimizer_handoff",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.v1",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractValidationMode"],
                "exact",
            )
            self.assertTrue(
                daily_payload["generatedFrom"]["rankingOptimizerContractValidated"]
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "legacy_top_level",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerDeprecationPhase"],
                "dual_write_preview",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerCanonicalSurface"],
                "optimizerHandoff",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerNextHardFailContractVersion"],
                "ranking-optimizer-contract.v2",
            )
            self.assertFalse(
                daily_payload["generatedFrom"]["rankingOptimizerCompatApplied"]
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerCompatAliasesApplied"],
                [],
            )
            self.assertEqual(weekly_payload["schemaVersion"], "weekly-promotion-decision.v1")
            self.assertIn("generatedFrom", weekly_payload)
            self.assertEqual(
                weekly_payload["championCandidateSource"]["sourceKind"],
                "discovery_artifact",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewResolvedProfileId"],
                "growth-default",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerContractId"],
                "ranking_optimizer_handoff",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerContractVersion"],
                "ranking-optimizer-contract.v1",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"][
                    "dailyReviewRankingOptimizerContractValidationMode"
                ],
                "exact",
            )
            self.assertTrue(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerContractValidated"]
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerSurfaceSource"],
                "legacy_top_level",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerDeprecationPhase"],
                "dual_write_preview",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerCanonicalSurface"],
                "optimizerHandoff",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"][
                    "dailyReviewRankingOptimizerNextHardFailContractVersion"
                ],
                "ranking-optimizer-contract.v2",
            )
            self.assertFalse(
                weekly_payload["generatedFrom"]["dailyReviewRankingOptimizerCompatApplied"]
            )
            self.assertEqual(
                weekly_payload["generatedFrom"][
                    "dailyReviewRankingOptimizerCompatAliasesApplied"
                ],
                [],
            )

    def test_optimizer_output_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_optimizer_output_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Optimizer sample outputs are aligned", result.stdout)


if __name__ == "__main__":
    main()
