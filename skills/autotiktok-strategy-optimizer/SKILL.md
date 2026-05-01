---
name: autotiktok-strategy-optimizer
description: Evaluate and optimize the AutoTikTok ranking strategy over time. Use when defining or updating outcome backfill, topic reward, performance reward, combined reward, daily review, shadow challengers, weekly promotion, or offline optimization rules for the AutoTikTok project.
---

# AutoTikTok Strategy Optimizer

Use this skill when the task is about post-ranking evaluation, reward design, and strategy iteration.

## What This Skill Owns

- `topicOutcomeBackfill`
- `postPerformanceSignal`
- `topicRewardBreakdown`
- `combinedRewardBreakdown`
- daily review
- shadow challenger evaluation
- weekly champion promotion
- optimizer guardrails
- ranking-layer rejection and rerank diagnostics after scoring
- ranking profile-selection provenance after scoring

## Read First

- Read [references/reward-and-backfill.md](references/reward-and-backfill.md) for reward formulas, performance enhancement signals, and backfill windows.
- Read [references/optimizer-loop.md](references/optimizer-loop.md) for daily review, shadow challengers, weekly promotion, and guardrails.
- Read [references/optimizer-artifacts.md](references/optimizer-artifacts.md) for the mock input and output artifacts shipped with this skill.
- Read [references/optimizer-delivery.md](references/optimizer-delivery.md) for owner scope, milestone order, and optimization deliverables.

## Working Rules

- Keep topic-level evaluation primary and post-performance as an enhancement signal.
- Do not let playback or view counts become the sole truth signal.
- Daily optimization may generate and compare shadow challengers.
- Daily optimization must not directly replace the online champion.
- Weekly promotion must respect hard gates such as duplicate-rate, executable-rate, and holdout safety.
- Weekly promotion artifacts should explain champion rollback review explicitly, including eligibility, severity, and reason codes when rollback watch/warning/critical is in play.
- Weekly promotion should also carry the applied stage-specific gate profile, so `growth`, `scale`, and `search_priority` lanes can use different weekly thresholds without hiding which policy decided the outcome.
- Do not change schema or evaluator rules just to improve a challenger score.

## Output Expectations

Optimizer work should usually end with one or more of these:

- a backfill rule
- a reward or metric update
- a daily-review decision rule
- a challenger evaluation summary
- a weekly promotion policy or threshold update

## Scheduling

- Use OpenClaw Gateway cron for recurring AutoTikTok runs. Do not implement a persistent scheduler loop inside this skill.
- Require explicit approval before creating or updating any cron job.
- Use stable cron job names so updates are deterministic:
  - `autotiktok:daily-optimizer`
  - `autotiktok:weekly-optimizer`
- Before creating a job, run `openclaw cron list` and match on exact `name`.
- If a matching job exists, update it with `openclaw cron edit <id> ...`.
- If no matching job exists, create it with `openclaw cron add --name <name> ...`.
- Prefer `--session isolated` for scheduled optimizer runs.
- Prefer `--light-context` plus `--tools exec,read,write` for those isolated jobs.
- Default to `--no-deliver` unless the user explicitly wants job summaries delivered back to chat.
- Use `python3 {baseDir}/scripts/build_optimizer_openclaw_cron_contract.py` when you want the committed OpenClaw cron management contract that freezes stable job names, exact-name matching policy, and `cron add` / `cron edit` templates.
- Read `references/openclaw-cron-ops.md` when you want the operator-facing setup and maintenance path for the preferred OpenClaw cron runtime.
- For standard OpenClaw cron runtime entrypoints, prefer:
  - `python3 {baseDir}/scripts/run_openclaw_cron_daily_optimizer.py`
  - `python3 {baseDir}/scripts/run_openclaw_cron_weekly_optimizer.py`
- The scheduler-facing artifacts below (`optimizer-job-schedule`, `optimizer-job-execution-context`, `optimizer-job-orchestration-cycle`) remain useful for fixture generation, deterministic rehearsal, and cutover validation, but they are no longer the preferred recurring runtime path.
- Those artifacts now explicitly self-identify as `runtimeRole=compatibility_rehearsal` with `preferredRecurringRuntime=openclaw_cron`; treat them as compatibility contracts, not runtime source-of-truth.

## Bundled Script

- Run `python3 {baseDir}/scripts/validate_optimizer_fixtures.py` to validate the shipped backfill, post-performance, and challenger fixtures.
- Run `python3 {baseDir}/scripts/calc_reward.py --topic-input metrics.json` to compute `TopicReward`.
- Add `--performance-input perf.json` to compute `PerformanceReward` and `CombinedReward`.
- Use CLI flags for quick experiments when you do not want to create JSON files.
- Run `python3 {baseDir}/scripts/daily_review_mock.py` to produce a mock daily review report from ranking output plus sample backfills.
- Run `python3 {baseDir}/scripts/run_preview_daily_review.py` when you want the same daily review entrypoint to default to the preview canonical lane (`vNext-preview/exact`) instead of the current live lane.
- `daily_review_mock.py` now hard-validates the optimizer-facing ranking contract before generating a report.
- The daily review entrypoint is now split into a thin runner (`scripts/daily_review_mock.py`), an input adapter layer (`scripts/optimizer_input_adapters.py`), and a report assembly service (`scripts/daily_review_service.py`).
- The adapter layer accepts both the current sample schemas and the planned runtime schema families (`topic-outcome-backfills.v1`, `topic-outcome-backfills-raw.v1`, `post-performance-signals.v1`, `post-performance-raw.v1`, `challenger-adjustments.v1`, `challenger-observations.v1`, `challenger-observations-raw.v1`), including empty performance batches, sparse optional post metrics, and pre-canonical raw payloads for backfills, performance, and challenger observations that get normalized back into the canonical optimizer artifacts.
- The adapter layer now also accepts scheduler-facing job-run envelopes (`topic-outcome-backfill-run.*`, `post-performance-signal-run.*`, `challenger-evaluation-run.*`) and unwraps them back into the canonical eval artifacts before daily review runs.
- The preferred challenger runtime surface is now `challenger-observations.*`, which feeds observed topic metrics and aggregated performance summaries into the shadow leaderboard; `challenger-adjustments.*` remains as a legacy compatibility input.
- Use `python3 {baseDir}/scripts/build_topic_outcome_backfill_run.py`, `build_post_performance_signal_run.py`, and `build_challenger_evaluation_run.py` when you want sample or cron-oriented eval job outputs instead of bare fixture payloads.
- Use `python3 {baseDir}/scripts/build_optimizer_input_manifest.py` when you want a scheduler-friendly manifest that points at the ranking/context/eval artifacts without embedding them yet.
- Use `python3 {baseDir}/scripts/build_optimizer_openclaw_cron_contract.py` when you want a standard OpenClaw cron contract artifact for recurring runtime management, including stable names `autotiktok:daily-optimizer` and `autotiktok:weekly-optimizer`.
- Use `python3 {baseDir}/scripts/build_optimizer_job_schedule.py` when you want one scheduler-facing plan that freezes the daily and weekly optimizer job defaults above the manifest layer.
- That schedule artifact now also freezes a top-level `schedulerRolloutIntents` catalog, so `production`, `raw_shadow_validation`, `real_provider_shadow_validation`, `preview_validation`, and `profile_compare_validation` can be expressed as stable scheduler intent ids instead of only lower-level rollout classes.
- Use `python3 {baseDir}/scripts/build_optimizer_input_source_registry.py` when you want a scheduler-facing binding registry for canonical and raw-shadow input lanes instead of putting concrete artifact paths directly into every manifest.
- Use `python3 {baseDir}/scripts/build_optimizer_input_rollout_policy.py` when you want a scheduler-facing rollout object that maps rollout intents and rollout classes such as `production_run -> production`, `raw_shadow_validation -> raw_shadow_validation`, and `real_provider_shadow_validation -> real_shadow_validation` onto concrete optimizer input source lanes.
- Use `python3 {baseDir}/scripts/build_optimizer_source_artifact_catalog.py` when you want the lowest committed stand-in for real-shadow physical artifact resolution beneath the provider registry.
- Use `python3 {baseDir}/scripts/build_optimizer_source_provider_registry.py` when you want the lower provider-binding layer beneath the real-shadow source provider catalog.
- Use `python3 {baseDir}/scripts/build_optimizer_source_provider_catalog.py` when you want the current stand-in for a future real source provider or artifact catalog beneath the resolver layer.
- Use `python3 {baseDir}/scripts/build_optimizer_job_artifact_resolver.py` when you want the next-layer stand-in for a future real artifact catalog and want source bindings to resolve through resolver entries instead of direct paths.
- Use `python3 {baseDir}/scripts/build_optimizer_input_bundle.py` when you want to package ranking, context, backfills, performance, and challenger inputs into one runtime bundle for later daily-review or cron execution.
- Use `python3 {baseDir}/scripts/materialize_optimizer_input_bundle.py --input-manifest ...` when a cron or job runner already produced a manifest and you want to materialize the canonical bundle from it.
- `build_optimizer_input_manifest.py` now also supports `--input-source-registry ... --source-lane sample_raw_shadow`, which produces a manifest that resolves raw-shadow job-run bindings through the registry instead of embedding direct artifact paths.
- `build_optimizer_input_manifest.py` now also supports `--input-source-registry ... --source-lane real_provider_shadow`, which produces a provider-backed real-shadow manifest that keeps module 2 on the same runtime path while swapping only the outer artifact resolution layer.
- `build_optimizer_input_manifest.py` now also supports `--input-rollout-policy ... --input-rollout-class ...`, which resolves the source lane through a scheduler-facing rollout class instead of hard-coding `sample_raw_shadow` or `real_provider_shadow`.
- Use `python3 {baseDir}/scripts/build_optimizer_runtime_profile_catalog.py` when you want the default planner-facing runtime profile family as an explicit artifact instead of leaving those profiles embedded in the window-set builder.
- Use `python3 {baseDir}/scripts/build_optimizer_runtime_profile_family_registry.py` when you want the planner-facing family/lane registry that resolves a stable runtime profile family into the current or preview catalog reference.
- Use `python3 {baseDir}/scripts/build_optimizer_runtime_profile_rollout_policy.py` when you want scheduler-facing rollout policy on top of that family registry, including active/default lane selection, rollout classes such as `production` / `preview_canary`, preview gating rules, and rule-based routing such as `preview:` batch labels or `windowSetPurpose=preview_validation`.
- The rollout policy artifact now has four layers: `evalPurposeTemplateFamilies` for reusable scheduler-default families, `evalPurposeTemplates` for named templates on top of those families, `evalPurposePolicies` for mapping `windowSetPurpose` onto templates, and `rolloutClassRules` for finer-grained overrides on top.
- The window-set artifact also records `windowSetBatchTypeSelectionSource`, `comparisonDimensionSelectionSource`, `runtimeProfilePlannerMetadataPolicyId`, `runtimeProfilePlannerMetadataContractFamilyId`, and `runtimeProfilePlannerMetadataContractId`, so you can tell whether batch metadata came from explicit scheduler input, a purpose-family/template default, or fallback defaults, and which planner metadata contract family plus concrete contract constrained the allowed batch-type/dimension pair.
- Use `python3 {baseDir}/scripts/build_optimizer_runtime_artifact_registry.py` when you want a planner-facing registry that maps runtime binding ids to concrete artifact paths.
- Use `python3 {baseDir}/scripts/build_optimizer_runtime_materialization_plan.py` when you want the companion planner artifact that explains how each runtime binding should be materialized from upstream job families and required artifact kinds.
- Run `python3 {baseDir}/scripts/weekly_promotion_mock.py` to turn a daily review report into a promotion decision sample.
- Run `python3 {baseDir}/scripts/build_weekly_review_window.py` when you want the committed multi-day weekly review window between `daily-review` and `weekly-promotion`.
- `weekly_promotion_mock.py` now accepts `--weekly-review-window-input`, so the committed weekly sample is generated through that multi-day window rather than directly from a single daily review. That weekly-review window now also freezes explicit reward-horizon weighting (`t+1`, `t+3`, optional `t+7`) plus per-window horizon availability and champion/challenger horizon breakdowns, while the weekly-promotion artifact itself now emits explicit challenger gate reviews and champion safety reviews instead of only a final decision string.
- Run `python3 {baseDir}/scripts/run_offline_optimizer_cycle.py` when you want a single offline-cycle artifact that bundles daily review and, optionally, a weekly promotion decision for later cron orchestration.
- Run `python3 {baseDir}/scripts/run_daily_optimizer_job.py` and `run_weekly_optimizer_job.py` when you want explicit day-level and week-level job artifacts on top of offline-cycle plus eval-run outputs.
- Run `python3 {baseDir}/scripts/run_openclaw_cron_daily_optimizer.py` and `run_openclaw_cron_weekly_optimizer.py` when you want the preferred OpenClaw cron entrypoints that write one optimizer job-run artifact and print a concise plain-text summary for the cron runner.
- Run `python3 {baseDir}/scripts/run_scheduled_optimizer_job.py --input-schedule-plan ... --schedule-id ...` when you want one scheduler-style dispatcher that resolves a committed job-schedule entry into the same `optimizer-job-run.v1` payloads.
- `run_scheduled_optimizer_job.py` now also accepts `--scheduler-rollout-intent ...`, and the resulting job-run, orchestration-cycle, compare, and compare-batch artifacts keep that scheduler intent provenance alongside rollout class, source lane, runtime profile rollout class, and any resolved `windowSetPurpose` / `comparisonDimension`. The schedule contract itself now also freezes `defaultRuntimeProfileRolloutClass`, `defaultWindowSetPurpose`, `defaultComparisonDimension`, `allowedRuntimeProfileRolloutClasses`, `allowedWindowSetPurposes`, and `allowedComparisonDimensions`, so resolver behavior is explicit before the runner executes.
- `build_optimizer_job_schedule.py` now also supports `--schedule-profile external_scheduler`, which produces the committed `optimizer-job-schedule.external.sample.json` contract for scheduler-supplied inputs plus `output_root` emission.
- Run `python3 {baseDir}/scripts/build_optimizer_job_execution_context.py` when you want a scheduler-facing execution-context artifact on top of the external job schedule. That execution context now freezes both `productionSchedulerRolloutIntent` and `shadowSchedulerRolloutIntent` per schedule, not just the lower-level rollout classes.
- Run `python3 {baseDir}/scripts/run_optimizer_job_orchestration_cycle.py` when you want one higher-level scheduler cycle that materializes production job runs, shadow job runs, compare, and compare batch from that execution context.
- Run `python3 {baseDir}/scripts/build_optimizer_job_shadow_compare_plan.py` when you want one scheduler-facing plan that freezes which scheduled jobs and scheduler rollout intents should participate in shadow comparison.
- Run `python3 {baseDir}/scripts/build_optimizer_job_shadow_compare.py` when you want the scheduler-facing compare artifact layer that freezes raw-shadow, real-shadow, preview-validation, and profile-compare scheduler intent semantics into committed compare objects instead of comparing them only inside validators.
- Run `python3 {baseDir}/scripts/build_optimizer_job_shadow_compare_batch_manifest.py` when you want a scheduler-facing batch manifest that freezes which compare artifacts should be grouped and by which dimension. The committed sample now groups by `candidateSchedulerRolloutIntent`, not only by `scheduleId`.
- Run `python3 {baseDir}/scripts/build_optimizer_job_shadow_compare_batch.py` when you want the grouped compare result on top of those daily/weekly compare artifacts.
- The committed sample family now carries both `optimizer-offline-cycle-daily.sample.json` and `optimizer-offline-cycle.sample.json`, and those offline-cycle artifacts can be used as runtime sources for later eval-run or history-batch materialization.
- Run `python3 {baseDir}/scripts/build_optimizer_eval_run.py` when you want a top-level offline evaluation artifact that summarizes reward metrics, promotion outcome, and input-source provenance while keeping the full offline cycle attached underneath.
- Run `python3 {baseDir}/scripts/build_optimizer_eval_batch_manifest.py` when you want a scheduler-facing manifest that freezes which eval-run artifacts should be compared and by which comparison dimension.
- Run `python3 {baseDir}/scripts/build_optimizer_eval_window_set.py` when you want a more cron-shaped replay input that freezes which historical windows and scenarios should be materialized before batch comparison. That payload now uses a top-level runtime-source catalog plus per-window `runtimeSourceId` references, and the catalog can mix `inputManifestPath`, `inputBundlePath`, and `inputOfflineCyclePath`.
- The committed window-set sample now prefers logical `sourceDescriptor` bindings inside `runtimeSources[*]` instead of repeating direct fixture paths. The default descriptor lane is now `planner_runtime_binding` (`profileId`), while `sample_artifact_binding` remains available as a compatibility shape.
- The committed runtime profile catalog now carries an explicit family/version contract, and the window-set sample records that through `runtimeProfileCatalogReference` so history replay can reject mismatched catalogs early.
- The committed runtime profile family registry now sits one step above that catalog, and the window-set sample records `runtimeProfileFamilyRegistryReference` so planner family/lane selection is explicit before catalog resolution.
- The committed runtime profile rollout policy now sits above the family registry, and the window-set sample records `runtimeProfileRolloutPolicyReference` plus the resolved lane-selection provenance so scheduler defaults and manual preview cutovers are distinguishable.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_catalog_cutover.py` when you want to rehearse a preview runtime profile catalog lane with canonical profile renames plus alias-based compatibility for legacy planner profile requests.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_cutover.py` when you want the same preview-vs-current rehearsal, but driven by rollout-policy defaults instead of an explicit lane flag.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_rule_routing.py` when you want to verify that rollout-policy rules can automatically route preview-marked batches onto `preview_canary` without an explicit class override.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_purpose_routing.py` when you want to verify the same canary routing from explicit planner intent (`windowSetPurpose=preview_validation`) instead of batch-label conventions.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_window_mode_routing.py` when you want to verify a more scheduler-shaped composite rule that routes by planner intent plus window-level selectors such as `historyWindowLabel` and `mode`.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_dimension_routing.py` when you want to verify scheduler-level batch metadata routing, where `windowSetPurpose`, `windowSetBatchType`, and `comparisonDimension` together determine the preview lane.
- Run `python3 skills/autotiktok/scripts/validate_runtime_profile_planner_metadata_contract_enforcement.py` when you want an explicit gate that planner metadata contracts reject disallowed `windowSetBatchType` / `comparisonDimension` combinations before history-manifest materialization.
- Run `python3 {baseDir}/scripts/build_optimizer_eval_batch_history_manifest.py` when you want a mock historical replay manifest that materializes runtime-source entries and applies deterministic batch/window replay metadata through manifest entries. Use its `--input-runtime-profile-catalog` flag when you want planner profile resolution to come from an explicit catalog artifact, add `--input-artifact-registry` when you want binding-to-path resolution to come from an explicit registry artifact, add `--input-materialization-plan` when you also want planner materialization metadata resolved into each runtime source, or use its `--input-manifest-path`, `--input-bundle-path`, and `--input-offline-cycle-*-path` overrides when you need to patch individual bindings directly.
- Run `python3 {baseDir}/scripts/build_optimizer_eval_batch.py` when you want a batch-level artifact that compares multiple eval runs, optionally from that manifest, and surfaces mode counts, grouped comparison summaries, average reward metrics, and the best run in one object.
- Use the hub script `python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract.py` before changing optimizer inputs if you need an explicit gate for the ranking subset this skill consumes.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_raw_ingress_alignment.py` when you want one explicit gate that proves raw backfill, performance, and challenger ingress payloads normalize back into the same canonical runtime inputs as the committed sample fixtures.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_shadow_input_alignment.py` when you want a stronger gate that proves the committed source registry plus raw-shadow manifest are deterministically generated and normalize to the same runtime optimizer inputs as the canonical manifest.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_real_shadow_input_alignment.py` when you want the next stronger gate that proves the committed source artifact catalog, source provider registry, source provider catalog, job artifact resolver, source registry, and real-shadow manifest are deterministically generated and still normalize to the same runtime optimizer inputs as the canonical and raw-shadow manifests.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_alignment.py` when you want a scheduler-level gate that proves the committed job schedule still regenerates deterministically and that its daily/weekly dispatch still matches the committed optimizer job-run samples.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_external_alignment.py` when you want the external-scheduler companion gate that proves `optimizer-job-schedule.external.sample.json` still regenerates deterministically and that scheduler-supplied inputs plus `output_root` dispatch still materialize valid daily/weekly job runs.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_openclaw_cron_runtime_alignment.py` when you want the focused gate for the preferred OpenClaw cron runtime.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_scheduler_compatibility_role_alignment.py` when you want the semantic gate that proves scheduler-facing sample artifacts still remain compatibility-only rehearsal contracts.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_execution_context_alignment.py` when you want the deterministic gate for `optimizer-job-execution-context.sample.json`.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_artifact_retention_policy_alignment.py` when you want the deterministic gate for `optimizer-job-artifact-retention-policy.sample.json` and the scheduler-facing retention contract it freezes.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_error_alignment.py` when you want the deterministic gate for `optimizer-job-error.sample.json`, including the scheduler-facing failure taxonomy, retryability, and owner-hint contract.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_run_summary_alignment.py` when you want the deterministic gate for `optimizer-run-summary.sample.json` and the lightweight scheduler-facing run summary embedded in the orchestration cycle.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_recent_run_summaries_alignment.py` when you want the deterministic gate for `optimizer-recent-run-summaries.sample.json` and the dashboard-facing recent-runs aggregate.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_recent_compare_summaries_alignment.py` when you want the deterministic gate for `optimizer-recent-compare-summaries.sample.json` and the flattened compare-batch aggregate for ops/dashboard consumers.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_recent_weekly_decisions_alignment.py` when you want the deterministic gate for `optimizer-recent-weekly-decisions.sample.json`, including scheduler-facing weekly decision, stage-mode, and rollback-severity aggregation.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_recent_failure_summaries_alignment.py` when you want the deterministic gate for `optimizer-recent-failure-summaries.sample.json` and the unified recent failure aggregate built from standalone job errors plus orchestration-cycle errors.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_orchestration_cycle_alignment.py` when you want the higher-level scheduler gate that proves the committed execution context still materializes one full production-plus-shadow orchestration cycle deterministically.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_rollout_alignment.py` when you want the stronger scheduler-level gate that proves raw-shadow, preview-validation, profile-compare-validation, and real-shadow rollouts still preserve production semantics while carrying the right runtime-profile cutover metadata.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_alignment.py` when you want the scheduler-facing compare gate that proves the committed shadow-compare plan and shadow-compare artifact still regenerate deterministically and still preserve raw-shadow vs production, real-shadow vs production, and the preview/profile-compare cutover lanes.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_cutover_alignment.py` when you want the focused cutover rehearsal gate for the `preview_validation` and `profile_compare_validation` compare lanes.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_batch_alignment.py` when you want the scheduler-facing compare-batch gate that proves the committed daily/weekly compare family still regenerates deterministically as one grouped compare object keyed by scheduler rollout intent.
- Use the hub script `python3 skills/autotiktok/scripts/validate_weekly_strategy_realism.py` when you want an explicit semantic gate for the committed weekly-review-window plus rollback behavior.
- Use the hub script `python3 skills/autotiktok/scripts/validate_weekly_stage_policy_alignment.py` when you want the committed growth / scale / search-priority weekly fixtures checked as a stage-specific gate family.
- Taken together, those gates now close the whole pre-real-data ingestion surface: raw payloads, job-run envelopes, source bindings, raw-shadow manifest materialization, source-artifact-catalog plus source-provider registry/catalog resolution, resolver-backed real-shadow materialization, and scheduler-facing shadow compare plus compare batching are all validated before module 2 consumes them.
- Use the hub script `python3 skills/autotiktok/scripts/run_optimizer_stage_matrix.py` when you want to compare daily-review behavior across `growth`, `scale`, and `search_priority` stage modes.
- Use the hub script `python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_expectations.py` when you want a semantic gate for that stage-matrix artifact, including daily-review-only recommendation behavior.
- The shared optimizer policy now lives in `config/optimizer-policy.v1.json`, while reusable evaluation and gate logic lives in `scripts/optimizer_lib.py`.

## Related Skills

- Use `autotiktok-topic-discovery` for upstream candidate generation and evidence quality.
- Use `autotiktok-topic-ranking` for feature vectors, scoring profiles, and ranking outputs that feed the optimizer.
