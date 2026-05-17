---
name: autotiktok
description: >
  Compatibility hub and routing guardrail for the AutoTikTok skill set. Use
  when the user asks for the complete AutoTikTok chain, TikTok Top topics,
  download plus video understanding, enriched Top topics, or help routing work
  to discovery, ranking, or optimizer skills. For video understanding, route to
  autotiktok-topic-discovery first; official AutoTikTok MP4 understanding must
  call openclaw infer video describe through run_video_content_analysis_batch.py
  with google/gemini-3-flash-preview and must not be replaced by ffmpeg frame
  extraction, image analysis, or an auto-selected alternate video model.
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
- For any request that says "complete AutoTikTok chain", "video
  understanding", "download + understand video", or "enriched Top 5", route to
  `autotiktok-topic-discovery` first and use its native video-understanding
  path. The required sequence is normalized `videoDownloadManifest` ->
  `run_video_content_analysis_batch.py` -> `video-content-analysis.json` ->
  `build_enriched_signal_items.py` -> discovery -> ranking.
- For live TikTok Top topic requests, the standard production artifact pipeline
  is mandatory unless the user explicitly asks for a quick report only:
  `trending output` -> `source-snapshots.from-trending.json` +
  `video-samples.from-trending.json` +
  `signal-items.from-trending.synthetic.json` -> raw download manifest ->
  `video-download-manifest.json` -> `video-content-analysis.json` ->
  `signal-items.enriched.json` -> `discovery-dry-run.json` ->
  `ranking-dry-run.json` -> user-facing report.
- Preserve the user's requested count scope through the live pipeline. If the
  request clearly asks for `N` hot / trending videos using wording such as
  `Top5`, `5条热门视频`, `获取50个热门视频`, `从50个热门视频里`, or
  `analyze 20 trending videos`, pass that `N` to `autotiktok-trending` as
  `--direct-keep N --top-n N` unless the user explicitly asks for a broader
  collector pool plus a smaller downstream sample.
- When the user gives two counts, keep both scopes explicit. For example,
  "collect 50 and download the top 5" means collector scope 50 and download /
  video-understanding scope 5; "collect Top5 and analyze those 5" means the
  collector, download, video-understanding, discovery, and ranking scopes are all 5.
- Do not allow the standard artifact pipeline to silently expand a requested
  TopN run back to the collector example/default retained count. The generated
  `videoSamples`, `signalItems`, `discovery-dry-run.json`, and
  `ranking-dry-run.json` should reflect the chosen scope unless the report
  explicitly labels a broader metadata-only recall lane.
- Preserve the selected ranking view through the live pipeline. For generic
  TopN hot / trending requests, use the `absolute_hot` view. For explicit fresh
  / rising requests, use the `fresh_hot` view. Do not merge `fresh_hot` samples
  into an `absolute_hot` TopN run unless the user explicitly asks for a merged or
  comparative view.
- When a run intentionally keeps both `absolute_hot` and `fresh_hot` in the
  downstream discovery / ranking pool, the download and video-understanding
  scope must cover the deduped union of both views. Prefer
  `autotiktok-video-download --from-bakeoff ... --bakeoff-view both --per-view-max N`
  for merged TopN runs. Do not run
  `autotiktok-video-download --from-bakeoff ... --max N` with the original
  TopN count if that cap would download only `absolute_hot`; omit `--max` or set
  it to the combined deduped sample count, then run Gemini analysis for every
  downloaded MP4 before building `signal-items.enriched.json`.
- For any TopN run that includes downloading and MP4 understanding, every topic
  entering the final `ranking-dry-run.json` recommendation pool should map back
  to a sample from the selected view with a downloaded MP4 and
  `analysis_succeeded`. Metadata-only fallback items may be retained in a
  separate diagnostic lane, but they must not be presented as video-understood
  recommendations.
- Do not mark a live Top topic run complete when it stops at
  `video-content-analysis.json` plus a hand-written report. If
  `signal-items.enriched.json`, `discovery-dry-run.json`, or
  `ranking-dry-run.json` is missing, report the run as partial and continue the
  artifact pipeline before summarizing final Top topics.
- The final live Top topic recommendation must be derived from
  `ranking-dry-run.json` when the standard artifact pipeline is requested or
  implied. The report may quote `video-content-analysis.json` as evidence, but
  it must not replace discovery/ranking with ad hoc scoring prose.
- User-facing reports for download + video-understanding runs must include a
  `视频文件` column in the ranking score summary table. Use
  `autotiktok-topic-ranking/scripts/build_ranking_report.py` with
  `--ranking`, `--discovery`, and `--video-content-analysis` so each ranked
  topic shows the downloaded MP4 filename from `videoPath`.
- The default AutoTikTok MP4 understanding model is
  `google/gemini-3-flash-preview`. Do not rely on OpenClaw's automatic
  `video.describe` model selection for this lane; a direct one-off call must use
  `openclaw infer video describe --model google/gemini-3-flash-preview`.
- Do not satisfy AutoTikTok video understanding by extracting MP4 frames,
  calling image-description tools, or writing a one-off `report_gen.py`.
  The official lane must call `openclaw infer video describe` through
  `skills/autotiktok-topic-discovery/scripts/run_video_content_analysis_batch.py`.
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
- Run `python3 skills/autotiktok/scripts/validate_trending_discovery_adapter_contract_alignment.py` when you want to confirm focused `autotiktok-trending` output fixtures are recognized as either canonical video samples or raw/ranked rows that need adapter normalization.
- Run `python3 skills/autotiktok/scripts/validate_trending_source_snapshots_alignment.py` when you want to confirm `autotiktok-trending` outputs can materialize discovery `sourceSnapshots` with `public_tiktok` provenance.
- Run `python3 skills/autotiktok/scripts/validate_trending_video_samples_alignment.py` when you want to confirm `autotiktok-trending` outputs normalize into canonical discovery `videoSamples`.
- Run `python3 skills/autotiktok/scripts/validate_trending_signal_items_alignment.py` when you want to confirm normalized trending `videoSamples` can generate metadata-only synthetic discovery `signalItems`.
- Run `python3 skills/autotiktok/scripts/validate_trending_discovery_ranking_integration.py` when you want to confirm trending metadata can run through discovery materialization, discovery dry-run, and ranking.
- Run `python3 skills/autotiktok/scripts/validate_video_download_manifest_adapter_alignment.py` when you want to confirm raw `autotiktok-video-download` output can normalize into a per-`videoSample` manifest with missing/error/invalid/duplicate handling.
- Run `python3 skills/autotiktok/scripts/validate_video_content_analysis_contract_alignment.py` when you want to confirm the stage-8 `videoContentAnalysis` sidecar contract, focused fixture, and default `google/gemini-3-flash-preview` model config stay aligned.
- Run `python3 skills/autotiktok/scripts/validate_video_content_analysis_batch_runner_alignment.py` when you want to confirm the MP4 understanding batch runner regenerates the committed `videoContentAnalysis` sidecar from the normalized download manifest.
- Run `python3 skills/autotiktok/scripts/validate_enriched_signal_items_alignment.py` when you want to confirm `videoContentAnalysis` enriches synthetic `signalItems` and falls back safely for missing or failed MP4 analysis.
- Run `python3 skills/autotiktok/scripts/validate_enriched_discovery_ranking_integration.py` when you want to confirm enriched `signalItems` can run through discovery and ranking, with a focused metadata-only vs enriched comparison.
- Run `python3 skills/autotiktok/scripts/validate_video_understanding_live_smoke_docs_alignment.py` when you want to confirm the video-understanding live-ish smoke runbook keeps limit, cache, fallback, and default-model guidance intact.
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
