# AutoTikTok 模块 2 Schema 草案

这份草案用于冻结模块 2 的最小开发契约，优先服务以下目标：

- 让模块 2 可以先基于 mock `topicCandidate` 开发
- 降低模块 1 和模块 2 的联调阻塞
- 让后续 `predictionRun`、回放和评测不返工

当前建议优先冻结 9 份 schema：

1. `TopicCandidateSchema`
2. `ScoringContextSchema`
3. `FeatureVectorSchema`
4. `TopicScoreSchema`
5. `PredictionRunSchema`
6. `TopicOutcomeBackfillSchema`
7. `PostPerformanceSignalSchema`
8. `TopicRewardBreakdownSchema`
9. `CombinedRewardBreakdownSchema`

## 当前新增的联调冻结点

为了降低模块 2 排名层和评测层的联调风险，当前还额外冻结一份“ranking -> optimizer 最小消费子集”：

- `profileSelection`
- `candidateSource`
- `scores[*].topicId`
- `scores[*].topicFingerprint`
- `scores[*].priorityLevel`
- `scores[*].recommendedUse`
- `scores[*].scoreBreakdown.feasibility`
- `scores[*].rerankAdjustedScore`
- `scores[*].isRejected`
- `scores[*].rerankReasons`
- `predictionRun`
- `rankingSummary`
- `rerankDiagnostics`

这些字段不是新的 schema，而是 optimizer 当前真实消费的 ranking 输出子集。后续如果 ranking 输出扩展字段，可以继续加；但不能随意移除或改语义。

为了给后续模块 2 schema 升级预留迁移位点，下游评测产物还会继续记录一层 handoff contract surface metadata：

- `rankingOptimizerContractId`
- `rankingOptimizerContractVersion`
- `rankingOptimizerContractValidationMode`
- `rankingOptimizerContractValidated`

当前默认是 `ranking_optimizer_handoff / ranking-optimizer-contract.v1 / exact / true`。
后续如果进入 `v2` 或兼容模式，不需要重做整条评测链，只需要沿这层 metadata 扩展支持范围。

当前已经补上的一个非破坏性升级点是：ranking 主产物本身现在应该显式带顶层 `schemaVersion`，
而不是让下游继续通过 `predictionRun.schemaVersion` 做隐式回退。
这也是当前 `vNext preview` rehearsal gate 的第一条硬要求。

为了让模块 2 可以开始接真实回填和表现数据，当前 runtime 入口还额外约定了一层“输入适配层”：

- `topic-outcome-backfills.sample.v1` / `topic-outcome-backfills.v1`
- `topic-outcome-backfills-raw.sample.v1` / `topic-outcome-backfills-raw.v1`
- `post-performance-signals.sample.v1` / `post-performance-signals.v1`
- `post-performance-raw.sample.v1` / `post-performance-raw.v1`
- `challenger-adjustments.sample.v1` / `challenger-adjustments.v1`
- `challenger-observations.sample.v1` / `challenger-observations.v1`
- `challenger-observations-raw.sample.v1` / `challenger-observations-raw.v1`

也就是说，fixture schema 和后续真实运行 schema 可以共用同一条 daily-review 入口，只在 adapter 层做归一化，而不是把 mock runner 和真实 runner 分成两套实现。

其中 `topic-outcome-backfills-raw.*` 的定位是“更接近上游 outcome backfill job 输出的原始接入面”，它允许上游先交付：

- `observedWindow`
- `matchedAt`
- `matchStrategy`
- `coverageDays`
- `queryLiftScore`
- `futureTopicDensityScore`
- `contentGapPersistenceScore`
- `matchedFutureFingerprints`
- `evidenceSourceRefs`
- `matchConfidence`

然后再由 optimizer adapter 统一映射回 canonical `topic-outcome-backfills.*`。

`post-performance-raw.*` 的定位是“更接近上游 performance job 输出的原始接入面”，它允许上游先交付：

- `observedViews`
- `expectedViews`
- `normalizedViewLift`
- `retentionRatio`
- `shareSaveRate`
- `followConversionRate`

然后再由 optimizer adapter 统一映射回 canonical `post-performance-signals.*`。这样后面接真实 performance job 时，主 daily-review / offline-cycle 逻辑不需要直接理解上游原始字段。

`challenger-observations-raw.*` 的定位则是“更接近上游 challenger evaluation job 输出的原始接入面”。它允许上游先交付：

- `rankingQuality.top3HitRate`
- `rankingQuality.top10HitRate`
- `rankingQuality.ndcg10`
- `rankingQuality.duplicationRate`
- `rankingQuality.typeCoverageRate`
- `rankingQuality.noveltyScore`
- `rankingQuality.executableRate`
- `performanceAggregate.normalizedReward`
- `performanceAggregate.appliedWeight`
- `performanceAggregate.coverageRate`
- `observedDays`

然后再由 adapter 统一映射回 canonical `challenger-observations.*`，继续复用当前的 challenger review、shadow leaderboard 和 daily review 逻辑。

其中 `challenger-observations` 是当前更推荐的长期输入面。它不再只传“相对 champion 的 reward delta”，而是直接传：

- challenger 自己的 `topicMetrics`
- 聚合后的 `performanceSummary`
- `holdoutDelta`
- `daysObserved`

这样 daily review 可以直接基于观测值重算 challenger 的 `topicReward` / `combinedReward`，更贴近后续离线优化环的真实实现。

在这层之上，当前还补了一层更接近 cron/runtime 的统一输入面：

- `optimizer-input-bundle.sample.v1` / `optimizer-input-bundle.v1`

它把 ranking、context、backfills、performance、challengerInput 收成一份 bundle，后续调度任务只需要生产一个 payload，就可以直接喂给 daily review 或 offline cycle。

在 bundle 之上，当前又补了一层更轻量的调度编排面：

- `optimizer-input-manifest.sample.v1` / `optimizer-input-manifest.v1`

manifest 只保存 artifact path 和少量 provenance，适合 cron/job runner 先产出一个“待执行清单”；真正执行模块 2 时，再把 manifest materialize 成 canonical input bundle。

当前这层 manifest 已经扩成双栈：

- canonical lane: 继续使用 `artifactPaths`
- raw-shadow lane: 使用 `artifactBindings` + `inputSourceRegistryReference`

也就是说，scheduler 现在既可以直接交具体 artifact path，也可以先交一个 source binding manifest，再由 resolver 把 binding 映射到真实 job artifact。

在这层 manifest 之上，当前又补了一层 scheduler-facing 输入切流对象：

- `optimizer-input-rollout-policy.sample.v1` / `optimizer-input-rollout-policy.v1`

它的职责是冻结：

- `defaultRolloutIntent`
- `defaultRolloutClass`
- `rolloutSelectionPrecedence[*]`
- `rolloutClasses[*].rolloutClass`
- `rolloutClasses[*].sourceLane`
- `rolloutIntents[*].rolloutIntent`
- `rolloutIntents[*].rolloutClass`
- `schedulePolicies[*].scheduleId`
- `schedulePolicies[*].defaultRolloutIntent`
- `schedulePolicies[*].allowedRolloutIntents`
- `schedulePolicies[*].defaultRolloutClass`
- `schedulePolicies[*].allowedRolloutClasses`

当前 committed sample 里已经正式支持：

- `production -> sample_canonical`
- `raw_shadow_validation -> sample_raw_shadow`
- `real_shadow_validation -> real_provider_shadow`

也就是说，后面的 scheduler 不需要手工挑哪份 manifest，而是可以先声明 rollout class，再由输入层解析出真正的 source lane。

为了让上游 job 输出可以直接被模块 2 消费，而不是先手工改成裸 artifact，当前还额外约定了三类 job-run envelope：

- `topic-outcome-backfill-run.sample.v1` / `topic-outcome-backfill-run.v1`
- `post-performance-signal-run.sample.v1` / `post-performance-signal-run.v1`
- `challenger-evaluation-run.sample.v1` / `challenger-evaluation-run.v1`

这些 envelope 的定位不是替代内部 canonical schema，而是给 cron / batch job 一个更稳定的交付面：

- job 自己的 `jobRunId`
- `jobKind`
- `generatedAt`
- 轻量 `generatedFrom`
- 内部真正要给 optimizer 消费的 `payload`

模块 2 runtime adapter 现在支持两种入口：

- 直接吃裸 `backfills / performance / challenger` artifact
- 吃 job-run envelope，再在 adapter 层解包回 canonical payload

这样后面接真实日常作业时，不需要让每个上游 job 了解 optimizer 内部 bundle 细节，只需要产出自己负责的 envelope 即可。

在 envelope 之上，当前又补了一层更接近真实调度器的 source resolver：

- `optimizer-input-source-registry.sample.v1` / `optimizer-input-source-registry.v1`

这层的职责是冻结：

- `bindingId`
- `artifactKey`
- `sourceLane`
- `path`

当前 committed sample 里已经有两条 direct-binding lane：

- `sample_canonical`
- `sample_raw_shadow`

其中 `sample_raw_shadow` 不是新的业务语义，而是一条接入验证链。它会把 raw backfill / raw performance / raw challenger job-run 输入通过 source binding 接进 manifest，再在 runtime adapter 层归一化回 canonical optimizer inputs。这样后面接真实作业时，可以先保留 committed sample lane，再并行挂一条真实 lane 做 shadow comparison。

在 source registry 之外，当前又补了一层更接近真实上游接线的 source artifact catalog：

- `optimizer-source-artifact-catalog.sample.v1` / `optimizer-source-artifact-catalog.v1`

这层的职责是冻结：

- `artifactCatalogEntryId`
- `artifactKey`
- `providerLane`
- `providerKind`
- `upstreamJobKind`
- `path`

它不是直接表达新的业务语义，而是把“provider binding 最终会解析到哪个物理 artifact”单独抽成一层。这样 provider registry 不需要再直接持有 path，而是可以先引用一个更接近真实 artifact catalog / object-store locator 的 entry。

在 artifact catalog 之上，当前又补了一层更接近真实上游接线的 source provider registry：

- `optimizer-source-provider-registry.sample.v1` / `optimizer-source-provider-registry.v1`

这层的职责是冻结：

- `providerBindingId`
- `artifactKey`
- `providerLane`
- `providerKind`
- `upstreamJobKind`
- `resolutionMode`
- `artifactCatalogEntryId`

当前 committed sample 里的 provider lane 是：

- `real_provider_shadow`

它不是直接表达新的业务语义，而是表达“更接近真实上游 artifact binding / object locator”的 provider binding 层。当前 committed sample 里的 registry 默认通过 `resolutionMode=artifact_catalog_entry` 指向 `optimizer-source-artifact-catalog`，后面的 provider catalog 则可以继续保留 direct-path provider，也可以通过 `providerBindingId` 绑定到这一层 registry。

在 provider registry 之上，当前又补了一层更接近真实上游接线的 source provider catalog：

- `optimizer-source-provider-catalog.sample.v1` / `optimizer-source-provider-catalog.v1`

这层的职责是冻结：

- `sourceProviderId`
- `artifactKey`
- `providerLane`
- `providerKind`
- `upstreamJobKind`
- `resolutionMode`
- `providerBindingId`

当前 committed sample 里的 provider lane 是：

- `real_provider_shadow`

它不是直接表达新的业务语义，而是表达“更接近真实上游 job 接线”的 provider binding 层。后面的 resolver 不再直接枚举每个 real-shadow 路径，而是先通过 `sourceProviderId` 绑定到这一层 catalog；而当前 committed sample 里的 catalog 又会继续通过 `resolutionMode=provider_binding_registry` 绑定到 `optimizer-source-provider-registry`。

在这层之上，当前又补了一层更接近真实上游接线的 resolver artifact：

- `optimizer-job-artifact-resolver.sample.v1` / `optimizer-job-artifact-resolver.v1`

这层的职责是冻结：

- `resolverEntryId`
- `artifactKey`
- `resolverLane`
- `sourceProviderId`

当前 committed sample 里的 resolver lane 是：

- `real_provider_shadow`

它不是直接表达新的业务语义，而是表达“更接近真实上游 job 接线”的 artifact 解析层。source registry 现在可以继续保留 direct-path binding，也可以把 `real_provider_shadow` 这类 lane 通过 `resolutionMode=job_artifact_resolver` 和 `resolverEntryId` 交给 resolver 物化，再由 resolver 继续通过 `sourceProviderId` 解析到 provider catalog，并最终通过 `providerBindingId` 解析到 provider registry，再通过 `artifactCatalogEntryId` 解析到 source artifact catalog。

当前还额外有一条 hub gate 专门保证这层接入面不漂移：

- `skills/autotiktok/scripts/validate_optimizer_shadow_input_alignment.py`
- `skills/autotiktok/scripts/validate_optimizer_real_shadow_input_alignment.py`

它会同时验证：

- committed `optimizer-input-source-registry.sample.json` 和 `optimizer-input-manifest.raw-shadow.sample.json` 仍然能被确定性生成
- canonical manifest 和 raw-shadow manifest 仍然会物化成同一份 runtime optimizer inputs
- committed `optimizer-source-artifact-catalog.sample.json`、`optimizer-source-provider-registry.sample.json`、`optimizer-source-provider-catalog.sample.json`、`optimizer-job-artifact-resolver.sample.json`、`optimizer-input-source-registry.sample.json` 和 `optimizer-input-manifest.real-shadow.sample.json` 仍然能被确定性生成
- canonical manifest、raw-shadow manifest 和 real-shadow manifest 仍然会物化成同一份 runtime optimizer inputs

也就是说，在没有真实线上数据的阶段，模块 2 的“真实数据接入层”和“真实上游接线 stand-in”都已经有了可执行对象：raw ingress、job-run envelope、source registry、raw-shadow manifest、source provider catalog、job artifact resolver、real-shadow manifest 和 shadow alignment gate 这一整条链已经闭合。

在这条 scheduler-facing job 链之上，当前又补了一组 committed compare artifact：

- `optimizer-job-shadow-compare-plan.sample.v1` / `optimizer-job-shadow-compare-plan.v1`
- `optimizer-job-shadow-compare.sample.v1` / `optimizer-job-shadow-compare.v1`
- `optimizer-job-shadow-compare-plan.daily.sample.v1` / `optimizer-job-shadow-compare-plan.v1`
- `optimizer-job-shadow-compare-plan.weekly.sample.v1` / `optimizer-job-shadow-compare-plan.v1`
- `optimizer-job-shadow-compare.daily.sample.v1` / `optimizer-job-shadow-compare.v1`
- `optimizer-job-shadow-compare.weekly.sample.v1` / `optimizer-job-shadow-compare.v1`
- `optimizer-job-shadow-compare-batch-manifest.sample.v1` / `optimizer-job-shadow-compare-batch-manifest.v1`
- `optimizer-job-shadow-compare-batch.sample.v1` / `optimizer-job-shadow-compare-batch.v1`

其中 compare plan 的职责是先冻结 scheduler-facing compare scope：

- `daily production -> raw_shadow_validation`
- `weekly production -> real_shadow_validation`
- `daily production -> preview_validation`
- `daily production -> profile_compare_validation`

compare artifact 的职责则不是替代 `optimizer-job-run.v1`，而是按这份 compare plan 真正物化 scheduled shadow compare，并显式记录：

- `scheduleId`
- `baseline.schedulerRolloutIntent`
- `candidate.schedulerRolloutIntent`
- `baseline.rolloutClass`
- `candidate.rolloutClass`
- `baseline.runtimeProfileRolloutClass`
- `candidate.runtimeProfileRolloutClass`
- `baseline.windowSetPurpose`
- `candidate.windowSetPurpose`
- `baseline.comparisonDimension`
- `candidate.comparisonDimension`
- `baseline.inputProvenance.optimizerInputSourceLane`
- `candidate.inputProvenance.optimizerInputSourceLane`
- `baseline.inputProvenance.optimizerInputArtifactResolverId`
- `candidate.inputProvenance.optimizerInputArtifactResolverId`
- `baseline.inputProvenance.optimizerInputSourceProviderCatalogId`
- `candidate.inputProvenance.optimizerInputSourceProviderCatalogId`
- `baseline.inputProvenance.optimizerInputSourceProviderRegistryId`
- `candidate.inputProvenance.optimizerInputSourceProviderRegistryId`
- `semanticMatch`
- `semanticDiffKeys`

在 compare artifact 之上，当前还补了一层 batch compare：

- batch manifest 先冻结：
  - `compareArtifactPaths`
  - `comparisonDimension`
  - `batchWindowLabel`
- batch artifact 再聚合：
  - `comparedScheduleIds`
  - `comparedSchedulerRolloutIntents`
  - `comparedCandidateRolloutClasses`
  - `comparedCandidateSchedulerRolloutIntents`
  - `comparedCandidateRuntimeProfileRolloutClasses`
  - `comparedCandidateWindowSetPurposes`
  - `comparedCandidateComparisonDimensions`
  - `comparedCandidateSourceLanes`
  - `groupSummaries`

当前还有对应 hub gate：

- `skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_alignment.py`
- `skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_cutover_alignment.py`
- `skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_batch_alignment.py`

也就是说，当前不仅有 input-lane rollout 和 scheduled job dispatch，还有一组 scheduler-facing compare family 和 compare batch 来冻结 raw-shadow、real-shadow、preview-validation、profile-compare-validation 这几条 compare lane 的结果，而不是只靠临时 validator 输出。

在当前链路上，再往上一层的离线评测聚合对象建议固定成：

- `optimizer-eval-run.v1`

它的定位不是替代 `daily-review-report.v1` 或 `weekly-promotion-decision.v1`，而是把一次完整离线评测批次里最需要横向比较的字段抽出来：

- 哪次 ranking run
- 哪个 evaluation window
- 题材层 reward / 合成 reward
- post coverage
- 当前 shadow leader
- 是否产生 weekly promotion decision
- 本次评测吃到的 backfill / performance / challenger job-run provenance

而完整的 daily / weekly 明细仍然挂在 `artifacts.offlineCycle` 下面。这样后面做历史对比、dashboard 或多日批次扫描时，不需要每次都解析整个 daily-review artifact。

在 `optimizer-offline-cycle.v1` 和 `optimizer-eval-run.v1` 之上，当前又补了一层更接近真实 scheduler 的 job orchestration object：

- `optimizer-openclaw-cron-contract.sample.v1`
- `optimizer-job-schedule.sample.v1` / `optimizer-job-schedule.v1`
- `optimizer-job-artifact-retention-policy.sample.v1` / `optimizer-job-artifact-retention-policy.v1`
- `optimizer-run-summary.sample.v1` / `optimizer-run-summary.v1`
- `optimizer-job-execution-context.sample.v1` / `optimizer-job-execution-context.v1`
- `optimizer-job-orchestration-cycle.sample.v1` / `optimizer-job-orchestration-cycle.v1`
- `optimizer-job-error.sample.v1` / `optimizer-job-error.v1`
- `optimizer-recent-run-summaries.sample.v1` / `optimizer-recent-run-summaries.v1`
- `optimizer-recent-compare-summaries.sample.v1` / `optimizer-recent-compare-summaries.v1`
- `optimizer-recent-weekly-decisions.sample.v1` / `optimizer-recent-weekly-decisions.v1`
- `optimizer-recent-failure-summaries.sample.v1` / `optimizer-recent-failure-summaries.v1`
- `optimizer-job-run.v1`
- `optimizer-weekly-review-window.sample.v1` / `optimizer-weekly-review-window.v1`

其中：

- `optimizer-openclaw-cron-contract.*` 负责冻结标准 OpenClaw cron 的稳定 job name、exact-name match 管理策略，以及 `cron add` / `cron edit` 模板
- `optimizer-job-schedule.*` 负责冻结 scheduler 默认执行计划
- `optimizer-job-artifact-retention-policy.*` 负责冻结 scheduler-facing artifact 的 retention contract
- `optimizer-run-summary.*` 负责承载一次 orchestration cycle 的轻量运行摘要
- `optimizer-recent-*.sample.v1` 负责把 recent run / compare / weekly decision / failure 收成 dashboard-facing aggregate contract
- `optimizer-job-run.v1` 负责承载某一次真正跑出来的 day-level / week-level optimizer job 结果

当前推荐的 recurring runtime 已经不是 `optimizer-job-schedule -> run_scheduled_optimizer_job.py` 这条路径，而是：

- `optimizer-openclaw-cron-contract`
- `run_openclaw_cron_daily_optimizer.py`
- `run_openclaw_cron_weekly_optimizer.py`

而 `optimizer-job-schedule.*`、`optimizer-job-execution-context.*`、`optimizer-job-orchestration-cycle.*` 现在明确只保留为：

- fixture generation
- deterministic rehearsal
- cutover validation

它们当前会在 payload 顶层显式带：

- `runtimeRole=compatibility_rehearsal`
- `preferredRecurringRuntime=openclaw_cron`
- `intendedUses=[fixture_generation, deterministic_rehearsal, cutover_validation]`

当前 committed sample 的 `optimizer-job-schedule` 会冻结两类 entry：

- `daily_optimizer_job`
- `weekly_optimizer_job`

每条 entry 当前会显式带：

- `scheduleId`
- `cadenceKind`
- `jobKind`
- `defaultSchedulerRolloutIntent`
- `allowedSchedulerRolloutIntents`
- `defaultInputMode`
- `defaultInputPath`
- `defaultPolicyPath`
- `defaultOutputPath`
- `rankingContractVersion`
- `rankingContractValidationMode`
- `includeWeeklyPromotion`
- `defaultJobRunId`
- `defaultCycleId`
- `defaultEvalRunId`
- `defaultReportId`
- `defaultGeneratedAt`
- `defaultInputSourceRegistryPath`
- `defaultInputRolloutIntent`
- `defaultInputRolloutClass`
- `defaultRuntimeProfileRolloutClass`
- `defaultWindowSetPurpose`
- `defaultComparisonDimension`
- `defaultInputRolloutSelectionSource`
- `defaultInputRolloutIntentSelectionSource`
- `defaultInputRolloutClassSelectionSource`
- `defaultInputSourceLane`
- `allowedInputRolloutIntents`
- `allowedInputRolloutClasses`
- `allowedRuntimeProfileRolloutClasses`
- `allowedWindowSetPurposes`
- `allowedComparisonDimensions`

在 per-schedule 默认值之外，这层 schedule contract 现在还会显式冻结一层 scheduler intent catalog：

- `schedulerRolloutIntents[*].schedulerRolloutIntent`
- `schedulerRolloutIntents[*].inputRolloutIntent`
- `schedulerRolloutIntents[*].inputRolloutClass`
- `schedulerRolloutIntents[*].runtimeProfileRolloutClass`
- `schedulerRolloutIntents[*].windowSetPurpose`
- `schedulerRolloutIntents[*].comparisonDimension`

当前 committed sample 里已经有 5 条 scheduler intent：

- `production`
- `raw_shadow_validation`
- `real_provider_shadow_validation`
- `preview_validation`
- `profile_compare_validation`

也就是说，scheduler 现在不需要再靠 `--input-rollout-class` 或临时 fixture 命名约定去猜这次 job 的真正 rollout 意图，而是可以先声明一个稳定的 `schedulerRolloutIntent`，再由 runner 统一解析到 input rollout、runtime profile rollout 以及可选的 eval purpose / comparison metadata。

当前这层 schedule contract 又补了一条 external scheduler profile：

- `scheduleProfile = fixture_replay | external_scheduler`
- `defaultPathResolutionMode = repo_relative | scheduler_supplied`
- `defaultOutputEmissionMode = direct_output_path | output_root`
- `defaultOutputRoot`
- `defaultTriggerKind`
- `defaultSchedulerOwner`
- `defaultExecutionEnvironment`

也就是说，committed `optimizer-job-schedule.sample.json` 继续冻结 repo 内 deterministic replay，而新增的 `optimizer-job-schedule.external.sample.json` 会冻结“外部调度器必须自己提供 manifest / policy / weekly window，并把 job run 发到 output root”这条 contract。统一 dispatcher 仍然是同一个：

- `run_scheduled_optimizer_job.py`

也就是说，模块 2 的 phase 2 现在已经不只是“有两个 daily/weekly 脚本”，而是已经有一层明确的 scheduler-facing 计划对象，再由统一 dispatcher 去 materialize 成具体的 `optimizer-job-run.v1`。

在 schedule 之上，当前又补了一层 execution context：

- `optimizer-job-execution-context.*`

它的职责是冻结：

- scheduler run id / trigger / owner / execution environment
- artifact emission mode
- default input paths
- per-schedule production / shadow rollout class
- per-schedule production / shadow scheduler rollout intent

也就是说，调度器现在不需要直接拼长命令行，而是可以先产出一份 execution context，再由：

- `run_optimizer_job_orchestration_cycle.py`

统一物化：

- production job runs
- raw-shadow / real-shadow job runs
- shadow compare
- compare batch

而 orchestration cycle 现在还会继续挂一层 retention-facing provenance：

- `artifacts.retentionPolicy`
- `generatedFrom.optimizerJobArtifactRetentionPolicySchemaVersion`
- `generatedFrom.optimizerJobArtifactRetentionPolicyId`
- `summary.retentionPolicyId`
- `summary.retentionManagedArtifactCount`
- `summary.retentionManagedArtifactKinds`

也就是说，调度器现在不只是能看“这次 cycle 跑出了哪些 artifact”，还能看“这批 artifact 受哪份 retention policy 管”，这样后面做 run summary、artifact retention 或 dashboard aggregate 时，不需要再从外部约定倒推保留策略。

在 retention contract 之上，当前又补了一层独立的 run summary：

- `artifacts.runSummary`
- standalone `optimizer-run-summary.*`

它的定位不是替代完整的 orchestration cycle，而是把运行态最关心的字段抽出来，例如：

- `runStatus`
- `successfulScheduleCount` / `partialFailureScheduleCount` / `failedScheduleCount`
- `matchedComparisonCount` / `mismatchedComparisonCount`
- `weeklyDecisionCounts`
- `schedulerRolloutIntentCounts`
- per-schedule 的 `productionWeeklyDecision`、`productionDailyRecommendation`、`mismatchedCompareCount`

也就是说，后面做 recent runs、dashboard aggregate 或 failure triage 时，不需要先扫整份 cycle，再把 schedule-level outcome 和 compare outcome 二次归纳。

如果单个 scheduled job 失败，则会额外产出：

- `optimizer-job-error.v1`

这层 error contract 现在已经不只是一个 `errorCode + errorMessage`，而是显式带：

- `failureStage`
- `retryable`
- `ownerHint`
- `failureSummary`

当前 taxonomy 已经至少区分：

- `input_resolution_failure`
- `rollout_policy_failure`
- `job_materialization_failure`
- `artifact_emission_failure`
- `scheduler_dispatch_failure`

也就是说，外部 cron / planner 对接时，不需要依赖 stderr 字符串来判断失败类型，也不需要额外猜“这个错误应该重试还是先找输入 owner / rollout owner / ops”。

在 `optimizer-run-summary.*`、`optimizer-job-shadow-compare-batch.*` 和 `optimizer-job-error.*` 之上，当前又补了 4 份 dashboard-facing recent aggregate：

- `optimizer-recent-run-summaries.*`
- `optimizer-recent-compare-summaries.*`
- `optimizer-recent-weekly-decisions.*`
- `optimizer-recent-failure-summaries.*`

它们分别负责：

- recent run：聚合 `runStatus`、production/shadow job-run 数量、compare artifact 数量、scheduler rollout intent 计数
- recent compare：聚合 compare batch，并 flatten 成稳定的 `groupEntries`
- recent weekly decision：聚合 scheduler-facing weekly job-run decision，并继续透传 `weeklyStageMode`、`weeklyStagePolicyId`、rollback severity
- recent failure：把 standalone `optimizer-job-error` 和 orchestration-cycle `artifacts.errors` 收成统一的 failure summary 入口

也就是说，dashboard 或 ops 层不需要再直接扫完整的 orchestration cycle 或 compare-batch payload，而是可以直接消费更稳定、体积更小的 recent aggregate contract。

其中 `optimizer-weekly-review-window.*` 位于：

- `daily-review`
- `weekly-promotion`

之间，负责冻结 weekly decision 需要的多日窗口语义，包括：

- champion 的多日 reward 聚合
- challenger 的多日 summary
- rollback signal
- weekly scenario id

当前 committed sample 里的 `rollbackSignals` 现在已经不是一个单独的布尔值，而是显式带：

- `rollbackEligible`
- `rollbackTriggered`
- `rollbackSeverity`
- `rollbackReasonCodes`
- `rollbackCriticalHoldoutFloor`
- `rollbackCriticalCombinedRewardFloor`

当前这层 contract 又进一步显式化了 reward horizon 语义：

- 顶层 `rewardHorizonPolicy`
  - 当前 committed sample 会显式声明：
    - `t+1`
    - `t+3`
    - `t+7`
  - 并带：
    - `configuredWeight`
    - `required`
- 每个 `window`
  - 现在会显式带：
    - `daysSinceWindowStart`
    - `availableRewardHorizonIds`
- `championObservation`
  - 不再只是一个平面 summary
  - 现在也会带：
    - `rewardHorizonBreakdown[*]`
- `challengerObservations[*]`
  - 同样会带：
    - `rewardHorizonBreakdown[*]`
- `aggregatedChampion`
  - 现在会继续带：
    - `rewardHorizonSummaries[*]`
- `challengerSummaries[*]`
  - 现在也会继续带：
    - `rewardHorizonSummaries[*]`

这意味着 weekly promotion 已经不只是“跨 3 个 window 求平均”，而是开始显式区分：

- 哪些 window 已经有 `t+1`
- 哪些 window 已经有 `t+3`
- `t+7` 是否可用
- 最终周级 reward 是按怎样的 horizon 权重汇总出来的

当前 weekly promotion 已经不再只直接消费单日 `daily-review-report.v1`，而是优先消费：

- `optimizer-weekly-review-window.v1`

然后再在这层之上做：

- promotion gate
- keep-champion gate
- rollback-champion gate

当前 `weekly-promotion` 这一层也不再只是输出一个最终 decision。它现在还会显式带两类 gate review：

- `promotionCandidateReviews[*]`
  - 对每个 challenger 给出 weekly promotion gate 评估
  - 当前 committed sample 已经会显式评估：
    - `minimum_window_entries`
    - `minimum_days_observed`
    - `minimum_winning_days`
    - `minimum_hard_gate_pass_days`
    - `required_reward_horizon_coverage`
    - `minimum_holdout_floor`
    - `minimum_average_holdout_delta`
    - `minimum_average_reward_delta`
    - `dup_rate_budget`
    - `executable_rate_budget`
    - `type_coverage_budget`
    - `post_coverage_budget`
- `championSafetyReview`
  - 对当前 champion 给出 rollback / keep 相关的 safety gate 评估
  - 当前 committed sample 还会显式带：
    - `rollbackEligible`
    - `rollbackTriggered`
    - `rollbackSeverity`
    - `rollbackReasonCodes`
  - 当前 committed sample 已经会显式评估：
    - `window_level_rollback_signal`
    - `rollback_eligibility`
    - `holdout_floor_breach_days`
    - `combined_reward_floor_breach_days`

这意味着现在 weekly promotion artifact 已经能回答两类问题：

- 为什么某个 challenger 被 promote
- 为什么某个 challenger 没有被 promote

而且 champion-side 的 rollback 也已经不是“触发 / 未触发”两档，而是显式区分：

- `watch`
- `warning`
- `critical`

另外，weekly gate 现在也不再是假定所有账号阶段都共用一套阈值。当前 committed sample 和实现已经支持按：

- `growth`
- `scale`
- `search_priority`

选择不同的 weekly gate profile。对应地，`weekly-promotion.gateSummary` 现在会显式带：

- `weeklyStageMode`
- `weeklyStagePolicyId`
- `weeklyStagePolicySelectionSource`
- `minimumAverageRewardDelta`
- `minimumAverageHoldoutDelta`

对应地，当前 committed artifact 也已经扩成 stage-specific 的 weekly sample：

- `optimizer-weekly-review-window.sample.json`
- `optimizer-weekly-review-window.scale.sample.json`
- `optimizer-weekly-review-window.search-priority.sample.json`
- `weekly-promotion.sample.json`
- `weekly-promotion.scale.sample.json`
- `weekly-promotion.search-priority.sample.json`

而不是只返回一个最终 `decision` 和一行 reason 文本。

再往上一层，建议把多次 `optimizer-eval-run` 的横向比较固定成：

- `optimizer-eval-batch.v1`

这层的定位是“批量比较视图”，而不是新的底层事实表。它主要回答：

- 这批评测里一共有多少次 eval run
- 各种 mode 各有多少次
- weekly decision 分布如何
- 平均 topic reward / combined reward / post coverage 是多少
- 当前 batch 里最好的 eval run 是哪一个

而 batch 下面仍然保留完整的 `artifacts.evalRuns`，所以后面如果做多日批次、回测对比或 dashboard，不需要在 summary 层和明细层之间二选一。

为了让调度层先冻结“比较哪些 eval run”，而不是每次临时把路径塞给 batch builder，当前又补了一层更轻的编排对象：

- `optimizer-eval-batch-manifest.sample.v1` / `optimizer-eval-batch-manifest.v1`

它的职责不是承载评测结果，而是承载 batch 的比较意图：

- `evalRunPaths`
- `comparisonDimension`
- `batchWindowLabel`

这样后面做多日历史回放时，可以先由 cron/job 产出 manifest，再由 batch builder 去 materialize 真正的 `optimizer-eval-batch.v1`。  
当前 `optimizer-eval-batch.v1` 也已经开始显式带：

- `summary.comparisonDimension`
- `summary.comparisonGroupCount`
- `summary.batchWindowLabel`
- `groupSummaries[*]`

也就是说，batch 不再只是“把多个 eval run 放在一起求平均”，而是已经开始支持按 mode、profile、evaluation window、weekly decision 等维度做分组比较。

为了让“历史批次回放”不用先生成一堆新的完整 eval-run 文件，当前 manifest 又额外支持 entry 模式：

- `evalRunEntries[*].path`
- `evalRunEntries[*].runtimeSource`
- `evalRunEntries[*].historyBatchLabel`
- `evalRunEntries[*].historyWindowLabel`
- `evalRunEntries[*].scenarioLabel`
- `evalRunEntries[*].summaryOverrides`

这个 entry 模式的定位是 mock / replay orchestration，而不是新的线上事实格式。它的用途是：

- 先复用一个已有 eval-run 作为 base artifact
- 或者直接从 runtime source materialize 一个新的 eval-run
- 再通过少量 deterministic override 模拟历史批次的 reward、coverage、weekly decision 差异
- 最后把这些 entry materialize 成真正参与 batch 比较的 eval-run 对象

这样后面在真实 cron 接入前，模块 2 已经能验证“跨批次历史对比”的 summary 结构、group 逻辑和 provenance 透传，而不用先把所有历史窗口都建成独立 fixture。

其中 `runtimeSource` 当前明确支持 3 类 scheduler-facing 输入：

- `inputManifestPath`
- `inputBundlePath`
- `inputOfflineCyclePath`

也就是说，history replay 已经不再被锁死在“先有 base eval-run path”这一种 mock 形态上，而是可以直接复用更接近真实作业输出的 manifest / bundle / offline cycle。

为了再往真实 cron 形态靠一步，当前又在 history manifest 上游补了一层：

- `optimizer-eval-window-set.sample.v1` / `optimizer-eval-window-set.v1`

这层不再直接关心 eval-run path，而是先冻结“要回放哪些窗口/场景”：

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

同时 `generatedFrom` 现在也会保留 `windowSetBatchTypeSelectionSource`、`comparisonDimensionSelectionSource`、`runtimeProfilePlannerMetadataPolicyId`、`runtimeProfilePlannerMetadataContractFamilyId` 和 `runtimeProfilePlannerMetadataContractId`，用于区分这些 planner-level metadata 是显式输入、purpose family/template 默认，还是 fallback 默认，以及它们最终受哪条 planner metadata contract family / contract 约束。

同时在同一个 `optimizer-eval-window-set` 里，再单独冻结一份 `runtimeSources[*]` catalog：

- `runtimeSourceId`
- `sourceDescriptor`
- `inputManifestPath`
- `inputBundlePath`
- `inputOfflineCyclePath`
- `includeWeeklyPromotion`
- `rankingContractVersion`
- `rankingContractValidationMode`

当前建议把 `runtimeSources[*]` 设计成“双栈”：

- committed sample / planner-first lane 优先使用 `sourceDescriptor`
- 本地联调 / 临时回放仍可直接写 path

在 `runtimeSources[*]` 之外，当前又补了一层独立 registry：

- `optimizer-runtime-artifact-registry.sample.v1` / `optimizer-runtime-artifact-registry.v1`

它负责把 planner descriptor 隐含的 binding id 显式映射成：

- `artifactField`
- `artifactPath`
- `runtimeSourceKind`
- `jobFamilyGroup`
- `materializationProfile`
- `sourceClass`
- `sourceVariant`

这样一来，window set 本身更像调度计划，而不是直接把文件系统路径硬编码进 planner object。当前 sample descriptor 的形态是：

- `descriptorKind = "planner_runtime_binding"`
- `profileId = ...`

同时保留一条兼容 lane：

- `descriptorKind = "sample_artifact_binding"`
- `artifactBinding = ...`

后续如果接真实 cron planner，可以继续把这层 descriptor 扩成 job-run descriptor、window-materialization descriptor 或 dataset binding，而不必回头改 window entry 本身。

而 registry 这一层则可以继续朝“调度环境的真实 artifact catalog”演进，不需要再把环境差异塞回 window set 本身。

在 window set 和 registry 之间，当前又补了一层更轻的默认 profile family：

- `optimizer-runtime-profile-family-registry.sample.v1`
- `optimizer-runtime-profile-rollout-policy.sample.v1`
- `optimizer-runtime-profile-catalog.sample.v1` / `optimizer-runtime-profile-catalog.v1`
- `optimizer-runtime-profile-catalog-preview.sample.v1`

rollout policy 先冻结“scheduler 默认走哪个 family lane，preview lane 是否打开”。当前它已经分成六层：

- `plannerMetadataContractFamilies`：冻结一组可复用的 `windowSetBatchType` / `comparisonDimension` 约束族
- `plannerMetadataContracts`：冻结具体允许的 `windowSetBatchType` / `comparisonDimension` 组合，并归属于某个 contract family
- `plannerMetadataPolicies`：冻结 planner metadata 默认值和优先级，并引用上面的 contract
- `evalPurposeTemplateFamilies`：冻结一组可复用 scheduler 默认值，比如 `runtimeProfileFamilyId` / `rolloutClass` / `plannerMetadataPolicyId`
- `evalPurposeTemplates`：把一个 template 绑定到某个 template family，并可按需要继续局部 override
- `evalPurposePolicies`：按 `windowSetPurpose` 绑定到某个 template
- `rolloutClassRules`：在 purpose default 之外，再根据 `batchWindowLabelPrefix`、`windowSetBatchType`、`comparisonDimension`、`historyWindowLabelPrefix`、`mode` 等条件做更细粒度 override

这样可以同时表达：

- “这类 eval 目的默认就走 preview canary”
- “这类目的里，只有某种历史 weekly replay 或某种 batch/dimension 组合才走 preview canary”

family registry 再冻结“这个 planner family 在 current / preview lane 下应该指向哪个 catalog”。catalog 再去定义具体 profile。catalog 里的每个 profile 当前会记录：

- `catalogFamily`
- `catalogVersion`
- `profileId`
- `aliasProfileIds`（当 preview catalog 还要兼容旧 planner profile 请求时）
- `bindingId`
- `runtimeSourceKind`
- `includeWeeklyPromotion`
- `jobFamilyGroup`
- `materializationProfile`
- `rankingContractVersion`
- `rankingContractValidationMode`

在 registry 旁边，当前还补了一层更偏 planner 语义的：

- `optimizer-runtime-materialization-plan.sample.v1` / `optimizer-runtime-materialization-plan.v1`

这层不再描述 artifact path，而是描述“这个 runtime binding 是怎么被物化出来的”：

- `planId`
- `outputBindingId`
- `jobFamilyGroup`
- `materializationProfile`
- `materializationStrategy`
- `upstreamJobFamilies`
- `requiredArtifactKinds`
- `includeWeeklyPromotion`

也就是说，现在 planner 相关对象已经拆成 5 层：

- `optimizer-eval-window-set` 负责声明窗口和 runtime binding intent
- `optimizer-runtime-profile-rollout-policy` 负责声明 scheduler 默认 lane 和 preview cutover 规则
- `optimizer-runtime-profile-family-registry` 负责把 family/lane 映射到具体 catalog
- `optimizer-runtime-profile-catalog` 负责声明默认 runtime profile family
- `optimizer-runtime-artifact-registry` 负责把 binding 映射到当前环境里的具体 artifact path
- `optimizer-runtime-materialization-plan` 负责描述这个 binding 背后的 job family 和物化策略

这样后面真的接 cron/job planner 时，可以同时保留：

- planner 想跑什么
- 当前环境里具体去哪取
- 这类输入理论上应该怎么被上游作业物化出来

然后再由 history manifest builder 把这些 window entry materialize 成 `evalRunEntries[*]`。  
这样后面真实 cron 接入时，更接近的链路会是：

- scheduler/job 先产出 window-set
- history manifest 从 window-set 派生
- eval batch 再从 history manifest 派生

也就是说，history replay 的输入层已经从“直接手写 eval-run entry 列表”推进成了“先声明窗口计划，再派生 batch 输入”。

当前 committed sample 的 `optimizer-eval-window-set` 也已经故意做成 mixed-source：

- recent daily lane 通过 `runtimeSourceId` 指向一个 `sourceDescriptor -> inputManifestPath` binding
- recent weekly lane 通过 `runtimeSourceId` 指向一个 `sourceDescriptor -> inputBundlePath` binding
- 两个 historical replay lane 通过 `runtimeSourceId` 指向 `sourceDescriptor -> inputOfflineCyclePath` binding

对应地，`optimizer-eval-batch.v1` 和 `optimizer-eval-batch-history.v1` 的 summary / group summary 现在都会显式带：

- `runtimeSourceKinds`
- `runtimeSourceIds`
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

这样后面做多窗口历史复盘时，可以直接看到：

- 这批比较到底混入了哪些 runtime source family
- 具体用了哪几个 planner-level source binding

同时现在还多了一条 runtime profile catalog 的 cutover rehearsal：

- current lane 保持当前 canonical `runtimeProfileIds`
- preview lane 可以用 preview catalog 的 canonical ids 替代它们
- 但旧 planner request 仍然会保留在 `runtimeProfileRequestedIds`

这样后面做 runtime profile catalog 升级时，可以先验证 planner 语义是否稳定，而不是直接硬切换。

而 `optimizer-eval-window-set` 本身现在会同时带：

- `runtimeProfileFamilyRegistryReference`
- `runtimeProfileCatalogReference`

也就是 planner 选择 catalog 的入口和最终落到的 catalog contract 都会被记录下来。

- 这些 binding 背后分别对应什么 materialization strategy 和上游 job family

下面的字段命名采用 TypeScript 内部表示的 `camelCase`。如果后续需要持久化成 JSON，对外再做序列化映射。

## 1. 设计原则

- 模块 2 的评分对象是 `topicCandidate`，不是单条热视频
- `feature builder` 输出 8 维特征向量，`score engine` 再做加权
- `topicCandidate` 必须自带 `searchEvidence` 和 `executionProfile`
- `predictionRun` 必须记录 schema、权重和代码版本

## 2. Zod / TypeScript 草案

```ts
import { z } from "zod";

export const TopicTypeEnum = z.enum(["trend", "search", "evergreen"]);

export const CandidateModeEnum = z.enum(["growth", "search", "series"]);

export const FreshnessWindowEnum = z.enum(["daily", "weekly", "evergreen"]);

export const SearchIntentTypeEnum = z.enum([
  "how_to",
  "mistake",
  "comparison",
  "case",
  "trend_reaction",
]);

export const SearchPersistenceHintEnum = z.enum(["daily", "weekly", "evergreen"]);

export const DependencyRiskEnum = z.enum(["low", "medium", "high"]);

export const SourceTypeEnum = z.enum([
  "creative_center_trend",
  "creative_center_detail",
  "creative_center_top_video",
  "search_insights_query",
  "search_insights_related_query",
  "search_insights_content_gap",
  "public_video_sample",
  "evergreen_library",
  "user_input",
]);

export const SearchEvidenceSchema = z.object({
  seedQueries: z.array(z.string()).default([]),
  relatedQueries: z.array(z.string()).default([]),
  contentGapQueries: z.array(z.string()).default([]),
  searchIntentType: SearchIntentTypeEnum,
  searchPersistenceHint: SearchPersistenceHintEnum,
});

export const ExecutionProfileSchema = z.object({
  recommendedFormats: z.array(z.string()).default([]),
  requiredAssets: z.array(z.string()).default([]),
  requiredCapabilities: z.array(z.string()).default([]),
  productionComplexity: z.number().min(0).max(1),
  dependencyRisk: DependencyRiskEnum,
  fastTurnaround: z.boolean(),
});

export const TopicCandidateSchema = z.object({
  schemaVersion: z.literal("topic-candidate.v1"),
  topicId: z.string().min(1),
  topicFingerprint: z.string().min(1),
  topicTitle: z.string().min(1),
  topicSummary: z.string().min(1),
  topicType: TopicTypeEnum,
  sourceType: z.array(SourceTypeEnum).min(1),
  sourceRef: z.array(z.string().min(1)).min(1),
  keywords: z.array(z.string()).default([]),
  contentAngle: z.array(z.string()).default([]),
  recommendedMode: CandidateModeEnum,
  expandability: z.number().min(0).max(1),
  freshnessWindow: FreshnessWindowEnum,
  searchEvidence: SearchEvidenceSchema,
  executionProfile: ExecutionProfileSchema,
  executionNotes: z.string().default(""),
});

export type TopicCandidate = z.infer<typeof TopicCandidateSchema>;

export const StageModeEnum = z.enum(["growth", "scale", "search_priority"]);

export const ProductionBudgetLevelEnum = z.enum(["low", "medium", "high"]);

export const TurnaroundSpeedEnum = z.enum(["same_day", "next_day", "multi_day"]);

export const ScoringContextSchema = z.object({
  schemaVersion: z.literal("scoring-context.v1"),
  accountId: z.string().min(1),
  market: z.string().min(1),
  language: z.string().min(1),
  niche: z.string().min(1),
  stageMode: StageModeEnum,
  acceptedFormats: z.array(z.string()).default([]),
  availableAssetTypes: z.array(z.string()).default([]),
  productionBudgetLevel: ProductionBudgetLevelEnum,
  turnaroundSpeed: TurnaroundSpeedEnum,
  canDoTalkingHead: z.boolean().default(false),
  canDoScreenRecording: z.boolean().default(false),
  canDoAiGen: z.boolean().default(false),
  activeContentBuckets: z.array(z.string()).default([]),
  historicalPerformanceSummary: z
    .object({
      topPerformingTopicFingerprints: z.array(z.string()).default([]),
      topPerformingFormats: z.array(z.string()).default([]),
      weakTopicFingerprints: z.array(z.string()).default([]),
    })
    .default({
      topPerformingTopicFingerprints: [],
      topPerformingFormats: [],
      weakTopicFingerprints: [],
    }),
});

export type ScoringContext = z.infer<typeof ScoringContextSchema>;

export const FeatureScoreSchema = z.object({
  score: z.number().min(1).max(5),
  confidence: z.number().min(0).max(1).default(1),
  evidenceRefs: z.array(z.string()).default([]),
  reason: z.string().min(1),
});

export const FeatureVectorSchema = z.object({
  schemaVersion: z.literal("feature-vector.v1"),
  demand: FeatureScoreSchema,
  competition: FeatureScoreSchema,
  fit: FeatureScoreSchema,
  rewrite: FeatureScoreSchema,
  series: FeatureScoreSchema,
  searchCapture: FeatureScoreSchema,
  longform: FeatureScoreSchema,
  feasibility: FeatureScoreSchema,
});

export type FeatureVector = z.infer<typeof FeatureVectorSchema>;

export const ScoringProfileIdEnum = z.enum([
  "growth-default",
  "scale-default",
  "search-priority-default",
]);

export const ScoringWeightsSchema = z
  .object({
    demand: z.number().min(0).max(1),
    fit: z.number().min(0).max(1),
    rewrite: z.number().min(0).max(1),
    series: z.number().min(0).max(1),
    searchCapture: z.number().min(0).max(1),
    longform: z.number().min(0).max(1),
    feasibility: z.number().min(0).max(1),
    competition: z.number().min(0).max(1),
  })
  .refine(
    (weights) =>
      Math.abs(
        weights.demand +
          weights.fit +
          weights.rewrite +
          weights.series +
          weights.searchCapture +
          weights.longform +
          weights.feasibility +
          weights.competition -
          1,
      ) < 1e-6,
    "Scoring weights must sum to 1",
  );

export const ScoringProfileSchema = z.object({
  schemaVersion: z.literal("scoring-profile.v1"),
  profileId: ScoringProfileIdEnum,
  weights: ScoringWeightsSchema,
  p0Threshold: z.number().min(0).max(5),
  p1Threshold: z.number().min(0).max(5),
  rejectBelow: z.number().min(0).max(5).default(0),
});

export type ScoringProfile = z.infer<typeof ScoringProfileSchema>;

export const PriorityLevelEnum = z.enum(["P0", "P1", "P2"]);

export const RecommendedUseEnum = z.enum([
  "growth",
  "search_capture",
  "series_seed",
  "longform_expand",
]);

export const NextActionEnum = z.enum(["generate_script", "hold_as_backup", "not_recommended"]);

export const ScoreBreakdownSchema = z.object({
  demand: z.number().min(1).max(5),
  competition: z.number().min(1).max(5),
  fit: z.number().min(1).max(5),
  rewrite: z.number().min(1).max(5),
  series: z.number().min(1).max(5),
  searchCapture: z.number().min(1).max(5),
  longform: z.number().min(1).max(5),
  feasibility: z.number().min(1).max(5),
});

export const TopicScoreSchema = z.object({
  schemaVersion: z.literal("topic-score.v1"),
  topicId: z.string().min(1),
  topicFingerprint: z.string().min(1),
  profileId: ScoringProfileIdEnum,
  scoreTotal: z.number().min(0).max(5),
  scoreBreakdown: ScoreBreakdownSchema,
  priorityLevel: PriorityLevelEnum,
  recommendedUse: RecommendedUseEnum,
  scoreReason: z.string().min(1),
  riskFlags: z.array(z.string()).default([]),
  nextAction: NextActionEnum,
  featureVector: FeatureVectorSchema,
});

export type TopicScore = z.infer<typeof TopicScoreSchema>;

export const PredictionRunSchema = z.object({
  schemaVersion: z.literal("prediction-run.v1"),
  runId: z.string().min(1),
  snapshotId: z.string().min(1),
  accountId: z.string().min(1),
  profileId: ScoringProfileIdEnum,
  topicCandidateSchemaVersion: z.literal("topic-candidate.v1"),
  scoringContextSchemaVersion: z.literal("scoring-context.v1"),
  scoringCodeVersion: z.string().min(1),
  createdAt: z.string().datetime(),
  candidateCount: z.number().int().nonnegative(),
  rankedTopicIds: z.array(z.string().min(1)),
});

export type PredictionRun = z.infer<typeof PredictionRunSchema>;

export const BackfillWindowEnum = z.enum(["t_plus_1", "t_plus_3", "t_plus_7"]);

export const TopicOutcomeBackfillSchema = z.object({
  schemaVersion: z.literal("topic-outcome-backfill.v1"),
  backfillId: z.string().min(1),
  runId: z.string().min(1),
  topicId: z.string().min(1),
  topicFingerprint: z.string().min(1),
  backfillWindow: BackfillWindowEnum,
  evaluatedAt: z.string().datetime(),
  searchLift: z.number().min(0).max(1),
  futureVideoDensity: z.number().min(0).max(1),
  contentGapPersistence: z.number().min(0).max(1),
  matchedFutureTopicFingerprints: z.array(z.string()).default([]),
  evidenceRefs: z.array(z.string()).default([]),
  outcomeConfidence: z.number().min(0).max(1).default(1),
});

export type TopicOutcomeBackfill = z.infer<typeof TopicOutcomeBackfillSchema>;

export const PerformanceSignalWindowEnum = z.enum([
  "publish_plus_1d",
  "publish_plus_3d",
  "publish_plus_7d",
]);

export const PostPerformanceSignalSchema = z.object({
  schemaVersion: z.literal("post-performance-signal.v1"),
  signalId: z.string().min(1),
  runId: z.string().min(1),
  topicId: z.string().min(1),
  topicFingerprint: z.string().min(1),
  postId: z.string().min(1),
  accountId: z.string().min(1),
  contentBucketId: z.string().min(1).optional(),
  format: z.string().min(1),
  measuredWindow: PerformanceSignalWindowEnum,
  measuredAt: z.string().datetime(),
  rawViews: z.number().nonnegative(),
  viewLift: z.number().min(0).max(1),
  retentionProxy: z.number().min(0).max(1).nullable().default(null),
  shareSaveProxy: z.number().min(0).max(1).nullable().default(null),
  followConversionProxy: z.number().min(0).max(1).nullable().default(null),
});

export type PostPerformanceSignal = z.infer<typeof PostPerformanceSignalSchema>;

export const TopicRewardBreakdownSchema = z.object({
  schemaVersion: z.literal("topic-reward-breakdown.v1"),
  rewardId: z.string().min(1),
  runId: z.string().min(1),
  evaluationWindow: BackfillWindowEnum,
  hitAt3: z.number().min(0).max(1),
  hitAt10: z.number().min(0).max(1),
  ndcgAt10: z.number().min(0).max(1),
  dupRate: z.number().min(0).max(1),
  typeCoverage: z.number().min(0).max(1),
  novelty: z.number().min(0).max(1),
  executableRate: z.number().min(0).max(1),
  topicReward: z.number().min(-1).max(1),
});

export type TopicRewardBreakdown = z.infer<typeof TopicRewardBreakdownSchema>;

export const CombinedRewardBreakdownSchema = z.object({
  schemaVersion: z.literal("combined-reward-breakdown.v1"),
  rewardId: z.string().min(1),
  runId: z.string().min(1),
  evaluationWindow: BackfillWindowEnum,
  topicReward: z.number().min(-1).max(1),
  performanceReward: z.number().min(0).max(1).nullable().default(null),
  performanceWeight: z.number().min(0).max(1),
  postCoverageRate: z.number().min(0).max(1),
  combinedReward: z.number().min(-1).max(1),
});

export type CombinedRewardBreakdown = z.infer<typeof CombinedRewardBreakdownSchema>;
```

## 3. 为什么这样拆

### `TopicCandidateSchema`

这是模块 2 的直接输入。当前最关键的不是多加字段，而是先冻结：

- `topicFingerprint` 的稳定语义
- `sourceType` / `sourceRef` 的格式
- `expandability` 和 `productionComplexity` 的量纲
- `searchEvidence` 和 `executionProfile` 的必填性

### `ScoringContextSchema`

模块 2 不是无上下文打分。至少要知道：

- 当前账号处于什么阶段
- 能接受哪些内容形式
- 有哪些素材和生产能力
- 历史上什么题材和形式表现更好

### `FeatureVectorSchema`

这层是 `feature builder` 的直接产物。建议每个维度都保留：

- `score`
- `confidence`
- `evidenceRefs`
- `reason`

这样后面生成 `scoreReason` 和 `riskFlags` 才不会失去可解释性。

### `TopicScoreSchema`

这是模块 2 的主输出。建议：

- `scoreTotal` 统一按 `0~5` 存储
- `scoreBreakdown` 保持与产品文档一致
- `riskFlags` 在 v1 先允许字符串数组，v2 再收紧为枚举

### `PredictionRunSchema`

如果没有这层，后面做回放、评测、权重对比会非常痛苦。至少要能回答：

- 这次跑的是哪份快照
- 用的是哪套 profile
- 当时模块 2 的代码版本是什么
- 最终排出来的顺序是什么

### `TopicOutcomeBackfillSchema`

这是题材层后验的主记录。它回答的是：

- 某次 run 中的某个题材
- 到 `t+1 / t+3 / t+7`
- 是否被后续平台信号验证

它主要服务 `TopicReward`。

### `PostPerformanceSignalSchema`

这是发布表现层的主记录。它回答的是：

- 某个题材是否真的被发成视频
- 发出来之后，播放和其他代理指标表现如何

它主要服务 `PerformanceReward`。

### `TopicRewardBreakdownSchema`

这是题材层 reward 的分项成绩单。它用于解释：

- 为什么这次 run 的题材层 reward 高或低
- 问题主要出在命中率、重复率、多样性，还是可执行性

### `CombinedRewardBreakdownSchema`

这是最终 reward 的归因账单。它用于解释：

- 题材层贡献了多少
- 发布层贡献了多少
- `PerformanceWeight` 实际是多少
- 最终 `CombinedReward` 是如何合成的

## 4. 这些对象之间的关系

建议的数据流如下：

1. `PredictionRun`
   - 记录某次排序运行产生了哪些候选和最终榜单
2. `TopicOutcomeBackfill`
   - 回填这些题材后续是否被平台信号验证
3. `PostPerformanceSignal`
   - 回填真实发布表现，尤其是归一化后的 `ViewLift`
4. `TopicRewardBreakdown`
   - 先算题材层 reward
5. `CombinedRewardBreakdown`
   - 再把题材层和发布层合成为总 reward

## 5. 模块 2 开工前的最小冻结清单

建议先冻结这些字段，不要边写边改：

- `TopicCandidateSchema`
- `ScoringContextSchema`
- `ScoringProfileSchema`
- `TopicScoreSchema`
- `PredictionRunSchema`
- `TopicOutcomeBackfillSchema`
- `PostPerformanceSignalSchema`
- `TopicRewardBreakdownSchema`
- `CombinedRewardBreakdownSchema`

冻结完成后就可以先用 mock fixture 开工：

1. `skills/autotiktok/fixtures/topic-candidates.fixture.json`
2. `skills/autotiktok/fixtures/scoring-context.fixture.json`
3. `skills/autotiktok/fixtures/scoring-profiles.fixture.json`

这三份 fixture 的定位略有不同：

- `topic-candidates.fixture.json` 是候选集合，方便直接做排序对比
- `scoring-context.fixture.json` 是单个上下文对象，方便直接喂给 `feature builder`
- `scoring-profiles.fixture.json` 是 profile 集合，方便切换账号阶段做对比测试

## 6. 下一步建议

如果模块 2 要先落代码，建议顺序如下：

1. 先实现 `ScoringProfileSchema`
2. 再实现 `TopicCandidateSchema` 和 `ScoringContextSchema`
3. 然后写 `feature builder`
4. 再写 `score engine`
5. 再接 `prediction run`
6. 最后接 `topic outcome backfill`、`post performance signal` 和 reward 计算

当前不建议一开始就把 `riskFlags`、`recommendedFormats`、`requiredCapabilities` 细化得过满。先把主干 contract 冻住，再在实现里补枚举和规则。
