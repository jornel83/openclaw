#!/usr/bin/env python3
"""
Validate that committed optimizer sample outputs match current deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DAILY_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "daily_review_mock.py"
)
WEEKLY_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "weekly_promotion_mock.py"
)
BUILD_WEEKLY_REVIEW_WINDOW_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_weekly_review_window.py"
)
COMMITTED_BACKFILL_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "topic-outcome-backfill-run.sample.json"
)
COMMITTED_PERFORMANCE_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "post-performance-signal-run.sample.json"
)
COMMITTED_CHALLENGER_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "challenger-evaluation-run.sample.json"
)
COMMITTED_MANIFEST = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-input-manifest.sample.json"
)
COMMITTED_INPUT_ROLLOUT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-rollout-policy.sample.json"
)
COMMITTED_DAILY = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "daily-review.sample.json"
)
COMMITTED_WEEKLY_REVIEW_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)
COMMITTED_WEEKLY_REVIEW_WINDOW_SCALE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.scale.sample.json"
)
COMMITTED_WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.search-priority.sample.json"
)
COMMITTED_WEEKLY = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "weekly-promotion.sample.json"
)
COMMITTED_WEEKLY_SCALE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.scale.sample.json"
)
COMMITTED_WEEKLY_SEARCH_PRIORITY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "weekly-promotion.search-priority.sample.json"
)
COMMITTED_EVAL_RUN = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-eval-run.sample.json"
)
COMMITTED_EVAL_RUN_DAILY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-run-daily.sample.json"
)
COMMITTED_OFFLINE_CYCLE_DAILY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-offline-cycle-daily.sample.json"
)
COMMITTED_OFFLINE_CYCLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-offline-cycle.sample.json"
)
COMMITTED_JOB_SCHEDULE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json"
)
COMMITTED_EXTERNAL_JOB_SCHEDULE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.external.sample.json"
)
COMMITTED_DAILY_JOB_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-daily-job-run.sample.json"
)
COMMITTED_WEEKLY_JOB_RUN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-job-run.sample.json"
)
COMMITTED_EVAL_BATCH_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-batch-manifest.sample.json"
)
COMMITTED_EVAL_BATCH_HISTORY_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-batch-history-manifest.sample.json"
)
COMMITTED_EVAL_WINDOW_SET = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-window-set.sample.json"
)
COMMITTED_EVAL_BATCH = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-eval-batch.sample.json"
)
COMMITTED_EVAL_BATCH_HISTORY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-eval-batch-history.sample.json"
)
COMMITTED_BUNDLE = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "fixtures" / "optimizer-input-bundle.sample.json"
)
COMMITTED_RUNTIME_ARTIFACT_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-artifact-registry.sample.json"
)
COMMITTED_RUNTIME_PROFILE_CATALOG = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-catalog.sample.json"
)
COMMITTED_RUNTIME_PROFILE_CATALOG_PREVIEW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-catalog-preview.sample.json"
)
COMMITTED_RUNTIME_PROFILE_FAMILY_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-family-registry.sample.json"
)
COMMITTED_RUNTIME_PROFILE_ROLLOUT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-rollout-policy.sample.json"
)
COMMITTED_RUNTIME_MATERIALIZATION_PLAN = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-materialization-plan.sample.json"
)
BUILD_BUNDLE_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "materialize_optimizer_input_bundle.py"
)
BUILD_RUNTIME_ARTIFACT_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_artifact_registry.py"
)
BUILD_RUNTIME_PROFILE_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_catalog.py"
)
BUILD_RUNTIME_PROFILE_FAMILY_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_family_registry.py"
)
BUILD_RUNTIME_PROFILE_ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_profile_rollout_policy.py"
)
BUILD_RUNTIME_MATERIALIZATION_PLAN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_runtime_materialization_plan.py"
)
BUILD_MANIFEST_SCRIPT = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts" / "build_optimizer_input_manifest.py"
)
BUILD_INPUT_ROLLOUT_POLICY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_rollout_policy.py"
)
BUILD_BACKFILL_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_topic_outcome_backfill_run.py"
)
BUILD_PERFORMANCE_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_post_performance_signal_run.py"
)
BUILD_CHALLENGER_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_challenger_evaluation_run.py"
)
BUILD_EVAL_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_run.py"
)
BUILD_OFFLINE_CYCLE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_offline_optimizer_cycle.py"
)
BUILD_JOB_SCHEDULE_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_schedule.py"
)
BUILD_DAILY_JOB_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_daily_optimizer_job.py"
)
BUILD_WEEKLY_JOB_RUN_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "run_weekly_optimizer_job.py"
)
BUILD_EVAL_BATCH_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch_manifest.py"
)
BUILD_EVAL_BATCH_HISTORY_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch_history_manifest.py"
)
BUILD_EVAL_WINDOW_SET_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_window_set.py"
)
BUILD_EVAL_BATCH_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_eval_batch.py"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-alignment-") as temp_dir:
            temp_root = Path(temp_dir)
            backfill_run_path = temp_root / "topic-outcome-backfill-run.json"
            performance_run_path = temp_root / "post-performance-signal-run.json"
            challenger_run_path = temp_root / "challenger-evaluation-run.json"
            manifest_path = temp_root / "optimizer-input-manifest.json"
            input_rollout_policy_path = (
                temp_root / "optimizer-input-rollout-policy.json"
            )
            bundle_path = temp_root / "optimizer-input-bundle.json"
            runtime_artifact_registry_path = (
                temp_root / "optimizer-runtime-artifact-registry.json"
            )
            runtime_profile_catalog_path = (
                temp_root / "optimizer-runtime-profile-catalog.json"
            )
            runtime_profile_catalog_preview_path = (
                temp_root / "optimizer-runtime-profile-catalog-preview.json"
            )
            runtime_profile_family_registry_path = (
                temp_root / "optimizer-runtime-profile-family-registry.json"
            )
            runtime_profile_rollout_policy_path = (
                temp_root / "optimizer-runtime-profile-rollout-policy.json"
            )
            runtime_materialization_plan_path = (
                temp_root / "optimizer-runtime-materialization-plan.json"
            )
            daily_path = temp_root / "daily-review.json"
            weekly_review_window_path = (
                temp_root / "optimizer-weekly-review-window.json"
            )
            weekly_review_window_scale_path = (
                temp_root / "optimizer-weekly-review-window.scale.json"
            )
            weekly_review_window_search_priority_path = (
                temp_root / "optimizer-weekly-review-window.search-priority.json"
            )
            weekly_path = temp_root / "weekly-promotion.json"
            weekly_scale_path = temp_root / "weekly-promotion.scale.json"
            weekly_search_priority_path = (
                temp_root / "weekly-promotion.search-priority.json"
            )
            offline_cycle_daily_path = temp_root / "optimizer-offline-cycle-daily.json"
            offline_cycle_path = temp_root / "optimizer-offline-cycle.json"
            job_schedule_path = temp_root / "optimizer-job-schedule.json"
            external_job_schedule_path = (
                temp_root / "optimizer-job-schedule.external.json"
            )
            daily_job_run_path = temp_root / "optimizer-daily-job-run.json"
            weekly_job_run_path = temp_root / "optimizer-weekly-job-run.json"
            eval_run_daily_path = temp_root / "optimizer-eval-run-daily.json"
            eval_run_path = temp_root / "optimizer-eval-run.json"
            eval_batch_manifest_path = temp_root / "optimizer-eval-batch-manifest.json"
            eval_window_set_path = temp_root / "optimizer-eval-window-set.json"
            eval_batch_history_manifest_path = (
                temp_root / "optimizer-eval-batch-history-manifest.json"
            )
            eval_batch_path = temp_root / "optimizer-eval-batch.json"
            eval_batch_history_path = temp_root / "optimizer-eval-batch-history.json"
            run_script(BUILD_BACKFILL_RUN_SCRIPT, "--output", str(backfill_run_path))
            run_script(
                BUILD_PERFORMANCE_RUN_SCRIPT, "--output", str(performance_run_path)
            )
            run_script(BUILD_CHALLENGER_RUN_SCRIPT, "--output", str(challenger_run_path))
            run_script(BUILD_MANIFEST_SCRIPT, "--output", str(manifest_path))
            run_script(
                BUILD_INPUT_ROLLOUT_POLICY_SCRIPT,
                "--output",
                str(input_rollout_policy_path),
            )
            run_script(BUILD_BUNDLE_SCRIPT, "--input-manifest", str(manifest_path), "--output", str(bundle_path))
            run_script(
                BUILD_RUNTIME_ARTIFACT_REGISTRY_SCRIPT,
                "--output",
                str(runtime_artifact_registry_path),
            )
            run_script(
                BUILD_RUNTIME_PROFILE_CATALOG_SCRIPT,
                "--output",
                str(runtime_profile_catalog_path),
            )
            run_script(
                BUILD_RUNTIME_PROFILE_CATALOG_SCRIPT,
                "--catalog-lane",
                "preview",
                "--output",
                str(runtime_profile_catalog_preview_path),
            )
            run_script(
                BUILD_RUNTIME_PROFILE_FAMILY_REGISTRY_SCRIPT,
                "--output",
                str(runtime_profile_family_registry_path),
            )
            run_script(
                BUILD_RUNTIME_PROFILE_ROLLOUT_POLICY_SCRIPT,
                "--input-runtime-profile-family-registry",
                str(runtime_profile_family_registry_path),
                "--output",
                str(runtime_profile_rollout_policy_path),
            )
            run_script(
                BUILD_RUNTIME_MATERIALIZATION_PLAN_SCRIPT,
                "--output",
                str(runtime_materialization_plan_path),
            )
            generated_backfill_run = load_json(backfill_run_path)
            committed_backfill_run = load_json(COMMITTED_BACKFILL_RUN)
            generated_performance_run = load_json(performance_run_path)
            committed_performance_run = load_json(COMMITTED_PERFORMANCE_RUN)
            generated_challenger_run = load_json(challenger_run_path)
            committed_challenger_run = load_json(COMMITTED_CHALLENGER_RUN)
            generated_manifest = load_json(manifest_path)
            committed_manifest = load_json(COMMITTED_MANIFEST)
            generated_input_rollout_policy = load_json(input_rollout_policy_path)
            committed_input_rollout_policy = load_json(COMMITTED_INPUT_ROLLOUT_POLICY)
            generated_runtime_artifact_registry = load_json(
                runtime_artifact_registry_path
            )
            committed_runtime_artifact_registry = load_json(
                COMMITTED_RUNTIME_ARTIFACT_REGISTRY
            )
            generated_runtime_profile_catalog = load_json(
                runtime_profile_catalog_path
            )
            committed_runtime_profile_catalog = load_json(
                COMMITTED_RUNTIME_PROFILE_CATALOG
            )
            generated_runtime_profile_catalog_preview = load_json(
                runtime_profile_catalog_preview_path
            )
            committed_runtime_profile_catalog_preview = load_json(
                COMMITTED_RUNTIME_PROFILE_CATALOG_PREVIEW
            )
            generated_runtime_profile_family_registry = load_json(
                runtime_profile_family_registry_path
            )
            committed_runtime_profile_family_registry = load_json(
                COMMITTED_RUNTIME_PROFILE_FAMILY_REGISTRY
            )
            generated_runtime_profile_rollout_policy = load_json(
                runtime_profile_rollout_policy_path
            )
            committed_runtime_profile_rollout_policy = load_json(
                COMMITTED_RUNTIME_PROFILE_ROLLOUT_POLICY
            )
            generated_runtime_materialization_plan = load_json(
                runtime_materialization_plan_path
            )
            committed_runtime_materialization_plan = load_json(
                COMMITTED_RUNTIME_MATERIALIZATION_PLAN
            )
            run_script(
                DAILY_SCRIPT,
                "--input-bundle",
                str(bundle_path),
                "--output",
                str(daily_path),
            )
            run_script(
                BUILD_WEEKLY_REVIEW_WINDOW_SCRIPT,
                "--daily-review-input",
                str(daily_path),
                "--output",
                str(weekly_review_window_path),
            )
            run_script(
                BUILD_WEEKLY_REVIEW_WINDOW_SCRIPT,
                "--daily-review-input",
                str(daily_path),
                "--stage-mode",
                "scale",
                "--review-window-id",
                "optimizer-weekly-review-window.scale.autotiktok.fixture.2026-04-20",
                "--output",
                str(weekly_review_window_scale_path),
            )
            run_script(
                BUILD_WEEKLY_REVIEW_WINDOW_SCRIPT,
                "--daily-review-input",
                str(daily_path),
                "--stage-mode",
                "search_priority",
                "--review-window-id",
                "optimizer-weekly-review-window.search-priority.autotiktok.fixture.2026-04-20",
                "--output",
                str(weekly_review_window_search_priority_path),
            )
            run_script(
                WEEKLY_SCRIPT,
                "--weekly-review-window-input",
                str(weekly_review_window_path),
                "--output",
                str(weekly_path),
            )
            run_script(
                WEEKLY_SCRIPT,
                "--weekly-review-window-input",
                str(weekly_review_window_scale_path),
                "--output",
                str(weekly_scale_path),
            )
            run_script(
                WEEKLY_SCRIPT,
                "--weekly-review-window-input",
                str(weekly_review_window_search_priority_path),
                "--output",
                str(weekly_search_priority_path),
            )
            run_script(
                BUILD_OFFLINE_CYCLE_SCRIPT,
                "--input-manifest",
                str(manifest_path),
                "--cycle-id",
                "optimizer-offline-cycle.autotiktok.fixture.2026-04-15.daily",
                "--report-id",
                "daily-review.autotiktok.fixture.2026-04-15.daily",
                "--output",
                str(offline_cycle_daily_path),
            )
            run_script(
                BUILD_OFFLINE_CYCLE_SCRIPT,
                "--input-bundle",
                str(bundle_path),
                "--include-weekly-promotion",
                "--weekly-review-window-input",
                str(weekly_review_window_path),
                "--output",
                str(offline_cycle_path),
            )
            run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--input-manifest",
                str(COMMITTED_MANIFEST),
                "--input-source-registry",
                str(ROOT / generated_input_rollout_policy["inputSourceRegistryReference"]["path"]),
                "--input-rollout-policy",
                str(COMMITTED_INPUT_ROLLOUT_POLICY),
                "--output",
                str(job_schedule_path),
            )
            run_script(
                BUILD_JOB_SCHEDULE_SCRIPT,
                "--input-manifest",
                str(COMMITTED_MANIFEST),
                "--input-source-registry",
                str(
                    ROOT
                    / generated_input_rollout_policy["inputSourceRegistryReference"][
                        "path"
                    ]
                ),
                "--input-rollout-policy",
                str(COMMITTED_INPUT_ROLLOUT_POLICY),
                "--schedule-profile",
                "external_scheduler",
                "--schedule-plan-id",
                "optimizer-job-schedule.external.autotiktok.fixture.2026-04-18",
                "--output",
                str(external_job_schedule_path),
            )
            run_script(
                BUILD_DAILY_JOB_RUN_SCRIPT,
                "--input-manifest",
                str(manifest_path),
                "--output",
                str(daily_job_run_path),
            )
            run_script(
                BUILD_WEEKLY_JOB_RUN_SCRIPT,
                "--input-manifest",
                str(manifest_path),
                "--weekly-review-window-input",
                str(weekly_review_window_path),
                "--output",
                str(weekly_job_run_path),
            )
            run_script(
                BUILD_EVAL_RUN_SCRIPT,
                "--exclude-weekly-promotion",
                "--input-offline-cycle",
                str(offline_cycle_daily_path),
                "--eval-run-id",
                "optimizer-eval-run.autotiktok.fixture.2026-04-15.daily",
                "--output",
                str(eval_run_daily_path),
            )
            run_script(
                BUILD_EVAL_RUN_SCRIPT,
                "--input-offline-cycle",
                str(offline_cycle_path),
                "--output",
                str(eval_run_path),
            )
            run_script(
                BUILD_EVAL_BATCH_MANIFEST_SCRIPT,
                "--output",
                str(eval_batch_manifest_path),
            )
            run_script(
                BUILD_EVAL_WINDOW_SET_SCRIPT,
                "--input-runtime-profile-family-registry",
                str(runtime_profile_family_registry_path),
                "--input-runtime-profile-rollout-policy",
                str(runtime_profile_rollout_policy_path),
                "--output",
                str(eval_window_set_path),
            )
            run_script(
                BUILD_EVAL_BATCH_HISTORY_MANIFEST_SCRIPT,
                "--input-window-set",
                str(eval_window_set_path),
                "--input-artifact-registry",
                str(runtime_artifact_registry_path),
                "--input-runtime-profile-catalog",
                str(runtime_profile_catalog_path),
                "--input-materialization-plan",
                str(runtime_materialization_plan_path),
                "--output",
                str(eval_batch_history_manifest_path),
            )
            run_script(
                BUILD_EVAL_BATCH_SCRIPT,
                "--input-eval-batch-manifest",
                str(eval_batch_manifest_path),
                "--output",
                str(eval_batch_path),
            )
            run_script(
                BUILD_EVAL_BATCH_SCRIPT,
                "--input-eval-batch-manifest",
                str(eval_batch_history_manifest_path),
                "--output",
                str(eval_batch_history_path),
            )
            generated_bundle = load_json(bundle_path)
            committed_bundle = load_json(COMMITTED_BUNDLE)
            generated_daily = load_json(daily_path)
            committed_daily = load_json(COMMITTED_DAILY)
            generated_weekly_review_window = load_json(weekly_review_window_path)
            committed_weekly_review_window = load_json(COMMITTED_WEEKLY_REVIEW_WINDOW)
            generated_weekly_review_window_scale = load_json(
                weekly_review_window_scale_path
            )
            committed_weekly_review_window_scale = load_json(
                COMMITTED_WEEKLY_REVIEW_WINDOW_SCALE
            )
            generated_weekly_review_window_search_priority = load_json(
                weekly_review_window_search_priority_path
            )
            committed_weekly_review_window_search_priority = load_json(
                COMMITTED_WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY
            )
            generated_weekly = load_json(weekly_path)
            committed_weekly = load_json(COMMITTED_WEEKLY)
            generated_weekly_scale = load_json(weekly_scale_path)
            committed_weekly_scale = load_json(COMMITTED_WEEKLY_SCALE)
            generated_weekly_search_priority = load_json(weekly_search_priority_path)
            committed_weekly_search_priority = load_json(
                COMMITTED_WEEKLY_SEARCH_PRIORITY
            )
            generated_offline_cycle_daily = load_json(offline_cycle_daily_path)
            committed_offline_cycle_daily = load_json(COMMITTED_OFFLINE_CYCLE_DAILY)
            generated_offline_cycle = load_json(offline_cycle_path)
            committed_offline_cycle = load_json(COMMITTED_OFFLINE_CYCLE)
            generated_job_schedule = load_json(job_schedule_path)
            committed_job_schedule = load_json(COMMITTED_JOB_SCHEDULE)
            generated_external_job_schedule = load_json(external_job_schedule_path)
            committed_external_job_schedule = load_json(COMMITTED_EXTERNAL_JOB_SCHEDULE)
            generated_daily_job_run = load_json(daily_job_run_path)
            committed_daily_job_run = load_json(COMMITTED_DAILY_JOB_RUN)
            generated_weekly_job_run = load_json(weekly_job_run_path)
            committed_weekly_job_run = load_json(COMMITTED_WEEKLY_JOB_RUN)
            generated_eval_run_daily = load_json(eval_run_daily_path)
            committed_eval_run_daily = load_json(COMMITTED_EVAL_RUN_DAILY)
            generated_eval_run = load_json(eval_run_path)
            committed_eval_run = load_json(COMMITTED_EVAL_RUN)
            generated_eval_batch_manifest = load_json(eval_batch_manifest_path)
            committed_eval_batch_manifest = load_json(COMMITTED_EVAL_BATCH_MANIFEST)
            generated_eval_window_set = load_json(eval_window_set_path)
            committed_eval_window_set = load_json(COMMITTED_EVAL_WINDOW_SET)
            generated_eval_batch_history_manifest = load_json(
                eval_batch_history_manifest_path
            )
            committed_eval_batch_history_manifest = load_json(
                COMMITTED_EVAL_BATCH_HISTORY_MANIFEST
            )
            generated_eval_batch = load_json(eval_batch_path)
            committed_eval_batch = load_json(COMMITTED_EVAL_BATCH)
            generated_eval_batch_history = load_json(eval_batch_history_path)
            committed_eval_batch_history = load_json(COMMITTED_EVAL_BATCH_HISTORY)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_backfill_run != committed_backfill_run:
        print("[ERROR] committed topic-outcome-backfill-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_performance_run != committed_performance_run:
        print("[ERROR] committed post-performance-signal-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_challenger_run != committed_challenger_run:
        print("[ERROR] committed challenger-evaluation-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_manifest != committed_manifest:
        print("[ERROR] committed optimizer-input-manifest.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_input_rollout_policy != committed_input_rollout_policy:
        print(
            "[ERROR] committed optimizer-input-rollout-policy.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_bundle != committed_bundle:
        print("[ERROR] committed optimizer-input-bundle.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_runtime_artifact_registry != committed_runtime_artifact_registry:
        print(
            "[ERROR] committed optimizer-runtime-artifact-registry.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_runtime_profile_catalog != committed_runtime_profile_catalog:
        print(
            "[ERROR] committed optimizer-runtime-profile-catalog.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if (
        generated_runtime_profile_catalog_preview
        != committed_runtime_profile_catalog_preview
    ):
        print(
            "[ERROR] committed optimizer-runtime-profile-catalog-preview.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if (
        generated_runtime_profile_family_registry
        != committed_runtime_profile_family_registry
    ):
        print(
            "[ERROR] committed optimizer-runtime-profile-family-registry.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if (
        generated_runtime_profile_rollout_policy
        != committed_runtime_profile_rollout_policy
    ):
        print(
            "[ERROR] committed optimizer-runtime-profile-rollout-policy.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_runtime_materialization_plan != committed_runtime_materialization_plan:
        print(
            "[ERROR] committed optimizer-runtime-materialization-plan.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_daily != committed_daily:
        print("[ERROR] committed daily-review.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_weekly_review_window != committed_weekly_review_window:
        print(
            "[ERROR] committed optimizer-weekly-review-window.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_weekly_review_window_scale != committed_weekly_review_window_scale:
        print(
            "[ERROR] committed optimizer-weekly-review-window.scale.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if (
        generated_weekly_review_window_search_priority
        != committed_weekly_review_window_search_priority
    ):
        print(
            "[ERROR] committed optimizer-weekly-review-window.search-priority.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_weekly != committed_weekly:
        print("[ERROR] committed weekly-promotion.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_weekly_scale != committed_weekly_scale:
        print("[ERROR] committed weekly-promotion.scale.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_weekly_search_priority != committed_weekly_search_priority:
        print(
            "[ERROR] committed weekly-promotion.search-priority.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_offline_cycle_daily != committed_offline_cycle_daily:
        print("[ERROR] committed optimizer-offline-cycle-daily.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_offline_cycle != committed_offline_cycle:
        print("[ERROR] committed optimizer-offline-cycle.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_job_schedule != committed_job_schedule:
        print("[ERROR] committed optimizer-job-schedule.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_external_job_schedule != committed_external_job_schedule:
        print(
            "[ERROR] committed optimizer-job-schedule.external.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_daily_job_run != committed_daily_job_run:
        print("[ERROR] committed optimizer-daily-job-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_weekly_job_run != committed_weekly_job_run:
        print("[ERROR] committed optimizer-weekly-job-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_run_daily != committed_eval_run_daily:
        print("[ERROR] committed optimizer-eval-run-daily.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_run != committed_eval_run:
        print("[ERROR] committed optimizer-eval-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_batch_manifest != committed_eval_batch_manifest:
        print("[ERROR] committed optimizer-eval-batch-manifest.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_window_set != committed_eval_window_set:
        print("[ERROR] committed optimizer-eval-window-set.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_batch_history_manifest != committed_eval_batch_history_manifest:
        print(
            "[ERROR] committed optimizer-eval-batch-history-manifest.sample.json is out of sync"
        )
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_batch != committed_eval_batch:
        print("[ERROR] committed optimizer-eval-batch.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    if generated_eval_batch_history != committed_eval_batch_history:
        print("[ERROR] committed optimizer-eval-batch-history.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py")
        return 1

    print("Optimizer sample outputs are aligned with current deterministic generation.")
    print(f"Backfill run sample: {COMMITTED_BACKFILL_RUN}")
    print(f"Performance run sample: {COMMITTED_PERFORMANCE_RUN}")
    print(f"Challenger run sample: {COMMITTED_CHALLENGER_RUN}")
    print(f"Input manifest: {COMMITTED_MANIFEST}")
    print(f"Input rollout policy: {COMMITTED_INPUT_ROLLOUT_POLICY}")
    print(f"Input bundle: {COMMITTED_BUNDLE}")
    print(f"Runtime artifact registry: {COMMITTED_RUNTIME_ARTIFACT_REGISTRY}")
    print(f"Runtime profile catalog: {COMMITTED_RUNTIME_PROFILE_CATALOG}")
    print(
        "Runtime profile catalog preview: "
        f"{COMMITTED_RUNTIME_PROFILE_CATALOG_PREVIEW}"
    )
    print(
        "Runtime profile family registry: "
        f"{COMMITTED_RUNTIME_PROFILE_FAMILY_REGISTRY}"
    )
    print(
        "Runtime profile rollout policy: "
        f"{COMMITTED_RUNTIME_PROFILE_ROLLOUT_POLICY}"
    )
    print(
        f"Runtime materialization plan: {COMMITTED_RUNTIME_MATERIALIZATION_PLAN}"
    )
    print(f"Daily sample: {COMMITTED_DAILY}")
    print(
        "Weekly review window samples: "
        f"{COMMITTED_WEEKLY_REVIEW_WINDOW}, {COMMITTED_WEEKLY_REVIEW_WINDOW_SCALE}, "
        f"{COMMITTED_WEEKLY_REVIEW_WINDOW_SEARCH_PRIORITY}"
    )
    print(
        "Weekly samples: "
        f"{COMMITTED_WEEKLY}, {COMMITTED_WEEKLY_SCALE}, {COMMITTED_WEEKLY_SEARCH_PRIORITY}"
    )
    print(f"Offline cycle daily sample: {COMMITTED_OFFLINE_CYCLE_DAILY}")
    print(f"Offline cycle sample: {COMMITTED_OFFLINE_CYCLE}")
    print(
        f"Job schedule samples: {COMMITTED_JOB_SCHEDULE}, "
        f"{COMMITTED_EXTERNAL_JOB_SCHEDULE}"
    )
    print(f"Daily job run sample: {COMMITTED_DAILY_JOB_RUN}")
    print(f"Weekly job run sample: {COMMITTED_WEEKLY_JOB_RUN}")
    print(f"Eval daily sample: {COMMITTED_EVAL_RUN_DAILY}")
    print(f"Eval run sample: {COMMITTED_EVAL_RUN}")
    print(f"Eval batch manifest sample: {COMMITTED_EVAL_BATCH_MANIFEST}")
    print(f"Eval window set sample: {COMMITTED_EVAL_WINDOW_SET}")
    print(
        f"Eval batch history manifest sample: {COMMITTED_EVAL_BATCH_HISTORY_MANIFEST}"
    )
    print(f"Eval batch sample: {COMMITTED_EVAL_BATCH}")
    print(f"Eval batch history sample: {COMMITTED_EVAL_BATCH_HISTORY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
