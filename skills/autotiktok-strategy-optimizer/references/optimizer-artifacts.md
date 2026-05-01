# Optimizer Artifacts

This reference explains the mock input and output files shipped with the optimizer skill.

## Input Artifacts

The optimizer scaffold uses these sample inputs:

- [../fixtures/optimizer-input-manifest.sample.json](../fixtures/optimizer-input-manifest.sample.json)
- [../fixtures/optimizer-input-manifest.raw-shadow.sample.json](../fixtures/optimizer-input-manifest.raw-shadow.sample.json)
- [../fixtures/optimizer-input-manifest.real-shadow.sample.json](../fixtures/optimizer-input-manifest.real-shadow.sample.json)
- [../fixtures/optimizer-input-bundle.sample.json](../fixtures/optimizer-input-bundle.sample.json)
- [../fixtures/optimizer-input-source-registry.sample.json](../fixtures/optimizer-input-source-registry.sample.json)
- [../fixtures/optimizer-source-artifact-catalog.sample.json](../fixtures/optimizer-source-artifact-catalog.sample.json)
- [../fixtures/optimizer-source-provider-registry.sample.json](../fixtures/optimizer-source-provider-registry.sample.json)
- [../fixtures/optimizer-source-provider-catalog.sample.json](../fixtures/optimizer-source-provider-catalog.sample.json)
- [../fixtures/optimizer-job-artifact-resolver.sample.json](../fixtures/optimizer-job-artifact-resolver.sample.json)
- [../fixtures/optimizer-input-rollout-policy.sample.json](../fixtures/optimizer-input-rollout-policy.sample.json)
- [../fixtures/optimizer-openclaw-cron-contract.sample.json](../fixtures/optimizer-openclaw-cron-contract.sample.json)
- [../fixtures/optimizer-job-schedule.sample.json](../fixtures/optimizer-job-schedule.sample.json)
- [../fixtures/optimizer-job-schedule.external.sample.json](../fixtures/optimizer-job-schedule.external.sample.json)
- [../fixtures/optimizer-job-execution-context.sample.json](../fixtures/optimizer-job-execution-context.sample.json)
- [../fixtures/optimizer-job-shadow-compare-plan.sample.json](../fixtures/optimizer-job-shadow-compare-plan.sample.json)
- [../fixtures/optimizer-runtime-profile-catalog.sample.json](../fixtures/optimizer-runtime-profile-catalog.sample.json)
- [../fixtures/optimizer-runtime-profile-rollout-policy.sample.json](../fixtures/optimizer-runtime-profile-rollout-policy.sample.json)
- [../fixtures/optimizer-runtime-artifact-registry.sample.json](../fixtures/optimizer-runtime-artifact-registry.sample.json)
- [../fixtures/optimizer-runtime-materialization-plan.sample.json](../fixtures/optimizer-runtime-materialization-plan.sample.json)
- [../fixtures/optimizer-eval-batch-manifest.sample.json](../fixtures/optimizer-eval-batch-manifest.sample.json)
- [../fixtures/optimizer-eval-window-set.sample.json](../fixtures/optimizer-eval-window-set.sample.json)
- [../fixtures/optimizer-eval-batch-history-manifest.sample.json](../fixtures/optimizer-eval-batch-history-manifest.sample.json)
- [../fixtures/topic-outcome-backfills.sample.json](../fixtures/topic-outcome-backfills.sample.json)
- [../fixtures/topic-outcome-backfills-raw.sample.json](../fixtures/topic-outcome-backfills-raw.sample.json)
- [../fixtures/topic-outcome-backfill-run.sample.json](../fixtures/topic-outcome-backfill-run.sample.json)
- [../fixtures/topic-outcome-backfill-raw-run.sample.json](../fixtures/topic-outcome-backfill-raw-run.sample.json)
- [../fixtures/post-performance-signals.sample.json](../fixtures/post-performance-signals.sample.json)
- [../fixtures/post-performance-raw.sample.json](../fixtures/post-performance-raw.sample.json)
- [../fixtures/post-performance-signal-run.sample.json](../fixtures/post-performance-signal-run.sample.json)
- [../fixtures/post-performance-signal-raw-run.sample.json](../fixtures/post-performance-signal-raw-run.sample.json)
- [../fixtures/challenger-adjustments.sample.json](../fixtures/challenger-adjustments.sample.json)
- [../fixtures/challenger-observations.sample.json](../fixtures/challenger-observations.sample.json)
- [../fixtures/challenger-observations-raw.sample.json](../fixtures/challenger-observations-raw.sample.json)
- [../fixtures/challenger-evaluation-run.sample.json](../fixtures/challenger-evaluation-run.sample.json)
- [../fixtures/challenger-evaluation-raw-run.sample.json](../fixtures/challenger-evaluation-raw-run.sample.json)
- [../../autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json](../../autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json)

Validate the ranking-to-optimizer handoff contract with:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract.py
```

That same contract is enforced at runtime by:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py
```

## Preferred OpenClaw Cron Runtime

If you want recurring AutoTikTok optimizer execution on a real OpenClaw Gateway, prefer the standard cron runtime instead of the fixture-only scheduler plan artifacts.

If you want the shortest operator-facing setup path, read [openclaw-cron-ops.md](openclaw-cron-ops.md).

Freeze that management contract with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_openclaw_cron_contract.py
```

The committed contract artifact currently freezes:

- stable job names:
  - `autotiktok:daily-optimizer`
  - `autotiktok:weekly-optimizer`
- exact-name matching policy before job creation
- `openclaw cron add` templates
- `openclaw cron edit <job-id>` templates
- the standard isolated session, tool allow-list, and `--no-deliver` defaults

Use these thin cron entrypoints:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_daily_optimizer.py
python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_weekly_optimizer.py
```

Each entrypoint:

- writes one `optimizer-job-run.v1` artifact
- accepts the same manifest / bundle / runtime inputs as the existing daily or weekly runner
- defaults to the canonical committed manifest inputs, plus the committed weekly review window for the weekly job
- supports `--output` or `--output-root`
- prints a concise plain-text summary intended for an OpenClaw isolated cron run

The preferred cron runtime path is also covered by the focused hub gate:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_openclaw_cron_runtime_alignment.py
```

Recommended OpenClaw cron jobs:

```bash
openclaw cron add \
  --name "autotiktok:daily-optimizer" \
  --cron "0 4 * * *" \
  --tz "UTC" \
  --session isolated \
  --message "Run python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_daily_optimizer.py and summarize the result, key decision, and output artifact path." \
  --tools exec,read,write \
  --light-context \
  --no-deliver
```

```bash
openclaw cron add \
  --name "autotiktok:weekly-optimizer" \
  --cron "15 4 * * 0" \
  --tz "UTC" \
  --session isolated \
  --message "Run python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_weekly_optimizer.py and summarize the weekly decision and output artifact path." \
  --tools exec,read,write \
  --light-context \
  --no-deliver
```

Manage those jobs like other OpenClaw standard cron integrations:

- `openclaw cron list`
- `openclaw cron edit <id> ...`
- `openclaw cron runs --id <job-id>`

If you want one scheduler-friendly payload instead of five separate files, build the runtime bundle with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_bundle.py
```

If you want one scheduler-facing orchestration plan above the manifest layer, build the job schedule with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_schedule.py
```

That scheduler-facing plan remains useful for deterministic rehearsal, fixture generation, and cutover validation, but it is no longer the preferred recurring runtime entrypoint once OpenClaw cron is available.

The legacy scheduler-facing artifacts now also carry explicit compatibility markers:

- `runtimeRole=compatibility_rehearsal`
- `preferredRecurringRuntime=openclaw_cron`
- `intendedUses=[fixture_generation, deterministic_rehearsal, cutover_validation]`

That compatibility role is locked by:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_scheduler_compatibility_role_alignment.py
```

If you want the external-scheduler profile instead of the repo-local fixture replay profile, build:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_schedule.py \
  --schedule-profile external_scheduler \
  --schedule-plan-id optimizer-job-schedule.external.autotiktok.fixture.2026-04-18
```

If you want the companion execution-context artifact on top of that external schedule, build:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_execution_context.py \
  --input-schedule-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.external.sample.json
```

If you want the higher-level scheduler cycle that materializes production and shadow job runs plus compare artifacts from that execution context, build:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_optimizer_job_orchestration_cycle.py \
  --input-execution-context skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-execution-context.sample.json
```

If you want one lighter-weight handoff object for cron orchestration first, build the manifest with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_manifest.py
```

If you want a scheduler-facing source registry plus a raw-shadow manifest that resolves those bindings instead of embedding direct paths, build:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_source_registry.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_rollout_policy.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_manifest.py \
  --input-source-registry skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-source-registry.sample.json \
  --source-lane sample_raw_shadow
```

If you want scheduler/job plans to switch input lanes by rollout class instead of hand-authoring manifests, use:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py \
  --input-schedule-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.sample.json \
  --schedule-id daily_optimizer_job \
  --input-rollout-class raw_shadow_validation
```

The input rollout policy now also freezes a scheduler-facing intent layer:

- `defaultRolloutIntent`
- `rolloutSelectionPrecedence`
- `rolloutIntents[*].rolloutIntent`
- `rolloutIntents[*].rolloutClass`
- `schedulePolicies[*].defaultRolloutIntent`
- `schedulePolicies[*].allowedRolloutIntents`

If you want the next-layer stand-in for a future real artifact catalog, build the resolver plus a resolver-backed real-shadow manifest with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_source_provider_registry.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_source_provider_catalog.py \
  --input-source-provider-registry skills/autotiktok-strategy-optimizer/fixtures/optimizer-source-provider-registry.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_artifact_resolver.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_source_registry.py \
  --input-artifact-resolver skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-artifact-resolver.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_manifest.py \
  --input-source-registry skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-source-registry.sample.json \
  --source-lane real_provider_shadow
```

The committed real-shadow stand-in is now a layered chain:

- source binding
- resolver entry
- source provider id
- provider catalog entry
- provider binding id in the provider registry
- concrete artifact path

So the current stand-in is already closer to a future object-store binding or provider-owned locator than the earlier "resolver directly owns every path" shape.

Then materialize the canonical bundle from that manifest with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/materialize_optimizer_input_bundle.py \
  --input-manifest skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json
```

If you want the scheduler-facing eval artifacts themselves, build the three job-run envelopes with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_topic_outcome_backfill_run.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_post_performance_signal_run.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_challenger_evaluation_run.py
```

Those three builders now accept either canonical payloads or the new raw ingress payloads as `--input`.

If you want one planner-facing registry that resolves runtime binding ids into concrete artifact paths, build:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_artifact_registry.py
```

There is now also a scheduler-facing dispatcher on top of the daily/weekly runners:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py \
  --input-schedule-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.sample.json \
  --schedule-id daily_optimizer_job
```

If you want to drive that dispatcher through the higher-level scheduler intent contract instead of a lower-level rollout class, use:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py \
  --input-schedule-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.sample.json \
  --schedule-id daily_optimizer_job \
  --scheduler-rollout-intent raw_shadow_validation
```

The committed `optimizer-job-schedule.sample.json` currently freezes two entries:

- `daily_optimizer_job`
- `weekly_optimizer_job`

The schedule artifact now also has a top-level `schedulerRolloutIntents` catalog. The committed sample currently freezes:

- `production`
- `raw_shadow_validation`
- `real_provider_shadow_validation`
- `preview_validation`
- `profile_compare_validation`

Each schedule entry records the scheduler default input mode/path, policy path, ranking-contract lane, output path, whether weekly promotion is enabled, the default ids/timestamps that later become the `optimizer-job-run.v1` payload, plus:

- `defaultSchedulerRolloutIntent`
- `allowedSchedulerRolloutIntents`
- `defaultInputRolloutIntent`
- `defaultInputRolloutClass`
- `defaultRuntimeProfileRolloutClass`
- `defaultWindowSetPurpose`
- `defaultComparisonDimension`
- `allowedRuntimeProfileRolloutClasses`
- `allowedWindowSetPurposes`
- `allowedComparisonDimensions`

There is now also a second committed plan:

- `optimizer-job-schedule.external.sample.json`

That plan keeps the same two entries, but switches them to:

- `scheduleProfile=external_scheduler`
- `pathResolutionMode=scheduler_supplied`
- `outputEmissionMode=output_root`

So the schedule itself stops freezing repo-local input paths and instead freezes the scheduler contract for how an external runner must supply inputs and where outputs should be emitted.

On top of that schedule contract there is now also:

- `optimizer-job-artifact-retention-policy.sample.json`
- `optimizer-run-summary.sample.json`
- `optimizer-job-error.sample.json`
- `optimizer-recent-run-summaries.sample.json`
- `optimizer-recent-compare-summaries.sample.json`
- `optimizer-recent-weekly-decisions.sample.json`
- `optimizer-recent-failure-summaries.sample.json`
- `optimizer-job-execution-context.sample.json`
- `optimizer-job-orchestration-cycle.sample.json`

The execution-context artifact freezes scheduler run metadata plus per-schedule production/shadow rollout classes and production/shadow scheduler rollout intents. The orchestration-cycle artifact is the scheduler-facing aggregate that materializes:

- production daily / weekly job runs
- raw-shadow / real-shadow job runs
- one compare artifact
- one compare batch

The retention-policy artifact freezes how long scheduler-facing artifacts should live and at what retention tier. The committed sample currently carries explicit rows for:

- `input_manifest`
- `input_bundle`
- `job_run`
- `shadow_compare`
- `shadow_compare_batch`
- `recent_run_summaries`
- `recent_compare_summaries`
- `recent_weekly_decisions`
- `recent_failure_summaries`
- `orchestration_cycle`
- `job_error`

The orchestration-cycle artifact now records that policy back into:

- `artifacts.retentionPolicy`
- `generatedFrom.optimizerJobArtifactRetentionPolicySchemaVersion`
- `generatedFrom.optimizerJobArtifactRetentionPolicyId`
- `summary.retentionPolicyId`
- `summary.retentionManagedArtifactCount`
- `summary.retentionManagedArtifactKinds`

There is now also a lightweight run-summary artifact on top of the orchestration cycle:

- `artifacts.runSummary`
- standalone `optimizer-run-summary.sample.json`

That summary keeps the scheduler-facing scan surface compact. The committed sample currently surfaces:

- `runStatus`
- schedule success / partial-failure / failure counts
- compare match / mismatch counts
- weekly decision counts
- scheduler rollout intent counts
- per-schedule production decision / recommendation snapshots

Each entry now also records scheduler-facing input rollout defaults:

- `defaultSchedulerRolloutIntent`
- `defaultInputSourceRegistryPath`
- `defaultInputRolloutIntent`
- `defaultInputRolloutClass`
- `defaultInputRolloutSelectionSource`
- `defaultInputRolloutIntentSelectionSource`
- `defaultInputRolloutClassSelectionSource`
- `defaultInputSourceLane`
- `allowedSchedulerRolloutIntents`
- `allowedInputRolloutIntents`
- `allowedInputRolloutClasses`

That means the committed plan can now express production canonical input, raw-shadow and real-shadow validation lanes, plus preview/profile-compare runtime-profile cutover intent without changing the daily/weekly job entrypoints themselves.

If a scheduled dispatch fails, `run_scheduled_optimizer_job.py` can now also emit a structured `optimizer-job-error.v1` artifact via `--error-output`, so external runners do not have to depend on stderr text alone when classifying failures.

That error contract now carries explicit triage fields:

- `failureStage`
- `retryable`
- `ownerHint`
- `failureSummary`

The committed sample currently uses an `input_resolution_failure` lane, and the scheduler-facing taxonomy now distinguishes at least:

- `input_resolution_failure`
- `rollout_policy_failure`
- `job_materialization_failure`
- `artifact_emission_failure`
- `scheduler_dispatch_failure`

The orchestration-cycle runner also now collects those per-schedule error artifacts into `artifacts.errors` instead of aborting the whole cycle on the first failure. That means `optimizer-run-summary.errorSummaries` can now carry owner hints and retryability alongside the schedule id and error code.

On top of the run summary, compare batch, and job-error contracts there is now also a dashboard-facing recent aggregate layer:

- `optimizer-recent-run-summaries.sample.json`
- `optimizer-recent-compare-summaries.sample.json`
- `optimizer-recent-weekly-decisions.sample.json`
- `optimizer-recent-failure-summaries.sample.json`

Those artifacts are intentionally lighter than the orchestration cycle. The committed samples now surface:

- recent run: `runStatus`, production/shadow job-run counts, compare artifact counts, scheduler rollout intent counts
- recent compare: compare-batch entries plus flattened `groupEntries`, including candidate rollout class, source lane, runtime-profile rollout class, window-set purpose, and comparison dimension
- recent weekly decisions: scheduler-facing weekly decisions, `weeklyStageMode`, `weeklyStagePolicyId`, rollback severity, and selected challenger profile ids
- recent failures: failure counts, retryability, owner-hint counts, and schedule-level failure summaries

That means dashboard / ops consumers no longer need to scan raw orchestration-cycle or compare-batch payloads just to render a recent-runs or recent-failures view.

If you want the committed retention-policy sample regenerated directly, run:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_artifact_retention_policy.py
```

If you want the committed run-summary sample regenerated directly from the committed orchestration cycle, run:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_run_summary.py
```

If you want the committed job-error sample regenerated directly, run:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_error_sample.py
```

If you want the default planner-facing runtime profile family as its own artifact, build:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_profile_catalog.py
```

That entrypoint is now intentionally split into three layers:

- `scripts/daily_review_mock.py` keeps the CLI and file IO surface stable
- `scripts/optimizer_input_adapters.py` normalizes ranking, backfill, performance, and challenger inputs
- `scripts/daily_review_service.py` assembles the daily review artifact from normalized runtime inputs

For day-to-day preview-lane work, use:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_preview_daily_review.py
```

That wrapper defaults to `vNext-preview/exact` and still exposes `--use-current-lane` when you intentionally need the current live lane.

If the ranking payload drifts, the daily review entrypoint now fails immediately instead of producing a partially valid optimizer artifact.

The input adapter layer now accepts both the committed sample schemas and the planned runtime schema families:

- `topic-outcome-backfills.sample.v1` and `topic-outcome-backfills.v1`
- `topic-outcome-backfills-raw.sample.v1` and `topic-outcome-backfills-raw.v1`
- `post-performance-signals.sample.v1` and `post-performance-signals.v1`
- `post-performance-raw.sample.v1` and `post-performance-raw.v1`
- `challenger-adjustments.sample.v1` and `challenger-adjustments.v1`
- `challenger-observations.sample.v1` and `challenger-observations.v1`
- `challenger-observations-raw.sample.v1` and `challenger-observations-raw.v1`

It now also accepts a scheduler-facing job-run envelope around those eval artifacts:

- `topic-outcome-backfill-run.sample.v1` and `topic-outcome-backfill-run.v1`
- `post-performance-signal-run.sample.v1` and `post-performance-signal-run.v1`
- `challenger-evaluation-run.sample.v1` and `challenger-evaluation-run.v1`

`topic-outcome-backfills-raw.*` is the new pre-canonical backfill ingress lane. It lets an upstream job ship raw-ish fields such as `observedWindow`, `matchStrategy`, `coverageDays`, `queryLiftScore`, `futureTopicDensityScore`, `contentGapPersistenceScore`, and `matchConfidence`, then lets `optimizer_input_adapters.py` normalize them back into canonical `topic-outcome-backfills.*`.

`post-performance-raw.*` is the new pre-canonical performance ingress lane. It lets an upstream job ship raw-ish fields such as `observedViews`, `expectedViews`, `normalizedViewLift`, `retentionRatio`, `shareSaveRate`, and `followConversionRate`, then lets `optimizer_input_adapters.py` normalize them back into canonical `post-performance-signals.*`.

`challenger-observations-raw.*` is the new pre-canonical challenger ingress lane. It lets an upstream job ship `rankingQuality.*`, `performanceAggregate.*`, and `observedDays`, then lets `optimizer_input_adapters.py` normalize them back into canonical `challenger-observations.*`.

If you want one explicit gate that proves all three raw ingress lanes normalize back into the same canonical runtime inputs, run:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_raw_ingress_alignment.py
```

That layer also allows two runtime cases that the strict sample-fixture validator does not model:

- empty daily performance batches
- sparse post-performance rows where proxy metrics are not available yet and `viewLift` is the only scoreable field

The default daily-review sample path now prefers `challenger-observations.sample.json`, which is closer to the intended offline evaluation loop than the older delta-only challenger input.

The default manifest and bundle builders now go one step further: they point at the three job-run envelopes by default, then unwrap them back into canonical inner artifacts inside `optimizer-input-bundle.sample.json`.

The older `challenger-adjustments` shape is still supported as a compatibility layer, but it should be treated as a legacy mock input rather than the preferred long-term runtime contract.

There is now also a raw-shadow ingestion lane on top of those raw job-run envelopes:

- `optimizer-input-source-registry.sample.json`
- `optimizer-input-manifest.raw-shadow.sample.json`

That lane keeps the committed canonical manifest untouched, but lets module 2 resolve a second manifest through `artifactBindings` plus `inputSourceRegistryReference`. The canonical and raw-shadow manifests now normalize to the same runtime optimizer inputs, which is the current stand-in for a future sample-lane vs real-lane shadow ingestion comparison.

The hub gate for that stand-in is:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_shadow_input_alignment.py
```

At this point the pre-real-data ingestion layer is complete: upstream-shaped raw payloads, scheduler-facing job-run envelopes, source bindings, raw-shadow manifest materialization, and canonical-vs-shadow runtime alignment are all under deterministic validation.

There is now also a resolver-backed real-shadow stand-in on top of that:

- `optimizer-source-artifact-catalog.sample.json`
- `optimizer-source-provider-registry.sample.json`
- `optimizer-source-provider-catalog.sample.json`
- `optimizer-job-artifact-resolver.sample.json`
- `optimizer-input-manifest.real-shadow.sample.json`

That lane uses `resolutionMode=job_artifact_resolver` and `resolverEntryId` inside the source registry instead of direct paths. The resolver now points at a separate `optimizer-source-provider-catalog`, that catalog resolves through `providerBindingId` into `optimizer-source-provider-registry`, and the provider registry now resolves through `artifactCatalogEntryId` into `optimizer-source-artifact-catalog`. So the current stand-in is no longer “resolver directly owns every path”; it is “resolver entry -> source provider id -> provider catalog entry -> provider binding id -> artifact catalog entry -> concrete artifact path”. That is the current placeholder for a future real artifact catalog, object-store-backed resolver, or provider-owned locator.

The dedicated gate for that lane is:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_real_shadow_input_alignment.py
```

That gate proves the committed source artifact catalog, source provider registry, source provider catalog, resolver, source registry, and real-shadow manifest still regenerate deterministically and that canonical, raw-shadow, and real-shadow manifests still collapse to the same runtime optimizer inputs.

There is now also a dedicated orchestration gate above those ingress layers:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_alignment.py
```

That gate proves:

- `optimizer-job-schedule.sample.json` still regenerates deterministically
- `run_scheduled_optimizer_job.py --schedule-id daily_optimizer_job` still matches committed `optimizer-daily-job-run.sample.json`
- `run_scheduled_optimizer_job.py --schedule-id weekly_optimizer_job` still matches committed `optimizer-weekly-job-run.sample.json`

There is now also a rollout-aware scheduler gate above that:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_job_schedule_rollout_alignment.py
```

That gate proves:

- scheduled daily raw-shadow rollout still matches production semantics
- scheduled weekly real-shadow rollout still matches production semantics
- the scheduled job artifacts now record which rollout intent, rollout class, and source lane were selected

There is now also a committed scheduler-facing compare family above that:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_alignment.py
```

That gate proves:

- `optimizer-job-shadow-compare-plan.sample.json` still regenerates deterministically
- `optimizer-job-shadow-compare.sample.json` still regenerates deterministically
- `optimizer-job-shadow-compare-batch-manifest.sample.json` still regenerates deterministically
- `optimizer-job-shadow-compare-batch.sample.json` still regenerates deterministically
- `daily_raw_shadow_vs_production` stays semantically identical while preserving raw-shadow source-lane provenance
- `weekly_real_shadow_vs_production` stays semantically identical while preserving resolver, provider-catalog, provider-registry, and source-artifact-catalog provenance
- `daily_preview_validation_vs_production` stays semantically identical while carrying `preview_canary` runtime-profile cutover metadata
- `daily_profile_compare_validation_vs_production` stays semantically identical while carrying `profile_compare_validation` / `rankingProfileId` compare metadata
- the committed daily/weekly compare family still rolls up into one stable compare batch by `candidateSchedulerRolloutIntent`

The compare layer is now split into four objects:

- `optimizer-job-shadow-compare-plan`: scheduler-facing intent about which schedule and rollout-class pairs should be compared
- `optimizer-job-shadow-compare`: the materialized compare result built from that plan
- `optimizer-job-shadow-compare-batch-manifest`: scheduler-facing intent about which compare artifacts should be grouped and by which dimension
- `optimizer-job-shadow-compare-batch`: the aggregated compare result built from that batch manifest

Those compare artifacts now also keep the higher-level scheduler intent provenance, not just rollout class and source lane. In practice that means:

- compare entries record `baseline.schedulerRolloutIntent` and `candidate.schedulerRolloutIntent`
- compare entries also record `runtimeProfileRolloutClass`, `windowSetPurpose`, and `comparisonDimension` for both baseline and candidate
- compare summary records `comparedSchedulerRolloutIntents`
- compare summary also records `comparedRuntimeProfileRolloutClasses`, `comparedWindowSetPurposes`, and `comparedComparisonDimensions`
- compare batch summary records `comparedCandidateSchedulerRolloutIntents`
- compare batch summary also records `comparedCandidateRuntimeProfileRolloutClasses`, `comparedCandidateWindowSetPurposes`, and `comparedCandidateComparisonDimensions`

There is now also a committed weekly-review window artifact between the daily and weekly layers:

- `optimizer-weekly-review-window.sample.json`

Build it with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_weekly_review_window.py
```

`weekly_promotion_mock.py` now accepts `--weekly-review-window-input`, so the committed weekly sample is generated through that multi-day window rather than directly from a single daily review. The semantic gate for that layer is:

```bash
python3 skills/autotiktok/scripts/validate_weekly_strategy_realism.py
```

The committed weekly-review window contract now makes the multi-day aggregation explicit instead of only shipping flat champion/challenger averages. It now carries:

- `rewardHorizonPolicy`
- `windows[*].availableRewardHorizonIds`
- `windows[*].championObservation.rewardHorizonBreakdown`
- `windows[*].challengerObservations[*].rewardHorizonBreakdown`
- `aggregatedChampion.rewardHorizonSummaries`
- `challengerSummaries[*].rewardHorizonSummaries`

So the weekly layer now distinguishes:

- required horizons such as `t+1` and `t+3`
- optional horizons such as `t+7`
- which horizons were actually available for each replay window
- how the weekly reward summary was weighted across those horizons

There is now also a scheduler-facing selector for eval-batch comparisons:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_manifest.py
```

That manifest does not embed the eval runs themselves. It only freezes:

- which `optimizer-eval-run` artifacts should be compared
- which comparison dimension the batch should group by
- which batch window label should be attached to the resulting comparison object

There is now a second manifest lane for historical replay samples:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_window_set.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_history_manifest.py
```

The new window-set layer is the scheduler-facing input. It freezes which replay windows and scenarios should be compared:

- `windowId`
- `mode`
- `windowSetPurpose`
- `windowSetBatchType`
- `historyBatchLabel`
- `historyWindowLabel`
- `scenarioLabel`
- `cycleId`
- `evalRunId`
- `reportId`
- `runtimeSourceId`

Its `generatedFrom` block now also records where planner-level defaults came from, including `windowSetBatchTypeSelectionSource` and `comparisonDimensionSelectionSource`. That lets later eval-batch audits distinguish explicit scheduler input from purpose-family/template defaults or fallback defaults.

That same provenance block now also records `runtimeProfilePlannerMetadataPolicyId`, `runtimeProfilePlannerMetadataContractFamilyId`, and `runtimeProfilePlannerMetadataContractId`, so downstream history-manifest and eval-batch artifacts can tell which planner metadata policy selected the batch metadata, which contract family it belonged to, and which concrete contract constrained the allowed `windowSetBatchType` / `comparisonDimension` pair.

The history manifest is now derived from that window set instead of being authored directly. It still uses `evalRunEntries`, but those entries are generated from the scheduler-facing window objects and now materialize one of three runtime sources directly:

- `inputManifestPath`
- `inputBundlePath`
- `inputOfflineCyclePath`

Those concrete runtime inputs now live in a top-level `runtimeSources` catalog on the window set itself. Each window points at one catalog entry through `runtimeSourceId`, which is closer to a real planner that freezes source bindings once and lets many windows reuse them.

That catalog now supports two forms:

- direct concrete paths
- a logical `sourceDescriptor`

The committed sample now prefers `sourceDescriptor`, not direct file paths. The current default descriptor lane uses `planner_runtime_binding` plus:

- `profileId`

That keeps the planner object focused on runtime intent rather than fixture names. The history-manifest builder resolves `profileId` through a planner-facing runtime profile catalog, then resolves the descriptor into the correct concrete runtime input before writing `evalRunEntries[*].runtimeSource`.

`sample_artifact_binding` remains available as a compatibility descriptor when you explicitly need fixture-name-level bindings.

There is now also a committed runtime profile catalog artifact:

- `optimizer-runtime-profile-catalog.sample.json`
- `optimizer-runtime-profile-catalog-preview.sample.json`
- `optimizer-runtime-profile-family-registry.sample.json`
- `optimizer-runtime-profile-rollout-policy.sample.json`

That catalog is the default profile family for planner descriptors. Each row records:

- `catalogFamily`
- `catalogVersion`
- `profileId`
- `bindingId`
- `runtimeSourceKind`
- `includeWeeklyPromotion`
- `jobFamilyGroup`
- `materializationProfile`
- `sourceClass`
- `sourceVariant`
- `rankingContractVersion`
- `rankingContractValidationMode`
- `aliasProfileIds` when a newer catalog lane still accepts legacy planner-requested ids

The family registry sits one level above those catalogs and freezes which catalog lane a planner family should resolve to. Each family row currently records:

- `familyId`
- `defaultLane`
- `supportedLanes`
- `lanes[*].catalog`

The rollout policy sits one level above the family registry and freezes which family lane should be used by default in scheduler-facing jobs. Each family policy row currently records:

- `familyId`
- `activeLane`
- `defaultLane`
- `defaultRolloutClass`
- `allowedLanes`
- `rolloutClasses[*].rolloutClass`
- `rolloutClasses[*].selectedLane`
- `previewLane`
- `previewEnabled`
- `rolloutStrategy`

The same artifact now also carries a reusable family/template layer plus purpose mapping. The committed sample now uses:

- `evalPurposeTemplateFamilies`: reusable scheduler-default families
- `evalPurposeTemplates`: named templates bound onto those families
- `evalPurposePolicies`: `windowSetPurpose -> template` mappings
- `plannerMetadataPolicies`: reusable metadata default/priority policies referenced by template families
- `plannerMetadataContractFamilies`: reusable contract families that define allowed `windowSetBatchType` / `comparisonDimension` envelopes
- `plannerMetadataContracts`: concrete contracts inside those families, enforced by the metadata policies

There is also a dedicated contract-enforcement gate for this layer:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_planner_metadata_contract_enforcement.py
```

It proves both the valid default routes and the failure path when a scheduler tries to override `windowSetBatchType` or `comparisonDimension` with a pair the selected metadata contract does not allow.

Today those templates/policies are:

- `preview_validation_family` -> `preview_validation_template` / `preview_validation_default`: `windowSetPurpose=preview_validation` -> `preview_canary`
- `cross_profile_validation_family` -> `profile_compare_validation_template` / `profile_compare_validation_default`: `windowSetPurpose=profile_compare_validation` -> `preview_canary`, plus default `windowSetBatchType=cross_profile_comparison` and `comparisonDimension=rankingProfileId`

The committed sample policy also ships rule-based routing for preview canaries. Today it includes:

- `preview_batch_label`: route to `preview_canary` when `batchWindowLabel` starts with `preview:`
- `preview_weekly_shadow_rehearsal`: route to `preview_canary` when `windowSetPurpose=weekly_shadow_rehearsal` and the window set includes a `historyWindowLabel` starting with `historical_` plus `mode=daily_with_weekly_promotion`
- `preview_scenario_prefix`: route to `preview_canary` when any window `scenarioLabel` starts with `preview_`

That means scheduler intent can now be expressed in two ways:

- naming convention: for example `batchWindowLabel=preview:...`
- explicit planner purpose policy: for example `windowSetPurpose=preview_validation`

And planner-level routing now has enough structure to distinguish:

- why this batch exists: `windowSetPurpose`
- what type of batch it is: `windowSetBatchType`
- how it will be grouped downstream: `comparisonDimension`

There is now also a committed runtime registry artifact:

- `optimizer-runtime-artifact-registry.sample.json`

That registry maps planner binding ids such as `optimizer_input_manifest` or `optimizer_offline_cycle_weekly` to:

- `artifactField`
- `artifactPath`
- `runtimeSourceKind`
- `jobFamilyGroup`
- `materializationProfile`
- `sourceClass`
- `sourceVariant`
- `materializationPlanId`

There is now a second planner-facing artifact beside the registry:

- `optimizer-runtime-materialization-plan.sample.json`

That plan explains how each binding is supposed to be produced, not where it lives. Each plan row currently records:

- `planId`
- `outputBindingId`
- `jobFamilyGroup`
- `materializationProfile`
- `sourceClass`
- `sourceVariant`
- `materializationStrategy`
- `upstreamJobFamilies`
- `requiredArtifactKinds`
- `includeWeeklyPromotion`

The intended split is now:

- `optimizer-eval-window-set` freezes planner intent
- `optimizer-runtime-profile-rollout-policy` decides which family lane is active/default for scheduler-driven window materialization
- `optimizer-runtime-profile-family-registry` resolves planner family/lane into a concrete runtime profile catalog reference
- `optimizer-runtime-profile-catalog` declares the default planner-facing runtime profile family and version
- `optimizer-runtime-artifact-registry` resolves planner binding ids into concrete runtime artifacts
- `optimizer-runtime-materialization-plan` explains how those bindings are materialized from upstream jobs and artifact families
- `optimizer-eval-batch-history-manifest` materializes eval-run entries from all three

When you need to resolve the same descriptor-based window set against non-committed artifacts, use the override flags on the history-manifest builder:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_history_manifest.py \
  --input-window-set /tmp/optimizer-eval-window-set.json \
  --input-runtime-profile-catalog /tmp/optimizer-runtime-profile-catalog.json \
  --input-artifact-registry /tmp/optimizer-runtime-artifact-registry.json \
  --input-materialization-plan /tmp/optimizer-runtime-materialization-plan.json \
  --input-manifest-path /tmp/optimizer-input-manifest.json \
  --input-bundle-path /tmp/optimizer-input-bundle.json \
  --input-offline-cycle-daily-path /tmp/optimizer-offline-cycle-daily.json \
  --input-offline-cycle-weekly-path /tmp/optimizer-offline-cycle.json
```

Each generated history entry can still apply deterministic replay metadata such as:

- `historyBatchLabel`
- `historyWindowLabel`
- `scenarioLabel`
- `summaryOverrides`

That lets the mock project model multi-batch history comparisons without first checking in a separate full eval-run JSON file for every historical variant.

Once those planner artifacts are resolved, the derived `optimizer-eval-batch.v1` summary and each `groupSummaries[*]` row now also record:

- `runtimeProfileIds`
- `runtimeProfileRequestedIds`
- `runtimeProfileAliasAppliedCount`
- `runtimeProfileCatalogIds`
- `runtimeProfileCatalogFamilies`
- `runtimeProfileCatalogVersions`
- `materializationPlanIds`
- `jobFamilyGroups`
- `materializationProfiles`
- `materializationStrategies`
- `requiredArtifactKinds`
- `upstreamJobFamilies`

So the replay result now tells you not only which runtime source was used, but also which planner materialization strategy produced it.

There is now also a catalog cutover rehearsal gate:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_catalog_cutover.py
```

And a second rollout-policy-driven cutover gate:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_cutover.py
```

And a third gate for rule-driven canary routing:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_rule_routing.py
```

That gate compares the current catalog lane against a preview catalog lane with canonical profile renames plus `aliasProfileIds`, and verifies that:

- grouped optimizer semantics stay stable
- legacy planner-requested ids still survive in `runtimeProfileRequestedIds`
- preview lanes materialize the new canonical `runtimeProfileIds`

For scheduler-style resolution, the committed window-set sample now records both:

- `runtimeProfileFamilyRegistryReference`
- `runtimeProfileCatalogReference`

So you can tell which family/lane selected the catalog, and which exact catalog contract was used after that resolution.

`daily_review_mock.py` and `run_offline_optimizer_cycle.py` now also accept:

```bash
--input-manifest skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json
--input-bundle skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json
```

When that path is used, the resulting daily-review artifact records:

- `generatedFrom.optimizerInputBundleSchemaVersion`
- `generatedFrom.optimizerInputBundleId`
- `generatedFrom.optimizerInputBundleGeneratedAt`
- `generatedFrom.optimizerInputBundleGeneratedFrom`
- `generatedFrom.optimizerInputManifestSchemaVersion`
- `generatedFrom.optimizerInputManifestId`
- `generatedFrom.optimizerInputManifestGeneratedAt`
- `generatedFrom.optimizerInputManifestGeneratedFrom`
- `generatedFrom.optimizerInputSources`

There is now also a bundle-style runner for cron-oriented offline evaluation:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py
python3 skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py --include-weekly-promotion
```

That runner emits one `optimizer-offline-cycle.v1` payload containing:

- summary fields for scheduling and dashboards
- the full daily review artifact
- an optional weekly promotion artifact when the cycle is run in weekly mode

The preview migration path now has two distinct runtime modes:

- `v1/exact`: optimizer consumes the legacy ranking top-level fields
- `vNext-preview/exact`: optimizer consumes `ranking.optimizerHandoff`
- `vNext-preview/compat`: optimizer can synthesize `optimizerHandoff` from legacy top-level fields

The new cutover rehearsal gate compares the first two directly:

```bash
python3 skills/autotiktok/scripts/validate_preview_lane_cutover.py
```

That is the quickest way to check whether switching module 2 to the preview canonical handoff surface changes optimizer-facing business semantics.

There is now a second audit for downstream orchestrators:

```bash
python3 skills/autotiktok/scripts/validate_preview_lane_consumer_cutover.py
```

That one is narrower and more aggressive: it corrupts legacy top-level ranking mirrors and confirms that preview-lane consumers such as stage-matrix and workflow-summary continue reading from `optimizerHandoff`.

There is also a preview-default wrapper rollout gate:

```bash
python3 skills/autotiktok/scripts/validate_preview_default_rollout.py
```

Use that when you want to confirm that:

- preview-first wrappers now default to `vNext-preview/exact`
- explicit `--use-current-lane` fallback still keeps the current live lane available for fixture-alignment workflows

When that check passes, the resulting optimizer artifacts now carry forward:

- `generatedFrom.rankingOptimizerContractVersion` on daily review
- `generatedFrom.dailyReviewRankingOptimizerContractVersion` on weekly promotion

This keeps later replay and provenance checks tied to the exact handoff contract version.

The propagated metadata now includes:

- contract id
- contract version
- validation mode
- validated flag
- surface source
- deprecation phase
- canonical surface
- deprecated top-level field list
- next hard-fail contract version
- compat alias list

`surface source` is the important new bit for replay:

- `legacy_top_level` means module 2 consumed the current top-level ranking fields
- `optimizer_handoff` means module 2 consumed the preview canonical handoff envelope
- `legacy_top_level_compat` means module 2 had to synthesize the preview envelope from deprecated fields

The deprecation metadata is the important new bit for migration planning:

- `dual_write_preview` means legacy top-level fields still exist, but they are already marked deprecated
- `optimizerHandoff` is the canonical consumer surface from the preview contract onward
- `ranking-optimizer-contract.v2` is the declared next point where those deprecated top-level fields can move from preview mirror to hard-fail territory

Validate the optimizer-owned fixture set with:

```bash
python3 {baseDir}/scripts/validate_optimizer_fixtures.py
```

Validate the committed bundle against current deterministic generation with:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_input_bundle_alignment.py
```

Validate the committed manifest against current deterministic generation with:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_input_manifest_alignment.py
```

## Output Artifacts

The optimizer scaffold writes:

- [../fixtures/daily-review.sample.json](../fixtures/daily-review.sample.json)
- [../fixtures/weekly-promotion.sample.json](../fixtures/weekly-promotion.sample.json)
- [../fixtures/optimizer-runtime-artifact-registry.sample.json](../fixtures/optimizer-runtime-artifact-registry.sample.json)
- [../fixtures/optimizer-offline-cycle-daily.sample.json](../fixtures/optimizer-offline-cycle-daily.sample.json)
- [../fixtures/optimizer-offline-cycle.sample.json](../fixtures/optimizer-offline-cycle.sample.json)
- [../fixtures/optimizer-eval-run-daily.sample.json](../fixtures/optimizer-eval-run-daily.sample.json)
- [../fixtures/optimizer-eval-run.sample.json](../fixtures/optimizer-eval-run.sample.json)
- [../fixtures/optimizer-eval-batch-manifest.sample.json](../fixtures/optimizer-eval-batch-manifest.sample.json)
- [../fixtures/optimizer-eval-window-set.sample.json](../fixtures/optimizer-eval-window-set.sample.json)
- [../fixtures/optimizer-eval-batch-history-manifest.sample.json](../fixtures/optimizer-eval-batch-history-manifest.sample.json)
- [../fixtures/optimizer-eval-batch.sample.json](../fixtures/optimizer-eval-batch.sample.json)
- [../fixtures/optimizer-eval-batch-history.sample.json](../fixtures/optimizer-eval-batch-history.sample.json)
- [../fixtures/optimizer-job-shadow-compare-plan.sample.json](../fixtures/optimizer-job-shadow-compare-plan.sample.json)
- [../fixtures/optimizer-job-shadow-compare.sample.json](../fixtures/optimizer-job-shadow-compare.sample.json)
- [../fixtures/optimizer-job-shadow-compare-plan.daily.sample.json](../fixtures/optimizer-job-shadow-compare-plan.daily.sample.json)
- [../fixtures/optimizer-job-shadow-compare-plan.weekly.sample.json](../fixtures/optimizer-job-shadow-compare-plan.weekly.sample.json)
- [../fixtures/optimizer-job-shadow-compare.daily.sample.json](../fixtures/optimizer-job-shadow-compare.daily.sample.json)
- [../fixtures/optimizer-job-shadow-compare.weekly.sample.json](../fixtures/optimizer-job-shadow-compare.weekly.sample.json)
- [../fixtures/optimizer-job-shadow-compare-batch-manifest.sample.json](../fixtures/optimizer-job-shadow-compare-batch-manifest.sample.json)
- [../fixtures/optimizer-job-shadow-compare-batch.sample.json](../fixtures/optimizer-job-shadow-compare-batch.sample.json)
- [../../autotiktok/fixtures/optimizer-stage-matrix.sample.json](../../autotiktok/fixtures/optimizer-stage-matrix.sample.json)

Build them explicitly with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py \
  --input-manifest skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/run_offline_optimizer_cycle.py \
  --input-bundle skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json \
  --include-weekly-promotion
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_runtime_artifact_registry.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_run.py \
  --input-offline-cycle skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle-daily.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_run.py \
  --input-offline-cycle skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_run.py --exclude-weekly-promotion
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_run.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_manifest.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_window_set.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch_history_manifest.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch.py \
  --input-eval-batch-manifest skills/autotiktok-strategy-optimizer/fixtures/optimizer-eval-batch-manifest.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch.py \
  --input-eval-batch-manifest skills/autotiktok-strategy-optimizer/fixtures/optimizer-eval-batch-history-manifest.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare_plan.py \
  --input-schedule-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.sample.json \
  --input-rollout-policy skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-rollout-policy.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare.py \
  --input-schedule-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.sample.json \
  --input-rollout-policy skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-rollout-policy.sample.json \
  --input-compare-plan skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-shadow-compare-plan.sample.json
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare_batch_manifest.py
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_job_shadow_compare_batch.py \
  --input-batch-manifest skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-shadow-compare-batch-manifest.sample.json
```

The committed batch sample now compares a daily-only eval run against a weekly-promotion eval run through that manifest, rather than relying on an implicit in-memory comparison set.

The committed history batch sample now goes one step further: it compares two replay batches (`2026-04-12` and `2026-04-15`), with one daily-only lane and one weekly lane in each batch.

That historical sample now comes from this chain:

- `optimizer-runtime-artifact-registry.sample.json`
- `optimizer-eval-window-set.sample.json`
- `optimizer-eval-batch-history-manifest.sample.json`
- `optimizer-eval-batch-history.sample.json`

So the committed history replay lane is no longer driven by hand-authored eval-run entry lists. It is driven by a more cron-shaped window-set object first.

That committed window set now intentionally mixes runtime source kinds instead of only reusing base eval-run paths:

- the recent daily lane references a catalog entry backed by `inputManifestPath`
- the recent weekly lane references a catalog entry backed by `inputBundlePath`
- the two historical replay lanes reference catalog entries backed by `inputOfflineCyclePath`

`optimizer-eval-batch.v1` now exposes both a flat item list and grouped comparison summaries. The grouped view is keyed by `summary.comparisonDimension` and currently records:

- `groupValue`
- `evalRunCount`
- `runtimeSourceKinds`
- `runtimeSourceIds`
- `modeCounts`
- `weeklyDecisionCounts`
- `rankingRunIds`
- `rankingProfileIds`
- `evaluationWindows`
- `historyBatchLabels`
- `historyWindowLabels`
- `scenarioLabels`
- average topic and combined reward
- average post coverage
- best eval-run id inside the group

The top-level batch summary now also records both `runtimeSourceKinds` and `runtimeSourceIds`, so history replay can prove which scheduler-facing source families and which planner-level source bindings participated in the batch without reopening every nested eval run.

Validate the optimizer stage matrix shape against current deterministic generation with:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_alignment.py
```

Validate the intended stage-mode semantics with:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_expectations.py
```

## Daily Review Report Shape

The daily review report summarizes:

- champion topic reward breakdown
- champion combined reward breakdown
- ranking profile-selection context and snapshot provenance
- ranking candidate-source provenance
- challenger input provenance and observation-window summary
- ranking review and rejection summary
- diagnostics
- shadow leaderboard
- recommendation

## Weekly Promotion Report Shape

The weekly promotion report summarizes:

- champion baseline
- champion profile-selection provenance carried forward from daily review
- champion candidate-source provenance carried forward from daily review
- challenger input kind carried forward from daily review
- best eligible challenger
- reward delta
- hard-gate checks
- explicit `promotionCandidateReviews[*]` for each challenger
- explicit `championSafetyReview` for champion-side rollback / keep decisions
- promote, keep-champion, or rollback-champion decision

The committed weekly sample now also carries champion rollback review metadata such as:

- `rollbackEligible`
- `rollbackTriggered`
- `rollbackSeverity`
- `rollbackReasonCodes`

The committed weekly sample now also carries stage-specific gate provenance such as:

- `weeklyStageMode`
- `weeklyStagePolicyId`
- `weeklyStagePolicySelectionSource`

The committed weekly fixture family now includes:

- `optimizer-weekly-review-window.sample.json`
- `optimizer-weekly-review-window.scale.sample.json`
- `optimizer-weekly-review-window.search-priority.sample.json`
- `weekly-promotion.sample.json`
- `weekly-promotion.scale.sample.json`
- `weekly-promotion.search-priority.sample.json`

The committed weekly sample now records challenger-side gate evaluations such as:

- `minimum_hard_gate_pass_days`
- `minimum_average_reward_delta`
- `minimum_average_holdout_delta`
- `dup_rate_budget`
- `executable_rate_budget`
- `type_coverage_budget`
- `post_coverage_budget`

and champion-side safety evaluations such as:

- `window_level_rollback_signal`
- `rollback_eligibility`
- `holdout_floor_breach_days`
- `combined_reward_floor_breach_days`

So the weekly artifact can now explain both:

- why a challenger was promoted
- why a challenger was rejected while the champion was still kept
- whether the champion is merely under watch, in warning, or in a critical rollback state
- which stage-specific weekly gate profile was applied to make that decision

Use the dedicated semantic gate when you want to verify those committed stage-specific fixtures:

```bash
python3 skills/autotiktok/scripts/validate_weekly_stage_policy_alignment.py
```

## Eval Run Shape

The eval-run artifact is the current top-level offline evaluation record. It summarizes:

- the offline cycle identity
- the ranking run and evaluation window
- topic reward and combined reward
- post coverage and challenger input kind
- rejected-count and shadow-leader summary
- optional weekly promotion outcome
- input-source provenance for backfill, performance, and challenger job runs

Build it with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_run.py
```

That artifact is intentionally thin: it carries the key comparison fields up front and keeps the full offline cycle under `artifacts.offlineCycle`.

## Eval Batch Shape

The eval-batch artifact is the next aggregation layer above eval-run. It summarizes:

- how many eval runs are in the batch
- mode counts such as `daily_review_only` vs `daily_with_weekly_promotion`
- weekly decision counts across the batch
- average topic reward / combined reward / post coverage
- the best eval run in the batch
- shared input-source kinds across backfill, performance, and challenger inputs

Build it with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_eval_batch.py
```

The default sample builder produces a small deterministic comparison set:

- one eval run in `daily_review_only` mode
- one eval run in `daily_with_weekly_promotion` mode

That keeps the batch artifact truly aggregated, while still remaining deterministic and easy to diff in git.

## Why These Are Mock Artifacts

These files are intentionally lightweight. Their purpose is to:

- unblock optimizer workflow development
- show stable object shapes
- provide replayable examples for later automation

They do not claim to be final production evaluation outputs.
