#!/usr/bin/env python3
"""
Refresh optimizer sample outputs from the current ranking sample and optimizer fixtures.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DAILY_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "daily-review.sample.json"
)
WEEKLY_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "weekly-promotion.sample.json"
)
EVAL_RUN_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-eval-run.sample.json"
)
EVAL_RUN_DAILY_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-eval-run-daily.sample.json"
)
EVAL_RUN_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "build_optimizer_eval_run.py"
)
EVAL_BATCH_MANIFEST_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-batch-manifest.sample.json"
)
EVAL_BATCH_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch_manifest.py"
)
EVAL_BATCH_HISTORY_MANIFEST_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-batch-history-manifest.sample.json"
)
EVAL_WINDOW_SET_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-window-set.sample.json"
)
EVAL_WINDOW_SET_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_window_set.py"
)
EVAL_BATCH_HISTORY_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch_history_manifest.py"
)
EVAL_BATCH_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-eval-batch.sample.json"
)
EVAL_BATCH_HISTORY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-batch-history.sample.json"
)
EVAL_BATCH_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "build_optimizer_eval_batch.py"
)
BACKFILL_RUN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "topic-outcome-backfill-run.sample.json"
)
BACKFILL_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_topic_outcome_backfill_run.py"
)
PERFORMANCE_RUN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "post-performance-signal-run.sample.json"
)
PERFORMANCE_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_post_performance_signal_run.py"
)
CHALLENGER_RUN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "challenger-evaluation-run.sample.json"
)
CHALLENGER_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_challenger_evaluation_run.py"
)
SOURCE_PROVIDER_REGISTRY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-source-provider-registry.sample.json"
)
SOURCE_ARTIFACT_CATALOG_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-source-artifact-catalog.sample.json"
)
SOURCE_ARTIFACT_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_source_artifact_catalog.py"
)
SOURCE_PROVIDER_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_source_provider_registry.py"
)
SOURCE_PROVIDER_CATALOG_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-source-provider-catalog.sample.json"
)
SOURCE_PROVIDER_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_source_provider_catalog.py"
)
JOB_ARTIFACT_RESOLVER_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-artifact-resolver.sample.json"
)
JOB_ARTIFACT_RESOLVER_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_artifact_resolver.py"
)
INPUT_SOURCE_REGISTRY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-source-registry.sample.json"
)
INPUT_ROLLOUT_POLICY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-rollout-policy.sample.json"
)
INPUT_SOURCE_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_source_registry.py"
)
INPUT_ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_rollout_policy.py"
)
MANIFEST_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-input-manifest.sample.json"
)
RAW_SHADOW_MANIFEST_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.raw-shadow.sample.json"
)
REAL_SHADOW_MANIFEST_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.real-shadow.sample.json"
)
MANIFEST_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "build_optimizer_input_manifest.py"
)
BUNDLE_OUTPUT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-input-bundle.sample.json"
)
BUNDLE_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "materialize_optimizer_input_bundle.py"
)
RUNTIME_ARTIFACT_REGISTRY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-artifact-registry.sample.json"
)
RUNTIME_PROFILE_CATALOG_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-catalog.sample.json"
)
RUNTIME_PROFILE_CATALOG_PREVIEW_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-catalog-preview.sample.json"
)
RUNTIME_PROFILE_FAMILY_REGISTRY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-family-registry.sample.json"
)
RUNTIME_PROFILE_ROLLOUT_POLICY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-rollout-policy.sample.json"
)
RUNTIME_ARTIFACT_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_artifact_registry.py"
)
RUNTIME_PROFILE_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_catalog.py"
)
RUNTIME_PROFILE_FAMILY_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_family_registry.py"
)
RUNTIME_PROFILE_ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_rollout_policy.py"
)
RUNTIME_MATERIALIZATION_PLAN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-materialization-plan.sample.json"
)
RUNTIME_MATERIALIZATION_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_materialization_plan.py"
)
DAILY_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "daily_review_mock.py"
)
WEEKLY_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "weekly_promotion_mock.py"
)
WEEKLY_REVIEW_WINDOW_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_weekly_review_window.py"
)
OFFLINE_CYCLE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_offline_optimizer_cycle.py"
)
JOB_SCHEDULE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_schedule.py"
)
OPENCLAW_CRON_CONTRACT_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_openclaw_cron_contract.py"
)
WEEKLY_REVIEW_WINDOW_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)
WEEKLY_REVIEW_WINDOW_SCALE_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.scale.sample.json"
)
WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.search-priority.sample.json"
)
WEEKLY_SCALE_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.scale.sample.json"
)
WEEKLY_SEARCH_PRIORITY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.search-priority.sample.json"
)
OFFLINE_CYCLE_DAILY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-offline-cycle-daily.sample.json"
)
OFFLINE_CYCLE_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-offline-cycle.sample.json"
)
JOB_SCHEDULE_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json"
)
JOB_SCHEDULE_EXTERNAL_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.external.sample.json"
)
OPENCLAW_CRON_CONTRACT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-openclaw-cron-contract.sample.json"
)
JOB_EXECUTION_CONTEXT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-execution-context.sample.json"
)
JOB_ARTIFACT_RETENTION_POLICY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-artifact-retention-policy.sample.json"
)
JOB_RUN_SUMMARY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-run-summary.sample.json"
)
JOB_ERROR_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-error.sample.json"
)
RECENT_RUN_SUMMARIES_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-run-summaries.sample.json"
)
RECENT_COMPARE_SUMMARIES_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-compare-summaries.sample.json"
)
RECENT_WEEKLY_DECISIONS_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-weekly-decisions.sample.json"
)
RECENT_FAILURE_SUMMARIES_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-recent-failure-summaries.sample.json"
)
JOB_ORCHESTRATION_CYCLE_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-orchestration-cycle.sample.json"
)
DAILY_JOB_RUN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-daily-job-run.sample.json"
)
WEEKLY_JOB_RUN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-job-run.sample.json"
)
DAILY_JOB_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_daily_optimizer_job.py"
)
WEEKLY_JOB_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_weekly_optimizer_job.py"
)
JOB_SHADOW_COMPARE_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare.sample.json"
)
JOB_SHADOW_COMPARE_DAILY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare.daily.sample.json"
)
JOB_SHADOW_COMPARE_WEEKLY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare.weekly.sample.json"
)
JOB_SHADOW_COMPARE_PLAN_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.sample.json"
)
JOB_SHADOW_COMPARE_PLAN_DAILY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.daily.sample.json"
)
JOB_SHADOW_COMPARE_PLAN_WEEKLY_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-plan.weekly.sample.json"
)
JOB_SHADOW_COMPARE_BATCH_MANIFEST_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch-manifest.sample.json"
)
JOB_SHADOW_COMPARE_BATCH_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch.sample.json"
)
JOB_SHADOW_COMPARE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare.py"
)
JOB_SHADOW_COMPARE_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_plan.py"
)
JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_batch_manifest.py"
)
JOB_SHADOW_COMPARE_BATCH_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_shadow_compare_batch.py"
)
JOB_EXECUTION_CONTEXT_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_execution_context.py"
)
JOB_ARTIFACT_RETENTION_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_artifact_retention_policy.py"
)
JOB_ORCHESTRATION_CYCLE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_optimizer_job_orchestration_cycle.py"
)
RUN_SUMMARY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_run_summary.py"
)
JOB_ERROR_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_error_sample.py"
)
RECENT_RUN_SUMMARIES_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_recent_run_summaries.py"
)
RECENT_COMPARE_SUMMARIES_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_recent_compare_summaries.py"
)
RECENT_WEEKLY_DECISIONS_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_recent_weekly_decisions.py"
)
RECENT_FAILURE_SUMMARIES_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_recent_failure_summaries.py"
)


def run_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> int:
    try:
        run_script(BACKFILL_RUN_SCRIPT, "--output", str(BACKFILL_RUN_OUTPUT))
        run_script(PERFORMANCE_RUN_SCRIPT, "--output", str(PERFORMANCE_RUN_OUTPUT))
        run_script(CHALLENGER_RUN_SCRIPT, "--output", str(CHALLENGER_RUN_OUTPUT))
        run_script(
            SOURCE_ARTIFACT_CATALOG_SCRIPT,
            "--output",
            str(SOURCE_ARTIFACT_CATALOG_OUTPUT),
        )
        run_script(
            SOURCE_PROVIDER_REGISTRY_SCRIPT,
            "--input-source-artifact-catalog",
            str(SOURCE_ARTIFACT_CATALOG_OUTPUT),
            "--output",
            str(SOURCE_PROVIDER_REGISTRY_OUTPUT),
        )
        run_script(
            SOURCE_PROVIDER_CATALOG_SCRIPT,
            "--input-source-provider-registry",
            str(SOURCE_PROVIDER_REGISTRY_OUTPUT),
            "--output",
            str(SOURCE_PROVIDER_CATALOG_OUTPUT),
        )
        run_script(
            JOB_ARTIFACT_RESOLVER_SCRIPT,
            "--input-source-provider-catalog",
            str(SOURCE_PROVIDER_CATALOG_OUTPUT),
            "--output",
            str(JOB_ARTIFACT_RESOLVER_OUTPUT),
        )
        run_script(
            INPUT_SOURCE_REGISTRY_SCRIPT,
            "--input-artifact-resolver",
            str(JOB_ARTIFACT_RESOLVER_OUTPUT),
            "--output",
            str(INPUT_SOURCE_REGISTRY_OUTPUT),
        )
        run_script(
            INPUT_ROLLOUT_POLICY_SCRIPT,
            "--input-source-registry",
            str(INPUT_SOURCE_REGISTRY_OUTPUT),
            "--output",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
        )
        run_script(MANIFEST_SCRIPT, "--output", str(MANIFEST_OUTPUT))
        run_script(
            MANIFEST_SCRIPT,
            "--input-source-registry",
            str(INPUT_SOURCE_REGISTRY_OUTPUT),
            "--source-lane",
            "sample_raw_shadow",
            "--manifest-id",
            "optimizer-input-manifest.raw-shadow.autotiktok.fixture.2026-04-18",
            "--generated-at",
            "2026-04-18T03:05:00Z",
            "--output",
            str(RAW_SHADOW_MANIFEST_OUTPUT),
        )
        run_script(
            MANIFEST_SCRIPT,
            "--input-source-registry",
            str(INPUT_SOURCE_REGISTRY_OUTPUT),
            "--source-lane",
            "real_provider_shadow",
            "--manifest-id",
            "optimizer-input-manifest.real-shadow.autotiktok.fixture.2026-04-18",
            "--generated-at",
            "2026-04-18T03:12:00Z",
            "--output",
            str(REAL_SHADOW_MANIFEST_OUTPUT),
        )
        run_script(BUNDLE_SCRIPT, "--input-manifest", str(MANIFEST_OUTPUT), "--output", str(BUNDLE_OUTPUT))
        run_script(
            RUNTIME_ARTIFACT_REGISTRY_SCRIPT,
            "--output",
            str(RUNTIME_ARTIFACT_REGISTRY_OUTPUT),
        )
        run_script(
            RUNTIME_PROFILE_CATALOG_SCRIPT,
            "--output",
            str(RUNTIME_PROFILE_CATALOG_OUTPUT),
        )
        run_script(
            RUNTIME_PROFILE_CATALOG_SCRIPT,
            "--catalog-lane",
            "preview",
            "--output",
            str(RUNTIME_PROFILE_CATALOG_PREVIEW_OUTPUT),
        )
        run_script(
            RUNTIME_PROFILE_FAMILY_REGISTRY_SCRIPT,
            "--output",
            str(RUNTIME_PROFILE_FAMILY_REGISTRY_OUTPUT),
        )
        run_script(
            RUNTIME_PROFILE_ROLLOUT_POLICY_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(RUNTIME_PROFILE_FAMILY_REGISTRY_OUTPUT),
            "--output",
            str(RUNTIME_PROFILE_ROLLOUT_POLICY_OUTPUT),
        )
        run_script(
            RUNTIME_MATERIALIZATION_PLAN_SCRIPT,
            "--output",
            str(RUNTIME_MATERIALIZATION_PLAN_OUTPUT),
        )
        run_script(
            DAILY_SCRIPT,
            "--input-bundle",
            str(BUNDLE_OUTPUT),
            "--output",
            str(DAILY_OUTPUT),
        )
        run_script(
            WEEKLY_REVIEW_WINDOW_SCRIPT,
            "--daily-review-input",
            str(DAILY_OUTPUT),
            "--output",
            str(WEEKLY_REVIEW_WINDOW_OUTPUT),
        )
        run_script(
            WEEKLY_SCRIPT,
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_OUTPUT),
            "--output",
            str(WEEKLY_OUTPUT),
        )
        run_script(
            WEEKLY_REVIEW_WINDOW_SCRIPT,
            "--daily-review-input",
            str(DAILY_OUTPUT),
            "--stage-mode",
            "scale",
            "--review-window-id",
            "optimizer-weekly-review-window.scale.autotiktok.fixture.2026-04-20",
            "--output",
            str(WEEKLY_REVIEW_WINDOW_SCALE_OUTPUT),
        )
        run_script(
            WEEKLY_SCRIPT,
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_SCALE_OUTPUT),
            "--output",
            str(WEEKLY_SCALE_OUTPUT),
        )
        run_script(
            WEEKLY_REVIEW_WINDOW_SCRIPT,
            "--daily-review-input",
            str(DAILY_OUTPUT),
            "--stage-mode",
            "search_priority",
            "--review-window-id",
            "optimizer-weekly-review-window.search-priority.autotiktok.fixture.2026-04-20",
            "--output",
            str(WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY_OUTPUT),
        )
        run_script(
            WEEKLY_SCRIPT,
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY_OUTPUT),
            "--output",
            str(WEEKLY_SEARCH_PRIORITY_OUTPUT),
        )
        run_script(
            OFFLINE_CYCLE_SCRIPT,
            "--input-manifest",
            str(MANIFEST_OUTPUT),
            "--cycle-id",
            "optimizer-offline-cycle.autotiktok.fixture.2026-04-15.daily",
            "--report-id",
            "daily-review.autotiktok.fixture.2026-04-15.daily",
            "--output",
            str(OFFLINE_CYCLE_DAILY_OUTPUT),
        )
        run_script(
            OFFLINE_CYCLE_SCRIPT,
            "--input-bundle",
            str(BUNDLE_OUTPUT),
            "--include-weekly-promotion",
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_OUTPUT),
            "--output",
            str(OFFLINE_CYCLE_OUTPUT),
        )
        run_script(
            JOB_SCHEDULE_SCRIPT,
            "--input-manifest",
            str(MANIFEST_OUTPUT),
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_OUTPUT),
            "--input-source-registry",
            str(INPUT_SOURCE_REGISTRY_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--output",
            str(JOB_SCHEDULE_OUTPUT),
        )
        run_script(
            JOB_SCHEDULE_SCRIPT,
            "--input-manifest",
            str(MANIFEST_OUTPUT),
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_OUTPUT),
            "--input-source-registry",
            str(INPUT_SOURCE_REGISTRY_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--schedule-profile",
            "external_scheduler",
            "--schedule-plan-id",
            "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
            "--output",
            str(JOB_SCHEDULE_EXTERNAL_OUTPUT),
        )
        run_script(
            OPENCLAW_CRON_CONTRACT_SCRIPT,
            "--output",
            str(OPENCLAW_CRON_CONTRACT_OUTPUT),
        )
        run_script(
            JOB_EXECUTION_CONTEXT_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_EXTERNAL_OUTPUT),
            "--output",
            str(JOB_EXECUTION_CONTEXT_OUTPUT),
        )
        run_script(
            JOB_ARTIFACT_RETENTION_POLICY_SCRIPT,
            "--output",
            str(JOB_ARTIFACT_RETENTION_POLICY_OUTPUT),
        )
        run_script(
            DAILY_JOB_RUN_SCRIPT,
            "--input-manifest",
            str(MANIFEST_OUTPUT),
            "--output",
            str(DAILY_JOB_RUN_OUTPUT),
        )
        run_script(
            WEEKLY_JOB_RUN_SCRIPT,
            "--input-manifest",
            str(MANIFEST_OUTPUT),
            "--weekly-review-window-input",
            str(WEEKLY_REVIEW_WINDOW_OUTPUT),
            "--output",
            str(WEEKLY_JOB_RUN_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_PLAN_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--output",
            str(JOB_SHADOW_COMPARE_PLAN_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_PLAN_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--comparison-scope",
            "daily",
            "--compare-plan-id",
            "optimizer-job-shadow-compare-plan.daily.autotiktok.fixture.2026-04-18",
            "--generated-at",
            "2026-04-18T05:41:00Z",
            "--output",
            str(JOB_SHADOW_COMPARE_PLAN_DAILY_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_PLAN_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--comparison-scope",
            "weekly",
            "--compare-plan-id",
            "optimizer-job-shadow-compare-plan.weekly.autotiktok.fixture.2026-04-18",
            "--generated-at",
            "2026-04-18T05:42:00Z",
            "--output",
            str(JOB_SHADOW_COMPARE_PLAN_WEEKLY_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--input-compare-plan",
            str(JOB_SHADOW_COMPARE_PLAN_OUTPUT),
            "--output",
            str(JOB_SHADOW_COMPARE_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--input-compare-plan",
            str(JOB_SHADOW_COMPARE_PLAN_DAILY_OUTPUT),
            "--compare-id",
            "optimizer-job-shadow-compare.daily.autotiktok.fixture.2026-04-18",
            "--generated-at",
            "2026-04-18T05:46:00Z",
            "--output",
            str(JOB_SHADOW_COMPARE_DAILY_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_OUTPUT),
            "--input-rollout-policy",
            str(INPUT_ROLLOUT_POLICY_OUTPUT),
            "--input-compare-plan",
            str(JOB_SHADOW_COMPARE_PLAN_WEEKLY_OUTPUT),
            "--compare-id",
            "optimizer-job-shadow-compare.weekly.autotiktok.fixture.2026-04-18",
            "--generated-at",
            "2026-04-18T05:47:00Z",
            "--output",
            str(JOB_SHADOW_COMPARE_WEEKLY_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_BATCH_MANIFEST_SCRIPT,
            "--input-compare-artifact",
            str(JOB_SHADOW_COMPARE_DAILY_OUTPUT),
            "--input-compare-artifact",
            str(JOB_SHADOW_COMPARE_WEEKLY_OUTPUT),
            "--output",
            str(JOB_SHADOW_COMPARE_BATCH_MANIFEST_OUTPUT),
        )
        run_script(
            JOB_SHADOW_COMPARE_BATCH_SCRIPT,
            "--input-batch-manifest",
            str(JOB_SHADOW_COMPARE_BATCH_MANIFEST_OUTPUT),
            "--output",
            str(JOB_SHADOW_COMPARE_BATCH_OUTPUT),
        )
        run_script(
            JOB_ORCHESTRATION_CYCLE_SCRIPT,
            "--input-schedule-plan",
            str(JOB_SCHEDULE_EXTERNAL_OUTPUT),
            "--input-execution-context",
            str(JOB_EXECUTION_CONTEXT_OUTPUT),
            "--input-artifact-retention-policy",
            str(JOB_ARTIFACT_RETENTION_POLICY_OUTPUT),
            "--run-summary-output",
            str(JOB_RUN_SUMMARY_OUTPUT),
            "--output",
            str(JOB_ORCHESTRATION_CYCLE_OUTPUT),
        )
        run_script(
            RUN_SUMMARY_SCRIPT,
            "--input-job-orchestration-cycle",
            str(JOB_ORCHESTRATION_CYCLE_OUTPUT),
            "--output",
            str(JOB_RUN_SUMMARY_OUTPUT),
        )
        run_script(
            JOB_ERROR_SCRIPT,
            "--output",
            str(JOB_ERROR_OUTPUT),
        )
        run_script(
            RECENT_RUN_SUMMARIES_SCRIPT,
            "--input-job-orchestration-cycle",
            str(JOB_ORCHESTRATION_CYCLE_OUTPUT),
            "--output",
            str(RECENT_RUN_SUMMARIES_OUTPUT),
        )
        run_script(
            RECENT_COMPARE_SUMMARIES_SCRIPT,
            "--input-job-shadow-compare-batch",
            str(JOB_SHADOW_COMPARE_BATCH_OUTPUT),
            "--input-job-orchestration-cycle",
            str(JOB_ORCHESTRATION_CYCLE_OUTPUT),
            "--output",
            str(RECENT_COMPARE_SUMMARIES_OUTPUT),
        )
        run_script(
            RECENT_WEEKLY_DECISIONS_SCRIPT,
            "--input-job-orchestration-cycle",
            str(JOB_ORCHESTRATION_CYCLE_OUTPUT),
            "--output",
            str(RECENT_WEEKLY_DECISIONS_OUTPUT),
        )
        run_script(
            RECENT_FAILURE_SUMMARIES_SCRIPT,
            "--input-job-error",
            str(JOB_ERROR_OUTPUT),
            "--input-job-orchestration-cycle",
            str(JOB_ORCHESTRATION_CYCLE_OUTPUT),
            "--output",
            str(RECENT_FAILURE_SUMMARIES_OUTPUT),
        )
        run_script(
            EVAL_RUN_SCRIPT,
            "--exclude-weekly-promotion",
            "--input-offline-cycle",
            str(OFFLINE_CYCLE_DAILY_OUTPUT),
            "--eval-run-id",
            "optimizer-eval-run.autotiktok.fixture.2026-04-15.daily",
            "--output",
            str(EVAL_RUN_DAILY_OUTPUT),
        )
        run_script(
            EVAL_RUN_SCRIPT,
            "--input-offline-cycle",
            str(OFFLINE_CYCLE_OUTPUT),
            "--output",
            str(EVAL_RUN_OUTPUT),
        )
        run_script(EVAL_BATCH_MANIFEST_SCRIPT, "--output", str(EVAL_BATCH_MANIFEST_OUTPUT))
        run_script(
            EVAL_WINDOW_SET_SCRIPT,
            "--input-runtime-profile-family-registry",
            str(RUNTIME_PROFILE_FAMILY_REGISTRY_OUTPUT),
            "--input-runtime-profile-rollout-policy",
            str(RUNTIME_PROFILE_ROLLOUT_POLICY_OUTPUT),
            "--output",
            str(EVAL_WINDOW_SET_OUTPUT),
        )
        run_script(
            EVAL_BATCH_HISTORY_MANIFEST_SCRIPT,
            "--input-window-set",
            str(EVAL_WINDOW_SET_OUTPUT),
            "--input-artifact-registry",
            str(RUNTIME_ARTIFACT_REGISTRY_OUTPUT),
            "--input-runtime-profile-catalog",
            str(RUNTIME_PROFILE_CATALOG_OUTPUT),
            "--input-materialization-plan",
            str(RUNTIME_MATERIALIZATION_PLAN_OUTPUT),
            "--output",
            str(EVAL_BATCH_HISTORY_MANIFEST_OUTPUT),
        )
        run_script(
            EVAL_BATCH_SCRIPT,
            "--input-eval-batch-manifest",
            str(EVAL_BATCH_MANIFEST_OUTPUT),
            "--output",
            str(EVAL_BATCH_OUTPUT),
        )
        run_script(
            EVAL_BATCH_SCRIPT,
            "--input-eval-batch-manifest",
            str(EVAL_BATCH_HISTORY_MANIFEST_OUTPUT),
            "--output",
            str(EVAL_BATCH_HISTORY_OUTPUT),
        )
        print(
            "Wrote optimizer sample outputs to "
            f"{BACKFILL_RUN_OUTPUT}, {PERFORMANCE_RUN_OUTPUT}, {CHALLENGER_RUN_OUTPUT}, "
            f"{SOURCE_ARTIFACT_CATALOG_OUTPUT}, "
            f"{SOURCE_PROVIDER_REGISTRY_OUTPUT}, "
            f"{SOURCE_PROVIDER_CATALOG_OUTPUT}, "
            f"{JOB_ARTIFACT_RESOLVER_OUTPUT}, {INPUT_SOURCE_REGISTRY_OUTPUT}, "
            f"{INPUT_ROLLOUT_POLICY_OUTPUT}, "
            f"{MANIFEST_OUTPUT}, {RAW_SHADOW_MANIFEST_OUTPUT}, {REAL_SHADOW_MANIFEST_OUTPUT}, "
            f"{BUNDLE_OUTPUT}, {RUNTIME_ARTIFACT_REGISTRY_OUTPUT}, "
            f"{RUNTIME_PROFILE_CATALOG_OUTPUT}, {RUNTIME_PROFILE_CATALOG_PREVIEW_OUTPUT}, "
            f"{RUNTIME_PROFILE_FAMILY_REGISTRY_OUTPUT}, {RUNTIME_PROFILE_ROLLOUT_POLICY_OUTPUT}, "
            f"{RUNTIME_MATERIALIZATION_PLAN_OUTPUT}, "
            f"{DAILY_OUTPUT}, {WEEKLY_REVIEW_WINDOW_OUTPUT}, "
            f"{WEEKLY_REVIEW_WINDOW_SCALE_OUTPUT}, {WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY_OUTPUT}, "
            f"{WEEKLY_OUTPUT}, {WEEKLY_SCALE_OUTPUT}, {WEEKLY_SEARCH_PRIORITY_OUTPUT}, "
            f"{OFFLINE_CYCLE_DAILY_OUTPUT}, {OFFLINE_CYCLE_OUTPUT}, "
            f"{JOB_SCHEDULE_OUTPUT}, {JOB_SCHEDULE_EXTERNAL_OUTPUT}, {OPENCLAW_CRON_CONTRACT_OUTPUT}, "
            f"{JOB_EXECUTION_CONTEXT_OUTPUT}, {JOB_ARTIFACT_RETENTION_POLICY_OUTPUT}, {JOB_RUN_SUMMARY_OUTPUT}, {JOB_ERROR_OUTPUT}, "
            f"{RECENT_RUN_SUMMARIES_OUTPUT}, {RECENT_COMPARE_SUMMARIES_OUTPUT}, {RECENT_WEEKLY_DECISIONS_OUTPUT}, {RECENT_FAILURE_SUMMARIES_OUTPUT}, "
            f"{JOB_ORCHESTRATION_CYCLE_OUTPUT}, "
            f"{DAILY_JOB_RUN_OUTPUT}, {WEEKLY_JOB_RUN_OUTPUT}, "
            f"{JOB_SHADOW_COMPARE_PLAN_OUTPUT}, {JOB_SHADOW_COMPARE_PLAN_DAILY_OUTPUT}, "
            f"{JOB_SHADOW_COMPARE_PLAN_WEEKLY_OUTPUT}, {JOB_SHADOW_COMPARE_OUTPUT}, "
            f"{JOB_SHADOW_COMPARE_DAILY_OUTPUT}, {JOB_SHADOW_COMPARE_WEEKLY_OUTPUT}, "
            f"{JOB_SHADOW_COMPARE_BATCH_MANIFEST_OUTPUT}, {JOB_SHADOW_COMPARE_BATCH_OUTPUT}, "
            f"{EVAL_RUN_DAILY_OUTPUT}, {EVAL_RUN_OUTPUT}, {EVAL_BATCH_MANIFEST_OUTPUT}, "
            f"{EVAL_WINDOW_SET_OUTPUT}, {EVAL_BATCH_HISTORY_MANIFEST_OUTPUT}, "
            f"{EVAL_BATCH_OUTPUT}, and {EVAL_BATCH_HISTORY_OUTPUT}"
        )
        return 0
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
