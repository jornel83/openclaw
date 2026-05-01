#!/usr/bin/env python3
"""
Smoke tests for workflow-summary sample alignment helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestWorkflowSummaryAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sync_script_produces_expected_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-workflow-summary-") as temp_dir:
            summary_path = Path(temp_dir) / "workflow-summary.sample.json"
            result = self.run_script(
                "skills/autotiktok/scripts/run_autotiktok_workflow.py",
                "--summary-output",
                str(summary_path),
                "--artifact-path-style",
                "basename",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "autotiktok-workflow-run.v1")
            self.assertEqual(payload["artifactPaths"]["discovery"], "discovery.json")
            self.assertEqual(payload["summary"]["candidateCount"], 3)
            self.assertEqual(payload["summary"]["candidateSourceKind"], "discovery_artifact")
            self.assertEqual(
                payload["generatedFrom"]["discoveryMaterializationSource"],
                "separate_snapshot_artifacts",
            )
            self.assertEqual(
                payload["generatedFrom"]["discoveryNormalizationRuleVersion"],
                "discovery-normalization.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["sourceSnapshotSchemaVersion"],
                "discovery-source-snapshots.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["signalItemsSchemaVersion"],
                "discovery-signal-items.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["videoSamplesSchemaVersion"],
                "discovery-video-samples.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["candidateSourceInputKind"],
                "snapshot_materialization",
            )
            self.assertEqual(
                payload["generatedFrom"]["candidateSourceMaterializationId"],
                "discovery-materialization.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["candidateSourceNormalizationRuleVersion"],
                "discovery-normalization.v1",
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

    def test_workflow_summary_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_workflow_summary_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Workflow summary sample is aligned", result.stdout)


if __name__ == "__main__":
    main()
