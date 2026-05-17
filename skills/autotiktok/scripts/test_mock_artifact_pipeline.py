#!/usr/bin/env python3
"""
Smoke tests for the AutoTikTok aggregate artifact maintenance scripts.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestMockArtifactPipeline(TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sync_all_mock_artifacts_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/sync_all_mock_artifacts.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Refreshed all AutoTikTok mock artifacts", result.stdout)

    def test_validate_all_mock_artifacts_passes(self):
        result = self.run_script(
            "skills/autotiktok/scripts/validate_all_mock_artifacts.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated all AutoTikTok mock artifacts", result.stdout)
        self.assertIn("validate_artifact_provenance_chain.py", result.stdout)
        self.assertIn(
            "validate_trending_discovery_adapter_contract_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_trending_source_snapshots_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_trending_video_samples_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_trending_signal_items_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_trending_discovery_ranking_integration.py",
            result.stdout,
        )
        self.assertIn(
            "validate_discovery_snapshot_materialization_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_discovery_snapshot_ingest_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_discovery_topic_abstraction_expectations.py",
            result.stdout,
        )
        self.assertIn(
            "validate_discovery_merge_packaging_expectations.py",
            result.stdout,
        )
        self.assertIn(
            "validate_discovery_ranking_handoff_alignment.py",
            result.stdout,
        )
        self.assertIn("validate_live_lane_dependency_inventory.py", result.stdout)
        self.assertIn("validate_ranking_optimizer_contract.py", result.stdout)
        self.assertIn("validate_ranking_optimizer_contract_rehearsal.py", result.stdout)
        self.assertIn("validate_ranking_profile_matrix_expectations.py", result.stdout)
        self.assertIn("validate_optimizer_input_manifest_alignment.py", result.stdout)
        self.assertIn("validate_optimizer_input_bundle_alignment.py", result.stdout)
        self.assertIn("validate_optimizer_raw_ingress_alignment.py", result.stdout)
        self.assertIn("validate_optimizer_shadow_input_alignment.py", result.stdout)
        self.assertIn(
            "validate_optimizer_real_shadow_input_alignment.py", result.stdout
        )
        self.assertIn("validate_optimizer_job_schedule_alignment.py", result.stdout)
        self.assertIn(
            "validate_optimizer_openclaw_cron_runtime_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_schedule_external_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_scheduler_compatibility_role_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_artifact_retention_policy_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_execution_context_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_error_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_run_summary_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_recent_run_summaries_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_recent_compare_summaries_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_recent_weekly_decisions_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_recent_failure_summaries_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_orchestration_cycle_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_schedule_rollout_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_shadow_compare_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_shadow_compare_cutover_alignment.py",
            result.stdout,
        )
        self.assertIn(
            "validate_optimizer_job_shadow_compare_batch_alignment.py",
            result.stdout,
        )
        self.assertIn("validate_weekly_strategy_realism.py", result.stdout)
        self.assertIn("validate_weekly_stage_policy_alignment.py", result.stdout)
        self.assertIn("validate_runtime_profile_catalog_cutover.py", result.stdout)
        self.assertIn("validate_runtime_profile_rollout_policy_cutover.py", result.stdout)
        self.assertIn(
            "validate_runtime_profile_rollout_policy_dimension_routing.py",
            result.stdout,
        )
        self.assertIn(
            "validate_runtime_profile_rollout_policy_purpose_routing.py",
            result.stdout,
        )
        self.assertIn("validate_runtime_profile_rollout_policy_rule_routing.py", result.stdout)
        self.assertIn(
            "validate_runtime_profile_rollout_policy_window_mode_routing.py",
            result.stdout,
        )
        self.assertIn("validate_optimizer_stage_matrix_alignment.py", result.stdout)
        self.assertIn("validate_optimizer_stage_matrix_expectations.py", result.stdout)
        self.assertIn("validate_preview_default_rollout.py", result.stdout)
        self.assertIn("validate_preview_lane_consumer_cutover.py", result.stdout)
        self.assertIn("validate_preview_lane_cutover.py", result.stdout)

    def test_sync_all_includes_workflow_summary(self):
        result = self.run_script(
            "skills/autotiktok/scripts/sync_all_mock_artifacts.py"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "sync_discovery_snapshot_materialization_sample.py", result.stdout
        )
        self.assertIn("sync_workflow_summary_sample.py", result.stdout)
        self.assertIn("sync_ranking_profile_matrix.py", result.stdout)
        self.assertIn("sync_optimizer_stage_matrix.py", result.stdout)


if __name__ == "__main__":
    main()
