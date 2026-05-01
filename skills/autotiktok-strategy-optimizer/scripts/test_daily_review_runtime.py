#!/usr/bin/env python3
"""
Unit tests for the daily review runtime adapters and service layer.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest import TestCase, main

from daily_review_service import build_daily_review_report
from optimizer_input_adapters import load_daily_review_runtime_inputs
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROOT = SKILL_DIR.parents[1]
RANKING_SAMPLE = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
CONTEXT_SAMPLE = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
)
BACKFILLS_SAMPLE = (
    SKILL_DIR / "fixtures" / "topic-outcome-backfills.sample.json"
)
BACKFILLS_RAW_SAMPLE = (
    SKILL_DIR / "fixtures" / "topic-outcome-backfills-raw.sample.json"
)
PERFORMANCE_SAMPLE = (
    SKILL_DIR / "fixtures" / "post-performance-signals.sample.json"
)
PERFORMANCE_RAW_SAMPLE = (
    SKILL_DIR / "fixtures" / "post-performance-raw.sample.json"
)
CHALLENGER_OBSERVATIONS_SAMPLE = (
    SKILL_DIR / "fixtures" / "challenger-observations.sample.json"
)
CHALLENGER_OBSERVATIONS_RAW_SAMPLE = (
    SKILL_DIR / "fixtures" / "challenger-observations-raw.sample.json"
)


class TestDailyReviewRuntime(TestCase):
    def build_runtime_inputs(
        self,
        *,
        backfills_payload: dict[str, object] | None = None,
        performance_items: list[dict[str, object]] | None = None,
        performance_payload: dict[str, object] | None = None,
        challenger_payload: dict[str, object],
    ):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        champion_profile_id = ranking_payload["predictionRun"]["profileId"]
        account_id = context_payload["accountId"]
        top_score = ranking_payload["scores"][0]

        normalized_backfills_payload = (
            {
                "schemaVersion": "topic-outcome-backfills.v1",
                "runId": run_id,
                "snapshotId": "snap.autotiktok.runtime.2026-04-16",
                "evaluationWindow": "t_plus_1",
                "items": [
                    {
                        "schemaVersion": "topic-outcome-backfill.v1",
                        "backfillId": "runtime.backfill.01",
                        "runId": run_id,
                        "topicId": top_score["topicId"],
                        "topicFingerprint": top_score["topicFingerprint"],
                        "backfillWindow": "t_plus_1",
                        "matchedBy": "topic_fingerprint",
                        "searchLift": 0.72,
                        "futureVideoDensity": 0.66,
                        "contentGapPersistence": 0.64,
                    }
                ],
            }
            if backfills_payload is None
            else backfills_payload
        )
        normalized_performance_payload = (
            {
                "schemaVersion": "post-performance-signals.v1",
                "runId": run_id,
                "accountId": account_id,
                "measuredWindow": "publish_plus_3d",
                "items": [] if performance_items is None else performance_items,
            }
            if performance_payload is None
            else performance_payload
        )
        normalized_challenger_payload = {
            "championProfileId": champion_profile_id,
            **challenger_payload,
        }

        with tempfile.TemporaryDirectory(prefix="autotiktok-runtime-inputs-") as temp_dir:
            temp_root = Path(temp_dir)
            backfills_path = temp_root / "backfills.json"
            performance_path = temp_root / "performance.json"
            challenger_path = temp_root / "challengers.json"
            backfills_path.write_text(
                json.dumps(
                    normalized_backfills_payload, ensure_ascii=True, indent=2
                )
                + "\n",
                encoding="utf-8",
            )
            performance_path.write_text(
                json.dumps(
                    normalized_performance_payload, ensure_ascii=True, indent=2
                )
                + "\n",
                encoding="utf-8",
            )
            challenger_path.write_text(
                json.dumps(normalized_challenger_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            return load_daily_review_runtime_inputs(
                ranking_input=RANKING_SAMPLE,
                context_input=CONTEXT_SAMPLE,
                backfills_input=backfills_path,
                performance_input=performance_path,
                challenger_input=challenger_path,
                contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
                validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            )

    def test_runtime_adapters_normalize_sparse_runtime_schemas(self):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        topic_id = ranking_payload["scores"][0]["topicId"]
        inputs = self.build_runtime_inputs(
            performance_items=[
                {
                    "schemaVersion": "post-performance-signal.v1",
                    "signalId": "runtime.signal.01",
                    "runId": run_id,
                    "topicId": topic_id,
                    "postId": "post.runtime.01",
                    "accountId": context_payload["accountId"],
                    "measuredWindow": "publish_plus_3d",
                    "viewLift": 0.61,
                }
            ],
            challenger_payload={
                "schemaVersion": "challenger-adjustments.v1",
                "challengers": [
                    {
                        "profileId": "search-priority-default",
                        "topicRewardDelta": 0.04,
                    }
                ],
            },
        )
        self.assertEqual(
            inputs.backfills_payload["schemaVersion"], "topic-outcome-backfills.v1"
        )
        self.assertEqual(
            inputs.performance_payload["schemaVersion"], "post-performance-signals.v1"
        )
        self.assertIsNone(inputs.performance_payload["items"][0]["retentionProxy"])
        self.assertIsNone(inputs.performance_payload["items"][0]["rawViews"])
        self.assertEqual(
            inputs.challenger_payload["schemaVersion"], "challenger-adjustments.v1"
        )
        self.assertEqual(inputs.challenger_payload["inputKind"], "adjustments")
        self.assertEqual(inputs.challenger_payload["challengers"][0]["daysObserved"], 1)
        self.assertEqual(
            inputs.challenger_payload["challengers"][0]["performanceRewardDelta"], 0.0
        )
        self.assertEqual(
            inputs.input_source_metadata["backfills"]["sourceKind"], "direct_artifact"
        )
        self.assertEqual(
            inputs.input_source_metadata["performance"]["sourceKind"], "direct_artifact"
        )
        self.assertEqual(
            inputs.input_source_metadata["challengerInput"]["sourceKind"], "direct_artifact"
        )

    def test_runtime_adapters_normalize_challenger_observations(self):
        inputs = self.build_runtime_inputs(
            performance_items=[],
            challenger_payload={
                "schemaVersion": "challenger-observations.v1",
                "evaluationWindow": "t_plus_3",
                "challengers": [
                    {
                        "schemaVersion": "challenger-observation.v1",
                        "profileId": "search-priority-default",
                        "topicMetrics": {
                            "Hit@3": 0.74,
                            "Hit@10": 0.7,
                            "NDCG@10": 0.93,
                            "DupRate": 0.28,
                            "TypeCoverage": 0.9,
                            "Novelty": 0.52,
                            "ExecutableRate": 0.7,
                        },
                        "performanceSummary": {
                            "performanceReward": 0.58,
                            "performanceWeight": 0.12,
                            "postCoverageRate": 0.67,
                        },
                        "holdoutDelta": 0.03,
                        "daysObserved": 5,
                    }
                ],
            },
        )
        self.assertEqual(
            inputs.challenger_payload["schemaVersion"], "challenger-observations.v1"
        )
        self.assertEqual(inputs.challenger_payload["inputKind"], "observations")
        self.assertEqual(inputs.challenger_payload["evaluationWindow"], "t_plus_3")
        self.assertEqual(
            inputs.challenger_payload["challengers"][0]["performanceSummary"]["performanceReward"],
            0.58,
        )

    def test_runtime_adapters_normalize_raw_post_performance_fixture(self):
        raw_performance_payload = json.loads(
            PERFORMANCE_RAW_SAMPLE.read_text(encoding="utf-8")
        )
        expected_performance_payload = json.loads(
            PERFORMANCE_SAMPLE.read_text(encoding="utf-8")
        )
        inputs = self.build_runtime_inputs(
            performance_payload=raw_performance_payload,
            challenger_payload={
                "schemaVersion": "challenger-adjustments.v1",
                "challengers": [],
            },
        )
        self.assertEqual(
            inputs.performance_payload,
            expected_performance_payload,
        )
        self.assertEqual(
            inputs.input_source_metadata["performance"]["sourceSchemaVersion"],
            "post-performance-raw.sample.v1",
        )
        self.assertEqual(
            inputs.input_source_metadata["performance"]["artifactSchemaVersion"],
            "post-performance-raw.sample.v1",
        )

    def test_runtime_adapters_normalize_raw_backfill_fixture(self):
        raw_backfills_payload = json.loads(
            BACKFILLS_RAW_SAMPLE.read_text(encoding="utf-8")
        )
        expected_backfills_payload = json.loads(
            BACKFILLS_SAMPLE.read_text(encoding="utf-8")
        )
        inputs = self.build_runtime_inputs(
            backfills_payload=raw_backfills_payload,
            performance_items=[],
            challenger_payload={
                "schemaVersion": "challenger-adjustments.v1",
                "challengers": [],
            },
        )
        self.assertEqual(inputs.backfills_payload, expected_backfills_payload)
        self.assertEqual(
            inputs.input_source_metadata["backfills"]["sourceSchemaVersion"],
            "topic-outcome-backfills-raw.sample.v1",
        )
        self.assertEqual(
            inputs.input_source_metadata["backfills"]["artifactSchemaVersion"],
            "topic-outcome-backfills-raw.sample.v1",
        )

    def test_runtime_adapters_normalize_raw_challenger_fixture(self):
        raw_challenger_payload = json.loads(
            CHALLENGER_OBSERVATIONS_RAW_SAMPLE.read_text(encoding="utf-8")
        )
        expected_challenger_payload = json.loads(
            CHALLENGER_OBSERVATIONS_SAMPLE.read_text(encoding="utf-8")
        )
        expected_challenger_payload["inputKind"] = "observations"
        inputs = self.build_runtime_inputs(
            performance_items=[],
            challenger_payload=raw_challenger_payload,
        )
        self.assertEqual(inputs.challenger_payload, expected_challenger_payload)
        self.assertEqual(inputs.challenger_payload["inputKind"], "observations")
        self.assertEqual(
            inputs.input_source_metadata["challengerInput"]["sourceSchemaVersion"],
            "challenger-observations-raw.sample.v1",
        )
        self.assertEqual(
            inputs.input_source_metadata["challengerInput"]["artifactSchemaVersion"],
            "challenger-observations-raw.sample.v1",
        )

    def test_runtime_loader_supports_input_bundle(self):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        champion_profile_id = ranking_payload["predictionRun"]["profileId"]
        bundle_payload = {
            "schemaVersion": "optimizer-input-bundle.v1",
            "bundleId": "runtime.optimizer.bundle.2026-04-16",
            "generatedAt": "2026-04-16T09:00:00Z",
            "generatedFrom": {"sourceKind": "runtime_test"},
            "artifacts": {
                "ranking": ranking_payload,
                "context": context_payload,
                "backfills": {
                    "schemaVersion": "topic-outcome-backfills.v1",
                    "runId": run_id,
                    "evaluationWindow": "t_plus_1",
                    "items": [
                        {
                            "schemaVersion": "topic-outcome-backfill.v1",
                            "backfillId": "bundle.backfill.01",
                            "runId": run_id,
                            "topicId": ranking_payload["scores"][0]["topicId"],
                            "topicFingerprint": ranking_payload["scores"][0]["topicFingerprint"],
                            "backfillWindow": "t_plus_1",
                            "matchedBy": "topic_fingerprint",
                            "searchLift": 0.72,
                            "futureVideoDensity": 0.66,
                            "contentGapPersistence": 0.64,
                        }
                    ],
                },
                "performance": {
                    "schemaVersion": "post-performance-signals.v1",
                    "runId": run_id,
                    "accountId": context_payload["accountId"],
                    "measuredWindow": "publish_plus_3d",
                    "items": [],
                },
                "challengerInput": {
                    "schemaVersion": "challenger-observations.v1",
                    "championProfileId": champion_profile_id,
                    "evaluationWindow": "t_plus_3",
                    "challengers": [],
                },
            },
        }
        with tempfile.TemporaryDirectory(prefix="autotiktok-runtime-bundle-") as temp_dir:
            bundle_path = Path(temp_dir) / "optimizer-input-bundle.json"
            bundle_path.write_text(
                json.dumps(bundle_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            inputs = load_daily_review_runtime_inputs(
                input_bundle=bundle_path,
                contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
                validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            )
        self.assertEqual(
            inputs.bundle_metadata["optimizerInputBundleSchemaVersion"],
            "optimizer-input-bundle.v1",
        )
        self.assertEqual(
            inputs.bundle_metadata["optimizerInputBundleId"],
            "runtime.optimizer.bundle.2026-04-16",
        )
        self.assertEqual(inputs.bundle_metadata["optimizerInputBundleGeneratedFrom"], {"sourceKind": "runtime_test"})

    def test_runtime_loader_unwraps_job_run_envelopes(self):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        champion_profile_id = ranking_payload["predictionRun"]["profileId"]
        account_id = context_payload["accountId"]
        topic_id = ranking_payload["scores"][0]["topicId"]
        topic_fingerprint = ranking_payload["scores"][0]["topicFingerprint"]
        backfills_payload = {
            "schemaVersion": "topic-outcome-backfills.v1",
            "runId": run_id,
            "evaluationWindow": "t_plus_1",
            "items": [
                {
                    "schemaVersion": "topic-outcome-backfill.v1",
                    "backfillId": "runtime.backfill.run-envelope.01",
                    "runId": run_id,
                    "topicId": topic_id,
                    "topicFingerprint": topic_fingerprint,
                    "backfillWindow": "t_plus_1",
                    "matchedBy": "topic_fingerprint",
                    "searchLift": 0.72,
                    "futureVideoDensity": 0.66,
                    "contentGapPersistence": 0.64,
                }
            ],
        }
        performance_payload = {
            "schemaVersion": "post-performance-signals.v1",
            "runId": run_id,
            "accountId": account_id,
            "measuredWindow": "publish_plus_3d",
            "items": [],
        }
        challenger_payload = {
            "schemaVersion": "challenger-observations.v1",
            "championProfileId": champion_profile_id,
            "evaluationWindow": "t_plus_3",
            "challengers": [],
        }
        backfill_run_payload = {
            "schemaVersion": "topic-outcome-backfill-run.v1",
            "jobRunId": "job.runtime.backfill.2026-04-16",
            "jobKind": "topic_outcome_backfill",
            "generatedAt": "2026-04-16T00:05:00Z",
            "generatedFrom": {"rankingRunId": run_id},
            "payload": backfills_payload,
        }
        performance_run_payload = {
            "schemaVersion": "post-performance-signal-run.v1",
            "jobRunId": "job.runtime.performance.2026-04-16",
            "jobKind": "post_performance_signal",
            "generatedAt": "2026-04-16T00:10:00Z",
            "generatedFrom": {"rankingRunId": run_id},
            "payload": performance_payload,
        }
        challenger_run_payload = {
            "schemaVersion": "challenger-evaluation-run.v1",
            "jobRunId": "job.runtime.challenger.2026-04-16",
            "jobKind": "challenger_evaluation",
            "generatedAt": "2026-04-16T00:15:00Z",
            "generatedFrom": {"championProfileId": champion_profile_id},
            "payload": challenger_payload,
        }
        with tempfile.TemporaryDirectory(prefix="autotiktok-runtime-job-runs-") as temp_dir:
            temp_root = Path(temp_dir)
            backfills_path = temp_root / "backfill-run.json"
            performance_path = temp_root / "performance-run.json"
            challenger_path = temp_root / "challenger-run.json"
            backfills_path.write_text(
                json.dumps(backfill_run_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            performance_path.write_text(
                json.dumps(performance_run_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            challenger_path.write_text(
                json.dumps(challenger_run_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            inputs = load_daily_review_runtime_inputs(
                ranking_input=RANKING_SAMPLE,
                context_input=CONTEXT_SAMPLE,
                backfills_input=backfills_path,
                performance_input=performance_path,
                challenger_input=challenger_path,
                contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
                validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            )
        self.assertEqual(
            inputs.backfills_payload["schemaVersion"], "topic-outcome-backfills.v1"
        )
        self.assertEqual(
            inputs.performance_payload["schemaVersion"], "post-performance-signals.v1"
        )
        self.assertEqual(
            inputs.challenger_payload["schemaVersion"], "challenger-observations.v1"
        )
        self.assertEqual(
            inputs.input_source_metadata["backfills"]["sourceKind"], "job_run_envelope"
        )
        self.assertEqual(
            inputs.input_source_metadata["performance"]["jobKind"],
            "post_performance_signal",
        )
        self.assertEqual(
            inputs.input_source_metadata["challengerInput"]["jobRunSchemaVersion"],
            "challenger-evaluation-run.v1",
        )

    def test_runtime_loader_unwraps_raw_post_performance_job_run_envelope(self):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        champion_profile_id = ranking_payload["predictionRun"]["profileId"]
        account_id = context_payload["accountId"]
        topic_id = ranking_payload["scores"][0]["topicId"]
        topic_fingerprint = ranking_payload["scores"][0]["topicFingerprint"]
        raw_performance_payload = json.loads(
            PERFORMANCE_RAW_SAMPLE.read_text(encoding="utf-8")
        )
        raw_performance_payload["schemaVersion"] = "post-performance-raw.v1"
        backfills_payload = {
            "schemaVersion": "topic-outcome-backfills.v1",
            "runId": run_id,
            "evaluationWindow": "t_plus_1",
            "items": [
                {
                    "schemaVersion": "topic-outcome-backfill.v1",
                    "backfillId": "runtime.backfill.raw-envelope.01",
                    "runId": run_id,
                    "topicId": topic_id,
                    "topicFingerprint": topic_fingerprint,
                    "backfillWindow": "t_plus_1",
                    "matchedBy": "topic_fingerprint",
                    "searchLift": 0.72,
                    "futureVideoDensity": 0.66,
                    "contentGapPersistence": 0.64,
                }
            ],
        }
        challenger_payload = {
            "schemaVersion": "challenger-observations.v1",
            "championProfileId": champion_profile_id,
            "evaluationWindow": "t_plus_3",
            "challengers": [],
        }
        performance_run_payload = {
            "schemaVersion": "post-performance-signal-run.v1",
            "jobRunId": "job.runtime.performance.raw.2026-04-16",
            "jobKind": "post_performance_signal",
            "generatedAt": "2026-04-16T00:10:00Z",
            "generatedFrom": {"rankingRunId": run_id},
            "payload": raw_performance_payload,
        }
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-runtime-raw-performance-run-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            backfills_path = temp_root / "backfills.json"
            performance_path = temp_root / "performance-run.json"
            challenger_path = temp_root / "challenger.json"
            backfills_path.write_text(
                json.dumps(backfills_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            performance_path.write_text(
                json.dumps(performance_run_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            challenger_path.write_text(
                json.dumps(challenger_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            inputs = load_daily_review_runtime_inputs(
                ranking_input=RANKING_SAMPLE,
                context_input=CONTEXT_SAMPLE,
                backfills_input=backfills_path,
                performance_input=performance_path,
                challenger_input=challenger_path,
                contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
                validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            )
        self.assertEqual(
            inputs.performance_payload["schemaVersion"], "post-performance-signals.v1"
        )
        self.assertEqual(
            inputs.performance_payload["items"][0]["rawViews"],
            raw_performance_payload["items"][0]["observedViews"],
        )
        self.assertEqual(
            inputs.performance_payload["items"][0]["baselineViews"],
            raw_performance_payload["items"][0]["expectedViews"],
        )
        self.assertEqual(
            inputs.performance_payload["items"][0]["viewLift"],
            raw_performance_payload["items"][0]["normalizedViewLift"],
        )
        self.assertEqual(
            inputs.input_source_metadata["performance"]["sourceKind"], "job_run_envelope"
        )
        self.assertEqual(
            inputs.input_source_metadata["performance"]["artifactSchemaVersion"],
            "post-performance-raw.v1",
        )

    def test_runtime_loader_unwraps_raw_backfill_job_run_envelope(self):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        champion_profile_id = ranking_payload["predictionRun"]["profileId"]
        raw_backfills_payload = json.loads(
            BACKFILLS_RAW_SAMPLE.read_text(encoding="utf-8")
        )
        raw_backfills_payload["schemaVersion"] = "topic-outcome-backfills-raw.v1"
        challenger_payload = {
            "schemaVersion": "challenger-observations.v1",
            "championProfileId": champion_profile_id,
            "evaluationWindow": "t_plus_3",
            "challengers": [],
        }
        performance_payload = {
            "schemaVersion": "post-performance-signals.v1",
            "runId": run_id,
            "accountId": context_payload["accountId"],
            "measuredWindow": "publish_plus_3d",
            "items": [],
        }
        backfill_run_payload = {
            "schemaVersion": "topic-outcome-backfill-run.v1",
            "jobRunId": "job.runtime.backfill.raw.2026-04-16",
            "jobKind": "topic_outcome_backfill",
            "generatedAt": "2026-04-16T00:05:00Z",
            "generatedFrom": {"rankingRunId": run_id},
            "payload": raw_backfills_payload,
        }
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-runtime-raw-backfill-run-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            backfills_path = temp_root / "backfill-run.json"
            performance_path = temp_root / "performance.json"
            challenger_path = temp_root / "challenger.json"
            backfills_path.write_text(
                json.dumps(backfill_run_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            performance_path.write_text(
                json.dumps(performance_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            challenger_path.write_text(
                json.dumps(challenger_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            inputs = load_daily_review_runtime_inputs(
                ranking_input=RANKING_SAMPLE,
                context_input=CONTEXT_SAMPLE,
                backfills_input=backfills_path,
                performance_input=performance_path,
                challenger_input=challenger_path,
                contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
                validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            )
        self.assertEqual(
            inputs.backfills_payload["schemaVersion"], "topic-outcome-backfills.v1"
        )
        self.assertEqual(
            inputs.backfills_payload["items"][0]["matchedBy"],
            raw_backfills_payload["items"][0]["matchStrategy"],
        )
        self.assertEqual(
            inputs.input_source_metadata["backfills"]["sourceKind"], "job_run_envelope"
        )
        self.assertEqual(
            inputs.input_source_metadata["backfills"]["artifactSchemaVersion"],
            "topic-outcome-backfills-raw.v1",
        )

    def test_runtime_loader_unwraps_raw_challenger_job_run_envelope(self):
        ranking_payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
        context_payload = json.loads(CONTEXT_SAMPLE.read_text(encoding="utf-8"))
        run_id = ranking_payload["predictionRun"]["runId"]
        champion_profile_id = ranking_payload["predictionRun"]["profileId"]
        raw_challenger_payload = json.loads(
            CHALLENGER_OBSERVATIONS_RAW_SAMPLE.read_text(encoding="utf-8")
        )
        raw_challenger_payload["schemaVersion"] = "challenger-observations-raw.v1"
        backfills_payload = {
            "schemaVersion": "topic-outcome-backfills.v1",
            "runId": run_id,
            "evaluationWindow": "t_plus_1",
            "items": [
                {
                    "schemaVersion": "topic-outcome-backfill.v1",
                    "backfillId": "runtime.backfill.raw-challenger.01",
                    "runId": run_id,
                    "topicId": ranking_payload["scores"][0]["topicId"],
                    "topicFingerprint": ranking_payload["scores"][0]["topicFingerprint"],
                    "backfillWindow": "t_plus_1",
                    "matchedBy": "topic_fingerprint",
                    "searchLift": 0.72,
                    "futureVideoDensity": 0.66,
                    "contentGapPersistence": 0.64,
                }
            ],
        }
        performance_payload = {
            "schemaVersion": "post-performance-signals.v1",
            "runId": run_id,
            "accountId": context_payload["accountId"],
            "measuredWindow": "publish_plus_3d",
            "items": [],
        }
        challenger_run_payload = {
            "schemaVersion": "challenger-evaluation-run.v1",
            "jobRunId": "job.runtime.challenger.raw.2026-04-16",
            "jobKind": "challenger_evaluation",
            "generatedAt": "2026-04-16T00:15:00Z",
            "generatedFrom": {"championProfileId": champion_profile_id},
            "payload": raw_challenger_payload,
        }
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-runtime-raw-challenger-run-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            backfills_path = temp_root / "backfills.json"
            performance_path = temp_root / "performance.json"
            challenger_path = temp_root / "challenger-run.json"
            backfills_path.write_text(
                json.dumps(backfills_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            performance_path.write_text(
                json.dumps(performance_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            challenger_path.write_text(
                json.dumps(challenger_run_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            inputs = load_daily_review_runtime_inputs(
                ranking_input=RANKING_SAMPLE,
                context_input=CONTEXT_SAMPLE,
                backfills_input=backfills_path,
                performance_input=performance_path,
                challenger_input=challenger_path,
                contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
                validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            )
        self.assertEqual(
            inputs.challenger_payload["schemaVersion"], "challenger-observations.v1"
        )
        self.assertEqual(inputs.challenger_payload["inputKind"], "observations")
        self.assertEqual(
            inputs.challenger_payload["challengers"][0]["daysObserved"],
            raw_challenger_payload["challengers"][0]["observedDays"],
        )
        self.assertEqual(
            inputs.input_source_metadata["challengerInput"]["sourceKind"],
            "job_run_envelope",
        )
        self.assertEqual(
            inputs.input_source_metadata["challengerInput"]["artifactSchemaVersion"],
            "challenger-observations-raw.v1",
        )

    def test_daily_review_service_handles_empty_runtime_batches(self):
        inputs = self.build_runtime_inputs(
            performance_items=[],
            challenger_payload={
                "schemaVersion": "challenger-adjustments.v1",
                "challengers": [],
            },
        )
        report = build_daily_review_report(
            inputs,
            report_id="daily-review.autotiktok.runtime.2026-04-16",
            generated_at="2026-04-16T06:00:00Z",
        )
        self.assertEqual(report["schemaVersion"], "daily-review-report.v1")
        self.assertEqual(
            report["generatedFrom"]["backfillsSchemaVersion"],
            "topic-outcome-backfills.v1",
        )
        self.assertEqual(
            report["generatedFrom"]["performanceSchemaVersion"],
            "post-performance-signals.v1",
        )
        self.assertEqual(
            report["generatedFrom"]["challengerSchemaVersion"],
            "challenger-adjustments.v1",
        )
        self.assertEqual(report["generatedFrom"]["challengerInputKind"], "adjustments")
        self.assertIsNone(report["combinedRewardBreakdown"]["performanceReward"])
        self.assertEqual(report["combinedRewardBreakdown"]["performanceWeight"], 0.0)
        self.assertEqual(report["challengerReview"]["inputKind"], "adjustments")
        self.assertEqual(
            report["generatedFrom"]["optimizerInputSources"]["backfills"]["sourceKind"],
            "direct_artifact",
        )
        self.assertEqual(report["postPerformanceRows"], [])
        self.assertEqual(report["shadowLeaderboard"], [])
        self.assertEqual(report["recommendation"]["kind"], "keep_champion")

    def test_daily_review_service_uses_observed_challenger_metrics(self):
        inputs = self.build_runtime_inputs(
            performance_items=[],
            challenger_payload={
                "schemaVersion": "challenger-observations.v1",
                "evaluationWindow": "t_plus_3",
                "observationWindow": "2026-04-10..2026-04-16",
                "challengers": [
                    {
                        "schemaVersion": "challenger-observation.v1",
                        "profileId": "search-priority-default",
                        "topicMetrics": {
                            "Hit@3": 0.8,
                            "Hit@10": 0.76,
                            "NDCG@10": 0.95,
                            "DupRate": 0.25,
                            "TypeCoverage": 0.92,
                            "Novelty": 0.54,
                            "ExecutableRate": 0.71,
                        },
                        "performanceSummary": {
                            "performanceReward": 0.61,
                            "performanceWeight": 0.12,
                            "postCoverageRate": 0.67,
                        },
                        "holdoutDelta": 0.05,
                        "daysObserved": 6,
                    }
                ],
            },
        )
        report = build_daily_review_report(
            inputs,
            report_id="daily-review.autotiktok.runtime-observed.2026-04-16",
            generated_at="2026-04-16T08:00:00Z",
        )
        self.assertEqual(
            report["generatedFrom"]["challengerSchemaVersion"],
            "challenger-observations.v1",
        )
        self.assertEqual(report["generatedFrom"]["challengerInputKind"], "observations")
        self.assertEqual(report["challengerReview"]["inputKind"], "observations")
        self.assertEqual(report["challengerReview"]["hardGatePassCount"], 1)
        self.assertEqual(report["challengerReview"]["leaderProfileId"], "search-priority-default")
        self.assertEqual(report["shadowLeaderboard"][0]["sourceInputKind"], "observations")
        self.assertGreater(report["shadowLeaderboard"][0]["combinedRewardDelta"], 0)
        self.assertEqual(report["shadowLeaderboard"][0]["postCoverageRate"], 0.67)


if __name__ == "__main__":
    main()
