#!/usr/bin/env python3
"""
Smoke tests for the AutoTikTok ranking skill.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROOT = SKILL_DIR.parents[1]


class TestRankingSkill(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_ranking_fixture_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-ranking/scripts/validate_ranking_fixtures.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ranking fixtures are valid.", result.stdout)
        self.assertIn("Context matrix fixture:", result.stdout)
        self.assertIn("Feature rubric:", result.stdout)

    def test_dry_run_outputs_prediction_run_and_scores(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-") as temp_dir:
            out_path = Path(temp_dir) / "ranking.json"
            result = self.run_script(
                "skills/autotiktok-topic-ranking/scripts/dry_run_ranking.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["profileId"], "growth-default")
            self.assertEqual(payload["schemaVersion"], "ranking-output.v1")
            self.assertEqual(payload["profileSelection"]["resolvedProfileId"], "growth-default")
            self.assertEqual(payload["profileSelection"]["selectionSource"], "context_stage_mode")
            self.assertEqual(payload["candidateSource"]["sourceKind"], "discovery_artifact")
            self.assertEqual(
                payload["candidateSource"]["sourceSnapshotId"], "snap.discovery.fixture.2026-04-15"
            )
            self.assertEqual(
                payload["candidateSource"]["sourcePolicyVersion"], "discovery-policy.v1"
            )
            self.assertEqual(
                payload["candidateSource"]["sourceInputKind"], "snapshot_materialization"
            )
            self.assertEqual(
                payload["candidateSource"]["sourceMaterializationId"],
                "discovery-materialization.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["candidateSource"]["sourceNormalizationRuleVersion"],
                "discovery-normalization.v1",
            )
            self.assertEqual(payload["predictionRun"]["schemaVersion"], "prediction-run.v1")
            self.assertEqual(payload["predictionRun"]["scoringCodeVersion"], "dry-run-ranking.v2")
            self.assertEqual(payload["predictionRun"]["profileSelectionSource"], "context_stage_mode")
            self.assertEqual(
                payload["predictionRun"]["candidateInputSchemaVersion"], "discovery-dry-run.v1"
            )
            self.assertEqual(
                payload["predictionRun"]["candidateSourceKind"], "discovery_artifact"
            )
            self.assertEqual(
                payload["predictionRun"]["candidateSourceInputKind"],
                "snapshot_materialization",
            )
            self.assertEqual(
                payload["predictionRun"]["candidateSourceMaterializationId"],
                "discovery-materialization.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["predictionRun"]["candidateSourceNormalizationRuleVersion"],
                "discovery-normalization.v1",
            )
            self.assertEqual(len(payload["scores"]), 3)
            self.assertEqual(payload["rankingSummary"]["topTopicId"], "tp_evergreen_ad_mistakes_001")
            self.assertIn("featureVector", payload["scores"][0])
            self.assertIn("rerankDiagnostics", payload)
            self.assertEqual(
                payload["optimizerHandoff"]["schemaVersion"],
                "ranking-optimizer-handoff.v2-preview",
            )
            self.assertEqual(
                payload["optimizerHandoff"]["deprecatedTopLevelFields"],
                [
                    "profileId",
                    "profileSelection",
                    "candidateSource",
                    "scores",
                    "predictionRun",
                    "rankingSummary",
                    "rerankDiagnostics",
                ],
            )
            self.assertEqual(
                payload["optimizerHandoff"]["deprecationPolicy"],
                {
                    "schemaVersion": "ranking-optimizer-deprecation-policy.v1",
                    "phase": "dual_write_preview",
                    "canonicalSurface": "optimizerHandoff",
                    "deprecatedTopLevelFields": [
                        "profileId",
                        "profileSelection",
                        "candidateSource",
                        "scores",
                        "predictionRun",
                        "rankingSummary",
                        "rerankDiagnostics",
                    ],
                    "exactPreviewRequiresTopLevelMirror": True,
                    "compatPreviewUsesLegacyFallback": True,
                    "nextHardFailContractVersion": "ranking-optimizer-contract.v2",
                },
            )
            self.assertEqual(payload["optimizerHandoff"]["profileId"], payload["profileId"])
            self.assertEqual(
                payload["optimizerHandoff"]["profileSelection"],
                payload["profileSelection"],
            )
            self.assertEqual(
                payload["optimizerHandoff"]["candidateSource"],
                payload["candidateSource"],
            )
            self.assertEqual(payload["optimizerHandoff"]["scores"], payload["scores"])
            self.assertEqual(
                payload["optimizerHandoff"]["predictionRun"],
                payload["predictionRun"],
            )
            self.assertEqual(
                payload["optimizerHandoff"]["rankingSummary"],
                payload["rankingSummary"],
            )
            self.assertEqual(
                payload["optimizerHandoff"]["rerankDiagnostics"],
                payload["rerankDiagnostics"],
            )
            self.assertEqual(payload["rankingSummary"]["rejectedTopicIds"], ["tp_trend_wired_earbuds_001"])
            self.assertTrue(payload["scores"][-1]["isRejected"])
            self.assertIn("below_reject_threshold", payload["scores"][-1]["rerankReasons"])

    def test_profile_matrix_uses_context_matrix_fixture(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-matrix-") as temp_dir:
            out_path = Path(temp_dir) / "matrix.json"
            result = self.run_script(
                "skills/autotiktok-topic-ranking/scripts/ranking_profile_matrix.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "ranking-profile-matrix.v1")
            self.assertEqual(
                payload["generatedFrom"]["contextMatrixFixtureVersion"],
                "scoring-context-matrix.fixture.v1",
            )
            stages = {item["stageMode"]: item for item in payload["stages"]}
            self.assertEqual(stages["growth"]["profileId"], "growth-default")
            self.assertEqual(stages["scale"]["profileId"], "scale-default")
            self.assertEqual(stages["search_priority"]["profileId"], "search-priority-default")

    def test_ranking_report_builder_outputs_score_table(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-report-") as temp_dir:
            out_path = Path(temp_dir) / "report.md"
            result = self.run_script(
                "skills/autotiktok-topic-ranking/scripts/build_ranking_report.py",
                "--top",
                "2",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = out_path.read_text(encoding="utf-8")
            self.assertIn("| 排名 | Topic | 视频文件 | ScoreTotal |", report)
            self.assertIn("3 ad creative mistakes that kill watch time", report)


if __name__ == "__main__":
    main()
