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

    def test_trending_adapter_contract_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_trending_discovery_adapter_contract.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Trending discovery adapter contract is valid.", result.stdout)
        self.assertIn("already canonical", result.stdout)
        self.assertIn("requires normalization", result.stdout)

    def test_video_content_analysis_contract_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_contract.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Video content analysis contract is valid.", result.stdout)
        self.assertIn("google/gemini-3-flash-preview", result.stdout)

    def test_video_content_analysis_batch_runner_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_batch_runner.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Video content analysis batch runner is valid.", result.stdout)
        self.assertIn("analysis_failed", result.stdout)

    def test_video_content_analysis_batch_runner_passes(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-video-content-analysis-") as temp_dir:
            out_path = Path(temp_dir) / "video-content-analysis.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/run_video_content_analysis_batch.py",
                "--use-default-response-fixture",
                "--schema-version",
                "discovery-video-content-analysis.sample.v1",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "discovery-video-content-analysis.sample.v1",
            )
            self.assertEqual(payload["summary"]["requested"], 4)
            self.assertEqual(payload["summary"]["analysisSucceeded"], 1)
            self.assertEqual(payload["summary"]["fallbackToMetadataOnly"], 3)
            self.assertEqual(
                payload["analyses"][0]["provenance"]["rawOutputSource"],
                "response_fixture",
            )

    def test_enriched_signal_items_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_enriched_signal_items.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Enriched signalItems are valid.", result.stdout)
        self.assertIn("metadata_only_fallback", result.stdout)

    def test_enriched_signal_items_builder_passes(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-enriched-signal-items-") as temp_dir:
            out_path = Path(temp_dir) / "signal-items.enriched.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_enriched_signal_items.py",
                "--schema-version",
                "discovery-signal-items.sample.v1",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["enriched"], 1)
            self.assertEqual(payload["summary"]["metadataOnlyFallback"], 3)
            self.assertEqual(
                payload["signalItems"][0]["rawMeta"]["enrichmentLane"],
                "video_content_analysis",
            )

    def test_video_download_manifest_adapter_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-topic-discovery/scripts/validate_video_download_manifest_adapter.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Video download manifest adapter is valid.", result.stdout)
        self.assertIn("download_missing", result.stdout)
        self.assertIn("invalid_file", result.stdout)

    def test_video_download_manifest_builder_passes(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-video-download-manifest-"
        ) as temp_dir:
            out_path = Path(temp_dir) / "video-download-manifest.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_video_download_manifest.py",
                "--schema-version",
                "discovery-video-download-manifest.sample.v1",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "discovery-video-download-manifest.sample.v1",
            )
            self.assertEqual(payload["summary"]["requested"], 4)
            self.assertEqual(payload["summary"]["fallbackToMetadataOnly"], 3)
            self.assertEqual(
                payload["downloads"][0]["duplicateRawDownloadIndexes"],
                [1],
            )

    def test_trending_source_snapshots_builder_passes(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-trending-source-snapshots-"
        ) as temp_dir:
            out_path = Path(temp_dir) / "source-snapshots.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_trending_source_snapshots.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "discovery-source-snapshots.v1")
            self.assertEqual(payload["sourceSnapshots"][0]["source"], "public_tiktok")
            self.assertEqual(
                payload["sourceSnapshots"][0]["sourceSubtype"],
                "consolidated_hot_video_sample",
            )

    def test_trending_video_samples_builder_passes(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-trending-video-samples-"
        ) as temp_dir:
            out_path = Path(temp_dir) / "video-samples.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_trending_video_samples.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "discovery-video-samples.v1")
            self.assertEqual(
                payload["videoSamples"][0]["videoSampleId"],
                "tt:7625618372616555808",
            )
            self.assertEqual(payload["videoSamples"][0]["metrics"]["views"], 182000)
            self.assertIn("hot_score", payload["videoSamples"][0]["rawMeta"])

    def test_trending_signal_items_builder_passes(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-trending-signal-items-"
        ) as temp_dir:
            out_path = Path(temp_dir) / "signal-items.json"
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_trending_signal_items.py",
                "--output",
                str(out_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "discovery-signal-items.v1")
            self.assertEqual(
                payload["signalItems"][0]["sourceType"],
                "public_video_sample",
            )
            self.assertEqual(
                payload["signalItems"][0]["videoSampleId"],
                "tt:7625618372616555808",
            )
            self.assertIn(
                "metadata-derived synthetic signal",
                payload["signalItems"][0]["executionNotes"],
            )

    def test_discovery_input_builder_filters_trending_view(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-trending-view-filter-"
        ) as temp_dir:
            out_dir = Path(temp_dir)
            result = self.run_script(
                "skills/autotiktok-topic-discovery/scripts/build_discovery_inputs_from_trending.py",
                "--input",
                "skills/autotiktok-topic-discovery/fixtures/trending-bakeoff.sample.json",
                "--view",
                "fresh_hot",
                "--output-dir",
                str(out_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            video_samples = json.loads(
                (out_dir / "video-samples.from-trending.json").read_text(
                    encoding="utf-8"
                )
            )
            source_snapshots = json.loads(
                (out_dir / "source-snapshots.from-trending.json").read_text(
                    encoding="utf-8"
                )
            )
            signal_items = json.loads(
                (out_dir / "signal-items.from-trending.synthetic.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(len(video_samples["videoSamples"]), 1)
            self.assertEqual(
                video_samples["videoSamples"][0]["sourceSnapshotId"],
                "snap.tiktok.direct-hot.fresh_hot.us.20260502t183100z",
            )
            self.assertEqual(
                source_snapshots["sourceSnapshots"][0]["sourceSubtype"],
                "fresh_hot_video_sample",
            )
            self.assertEqual(len(signal_items["signalItems"]), 1)
            self.assertEqual(
                signal_items["signalItems"][0]["videoSampleId"],
                video_samples["videoSamples"][0]["videoSampleId"],
            )

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
