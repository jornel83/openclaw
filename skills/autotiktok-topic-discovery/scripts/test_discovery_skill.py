#!/usr/bin/env python3
"""
Smoke tests for the AutoTikTok discovery skill.
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


class TestDiscoverySkill(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_raw_signal_fixture_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_raw_signals.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Raw-signal fixture is valid.", result.stdout)

    def test_snapshot_materialization_fixture_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_discovery_snapshot_materialization.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Snapshot-materialization fixture is valid.", result.stdout)

    def test_snapshot_materialization_builder_rebuilds_committed_fixture(self):
        committed_fixture = (
            SKILL_DIR / "fixtures" / "discovery-snapshot-materialization.sample.json"
        )
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-materialization-") as temp_dir:
            out_path = Path(temp_dir) / "discovery-snapshot-materialization.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_discovery_snapshot_materialization.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(out_path.read_text(encoding="utf-8")),
                json.loads(committed_fixture.read_text(encoding="utf-8")),
            )

    def test_discovery_dry_run_produces_expected_shape(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-") as temp_dir:
            out_path = Path(temp_dir) / "discovery.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/discovery_dry_run.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "discovery-dry-run.v1")
            self.assertEqual(payload["policyVersion"], "discovery-policy.v1")
            self.assertEqual(payload["generatedFrom"]["normalizationRuleVersion"], "discovery-normalization.v1")
            self.assertEqual(len(payload["evidenceBundles"]), 3)
            self.assertEqual(len(payload["mergeGroups"]), 3)
            self.assertEqual(len(payload["normalizedSignals"]), 6)
            self.assertEqual(len(payload["topicAbstractions"]), 3)
            self.assertEqual(len(payload["candidates"]), 3)
            self.assertEqual(
                payload["generatedFrom"]["inputKind"], "snapshot_materialization"
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
            self.assertEqual(
                payload["normalizedSignals"][0]["fingerprintSeed"],
                "evergreen.series.mistakes_ad_creative",
            )
            self.assertEqual(
                payload["topicAbstractions"][0]["titleSelectionSource"],
                "normalized_anchor_signal",
            )
            self.assertIn("anchorSignalId", payload["evidenceBundles"][0])
            self.assertIn("mergedSignalCount", payload["mergeGroups"][0])
            self.assertIn("topicAbstractionId", payload["evidenceBundles"][0])
            self.assertIn("normalizedTopicKey", payload["mergeGroups"][0])
            self.assertIn(
                "searchEvidenceSummary", payload["evidenceBundles"][0]
            )
            self.assertIn(
                "executionEvidenceSummary", payload["evidenceBundles"][0]
            )
            self.assertIn("dedupeDecision", payload["mergeGroups"][0])
            self.assertIn("mergeGuardrails", payload["mergeGroups"][0])
            self.assertIn("packagingReadiness", payload["mergeGroups"][0])
            self.assertIn(
                "coverageLabel", payload["candidates"][0]["searchEvidence"]
            )
            self.assertIn(
                "packagingRisk", payload["candidates"][0]["executionProfile"]
            )

    def test_discovery_output_passes_candidate_contract_check(self):
        fixture_path = SKILL_DIR / "fixtures" / "discovery-dry-run.sample.json"
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/check_topic_candidate_contract.py",
            "--input",
            str(fixture_path),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Topic-candidate contract is valid.", result.stdout)

    def test_discovery_dry_run_supports_legacy_raw_signal_input(self):
        raw_fixture = SKILL_DIR / "fixtures" / "raw-signals.sample.json"
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-legacy-") as temp_dir:
            out_path = Path(temp_dir) / "discovery.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/discovery_dry_run.py",
                "--signals",
                str(raw_fixture),
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["generatedFrom"]["inputKind"], "raw_signal_fixture")

    def test_discovery_dry_run_supports_standalone_snapshot_inputs(self):
        source_snapshots = SKILL_DIR / "fixtures" / "source-snapshots.sample.json"
        signal_items = SKILL_DIR / "fixtures" / "signal-items.sample.json"
        video_samples = SKILL_DIR / "fixtures" / "video-samples.sample.json"
        with tempfile.TemporaryDirectory(prefix="autotiktok-discovery-standalone-") as temp_dir:
            out_path = Path(temp_dir) / "discovery.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/discovery_dry_run.py",
                "--source-snapshots",
                str(source_snapshots),
                "--signal-items",
                str(signal_items),
                "--video-samples",
                str(video_samples),
                "--materialization-id",
                "discovery-materialization.autotiktok.fixture.2026-04-15",
                "--materialization-schema-version",
                "discovery-snapshot-materialization.sample.v1",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["materializationSource"],
                "separate_snapshot_artifacts",
            )
            self.assertEqual(
                payload["generatedFrom"]["materializationId"],
                "discovery-materialization.autotiktok.fixture.2026-04-15",
            )


if __name__ == "__main__":
    main()
