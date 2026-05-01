# AutoTikTok End-to-End Workflow

This reference explains how the three AutoTikTok skills fit together as one decoupled system.

## Skill Order

Use the skills in this order:

1. `autotiktok-topic-discovery`
2. `autotiktok-topic-ranking`
3. `autotiktok-strategy-optimizer`

## Responsibilities

### Discovery

Discovery converts signal-level inputs into:

- `evidenceBundles`
- `mergeGroups`
- `topicCandidates`

Current mock output:

- [../../autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json](../../autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json)

### Ranking

Ranking consumes candidates, account context, and scoring profiles to emit:

- `topicScores`
- `predictionRun`

Current mock output:

- [../../autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json](../../autotiktok-topic-ranking/fixtures/ranking-dry-run.sample.json)

### Optimizer

Optimizer consumes ranking output plus topic outcomes, post-performance signals, and challenger observations to emit:

- `dailyReviewReport`
- `weeklyReviewWindow`
- `weeklyPromotionDecision`

Current mock outputs:

- [../../autotiktok-strategy-optimizer/fixtures/daily-review.sample.json](../../autotiktok-strategy-optimizer/fixtures/daily-review.sample.json)
- [../../autotiktok-strategy-optimizer/fixtures/optimizer-weekly-review-window.sample.json](../../autotiktok-strategy-optimizer/fixtures/optimizer-weekly-review-window.sample.json)
- [../../autotiktok-strategy-optimizer/fixtures/weekly-promotion.sample.json](../../autotiktok-strategy-optimizer/fixtures/weekly-promotion.sample.json)

## Artifact Chain

The committed mock sample family now covers this chain:

1. `source-snapshots.sample.json`
2. `signal-items.sample.json`
3. `video-samples.sample.json`
4. `discovery-snapshot-materialization.sample.json`
5. `raw-signals.sample.json`
6. `discovery.json`
7. `ranking.json`
8. `topic-outcome-backfill-run.json`
9. `post-performance-signal-run.json`
10. `challenger-evaluation-run.json`
11. `optimizer-source-artifact-catalog.json`
12. `optimizer-source-provider-registry.json`
13. `optimizer-source-provider-catalog.json`
14. `optimizer-job-artifact-resolver.json`
15. `optimizer-input-source-registry.json`
16. `optimizer-input-manifest.json`
17. `optimizer-input-rollout-policy.json`
18. `optimizer-input-bundle.json`
19. `optimizer-runtime-artifact-registry.json`
20. `daily-review.json`
21. `optimizer-weekly-review-window.json`
22. `weekly-promotion.json`
23. `optimizer-offline-cycle-daily.json`
24. `optimizer-offline-cycle.json`
25. `optimizer-job-schedule.json`
26. `optimizer-daily-job-run.json`
27. `optimizer-weekly-job-run.json`
28. `optimizer-job-shadow-compare-plan.json`
29. `optimizer-job-shadow-compare.json`
30. `optimizer-job-shadow-compare-batch-manifest.json`
31. `optimizer-job-shadow-compare-batch.json`
32. `optimizer-eval-run-daily.json`
33. `optimizer-eval-run.json`
34. `optimizer-eval-batch-manifest.json`
35. `optimizer-eval-batch.json`
36. `optimizer-eval-window-set.json`
37. `optimizer-eval-batch-history-manifest.json`
38. `optimizer-eval-batch-history.json`

The first handoff that matters is `topicCandidates`: ranking can now consume discovery output directly instead of using a separately curated candidate fixture.

The shared ranking fixture at `skills/autotiktok/fixtures/topic-candidates.fixture.json` is now treated as a derived artifact from discovery, not a separately authored source of truth.

On the discovery side there is now also an explicit ingest seam before the old raw-signal fixture. The committed sample freezes:

- three standalone storage-shaped inputs:
  - `sourceSnapshots`
  - `signalItems`
  - `videoSamples`
- one derived snapshot-materialization input
- one compatibility raw-signal input
- one derived discovery output

So discovery is no longer modeled as "hand-authored raw signals go straight into packaging". It is now "standalone snapshot artifacts materialize into the snapshot-materialization contract, then into the raw-signal compatibility layer, then the packaging core builds evidence bundles and topic candidates".

The committed discovery artifact now also freezes two discovery-owned intermediate layers before ranking:

- `normalizedSignals`
- `topicAbstractions`

So module 1 is no longer only exposing final packaged candidates. It now exposes the deterministic normalization and abstraction layers that explain how those candidates were constructed.

The current discovery artifact now also freezes the merge / packaging layer explicitly:

- `mergeClassification`
- `dedupeDecision`
- `searchEvidenceSummary`
- `executionEvidenceSummary`
- `packagingReadiness`

So downstream workflow review can now inspect not just “what topic candidate came out”, but also “how discovery decided to merge and package the underlying signals”.

## One-Shot Workflow Runner

To run the whole mock workflow and keep the generated artifacts:

```bash
python3 skills/autotiktok/scripts/run_autotiktok_workflow.py \
  --artifacts-dir /tmp/autotiktok-workflow \
  --summary-output /tmp/autotiktok-workflow-summary.json
```

The workflow runner:

1. runs discovery dry-run
2. validates the generated candidate contract
3. runs ranking against the generated candidates
4. builds an optimizer input manifest
5. materializes an optimizer input bundle from that manifest
6. runs the daily review mock from that bundle
7. runs the weekly promotion mock
8. writes a compact summary of the full chain, including ranking profile-selection provenance

That summary now also carries candidate-source provenance from ranking, so the workflow can distinguish:

- ranking over direct discovery output
- ranking over the shared derived candidates fixture
- ranking over any future standalone candidate fixture

It also now records both the optimizer manifest identity and the optimizer bundle identity, so the workflow can point at the exact scheduler handoff and the exact canonical runtime object that fed daily review.

The workflow summary now also records discovery ingest provenance from the standalone snapshot artifacts, including:

- `discoveryMaterializationSource`
- `sourceSnapshotSchemaVersion`
- `signalItemsSchemaVersion`
- `videoSamplesSchemaVersion`

The default optimizer sample lane now uses scheduler-facing job-run envelopes for:

- topic outcome backfill
- post performance signal
- challenger evaluation

That means workflow and stage-matrix replays are now closer to the intended cron topology: manifest points at job outputs, bundle materialization unwraps them into canonical inner artifacts, and daily review records the resolved input-source metadata under `generatedFrom.optimizerInputSources`.

The real-shadow stand-in lane now also has one extra layer underneath the resolver:

- `optimizer-source-artifact-catalog`
- `optimizer-source-provider-registry`
- `optimizer-source-provider-catalog`
- `optimizer-job-artifact-resolver`
- `optimizer-input-source-registry`
- `optimizer-input-manifest.real-shadow`

So the current stand-in is no longer just “resolver maps binding to path”. It is “source binding -> resolver entry -> source provider id -> provider catalog entry -> provider binding id -> artifact catalog entry -> concrete artifact path”, which is closer to how a future artifact catalog or source-provider-backed runtime should behave.

The offline evaluation layer now adds a second orchestration step above daily and weekly artifacts:

- one scheduler-facing `optimizer-job-schedule`
- one planner-facing `optimizer-runtime-artifact-registry`
- one daily-only `optimizer-offline-cycle`
- one weekly-promotion `optimizer-offline-cycle`
- one daily-only `optimizer-eval-run`
- one weekly-promotion `optimizer-eval-run`
- one `optimizer-eval-batch-manifest`
- one grouped `optimizer-eval-batch`
- one scheduler-facing `optimizer-eval-window-set`
- one historical replay `optimizer-eval-batch-history-manifest`
- one grouped `optimizer-eval-batch-history`

That means the mock workflow now models three layers at once:

- runtime execution handoff: `manifest -> bundle`
- scheduler dispatch handoff: `input-rollout-policy -> job-schedule -> scheduled job -> optimizer-job-run -> optimizer-job-shadow-compare-plan -> optimizer-job-shadow-compare -> optimizer-job-shadow-compare-batch-manifest -> optimizer-job-shadow-compare-batch`
- offline comparison handoff: `runtime-artifact-registry + window-set -> history-manifest -> eval-batch`, plus `offline-cycle -> eval-run -> eval-batch-manifest -> eval-batch`

For recurring execution on a real OpenClaw Gateway, the preferred runtime path is now the standard cron runtime:

- `optimizer-openclaw-cron-contract`
- `run_openclaw_cron_daily_optimizer.py`
- `run_openclaw_cron_weekly_optimizer.py`

Those entrypoints still emit the same `optimizer-job-run.v1` artifacts, but they now default to the canonical manifest / weekly-window inputs that match the committed runtime fixtures.

The older scheduler-facing artifacts remain in the sample family for:

- deterministic rehearsal
- fixture generation
- cutover validation

Those scheduler-facing artifacts now also self-identify inside the payload as:

- `runtimeRole=compatibility_rehearsal`
- `preferredRecurringRuntime=openclaw_cron`
- `intendedUses=[fixture_generation, deterministic_rehearsal, cutover_validation]`

but they are no longer the preferred recurring runtime source of truth once OpenClaw cron is available.

That scheduler dispatch handoff now has an explicit compare-plan layer plus a compare object on top. `optimizer-job-shadow-compare-plan` first freezes two committed comparisons:

- `daily_raw_shadow_vs_production`
- `weekly_real_shadow_vs_production`

Then `optimizer-job-shadow-compare` materializes those plan entries into concrete scheduled-job comparisons. On top of that, `optimizer-job-shadow-compare-batch-manifest` freezes the daily and weekly compare artifacts as one grouped scheduler-facing input, and `optimizer-job-shadow-compare-batch` aggregates them by `scheduleId`. So sample lane, raw-shadow lane, and real-shadow lane are no longer only compared inside ad hoc validators. They also have committed scheduler-facing plan, compare, and compare-batch artifacts with rollout-class, source-lane, resolver, provider-catalog, provider-registry, and source-artifact-catalog provenance.

The weekly optimizer lane now also has its own dedicated semantic handoff:

- `daily-review -> optimizer-weekly-review-window -> weekly-promotion`

That means weekly promotion is no longer modeled as "re-read the daily review and decide immediately". The committed sample family now freezes a multi-day weekly review window first, then derives promotion or rollback from that object.

The historical replay lane is now intentionally window-set-driven first. It freezes replay windows and scenarios in `optimizer-eval-window-set`, then derives `optimizer-eval-batch-history-manifest`, then derives the grouped batch result. That is closer to how future offline history scans will stitch together many past runs without hand-authoring full JSON for every batch.

That window-set layer is now also mixed-source on purpose. The committed sample uses a top-level `runtimeSources` catalog plus per-window `runtimeSourceId` references:

- one catalog entry backed by `inputManifestPath`
- one catalog entry backed by `inputBundlePath`
- two catalog entries backed by `inputOfflineCyclePath`

Those catalog entries now prefer a logical `sourceDescriptor` over direct file paths. The current committed sample uses the planner-oriented `planner_runtime_binding` shape (`profileId`), and the history-manifest builder resolves each descriptor through a planner rollout-policy step first (`runtimeProfileRolloutPolicyReference`), then through a planner family/lane step (`runtimeProfileFamilyRegistryReference`), then through the resolved runtime profile catalog reference (`catalogId` + `catalogFamily` + `catalogVersion` + `schemaVersion`) before writing `evalRunEntries[*].runtimeSource`.

That resolution can now happen through a separate `optimizer-runtime-profile-catalog` plus `optimizer-runtime-artifact-registry`, and the binding itself can be explained by `optimizer-runtime-materialization-plan`, so planner intent, environment-specific artifact paths, and materialization semantics are no longer coupled in one object.

So historical replay is no longer restricted to "take an existing eval-run path and relabel it". The history manifest can now materialize eval runs directly from scheduler-facing runtime inputs, and the grouped batch summary records the participating `runtimeSourceKinds`, `runtimeProfileIds`, `runtimeProfileCatalogIds` / `runtimeProfileCatalogFamilies` / `runtimeProfileCatalogVersions`, concrete `runtimeSourceIds`, resolved `materializationPlanIds`, planner-facing `jobFamilyGroups` / `materializationProfiles`, and the resulting `materializationStrategies`.

There is now also a runtime profile catalog cutover rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_catalog_cutover.py
```

That gate compares:

- current catalog lane: current canonical `runtimeProfileIds`
- preview catalog lane: preview canonical ids plus alias-based compatibility for legacy planner requests

It asserts that optimizer-facing batch semantics stay stable while the preview lane moves canonical profile identity into the preview catalog family/version.

There is now also a runtime profile rollout-policy cutover rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_cutover.py
```

That gate keeps the same current-vs-preview semantic comparison, but it now drives lane selection through rollout-policy classes (`production` vs `preview_canary`) rather than an explicit `--runtime-profile-lane` override.

There is now also a rule-routing rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_rule_routing.py
```

That gate verifies a preview-marked batch (for example `batchWindowLabel=preview:...`) is automatically routed onto the `preview_canary` class without passing an explicit class override.

There is now also a purpose-routing rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_purpose_routing.py
```

That gate verifies an explicitly tagged planner intent (currently `windowSetPurpose=preview_validation`) is also enough to route the window set onto `preview_canary`, without relying on batch-label naming conventions.

That path is now purpose-policy-driven rather than rule-driven: the rollout policy sample declares `preview_validation` through `preview_validation_default -> preview_validation_template -> preview_validation_family`, so the window-set builder resolves `policy_purpose` before considering more specific rule selectors.

There is now also a window+mode routing rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_window_mode_routing.py
```

That gate verifies a more scheduler-shaped composite rule can route to `preview_canary` from explicit planner intent plus window-level selectors, currently `windowSetPurpose=weekly_shadow_rehearsal` together with a historical weekly window.

There is now also a dimension-routing rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_dimension_routing.py
```

That gate verifies scheduler-level batch metadata can also drive rollout selection: the current sample routes to `preview_canary` when planner intent declares `windowSetPurpose=profile_compare_validation`, `windowSetBatchType=cross_profile_comparison`, and `comparisonDimension=rankingProfileId`.

That path is also purpose-policy-driven now. The policy sample declares `profile_compare_validation` as a preview-purpose default and also freezes the default batch type plus comparison dimension for that eval purpose, so the builder can resolve those defaults before history-manifest materialization.

The rollout-policy sample now also separates planner metadata defaults from planner metadata contract families and concrete contracts. In practice that means `optimizer-eval-window-set.generatedFrom` records both the source of `windowSetBatchType` / `comparisonDimension` and the resolved `runtimeProfilePlannerMetadataPolicyId` / `runtimeProfilePlannerMetadataContractFamilyId` / `runtimeProfilePlannerMetadataContractId`, so downstream replay artifacts can prove not only where the defaults came from but also which allowed batch-type/dimension contract family and concrete contract were enforced.

There is now also a planner-metadata contract enforcement rehearsal:

```bash
python3 skills/autotiktok/scripts/validate_runtime_profile_planner_metadata_contract_enforcement.py
```

That gate verifies the happy path for both the standard replay contract and the cross-profile comparison contract, then deliberately passes invalid explicit overrides to prove the window-set builder rejects disallowed `windowSetBatchType` / `comparisonDimension` combinations before any history manifest or eval batch is materialized.

## Discovery Sample Output Alignment

The committed discovery sample output is treated as a derived artifact from the raw-signal fixture plus discovery policy.

Validate it with:

```bash
python3 skills/autotiktok/scripts/validate_discovery_output_alignment.py
```

Regenerate it with:

```bash
python3 skills/autotiktok/scripts/sync_discovery_sample_output.py
```

## Shared Fixture Alignment

The shared ranking candidates fixture is a convenience input for standalone ranking runs, but it should stay aligned with the discovery sample artifact.

Validate alignment with:

```bash
python3 skills/autotiktok/scripts/validate_shared_fixture_alignment.py
```

Regenerate the shared fixture from discovery with:

```bash
python3 skills/autotiktok/scripts/sync_shared_candidates_fixture.py
```

## Ranking Sample Output Alignment

The committed ranking sample output is also treated as a derived artifact.

Its default candidate input is now the committed discovery artifact itself, while `skills/autotiktok/fixtures/topic-candidates.fixture.json` stays as a derived compatibility fixture for consumers that still want the candidate-only surface.

Validate it with:

```bash
python3 skills/autotiktok/scripts/validate_ranking_output_alignment.py
```

Regenerate it with:

```bash
python3 skills/autotiktok/scripts/sync_ranking_sample_output.py
```

## Ranking Profile Matrix Alignment

The committed ranking profile matrix is also treated as a derived artifact.

Validate it with:

```bash
python3 skills/autotiktok/scripts/validate_ranking_profile_matrix_alignment.py
```

Regenerate it with:

```bash
python3 skills/autotiktok/scripts/sync_ranking_profile_matrix.py
```

For a semantic gate on the committed matrix, run:

```bash
python3 skills/autotiktok/scripts/validate_ranking_profile_matrix_expectations.py
```

## Optimizer Stage Matrix Alignment

The committed optimizer stage matrix is also treated as a derived artifact.

Validate it with:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_alignment.py
```

For a semantic gate on the committed matrix, run:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_stage_matrix_expectations.py
```

Regenerate it with:

```bash
python3 skills/autotiktok/scripts/sync_optimizer_stage_matrix.py
```

To inspect the live cross-stage replay directly:

```bash
python3 skills/autotiktok/scripts/run_optimizer_stage_matrix.py
```

To rehearse the preview cutover lane directly:

```bash
python3 skills/autotiktok/scripts/run_optimizer_stage_matrix.py \
  --ranking-contract-version ranking-optimizer-contract.vNext-preview \
  --ranking-contract-validation-mode exact
```

In that preview lane, the stage-matrix runner now reads ranking semantics from the canonical `optimizerHandoff` surface instead of the deprecated top-level mirror.

There are now preview-first wrappers for day-to-day manual use:

```bash
python3 skills/autotiktok/scripts/run_preview_optimizer_stage_matrix.py
python3 skills/autotiktok/scripts/run_preview_autotiktok_workflow.py --summary-output /tmp/workflow-preview.json
```

Both wrappers default to `vNext-preview/exact`. If you need to fall back to the current live lane, pass:

```bash
--use-current-lane
```

## Optimizer Sample Output Alignment

The committed optimizer sample outputs are also treated as derived artifacts.

Validate them with:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_output_alignment.py
```

Regenerate them with:

```bash
python3 skills/autotiktok/scripts/sync_optimizer_sample_outputs.py
```

## Ranking To Optimizer Contract Gate

To validate the optimizer-facing subset of ranking output directly:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract.py
```

This gate checks the fields that `daily_review_mock.py` and `optimizer_lib.py` actually consume:

- `profileSelection`
- `candidateSource`
- `scores`
- `predictionRun`
- `rankingSummary`
- `rerankDiagnostics`

`daily_review_mock.py` now uses the same shared contract helper at runtime, so the optimizer stage fails fast on ranking handoff regressions.

That validated handoff now propagates into derived artifacts as metadata:

- daily review carries `generatedFrom.rankingOptimizerContractVersion`
- weekly promotion carries `generatedFrom.dailyReviewRankingOptimizerContractVersion`
- optimizer stage matrix carries `generatedFrom.rankingOptimizerContractVersion`
- workflow summary carries `generatedFrom.rankingOptimizerContractVersion`

The contract surface is now version-ready rather than a bare string. Derived artifacts carry:

- `rankingOptimizerContractId`
- `rankingOptimizerContractVersion`
- `rankingOptimizerContractValidationMode`
- `rankingOptimizerContractValidated`
- `rankingOptimizerSurfaceSource`
- `rankingOptimizerDeprecationPhase`
- `rankingOptimizerCanonicalSurface`
- `rankingOptimizerDeprecatedTopLevelFields`
- `rankingOptimizerNextHardFailContractVersion`
- `rankingOptimizerCompatAliasesApplied`

There is now also a forward-compat rehearsal gate:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py
```

That gate now defaults to the true dual-write preview path: committed ranking output must expose a canonical `optimizerHandoff` block while still mirroring the legacy top-level fields.

So the current workflow state is now explicit:

- stable runtime path remains `v1/exact`
- preview canonical path is `vNext-preview/exact`
- fallback migration path is `vNext-preview/compat`
- declared next hard-fail point for deprecated top-level ranking fields is `ranking-optimizer-contract.v2`

If you want to explicitly rehearse migration fallback from old ranking payloads, use:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py \
  --validation-mode compat
```

There is now also a lane-cutover comparison gate:

```bash
python3 skills/autotiktok/scripts/validate_preview_lane_cutover.py
```

That gate runs both:

- current lane: `v1/exact`
- preview canonical lane: `vNext-preview/exact`

and confirms that stage-matrix plus workflow-summary business semantics stay stable while the optimizer consumer surface switches from legacy top-level fields to `optimizerHandoff`.

There is also a consumer cutover audit:

```bash
python3 skills/autotiktok/scripts/validate_preview_lane_consumer_cutover.py
```

That audit intentionally corrupts the legacy top-level ranking mirrors and verifies that preview-lane orchestrators still resolve their summary fields from `optimizerHandoff`.

There is also a preview-default rollout gate:

```bash
python3 skills/autotiktok/scripts/validate_preview_default_rollout.py
```

That one checks the wrapper commands themselves:

- wrapper default path is `vNext-preview/exact`
- explicit `--use-current-lane` fallback still preserves the live lane

To inspect the current machine-readable inventory of remaining live-lane defaults:

```bash
python3 skills/autotiktok/scripts/list_live_lane_dependencies.py
```

To validate that inventory:

```bash
python3 skills/autotiktok/scripts/validate_live_lane_dependency_inventory.py
```

## Live-Lane Fallback Inventory

The following surfaces intentionally still keep the live lane as their default because they are tied to committed exact-path fixtures:

- `skills/autotiktok/scripts/sync_optimizer_stage_matrix.py`
- `skills/autotiktok/scripts/sync_workflow_summary_sample.py`
- `skills/autotiktok/scripts/validate_optimizer_stage_matrix_alignment.py`
- `skills/autotiktok/scripts/validate_workflow_summary_alignment.py`
- `skills/autotiktok/scripts/validate_artifact_provenance_chain.py`

## Workflow Summary Sample Alignment

The committed workflow summary sample is also treated as a derived artifact.

Validate it with:

```bash
python3 skills/autotiktok/scripts/validate_workflow_summary_alignment.py
```

Regenerate it with:

```bash
python3 skills/autotiktok/scripts/sync_workflow_summary_sample.py
```

## Individual Commands

Use these when you want to inspect one stage at a time:

```bash
python3 skills/autotiktok-topic-discovery/scripts/discovery_dry_run.py \
  --output /tmp/discovery.json

python3 skills/autotiktok-topic-ranking/scripts/dry_run_ranking.py \
  --candidates /tmp/discovery.json \
  --context skills/autotiktok/fixtures/scoring-context.fixture.json \
  --profiles skills/autotiktok/fixtures/scoring-profiles.fixture.json \
  --output /tmp/ranking.json

python3 skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py \
  --ranking-input /tmp/ranking.json \
  --context-input skills/autotiktok/fixtures/scoring-context.fixture.json \
  --output /tmp/daily-review.json

python3 skills/autotiktok/scripts/run_autotiktok_workflow.py \
  --summary-output /tmp/workflow-preview.json \
  --artifact-path-style basename \
  --ranking-contract-version ranking-optimizer-contract.vNext-preview \
  --ranking-contract-validation-mode exact

python3 skills/autotiktok-strategy-optimizer/scripts/weekly_promotion_mock.py \
  --daily-review-input /tmp/daily-review.json \
  --output /tmp/weekly-promotion.json
```

## Daily And Weekly Use

Use the workflow in two rhythms:

- Daily:
  - discovery refreshes candidate packaging
  - ranking produces the current recommendation set
  - optimizer produces the daily review report
- Weekly:
  - optimizer reads the accumulated daily-review state
  - weekly promotion decides whether the shadow challenger replaces the champion

## Smoke Test Entry Points

To run the complete local smoke set:

```bash
python3 skills/autotiktok/scripts/test_autotiktok_skills.py
```

To run only the end-to-end workflow smoke:

```bash
python3 skills/autotiktok/scripts/test_end_to_end_workflow.py
```

## Aggregate Artifact Maintenance

To refresh every committed mock artifact in the correct dependency order:

```bash
python3 skills/autotiktok/scripts/sync_all_mock_artifacts.py
```

To validate every committed mock artifact in one pass:

```bash
python3 skills/autotiktok/scripts/validate_all_mock_artifacts.py
```

To validate the cross-artifact provenance chain specifically:

```bash
python3 skills/autotiktok/scripts/validate_artifact_provenance_chain.py
```

That validator now checks the main pipeline chain plus both stage-matrix branches:

- discovery sample -> shared topic candidates fixture
- shared topic candidates fixture -> ranking sample
- shared topic candidates fixture -> ranking profile matrix
- ranking sample -> daily review sample -> weekly promotion sample
- ranking profile matrix -> optimizer stage matrix
- discovery + ranking + optimizer outputs -> workflow summary sample

## Why This Matters

Keeping discovery, ranking, and optimizer independently runnable preserves decoupling from OpenClaw core, while the hub workflow runner and smoke tests make the full system operable as one pipeline.
