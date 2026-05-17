#!/usr/bin/env python3
"""
Run smoke tests across the three AutoTikTok skills.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]

TEST_SCRIPTS = [
    "skills/autotiktok/scripts/test_mock_artifact_pipeline.py",
    "skills/autotiktok/scripts/test_artifact_provenance_chain.py",
    "skills/autotiktok/scripts/test_workflow_summary_alignment.py",
    "skills/autotiktok/scripts/test_trending_discovery_adapter_contract_alignment.py",
    "skills/autotiktok/scripts/test_trending_source_snapshots_alignment.py",
    "skills/autotiktok/scripts/test_trending_video_samples_alignment.py",
    "skills/autotiktok/scripts/test_trending_signal_items_alignment.py",
    "skills/autotiktok/scripts/test_trending_discovery_ranking_integration.py",
    "skills/autotiktok/scripts/test_video_download_manifest_adapter_alignment.py",
    "skills/autotiktok/scripts/test_video_content_analysis_contract_alignment.py",
    "skills/autotiktok/scripts/test_video_content_analysis_batch_runner_alignment.py",
    "skills/autotiktok/scripts/test_enriched_signal_items_alignment.py",
    "skills/autotiktok/scripts/test_enriched_discovery_ranking_integration.py",
    "skills/autotiktok/scripts/test_video_understanding_live_smoke_docs_alignment.py",
    "skills/autotiktok/scripts/test_video_understanding_routing_guardrails.py",
    "skills/autotiktok/scripts/test_discovery_snapshot_materialization_alignment.py",
    "skills/autotiktok/scripts/test_discovery_snapshot_ingest_alignment.py",
    "skills/autotiktok/scripts/test_discovery_output_alignment.py",
    "skills/autotiktok/scripts/test_discovery_topic_abstraction_expectations.py",
    "skills/autotiktok/scripts/test_discovery_merge_packaging_expectations.py",
    "skills/autotiktok/scripts/test_discovery_ranking_handoff_alignment.py",
    "skills/autotiktok/scripts/test_live_lane_dependency_inventory.py",
    "skills/autotiktok/scripts/test_ranking_output_alignment.py",
    "skills/autotiktok/scripts/test_ranking_optimizer_contract.py",
    "skills/autotiktok/scripts/test_ranking_optimizer_contract_rehearsal.py",
    "skills/autotiktok/scripts/test_ranking_profile_matrix_alignment.py",
    "skills/autotiktok/scripts/test_ranking_profile_matrix_expectations.py",
    "skills/autotiktok/scripts/test_optimizer_raw_ingress_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_shadow_input_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_real_shadow_input_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_output_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_openclaw_cron_runtime_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_schedule_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_schedule_external_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_scheduler_compatibility_role_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_artifact_retention_policy_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_execution_context_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_error_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_run_summary_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_recent_run_summaries_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_recent_compare_summaries_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_recent_weekly_decisions_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_recent_failure_summaries_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_orchestration_cycle_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_schedule_rollout_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_shadow_compare_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_shadow_compare_cutover_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_job_shadow_compare_batch_alignment.py",
    "skills/autotiktok/scripts/test_weekly_strategy_realism.py",
    "skills/autotiktok/scripts/test_weekly_stage_policy_alignment.py",
    "skills/autotiktok/scripts/test_runtime_profile_catalog_cutover.py",
    "skills/autotiktok/scripts/test_runtime_profile_rollout_policy_cutover.py",
    "skills/autotiktok/scripts/test_runtime_profile_planner_metadata_contract_enforcement.py",
    "skills/autotiktok/scripts/test_runtime_profile_rollout_policy_dimension_routing.py",
    "skills/autotiktok/scripts/test_runtime_profile_rollout_policy_purpose_routing.py",
    "skills/autotiktok/scripts/test_runtime_profile_rollout_policy_rule_routing.py",
    "skills/autotiktok/scripts/test_runtime_profile_rollout_policy_window_mode_routing.py",
    "skills/autotiktok/scripts/test_optimizer_stage_matrix_alignment.py",
    "skills/autotiktok/scripts/test_optimizer_stage_matrix_expectations.py",
    "skills/autotiktok/scripts/test_preview_default_rollout.py",
    "skills/autotiktok/scripts/test_preview_lane_consumer_cutover.py",
    "skills/autotiktok/scripts/test_preview_lane_cutover.py",
    "skills/autotiktok/scripts/test_shared_fixture_alignment.py",
    "skills/autotiktok-topic-discovery/scripts/test_discovery_skill.py",
    "skills/autotiktok-topic-ranking/scripts/test_ranking_skill.py",
    "skills/autotiktok-topic-ranking/scripts/test_ranking_report.py",
    "skills/autotiktok-strategy-optimizer/scripts/test_daily_review_runtime.py",
    "skills/autotiktok-strategy-optimizer/scripts/test_optimizer_skill.py",
    "skills/autotiktok/scripts/test_end_to_end_workflow.py",
]


class TestAutotiktokSkills(TestCase):
    def test_all_skill_smokes_pass(self):
        for script in TEST_SCRIPTS:
            result = subprocess.run(
                [sys.executable, script],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=f"{script} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
            )


if __name__ == "__main__":
    main()
