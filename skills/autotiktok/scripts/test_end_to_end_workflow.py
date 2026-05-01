#!/usr/bin/env python3
"""
Smoke test for the AutoTikTok end-to-end workflow runner.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestEndToEndWorkflow(TestCase):
    def test_workflow_runner_emits_expected_summary(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-workflow-") as temp_dir:
            artifacts_dir = Path(temp_dir) / "artifacts"
            summary_path = Path(temp_dir) / "summary.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "skills/autotiktok/scripts/run_autotiktok_workflow.py",
                    "--artifacts-dir",
                    str(artifacts_dir),
                    "--summary-output",
                    str(summary_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "autotiktok-workflow-run.v1")
            self.assertEqual(payload["summary"]["candidateCount"], 3)
            self.assertEqual(payload["summary"]["requestedProfileId"], "auto")
            self.assertEqual(payload["summary"]["resolvedProfileId"], "growth-default")
            self.assertEqual(payload["summary"]["profileSelectionSource"], "context_stage_mode")
            self.assertEqual(payload["summary"]["topTopicId"], "tp_evergreen_ad_mistakes_001")
            self.assertEqual(payload["summary"]["rankingSnapshotId"], "snap.autotiktok.workflow.fixture.2026-04-15")
            self.assertEqual(payload["summary"]["candidateSourceKind"], "discovery_artifact")
            self.assertEqual(payload["summary"]["candidateSourceSnapshotId"], "snap.discovery.fixture.2026-04-15")
            self.assertTrue(
                str(payload["artifactPaths"]["optimizerInputManifest"]).endswith(
                    "optimizer-input-manifest.json"
                )
            )
            self.assertTrue(
                str(payload["artifactPaths"]["optimizerInputBundle"]).endswith(
                    "optimizer-input-bundle.json"
                )
            )
            self.assertEqual(
                payload["summary"]["candidateSourcePolicyVersion"], "discovery-policy.v1"
            )
            self.assertEqual(
                payload["generatedFrom"]["candidateInputSchemaVersion"], "discovery-dry-run.v1"
            )
            self.assertEqual(
                payload["generatedFrom"]["discoveryInputKind"],
                "snapshot_materialization",
            )
            self.assertEqual(
                payload["generatedFrom"]["discoveryInputSchemaVersion"],
                "discovery-snapshot-materialization.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["discoveryNormalizationRuleVersion"],
                "discovery-normalization.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["discoveryMaterializationId"],
                "discovery-materialization.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["discoveryMaterializationSource"],
                "separate_snapshot_artifacts",
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
                payload["generatedFrom"]["optimizerInputManifestSchemaVersion"],
                "optimizer-input-manifest.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputManifestId"],
                "optimizer-input-manifest.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputBundleSchemaVersion"],
                "optimizer-input-bundle.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputBundleId"],
                "optimizer-input-bundle.autotiktok.fixture.2026-04-15",
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
            self.assertIn(payload["summary"]["weeklyDecision"], {"promote", "keep_champion"})

    def test_workflow_runner_supports_preview_exact_lane(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-workflow-preview-") as temp_dir:
            artifacts_dir = Path(temp_dir) / "artifacts"
            summary_path = Path(temp_dir) / "summary-preview.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "skills/autotiktok/scripts/run_autotiktok_workflow.py",
                    "--artifacts-dir",
                    str(artifacts_dir),
                    "--summary-output",
                    str(summary_path),
                    "--artifact-path-style",
                    "basename",
                    "--ranking-contract-version",
                    "ranking-optimizer-contract.vNext-preview",
                    "--ranking-contract-validation-mode",
                    "exact",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
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
