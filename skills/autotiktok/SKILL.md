---
name: autotiktok
description: Legacy compatibility hub for the AutoTikTok skill set. Use only when you need the shared AutoTikTok docs root or need help routing work to the newer discovery, ranking, or optimizer skills.
disable-model-invocation: true
---

# AutoTikTok

This is now a compatibility hub, not the preferred main skill.

Prefer the newer functional skills:

- `autotiktok-topic-discovery`
- `autotiktok-topic-ranking`
- `autotiktok-strategy-optimizer`

## How To Use

- Read [docs/technical-plan.md](docs/technical-plan.md) when you need the full master plan.
- Read [docs/development-plan.md](docs/development-plan.md) when you need the 3-owner delivery plan.
- Read [docs/module2-schema-draft.md](docs/module2-schema-draft.md) when you need the current module-2 contract draft.
- Read [references/end-to-end-workflow.md](references/end-to-end-workflow.md) when you need the current cross-skill workflow and smoke-test entry point.
- Run `python3 skills/autotiktok/scripts/sync_all_mock_artifacts.py` when you intentionally want to refresh every committed AutoTikTok mock artifact in dependency order.
- Run `python3 skills/autotiktok/scripts/validate_all_mock_artifacts.py` when you want one gate that checks discovery, shared candidates, ranking output, and optimizer outputs together.
- Run `python3 skills/autotiktok/scripts/validate_artifact_provenance_chain.py` when you want to confirm the committed artifacts still agree on provenance across the whole mock pipeline, including the ranking and optimizer stage matrices.
- Run `python3 skills/autotiktok/scripts/validate_workflow_summary_alignment.py` when you need to confirm the committed workflow summary sample still matches the current deterministic workflow runner.
- Run `python3 skills/autotiktok/scripts/sync_workflow_summary_sample.py` when you intentionally want to regenerate `skills/autotiktok/fixtures/workflow-summary.sample.json`.
- Run `python3 skills/autotiktok/scripts/validate_ranking_profile_matrix_alignment.py` when you need to confirm the committed multi-stage ranking matrix still matches the current deterministic matrix runner.
- Run `python3 skills/autotiktok/scripts/validate_ranking_profile_matrix_expectations.py` when you want to confirm the matrix still expresses the intended stage-mode behavior.
- Run `python3 skills/autotiktok/scripts/sync_ranking_profile_matrix.py` when you intentionally want to regenerate `skills/autotiktok-topic-ranking/fixtures/ranking-profile-matrix.sample.json`.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_alignment.py` when you need to confirm the committed optimizer stage matrix still matches the current deterministic optimizer replay runner.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_expectations.py` when you want a semantic gate on the committed optimizer stage matrix, not just a replay-alignment check.
- Run `python3 skills/autotiktok/scripts/sync_optimizer_stage_matrix.py` when you intentionally want to regenerate `skills/autotiktok/fixtures/optimizer-stage-matrix.sample.json`.
- Run `python3 skills/autotiktok/scripts/run_optimizer_stage_matrix.py` when you want a compact cross-stage daily-review comparison.
- Run `python3 skills/autotiktok/scripts/run_preview_optimizer_stage_matrix.py` when you want the preview-first version of that comparison, with `vNext-preview/exact` as the default lane.
- Run `python3 skills/autotiktok/scripts/validate_preview_lane_cutover.py` when you want to compare `v1/exact` against `vNext-preview/exact` and confirm the optimizer cutover lane preserves stage-matrix plus workflow-summary semantics.
- Run `python3 skills/autotiktok/scripts/validate_preview_lane_consumer_cutover.py` when you want to audit that preview-lane orchestrators now read `optimizerHandoff` rather than deprecated top-level ranking mirrors.
- Run `python3 skills/autotiktok/scripts/validate_preview_default_rollout.py` when you want to confirm preview-first wrappers default to the preview lane and still expose a `--use-current-lane` fallback.
- Run `python3 skills/autotiktok/scripts/list_live_lane_dependencies.py` when you want the current machine-readable inventory of scripts and gates that intentionally still default to the live lane.
- Run `python3 skills/autotiktok/scripts/validate_live_lane_dependency_inventory.py` when you want a governance gate for that inventory.
- Use `skills/autotiktok/fixtures/scoring-context-matrix.fixture.json` when you want to adjust the stage-specific assumptions behind the ranking profile matrix.
- Run `python3 skills/autotiktok/scripts/validate_discovery_output_alignment.py` when you need to confirm the committed discovery sample output still matches the current deterministic discovery runner.
- Run `python3 skills/autotiktok/scripts/validate_discovery_snapshot_materialization_alignment.py` when you want an explicit gate for the snapshot-materialization fixture that now drives discovery by default.
- Run `python3 skills/autotiktok/scripts/validate_discovery_snapshot_ingest_alignment.py` when you want to confirm the committed `source-snapshots / signal-items / video-samples` trio still materializes the committed discovery ingest seam and the committed discovery output.
- Run `python3 skills/autotiktok/scripts/validate_discovery_topic_abstraction_expectations.py` when you want the semantic gate for discovery normalization and topic-abstraction output, not just replay alignment.
- Run `python3 skills/autotiktok/scripts/validate_discovery_merge_packaging_expectations.py` when you want the semantic gate for discovery merge, dedupe, and packaging output, not just replay alignment.
- Run `python3 skills/autotiktok/scripts/validate_discovery_ranking_handoff_alignment.py` when you want the direct handoff gate that proves ranking now defaults to the committed discovery artifact rather than the derived shared candidates fixture.
- Run `python3 skills/autotiktok/scripts/sync_discovery_snapshot_materialization_sample.py` when you intentionally want to regenerate `skills/autotiktok-topic-discovery/fixtures/discovery-snapshot-materialization.sample.json` from the standalone snapshot inputs.
- Run `python3 skills/autotiktok/scripts/sync_discovery_sample_output.py` when you intentionally want to regenerate `skills/autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json`.
- Run `python3 skills/autotiktok/scripts/validate_shared_fixture_alignment.py` when you need to confirm the shared ranking candidates fixture still matches the current discovery output.
- Run `python3 skills/autotiktok/scripts/sync_shared_candidates_fixture.py` when you intentionally want to regenerate `skills/autotiktok/fixtures/topic-candidates.fixture.json` from the discovery sample artifact.
- Run `python3 skills/autotiktok/scripts/validate_ranking_output_alignment.py` when you need to confirm the committed ranking sample output still matches the current deterministic ranking runner.
- Run `python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract.py` when you want an explicit gate for the optimizer-facing subset of ranking output.
- Run `python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py` when you want to verify the preview dual-write handoff path (`optimizerHandoff`) before changing module-2 consumers.
- Use `skills/autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json` when you need the current preview deprecation policy for the ranking-to-optimizer handoff, including the declared `ranking-optimizer-contract.v2` hard-fail target.
- Run `python3 skills/autotiktok/scripts/sync_ranking_sample_output.py` when you intentionally want to regenerate `skills/autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json`.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_output_alignment.py` when you need to confirm the committed optimizer sample outputs still match the current deterministic generators, including the offline-cycle and history-replay families.
- Run `python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py` when you intentionally want to regenerate the committed optimizer sample family, including `daily-review.sample.json`, `weekly-promotion.sample.json`, `optimizer-offline-cycle*.sample.json`, `optimizer-eval-run*.sample.json`, `optimizer-eval-batch*.sample.json`, `optimizer-eval-window-set.sample.json`, and the history-replay eval-batch samples.
- Read `skills/autotiktok-strategy-optimizer/references/openclaw-cron-ops.md` when you need the preferred operator-facing runbook for recurring AutoTikTok optimizer jobs on an OpenClaw Gateway.
- The committed optimizer sample family now also includes `optimizer-source-artifact-catalog.sample.json`, `optimizer-source-provider-registry.sample.json`, `optimizer-source-provider-catalog.sample.json`, `optimizer-input-rollout-policy.sample.json`, `optimizer-openclaw-cron-contract.sample.json`, `optimizer-job-schedule*.sample.json`, `optimizer-job-execution-context.sample.json`, `optimizer-job-orchestration-cycle.sample.json`, `optimizer-run-summary.sample.json`, `optimizer-job-error.sample.json`, `optimizer-recent-*.sample.json`, `optimizer-job-shadow-compare-plan*.sample.json`, `optimizer-job-shadow-compare*.sample.json`, `optimizer-job-shadow-compare-batch*.sample.json`, and `optimizer-weekly-review-window.sample.json`, so source-provider resolution, artifact-catalog resolution, input-lane rollout, standard OpenClaw cron management, external scheduler contracts, scheduler-facing execution context, scheduler-facing orchestration-cycle aggregation, scheduler-facing run summaries, structured job failures, dashboard-facing recent aggregates, scheduler-facing shadow compare planning, scheduler-facing shadow compare results, scheduler-facing shadow compare batching, and weekly promotion all have explicit artifacts rather than only implicit script behavior.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_openclaw_cron_runtime_alignment.py` when you want the focused gate for the preferred standard cron runtime.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_scheduler_compatibility_role_alignment.py` when you want the semantic gate that proves the legacy scheduler-facing artifacts remain compatibility-only rehearsal contracts.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_external_alignment.py` when you want the external-scheduler companion gate that proves `optimizer-job-schedule.external.sample.json` still regenerates deterministically and that scheduler-supplied inputs plus `output_root` dispatch still materialize valid daily/weekly job runs.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_job_execution_context_alignment.py` when you want the deterministic gate for `optimizer-job-execution-context.sample.json`.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_job_orchestration_cycle_alignment.py` when you want the higher-level scheduler gate that proves one committed execution context still materializes a full production-plus-shadow orchestration cycle deterministically.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_rollout_alignment.py` when you want a scheduler-level gate that proves `raw_shadow_validation` and `real_shadow_validation` rollout classes still preserve production daily/weekly semantics.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_alignment.py` when you want the committed scheduler-facing compare artifact that freezes `daily_raw_shadow_vs_production` plus `weekly_real_shadow_vs_production` and proves it still regenerates deterministically.
- Run `python3 skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_batch_alignment.py` when you want the scheduler-facing compare batch gate that proves the committed daily/weekly compare family still rolls up into one deterministic grouped compare artifact.
- Run `python3 skills/autotiktok/scripts/validate_weekly_strategy_realism.py` when you want the semantic gate for `daily-review -> optimizer-weekly-review-window -> weekly-promotion`, including rollback behavior.
- The committed `optimizer-eval-window-set.sample.json` now uses a top-level runtime-source catalog and per-window `runtimeSourceId` references, rather than repeating concrete input paths on every window entry. Its default descriptor lane is now planner-oriented (`planner_runtime_binding` with `profileId`) rather than fixture-name-oriented, and descriptor resolution can now be externalized through `optimizer-runtime-profile-rollout-policy.sample.json`, `optimizer-runtime-profile-family-registry.sample.json`, `optimizer-runtime-profile-catalog.sample.json`, and `optimizer-runtime-artifact-registry.sample.json`.
- That runtime profile catalog now has an explicit family/version contract, and the window-set sample carries a matching `runtimeProfileCatalogReference` so resolver drift is caught before history-manifest materialization.
- There is now also a committed `optimizer-runtime-profile-family-registry.sample.json`, and the window-set sample records `runtimeProfileFamilyRegistryReference` so planner family/lane selection is explicit before catalog resolution.
- There is now also a committed `optimizer-runtime-profile-rollout-policy.sample.json`, and the window-set sample records `runtimeProfileRolloutPolicyReference` plus lane-selection provenance so scheduler default rollout, class-based canaries (`production` vs `preview_canary`), and explicit preview overrides are distinguishable.
- The rollout policy sample now also carries rule-based routing for preview canaries, so a scheduler can either mark a batch like `preview:...` or set `windowSetPurpose=preview_validation` and let the window-set builder resolve `preview_canary` automatically.
- The rollout policy sample now carries `evalPurposeTemplateFamilies`, `evalPurposeTemplates`, and `evalPurposePolicies`, so scheduler-facing batches can inherit a reusable scheduler-default family from `windowSetPurpose` before any finer-grained rule matching is applied.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_catalog_cutover.py` when you want the runtime profile catalog equivalent of the ranking contract preview rehearsal: current lane vs preview catalog lane, with alias-based compatibility for legacy planner profile requests.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_cutover.py` when you want the scheduler-rollout equivalent of that rehearsal: current vs preview policy defaults, without passing an explicit lane override.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_purpose_routing.py` when you want to verify explicit planner-intent routing (`windowSetPurpose=preview_validation`) from the rollout policy itself.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_rule_routing.py` when you want to verify rule-driven canary routing from the rollout policy itself.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_window_mode_routing.py` when you want to verify scheduler-shaped composite routing from planner intent plus window-level selectors such as `historyWindowLabel` and `mode`.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_dimension_routing.py` when you want to verify planner-level batch metadata routing from `windowSetPurpose`, `windowSetBatchType`, and `comparisonDimension`.
- Run `python3 skills/autotiktok/scripts/run_autotiktok_workflow.py` when you need a single mock end-to-end execution path across discovery, ranking, and optimizer. Pass `--ranking-contract-version ranking-optimizer-contract.vNext-preview --ranking-contract-validation-mode exact` when you want the preview cutover lane instead of the current live lane.
- Run `python3 skills/autotiktok/scripts/run_preview_autotiktok_workflow.py` when you want that end-to-end workflow to default to the preview canonical lane rather than the live lane.
- Use this hub only as a shared docs root or routing page.

## Scope

This directory now acts as shared AutoTikTok project material:

- master technical plan
- development plan
- module-2 schema draft
- shared fixtures

Implementation-focused work should happen through the three functional skills above.
