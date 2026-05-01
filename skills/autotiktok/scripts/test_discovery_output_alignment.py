#!/usr/bin/env python3
"""
Smoke tests for discovery sample-output alignment helpers.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestDiscoveryOutputAlignment(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sync_script_produces_expected_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-sync-") as temp_dir:
            discovery_path = Path(temp_dir) / "discovery-dry-run.sample.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/discovery_dry_run.py",
                "--output",
                str(discovery_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(discovery_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "discovery-dry-run.v1")
            self.assertEqual(payload["policyVersion"], "discovery-policy.v1")
            self.assertEqual(payload["snapshotId"], "snap.discovery.fixture.2026-04-15")
            self.assertEqual(
                payload["generatedFrom"]["inputKind"], "snapshot_materialization"
            )
            self.assertEqual(
                payload["generatedFrom"]["normalizationRuleVersion"],
                "discovery-normalization.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["inputSchemaVersion"],
                "discovery-snapshot-materialization.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["materializationSource"],
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
            self.assertEqual(len(payload["normalizedSignals"]), 6)
            self.assertEqual(len(payload["topicAbstractions"]), 3)
            self.assertEqual(len(payload["candidates"]), 3)
            self.assertIn(
                "searchEvidenceSummary", payload["evidenceBundles"][0]
            )
            self.assertIn("dedupeDecision", payload["mergeGroups"][0])
            self.assertIn(
                "packagingRisk", payload["candidates"][0]["executionProfile"]
            )

    def test_discovery_output_alignment_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_discovery_output_alignment.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Discovery sample output is aligned", result.stdout)


if __name__ == "__main__":
    main()
