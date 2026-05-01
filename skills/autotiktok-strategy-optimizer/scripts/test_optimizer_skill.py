#!/usr/bin/env python3
"""
Smoke tests for the AutoTikTok optimizer skill.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main

from optimizer_input_rollout_lib import resolve_optimizer_input_rollout_selection
from optimizer_job_schedule_lib import (
    resolve_optimizer_job_schedule_execution_policy,
    resolve_optimizer_job_scheduler_rollout_intent,
)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROOT = SKILL_DIR.parents[1]
RANKING_SAMPLE = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
RAW_BACKFILLS_SAMPLE = (
    SKILL_DIR / "fixtures" / "topic-outcome-backfills-raw.sample.json"
)
RAW_PERFORMANCE_SAMPLE = (
    SKILL_DIR / "fixtures" / "post-performance-raw.sample.json"
)
RAW_CHALLENGER_SAMPLE = (
    SKILL_DIR / "fixtures" / "challenger-observations-raw.sample.json"
)


class TestOptimizerSkill(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def build_input_bundle(self, output_path: Path) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_bundle.py",
            "--output",
            str(output_path),
        )

    def build_input_source_registry(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_source_registry.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_source_provider_catalog(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_source_provider_catalog.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_source_provider_registry(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_source_provider_registry.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_source_artifact_catalog(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_source_artifact_catalog.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_input_rollout_policy(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_rollout_policy.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_artifact_resolver(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_artifact_resolver.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_runtime_artifact_registry(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_artifact_registry.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_runtime_profile_catalog(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_profile_catalog.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_runtime_profile_family_registry(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_profile_family_registry.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_runtime_profile_rollout_policy(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_profile_rollout_policy.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_runtime_materialization_plan(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_materialization_plan.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_input_manifest(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_manifest.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_eval_run(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_run.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_eval_batch(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_eval_batch_manifest(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_manifest.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_eval_batch_history_manifest(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_history_manifest.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_eval_window_set(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_window_set.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_topic_outcome_backfill_run(
        self, output_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_topic_outcome_backfill_run.py",
            "--output",
            str(output_path),
        )

    def build_post_performance_signal_run(
        self, output_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_post_performance_signal_run.py",
            "--output",
            str(output_path),
        )

    def build_challenger_evaluation_run(
        self, output_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_challenger_evaluation_run.py",
            "--output",
            str(output_path),
        )

    def build_offline_cycle(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_weekly_review_window(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_weekly_review_window.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_daily_job_run(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_daily_optimizer_job.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_weekly_job_run(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_weekly_optimizer_job.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_openclaw_cron_daily_job(
        self, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_daily_optimizer.py",
            *extra_args,
        )

    def build_openclaw_cron_weekly_job(
        self, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_weekly_optimizer.py",
            *extra_args,
        )

    def build_openclaw_cron_contract(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_openclaw_cron_contract.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_schedule(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_schedule.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_execution_context(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_execution_context.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_artifact_retention_policy(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_artifact_retention_policy.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_error_sample(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_error_sample.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def run_scheduled_job(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def run_job_orchestration_cycle(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/run_optimizer_job_orchestration_cycle.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_run_summary(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_run_summary.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_recent_run_summaries(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_recent_run_summaries.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_recent_compare_summaries(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_recent_compare_summaries.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_recent_weekly_decisions(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_recent_weekly_decisions.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_recent_failure_summaries(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_recent_failure_summaries.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_shadow_compare(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_shadow_compare_plan(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare_plan.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_shadow_compare_batch_manifest(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare_batch_manifest.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_job_shadow_compare_batch(
        self, output_path: Path, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare_batch.py",
            *extra_args,
            "--output",
            str(output_path),
        )

    def build_history_window_inputs(
        self, temp_root: Path
    ) -> tuple[Path, Path, Path, Path]:
        manifest_path = temp_root / "optimizer-input-manifest.json"
        bundle_path = temp_root / "optimizer-input-bundle.json"
        offline_cycle_daily_path = temp_root / "optimizer-offline-cycle-daily.json"
        offline_cycle_weekly_path = temp_root / "optimizer-offline-cycle.json"
        manifest = self.build_input_manifest(manifest_path)
        self.assertEqual(manifest.returncode, 0, manifest.stderr)
        bundle = self.build_input_bundle(bundle_path)
        self.assertEqual(bundle.returncode, 0, bundle.stderr)
        offline_cycle_daily = self.build_offline_cycle(
            offline_cycle_daily_path,
            "--input-manifest",
            str(manifest_path),
            "--cycle-id",
            "optimizer-offline-cycle.autotiktok.test.daily",
            "--report-id",
            "daily-review.autotiktok.test.daily",
        )
        self.assertEqual(offline_cycle_daily.returncode, 0, offline_cycle_daily.stderr)
        offline_cycle_weekly = self.build_offline_cycle(
            offline_cycle_weekly_path,
            "--input-bundle",
            str(bundle_path),
            "--include-weekly-promotion",
            "--cycle-id",
            "optimizer-offline-cycle.autotiktok.test.weekly",
            "--report-id",
            "daily-review.autotiktok.test.weekly",
        )
        self.assertEqual(
            offline_cycle_weekly.returncode, 0, offline_cycle_weekly.stderr
        )
        return (
            manifest_path,
            bundle_path,
            offline_cycle_daily_path,
            offline_cycle_weekly_path,
        )

    def test_optimizer_fixture_validator_passes(self):
        result = self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/validate_optimizer_fixtures.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Optimizer fixtures are valid.", result.stdout)

    def test_optimizer_input_bundle_builder_writes_bundle(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-bundle-") as temp_dir:
            bundle_path = Path(temp_dir) / "optimizer-input-bundle.json"
            result = self.build_input_bundle(bundle_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-input-bundle.sample.v1")
            self.assertEqual(
                payload["artifacts"]["challengerInput"]["schemaVersion"],
                "challenger-observations.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["inputSources"]["backfills"]["sourceKind"],
                "job_run_envelope",
            )
            self.assertEqual(
                payload["generatedFrom"]["inputSources"]["performance"]["sourceKind"],
                "job_run_envelope",
            )
            self.assertEqual(
                payload["generatedFrom"]["inputSources"]["challengerInput"]["sourceKind"],
                "job_run_envelope",
            )

    def test_optimizer_input_manifest_builder_writes_manifest(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-manifest-") as temp_dir:
            manifest_path = Path(temp_dir) / "optimizer-input-manifest.json"
            result = self.build_input_manifest(manifest_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-input-manifest.sample.v1")
            self.assertIn(
                "skills/autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json",
                payload["artifactPaths"]["ranking"],
            )
            self.assertIn(
                "skills/autotiktok-strategy-optimizer/fixtures/topic-outcome-backfill-run.sample.json",
                payload["artifactPaths"]["backfills"],
            )
            self.assertIn(
                "skills/autotiktok-strategy-optimizer/fixtures/post-performance-signal-run.sample.json",
                payload["artifactPaths"]["performance"],
            )
            self.assertIn(
                "skills/autotiktok-strategy-optimizer/fixtures/challenger-evaluation-run.sample.json",
                payload["artifactPaths"]["challengerInput"],
            )

    def test_optimizer_input_source_registry_builder_writes_registry(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-input-source-registry-"
        ) as temp_dir:
            registry_path = Path(temp_dir) / "optimizer-input-source-registry.json"
            artifact_catalog_path = (
                Path(temp_dir) / "optimizer-source-artifact-catalog.json"
            )
            provider_registry_path = (
                Path(temp_dir) / "optimizer-source-provider-registry.json"
            )
            provider_catalog_path = (
                Path(temp_dir) / "optimizer-source-provider-catalog.json"
            )
            resolver_path = Path(temp_dir) / "optimizer-job-artifact-resolver.json"
            artifact_catalog_result = self.build_source_artifact_catalog(
                artifact_catalog_path
            )
            self.assertEqual(
                artifact_catalog_result.returncode, 0, artifact_catalog_result.stderr
            )
            provider_registry_result = self.build_source_provider_registry(
                provider_registry_path,
                "--input-source-artifact-catalog",
                str(artifact_catalog_path),
            )
            self.assertEqual(
                provider_registry_result.returncode, 0, provider_registry_result.stderr
            )
            provider_result = self.build_source_provider_catalog(
                provider_catalog_path,
                "--input-source-provider-registry",
                str(provider_registry_path),
            )
            self.assertEqual(provider_result.returncode, 0, provider_result.stderr)
            resolver_result = self.build_job_artifact_resolver(
                resolver_path,
                "--input-source-provider-catalog",
                str(provider_catalog_path),
            )
            self.assertEqual(resolver_result.returncode, 0, resolver_result.stderr)
            result = self.build_input_source_registry(
                registry_path,
                "--input-artifact-resolver",
                str(resolver_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-input-source-registry.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["sourceCount"], 15)
            self.assertEqual(payload["generatedFrom"]["laneCount"], 3)
            self.assertEqual(payload["sources"][0]["bindingId"], "ranking_sample")
            self.assertEqual(payload["sources"][-1]["bindingId"], "challenger_real_shadow")
            self.assertEqual(
                payload["inputArtifactResolverReference"]["resolverId"],
                "optimizer-job-artifact-resolver.autotiktok.fixture.2026-04-18",
            )

    def test_optimizer_source_provider_registry_builder_writes_registry(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-source-provider-registry-"
        ) as temp_dir:
            artifact_catalog_path = (
                Path(temp_dir) / "optimizer-source-artifact-catalog.json"
            )
            registry_path = Path(temp_dir) / "optimizer-source-provider-registry.json"
            artifact_catalog_result = self.build_source_artifact_catalog(
                artifact_catalog_path
            )
            self.assertEqual(
                artifact_catalog_result.returncode, 0, artifact_catalog_result.stderr
            )
            result = self.build_source_provider_registry(
                registry_path,
                "--input-source-artifact-catalog",
                str(artifact_catalog_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-source-provider-registry.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["bindingCount"], 5)
            self.assertEqual(payload["generatedFrom"]["laneCount"], 1)
            self.assertEqual(
                payload["bindings"][0]["providerBindingId"],
                "ranking_real_shadow_binding",
            )
            self.assertEqual(
                payload["bindings"][-1]["providerBindingId"],
                "challenger_real_shadow_binding",
            )
            self.assertEqual(
                payload["inputSourceArtifactCatalogReference"]["catalogId"],
                "optimizer-source-artifact-catalog.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                payload["bindings"][0]["artifactCatalogEntryId"],
                "ranking_real_shadow_artifact",
            )

    def test_optimizer_source_artifact_catalog_builder_writes_catalog(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-source-artifact-catalog-"
        ) as temp_dir:
            catalog_path = Path(temp_dir) / "optimizer-source-artifact-catalog.json"
            result = self.build_source_artifact_catalog(catalog_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-source-artifact-catalog.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["entryCount"], 5)
            self.assertEqual(payload["generatedFrom"]["laneCount"], 1)
            self.assertEqual(
                payload["entries"][0]["artifactCatalogEntryId"],
                "ranking_real_shadow_artifact",
            )
            self.assertEqual(
                payload["entries"][-1]["artifactCatalogEntryId"],
                "challenger_real_shadow_artifact",
            )

    def test_optimizer_source_provider_catalog_builder_writes_catalog(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-source-provider-catalog-"
        ) as temp_dir:
            artifact_catalog_path = (
                Path(temp_dir) / "optimizer-source-artifact-catalog.json"
            )
            provider_registry_path = (
                Path(temp_dir) / "optimizer-source-provider-registry.json"
            )
            catalog_path = Path(temp_dir) / "optimizer-source-provider-catalog.json"
            artifact_catalog_result = self.build_source_artifact_catalog(
                artifact_catalog_path
            )
            self.assertEqual(
                artifact_catalog_result.returncode, 0, artifact_catalog_result.stderr
            )
            registry_result = self.build_source_provider_registry(
                provider_registry_path,
                "--input-source-artifact-catalog",
                str(artifact_catalog_path),
            )
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            result = self.build_source_provider_catalog(
                catalog_path,
                "--input-source-provider-registry",
                str(provider_registry_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-source-provider-catalog.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["providerCount"], 5)
            self.assertEqual(payload["generatedFrom"]["laneCount"], 1)
            self.assertEqual(
                payload["providers"][0]["sourceProviderId"],
                "ranking_real_shadow_provider",
            )
            self.assertEqual(
                payload["providers"][-1]["sourceProviderId"],
                "challenger_real_shadow_provider",
            )
            self.assertEqual(
                payload["providers"][0]["providerBindingId"],
                "ranking_real_shadow_binding",
            )
            self.assertEqual(
                payload["inputSourceProviderRegistryReference"]["registryId"],
                "optimizer-source-provider-registry.autotiktok.fixture.2026-04-18",
            )

    def test_optimizer_job_artifact_resolver_builder_writes_resolver(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-artifact-resolver-"
        ) as temp_dir:
            artifact_catalog_path = (
                Path(temp_dir) / "optimizer-source-artifact-catalog.json"
            )
            provider_registry_path = (
                Path(temp_dir) / "optimizer-source-provider-registry.json"
            )
            provider_catalog_path = (
                Path(temp_dir) / "optimizer-source-provider-catalog.json"
            )
            resolver_path = Path(temp_dir) / "optimizer-job-artifact-resolver.json"
            artifact_catalog_result = self.build_source_artifact_catalog(
                artifact_catalog_path
            )
            self.assertEqual(
                artifact_catalog_result.returncode, 0, artifact_catalog_result.stderr
            )
            provider_registry_result = self.build_source_provider_registry(
                provider_registry_path,
                "--input-source-artifact-catalog",
                str(artifact_catalog_path),
            )
            self.assertEqual(
                provider_registry_result.returncode, 0, provider_registry_result.stderr
            )
            provider_result = self.build_source_provider_catalog(
                provider_catalog_path,
                "--input-source-provider-registry",
                str(provider_registry_path),
            )
            self.assertEqual(provider_result.returncode, 0, provider_result.stderr)
            result = self.build_job_artifact_resolver(
                resolver_path,
                "--input-source-provider-catalog",
                str(provider_catalog_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(resolver_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-job-artifact-resolver.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["entryCount"], 5)
            self.assertEqual(payload["generatedFrom"]["laneCount"], 1)
            self.assertEqual(payload["entries"][0]["resolverEntryId"], "ranking_real_shadow")
            self.assertEqual(
                payload["entries"][-1]["resolverEntryId"], "challenger_real_shadow"
            )
            self.assertEqual(
                payload["entries"][0]["sourceProviderId"],
                "ranking_real_shadow_provider",
            )
            self.assertEqual(
                payload["inputSourceProviderCatalogReference"]["catalogId"],
                "optimizer-source-provider-catalog.autotiktok.fixture.2026-04-18",
            )

    def test_optimizer_input_manifest_builder_supports_raw_shadow_lane(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-raw-shadow-manifest-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-input-source-registry.json"
            manifest_path = temp_root / "optimizer-input-manifest.raw-shadow.json"
            resolver_path = temp_root / "optimizer-job-artifact-resolver.json"
            resolver_result = self.build_job_artifact_resolver(resolver_path)
            self.assertEqual(resolver_result.returncode, 0, resolver_result.stderr)
            registry_result = self.build_input_source_registry(
                registry_path,
                "--input-artifact-resolver",
                str(resolver_path),
            )
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            manifest_result = self.build_input_manifest(
                manifest_path,
                "--input-source-registry",
                str(registry_path),
                "--source-lane",
                "sample_raw_shadow",
                "--manifest-id",
                "optimizer-input-manifest.raw-shadow.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T03:05:00Z",
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["generatedFrom"]["sourceLane"], "sample_raw_shadow")
            self.assertEqual(
                payload["artifactBindings"]["backfills"], "backfills_raw_shadow"
            )
            self.assertEqual(
                payload["artifactBindings"]["performance"], "performance_raw_shadow"
            )
            self.assertEqual(
                payload["artifactBindings"]["challengerInput"],
                "challenger_raw_shadow",
            )

    def test_optimizer_input_manifest_builder_supports_real_shadow_lane(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-real-shadow-manifest-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            artifact_catalog_path = (
                temp_root / "optimizer-source-artifact-catalog.json"
            )
            provider_registry_path = (
                temp_root / "optimizer-source-provider-registry.json"
            )
            provider_catalog_path = (
                temp_root / "optimizer-source-provider-catalog.json"
            )
            resolver_path = temp_root / "optimizer-job-artifact-resolver.json"
            registry_path = temp_root / "optimizer-input-source-registry.json"
            manifest_path = temp_root / "optimizer-input-manifest.real-shadow.json"
            artifact_catalog_result = self.build_source_artifact_catalog(
                artifact_catalog_path
            )
            self.assertEqual(
                artifact_catalog_result.returncode, 0, artifact_catalog_result.stderr
            )
            provider_registry_result = self.build_source_provider_registry(
                provider_registry_path,
                "--input-source-artifact-catalog",
                str(artifact_catalog_path),
            )
            self.assertEqual(
                provider_registry_result.returncode, 0, provider_registry_result.stderr
            )
            provider_result = self.build_source_provider_catalog(
                provider_catalog_path,
                "--input-source-provider-registry",
                str(provider_registry_path),
            )
            self.assertEqual(provider_result.returncode, 0, provider_result.stderr)
            resolver_result = self.build_job_artifact_resolver(
                resolver_path,
                "--input-source-provider-catalog",
                str(provider_catalog_path),
            )
            self.assertEqual(resolver_result.returncode, 0, resolver_result.stderr)
            registry_result = self.build_input_source_registry(
                registry_path,
                "--input-artifact-resolver",
                str(resolver_path),
            )
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            manifest_result = self.build_input_manifest(
                manifest_path,
                "--input-source-registry",
                str(registry_path),
                "--source-lane",
                "real_provider_shadow",
                "--manifest-id",
                "optimizer-input-manifest.real-shadow.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T03:12:00Z",
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["generatedFrom"]["sourceLane"], "real_provider_shadow")
            self.assertEqual(
                payload["artifactBindings"]["backfills"], "backfills_real_shadow"
            )
            self.assertEqual(
                payload["artifactBindings"]["performance"], "performance_real_shadow"
            )
            self.assertEqual(
                payload["artifactBindings"]["challengerInput"],
                "challenger_real_shadow",
            )
            self.assertEqual(
                payload["generatedFrom"][
                    "optimizerInputSourceProviderCatalogSchemaVersion"
                ],
                "optimizer-source-provider-catalog.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSourceProviderCatalogId"],
                "optimizer-source-provider-catalog.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                payload["generatedFrom"][
                    "optimizerInputSourceProviderRegistrySchemaVersion"
                ],
                "optimizer-source-provider-registry.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSourceProviderRegistryId"],
                "optimizer-source-provider-registry.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                payload["generatedFrom"][
                    "optimizerInputSourceArtifactCatalogSchemaVersion"
                ],
                "optimizer-source-artifact-catalog.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSourceArtifactCatalogId"],
                "optimizer-source-artifact-catalog.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSourceProviderClass"],
                "artifact_catalog_service",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputArtifactLocatorKind"],
                "provider_locator",
            )

    def test_optimizer_job_run_builders_write_envelopes(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-job-runs-") as temp_dir:
            temp_root = Path(temp_dir)
            backfill_run_path = temp_root / "topic-outcome-backfill-run.json"
            performance_run_path = temp_root / "post-performance-signal-run.json"
            challenger_run_path = temp_root / "challenger-evaluation-run.json"
            backfill_result = self.build_topic_outcome_backfill_run(backfill_run_path)
            performance_result = self.build_post_performance_signal_run(performance_run_path)
            challenger_result = self.build_challenger_evaluation_run(challenger_run_path)
            self.assertEqual(backfill_result.returncode, 0, backfill_result.stderr)
            self.assertEqual(performance_result.returncode, 0, performance_result.stderr)
            self.assertEqual(challenger_result.returncode, 0, challenger_result.stderr)
            backfill_payload = json.loads(backfill_run_path.read_text(encoding="utf-8"))
            performance_payload = json.loads(performance_run_path.read_text(encoding="utf-8"))
            challenger_payload = json.loads(challenger_run_path.read_text(encoding="utf-8"))
            self.assertEqual(
                backfill_payload["schemaVersion"],
                "topic-outcome-backfill-run.sample.v1",
            )
            self.assertEqual(
                performance_payload["schemaVersion"],
                "post-performance-signal-run.sample.v1",
            )
            self.assertEqual(
                challenger_payload["schemaVersion"],
                "challenger-evaluation-run.sample.v1",
            )

    def test_optimizer_job_run_builders_accept_raw_payloads(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-raw-job-runs-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            backfill_run_path = temp_root / "topic-outcome-backfill-run.raw.json"
            performance_run_path = temp_root / "post-performance-signal-run.raw.json"
            challenger_run_path = temp_root / "challenger-evaluation-run.raw.json"
            backfill_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/build_topic_outcome_backfill_run.py",
                "--input",
                str(RAW_BACKFILLS_SAMPLE),
                "--output",
                str(backfill_run_path),
            )
            performance_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/build_post_performance_signal_run.py",
                "--input",
                str(RAW_PERFORMANCE_SAMPLE),
                "--output",
                str(performance_run_path),
            )
            challenger_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/build_challenger_evaluation_run.py",
                "--input",
                str(RAW_CHALLENGER_SAMPLE),
                "--output",
                str(challenger_run_path),
            )
            self.assertEqual(backfill_result.returncode, 0, backfill_result.stderr)
            self.assertEqual(performance_result.returncode, 0, performance_result.stderr)
            self.assertEqual(challenger_result.returncode, 0, challenger_result.stderr)
            backfill_payload = json.loads(backfill_run_path.read_text(encoding="utf-8"))
            performance_payload = json.loads(performance_run_path.read_text(encoding="utf-8"))
            challenger_payload = json.loads(challenger_run_path.read_text(encoding="utf-8"))
            self.assertEqual(
                backfill_payload["payload"]["schemaVersion"],
                "topic-outcome-backfills-raw.sample.v1",
            )
            self.assertEqual(
                performance_payload["payload"]["schemaVersion"],
                "post-performance-raw.sample.v1",
            )
            self.assertEqual(
                challenger_payload["payload"]["schemaVersion"],
                "challenger-observations-raw.sample.v1",
            )

    def test_optimizer_input_bundle_materializer_accepts_manifest(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-materialize-") as temp_dir:
            manifest_path = Path(temp_dir) / "optimizer-input-manifest.json"
            bundle_path = Path(temp_dir) / "optimizer-input-bundle.json"
            manifest = self.build_input_manifest(manifest_path)
            self.assertEqual(manifest.returncode, 0, manifest.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/materialize_optimizer_input_bundle.py",
                "--input-manifest",
                str(manifest_path),
                "--output",
                str(bundle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-input-bundle.sample.v1")
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputManifestSchemaVersion"],
                "optimizer-input-manifest.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["inputSources"]["challengerInput"]["jobKind"],
                "challenger_evaluation",
            )

    def test_optimizer_runtime_artifact_registry_builder_writes_registry(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-runtime-artifact-registry-"
        ) as temp_dir:
            registry_path = Path(temp_dir) / "optimizer-runtime-artifact-registry.json"
            result = self.build_runtime_artifact_registry(registry_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-runtime-artifact-registry.sample.v1",
            )
            self.assertEqual(payload["generatedFrom"]["bindingCount"], 4)
            self.assertEqual(payload["bindings"][0]["bindingId"], "optimizer_input_manifest")
            self.assertEqual(payload["bindings"][0]["artifactField"], "inputManifestPath")
            self.assertEqual(payload["bindings"][0]["runtimeSourceKind"], "input_manifest")
            self.assertEqual(
                payload["bindings"][0]["jobFamilyGroup"],
                "optimizer_input_jobs",
            )
            self.assertEqual(
                payload["bindings"][0]["materializationProfile"],
                "manifest_from_job_runs",
            )
            self.assertEqual(
                payload["bindings"][0]["materializationPlanId"],
                "optimizer_input_manifest_plan",
            )

    def test_optimizer_runtime_profile_catalog_builder_writes_catalog(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-runtime-profile-catalog-"
        ) as temp_dir:
            catalog_path = Path(temp_dir) / "optimizer-runtime-profile-catalog.json"
            result = self.build_runtime_profile_catalog(catalog_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-runtime-profile-catalog.sample.v1",
            )
            self.assertEqual(
                payload["catalogFamily"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(payload["catalogVersion"], "2026-04-15")
            self.assertEqual(payload["generatedFrom"]["profileCount"], 4)
            self.assertEqual(
                payload["profiles"][0]["profileId"],
                "optimizer_input_manifest_profile",
            )
            self.assertEqual(
                payload["profiles"][0]["bindingId"],
                "optimizer_input_manifest",
            )
            self.assertEqual(
                payload["profiles"][0]["jobFamilyGroup"],
                "optimizer_input_jobs",
            )
            self.assertEqual(
                payload["profiles"][0]["materializationProfile"],
                "manifest_from_job_runs",
            )
            self.assertNotIn("aliasProfileIds", payload["profiles"][0])

    def test_optimizer_runtime_profile_catalog_builder_writes_preview_catalog(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-runtime-profile-catalog-preview-"
        ) as temp_dir:
            catalog_path = Path(temp_dir) / "optimizer-runtime-profile-catalog.preview.json"
            result = self.build_runtime_profile_catalog(
                catalog_path,
                "--catalog-lane",
                "preview",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )
            self.assertEqual(
                payload["catalogFamily"],
                "autotiktok-runtime-profiles-preview",
            )
            self.assertEqual(payload["catalogVersion"], "2026-04-16-preview")
            self.assertEqual(
                payload["profiles"][0]["profileId"],
                "optimizer_input_manifest_profile_preview",
            )
            self.assertEqual(
                payload["profiles"][0]["aliasProfileIds"],
                ["optimizer_input_manifest_profile"],
            )

    def test_optimizer_runtime_profile_family_registry_builder_writes_registry(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-runtime-profile-family-registry-"
        ) as temp_dir:
            registry_path = (
                Path(temp_dir) / "optimizer-runtime-profile-family-registry.json"
            )
            result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-runtime-profile-family-registry.sample.v1",
            )
            self.assertEqual(
                payload["registryId"],
                "optimizer-runtime-profile-family-registry.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(payload["generatedFrom"]["familyCount"], 1)
            self.assertEqual(
                payload["families"][0]["familyId"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(payload["families"][0]["defaultLane"], "current")
            self.assertEqual(
                payload["families"][0]["supportedLanes"],
                ["current", "preview"],
            )
            self.assertEqual(
                payload["families"][0]["lanes"][1]["catalog"]["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )

    def test_optimizer_runtime_profile_rollout_policy_builder_writes_policy(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-runtime-profile-rollout-policy-"
        ) as temp_dir:
            policy_path = (
                Path(temp_dir) / "optimizer-runtime-profile-rollout-policy.json"
            )
            result = self.build_runtime_profile_rollout_policy(policy_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(policy_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-runtime-profile-rollout-policy.sample.v1",
            )
            self.assertEqual(
                payload["policyId"],
                "optimizer-runtime-profile-rollout-policy.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["runtimeProfileFamilyRegistryReference"]["registryId"],
                "optimizer-runtime-profile-family-registry.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(payload["generatedFrom"]["familyPolicyCount"], 1)
            self.assertEqual(
                payload["familyPolicies"][0]["familyId"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(payload["familyPolicies"][0]["activeLane"], "current")
            self.assertEqual(payload["familyPolicies"][0]["defaultLane"], "current")
            self.assertEqual(
                payload["familyPolicies"][0]["defaultRolloutClass"],
                "production",
            )
            self.assertEqual(
                payload["familyPolicies"][0]["allowedLanes"],
                ["current", "preview"],
            )
            self.assertEqual(
                payload["familyPolicies"][0]["rolloutClasses"],
                [
                    {"rolloutClass": "production", "selectedLane": "current"},
                    {
                        "rolloutClass": "preview_canary",
                        "selectedLane": "preview",
                    },
                ],
            )
            self.assertTrue(payload["familyPolicies"][0]["previewEnabled"])
            self.assertEqual(
                payload["plannerMetadataPolicies"],
                [
                    {
                        "metadataPolicyId": "standard_replay_metadata_policy",
                        "metadataContractFamilyId": "standard_replay_metadata_contract_family",
                        "metadataContractId": "standard_replay_metadata_contract",
                        "defaultWindowSetBatchType": "standard_replay",
                        "defaultComparisonDimension": "historyBatchLabel",
                        "windowSetBatchTypePriority": [
                            "purpose_template",
                            "purpose_template_family",
                            "metadata_policy_default",
                            "fallback_default",
                        ],
                        "comparisonDimensionPriority": [
                            "purpose_template",
                            "purpose_template_family",
                            "metadata_policy_default",
                            "fallback_default",
                        ],
                    },
                    {
                        "metadataPolicyId": "cross_profile_compare_metadata_policy",
                        "metadataContractFamilyId": "cross_profile_compare_metadata_contract_family",
                        "metadataContractId": "cross_profile_compare_metadata_contract",
                        "defaultWindowSetBatchType": "cross_profile_comparison",
                        "defaultComparisonDimension": "rankingProfileId",
                        "windowSetBatchTypePriority": [
                            "purpose_template",
                            "purpose_template_family",
                            "metadata_policy_default",
                            "fallback_default",
                        ],
                        "comparisonDimensionPriority": [
                            "purpose_template",
                            "purpose_template_family",
                            "metadata_policy_default",
                            "fallback_default",
                        ],
                    },
                ],
            )
            self.assertEqual(
                payload["plannerMetadataContractFamilies"],
                [
                    {
                        "metadataContractFamilyId": "standard_replay_metadata_contract_family",
                        "defaultMetadataContractId": "standard_replay_metadata_contract",
                        "allowedWindowSetBatchTypes": ["standard_replay"],
                        "allowedComparisonDimensions": [
                            "historyBatchLabel",
                            "historyWindowLabel",
                            "mode",
                            "evaluationWindow",
                        ],
                    },
                    {
                        "metadataContractFamilyId": "cross_profile_compare_metadata_contract_family",
                        "defaultMetadataContractId": "cross_profile_compare_metadata_contract",
                        "allowedWindowSetBatchTypes": ["cross_profile_comparison"],
                        "allowedComparisonDimensions": [
                            "rankingProfileId",
                            "rankingSnapshotId",
                        ],
                    },
                ],
            )
            self.assertEqual(
                payload["plannerMetadataContracts"],
                [
                    {
                        "metadataContractFamilyId": "standard_replay_metadata_contract_family",
                        "metadataContractId": "standard_replay_metadata_contract",
                        "allowedWindowSetBatchTypes": ["standard_replay"],
                        "allowedComparisonDimensions": [
                            "historyBatchLabel",
                            "historyWindowLabel",
                            "mode",
                            "evaluationWindow",
                        ],
                    },
                    {
                        "metadataContractFamilyId": "cross_profile_compare_metadata_contract_family",
                        "metadataContractId": "cross_profile_compare_metadata_contract",
                        "allowedWindowSetBatchTypes": ["cross_profile_comparison"],
                        "allowedComparisonDimensions": [
                            "rankingProfileId",
                            "rankingSnapshotId",
                        ],
                    },
                ],
            )
            self.assertEqual(
                payload["evalPurposeTemplateFamilies"],
                [
                    {
                        "templateFamilyId": "preview_validation_family",
                        "runtimeProfileFamilyId": "autotiktok-runtime-profiles",
                        "defaultRolloutClass": "preview_canary",
                        "plannerMetadataPolicyId": "standard_replay_metadata_policy",
                    },
                    {
                        "templateFamilyId": "cross_profile_validation_family",
                        "runtimeProfileFamilyId": "autotiktok-runtime-profiles",
                        "defaultRolloutClass": "preview_canary",
                        "plannerMetadataPolicyId": "cross_profile_compare_metadata_policy",
                    },
                ],
            )
            self.assertEqual(
                payload["evalPurposeTemplates"],
                [
                    {
                        "templateId": "preview_validation_template",
                        "templateFamilyId": "preview_validation_family",
                    },
                    {
                        "templateId": "profile_compare_validation_template",
                        "templateFamilyId": "cross_profile_validation_family",
                    },
                ],
            )
            self.assertEqual(
                payload["evalPurposePolicies"],
                [
                    {
                        "purposePolicyId": "preview_validation_default",
                        "windowSetPurpose": "preview_validation",
                        "templateId": "preview_validation_template",
                    },
                    {
                        "purposePolicyId": "profile_compare_validation_default",
                        "windowSetPurpose": "profile_compare_validation",
                        "templateId": "profile_compare_validation_template",
                    },
                ],
            )
            self.assertEqual(
                payload["rolloutClassRules"],
                [
                    {
                        "ruleId": "preview_batch_label",
                        "rolloutClass": "preview_canary",
                        "batchWindowLabelPrefix": "preview:",
                    },
                    {
                        "ruleId": "preview_weekly_shadow_rehearsal",
                        "rolloutClass": "preview_canary",
                        "windowSetPurpose": "weekly_shadow_rehearsal",
                        "historyWindowLabelPrefix": "historical_",
                        "mode": "daily_with_weekly_promotion",
                    },
                    {
                        "ruleId": "preview_scenario_prefix",
                        "rolloutClass": "preview_canary",
                        "scenarioLabelPrefix": "preview_",
                    },
                ],
            )

    def test_optimizer_runtime_materialization_plan_builder_writes_plan(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-runtime-materialization-plan-"
        ) as temp_dir:
            plan_path = Path(temp_dir) / "optimizer-runtime-materialization-plan.json"
            result = self.build_runtime_materialization_plan(plan_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-runtime-materialization-plan.sample.v1",
            )
            self.assertEqual(payload["generatedFrom"]["planCount"], 4)
            self.assertEqual(payload["plans"][0]["planId"], "optimizer_input_manifest_plan")
            self.assertEqual(
                payload["plans"][0]["jobFamilyGroup"],
                "optimizer_input_jobs",
            )
            self.assertEqual(
                payload["plans"][0]["materializationProfile"],
                "manifest_from_job_runs",
            )
            self.assertEqual(
                payload["plans"][0]["upstreamJobFamilies"],
                [
                    "topic_outcome_backfill",
                    "post_performance_signal",
                    "challenger_evaluation",
                ],
            )

    def test_optimizer_eval_run_builder_writes_eval_run(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-eval-run-") as temp_dir:
            eval_run_path = Path(temp_dir) / "optimizer-eval-run.json"
            result = self.build_eval_run(eval_run_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(eval_run_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-eval-run.v1")
            self.assertEqual(
                payload["generatedFrom"]["optimizerOfflineCycleSchemaVersion"],
                "optimizer-offline-cycle.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSources"]["backfills"]["jobKind"],
                "topic_outcome_backfill",
            )
            self.assertIn(
                payload["summary"]["weeklyDecision"],
                {"promote", "keep_champion", "rollback_champion"},
            )

    def test_daily_optimizer_job_builder_writes_job_run(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-daily-job-run-"
        ) as temp_dir:
            job_run_path = Path(temp_dir) / "optimizer-daily-job-run.json"
            result = self.build_daily_job_run(job_run_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(job_run_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-run.v1")
            self.assertEqual(payload["jobKind"], "daily_optimizer_job")
            self.assertEqual(payload["mode"], "daily_review_only")
            self.assertEqual(
                payload["generatedFrom"]["optimizerEvalRunSchemaVersion"],
                "optimizer-eval-run.v1",
            )
            self.assertIsNone(payload["summary"]["weeklyDecision"])

    def test_weekly_optimizer_job_builder_writes_job_run(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-weekly-job-run-"
        ) as temp_dir:
            job_run_path = Path(temp_dir) / "optimizer-weekly-job-run.json"
            result = self.build_weekly_job_run(job_run_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(job_run_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-run.v1")
            self.assertEqual(payload["jobKind"], "weekly_optimizer_job")
            self.assertEqual(payload["mode"], "daily_with_weekly_promotion")
            self.assertEqual(
                payload["generatedFrom"]["optimizerOfflineCycleSchemaVersion"],
                "optimizer-offline-cycle.v1",
            )
            self.assertIn(
                payload["summary"]["weeklyDecision"],
                {"promote", "keep_champion", "rollback_champion"},
            )

    def test_openclaw_cron_daily_optimizer_entrypoint_writes_summary_and_output(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-openclaw-cron-daily-"
        ) as temp_dir:
            output_root = Path(temp_dir) / "cron-output"
            job_run_id = "optimizer-daily-job-run.autotiktok.cron.test"
            result = self.build_openclaw_cron_daily_job(
                "--output-root",
                str(output_root),
                "--job-run-id",
                job_run_id,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output_path = output_root / f"{job_run_id}.json"
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-run.v1")
            self.assertEqual(payload["jobKind"], "daily_optimizer_job")
            self.assertIn("status=ok", result.stdout)
            self.assertIn(f"output={output_path}", result.stdout)
            self.assertIn(
                f"daily_recommendation={payload['summary']['dailyRecommendation']}",
                result.stdout,
            )

    def test_openclaw_cron_weekly_optimizer_entrypoint_writes_summary_and_output(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-openclaw-cron-weekly-"
        ) as temp_dir:
            output_path = Path(temp_dir) / "weekly-job-run.json"
            job_run_id = "optimizer-weekly-job-run.autotiktok.cron.test"
            result = self.build_openclaw_cron_weekly_job(
                "--output",
                str(output_path),
                "--job-run-id",
                job_run_id,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-run.v1")
            self.assertEqual(payload["jobKind"], "weekly_optimizer_job")
            self.assertIn("status=ok", result.stdout)
            self.assertIn(f"output={output_path}", result.stdout)
            self.assertIn(
                f"weekly_decision={payload['summary']['weeklyDecision']}",
                result.stdout,
            )

    def test_optimizer_openclaw_cron_contract_builder_writes_contract(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-openclaw-cron-contract-"
        ) as temp_dir:
            contract_path = Path(temp_dir) / "optimizer-openclaw-cron-contract.json"
            result = self.build_openclaw_cron_contract(contract_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-openclaw-cron-contract.sample.v1",
            )
            self.assertEqual(payload["summary"]["jobCount"], 2)
            self.assertTrue(payload["managementPolicy"]["requiresExplicitApproval"])
            self.assertEqual(
                payload["jobs"][0]["jobName"],
                "autotiktok:daily-optimizer",
            )
            self.assertEqual(
                payload["jobs"][1]["jobName"],
                "autotiktok:weekly-optimizer",
            )
            self.assertIn("openclaw cron add", payload["jobs"][0]["cliTemplates"]["add"])
            self.assertIn("<job-id>", payload["jobs"][1]["cliTemplates"]["edit"])

    def test_optimizer_job_schedule_builder_writes_plan(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-schedule-"
        ) as temp_dir:
            schedule_path = Path(temp_dir) / "optimizer-job-schedule.json"
            result = self.build_job_schedule(schedule_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(schedule_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-job-schedule.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["scheduleCount"], 2)
            self.assertEqual(payload["schedules"][0]["scheduleId"], "daily_optimizer_job")
            self.assertEqual(payload["schedules"][0]["defaultInputMode"], "manifest")
            self.assertEqual(
                payload["schedules"][1]["scheduleId"], "weekly_optimizer_job"
            )
            self.assertTrue(payload["schedules"][1]["includeWeeklyPromotion"])
            self.assertEqual(
                payload["schedules"][1]["defaultWeeklyReviewWindowPath"],
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-weekly-review-window.sample.json",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputRolloutPolicyId"],
                "optimizer-input-rollout-policy.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputRolloutPolicyFamily"],
                "autotiktok-optimizer-input-rollout",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputRolloutPolicyVersion"],
                "2026-04-18",
            )
            self.assertEqual(
                payload["generatedFrom"]["schedulerRolloutIntentCount"], 5
            )
            scheduler_rollout_intents = {
                entry["schedulerRolloutIntent"]: entry
                for entry in payload["schedulerRolloutIntents"]
            }
            self.assertEqual(
                scheduler_rollout_intents["production"]["inputRolloutIntent"],
                "production_run",
            )
            self.assertEqual(
                scheduler_rollout_intents["raw_shadow_validation"][
                    "inputRolloutClass"
                ],
                "raw_shadow_validation",
            )
            self.assertEqual(
                scheduler_rollout_intents["preview_validation"][
                    "runtimeProfileRolloutClass"
                ],
                "preview_canary",
            )
            self.assertEqual(
                scheduler_rollout_intents["profile_compare_validation"][
                    "comparisonDimension"
                ],
                "rankingProfileId",
            )
            self.assertEqual(
                payload["schedules"][0]["defaultSchedulerRolloutIntent"],
                "production",
            )
            self.assertEqual(
                payload["schedules"][0]["allowedSchedulerRolloutIntents"],
                [
                    "preview_validation",
                    "production",
                    "profile_compare_validation",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )
            self.assertEqual(
                payload["schedules"][0]["defaultRuntimeProfileRolloutClass"],
                "production",
            )
            self.assertIsNone(payload["schedules"][0]["defaultWindowSetPurpose"])
            self.assertIsNone(payload["schedules"][0]["defaultComparisonDimension"])
            self.assertEqual(
                payload["schedules"][0]["allowedRuntimeProfileRolloutClasses"],
                ["preview_canary", "production"],
            )
            self.assertEqual(
                payload["schedules"][0]["allowedWindowSetPurposes"],
                ["preview_validation", "profile_compare_validation"],
            )
            self.assertEqual(
                payload["schedules"][0]["allowedComparisonDimensions"],
                ["historyBatchLabel", "rankingProfileId"],
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputRolloutClass"], "production"
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputRolloutIntent"],
                "production_run",
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputRolloutSelectionSource"],
                "policy_schedule_default",
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputRolloutIntentSelectionSource"],
                "policy_schedule_default",
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputRolloutClassSelectionSource"],
                "mapped_from_schedule_rollout_intent_default",
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputSourceLane"],
                "sample_canonical",
            )
            self.assertEqual(
                payload["schedules"][0]["allowedInputRolloutIntents"],
                [
                    "production_run",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )
            self.assertEqual(
                payload["schedules"][0]["defaultInputSourceRegistryPath"],
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-source-registry.sample.json",
            )

    def test_optimizer_job_schedule_builder_writes_external_schedule_plan(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-schedule-external-"
        ) as temp_dir:
            schedule_path = Path(temp_dir) / "optimizer-job-schedule.external.json"
            result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(schedule_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-schedule.sample.v1")
            self.assertEqual(payload["scheduleProfile"], "external_scheduler")
            self.assertEqual(
                payload["defaultPathResolutionMode"], "scheduler_supplied"
            )
            self.assertEqual(payload["defaultOutputEmissionMode"], "output_root")
            self.assertEqual(
                payload["defaultOutputRoot"], "artifacts/optimizer-job-runs"
            )
            self.assertEqual(payload["defaultTriggerKind"], "cron")
            self.assertEqual(
                payload["defaultExecutionEnvironment"], "scheduler_managed"
            )
            self.assertEqual(payload["defaultSchedulerOwner"], "external_scheduler")
            self.assertEqual(payload["generatedFrom"]["scheduleCount"], 2)
            daily_schedule = payload["schedules"][0]
            weekly_schedule = payload["schedules"][1]
            self.assertEqual(daily_schedule["scheduleId"], "daily_optimizer_job")
            self.assertEqual(
                daily_schedule["pathResolutionMode"], "scheduler_supplied"
            )
            self.assertEqual(daily_schedule["outputEmissionMode"], "output_root")
            self.assertEqual(
                daily_schedule["defaultOutputRoot"], "artifacts/optimizer-job-runs"
            )
            self.assertEqual(daily_schedule["outputSubdir"], "daily_optimizer_job")
            self.assertIsNone(daily_schedule["defaultInputPath"])
            self.assertIsNone(daily_schedule["defaultPolicyPath"])
            self.assertIsNone(daily_schedule["defaultOutputPath"])
            self.assertIsNone(daily_schedule["defaultInputSourceRegistryPath"])
            self.assertEqual(
                daily_schedule["defaultSchedulerRolloutIntent"], "production"
            )
            self.assertEqual(
                daily_schedule["defaultInputRolloutIntent"], "production_run"
            )
            self.assertEqual(
                daily_schedule["defaultInputRolloutIntentSelectionSource"],
                "policy_schedule_default",
            )
            self.assertEqual(weekly_schedule["scheduleId"], "weekly_optimizer_job")
            self.assertEqual(
                weekly_schedule["pathResolutionMode"], "scheduler_supplied"
            )
            self.assertEqual(weekly_schedule["outputEmissionMode"], "output_root")
            self.assertEqual(weekly_schedule["outputSubdir"], "weekly_optimizer_job")
            self.assertIsNone(weekly_schedule["defaultInputPath"])
            self.assertIsNone(weekly_schedule["defaultPolicyPath"])
            self.assertIsNone(weekly_schedule["defaultOutputPath"])
            self.assertIsNone(weekly_schedule["defaultWeeklyReviewWindowPath"])
            self.assertIsNone(weekly_schedule["defaultInputSourceRegistryPath"])
            self.assertEqual(
                weekly_schedule["defaultSchedulerRolloutIntent"], "production"
            )
            self.assertEqual(
                weekly_schedule["allowedInputRolloutIntents"],
                [
                    "production_run",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )

    def test_optimizer_job_execution_context_builder_writes_context(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-execution-context-"
        ) as temp_dir:
            context_path = Path(temp_dir) / "optimizer-job-execution-context.json"
            result = self.build_job_execution_context(context_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(context_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-job-execution-context.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerJobSchedulePlanId"],
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                payload["defaultRunContext"]["artifactEmissionMode"], "inline_only"
            )
            self.assertTrue(payload["defaultRunContext"]["emitShadowCompare"])
            self.assertTrue(payload["defaultRunContext"]["emitCompareBatch"])
            self.assertTrue(payload["defaultRunContext"]["emitErrorArtifact"])
            self.assertEqual(
                payload["defaultInputs"]["inputManifestPath"],
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json",
            )
            self.assertEqual(len(payload["schedules"]), 2)
            self.assertEqual(
                payload["schedules"][0]["productionSchedulerRolloutIntent"],
                "production",
            )
            self.assertEqual(
                payload["schedules"][0]["shadowSchedulerRolloutIntent"],
                "raw_shadow_validation",
            )
            self.assertEqual(
                payload["schedules"][0]["shadowRolloutClass"],
                "raw_shadow_validation",
            )
            self.assertEqual(
                payload["schedules"][1]["productionSchedulerRolloutIntent"],
                "production",
            )
            self.assertEqual(
                payload["schedules"][1]["shadowSchedulerRolloutIntent"],
                "real_provider_shadow_validation",
            )
            self.assertEqual(
                payload["schedules"][1]["shadowRolloutClass"],
                "real_shadow_validation",
            )

    def test_optimizer_job_artifact_retention_policy_builder_writes_policy(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-artifact-retention-policy-"
        ) as temp_dir:
            policy_path = (
                Path(temp_dir) / "optimizer-job-artifact-retention-policy.json"
            )
            result = self.build_job_artifact_retention_policy(policy_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(policy_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-job-artifact-retention-policy.sample.v1",
            )
            self.assertEqual(
                payload["policyId"],
                "optimizer-job-artifact-retention-policy.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(payload["generatedFrom"]["artifactPolicyCount"], 11)
            policies = {
                entry["artifactKind"]: entry for entry in payload["artifactPolicies"]
            }
            self.assertEqual(policies["job_run"]["retentionTier"], "operational")
            self.assertEqual(policies["job_run"]["keepLatestCount"], 20)
            self.assertTrue(policies["job_run"]["keepFailureArtifacts"])
            self.assertEqual(
                policies["shadow_compare"]["partitionDimensions"],
                ["scheduleId", "candidateSchedulerRolloutIntent"],
            )
            self.assertEqual(
                policies["job_error"]["retentionTier"], "failure_audit"
            )

    def test_optimizer_job_error_builder_writes_triage_fields(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-error-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            error_path = temp_root / "optimizer-job-error.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            error_result = self.build_job_error_sample(
                error_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(error_result.returncode, 0, error_result.stderr)
            payload = json.loads(error_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-error.sample.v1")
            self.assertEqual(payload["errorCode"], "input_resolution_failure")
            self.assertEqual(payload["failureStage"], "input_resolution")
            self.assertFalse(payload["retryable"])
            self.assertEqual(payload["ownerHint"], "input_pipeline")
            self.assertEqual(
                payload["generatedFrom"]["optimizerJobScheduleProfile"],
                "external_scheduler",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerJobKind"],
                "weekly_optimizer_job",
            )

    def test_optimizer_input_rollout_policy_builder_writes_policy(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-input-rollout-policy-"
        ) as temp_dir:
            policy_path = Path(temp_dir) / "optimizer-input-rollout-policy.json"
            result = self.build_input_rollout_policy(policy_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(policy_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-input-rollout-policy.sample.v1"
            )
            self.assertEqual(payload["defaultRolloutIntent"], "production_run")
            self.assertEqual(payload["defaultRolloutClass"], "production")
            self.assertEqual(
                payload["rolloutSelectionPrecedence"],
                [
                    "explicit_rollout_class",
                    "explicit_rollout_intent",
                    "schedule_rollout_intent_default",
                    "global_rollout_intent_default",
                ],
            )
            rollout_classes = {
                entry["rolloutClass"]: entry["sourceLane"]
                for entry in payload["rolloutClasses"]
            }
            rollout_intents = {
                entry["rolloutIntent"]: entry["rolloutClass"]
                for entry in payload["rolloutIntents"]
            }
            self.assertEqual(rollout_classes["production"], "sample_canonical")
            self.assertEqual(
                rollout_classes["raw_shadow_validation"], "sample_raw_shadow"
            )
            self.assertEqual(
                rollout_classes["real_shadow_validation"], "real_provider_shadow"
            )
            self.assertEqual(rollout_intents["production_run"], "production")
            self.assertEqual(
                rollout_intents["raw_shadow_validation"], "raw_shadow_validation"
            )
            self.assertEqual(
                rollout_intents["real_provider_shadow_validation"],
                "real_shadow_validation",
            )

    def test_optimizer_input_rollout_policy_resolves_explicit_rollout_intent(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-input-rollout-policy-resolve-"
        ) as temp_dir:
            policy_path = Path(temp_dir) / "optimizer-input-rollout-policy.json"
            result = self.build_input_rollout_policy(policy_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(policy_path.read_text(encoding="utf-8"))
            selection = resolve_optimizer_input_rollout_selection(
                payload,
                schedule_id="weekly_optimizer_job",
                explicit_rollout_intent="real_provider_shadow_validation",
            )
            self.assertEqual(selection["rolloutIntent"], "real_provider_shadow_validation")
            self.assertEqual(selection["rolloutClass"], "real_shadow_validation")
            self.assertEqual(selection["sourceLane"], "real_provider_shadow")
            self.assertEqual(selection["selectionSource"], "explicit")
            self.assertEqual(
                selection["rolloutIntentSelectionSource"],
                "explicit_rollout_intent",
            )
            self.assertEqual(
                selection["rolloutClassSelectionSource"],
                "mapped_from_explicit_rollout_intent",
            )

    def test_optimizer_job_schedule_resolves_scheduler_rollout_intent(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-schedule-resolve-"
        ) as temp_dir:
            schedule_path = Path(temp_dir) / "optimizer-job-schedule.json"
            result = self.build_job_schedule(schedule_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(schedule_path.read_text(encoding="utf-8"))
            default_selection = resolve_optimizer_job_scheduler_rollout_intent(
                payload, schedule_id="daily_optimizer_job"
            )
            self.assertEqual(
                default_selection["schedulerRolloutIntent"], "production"
            )
            self.assertEqual(default_selection["selectionSource"], "schedule_default")
            explicit_selection = resolve_optimizer_job_scheduler_rollout_intent(
                payload,
                schedule_id="weekly_optimizer_job",
                explicit_scheduler_rollout_intent="real_provider_shadow_validation",
            )
            self.assertEqual(
                explicit_selection["inputRolloutClass"], "real_shadow_validation"
            )
            self.assertEqual(
                explicit_selection["selectionSource"],
                "explicit_scheduler_intent",
            )
            mapped_selection = resolve_optimizer_job_scheduler_rollout_intent(
                payload,
                schedule_id="daily_optimizer_job",
                explicit_rollout_class="raw_shadow_validation",
            )
            self.assertEqual(
                mapped_selection["schedulerRolloutIntent"], "raw_shadow_validation"
            )
            self.assertEqual(
                mapped_selection["selectionSource"],
                "mapped_from_explicit_rollout_class",
            )

    def test_optimizer_job_schedule_resolves_execution_policy(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-schedule-execution-policy-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            policy_result = self.build_input_rollout_policy(rollout_policy_path)
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            schedule_payload = json.loads(schedule_path.read_text(encoding="utf-8"))
            rollout_policy_payload = json.loads(
                rollout_policy_path.read_text(encoding="utf-8")
            )
            preview_selection = resolve_optimizer_job_schedule_execution_policy(
                schedule_payload,
                input_rollout_policy_payload=rollout_policy_payload,
                schedule_id="daily_optimizer_job",
                explicit_scheduler_rollout_intent="preview_validation",
            )
            self.assertEqual(
                preview_selection["schedulerRolloutIntent"], "preview_validation"
            )
            self.assertEqual(preview_selection["inputRolloutClass"], "production")
            self.assertEqual(preview_selection["sourceLane"], "sample_canonical")
            self.assertEqual(
                preview_selection["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertEqual(
                preview_selection["windowSetPurpose"], "preview_validation"
            )
            self.assertEqual(
                preview_selection["comparisonDimension"], "historyBatchLabel"
            )
            self.assertEqual(
                preview_selection["selectionSource"], "explicit_scheduler_intent"
            )
            mapped_selection = resolve_optimizer_job_schedule_execution_policy(
                schedule_payload,
                input_rollout_policy_payload=rollout_policy_payload,
                schedule_id="weekly_optimizer_job",
                explicit_rollout_class="real_shadow_validation",
            )
            self.assertEqual(
                mapped_selection["schedulerRolloutIntent"],
                "real_provider_shadow_validation",
            )
            self.assertEqual(
                mapped_selection["inputRolloutClass"], "real_shadow_validation"
            )
            self.assertEqual(
                mapped_selection["sourceLane"], "real_provider_shadow"
            )
            self.assertEqual(
                mapped_selection["runtimeProfileRolloutClass"], "production"
            )
            self.assertEqual(
                mapped_selection["selectionSource"],
                "mapped_from_explicit_rollout_class",
            )

    def test_scheduled_optimizer_job_runner_matches_daily_job(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-scheduled-optimizer-daily-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            output_path = temp_root / "optimizer-daily-job-run.json"
            schedule_result = self.build_job_schedule(schedule_path)
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            result = self.run_scheduled_job(
                output_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-run.v1")
            self.assertEqual(payload["jobKind"], "daily_optimizer_job")
            self.assertEqual(payload["mode"], "daily_review_only")

    def test_scheduled_optimizer_job_runner_supports_external_schedule_output_root(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-scheduled-optimizer-external-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            output_root = temp_root / "scheduled-outputs"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)

            daily_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py",
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--input-manifest",
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json",
                "--policy",
                "skills/autotiktok-strategy-optimizer/config/optimizer-policy.v1.json",
                "--output-root",
                str(output_root),
                "--scheduler-run-id",
                "cron.daily.2026-04-18",
                "--scheduler-trigger-kind",
                "cron",
                "--scheduler-owner",
                "external_scheduler",
                "--execution-environment",
                "scheduler_managed",
            )
            self.assertEqual(daily_result.returncode, 0, daily_result.stderr)
            daily_output = (
                output_root
                / "daily_optimizer_job"
                / "optimizer-daily-job-run.autotiktok.fixture.2026-04-18.json"
            )
            self.assertTrue(daily_output.exists())
            daily_payload = json.loads(daily_output.read_text(encoding="utf-8"))
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobScheduleProfile"],
                "external_scheduler",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobPathResolutionMode"],
                "scheduler_supplied",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobOutputEmissionMode"],
                "output_root",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobOutputRoot"],
                str(output_root),
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobSchedulerRunId"],
                "cron.daily.2026-04-18",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobTriggerKind"], "cron"
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobSchedulerOwner"],
                "external_scheduler",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerJobExecutionEnvironment"],
                "scheduler_managed",
            )

            weekly_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py",
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
                "--input-manifest",
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json",
                "--policy",
                "skills/autotiktok-strategy-optimizer/config/optimizer-policy.v1.json",
                "--weekly-review-window-input",
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-weekly-review-window.sample.json",
                "--output-root",
                str(output_root),
                "--scheduler-run-id",
                "planner.weekly.2026-04-18",
                "--scheduler-trigger-kind",
                "planner",
                "--scheduler-owner",
                "external_scheduler",
                "--execution-environment",
                "scheduler_managed",
            )
            self.assertEqual(weekly_result.returncode, 0, weekly_result.stderr)
            weekly_output = (
                output_root
                / "weekly_optimizer_job"
                / "optimizer-weekly-job-run.autotiktok.fixture.2026-04-18.json"
            )
            self.assertTrue(weekly_output.exists())
            weekly_payload = json.loads(weekly_output.read_text(encoding="utf-8"))
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobScheduleProfile"],
                "external_scheduler",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobPathResolutionMode"],
                "scheduler_supplied",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobOutputEmissionMode"],
                "output_root",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobOutputRoot"],
                str(output_root),
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobSchedulerRunId"],
                "planner.weekly.2026-04-18",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobTriggerKind"],
                "planner",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobSchedulerOwner"],
                "external_scheduler",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["optimizerJobExecutionEnvironment"],
                "scheduler_managed",
            )

    def test_scheduled_optimizer_job_runner_writes_error_artifact(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-scheduled-optimizer-error-artifact-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            error_path = temp_root / "optimizer-job.error.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py",
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--input-manifest",
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json",
                "--scheduler-run-id",
                "cron.daily.error.2026-04-19",
                "--scheduler-trigger-kind",
                "cron",
                "--scheduler-owner",
                "external_scheduler",
                "--execution-environment",
                "scheduler_managed",
                "--execution-context-id",
                "optimizer-job-execution-context.autotiktok.fixture.2026-04-19",
                "--artifact-emission-mode",
                "inline_only",
                "--error-output",
                str(error_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(error_path.exists())
            error_payload = json.loads(error_path.read_text(encoding="utf-8"))
            self.assertEqual(
                error_payload["schemaVersion"], "optimizer-job-error.sample.v1"
            )
            self.assertEqual(error_payload["errorCode"], "input_resolution_failure")
            self.assertEqual(error_payload["failureStage"], "input_resolution")
            self.assertFalse(error_payload["retryable"])
            self.assertEqual(error_payload["ownerHint"], "input_pipeline")
            self.assertEqual(
                error_payload["generatedFrom"]["optimizerJobExecutionContextId"],
                "optimizer-job-execution-context.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(
                error_payload["generatedFrom"]["optimizerJobSchedulerRunId"],
                "cron.daily.error.2026-04-19",
            )
            self.assertEqual(
                error_payload["generatedFrom"]["optimizerJobScheduleProfile"],
                "external_scheduler",
            )
            self.assertEqual(
                error_payload["generatedFrom"]["optimizerJobKind"],
                "daily_optimizer_job",
            )
            self.assertEqual(
                error_payload["failureSummary"],
                "scheduled optimizer job could not resolve required runtime inputs",
            )

    def test_scheduled_optimizer_job_runner_accepts_raw_shadow_rollout(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-scheduled-optimizer-daily-raw-shadow-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            production_output = temp_root / "optimizer-daily-job-run.production.json"
            shadow_output = temp_root / "optimizer-daily-job-run.raw-shadow.json"
            policy_result = self.build_input_rollout_policy(rollout_policy_path)
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            production_result = self.run_scheduled_job(
                production_output,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
            )
            self.assertEqual(
                production_result.returncode, 0, production_result.stderr
            )
            shadow_result = self.run_scheduled_job(
                shadow_output,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "daily_optimizer_job",
                "--input-rollout-class",
                "raw_shadow_validation",
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(shadow_result.returncode, 0, shadow_result.stderr)
            production_payload = json.loads(
                production_output.read_text(encoding="utf-8")
            )
            shadow_payload = json.loads(shadow_output.read_text(encoding="utf-8"))
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputSourceLane"],
                "sample_raw_shadow",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputRolloutClass"],
                "raw_shadow_validation",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputLaneSelectionSource"],
                "explicit",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerJobSchedulerRolloutIntent"],
                "raw_shadow_validation",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"][
                    "optimizerJobSchedulerRolloutIntentSelectionSource"
                ],
                "mapped_from_explicit_rollout_class",
            )
            self.assertEqual(
                shadow_payload["summary"]["dailyRecommendation"],
                production_payload["summary"]["dailyRecommendation"],
            )
            self.assertEqual(
                shadow_payload["summary"]["shadowLeaderProfileId"],
                production_payload["summary"]["shadowLeaderProfileId"],
            )

    def test_scheduled_optimizer_job_runner_matches_weekly_job(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-scheduled-optimizer-weekly-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            output_path = temp_root / "optimizer-weekly-job-run.json"
            schedule_result = self.build_job_schedule(schedule_path)
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            result = self.run_scheduled_job(
                output_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-job-run.v1")
            self.assertEqual(payload["jobKind"], "weekly_optimizer_job")
            self.assertEqual(payload["mode"], "daily_with_weekly_promotion")
            self.assertIn(
                payload["summary"]["weeklyDecision"],
                {"promote", "keep_champion", "rollback_champion"},
            )

    def test_scheduled_optimizer_job_runner_accepts_real_shadow_rollout(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-scheduled-optimizer-weekly-real-shadow-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            production_output = temp_root / "optimizer-weekly-job-run.production.json"
            shadow_output = temp_root / "optimizer-weekly-job-run.real-shadow.json"
            policy_result = self.build_input_rollout_policy(rollout_policy_path)
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            production_result = self.run_scheduled_job(
                production_output,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
            )
            self.assertEqual(
                production_result.returncode, 0, production_result.stderr
            )
            shadow_result = self.run_scheduled_job(
                shadow_output,
                "--input-schedule-plan",
                str(schedule_path),
                "--schedule-id",
                "weekly_optimizer_job",
                "--input-rollout-class",
                "real_shadow_validation",
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(shadow_result.returncode, 0, shadow_result.stderr)
            production_payload = json.loads(
                production_output.read_text(encoding="utf-8")
            )
            shadow_payload = json.loads(shadow_output.read_text(encoding="utf-8"))
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputSourceLane"],
                "real_provider_shadow",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputRolloutClass"],
                "real_shadow_validation",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputLaneSelectionSource"],
                "explicit",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerJobSchedulerRolloutIntent"],
                "real_provider_shadow_validation",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerJobRuntimeProfileRolloutClass"],
                "production",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputSourceProviderClass"],
                "artifact_catalog_service",
            )
            self.assertEqual(
                shadow_payload["generatedFrom"]["optimizerInputArtifactLocatorKind"],
                "provider_locator",
            )
            self.assertEqual(
                shadow_payload["summary"]["weeklyDecision"],
                production_payload["summary"]["weeklyDecision"],
            )
            self.assertEqual(
                shadow_payload["summary"]["selectedChallengerProfileId"],
                production_payload["summary"]["selectedChallengerProfileId"],
            )

    def test_optimizer_job_shadow_compare_builder_writes_compare(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-shadow-compare-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            compare_plan_path = temp_root / "optimizer-job-shadow-compare-plan.json"
            compare_path = temp_root / "optimizer-job-shadow-compare.json"
            policy_result = self.build_input_rollout_policy(rollout_policy_path)
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            compare_plan_result = self.build_job_shadow_compare_plan(
                compare_plan_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(
                compare_plan_result.returncode, 0, compare_plan_result.stderr
            )
            compare_plan_payload = json.loads(
                compare_plan_path.read_text(encoding="utf-8")
            )
            self.assertEqual(
                compare_plan_payload["schemaVersion"],
                "optimizer-job-shadow-compare-plan.sample.v1",
            )
            self.assertEqual(len(compare_plan_payload["comparisons"]), 4)
            self.assertEqual(
                [entry["comparisonId"] for entry in compare_plan_payload["comparisons"]],
                [
                    "daily_raw_shadow_vs_production",
                    "weekly_real_shadow_vs_production",
                    "daily_preview_validation_vs_production",
                    "daily_profile_compare_validation_vs_production",
                ],
            )
            compare_result = self.build_job_shadow_compare(
                compare_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(compare_plan_path),
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            payload = json.loads(compare_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-job-shadow-compare.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerJobShadowComparePlanId"],
                "optimizer-job-shadow-compare-plan.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(payload["summary"]["comparisonCount"], 4)
            self.assertEqual(payload["summary"]["matchedComparisonCount"], 4)
            self.assertEqual(
                payload["summary"]["comparedScheduleIds"],
                ["daily_optimizer_job", "weekly_optimizer_job"],
            )
            self.assertEqual(
                payload["summary"]["comparedSchedulerRolloutIntents"],
                [
                    "preview_validation",
                    "production",
                    "profile_compare_validation",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )
            self.assertEqual(
                payload["summary"]["comparedRolloutClasses"],
                [
                    "production",
                    "raw_shadow_validation",
                    "real_shadow_validation",
                ],
            )
            self.assertEqual(
                payload["summary"]["comparedRuntimeProfileRolloutClasses"],
                ["preview_canary", "production"],
            )
            self.assertEqual(
                payload["summary"]["comparedWindowSetPurposes"],
                ["preview_validation", "profile_compare_validation"],
            )
            self.assertEqual(
                payload["summary"]["comparedComparisonDimensions"],
                ["historyBatchLabel", "rankingProfileId"],
            )
            comparisons = {
                entry["comparisonId"]: entry for entry in payload["comparisons"]
            }
            self.assertEqual(
                comparisons["daily_raw_shadow_vs_production"]["candidate"][
                    "schedulerRolloutIntent"
                ],
                "raw_shadow_validation",
            )
            self.assertEqual(
                comparisons["daily_raw_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceLane"],
                "sample_raw_shadow",
            )
            self.assertIsNone(
                comparisons["daily_raw_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceProviderRegistryId"]
            )
            self.assertIsNone(
                comparisons["daily_raw_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceArtifactCatalogId"]
            )
            self.assertEqual(
                comparisons["weekly_real_shadow_vs_production"]["candidate"][
                    "schedulerRolloutIntent"
                ],
                "real_provider_shadow_validation",
            )
            self.assertEqual(
                comparisons["weekly_real_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceLane"],
                "real_provider_shadow",
            )
            self.assertEqual(
                comparisons["weekly_real_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceProviderRegistryId"],
                "optimizer-source-provider-registry.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                comparisons["weekly_real_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceArtifactCatalogId"],
                "optimizer-source-artifact-catalog.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                comparisons["weekly_real_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputSourceProviderClass"],
                "artifact_catalog_service",
            )
            self.assertEqual(
                comparisons["weekly_real_shadow_vs_production"]["candidate"][
                    "inputProvenance"
                ]["optimizerInputArtifactLocatorKind"],
                "provider_locator",
            )
            self.assertEqual(
                comparisons["daily_preview_validation_vs_production"]["baseline"][
                    "schedulerRolloutIntent"
                ],
                "production",
            )
            self.assertEqual(
                comparisons["daily_preview_validation_vs_production"]["candidate"][
                    "schedulerRolloutIntent"
                ],
                "preview_validation",
            )
            self.assertEqual(
                comparisons["daily_preview_validation_vs_production"]["candidate"][
                    "runtimeProfileRolloutClass"
                ],
                "preview_canary",
            )
            self.assertEqual(
                comparisons["daily_preview_validation_vs_production"]["candidate"][
                    "windowSetPurpose"
                ],
                "preview_validation",
            )
            self.assertEqual(
                comparisons["daily_preview_validation_vs_production"]["candidate"][
                    "comparisonDimension"
                ],
                "historyBatchLabel",
            )
            self.assertEqual(
                comparisons["daily_profile_compare_validation_vs_production"][
                    "candidate"
                ]["schedulerRolloutIntent"],
                "profile_compare_validation",
            )
            self.assertEqual(
                comparisons["daily_profile_compare_validation_vs_production"][
                    "candidate"
                ]["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertEqual(
                comparisons["daily_profile_compare_validation_vs_production"][
                    "candidate"
                ]["windowSetPurpose"],
                "profile_compare_validation",
            )
            self.assertEqual(
                comparisons["daily_profile_compare_validation_vs_production"][
                    "candidate"
                ]["comparisonDimension"],
                "rankingProfileId",
            )

    def test_optimizer_job_orchestration_cycle_runner_writes_cycle(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-orchestration-cycle-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            run_summary_path = temp_root / "optimizer-run-summary.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
                "--run-summary-output",
                str(run_summary_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            run_summary = json.loads(run_summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-job-orchestration-cycle.sample.v1",
            )
            self.assertEqual(payload["summary"]["executedScheduleCount"], 2)
            self.assertEqual(payload["summary"]["jobRunCount"], 4)
            self.assertEqual(payload["summary"]["shadowComparedScheduleCount"], 2)
            self.assertEqual(payload["summary"]["compareArtifactCount"], 1)
            self.assertEqual(payload["summary"]["compareBatchCount"], 1)
            self.assertEqual(payload["summary"]["errorCount"], 0)
            self.assertEqual(
                payload["generatedFrom"]["optimizerJobExecutionContextId"],
                "optimizer-job-execution-context.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(
                payload["generatedFrom"][
                    "optimizerJobArtifactRetentionPolicyId"
                ],
                "optimizer-job-artifact-retention-policy.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(
                payload["artifacts"]["jobRuns"][0]["generatedFrom"][
                    "optimizerJobExecutionContextId"
                ],
                "optimizer-job-execution-context.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(
                payload["artifacts"]["jobRuns"][1]["schedulerRolloutIntent"],
                "raw_shadow_validation",
            )
            self.assertEqual(
                payload["artifacts"]["shadowCompare"]["summary"][
                    "comparedSourceLanes"
                ],
                ["real_provider_shadow", "sample_raw_shadow"],
            )
            self.assertEqual(
                payload["artifacts"]["shadowCompare"]["summary"][
                    "comparedSchedulerRolloutIntents"
                ],
                [
                    "production",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )
            self.assertEqual(
                payload["artifacts"]["shadowCompare"]["summary"][
                    "comparedRuntimeProfileRolloutClasses"
                ],
                ["production"],
            )
            self.assertEqual(
                payload["artifacts"]["shadowCompareBatch"]["summary"][
                    "comparisonCount"
                ],
                2,
            )
            self.assertEqual(
                payload["summary"]["retentionPolicyId"],
                "optimizer-job-artifact-retention-policy.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(
                payload["summary"]["retentionManagedArtifactKinds"],
                [
                    "input_bundle",
                    "input_manifest",
                    "job_error",
                    "job_run",
                    "orchestration_cycle",
                    "recent_compare_summaries",
                    "recent_failure_summaries",
                    "recent_run_summaries",
                    "recent_weekly_decisions",
                    "shadow_compare",
                    "shadow_compare_batch",
                ],
            )
            self.assertEqual(
                payload["summary"]["retentionManagedArtifactCount"],
                11,
            )
            self.assertEqual(
                payload["artifacts"]["runSummary"]["schemaVersion"],
                "optimizer-run-summary.sample.v1",
            )
            self.assertEqual(
                payload["artifacts"]["runSummary"]["runSummaryId"],
                "optimizer-run-summary.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(
                payload["artifacts"]["runSummary"]["summary"]["runStatus"],
                "success",
            )
            self.assertEqual(
                payload["artifacts"]["runSummary"]["summary"]["jobRunCount"],
                4,
            )
            self.assertEqual(
                run_summary,
                payload["artifacts"]["runSummary"],
            )
            self.assertEqual(
                payload["artifacts"]["retentionPolicy"]["schemaVersion"],
                "optimizer-job-artifact-retention-policy.sample.v1",
            )

    def test_optimizer_job_orchestration_cycle_runner_collects_schedule_errors(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-orchestration-cycle-error-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            run_summary_path = temp_root / "optimizer-run-summary.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            execution_context = json.loads(
                execution_context_path.read_text(encoding="utf-8")
            )
            execution_context["defaultInputs"][
                "weeklyReviewWindowPath"
            ] = "skills/autotiktok-strategy-optimizer/fixtures/missing-weekly-review-window.sample.json"
            execution_context_path.write_text(
                json.dumps(execution_context, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
                "--run-summary-output",
                str(run_summary_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            run_summary = json.loads(run_summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["errorCount"], 1)
            self.assertEqual(len(payload["artifacts"]["errors"]), 1)
            self.assertEqual(
                payload["artifacts"]["errors"][0]["errorCode"],
                "input_resolution_failure",
            )
            self.assertEqual(
                payload["artifacts"]["errors"][0]["generatedFrom"][
                    "optimizerJobKind"
                ],
                "weekly_optimizer_job",
            )
            self.assertEqual(run_summary["summary"]["runStatus"], "partial_failure")
            self.assertEqual(run_summary["summary"]["successfulScheduleCount"], 1)
            self.assertEqual(run_summary["summary"]["failedScheduleCount"], 1)
            self.assertEqual(len(run_summary["errorSummaries"]), 1)
            self.assertEqual(
                run_summary["errorSummaries"][0]["ownerHint"],
                "input_pipeline",
            )

    def test_optimizer_run_summary_builder_writes_summary(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-run-summary-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            run_summary_path = temp_root / "optimizer-run-summary.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            summary_result = self.build_run_summary(
                run_summary_path,
                "--input-job-orchestration-cycle",
                str(cycle_path),
            )
            self.assertEqual(summary_result.returncode, 0, summary_result.stderr)
            payload = json.loads(run_summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-run-summary.sample.v1")
            self.assertEqual(
                payload["generatedFrom"]["optimizerJobOrchestrationCycleId"],
                "optimizer-job-orchestration-cycle.autotiktok.fixture.2026-04-19",
            )
            self.assertEqual(payload["summary"]["scheduleCount"], 2)
            self.assertEqual(payload["summary"]["productionJobRunCount"], 2)
            self.assertEqual(payload["summary"]["shadowJobRunCount"], 2)
            self.assertEqual(payload["summary"]["compareArtifactCount"], 1)
            self.assertEqual(payload["summary"]["compareBatchCount"], 1)
            self.assertEqual(len(payload["scheduleSummaries"]), 2)

    def test_optimizer_recent_run_summaries_builder_writes_aggregate(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-recent-run-summaries-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            aggregate_path = temp_root / "optimizer-recent-run-summaries.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            aggregate_result = self.build_recent_run_summaries(
                aggregate_path,
                "--input-job-orchestration-cycle",
                str(cycle_path),
            )
            self.assertEqual(aggregate_result.returncode, 0, aggregate_result.stderr)
            payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-recent-run-summaries.sample.v1",
            )
            self.assertEqual(payload["summary"]["runSummaryCount"], 1)
            self.assertEqual(payload["summary"]["jobRunCount"], 4)
            self.assertEqual(payload["summary"]["errorCount"], 0)

    def test_optimizer_recent_weekly_decisions_builder_writes_aggregate(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-recent-weekly-decisions-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            aggregate_path = temp_root / "optimizer-recent-weekly-decisions.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            aggregate_result = self.build_recent_weekly_decisions(
                aggregate_path,
                "--input-job-orchestration-cycle",
                str(cycle_path),
            )
            self.assertEqual(aggregate_result.returncode, 0, aggregate_result.stderr)
            payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-recent-weekly-decisions.sample.v1",
            )
            self.assertEqual(payload["summary"]["weeklyDecisionCount"], 2)
            self.assertEqual(payload["summary"]["decisionCounts"], {"promote": 2})

    def test_optimizer_job_shadow_compare_batch_builder_writes_batch(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-job-shadow-compare-batch-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.json"
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            daily_plan_path = (
                temp_root / "optimizer-job-shadow-compare-plan.daily.json"
            )
            weekly_plan_path = (
                temp_root / "optimizer-job-shadow-compare-plan.weekly.json"
            )
            daily_compare_path = temp_root / "optimizer-job-shadow-compare.daily.json"
            weekly_compare_path = (
                temp_root / "optimizer-job-shadow-compare.weekly.json"
            )
            batch_manifest_path = (
                temp_root / "optimizer-job-shadow-compare-batch-manifest.json"
            )
            batch_path = temp_root / "optimizer-job-shadow-compare-batch.json"

            policy_result = self.build_input_rollout_policy(rollout_policy_path)
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            daily_plan_result = self.build_job_shadow_compare_plan(
                daily_plan_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "daily",
                "--compare-plan-id",
                "optimizer-job-shadow-compare-plan.daily.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:41:00Z",
            )
            self.assertEqual(daily_plan_result.returncode, 0, daily_plan_result.stderr)
            weekly_plan_result = self.build_job_shadow_compare_plan(
                weekly_plan_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "weekly",
                "--compare-plan-id",
                "optimizer-job-shadow-compare-plan.weekly.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:42:00Z",
            )
            self.assertEqual(
                weekly_plan_result.returncode, 0, weekly_plan_result.stderr
            )
            daily_compare_result = self.build_job_shadow_compare(
                daily_compare_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(daily_plan_path),
                "--compare-id",
                "optimizer-job-shadow-compare.daily.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:46:00Z",
            )
            self.assertEqual(
                daily_compare_result.returncode, 0, daily_compare_result.stderr
            )
            weekly_compare_result = self.build_job_shadow_compare(
                weekly_compare_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(weekly_plan_path),
                "--compare-id",
                "optimizer-job-shadow-compare.weekly.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:47:00Z",
            )
            self.assertEqual(
                weekly_compare_result.returncode, 0, weekly_compare_result.stderr
            )
            batch_manifest_result = self.build_job_shadow_compare_batch_manifest(
                batch_manifest_path,
                "--input-compare-artifact",
                str(daily_compare_path),
                "--input-compare-artifact",
                str(weekly_compare_path),
            )
            self.assertEqual(
                batch_manifest_result.returncode, 0, batch_manifest_result.stderr
            )
            batch_manifest_payload = json.loads(
                batch_manifest_path.read_text(encoding="utf-8")
            )
            self.assertEqual(
                batch_manifest_payload["schemaVersion"],
                "optimizer-job-shadow-compare-batch-manifest.sample.v1",
            )
            self.assertEqual(
                batch_manifest_payload["comparisonDimension"],
                "candidateSchedulerRolloutIntent",
            )
            self.assertEqual(
                batch_manifest_payload["generatedFrom"]["compareArtifactCount"], 2
            )
            batch_result = self.build_job_shadow_compare_batch(
                batch_path,
                "--input-batch-manifest",
                str(batch_manifest_path),
            )
            self.assertEqual(batch_result.returncode, 0, batch_result.stderr)
            payload = json.loads(batch_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-job-shadow-compare-batch.sample.v1"
            )
            self.assertEqual(payload["summary"]["compareArtifactCount"], 2)
            self.assertEqual(payload["summary"]["comparisonCount"], 4)
            self.assertEqual(payload["summary"]["matchedComparisonCount"], 4)
            self.assertEqual(
                payload["summary"]["comparedScheduleIds"],
                ["daily_optimizer_job", "weekly_optimizer_job"],
            )
            self.assertEqual(
                payload["summary"]["comparedCandidateRolloutClasses"],
                ["production", "raw_shadow_validation", "real_shadow_validation"],
            )
            self.assertEqual(
                payload["summary"]["comparedCandidateSchedulerRolloutIntents"],
                [
                    "preview_validation",
                    "profile_compare_validation",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )
            self.assertEqual(
                payload["summary"]["comparedCandidateRuntimeProfileRolloutClasses"],
                ["preview_canary", "production"],
            )
            self.assertEqual(
                payload["summary"]["comparedCandidateWindowSetPurposes"],
                ["preview_validation", "profile_compare_validation"],
            )
            self.assertEqual(
                payload["summary"]["comparedCandidateComparisonDimensions"],
                ["historyBatchLabel", "rankingProfileId"],
            )
            self.assertEqual(
                payload["summary"]["comparedCandidateSourceLanes"],
                ["real_provider_shadow", "sample_canonical", "sample_raw_shadow"],
            )
            self.assertEqual(len(payload["groupSummaries"]), 4)
            self.assertEqual(
                [item["groupValue"] for item in payload["groupSummaries"]],
                [
                    "preview_validation",
                    "profile_compare_validation",
                    "raw_shadow_validation",
                    "real_provider_shadow_validation",
                ],
            )

    def test_optimizer_recent_compare_summaries_builder_writes_aggregate(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-recent-compare-summaries-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            rollout_policy_path = temp_root / "optimizer-input-rollout-policy.json"
            replay_schedule_path = temp_root / "optimizer-job-schedule.json"
            external_schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            daily_plan_path = (
                temp_root / "optimizer-job-shadow-compare-plan.daily.json"
            )
            weekly_plan_path = (
                temp_root / "optimizer-job-shadow-compare-plan.weekly.json"
            )
            daily_compare_path = temp_root / "optimizer-job-shadow-compare.daily.json"
            weekly_compare_path = (
                temp_root / "optimizer-job-shadow-compare.weekly.json"
            )
            batch_manifest_path = (
                temp_root / "optimizer-job-shadow-compare-batch-manifest.json"
            )
            batch_path = temp_root / "optimizer-job-shadow-compare-batch.json"
            aggregate_path = temp_root / "optimizer-recent-compare-summaries.json"

            policy_result = self.build_input_rollout_policy(rollout_policy_path)
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            schedule_result = self.build_job_schedule(
                replay_schedule_path,
                "--input-rollout-policy",
                str(rollout_policy_path),
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            external_schedule_result = self.build_job_schedule(
                external_schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(
                external_schedule_result.returncode,
                0,
                external_schedule_result.stderr,
            )
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(external_schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(external_schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            daily_plan_result = self.build_job_shadow_compare_plan(
                daily_plan_path,
                "--input-schedule-plan",
                str(replay_schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "daily",
                "--compare-plan-id",
                "optimizer-job-shadow-compare-plan.daily.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:41:00Z",
            )
            self.assertEqual(daily_plan_result.returncode, 0, daily_plan_result.stderr)
            weekly_plan_result = self.build_job_shadow_compare_plan(
                weekly_plan_path,
                "--input-schedule-plan",
                str(replay_schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--comparison-scope",
                "weekly",
                "--compare-plan-id",
                "optimizer-job-shadow-compare-plan.weekly.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:42:00Z",
            )
            self.assertEqual(
                weekly_plan_result.returncode, 0, weekly_plan_result.stderr
            )
            daily_compare_result = self.build_job_shadow_compare(
                daily_compare_path,
                "--input-schedule-plan",
                str(replay_schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(daily_plan_path),
                "--compare-id",
                "optimizer-job-shadow-compare.daily.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:46:00Z",
            )
            self.assertEqual(
                daily_compare_result.returncode, 0, daily_compare_result.stderr
            )
            weekly_compare_result = self.build_job_shadow_compare(
                weekly_compare_path,
                "--input-schedule-plan",
                str(replay_schedule_path),
                "--input-rollout-policy",
                str(rollout_policy_path),
                "--input-compare-plan",
                str(weekly_plan_path),
                "--compare-id",
                "optimizer-job-shadow-compare.weekly.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T05:47:00Z",
            )
            self.assertEqual(
                weekly_compare_result.returncode, 0, weekly_compare_result.stderr
            )
            batch_manifest_result = self.build_job_shadow_compare_batch_manifest(
                batch_manifest_path,
                "--input-compare-artifact",
                str(daily_compare_path),
                "--input-compare-artifact",
                str(weekly_compare_path),
            )
            self.assertEqual(
                batch_manifest_result.returncode, 0, batch_manifest_result.stderr
            )
            batch_result = self.build_job_shadow_compare_batch(
                batch_path,
                "--input-batch-manifest",
                str(batch_manifest_path),
            )
            self.assertEqual(batch_result.returncode, 0, batch_result.stderr)
            aggregate_result = self.build_recent_compare_summaries(
                aggregate_path,
                "--input-job-shadow-compare-batch",
                str(batch_path),
                "--input-job-orchestration-cycle",
                str(cycle_path),
            )
            self.assertEqual(aggregate_result.returncode, 0, aggregate_result.stderr)
            payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-recent-compare-summaries.sample.v1",
            )
            self.assertEqual(payload["summary"]["compareBatchCount"], 2)
            self.assertEqual(payload["summary"]["comparisonCount"], 6)
            self.assertEqual(payload["summary"]["groupEntryCount"], 6)

    def test_optimizer_recent_failure_summaries_builder_writes_aggregate(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-recent-failure-summaries-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            schedule_path = temp_root / "optimizer-job-schedule.external.json"
            execution_context_path = (
                temp_root / "optimizer-job-execution-context.json"
            )
            retention_policy_path = (
                temp_root / "optimizer-job-artifact-retention-policy.json"
            )
            cycle_path = temp_root / "optimizer-job-orchestration-cycle.json"
            error_path = temp_root / "optimizer-job-error.json"
            aggregate_path = temp_root / "optimizer-recent-failure-summaries.json"
            schedule_result = self.build_job_schedule(
                schedule_path,
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            )
            self.assertEqual(schedule_result.returncode, 0, schedule_result.stderr)
            context_result = self.build_job_execution_context(
                execution_context_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(context_result.returncode, 0, context_result.stderr)
            retention_result = self.build_job_artifact_retention_policy(
                retention_policy_path
            )
            self.assertEqual(retention_result.returncode, 0, retention_result.stderr)
            cycle_result = self.run_job_orchestration_cycle(
                cycle_path,
                "--input-schedule-plan",
                str(schedule_path),
                "--input-execution-context",
                str(execution_context_path),
                "--input-artifact-retention-policy",
                str(retention_policy_path),
            )
            self.assertEqual(cycle_result.returncode, 0, cycle_result.stderr)
            error_result = self.build_job_error_sample(
                error_path,
                "--input-schedule-plan",
                str(schedule_path),
            )
            self.assertEqual(error_result.returncode, 0, error_result.stderr)
            aggregate_result = self.build_recent_failure_summaries(
                aggregate_path,
                "--input-job-error",
                str(error_path),
                "--input-job-orchestration-cycle",
                str(cycle_path),
            )
            self.assertEqual(aggregate_result.returncode, 0, aggregate_result.stderr)
            payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"],
                "optimizer-recent-failure-summaries.sample.v1",
            )
            self.assertEqual(payload["summary"]["failureCount"], 1)
            self.assertEqual(payload["summary"]["retryableCount"], 0)
            self.assertEqual(
                payload["summary"]["ownerHintCounts"], {"input_pipeline": 1}
            )

    def test_optimizer_eval_batch_manifest_builder_writes_manifest(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-batch-manifest-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            daily_eval_run_path = temp_root / "optimizer-eval-run-daily.json"
            weekly_eval_run_path = temp_root / "optimizer-eval-run-weekly.json"
            manifest_path = temp_root / "optimizer-eval-batch-manifest.json"
            daily_result = self.build_eval_run(
                daily_eval_run_path,
                "--exclude-weekly-promotion",
                "--cycle-id",
                "optimizer-offline-cycle.autotiktok.test.daily",
                "--eval-run-id",
                "optimizer-eval-run.autotiktok.test.daily",
                "--report-id",
                "daily-review.autotiktok.test.daily",
            )
            weekly_result = self.build_eval_run(
                weekly_eval_run_path,
                "--cycle-id",
                "optimizer-offline-cycle.autotiktok.test.weekly",
                "--eval-run-id",
                "optimizer-eval-run.autotiktok.test.weekly",
                "--report-id",
                "daily-review.autotiktok.test.weekly",
            )
            self.assertEqual(daily_result.returncode, 0, daily_result.stderr)
            self.assertEqual(weekly_result.returncode, 0, weekly_result.stderr)
            result = self.build_eval_batch_manifest(
                manifest_path,
                "--input-eval-run",
                str(daily_eval_run_path),
                "--input-eval-run",
                str(weekly_eval_run_path),
                "--comparison-dimension",
                "mode",
                "--batch-window-label",
                "2026-04-14..2026-04-15",
                "--path-style",
                "absolute",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-eval-batch-manifest.sample.v1"
            )
            self.assertEqual(payload["comparisonDimension"], "mode")
            self.assertEqual(payload["batchWindowLabel"], "2026-04-14..2026-04-15")
            self.assertEqual(
                payload["evalRunPaths"],
                [str(daily_eval_run_path), str(weekly_eval_run_path)],
            )
            self.assertEqual(payload["generatedFrom"]["evalRunCount"], 2)

    def test_optimizer_eval_batch_builder_writes_eval_batch(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-eval-batch-") as temp_dir:
            eval_batch_path = Path(temp_dir) / "optimizer-eval-batch.json"
            result = self.build_eval_batch(eval_batch_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(eval_batch_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-eval-batch.v1")
            self.assertEqual(payload["summary"]["evalRunCount"], 2)
            self.assertEqual(payload["summary"]["comparisonDimension"], "mode")
            self.assertEqual(payload["summary"]["comparisonGroupCount"], 2)
            self.assertEqual(payload["summary"]["batchWindowLabel"], "2026-04-15..2026-04-15")
            self.assertEqual(
                payload["summary"]["modeCounts"],
                {
                    "daily_review_only": 1,
                    "daily_with_weekly_promotion": 1,
                },
            )
            self.assertEqual(
                payload["generatedFrom"]["sourceMode"], "default_mode_comparison"
            )
            self.assertEqual(payload["generatedFrom"]["comparisonDimension"], "mode")
            self.assertEqual(
                payload["generatedFrom"]["batchWindowLabel"], "2026-04-15..2026-04-15"
            )
            self.assertEqual(
                payload["summary"]["inputSourceKinds"]["challengerInput"],
                ["job_run_envelope"],
            )
            self.assertEqual(
                [item["groupValue"] for item in payload["groupSummaries"]],
                ["daily_review_only", "daily_with_weekly_promotion"],
            )

    def test_optimizer_eval_batch_builder_accepts_manifest(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-batch-manifest-build-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            daily_eval_run_path = temp_root / "optimizer-eval-run-daily.json"
            weekly_eval_run_path = temp_root / "optimizer-eval-run-weekly.json"
            manifest_path = temp_root / "optimizer-eval-batch-manifest.json"
            eval_batch_path = temp_root / "optimizer-eval-batch.json"
            daily_result = self.build_eval_run(
                daily_eval_run_path,
                "--exclude-weekly-promotion",
                "--cycle-id",
                "optimizer-offline-cycle.autotiktok.test.daily",
                "--eval-run-id",
                "optimizer-eval-run.autotiktok.test.daily",
                "--report-id",
                "daily-review.autotiktok.test.daily",
            )
            weekly_result = self.build_eval_run(
                weekly_eval_run_path,
                "--cycle-id",
                "optimizer-offline-cycle.autotiktok.test.weekly",
                "--eval-run-id",
                "optimizer-eval-run.autotiktok.test.weekly",
                "--report-id",
                "daily-review.autotiktok.test.weekly",
            )
            self.assertEqual(daily_result.returncode, 0, daily_result.stderr)
            self.assertEqual(weekly_result.returncode, 0, weekly_result.stderr)
            manifest_result = self.build_eval_batch_manifest(
                manifest_path,
                "--input-eval-run",
                str(daily_eval_run_path),
                "--input-eval-run",
                str(weekly_eval_run_path),
                "--comparison-dimension",
                "mode",
                "--batch-window-label",
                "2026-04-14..2026-04-15",
                "--path-style",
                "absolute",
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            result = self.build_eval_batch(
                eval_batch_path,
                "--input-eval-batch-manifest",
                str(manifest_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(eval_batch_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-eval-batch.v1")
            self.assertEqual(payload["summary"]["evalRunCount"], 2)
            self.assertEqual(payload["summary"]["comparisonDimension"], "mode")
            self.assertEqual(payload["summary"]["comparisonGroupCount"], 2)
            self.assertEqual(payload["summary"]["batchWindowLabel"], "2026-04-14..2026-04-15")
            self.assertEqual(payload["generatedFrom"]["sourceMode"], "eval_batch_manifest")
            self.assertEqual(
                payload["generatedFrom"]["sourceDescriptor"]["manifestSchemaVersion"],
                "optimizer-eval-batch-manifest.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["sourceDescriptor"]["inputEvalRunPaths"],
                [str(daily_eval_run_path), str(weekly_eval_run_path)],
            )
            self.assertEqual(
                [item["groupValue"] for item in payload["groupSummaries"]],
                ["daily_review_only", "daily_with_weekly_promotion"],
            )

    def test_optimizer_eval_batch_history_manifest_builder_writes_manifest(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-batch-history-manifest-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            (
                manifest_input_path,
                bundle_input_path,
                offline_cycle_daily_path,
                offline_cycle_weekly_path,
            ) = self.build_history_window_inputs(temp_root)
            window_set_path = temp_root / "optimizer-eval-window-set.json"
            manifest_path = temp_root / "optimizer-eval-batch-history-manifest.json"
            window_set_result = self.build_eval_window_set(
                window_set_path,
                "--runtime-source-mode",
                "path",
                "--input-manifest-path",
                str(manifest_input_path),
                "--input-bundle-path",
                str(bundle_input_path),
                "--input-offline-cycle-daily-path",
                str(offline_cycle_daily_path),
                "--input-offline-cycle-weekly-path",
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(window_set_result.returncode, 0, window_set_result.stderr)
            result = self.build_eval_batch_history_manifest(
                manifest_path, "--input-window-set", str(window_set_path)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-eval-batch-manifest.sample.v1"
            )
            self.assertEqual(payload["comparisonDimension"], "historyBatchLabel")
            self.assertEqual(payload["batchWindowLabel"], "2026-04-12..2026-04-15")
            self.assertEqual(payload["generatedFrom"]["evalRunCount"], 4)
            self.assertEqual(len(payload["evalRunEntries"]), 4)
            self.assertIn("runtimeSource", payload["evalRunEntries"][0])
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["runtimeSourceId"],
                "recent-daily-manifest",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["inputManifestPath"],
                str(manifest_input_path),
            )
            self.assertFalse(
                payload["evalRunEntries"][0]["runtimeSource"]["includeWeeklyPromotion"]
            )
            self.assertEqual(
                payload["evalRunEntries"][1]["runtimeSource"]["inputBundlePath"],
                str(bundle_input_path),
            )
            self.assertEqual(
                payload["evalRunEntries"][2]["runtimeSource"]["inputOfflineCyclePath"],
                str(offline_cycle_daily_path),
            )
            self.assertEqual(
                payload["evalRunEntries"][2]["historyBatchLabel"], "2026-04-12"
            )
            self.assertEqual(
                payload["evalRunEntries"][2]["scenarioLabel"], "historical_daily"
            )
            self.assertEqual(
                payload["evalRunEntries"][3]["summaryOverrides"]["weeklyDecision"],
                "keep_champion",
            )

    def test_optimizer_eval_window_set_builder_writes_window_set(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            (
                manifest_input_path,
                bundle_input_path,
                offline_cycle_daily_path,
                offline_cycle_weekly_path,
            ) = self.build_history_window_inputs(temp_root)
            window_set_path = temp_root / "optimizer-eval-window-set.json"
            result = self.build_eval_window_set(
                window_set_path,
                "--runtime-source-mode",
                "path",
                "--input-manifest-path",
                str(manifest_input_path),
                "--input-bundle-path",
                str(bundle_input_path),
                "--input-offline-cycle-daily-path",
                str(offline_cycle_daily_path),
                "--input-offline-cycle-weekly-path",
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-eval-window-set.sample.v1")
            self.assertEqual(payload["comparisonDimension"], "historyBatchLabel")
            self.assertEqual(payload["batchWindowLabel"], "2026-04-12..2026-04-15")
            self.assertEqual(payload["windowSetPurpose"], "production_replay")
            self.assertEqual(payload["windowSetBatchType"], "standard_replay")
            self.assertEqual(payload["generatedFrom"]["windowCount"], 4)
            self.assertEqual(payload["generatedFrom"]["runtimeSourceCount"], 4)
            self.assertEqual(
                payload["generatedFrom"]["windowSetPurpose"], "production_replay"
            )
            self.assertEqual(
                payload["generatedFrom"]["windowSetBatchType"], "standard_replay"
            )
            self.assertEqual(
                payload["generatedFrom"]["windowSetBatchTypeSelectionSource"],
                "fallback_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["comparisonDimensionSelectionSource"],
                "fallback_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutPolicyId"],
                "optimizer-runtime-profile-rollout-policy.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutPolicyFamily"],
                "autotiktok-runtime-profile-rollout",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutPolicyVersion"],
                "2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutClass"],
                "production",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileFamilyRegistryId"],
                "optimizer-runtime-profile-family-registry.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileFamilyId"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogLane"],
                "current",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogFamily"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogVersion"],
                "2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogSchemaVersion"],
                "optimizer-runtime-profile-catalog.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "policy_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileActiveLane"],
                "current",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileDefaultLane"],
                "current",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutStrategy"],
                "manual_gated_preview",
            )
            self.assertNotIn(
                "runtimeProfileMatchedRolloutRuleId", payload["generatedFrom"]
            )
            self.assertEqual(
                payload["generatedFrom"]["modeCounts"],
                {
                    "daily_review_only": 2,
                    "daily_with_weekly_promotion": 2,
                },
            )
            self.assertEqual(len(payload["runtimeSources"]), 4)
            self.assertEqual(
                payload["runtimeSources"][0]["runtimeSourceId"],
                "recent-daily-manifest",
            )
            self.assertEqual(
                payload["runtimeSources"][0]["runtimeSourceKind"],
                "input_manifest",
            )
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogFamily"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogVersion"],
                "2026-04-15",
            )
            self.assertEqual(
                payload["runtimeProfileRolloutPolicyReference"]["policyId"],
                "optimizer-runtime-profile-rollout-policy.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["runtimeProfileRolloutPolicyReference"]["policyFamily"],
                "autotiktok-runtime-profile-rollout",
            )
            self.assertEqual(
                payload["runtimeProfileRolloutPolicyReference"]["policyVersion"],
                "2026-04-15",
            )
            self.assertEqual(
                payload["runtimeProfileRolloutPolicyReference"]["familyId"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["runtimeProfileFamilyRegistryReference"]["registryId"],
                "optimizer-runtime-profile-family-registry.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["runtimeProfileFamilyRegistryReference"]["schemaVersion"],
                "optimizer-runtime-profile-family-registry.sample.v1",
            )
            self.assertEqual(
                payload["runtimeProfileFamilyRegistryReference"]["familyId"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["runtimeProfileFamilyRegistryReference"]["lane"],
                "current",
            )
            self.assertEqual(
                payload["runtimeSources"][0]["inputManifestPath"],
                str(manifest_input_path),
            )
            self.assertEqual(payload["windows"][0]["windowId"], "recent-daily")
            self.assertEqual(
                payload["windows"][0]["runtimeSourceId"],
                "recent-daily-manifest",
            )
            self.assertFalse(payload["windows"][0]["includeWeeklyPromotion"])
            self.assertEqual(
                payload["windows"][1]["runtimeSourceId"],
                "recent-weekly-bundle",
            )
            self.assertTrue(payload["windows"][1]["includeWeeklyPromotion"])
            self.assertEqual(
                payload["windows"][2]["runtimeSourceId"],
                "historical-daily-cycle",
            )
            self.assertEqual(
                payload["windows"][3]["runtimeSourceId"],
                "historical-weekly-cycle",
            )
            self.assertEqual(payload["windows"][2]["scenarioLabel"], "historical_daily")

    def test_optimizer_eval_window_set_descriptor_mode_resolves_via_history_manifest(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-descriptor-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            (
                manifest_input_path,
                bundle_input_path,
                offline_cycle_daily_path,
                offline_cycle_weekly_path,
            ) = self.build_history_window_inputs(temp_root)
            window_set_path = temp_root / "optimizer-eval-window-set.json"
            manifest_path = temp_root / "optimizer-eval-batch-history-manifest.json"
            registry_path = temp_root / "optimizer-runtime-artifact-registry.json"
            profile_catalog_path = temp_root / "optimizer-runtime-profile-catalog.json"
            plan_path = temp_root / "optimizer-runtime-materialization-plan.json"
            result = self.build_eval_window_set(window_set_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            registry_result = self.build_runtime_artifact_registry(
                registry_path,
                "--input-manifest-path",
                str(manifest_input_path),
                "--input-bundle-path",
                str(bundle_input_path),
                "--input-offline-cycle-daily-path",
                str(offline_cycle_daily_path),
                "--input-offline-cycle-weekly-path",
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            profile_catalog_result = self.build_runtime_profile_catalog(
                profile_catalog_path
            )
            self.assertEqual(
                profile_catalog_result.returncode, 0, profile_catalog_result.stderr
            )
            plan_result = self.build_runtime_materialization_plan(plan_path)
            self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
            window_set_payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(
                window_set_payload["runtimeSources"][0]["sourceDescriptor"]["descriptorKind"],
                "planner_runtime_binding",
            )
            self.assertEqual(
                window_set_payload["runtimeSources"][0]["sourceDescriptor"]["profileId"],
                "optimizer_input_manifest_profile",
            )
            self.assertEqual(
                window_set_payload["windows"][0]["runtimeSourceId"],
                "recent-daily-manifest",
            )
            manifest_result = self.build_eval_batch_history_manifest(
                manifest_path,
                "--input-window-set",
                str(window_set_path),
                "--input-artifact-registry",
                str(registry_path),
                "--input-runtime-profile-catalog",
                str(profile_catalog_path),
                "--input-materialization-plan",
                str(plan_path),
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["inputManifestPath"],
                str(manifest_input_path),
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["runtimeSourceId"],
                "recent-daily-manifest",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["runtimeProfileId"],
                "optimizer_input_manifest_profile",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"][
                    "runtimeProfileRequestedId"
                ],
                "optimizer_input_manifest_profile",
            )
            self.assertFalse(
                payload["evalRunEntries"][0]["runtimeSource"][
                    "runtimeProfileAliasApplied"
                ]
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"][
                    "runtimeProfileCatalogId"
                ],
                "optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"][
                    "runtimeProfileCatalogFamily"
                ],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"][
                    "runtimeProfileCatalogVersion"
                ],
                "2026-04-15",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"][
                    "runtimeProfileCatalogSchemaVersion"
                ],
                "optimizer-runtime-profile-catalog.sample.v1",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["materializationPlanId"],
                "optimizer_input_manifest_plan",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["jobFamilyGroup"],
                "optimizer_input_jobs",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["materializationProfile"],
                "manifest_from_job_runs",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["materializationStrategy"],
                "job_run_aggregation",
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["upstreamJobFamilies"],
                [
                    "topic_outcome_backfill",
                    "post_performance_signal",
                    "challenger_evaluation",
                ],
            )
            self.assertEqual(
                payload["evalRunEntries"][0]["runtimeSource"]["requiredArtifactKinds"],
                ["ranking_output", "scoring_context"],
            )
            self.assertEqual(
                payload["evalRunEntries"][3]["runtimeSource"]["inputOfflineCyclePath"],
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(
                payload["evalRunEntries"][3]["runtimeSource"]["materializationStrategy"],
                "offline_cycle_execution",
            )
            self.assertTrue(
                payload["evalRunEntries"][3]["runtimeSource"][
                    "planIncludeWeeklyPromotion"
                ]
            )

    def test_optimizer_eval_window_set_can_resolve_preview_family_registry_lane(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-family-registry-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            window_set_path = temp_root / "optimizer-eval-window-set.preview.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            result = self.build_eval_window_set(
                window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--runtime-profile-lane",
                "preview",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["runtimeProfileFamilyRegistryReference"]["lane"],
                "preview",
            )
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogFamily"],
                "autotiktok-runtime-profiles-preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogLane"],
                "preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "explicit",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileActiveLane"],
                "current",
            )

    def test_optimizer_eval_window_set_can_resolve_preview_rollout_policy_class(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-rollout-policy-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            policy_path = temp_root / "optimizer-runtime-profile-rollout-policy.json"
            window_set_path = temp_root / "optimizer-eval-window-set.preview.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            policy_result = self.build_runtime_profile_rollout_policy(
                policy_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            result = self.build_eval_window_set(
                window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--input-runtime-profile-rollout-policy",
                str(policy_path),
                "--runtime-profile-rollout-class",
                "preview_canary",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogLane"],
                "preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "policy_class",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileActiveLane"],
                "current",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileDefaultLane"],
                "current",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutStrategy"],
                "manual_gated_preview",
            )
            self.assertNotIn(
                "runtimeProfileMatchedRolloutRuleId", payload["generatedFrom"]
            )

    def test_optimizer_eval_window_set_can_resolve_preview_rollout_policy_rule(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-rollout-rule-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            policy_path = temp_root / "optimizer-runtime-profile-rollout-policy.json"
            window_set_path = temp_root / "optimizer-eval-window-set.preview-rule.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            policy_result = self.build_runtime_profile_rollout_policy(
                policy_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            result = self.build_eval_window_set(
                window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--input-runtime-profile-rollout-policy",
                str(policy_path),
                "--batch-window-label",
                "preview:2026-04-12..2026-04-15",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogLane"],
                "preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "policy_rule",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileMatchedRolloutRuleId"],
                "preview_batch_label",
            )

    def test_optimizer_eval_window_set_can_resolve_preview_rollout_policy_purpose(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-rollout-purpose-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            policy_path = temp_root / "optimizer-runtime-profile-rollout-policy.json"
            window_set_path = temp_root / "optimizer-eval-window-set.preview-purpose.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            policy_result = self.build_runtime_profile_rollout_policy(
                policy_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            result = self.build_eval_window_set(
                window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--input-runtime-profile-rollout-policy",
                str(policy_path),
                "--window-set-purpose",
                "preview_validation",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["windowSetPurpose"], "preview_validation")
            self.assertEqual(
                payload["generatedFrom"]["windowSetPurpose"], "preview_validation"
            )
            self.assertEqual(payload["windowSetBatchType"], "standard_replay")
            self.assertEqual(
                payload["generatedFrom"]["windowSetBatchTypeSelectionSource"],
                "metadata_policy_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["comparisonDimensionSelectionSource"],
                "metadata_policy_default",
            )
            self.assertEqual(
                payload["runtimeProfileCatalogReference"]["catalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileCatalogLane"],
                "preview",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "policy_purpose",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePurposePolicyId"],
                "preview_validation_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePurposeTemplateId"],
                "preview_validation_template",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePurposeTemplateFamilyId"],
                "preview_validation_family",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePlannerMetadataPolicyId"],
                "standard_replay_metadata_policy",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePlannerMetadataContractFamilyId"],
                "standard_replay_metadata_contract_family",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePlannerMetadataContractId"],
                "standard_replay_metadata_contract",
            )
            self.assertNotIn(
                "runtimeProfileMatchedRolloutRuleId", payload["generatedFrom"]
            )

    def test_optimizer_eval_window_set_can_resolve_preview_rollout_policy_window_mode_rule(
        self,
    ):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-rollout-window-mode-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            policy_path = temp_root / "optimizer-runtime-profile-rollout-policy.json"
            window_set_path = temp_root / "optimizer-eval-window-set.preview-window-mode.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            policy_result = self.build_runtime_profile_rollout_policy(
                policy_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            result = self.build_eval_window_set(
                window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--input-runtime-profile-rollout-policy",
                str(policy_path),
                "--window-set-purpose",
                "weekly_shadow_rehearsal",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["windowSetPurpose"], "weekly_shadow_rehearsal")
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "policy_rule",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileMatchedRolloutRuleId"],
                "preview_weekly_shadow_rehearsal",
            )

    def test_optimizer_eval_window_set_can_resolve_preview_rollout_policy_dimension_rule(
        self,
    ):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-rollout-dimension-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            policy_path = temp_root / "optimizer-runtime-profile-rollout-policy.json"
            window_set_path = temp_root / "optimizer-eval-window-set.preview-dimension.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            policy_result = self.build_runtime_profile_rollout_policy(
                policy_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            result = self.build_eval_window_set(
                window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--input-runtime-profile-rollout-policy",
                str(policy_path),
                "--window-set-purpose",
                "profile_compare_validation",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(window_set_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["comparisonDimension"], "rankingProfileId"
            )
            self.assertEqual(
                payload["windowSetPurpose"], "profile_compare_validation"
            )
            self.assertEqual(
                payload["windowSetBatchType"], "cross_profile_comparison"
            )
            self.assertEqual(
                payload["generatedFrom"]["windowSetBatchTypeSelectionSource"],
                "metadata_policy_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["comparisonDimensionSelectionSource"],
                "metadata_policy_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileLaneSelectionSource"],
                "policy_purpose",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePurposePolicyId"],
                "profile_compare_validation_default",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePurposeTemplateId"],
                "profile_compare_validation_template",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePurposeTemplateFamilyId"],
                "cross_profile_validation_family",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePlannerMetadataPolicyId"],
                "cross_profile_compare_metadata_policy",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePlannerMetadataContractFamilyId"],
                "cross_profile_compare_metadata_contract_family",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfilePlannerMetadataContractId"],
                "cross_profile_compare_metadata_contract",
            )
            self.assertEqual(
                payload["generatedFrom"]["runtimeProfileRolloutClass"],
                "preview_canary",
            )
            self.assertNotIn(
                "runtimeProfileMatchedRolloutRuleId", payload["generatedFrom"]
            )

    def test_optimizer_eval_window_set_rejects_invalid_planner_metadata_contract_override(
        self,
    ):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-metadata-contract-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "optimizer-runtime-profile-family-registry.json"
            policy_path = temp_root / "optimizer-runtime-profile-rollout-policy.json"
            invalid_window_set_path = temp_root / "optimizer-eval-window-set.invalid.json"
            registry_result = self.build_runtime_profile_family_registry(registry_path)
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            policy_result = self.build_runtime_profile_rollout_policy(
                policy_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)
            result = self.build_eval_window_set(
                invalid_window_set_path,
                "--input-runtime-profile-family-registry",
                str(registry_path),
                "--input-runtime-profile-rollout-policy",
                str(policy_path),
                "--window-set-purpose",
                "profile_compare_validation",
                "--window-set-batch-type",
                "standard_replay",
            )
            self.assertNotEqual(result.returncode, 0)
            combined_output = f"{result.stdout}\n{result.stderr}"
            self.assertIn("does not allow windowSetBatchType", combined_output)

    def test_optimizer_eval_batch_descriptor_history_manifest_tracks_materialization_plan(
        self,
    ):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-batch-descriptor-history-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            (
                manifest_input_path,
                bundle_input_path,
                offline_cycle_daily_path,
                offline_cycle_weekly_path,
            ) = self.build_history_window_inputs(temp_root)
            window_set_path = temp_root / "optimizer-eval-window-set.json"
            manifest_path = temp_root / "optimizer-eval-batch-history-manifest.json"
            registry_path = temp_root / "optimizer-runtime-artifact-registry.json"
            profile_catalog_path = temp_root / "optimizer-runtime-profile-catalog.json"
            plan_path = temp_root / "optimizer-runtime-materialization-plan.json"
            eval_batch_path = temp_root / "optimizer-eval-batch-history.json"
            window_set_result = self.build_eval_window_set(window_set_path)
            self.assertEqual(window_set_result.returncode, 0, window_set_result.stderr)
            registry_result = self.build_runtime_artifact_registry(
                registry_path,
                "--input-manifest-path",
                str(manifest_input_path),
                "--input-bundle-path",
                str(bundle_input_path),
                "--input-offline-cycle-daily-path",
                str(offline_cycle_daily_path),
                "--input-offline-cycle-weekly-path",
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            profile_catalog_result = self.build_runtime_profile_catalog(
                profile_catalog_path
            )
            self.assertEqual(
                profile_catalog_result.returncode, 0, profile_catalog_result.stderr
            )
            plan_result = self.build_runtime_materialization_plan(plan_path)
            self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
            manifest_result = self.build_eval_batch_history_manifest(
                manifest_path,
                "--input-window-set",
                str(window_set_path),
                "--input-artifact-registry",
                str(registry_path),
                "--input-runtime-profile-catalog",
                str(profile_catalog_path),
                "--input-materialization-plan",
                str(plan_path),
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            result = self.build_eval_batch(
                eval_batch_path,
                "--input-eval-batch-manifest",
                str(manifest_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(eval_batch_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["summary"]["runtimeProfileIds"],
                [
                    "optimizer_input_bundle_profile",
                    "optimizer_input_manifest_profile",
                    "optimizer_offline_cycle_daily_profile",
                    "optimizer_offline_cycle_weekly_profile",
                ],
            )
            self.assertEqual(
                payload["summary"]["runtimeProfileRequestedIds"],
                [
                    "optimizer_input_bundle_profile",
                    "optimizer_input_manifest_profile",
                    "optimizer_offline_cycle_daily_profile",
                    "optimizer_offline_cycle_weekly_profile",
                ],
            )
            self.assertEqual(
                payload["summary"]["runtimeProfileAliasAppliedCount"],
                0,
            )
            self.assertEqual(
                payload["summary"]["runtimeProfileCatalogIds"],
                ["optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15"],
            )
            self.assertEqual(
                payload["summary"]["runtimeProfileCatalogFamilies"],
                ["autotiktok-runtime-profiles"],
            )
            self.assertEqual(
                payload["summary"]["runtimeProfileCatalogVersions"],
                ["2026-04-15"],
            )
            self.assertEqual(
                payload["summary"]["runtimeProfileCatalogSchemaVersions"],
                ["optimizer-runtime-profile-catalog.sample.v1"],
            )
            self.assertEqual(
                payload["summary"]["materializationPlanIds"],
                [
                    "optimizer_input_bundle_plan",
                    "optimizer_input_manifest_plan",
                    "optimizer_offline_cycle_daily_plan",
                    "optimizer_offline_cycle_weekly_plan",
                ],
            )
            self.assertEqual(
                payload["summary"]["jobFamilyGroups"],
                ["optimizer_input_jobs", "optimizer_offline_cycle_jobs"],
            )
            self.assertEqual(
                payload["summary"]["materializationProfiles"],
                [
                    "bundle_from_manifest",
                    "daily_cycle_from_manifest",
                    "manifest_from_job_runs",
                    "weekly_cycle_from_bundle",
                ],
            )
            self.assertEqual(
                payload["summary"]["materializationStrategies"],
                [
                    "job_run_aggregation",
                    "manifest_materialization",
                    "offline_cycle_execution",
                ],
            )
            self.assertEqual(
                payload["summary"]["requiredArtifactKinds"],
                [
                    "optimizer_input_bundle",
                    "optimizer_input_manifest",
                    "ranking_output",
                    "scoring_context",
                ],
            )
            self.assertEqual(
                payload["summary"]["upstreamJobFamilies"],
                [
                    "challenger_evaluation",
                    "post_performance_signal",
                    "topic_outcome_backfill",
                ],
            )
            self.assertEqual(
                payload["items"][0]["runtimeProfileId"],
                "optimizer_input_manifest_profile",
            )
            self.assertEqual(
                payload["items"][0]["runtimeProfileRequestedId"],
                "optimizer_input_manifest_profile",
            )
            self.assertFalse(payload["items"][0]["runtimeProfileAliasApplied"])
            self.assertEqual(
                payload["items"][0]["runtimeProfileCatalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["items"][0]["runtimeProfileCatalogFamily"],
                "autotiktok-runtime-profiles",
            )
            self.assertEqual(
                payload["items"][0]["runtimeProfileCatalogVersion"],
                "2026-04-15",
            )
            self.assertEqual(
                payload["items"][0]["materializationPlanId"],
                "optimizer_input_manifest_plan",
            )
            self.assertEqual(
                payload["items"][0]["jobFamilyGroup"],
                "optimizer_input_jobs",
            )
            self.assertEqual(
                payload["items"][0]["materializationProfile"],
                "manifest_from_job_runs",
            )
            self.assertEqual(
                payload["items"][0]["materializationStrategy"],
                "job_run_aggregation",
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeProfileIds"],
                [
                    "optimizer_offline_cycle_daily_profile",
                    "optimizer_offline_cycle_weekly_profile",
                ],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeProfileRequestedIds"],
                [
                    "optimizer_offline_cycle_daily_profile",
                    "optimizer_offline_cycle_weekly_profile",
                ],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeProfileAliasAppliedCount"],
                0,
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeProfileCatalogIds"],
                ["optimizer-runtime-profile-catalog.autotiktok.fixture.2026-04-15"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeProfileCatalogFamilies"],
                ["autotiktok-runtime-profiles"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeProfileCatalogVersions"],
                ["2026-04-15"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["materializationPlanIds"],
                [
                    "optimizer_offline_cycle_daily_plan",
                    "optimizer_offline_cycle_weekly_plan",
                ],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["jobFamilyGroups"],
                ["optimizer_offline_cycle_jobs"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["materializationProfiles"],
                ["daily_cycle_from_manifest", "weekly_cycle_from_bundle"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["materializationStrategies"],
                ["offline_cycle_execution"],
            )

    def test_optimizer_eval_batch_history_manifest_rejects_catalog_version_mismatch(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-batch-history-mismatch-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            window_set_path = temp_root / "optimizer-eval-window-set.json"
            manifest_path = temp_root / "optimizer-eval-batch-history-manifest.json"
            profile_catalog_path = temp_root / "optimizer-runtime-profile-catalog.json"
            window_set_result = self.build_eval_window_set(window_set_path)
            self.assertEqual(window_set_result.returncode, 0, window_set_result.stderr)
            profile_catalog_result = self.build_runtime_profile_catalog(
                profile_catalog_path
            )
            self.assertEqual(
                profile_catalog_result.returncode, 0, profile_catalog_result.stderr
            )
            profile_catalog_payload = json.loads(
                profile_catalog_path.read_text(encoding="utf-8")
            )
            profile_catalog_payload["catalogVersion"] = "2026-04-16-preview"
            profile_catalog_path.write_text(
                json.dumps(profile_catalog_payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.build_eval_batch_history_manifest(
                manifest_path,
                "--input-window-set",
                str(window_set_path),
                "--input-runtime-profile-catalog",
                str(profile_catalog_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "runtime profile catalog version does not match",
                result.stderr,
            )

    def test_optimizer_eval_window_set_preview_catalog_resolves_aliases(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-window-set-preview-catalog-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            (
                manifest_input_path,
                bundle_input_path,
                offline_cycle_daily_path,
                offline_cycle_weekly_path,
            ) = self.build_history_window_inputs(temp_root)
            window_set_path = temp_root / "optimizer-eval-window-set.preview.json"
            manifest_path = temp_root / "optimizer-eval-batch-history-manifest.preview.json"
            registry_path = temp_root / "optimizer-runtime-artifact-registry.json"
            profile_catalog_path = temp_root / "optimizer-runtime-profile-catalog.preview.json"
            plan_path = temp_root / "optimizer-runtime-materialization-plan.json"
            window_set_result = self.build_eval_window_set(
                window_set_path,
                "--runtime-profile-catalog-id",
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
                "--runtime-profile-catalog-family",
                "autotiktok-runtime-profiles-preview",
                "--runtime-profile-catalog-version",
                "2026-04-16-preview",
            )
            self.assertEqual(window_set_result.returncode, 0, window_set_result.stderr)
            registry_result = self.build_runtime_artifact_registry(
                registry_path,
                "--input-manifest-path",
                str(manifest_input_path),
                "--input-bundle-path",
                str(bundle_input_path),
                "--input-offline-cycle-daily-path",
                str(offline_cycle_daily_path),
                "--input-offline-cycle-weekly-path",
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
            profile_catalog_result = self.build_runtime_profile_catalog(
                profile_catalog_path,
                "--catalog-lane",
                "preview",
            )
            self.assertEqual(
                profile_catalog_result.returncode, 0, profile_catalog_result.stderr
            )
            plan_result = self.build_runtime_materialization_plan(plan_path)
            self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
            manifest_result = self.build_eval_batch_history_manifest(
                manifest_path,
                "--input-window-set",
                str(window_set_path),
                "--input-artifact-registry",
                str(registry_path),
                "--input-runtime-profile-catalog",
                str(profile_catalog_path),
                "--input-materialization-plan",
                str(plan_path),
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            first_runtime_source = payload["evalRunEntries"][0]["runtimeSource"]
            self.assertEqual(
                first_runtime_source["runtimeProfileRequestedId"],
                "optimizer_input_manifest_profile",
            )
            self.assertEqual(
                first_runtime_source["runtimeProfileId"],
                "optimizer_input_manifest_profile_preview",
            )
            self.assertTrue(first_runtime_source["runtimeProfileAliasApplied"])
            self.assertEqual(
                first_runtime_source["runtimeProfileCatalogId"],
                "optimizer-runtime-profile-catalog.autotiktok.preview.2026-04-16",
            )
            self.assertEqual(
                first_runtime_source["runtimeProfileCatalogFamily"],
                "autotiktok-runtime-profiles-preview",
            )
            self.assertEqual(
                first_runtime_source["runtimeProfileCatalogVersion"],
                "2026-04-16-preview",
            )

    def test_optimizer_eval_batch_builder_accepts_history_manifest_entries(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-eval-batch-history-build-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            (
                manifest_input_path,
                bundle_input_path,
                offline_cycle_daily_path,
                offline_cycle_weekly_path,
            ) = self.build_history_window_inputs(temp_root)
            window_set_path = temp_root / "optimizer-eval-window-set.json"
            manifest_path = temp_root / "optimizer-eval-batch-history-manifest.json"
            eval_batch_path = temp_root / "optimizer-eval-batch-history.json"
            window_set_result = self.build_eval_window_set(
                window_set_path,
                "--runtime-source-mode",
                "path",
                "--input-manifest-path",
                str(manifest_input_path),
                "--input-bundle-path",
                str(bundle_input_path),
                "--input-offline-cycle-daily-path",
                str(offline_cycle_daily_path),
                "--input-offline-cycle-weekly-path",
                str(offline_cycle_weekly_path),
            )
            self.assertEqual(window_set_result.returncode, 0, window_set_result.stderr)
            manifest_result = self.build_eval_batch_history_manifest(
                manifest_path,
                "--input-window-set",
                str(window_set_path),
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            result = self.build_eval_batch(
                eval_batch_path,
                "--input-eval-batch-manifest",
                str(manifest_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(eval_batch_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-eval-batch.v1")
            self.assertEqual(payload["summary"]["evalRunCount"], 4)
            self.assertEqual(
                payload["summary"]["comparisonDimension"], "historyBatchLabel"
            )
            self.assertEqual(payload["summary"]["comparisonGroupCount"], 2)
            self.assertEqual(
                payload["summary"]["historyBatchLabels"], ["2026-04-12", "2026-04-15"]
            )
            self.assertEqual(
                payload["summary"]["historyWindowLabels"],
                ["historical_batch", "recent_batch"],
            )
            self.assertEqual(
                payload["summary"]["runtimeSourceKinds"],
                ["input_bundle", "input_manifest", "offline_cycle"],
            )
            self.assertEqual(
                payload["summary"]["runtimeSourceIds"],
                [
                    "historical-daily-cycle",
                    "historical-weekly-cycle",
                    "recent-daily-manifest",
                    "recent-weekly-bundle",
                ],
            )
            self.assertEqual(
                payload["summary"]["scenarioLabels"],
                [
                    "current_daily",
                    "current_weekly",
                    "historical_daily",
                    "historical_weekly",
                ],
            )
            self.assertEqual(payload["generatedFrom"]["sourceMode"], "eval_batch_manifest")
            self.assertIn(
                "inputEvalRunEntries", payload["generatedFrom"]["sourceDescriptor"]
            )
            self.assertEqual(
                [item["groupValue"] for item in payload["groupSummaries"]],
                ["2026-04-12", "2026-04-15"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["modeCounts"],
                {
                    "daily_review_only": 1,
                    "daily_with_weekly_promotion": 1,
                },
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeSourceKinds"],
                ["offline_cycle"],
            )
            self.assertEqual(
                payload["groupSummaries"][0]["runtimeSourceIds"],
                ["historical-daily-cycle", "historical-weekly-cycle"],
            )
            historical_items = [
                item for item in payload["items"] if item["historyBatchLabel"] == "2026-04-12"
            ]
            self.assertEqual(len(historical_items), 2)
            self.assertTrue(
                all(item["combinedReward"] == 0.5742 for item in historical_items)
            )


    def test_calc_reward_inline_path(self):
        result = self.run_script(
            "skills/autotiktok-strategy-optimizer/scripts/calc_reward.py",
            "--hit3",
            "0.67",
            "--ndcg10",
            "0.59",
            "--hit10",
            "0.83",
            "--novelty",
            "0.62",
            "--type-coverage",
            "0.74",
            "--executable-rate",
            "0.91",
            "--dup-rate",
            "0.18",
            "--view-lift",
            "0.55",
            "--performance-weight",
            "0.1",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["combinedReward"], 0.6)
        self.assertLessEqual(payload["performanceWeight"], 0.1)

    def test_daily_and_weekly_mock_outputs(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-") as temp_dir:
            daily_path = Path(temp_dir) / "daily.json"
            weekly_window_path = Path(temp_dir) / "weekly-window.json"
            weekly_path = Path(temp_dir) / "weekly.json"
            daily = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--output",
                str(daily_path),
            )
            self.assertEqual(daily.returncode, 0, daily.stderr)
            weekly_window = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/build_weekly_review_window.py",
                "--daily-review-input",
                str(daily_path),
                "--output",
                str(weekly_window_path),
            )
            self.assertEqual(weekly_window.returncode, 0, weekly_window.stderr)
            weekly = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(weekly_path),
            )
            self.assertEqual(weekly.returncode, 0, weekly.stderr)
            daily_payload = json.loads(daily_path.read_text(encoding="utf-8"))
            weekly_window_payload = json.loads(
                weekly_window_path.read_text(encoding="utf-8")
            )
            weekly_payload = json.loads(weekly_path.read_text(encoding="utf-8"))
            self.assertEqual(daily_payload["schemaVersion"], "daily-review-report.v1")
            self.assertEqual(daily_payload["policyVersion"], "optimizer-policy.v1")
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingSchemaVersion"],
                "ranking-output.v1",
            )
            self.assertEqual(daily_payload["rankingContext"]["requestedProfileId"], "auto")
            self.assertEqual(daily_payload["rankingContext"]["resolvedProfileId"], "growth-default")
            self.assertEqual(daily_payload["rankingContext"]["selectionSource"], "context_stage_mode")
            self.assertEqual(daily_payload["candidateSource"]["sourceKind"], "discovery_artifact")
            self.assertEqual(
                daily_payload["candidateSource"]["sourceSnapshotId"],
                "snap.discovery.fixture.2026-04-15",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingProfileSelectionSource"], "context_stage_mode"
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
                daily_payload["generatedFrom"]["rankingOptimizerDeprecatedTopLevelFields"],
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
            self.assertEqual(
                daily_payload["generatedFrom"]["challengerSchemaVersion"],
                "challenger-observations.sample.v1",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerInputSources"]["backfills"]["jobKind"],
                "topic_outcome_backfill",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerInputSources"]["performance"]["jobKind"],
                "post_performance_signal",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["optimizerInputSources"]["challengerInput"]["jobKind"],
                "challenger_evaluation",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["challengerInputKind"],
                "observations",
            )
            self.assertEqual(
                daily_payload["challengerReview"]["inputKind"],
                "observations",
            )
            self.assertEqual(
                daily_payload["challengerReview"]["leaderProfileId"],
                "search-priority-default",
            )
            self.assertEqual(daily_payload["rankingReview"]["rejectedTopicIds"], ["tp_trend_wired_earbuds_001"])
            self.assertGreaterEqual(daily_payload["rankingReview"]["rejectedCount"], 1)
            self.assertGreater(
                daily_payload["shadowLeaderboard"][0]["combinedRewardDelta"], 0
            )
            self.assertEqual(
                daily_payload["shadowLeaderboard"][0]["sourceInputKind"],
                "observations",
            )
            self.assertEqual(
                weekly_window_payload["schemaVersion"],
                "optimizer-weekly-review-window.sample.v1",
            )
            self.assertEqual(
                weekly_window_payload["generatedFrom"]["scenarioId"],
                "promotion_default",
            )
            self.assertEqual(
                weekly_window_payload["bestChallengerProfileId"],
                "search-priority-default",
            )
            self.assertEqual(len(weekly_window_payload["windows"]), 3)
            self.assertEqual(weekly_payload["schemaVersion"], "weekly-promotion-decision.v1")
            self.assertEqual(
                weekly_payload["sourceReviewWindowId"],
                weekly_window_payload["reviewWindowId"],
            )
            self.assertEqual(
                weekly_payload["championProfileSelection"]["resolvedProfileId"], "growth-default"
            )
            self.assertEqual(
                weekly_payload["championCandidateSource"]["sourceKind"],
                "discovery_artifact",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewProfileSelectionSource"],
                "context_stage_mode",
            )
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewCandidateSourceKind"],
                "discovery_artifact",
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
                    "dailyReviewRankingOptimizerDeprecatedTopLevelFields"
                ],
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
            self.assertEqual(
                weekly_payload["generatedFrom"]["dailyReviewChallengerInputKind"],
                "observations",
            )
            self.assertIn(
                weekly_payload["decision"],
                {"promote", "keep_champion", "rollback_champion"},
            )

    def test_daily_review_mock_rejects_invalid_ranking_contract(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-contract-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-invalid.json"
            payload = json.loads(RANKING_SAMPLE.read_text(encoding="utf-8"))
            payload["predictionRun"]["candidateCount"] = (
                payload["predictionRun"]["candidateCount"] + 1
            )
            ranking_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--ranking-input",
                str(ranking_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "ranking output does not satisfy the optimizer-facing contract",
                result.stdout,
            )
            self.assertIn(
                "candidateCount must match len(scores)",
                result.stdout,
            )

    def test_weekly_review_window_builder_writes_window(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-weekly-review-window-"
        ) as temp_dir:
            weekly_window_path = Path(temp_dir) / "weekly-window.json"
            result = self.build_weekly_review_window(weekly_window_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(weekly_window_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schemaVersion"], "optimizer-weekly-review-window.sample.v1"
            )
            self.assertEqual(payload["generatedFrom"]["scenarioId"], "promotion_default")
            self.assertEqual(
                [item["horizonId"] for item in payload["rewardHorizonPolicy"]["horizons"]],
                ["t+1", "t+3", "t+7"],
            )
            self.assertEqual(
                payload["windows"][0]["availableRewardHorizonIds"],
                ["t+1", "t+3", "t+7"],
            )
            self.assertEqual(
                payload["windows"][-1]["availableRewardHorizonIds"],
                ["t+1", "t+3"],
            )
            self.assertEqual(
                payload["aggregatedChampion"]["rewardHorizonSummaries"][0]["horizonId"],
                "t+1",
            )
            self.assertEqual(payload["aggregatedChampion"]["windowCount"], 3)
            self.assertEqual(
                payload["bestChallengerProfileId"], "search-priority-default"
            )
            self.assertFalse(payload["rollbackSignals"]["rollbackEligible"])
            self.assertFalse(payload["rollbackSignals"]["rollbackTriggered"])
            self.assertEqual(payload["rollbackSignals"]["rollbackSeverity"], "none")

    def test_weekly_promotion_mock_can_emit_rollback_decision(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-weekly-rollback-") as temp_dir:
            temp_root = Path(temp_dir)
            weekly_window_path = temp_root / "weekly-window-rollback.json"
            weekly_path = temp_root / "weekly-rollback.json"
            window_result = self.build_weekly_review_window(
                weekly_window_path,
                "--scenario",
                "rollback_guardrail",
            )
            self.assertEqual(window_result.returncode, 0, window_result.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(weekly_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(weekly_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "rollback_champion")
            self.assertEqual(
                payload["generatedFrom"]["weeklyReviewWindowScenarioId"],
                "rollback_guardrail",
            )
            self.assertEqual(
                payload["gateSummary"]["requiredRewardHorizonIds"],
                ["t+1", "t+3"],
            )
            self.assertEqual(
                payload["championSafetyReview"]["rollbackSeverity"], "critical"
            )
            self.assertTrue(payload["championSafetyReview"]["rollbackTriggered"])
            self.assertIn(
                "critical_holdout_regression",
                payload["championSafetyReview"]["rollbackReasonCodes"],
            )
            self.assertIn(
                "holdout_floor_breach_days",
                payload["championSafetyReview"]["failedGateIds"],
            )
            self.assertIn("critical_holdout_regression", payload["reason"])

    def test_weekly_promotion_mock_emits_candidate_gate_reviews(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-weekly-gates-") as temp_dir:
            temp_root = Path(temp_dir)
            weekly_window_path = temp_root / "weekly-window.json"
            weekly_path = temp_root / "weekly-promotion.json"
            window_result = self.build_weekly_review_window(weekly_window_path)
            self.assertEqual(window_result.returncode, 0, window_result.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(weekly_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(weekly_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "promote")
            self.assertEqual(
                payload["promotionCandidateReviews"][0]["profileId"],
                "search-priority-default",
            )
            self.assertTrue(
                payload["promotionCandidateReviews"][0]["eligibleForPromotion"]
            )
            self.assertFalse(payload["championSafetyReview"]["rollbackEligible"])
            self.assertFalse(payload["championSafetyReview"]["rollbackTriggered"])
            self.assertEqual(payload["championSafetyReview"]["rollbackSeverity"], "none")
            self.assertEqual(payload["gateSummary"]["weeklyStageMode"], "growth")
            self.assertEqual(
                payload["gateSummary"]["weeklyStagePolicyId"], "growth_weekly_gate"
            )

    def test_weekly_promotion_mock_can_explain_keep_champion(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-weekly-keep-") as temp_dir:
            temp_root = Path(temp_dir)
            weekly_window_path = temp_root / "weekly-window.json"
            weekly_keep_path = temp_root / "weekly-keep.json"
            window_result = self.build_weekly_review_window(weekly_window_path)
            self.assertEqual(window_result.returncode, 0, window_result.stderr)
            payload = json.loads(weekly_window_path.read_text(encoding="utf-8"))
            challenger = payload["challengerSummaries"][0]
            challenger["hardGatePassDayCount"] = 1
            challenger["avgHoldoutDelta"] = -0.001
            weekly_window_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(weekly_keep_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            keep_payload = json.loads(weekly_keep_path.read_text(encoding="utf-8"))
            self.assertEqual(keep_payload["decision"], "keep_champion")
            self.assertEqual(
                keep_payload["promotionCandidateReviews"][0]["profileId"],
                "search-priority-default",
            )
            self.assertFalse(
                keep_payload["promotionCandidateReviews"][0]["eligibleForPromotion"]
            )
            self.assertIn(
                "minimum_hard_gate_pass_days",
                keep_payload["promotionCandidateReviews"][0]["failedGateIds"],
            )
            self.assertIn(
                "minimum_average_holdout_delta",
                keep_payload["promotionCandidateReviews"][0]["failedGateIds"],
            )

    def test_weekly_promotion_mock_can_explain_keep_with_rollback_watch(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-weekly-keep-watch-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            weekly_window_path = temp_root / "weekly-window-watch.json"
            weekly_keep_path = temp_root / "weekly-keep-watch.json"
            window_result = self.build_weekly_review_window(weekly_window_path)
            self.assertEqual(window_result.returncode, 0, window_result.stderr)
            payload = json.loads(weekly_window_path.read_text(encoding="utf-8"))
            challenger = payload["challengerSummaries"][0]
            challenger["hardGatePassDayCount"] = 1
            challenger["avgHoldoutDelta"] = -0.001
            payload["rollbackSignals"]["rollbackEligible"] = True
            payload["rollbackSignals"]["rollbackTriggered"] = False
            payload["rollbackSignals"]["rollbackSeverity"] = "watch"
            payload["rollbackSignals"]["rollbackReasonCodes"] = [
                "holdout_floor_breach_days"
            ]
            weekly_window_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(weekly_keep_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            keep_payload = json.loads(weekly_keep_path.read_text(encoding="utf-8"))
            self.assertEqual(keep_payload["decision"], "keep_champion")
            self.assertTrue(keep_payload["championSafetyReview"]["rollbackEligible"])
            self.assertFalse(keep_payload["championSafetyReview"]["rollbackTriggered"])
            self.assertEqual(
                keep_payload["championSafetyReview"]["rollbackSeverity"], "watch"
            )
            self.assertIn(
                "holdout_floor_breach_days",
                keep_payload["championSafetyReview"]["rollbackReasonCodes"],
            )
            self.assertIn("watch rollback review", keep_payload["reason"])
            self.assertIn("holdout_floor_breach_days", keep_payload["reason"])

    def test_weekly_promotion_mock_applies_stage_specific_gates(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-weekly-stage-gates-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            weekly_window_path = temp_root / "weekly-window.json"
            scale_weekly_path = temp_root / "weekly-scale.json"
            search_weekly_path = temp_root / "weekly-search.json"
            window_result = self.build_weekly_review_window(weekly_window_path)
            self.assertEqual(window_result.returncode, 0, window_result.stderr)
            payload = json.loads(weekly_window_path.read_text(encoding="utf-8"))

            payload["championProfileSelection"]["stageMode"] = "scale"
            payload["generatedFrom"]["stageMode"] = "scale"
            weekly_window_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            scale_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(scale_weekly_path),
            )
            self.assertEqual(scale_result.returncode, 0, scale_result.stderr)
            scale_payload = json.loads(scale_weekly_path.read_text(encoding="utf-8"))
            self.assertEqual(scale_payload["decision"], "keep_champion")
            self.assertEqual(scale_payload["gateSummary"]["weeklyStageMode"], "scale")
            self.assertEqual(
                scale_payload["gateSummary"]["weeklyStagePolicyId"],
                "scale_weekly_gate",
            )
            self.assertEqual(
                scale_payload["gateSummary"]["minimumAverageRewardDelta"], 0.03
            )
            self.assertEqual(
                scale_payload["gateSummary"]["minimumAverageHoldoutDelta"], 0.007
            )
            self.assertIn(
                "minimum_average_reward_delta",
                scale_payload["promotionCandidateReviews"][0]["failedGateIds"],
            )
            self.assertIn(
                "minimum_average_holdout_delta",
                scale_payload["promotionCandidateReviews"][0]["failedGateIds"],
            )

            payload["championProfileSelection"]["stageMode"] = "search_priority"
            payload["generatedFrom"]["stageMode"] = "search_priority"
            weekly_window_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            search_result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(search_weekly_path),
            )
            self.assertEqual(search_result.returncode, 0, search_result.stderr)
            search_payload = json.loads(search_weekly_path.read_text(encoding="utf-8"))
            self.assertEqual(search_payload["decision"], "keep_champion")
            self.assertEqual(
                search_payload["gateSummary"]["weeklyStageMode"], "search_priority"
            )
            self.assertEqual(
                search_payload["gateSummary"]["weeklyStagePolicyId"],
                "search_priority_weekly_gate",
            )
            self.assertEqual(
                search_payload["gateSummary"]["minimumAverageRewardDelta"], 0.032
            )
            self.assertEqual(
                search_payload["gateSummary"]["minimumAverageHoldoutDelta"], 0.008
            )
            self.assertIn(
                "minimum_average_reward_delta",
                search_payload["promotionCandidateReviews"][0]["failedGateIds"],
            )
            self.assertIn(
                "minimum_average_holdout_delta",
                search_payload["promotionCandidateReviews"][0]["failedGateIds"],
            )

    def test_daily_review_mock_accepts_legacy_aliases_in_compat_mode(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-compat-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking-legacy.json"
            daily_path = Path(temp_dir) / "daily-compat.json"
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
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--ranking-input",
                str(ranking_path),
                "--ranking-contract-version",
                "ranking-optimizer-contract.vNext-preview",
                "--ranking-contract-validation-mode",
                "compat",
                "--output",
                str(daily_path),
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            daily_payload = json.loads(daily_path.read_text(encoding="utf-8"))
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.vNext-preview",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractValidationMode"],
                "compat",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "legacy_top_level_compat",
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
            self.assertTrue(
                daily_payload["generatedFrom"]["rankingOptimizerCompatApplied"]
            )
            self.assertIn(
                "optimizerHandoff<-legacy_top_level",
                daily_payload["generatedFrom"]["rankingOptimizerCompatAliasesApplied"],
            )
            self.assertIn(
                "schemaVersion<-implicit_ranking_output_v1",
                daily_payload["generatedFrom"]["rankingOptimizerCompatAliasesApplied"],
            )
            self.assertIn(
                "profileSelection.selectionSource<-predictionRun.profileSelectionSource",
                daily_payload["generatedFrom"]["rankingOptimizerCompatAliasesApplied"],
            )

    def test_preview_daily_review_wrapper_defaults_to_preview_lane(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-preview-wrapper-") as temp_dir:
            preview_daily_path = Path(temp_dir) / "daily-preview.json"
            current_daily_path = Path(temp_dir) / "daily-current.json"
            preview = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_preview_daily_review.py",
                "--output",
                str(preview_daily_path),
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            current = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_preview_daily_review.py",
                "--use-current-lane",
                "--output",
                str(current_daily_path),
            )
            self.assertEqual(current.returncode, 0, current.stderr)
            preview_payload = json.loads(preview_daily_path.read_text(encoding="utf-8"))
            current_payload = json.loads(current_daily_path.read_text(encoding="utf-8"))
            self.assertEqual(
                preview_payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.vNext-preview",
            )
            self.assertEqual(
                preview_payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "optimizer_handoff",
            )
            self.assertEqual(
                current_payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.v1",
            )
            self.assertEqual(
                current_payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "legacy_top_level",
            )

    def test_daily_review_mock_uses_optimizer_handoff_in_preview_exact_mode(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-preview-") as temp_dir:
            daily_path = Path(temp_dir) / "daily-preview-exact.json"
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--ranking-contract-version",
                "ranking-optimizer-contract.vNext-preview",
                "--ranking-contract-validation-mode",
                "exact",
                "--output",
                str(daily_path),
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            daily_payload = json.loads(daily_path.read_text(encoding="utf-8"))
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractVersion"],
                "ranking-optimizer-contract.vNext-preview",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerContractValidationMode"],
                "exact",
            )
            self.assertEqual(
                daily_payload["generatedFrom"]["rankingOptimizerSurfaceSource"],
                "optimizer_handoff",
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
            self.assertEqual(
                daily_payload["rankingContext"]["resolvedProfileId"],
                "growth-default",
            )

    def test_daily_review_mock_accepts_optimizer_input_bundle(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-bundle-run-") as temp_dir:
            bundle_path = Path(temp_dir) / "optimizer-input-bundle.json"
            daily_path = Path(temp_dir) / "daily-from-bundle.json"
            bundle = self.build_input_bundle(bundle_path)
            self.assertEqual(bundle.returncode, 0, bundle.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--input-bundle",
                str(bundle_path),
                "--output",
                str(daily_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(daily_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputBundleSchemaVersion"],
                "optimizer-input-bundle.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputBundleId"],
                "optimizer-input-bundle.autotiktok.fixture.2026-04-15",
            )

    def test_daily_review_mock_accepts_optimizer_input_manifest(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-manifest-run-") as temp_dir:
            manifest_path = Path(temp_dir) / "optimizer-input-manifest.json"
            daily_path = Path(temp_dir) / "daily-from-manifest.json"
            manifest = self.build_input_manifest(manifest_path)
            self.assertEqual(manifest.returncode, 0, manifest.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
                "--input-manifest",
                str(manifest_path),
                "--output",
                str(daily_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(daily_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputManifestSchemaVersion"],
                "optimizer-input-manifest.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputManifestId"],
                "optimizer-input-manifest.autotiktok.fixture.2026-04-15",
            )

    def test_offline_optimizer_cycle_runner_accepts_input_bundle(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-offline-cycle-bundle-") as temp_dir:
            bundle_path = Path(temp_dir) / "optimizer-input-bundle.json"
            cycle_path = Path(temp_dir) / "cycle-bundle.json"
            bundle = self.build_input_bundle(bundle_path)
            self.assertEqual(bundle.returncode, 0, bundle.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py",
                "--input-bundle",
                str(bundle_path),
                "--include-weekly-promotion",
                "--output",
                str(cycle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputBundleSchemaVersion"],
                "optimizer-input-bundle.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputBundleId"],
                "optimizer-input-bundle.autotiktok.fixture.2026-04-15",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSources"]["challengerInput"]["jobKind"],
                "challenger_evaluation",
            )
            self.assertEqual(payload["mode"], "daily_with_weekly_promotion")

    def test_offline_optimizer_cycle_runner_accepts_input_manifest(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-offline-cycle-manifest-") as temp_dir:
            manifest_path = Path(temp_dir) / "optimizer-input-manifest.json"
            cycle_path = Path(temp_dir) / "cycle-manifest.json"
            manifest = self.build_input_manifest(manifest_path)
            self.assertEqual(manifest.returncode, 0, manifest.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py",
                "--input-manifest",
                str(manifest_path),
                "--output",
                str(cycle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputManifestSchemaVersion"],
                "optimizer-input-manifest.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputManifestId"],
                "optimizer-input-manifest.autotiktok.fixture.2026-04-15",
            )

    def test_eval_run_builder_accepts_input_offline_cycle(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-eval-run-offline-cycle-") as temp_dir:
            temp_root = Path(temp_dir)
            cycle_path = temp_root / "optimizer-offline-cycle.json"
            eval_run_path = temp_root / "optimizer-eval-run.json"
            cycle = self.build_offline_cycle(
                cycle_path,
                "--input-bundle",
                "skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json",
                "--include-weekly-promotion",
            )
            self.assertEqual(cycle.returncode, 0, cycle.stderr)
            result = self.build_eval_run(
                eval_run_path,
                "--input-offline-cycle",
                str(cycle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(eval_run_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-eval-run.v1")
            self.assertEqual(
                payload["generatedFrom"]["optimizerOfflineCycleSchemaVersion"],
                "optimizer-offline-cycle.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSources"]["performance"]["jobKind"],
                "post_performance_signal",
            )

    def test_offline_optimizer_cycle_runner_defaults_to_daily_mode(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-offline-cycle-") as temp_dir:
            cycle_path = Path(temp_dir) / "cycle.json"
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py",
                "--output",
                str(cycle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "optimizer-offline-cycle.v1")
            self.assertEqual(payload["mode"], "daily_review_only")
            self.assertEqual(
                payload["summary"]["challengerInputKind"], "observations"
            )
            self.assertEqual(
                payload["generatedFrom"]["challengerSchemaVersion"],
                "challenger-observations.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["optimizerInputSources"]["backfills"]["jobKind"],
                "topic_outcome_backfill",
            )
            self.assertIsNone(payload["artifacts"]["weeklyPromotion"])

    def test_offline_optimizer_cycle_runner_can_include_weekly_promotion(self):
        with tempfile.TemporaryDirectory(prefix="autotiktok-offline-cycle-weekly-") as temp_dir:
            cycle_path = Path(temp_dir) / "cycle-weekly.json"
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py",
                "--include-weekly-promotion",
                "--output",
                str(cycle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "daily_with_weekly_promotion")
            self.assertIsNotNone(payload["artifacts"]["weeklyPromotion"])
            self.assertIn(
                payload["summary"]["weeklyDecision"],
                {"promote", "keep_champion", "rollback_champion"},
            )

    def test_offline_optimizer_cycle_runner_accepts_weekly_review_window(self):
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-offline-cycle-weekly-window-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            weekly_window_path = temp_root / "weekly-window.json"
            cycle_path = temp_root / "cycle-weekly-window.json"
            window_result = self.build_weekly_review_window(weekly_window_path)
            self.assertEqual(window_result.returncode, 0, window_result.stderr)
            result = self.run_script(
                "skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py",
                "--include-weekly-promotion",
                "--weekly-review-window-input",
                str(weekly_window_path),
                "--output",
                str(cycle_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(cycle_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["generatedFrom"]["weeklyReviewWindowSchemaVersion"],
                "optimizer-weekly-review-window.sample.v1",
            )
            self.assertEqual(
                payload["generatedFrom"]["weeklyReviewWindowId"],
                "optimizer-weekly-review-window.autotiktok.fixture.2026-04-20",
            )


if __name__ == "__main__":
    main()
