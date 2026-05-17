# AutoTikTok 最新开发计划

## 1. 当前阶段判断

AutoTikTok 现在已经完成了“模块 2 可开发、可回放、可比较、可验证、可调度、可观测”的工程化阶段。

接下来的工作集中到外部集成线：

- 把模块 1 接到真实 collector / snapshot artifact
- 先用 `autotiktok-trending` metadata 跑通 `sourceSnapshots + videoSamples + synthetic signalItems -> discovery -> ranking`
- 当前正在用 `autotiktok-video-download` 下载的 MP4 和多模态模型增强 `signalItems`

当前已经成型的基础能力主要集中在模块 2 和调度/运维层：

- 3 个 skill 的结构已经拆开并稳定：
  - `skills/autotiktok-topic-discovery`
  - `skills/autotiktok-topic-ranking`
  - `skills/autotiktok-strategy-optimizer`
- 模块 1 到模块 2 的 handoff contract、preview lane、provenance、cutover rehearsal 已落地。
- 模块 2 已经有完整的离线优化 artifact 链：
  - `daily-review`
  - `weekly-promotion`
  - `optimizer-offline-cycle`
  - `optimizer-eval-run`
  - `optimizer-eval-batch`
  - `optimizer-eval-window-set`
  - `optimizer-eval-batch-history-manifest`
  - `optimizer-eval-batch-history`
- planner / scheduler 侧已经推进到 policy 驱动，而不是只靠脚本参数硬编码。
- 模块 1 当前已经有 discovery-owned contract 和 deterministic dry-run scaffold，但还没有接入真实采集器和真实快照存储。

一句话总结：前六个阶段已经把模块 2、scheduler orchestration、weekly realism、rollout/cutover、ops aggregate、模块 1 的 repo 内实现、以及 OpenClaw 标准 cron runtime 都做完；接下来进入真实上游输入接线。

## 2. 已完成部分

### 2.1 Skill 与模块骨架

- AutoTikTok 已按功能拆成 3 个独立 skill。
- 每个 skill 都已经有自己的 `SKILL.md`、fixtures、scripts、references。
- `skills/autotiktok` 作为共享 docs、总校验和 workflow hub 使用。

### 2.2 模块 1 Scaffold 与 Handoff

- `skills/autotiktok-topic-discovery` 已经不是空壳，当前已具备：
  - `raw-signals.sample.json`
  - `discovery-policy.v1.json`
  - `discovery_dry_run.py`
  - `discovery-dry-run.sample.json`
- 当前 discovery scaffold 已经可以稳定完成：
  - `signal -> evidenceBundle -> mergeGroup -> topicCandidate`
  - `topicFingerprint`
  - `searchEvidence`
  - `executionProfile`
- discovery -> ranking 这条 handoff 已经打通：
  - ranking 可以直接消费 discovery 输出
  - `skills/autotiktok/fixtures/topic-candidates.fixture.json` 现在被视为 discovery 的派生产物，而不是手写真值
- ranking -> optimizer 这条 handoff 也已稳定：
  - current lane
  - preview lane
  - contract rehearsal
  - provenance chain
  - `optimizerHandoff` / compat / preview-first 演练

### 2.3 模块 2 Runtime 分层

- `daily_review_mock.py` 已拆成清晰的三层：
  - runner
  - adapter
  - service
- 模块 2 已不再依赖单个大脚本。
- 当前核心入口和实现已经稳定在：
  - `skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py`
  - `skills/autotiktok-strategy-optimizer/scripts/optimizer_input_adapters.py`
  - `skills/autotiktok-strategy-optimizer/scripts/daily_review_service.py`
  - `skills/autotiktok-strategy-optimizer/scripts/optimizer_lib.py`

### 2.4 输入层标准化

- 已完成 scheduler-facing 输入对象：
  - `topic-outcome-backfill-run`
  - `post-performance-signal-run`
  - `challenger-evaluation-run`
  - `optimizer-input-manifest`
  - `optimizer-input-bundle`
- 这些输入已经可以喂给：
  - `daily review`
  - `offline cycle`
  - `eval run`
  - `history replay`

### 2.5 离线优化与历史回放

- 已完成离线优化 artifact 体系：
  - `optimizer-offline-cycle`
  - `optimizer-eval-run`
  - `optimizer-eval-batch`
  - `optimizer-eval-window-set`
  - `optimizer-eval-batch-history-manifest`
  - `optimizer-eval-batch-history`
- 已支持：
  - 多窗口 replay
  - 多批次 grouped batch
  - mixed-source runtime materialization
  - history replay provenance

### 2.6 Planner / Scheduler Policy

- 已完成：
  - runtime profile catalog
  - runtime profile family registry
  - runtime profile rollout policy
  - planner metadata contract families
  - eval purpose template families
  - eval purpose templates
  - eval purpose policies
  - rollout class rules
  - planner metadata policies
  - planner metadata contracts
- 当前 `optimizer-eval-window-set` 已能记录：
  - `windowSetBatchTypeSelectionSource`
  - `comparisonDimensionSelectionSource`
  - `runtimeProfilePlannerMetadataPolicyId`
  - `runtimeProfilePlannerMetadataContractFamilyId`
  - `runtimeProfilePlannerMetadataContractId`

### 2.7 最新新增能力

最新几轮完成了五块事：先把 planner metadata 这层从“单个 contract”推进成“contract family + concrete contract”，然后把真实数据接入层从 raw ingress 一路补到了 source binding 和 raw-shadow manifest，接着把“真实上游接线”这一阶段从第一版 resolver abstraction 继续推进成了 `source artifact catalog -> provider registry -> provider catalog -> resolver` stand-in，随后把 sample lane / shadow lane 的对照收口成了 scheduler-facing compare family 和 compare batch，最后又把这条 provenance 继续透传到了 job schedule、job run、compare 和 compare batch。

- `optimizer-runtime-profile-rollout-policy` 现在已经有：
  - `plannerMetadataContractFamilies`
  - `plannerMetadataContracts`
  - `plannerMetadataPolicies`
- `build_optimizer_eval_window_set.py` 现在不仅会选默认 batch metadata，还会验证它是否满足所选 contract family / contract。
- 新增专门校验：
  - `skills/autotiktok/scripts/validate_runtime_profile_planner_metadata_contract_enforcement.py`
- 新增 smoke：
  - `skills/autotiktok/scripts/test_runtime_profile_planner_metadata_contract_enforcement.py`
- `window-set -> history manifest -> eval batch` 这条链已经继续透传：
  - `runtimeProfilePlannerMetadataContractFamilyId`
  - `runtimeProfilePlannerMetadataContractId`
- `optimizer_input_adapters.py` 现在已经支持：
  - `topic-outcome-backfills-raw.sample.v1`
  - `topic-outcome-backfills-raw.v1`
  - `post-performance-raw.sample.v1`
  - `post-performance-raw.v1`
  - `challenger-observations-raw.sample.v1`
  - `challenger-observations-raw.v1`
- raw backfill 输入现在会先以原始字段进入 adapter：
  - `observedWindow`
  - `matchStrategy`
  - `coverageDays`
  - `queryLiftScore`
  - `futureTopicDensityScore`
  - `contentGapPersistenceScore`
  - `matchConfidence`
- raw performance 输入现在会先以原始字段进入 adapter：
  - `observedViews`
  - `expectedViews`
  - `normalizedViewLift`
  - `retentionRatio`
  - `shareSaveRate`
  - `followConversionRate`
- raw challenger observation 输入现在会先以原始字段进入 adapter：
  - `rankingQuality.*`
  - `performanceAggregate.*`
  - `observedDays`
- 然后统一归一化回 canonical：
  - `topic-outcome-backfills.*`
  - `post-performance-signals.*`
  - `challenger-observations.*`
- 在 raw adapter 之上，当前又补了 scheduler-facing source binding：
  - `optimizer-input-source-registry.sample.v1`
  - `optimizer-input-source-registry.v1`
- 当前 committed sample 已有两条 source lane：
  - `sample_canonical`
  - `sample_raw_shadow`
- source registry 现在又新增了第三条 lane：
  - `real_provider_shadow`
- `optimizer-input-manifest` 也已经扩成双栈：
  - canonical lane: `artifactPaths`
  - raw-shadow lane: `artifactBindings + inputSourceRegistryReference`
- 现在又新增了一层 source artifact catalog：
  - `optimizer-source-artifact-catalog.sample.v1`
  - `optimizer-source-artifact-catalog.v1`
- 这层 source artifact catalog 会冻结：
  - `artifactCatalogEntryId`
  - `artifactKey`
  - `providerLane`
  - `providerKind`
  - `upstreamJobKind`
  - `path`
- 它不是新的业务语义层，而是把“provider binding 最终会解析到哪个物理 artifact”单独抽成一层。这样 provider registry 不需要再直接持有 path，而是可以先引用一个更接近真实 artifact catalog / object-store locator 的 entry。
- 在 artifact catalog 之上，当前又新增了一层 provider registry：
  - `optimizer-source-provider-registry.sample.v1`
  - `optimizer-source-provider-registry.v1`
- 这层 provider registry 会冻结：
  - `providerBindingId`
  - `artifactKey`
  - `providerLane`
  - `providerKind`
  - `upstreamJobKind`
  - `resolutionMode`
  - `artifactCatalogEntryId`
- 当前 committed sample 里的 provider registry 默认通过 `resolutionMode=artifact_catalog_entry` 指向 `optimizer-source-artifact-catalog`，只在 fallback 情况下才直接持有 path。
- 在 provider registry 之上，当前又新增了一层 provider catalog：
  - `optimizer-source-provider-catalog.sample.v1`
  - `optimizer-source-provider-catalog.v1`
- 这层 provider catalog 会冻结：
  - `sourceProviderId`
  - `artifactKey`
  - `providerLane`
  - `providerKind`
  - `upstreamJobKind`
  - `resolutionMode`
  - `providerBindingId`
- 当前 committed sample 里，provider catalog 默认通过 `resolutionMode=provider_binding_registry` 指向 provider registry，而不是直接持有 path。
- 现在又新增了一层 resolver artifact：
  - `optimizer-job-artifact-resolver.sample.v1`
  - `optimizer-job-artifact-resolver.v1`
- 这层 resolver 会把 real-lane source binding 映射到更接近真实上游 job 的 artifact 入口，当前 committed sample 里已经能把 `real_provider_shadow` lane 解析成 ranking/context fixture 加 raw job-run envelope 组合。
- 也就是说，当前 real-shadow lane 已经不再只是“resolver 直接写 path”或“catalog 直接写 path”，而是先走 `resolver -> sourceProviderId -> provider catalog -> providerBindingId -> provider registry -> artifactCatalogEntryId -> path`。
- 新增专门的 shadow ingress gate：
  - `skills/autotiktok/scripts/validate_optimizer_shadow_input_alignment.py`
  - `skills/autotiktok/scripts/test_optimizer_shadow_input_alignment.py`
- 新增 real-lane stand-in gate：
  - `skills/autotiktok/scripts/validate_optimizer_real_shadow_input_alignment.py`
  - `skills/autotiktok/scripts/test_optimizer_real_shadow_input_alignment.py`
- 这条 gate 现在会同时证明两件事：
  - committed source registry 和 raw-shadow manifest 是可重复生成的
  - canonical manifest 和 raw-shadow manifest 会收敛成同一份 runtime optimizer inputs
- real-lane stand-in gate 则会继续证明：
  - committed source artifact catalog、source provider registry、source provider catalog、resolver、source registry 和 real-shadow manifest 是可重复生成的
  - canonical、raw-shadow、real-shadow 三条 lane 会收敛成同一份 runtime optimizer inputs
- 在 scheduler/job 层之上，当前又新增了一份对照计划对象：
  - `optimizer-job-shadow-compare-plan.sample.v1`
  - `optimizer-job-shadow-compare-plan.v1`
- 这份 compare plan 会冻结两组 scheduler-facing shadow compare：
  - `daily production -> raw_shadow_validation`
  - `weekly production -> real_shadow_validation`
- 在 compare plan 之上，当前又新增了一份对照产物：
  - `optimizer-job-shadow-compare.sample.v1`
  - `optimizer-job-shadow-compare.v1`
- 这份 compare artifact 会按 compare plan 物化对应的 scheduled job output 对照结果。
- 它不仅会验证语义是否一致，还会显式记录各条 lane 的：
  - `optimizerInputSourceLane`
  - `optimizerInputRolloutClass`
  - `optimizerInputArtifactResolverId`
  - `optimizerInputSourceProviderCatalogId`
  - `optimizerInputSourceProviderRegistryId`
  - `optimizerInputSourceArtifactCatalogId`
- 新增专门 gate：
  - `skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_alignment.py`
  - `skills/autotiktok/scripts/test_optimizer_job_shadow_compare_alignment.py`
- 在 compare family 之上，当前又新增了一层 batch compare：
  - `optimizer-job-shadow-compare-plan.daily.sample.v1`
  - `optimizer-job-shadow-compare-plan.weekly.sample.v1`
  - `optimizer-job-shadow-compare.daily.sample.v1`
  - `optimizer-job-shadow-compare.weekly.sample.v1`
  - `optimizer-job-shadow-compare-batch-manifest.sample.v1`
  - `optimizer-job-shadow-compare-batch.sample.v1`
- 这层 batch compare 会先冻结“比较哪几份 compare artifact、按哪个 comparison dimension 聚合”，再物化一份 scheduler-facing compare batch，而不是只保留单个 compare object。
- 新增 batch gate：
  - `skills/autotiktok/scripts/validate_optimizer_job_shadow_compare_batch_alignment.py`
  - `skills/autotiktok/scripts/test_optimizer_job_shadow_compare_batch_alignment.py`

这意味着 scheduler 如果传入不合法的：

- `windowSetBatchType`
- `comparisonDimension`

组合，系统会在 window-set builder 入口直接失败，而不是把错误带到后续 replay / eval batch；同时下游产物也能明确知道当前批次归属于哪条 metadata contract family。

这也意味着“真实数据接入层”在当前无真实线上数据的阶段已经完整落地了，而“真实上游接线”也已经从第一版 stand-in 继续收口到了 `source artifact catalog -> provider registry -> provider catalog -> resolver -> source registry -> manifest` 这条 seam；同时 sample lane 和 shadow lane 也已经有了 scheduler-facing compare family 和 compare batch。后续真实 backfill / performance / challenger job 只需要对齐 raw schema，并把真实 source provider / artifact catalog 接到现有 seam 上，不需要重写模块 2 主逻辑。

### 2.8 日级 / 周级 Job Orchestration

- 当前已经不只是有两个独立 runner：
  - `skills/autotiktok-strategy-optimizer/scripts/run_daily_optimizer_job.py`
  - `skills/autotiktok-strategy-optimizer/scripts/run_weekly_optimizer_job.py`
- 还新增了一层 scheduler-facing 计划对象：
  - `skills/autotiktok-strategy-optimizer/fixtures/optimizer-job-schedule.sample.json`
- 以及一个统一 dispatcher：
  - `skills/autotiktok-strategy-optimizer/scripts/run_scheduled_optimizer_job.py`
- 这层计划对象当前会冻结：
  - `scheduleId`
  - `cadenceKind`
  - `jobKind`
  - `defaultInputMode`
  - `defaultInputPath`
  - `defaultPolicyPath`
  - `defaultOutputPath`
  - `rankingContractVersion`
  - `rankingContractValidationMode`
  - `includeWeeklyPromotion`
  - 各类默认 `jobRunId / cycleId / evalRunId / reportId / generatedAt`
- 也就是说，phase 2 现在已经从“有两个脚本入口”推进成了“有一个可被 scheduler 消费的 job schedule plan，再由统一 runner dispatch 到 daily / weekly job”。
- 新增专门 gate：
  - `skills/autotiktok/scripts/validate_optimizer_job_schedule_alignment.py`
  - `skills/autotiktok/scripts/test_optimizer_job_schedule_alignment.py`
- 这条 gate 当前会证明两件事：
  - committed `optimizer-job-schedule.sample.json` 仍然能被确定性生成
  - 用通用 scheduled runner 跑出来的 daily / weekly job run，仍然和 committed `optimizer-daily-job-run.sample.json` / `optimizer-weekly-job-run.sample.json` 完全一致

### 2.9 Weekly Strategy Realism

- weekly 决策现在不再只直接消费单日 `daily-review`。
- 新增了多日聚合 artifact：
  - `optimizer-weekly-review-window.sample.v1`
  - `optimizer-weekly-review-window.v1`
- 当前 weekly promotion 现在走这条链：
  - `daily-review -> optimizer-weekly-review-window -> weekly-promotion`
- 当前已落地：
  - 多日窗口 reward 聚合
  - `minWindowEntries` / `minWinningDays` / `minAvgRewardDelta`
  - `rollbackHoldoutFloor` / `rollbackCombinedRewardFloor` / `rollbackMinBreachDays`
  - `rollback_champion` 决策分支
- 新增专门 gate：
  - `skills/autotiktok/scripts/validate_weekly_strategy_realism.py`
  - `skills/autotiktok/scripts/test_weekly_strategy_realism.py`

### 2.10 Scheduler Input Rollout Policy

- 当前 scheduler/job 层已经不只是冻结 daily / weekly 计划，还开始冻结“输入 lane 如何切换”：
  - `optimizer-input-rollout-policy.sample.v1`
  - `optimizer-input-rollout-policy.v1`
- 当前 rollout policy 会把：
  - `production -> sample_canonical`
  - `raw_shadow_validation -> sample_raw_shadow`
  - `real_shadow_validation -> real_provider_shadow`
    映射成正式 scheduler-facing 对象，而不是继续靠命令行手工约定。
- `optimizer-job-schedule.sample.json` 现在也会显式记录：
  - `defaultInputSourceRegistryPath`
  - `defaultInputRolloutClass`
  - `defaultInputSourceLane`
  - `allowedInputRolloutClasses`
- `run_scheduled_optimizer_job.py` 现在支持：
  - `--input-rollout-class`
  - `--input-source-registry`
  - `--input-rollout-policy`
- 这意味着 scheduler 现在已经能在 job plan 层切换：
  - canonical lane
  - raw-shadow lane
  - real-shadow lane
- 新增专门 gate：
  - `skills/autotiktok/scripts/validate_optimizer_job_schedule_rollout_alignment.py`
  - `skills/autotiktok/scripts/test_optimizer_job_schedule_rollout_alignment.py`
- 这条 gate 会证明：
  - scheduled daily raw-shadow rollout 和 production 语义一致
  - scheduled weekly real-shadow rollout 和 production 语义一致
- 在这个 gate 之上，当前又新增了一份 scheduler-facing compare plan/object：
  - `optimizer-job-shadow-compare-plan.sample.v1`
  - `optimizer-job-shadow-compare-plan.v1`
  - `optimizer-job-shadow-compare.sample.v1`
  - `optimizer-job-shadow-compare.v1`
- compare plan 先冻结“比较哪些 schedule / rollout class 组合”，compare artifact 再把 production / raw-shadow / real-shadow 三条 lane 的 scheduled job output 收成一份 committed artifact，而不是只在 validator 里临时比较。

## 3. 当前未完成部分

当前主要未完成的，不再是模块 2 或调度骨架，而是模块 1 的真实上游接线和真实候选池构建。

### 3.1 TikTok 采集器与快照/原始信号存储

技术方案里的这些对象还没有完成真实接线：

- `collector_creative_center`
- `collector_search_insights`
- `collector_public_tiktok`
- `sourceSnapshots`
- `signalItems`
- `videoSamples`

当前 discovery 已经支持从 `sourceSnapshots + signalItems + videoSamples` materialize 输入，但这三份 artifact 仍主要来自 fixture / stand-in。下一步要把 `autotiktok-trending` 的真实 hot-video 输出转成 discovery 可消费的三输入。

### 3.2 模块 1 真实流水线

技术方案定义的这条 discovery 流水线还没有在真实输入上跑起来：

1. `Signal Ingestion`
2. `Normalization`
3. `Topic Abstraction`
4. `Candidate Expansion`
5. `Merge & Dedupe`
6. `Tagging & Packaging`

当前 `discovery_dry_run.py` 已覆盖 deterministic ingest、normalization、topic abstraction、merge / dedupe、evidence packaging scaffold，但还没有在真实 collector 输出上跑通。

### 3.3 模块 1 -> Ranking 的真实 Handoff

虽然 `topicCandidate` contract 已经稳定，但还没有完成下面这些真实接线：

- 用真实 snapshot / signal artifact 生成 discovery output
- 用真实 discovery artifact 驱动 ranking dry-run / profile matrix
- 把 snapshot/source provenance 从 discovery 一路透传到 ranking、optimizer、workflow summary

### 3.4 协作边界

当前最适合并行开发的边界是：

- 上游同事负责：
  - `autotiktok-trending` 热门视频采集器
  - `autotiktok-video-download` 视频下载 sidecar
  - 快照与原始信号存储
- 当前模块可以继续推进：
  - trending metadata -> discovery 三输入 adapter
  - metadata-only synthetic `signalItems` builder
  - discovery -> ranking 的真实输入 handoff smoke
  - 后续 MP4 多模态内容分析 artifact

也就是说，模块 1 不需要等上游全部完工才开始，但最终的真实 E2E 需要和 collector / snapshot contract 对齐。

## 4. 开发阶段总览

### 阶段 1（已完成）：接入 cron / job orchestration

目标：

- 把当前链路从“可手动回放”推进成“可调度运行”。

当前状态：

- 已完成：
  - `optimizer-job-schedule` 现在已经支持 `fixture_replay` / `external_scheduler` 双 profile
  - 新增 committed fixture：
    - `optimizer-job-schedule.sample.json`
    - `optimizer-job-schedule.external.sample.json`
    - `optimizer-job-execution-context.sample.json`
    - `optimizer-job-orchestration-cycle.sample.json`
  - `run_scheduled_optimizer_job.py` 已支持：
    - scheduler-supplied path resolution
    - `output_root` emission
    - execution context provenance
    - structured error artifact
  - `run_optimizer_job_orchestration_cycle.py` 已支持：
    - execution-context 驱动的 daily / weekly schedule run
    - raw-shadow / real-shadow compare automation
    - compare batch 自动物化
    - scheduler-facing cycle artifact 汇总

建议拆分：

- 日级：
  - `manifest -> bundle -> daily review -> offline cycle`
- 周级：
  - `weekly promotion / rollback decision`

完成标准：

- 日级和周级入口具备独立 runner
- planner artifact 与 runtime artifact 的边界清晰
- scheduler-facing job schedule plan 可以统一 dispatch 到 daily / weekly job

当前结果：

- 上述完成标准已经满足，阶段 1 完成。

### 阶段 2（已完成）：增强 weekly strategy realism

目标：

- 让 weekly promotion / rollback 逻辑更接近真实策略，而不是只靠 sample 决策路径。

建议拆分：

- 开发包 1（已完成）：多日窗口聚合增强
  - 扩 `optimizer-weekly-review-window`
  - 从单一 summary 聚合，推进到更明确的 day-by-day / window-by-window reward 汇总
  - 显式区分 `t+1`、`t+3`、可选 `t+7` 的权重和可用性
- 开发包 2（已完成）：holdout / safety gate 收紧
  - 把当前 sample 级 holdout / safety 条件推进成更像真实晋升门槛的 gate
  - 明确 champion / challenger 在 hidden holdout、duplicate、coverage、executable-rate 上的最低要求
  - 让 weekly decision artifact 显式记录是哪个 gate 拒绝了晋升
- 开发包 3（已完成）：rollback 条件细化
  - 把 rollback 从当前存在与否判断，推进成更清晰的 rollback reason / rollback severity / rollback eligibility
  - 让 weekly promotion / keep / rollback 三种结果的判定边界稳定下来
  - 保证 rollback 逻辑可以被 scheduler-facing artifact 和 compare 继续透传
- 开发包 4（已完成）：账号阶段差异化 weekly gate
  - 按 `growth`、`scale`、`search_priority` 等阶段收紧 weekly gate
  - 让不同阶段在 promotion threshold、risk tolerance、holdout 要求上可以不同
  - 保证 stage matrix、weekly decision、workflow summary 仍然一致
- 开发包 5（已完成）：validator / artifact / sample 跟进
  - 给 weekly realism 新增 deterministic fixture、semantic gate、aggregate smoke
  - 保证新 weekly 语义不是只存在于脚本实现里，而是也存在 committed artifact contract 里

重点任务：

- 多日窗口 reward 聚合
- holdout / safety gate
- rollback gate
- champion / challenger 更真实的晋升条件

当前状态：

- 已完成：
  - 开发包 1 已落地
  - 开发包 2 已落地
  - 开发包 3 已落地
  - 开发包 4 已落地
  - `optimizer-weekly-review-window` 现在已经显式带：
    - `rewardHorizonPolicy`
    - 每个 window 的 `availableRewardHorizonIds`
    - champion / challenger 的 `rewardHorizonBreakdown`
    - `aggregatedChampion.rewardHorizonSummaries`
    - `challengerSummaries[*].rewardHorizonSummaries`
    - `rollbackSignals.rollbackEligible`
    - `rollbackSignals.rollbackSeverity`
    - `rollbackSignals.rollbackReasonCodes`
  - `weekly-promotion` 的 `gateSummary` 现在也会继续记录：
    - `rewardHorizonIds`
    - `requiredRewardHorizonIds`
    - `optionalRewardHorizonIds`
    - `minimumHardGatePassDays`
    - `minimumAverageRewardDelta`
    - `minimumAverageHoldoutDelta`
    - `maximumPostCoverageRateDrop`
    - `rollbackCriticalHoldoutFloor`
    - `rollbackCriticalCombinedRewardFloor`
    - `weeklyStageMode`
    - `weeklyStagePolicyId`
    - `weeklyStagePolicySelectionSource`
  - `weekly-promotion` 现在还会显式带：
    - `promotionCandidateReviews[*]`
    - `championSafetyReview`
    - `championSafetyReview.rollbackEligible`
    - `championSafetyReview.rollbackSeverity`
    - `championSafetyReview.rollbackReasonCodes`
  - committed sample 现在也已经扩成：
    - `optimizer-weekly-review-window.sample.json`
    - `optimizer-weekly-review-window.scale.sample.json`
    - `optimizer-weekly-review-window.search-priority.sample.json`
    - `weekly-promotion.sample.json`
    - `weekly-promotion.scale.sample.json`
    - `weekly-promotion.search-priority.sample.json`
  - hub gate 现在也已经补到：
    - `validate_weekly_strategy_realism.py`
    - `validate_weekly_stage_policy_alignment.py`
- 下一步：
  - 进入阶段 3：继续收紧 scheduler / rollout policy

完成标准：

- weekly decision 不再只是 deterministic sample 输出
- 能基于多日窗口给出更可信的 promotion / rollback 结果

### 阶段 3（已完成）：继续收紧 scheduler / rollout policy

目标：

- 在真实 lane 和 cron 接入后，把当前的 planner / rollout policy 从 sample 演练推进成真实切流策略。

建议拆分：

- 开发包 1：统一 rollout policy 面
  - 收清 `input lane`、`runtime profile lane`、`rollout class`、`eval purpose` 的边界
  - 明确 explicit override、schedule default、purpose/template default、fallback default 的优先级
  - 避免 scheduler、runner、compare 各自长出一套 lane 解释逻辑
- 开发包 2：scheduler intent contract
  - 让 `optimizer-job-schedule` 显式表达 rollout intent，而不是只靠临时 flag 或 fixture 约定
  - 区分 production、preview validation、raw shadow validation、real-provider shadow validation、profile compare validation
  - 让 daily / weekly / compare 都共享同一套 intent contract
- 开发包 3：policy resolver 接入调度链
  - 让 schedule -> rollout policy -> source lane / runtime profile lane 自动化
  - 把 selection source 明确写进 artifact provenance
  - 非法 override 或冲突组合在 runner 入口直接拒绝
- 开发包 4：cutover rehearsal 和 compare 联动
  - 让 shadow compare / compare batch 能理解 rollout intent
  - 把 current / preview / real-shadow 的切换规则接进 scheduler-facing compare artifact
  - 补 scheduler-facing 的 cutover rehearsal gate
- 开发包 5：artifact / validator / smoke 收口
  - 为阶段 3 新增 deterministic fixture、semantic gate、aggregate smoke
  - 保证新的 rollout policy 语义落进 committed artifact，而不是只停在实现里

重点任务：

- 统一 input lane 和 runtime profile lane 的 policy 分层
- scheduler rollout intent contract
- policy resolver 接入调度链
- current / preview / real-shadow compare 联动
- validator / artifact / smoke 收口

当前状态：

- 开发包 1 已完成：
  - `optimizer-input-rollout-policy` 现在显式区分 `rolloutIntent`、`rolloutClass`、`sourceLane`
  - `optimizer-job-schedule` 现在会透传 default/allowed rollout intents，以及默认 intent/class 的 selection provenance
  - input rollout 的 precedence 已固定成 `explicit rollout class -> explicit rollout intent -> schedule intent default -> global intent default`
- 开发包 2 已完成：
  - `optimizer-job-schedule` 现在新增顶层 `schedulerRolloutIntents[*]` catalog，显式冻结 `production`、`raw_shadow_validation`、`real_provider_shadow_validation`、`preview_validation`、`profile_compare_validation`
  - schedule entry 现在会继续透传 `defaultSchedulerRolloutIntent`、`allowedSchedulerRolloutIntents`
  - `optimizer-job-execution-context` 现在会显式冻结 `productionSchedulerRolloutIntent` 和 `shadowSchedulerRolloutIntent`
  - `run_scheduled_optimizer_job.py` 现在支持 `--scheduler-rollout-intent`，并把 scheduler intent、runtime profile rollout class、window-set purpose、comparison dimension 一路透传到 `optimizer-job-run`、shadow compare、compare batch、orchestration cycle
- 开发包 3 已完成：
  - schedule -> input rollout policy -> source lane / runtime profile lane 现在已经由统一 resolver 自动解析
  - `optimizer-job-schedule` 现在会显式冻结 `defaultRuntimeProfileRolloutClass`、`defaultWindowSetPurpose`、`defaultComparisonDimension`
  - schedule entry 现在还会冻结 `allowedRuntimeProfileRolloutClasses`、`allowedWindowSetPurposes`、`allowedComparisonDimensions`
  - `run_scheduled_optimizer_job.py` 现在统一走 execution-policy resolver，并把 selection provenance 继续透传到 generatedFrom
- 开发包 4 已完成：
  - scheduler-facing compare plan 现在不只覆盖 raw-shadow / real-shadow，也覆盖 `preview_validation` 和 `profile_compare_validation`
  - compare artifact 现在会显式记录 candidate 的 runtime profile rollout class、window-set purpose、comparison dimension
  - compare batch 现在默认按 `candidateSchedulerRolloutIntent` 聚合，而不再只按 `scheduleId`
  - 新增 cutover rehearsal gate：`validate_optimizer_job_shadow_compare_cutover_alignment.py`
- 开发包 5 已完成：
  - committed sample、semantic gate、aggregate smoke 都已经更新到阶段 3 的 policy 语义
  - `validate_all_mock_artifacts.py`、`test_mock_artifact_pipeline.py`、`test_autotiktok_skills.py` 已接入新的 compare cutover validator

完成标准：

- 不同 eval purpose 和 rollout class 可以稳定映射到不同 lane / policy
- 非法 override 会在 planner 入口被拒绝
- sample / validator / smoke 全部跟上

### 阶段 4（已完成）：监控与运维

目标：

- 补齐真正运行所需的运维面。

建议拆分：

- 开发包 1：artifact retention contract
  - 冻结 scheduler-facing artifact 的 retention policy
  - 区分 input、job run、shadow compare、compare batch、orchestration cycle、job error 的保留层级和保留策略
  - 让 `optimizer-job-orchestration-cycle` 显式记录 retention policy provenance
- 开发包 2：run summary contract
  - 补一个轻量、可聚合的运行摘要对象
  - 汇总 schedule 执行结果、weekly decision、compare 结果、rollback watch/warning/critical
- 开发包 3：error reporting / failure triage
  - 让 `optimizer-job-error.v1` 从单点结构化错误对象扩成更完整的 failure taxonomy
  - 区分可重试错误、contract breakage、input resolution failure、policy failure
- 开发包 4：dashboard-facing aggregate artifacts
  - 增加 recent run / compare / weekly decision / failure 的轻量 aggregate artifacts
  - 为 dashboard / ops 页提供稳定输入，而不是直接扫原始 artifact
- 开发包 5：artifact / validator / smoke 收口
  - 刷新 committed sample
  - 补 semantic gate
  - 接进 `validate_all_mock_artifacts.py`、`test_mock_artifact_pipeline.py`、`test_autotiktok_skills.py`

当前状态：

- 开发包 1 已完成：
  - 已新增 `optimizer-job-artifact-retention-policy.*`
  - `optimizer-job-orchestration-cycle` 现在会透传 retention policy artifact、本次受 retention 管理的 artifact kind 列表，以及 retention policy provenance
  - hub gate `validate_optimizer_job_artifact_retention_policy_alignment.py` 已接入 aggregate validator / smoke
- 开发包 2 已完成：
  - 已新增 `optimizer-run-summary.*`
  - orchestration cycle 现在会内嵌 `artifacts.runSummary`，并可单独物化成 committed `optimizer-run-summary.sample.json`
  - run summary 当前会显式汇总 `runStatus`、schedule 成功/失败状态、compare match/mismatch、weekly decision、scheduler rollout intent 计数
  - hub gate `validate_optimizer_run_summary_alignment.py` 已接入 aggregate validator / smoke
- 开发包 3 已完成：
  - 已新增 committed `optimizer-job-error.sample.json`
  - `optimizer-job-error.v1` 现在会显式带 `failureStage`、`retryable`、`ownerHint`、`failureSummary`
  - scheduled runner 现在会把输入缺失、rollout 解析失败、artifact emission 失败等情况区分成不同 taxonomy，而不再统一落成一个 `scheduled_job_failed`
  - orchestration cycle 现在会按 schedule 收集结构化 `errors[]`，并把这层 failure triage 继续透传到 `optimizer-run-summary.errorSummaries`
  - hub gate `validate_optimizer_job_error_alignment.py` 已接入 aggregate validator / smoke
- 开发包 4 已完成：
  - 已新增 4 份 dashboard-facing aggregate artifact：
    - `optimizer-recent-run-summaries.*`
    - `optimizer-recent-compare-summaries.*`
    - `optimizer-recent-weekly-decisions.*`
    - `optimizer-recent-failure-summaries.*`
  - recent run aggregate 现在会直接汇总 `runStatus`、production/shadow job-run 数量、compare artifact 数量、weekly decision 和 scheduler rollout intent 计数
  - recent compare aggregate 现在会把 committed compare batch 和 orchestration-cycle 内嵌 compare batch 收成稳定的 `entries + groupEntries` contract，供 dashboard / ops 扫描 compare lane
  - recent weekly decision aggregate 现在会从 scheduler-facing job-run record 继续透传 `weeklyStageMode`、`weeklyStagePolicyId`、rollback severity 和 selected challenger
  - recent failure aggregate 现在会把 standalone `optimizer-job-error` 和 orchestration-cycle `artifacts.errors` 收成统一的 failure summary 入口
- 开发包 5 已完成：
  - committed sample 已刷新并新增 4 份 recent aggregate fixture
  - 新增 hub gate：
    - `validate_optimizer_recent_run_summaries_alignment.py`
    - `validate_optimizer_recent_compare_summaries_alignment.py`
    - `validate_optimizer_recent_weekly_decisions_alignment.py`
    - `validate_optimizer_recent_failure_summaries_alignment.py`
  - 已接进 `validate_all_mock_artifacts.py`、`test_mock_artifact_pipeline.py`、`test_autotiktok_skills.py`

完成标准：

- 调度任务运行结果可追踪
- 异常能被发现和定位

### 阶段 5（已完成）：模块 1 真实实现

目标：

- 把当前 discovery scaffold 从 fixture packaging 升级成真实的模块 1 流水线。

建议拆分：

- 开发包 1：collector output / snapshot contract adapter
  - 冻结 discovery 实际消费的 `raw signal` / `snapshot materialization` contract
  - 明确 collector 输出如何映射到 `raw-signals` 或等价中间对象
  - 让 discovery 不再直接依赖手写 fixture 结构
- 开发包 2：snapshot 驱动的 discovery ingest
  - 让 discovery 从 snapshot / signal / video sample artifact materialize 输入
  - 把 `sourceSnapshots`、`signalItems`、`videoSamples` 映射到 discovery runtime object
  - 保留 replay-friendly 的 snapshot provenance
- 开发包 3：normalization 与 topic abstraction
  - 把当前 dry-run 的固定字段拼装推进成真正的 normalization 规则
  - 补 topic abstraction、candidate expansion、topic title / summary 生成规则
  - 收紧 `topicFingerprint` 的稳定性
- 开发包 4：merge / dedupe / evidence packaging
  - 强化 `evidenceBundle`
  - 强化 merge-group 规则
  - 完成 `searchEvidence`、`executionProfile`、`executionNotes` 的真实打包逻辑
- 开发包 5：discovery -> ranking 真实 handoff 与总链路收口
  - 让 ranking 默认消费真实 discovery artifact，而不是派生 fixture
  - 补 provenance、validator、workflow smoke
  - 保证真实 discovery 输入不会打破 ranking / optimizer 的已完成 contract

重点任务：

- 把 collector / snapshot 结果接成 discovery 真正的 ingest seam
- 完成模块 1 的 normalization、abstraction、merge、packaging
- 把 `topicCandidate` 从 dry-run artifact 升级成真实上游驱动产物
- 继续保持 discovery -> ranking -> optimizer 的 contract 稳定

当前状态：

- 已完成：
  - discovery-owned `topicCandidate` contract
  - `discovery-snapshot-materialization.sample.json`
  - `raw-signals.sample.json`
  - `discovery-policy.v1.json`
  - `discovery_dry_run.py`
  - `discovery-dry-run.sample.json`
  - discovery -> ranking dry-run handoff
  - 开发包 1 已完成：
    - discovery 默认输入已经从手写 `raw-signals.sample.json` 切到 `discovery-snapshot-materialization.sample.json`
    - discovery core 现在会先走 snapshot-materialization adapter，再进入 raw-signal compatibility layer
    - 新增 validator / hub gate：
      - `validate_discovery_snapshot_materialization.py`
      - `validate_discovery_snapshot_materialization_alignment.py`
  - 开发包 2 已完成：
    - discovery ingest seam 现在已经拆成独立的：
      - `source-snapshots.sample.json`
      - `signal-items.sample.json`
      - `video-samples.sample.json`
    - `build_discovery_snapshot_materialization.py` 现在会把这 3 份 standalone artifact materialize 成 committed `discovery-snapshot-materialization.sample.json`
    - `discovery_dry_run.py` 现在支持直接消费 `--source-snapshots / --signal-items / --video-samples`
    - `run_autotiktok_workflow.py` 默认 discovery lane 也已经切到 standalone snapshot ingest，而不是只吃预构建 materialization fixture
    - 新增 validator / hub gate：
      - `validate_discovery_snapshot_ingest_alignment.py`
      - `test_discovery_snapshot_ingest_alignment.py`
  - 开发包 3 已完成：
    - discovery output 现在显式带：
      - `normalizedSignals`
      - `topicAbstractions`
    - `topicCandidate` 的 canonical title / summary 现在通过 abstraction layer 选定，而不是只在 packaging 末端隐式吃 anchor 字段
    - discovery 现在会继续透传：
      - `normalizationRuleVersion`
      - `normalizedSignalCount`
      - `topicAbstractionCount`
    - 新增 semantic gate：
      - `validate_discovery_topic_abstraction_expectations.py`
      - `test_discovery_topic_abstraction_expectations.py`
  - 开发包 4 已完成：
    - `evidenceBundles` 现在显式带：
      - `sourceSnapshotRefs`
      - `videoSampleIds`
      - `mergeClassification`
      - `searchEvidenceSummary`
      - `executionEvidenceSummary`
    - `mergeGroups` 现在显式带：
      - `mergeClassification`
      - `dedupeDecision`
      - `mergeGuardrails`
      - `packagingReadiness`
    - `topicCandidate.searchEvidence` / `executionProfile` 现在显式带 packaging counts 和 labels
    - `executionNotes` 现在会附带一条稳定的 packaging summary
    - 新增 semantic gate：
      - `validate_discovery_merge_packaging_expectations.py`
      - `test_discovery_merge_packaging_expectations.py`
  - 开发包 5 已完成：
    - ranking dry-run / profile matrix / optimizer stage matrix 默认输入现在都切到 committed discovery artifact，而不是 `topic-candidates.fixture.json`
    - ranking handoff provenance 现在会显式冻结：
      - `sourceInputKind`
      - `sourceMaterializationId`
      - `sourceNormalizationRuleVersion`
    - workflow summary 现在也会继续透传这条 discovery -> ranking provenance
    - 新增 direct handoff gate：
      - `validate_discovery_ranking_handoff_alignment.py`
      - `test_discovery_ranking_handoff_alignment.py`
- 后续外部依赖：
  - 真实 collector / snapshot artifact 接入仍依赖上游模块完成
  - 当前模块 1 repo 内计划已经收口，后续主要是把真实采集器和快照存储接进现有 seam
- 协作说明：
  - 如果 collector 和 snapshot 由其他同事开发，当前已完成的开发包 1 可以作为输入 contract 对齐基线
  - 开发包 2-5 仍然可以在 agreed contract 和 stand-in snapshot object 上并行推进

完成标准：

- discovery 可以消费 snapshot/materialized raw signal，而不是只消费手写 fixture
- discovery 能稳定产出真实 `topicCandidate`
- ranking 可以直接消费真实 discovery artifact
- workflow summary 能从 discovery provenance 一路追到 optimizer / orchestration

### 阶段 6（已完成）：迁移到 OpenClaw 标准 cron

目标：

- 把 AutoTikTok 的 recurring optimizer job 从当前自定义 scheduler-facing control plane 迁到 OpenClaw 标准 cron runtime。

建议拆分：

- 开发包 1（已完成）：标准 cron entrypoint 与 skill 规则
  - 新增薄入口脚本：
    - `run_openclaw_cron_daily_optimizer.py`
    - `run_openclaw_cron_weekly_optimizer.py`
  - 复用现有 daily / weekly job runner，不重写业务逻辑
  - 在 `SKILL.md` 和 reference 里明确：
    - 使用 OpenClaw cron
    - 使用稳定 job name
    - 先 `list` 再 `edit/add`
- 开发包 2（已完成）：cron job 管理 contract
  - 把 AutoTikTok skill 的调度规则补成和 `healthcheck` 一样的标准模式
  - 明确：
    - `autotiktok:daily-optimizer`
    - `autotiktok:weekly-optimizer`
  - 给出稳定的 `openclaw cron add` / `openclaw cron edit` 模板
- 开发包 3（已完成）：runtime cutover
  - 让 OpenClaw cron 成为 daily / weekly optimizer job 的首选 runtime 入口
  - 保持输出仍然是现有 `optimizer-job-run.v1`
  - 保持现有 daily review / weekly review window / weekly promotion / eval / compare 业务链不变
- 开发包 4（已完成）：兼容层降级
  - 把 `optimizer-job-schedule`、`optimizer-job-execution-context`、`optimizer-job-orchestration-cycle` 从“主运行路径”降级成：
    - fixture generation
    - deterministic rehearsal
    - cutover validation
  - 不立即删除，先去掉 runtime source-of-truth 地位
- 开发包 5（已完成）：validator / docs / ops 收口
  - 为 OpenClaw cron runtime 增加 focused smoke
  - 文档明确区分：
    - 标准 cron 运行路径
    - fixture-only scheduler artifacts
  - 保证后续团队不会再把自定义 scheduler artifact 当成真实调度入口

重点任务：

- 用 OpenClaw cron 替代 AutoTikTok 自定义 scheduler runtime
- 保留业务 runner，替换调度控制面
- 收口 stable job name、list/edit/add 规则、cron prompt 模板
- 把旧 scheduler artifact 降级为兼容/演练层，而不是直接删除

当前状态：

- 开发包 1 已完成：
  - 已新增：
    - `skills/autotiktok-strategy-optimizer/scripts/openclaw_cron_job_lib.py`
    - `skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_daily_optimizer.py`
    - `skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_weekly_optimizer.py`
  - 新入口会直接复用：
    - `run_daily_optimizer_job.py`
    - `run_weekly_optimizer_job.py`
  - 新入口已支持：
    - `--output`
    - `--output-root`
    - OpenClaw isolated cron 友好的简洁文本 summary
  - `skills/autotiktok-strategy-optimizer/SKILL.md` 和 `references/optimizer-artifacts.md` 已补 OpenClaw cron 规则与模板
- 开发包 2 已完成：
  - 已新增 committed contract artifact：
    - `skills/autotiktok-strategy-optimizer/fixtures/optimizer-openclaw-cron-contract.sample.json`
  - 已新增 contract builder：
    - `skills/autotiktok-strategy-optimizer/scripts/openclaw_cron_contract_lib.py`
    - `skills/autotiktok-strategy-optimizer/scripts/build_optimizer_openclaw_cron_contract.py`
  - 当前 contract 已冻结：
    - 稳定 job name：
      - `autotiktok:daily-optimizer`
      - `autotiktok:weekly-optimizer`
    - `openclaw cron list -> exact-name match -> edit/add` 管理策略
    - 标准 `openclaw cron add` / `openclaw cron edit <job-id>` 模板
    - 默认 isolated session、`exec/read/write` tool allow-list、`--light-context`、`--no-deliver`
- 开发包 3 已完成：
  - `run_openclaw_cron_daily_optimizer.py` 现在默认走 canonical `optimizer-input-manifest.sample.json`
  - `run_openclaw_cron_weekly_optimizer.py` 现在默认走 canonical `optimizer-input-manifest.sample.json` 和 `optimizer-weekly-review-window.sample.json`
  - 已新增 focused gate：
    - `skills/autotiktok/scripts/validate_optimizer_openclaw_cron_runtime_alignment.py`
    - `skills/autotiktok/scripts/test_optimizer_openclaw_cron_runtime_alignment.py`
  - `skills/autotiktok/scripts/sync_optimizer_sample_outputs.py` 现在会同步：
    - `skills/autotiktok-strategy-optimizer/fixtures/optimizer-openclaw-cron-contract.sample.json`
  - OpenClaw cron runtime gate 已接进：
    - `validate_all_mock_artifacts.py`
    - `test_mock_artifact_pipeline.py`
    - `test_autotiktok_skills.py`
- 开发包 4 已完成：
  - `optimizer-job-schedule`、`optimizer-job-execution-context`、`optimizer-job-orchestration-cycle` 现在都会显式冻结：
    - `runtimeRole=compatibility_rehearsal`
    - `preferredRecurringRuntime=openclaw_cron`
    - `intendedUses=[fixture_generation, deterministic_rehearsal, cutover_validation]`
  - 已新增 focused semantic gate：
    - `skills/autotiktok/scripts/validate_optimizer_scheduler_compatibility_role_alignment.py`
    - `skills/autotiktok/scripts/test_optimizer_scheduler_compatibility_role_alignment.py`
  - compatibility-role gate 已接进：
    - `validate_all_mock_artifacts.py`
    - `test_mock_artifact_pipeline.py`
    - `test_autotiktok_skills.py`
- 开发包 5 已完成：
  - 已新增 ops runbook：
    - `skills/autotiktok-strategy-optimizer/references/openclaw-cron-ops.md`
  - hub / schema / technical docs 现在都显式区分：
    - OpenClaw 标准 cron runtime
    - compatibility-only scheduler artifacts
  - focused gate 入口已在 hub 文档里收口：
    - `validate_optimizer_openclaw_cron_runtime_alignment.py`
    - `validate_optimizer_scheduler_compatibility_role_alignment.py`
- 下一步：
  - 阶段 6 完成；下一步回到真实 collector / snapshot artifact 接线

完成标准：

- AutoTikTok recurring runtime 的 source of truth 变成：
  - `openclaw cron list`
  - `openclaw cron runs`
  - Gateway task / cron history
- AutoTikTok 现有 scheduler-facing artifact 不再被视为真实调度主入口
- daily / weekly recurring runs 可以只通过 OpenClaw 标准 cron 完成

### 阶段 7（已完成）：`autotiktok-trending` metadata bootstrap 接入 discovery

目标：

- 先不用多模态模型，只基于 `autotiktok-trending` 已经采集到的 metadata，把真实热门视频输入接到 discovery。
- 跑通第一条真实 collector 链路：
  - `autotiktok-trending output -> sourceSnapshots -> videoSamples -> synthetic signalItems -> discovery -> ranking`
- 明确 `autotiktok-video-download` 当前是媒体下载 sidecar，不作为 discovery 主输入。

输入范围：

- 支持标准 bakeoff 输出：
  - `routes[*].absolute_hot_video_samples`
  - `routes[*].fresh_hot_video_samples`
- 支持 consolidated top-N 输出：
  - 顶层 `absolute_hot_video_samples`
  - 其中 `videoSamples[*]` 可能仍是 raw/ranked row，需要 adapter 归一化。

建议拆分：

- 开发包 1（已完成）：trending 输出形状识别与 adapter contract
  - 识别两类输入：
    - 标准 canonical `discovery-video-samples.v1`
    - consolidated raw/ranked rows
  - 明确哪些字段来自 collector 原始输出，哪些字段由 adapter 生成。
  - 建立 focused fixture，覆盖至少一个 canonical bakeoff 样例和一个 consolidated top-N 样例。
- 开发包 2（已完成）：`sourceSnapshots` 生成
  - 从 trending artifact 的 `snapshotId`、`market`、`language`、`capturedAt` 生成 discovery source snapshot artifact。
  - `source` 固定为 `public_tiktok`。
  - `sourceSubtype` 按输入视图区分：
    - `absolute_hot_video_sample`
    - `fresh_hot_video_sample`
    - `consolidated_hot_video_sample`
  - 保证所有 normalized video sample 的 `sourceSnapshotId` 都能回指到 `sourceSnapshots[*].sourceSnapshotId`。
- 开发包 3（已完成）：`videoSamples` 字段归一化
  - 把 raw/ranked row 机械映射成 canonical `videoSamples[*]`。
  - 核心映射：
    - `video_id -> platformVideoId`
    - `video_id -> videoSampleId=tt:<video_id>`
    - `create_time -> publishedAt`
    - `description -> title / desc`
    - `author_id -> authorId`
    - `author -> authorHandle`
    - `author_display_name -> authorDisplayName`
    - `view_count / like_count / share_count / comment_count -> metrics`
    - `share_url || url -> shareUrl`
  - `hot_score`、`ranking_mode`、`ranking_rank`、`route_rank` 等 collector 排名诊断只进入 `rawMeta`，不进入 canonical 顶层。
  - 对 `hashtags` 做轻量清洗；缺失时从 `description` 的 `#tag` 提取。
  - 按 `videoSampleId` 去重，保留稳定、可解释的优先级。
- 开发包 4（已完成）：metadata-only synthetic `signalItems`
  - 每条 normalized video sample 先生成一条 synthetic public-video signal。
  - 动态生成字段：
    - `signalId`
    - `topicId`
    - `topicFingerprint`
    - `topicTitle`
    - `topicSummary`
    - `keywords`
    - `contentAngles`
    - `relatedQueries`
    - `signalConfidence`
    - `expandabilityHint`
  - 默认字段先固定：
    - `topicType=trend`
    - `sourceType=public_video_sample`
    - `searchIntentType=trend_reaction`
    - `searchPersistenceHint=daily`
    - `recommendedMode=growth`
    - `freshnessWindow=daily`
    - `recommendedFormats=[talking_head, image_plus_voiceover]`
    - `requiredAssets=[reference video, trend screenshots]`
    - `requiredCapabilities=[trend commentary, fast edit packaging]`
  - `executionNotes` 必须显式标注这是 metadata-derived synthetic signal，避免和后续多模态分析结果混淆。
- 开发包 5（已完成）：discovery / ranking 联调和 validator 收口
  - 新增 adapter 脚本：
    - `skills/autotiktok-topic-discovery/scripts/build_discovery_inputs_from_trending.py`
  - 输出三份文件：
    - `source-snapshots.from-trending.json`
    - `video-samples.from-trending.json`
    - `signal-items.from-trending.synthetic.json`
  - 用现有入口验证：
    - `build_discovery_snapshot_materialization.py`
    - `discovery_dry_run.py`
    - `dry_run_ranking.py`
  - 新增 focused alignment gate，证明 trending output 可以稳定进入 discovery / ranking。

完成标准：

- consolidated top-N trending 输出可以转成合法 `sourceSnapshots`、`videoSamples`、`signalItems`。
- `videoSamples` 通过 discovery 当前字段校验，不再把 raw/ranked row 伪装成 canonical video sample。
- `signalItems` 第一版先以 metadata-derived synthetic signal 形式跑通链路。
- discovery 能产出 `topicCandidates`，ranking 能消费这些 candidates。
- 输出 provenance 能追溯到原始 `videoSampleId` / `platformVideoId` / `sourceSnapshotId`。

后续阶段预留：

- 阶段 7 完成后，再进入 MP4 多模态内容分析：
  - `videoSamples + download manifest -> videoContentAnalysis -> enriched signalItems`
  - 多模态模型只增强题材理解，不直接替代 deterministic adapter。

### 阶段 8（已完成）：MP4 多模态内容分析接入

目标：

- 基于 `autotiktok-video-download` 下载到本地的 MP4，生成可追溯的 `videoContentAnalysis` artifact。
- 默认使用 OpenClaw media-understanding：
  - `provider=google`
  - `model=gemini-3-flash-preview`
- 模型选择必须是配置默认值，而不是写死在业务逻辑深处；脚本需要支持 CLI 参数覆盖，后续可切换到 `kimi-k2.6`、`gemini-3.1-pro-preview` 或 shadow compare。
- 第一版只做 sidecar enhancement，不替代阶段 7 已完成的 deterministic metadata adapter。
- 输出结果用于增强 synthetic `signalItems`，让 discovery / ranking 在原有 metadata-only 链路之外获得视频内容理解证据。

输入范围：

- 阶段 7 已生成的 `videoSamples`：
  - `videoSampleId`
  - `platformVideoId`
  - `sourceSnapshotId`
  - `shareUrl`
  - `hashtags`
  - `metrics`
  - `rawMeta`
- `autotiktok-video-download` 的下载 manifest 或下载目录：
  - 本地 MP4 路径
  - 下载状态
  - 原始 TikTok video id / URL
  - 下载时间
  - 文件大小 / MIME 信息
- OpenClaw video describe 输出：
  - `ok`
  - `provider`
  - `model`
  - `outputs[*].text`
  - `attempts`
  - `errors`

建议拆分：

- 开发包 1（已完成）：`videoContentAnalysis` contract 与 focused fixture
  - 定义 `videoContentAnalysis.v1` artifact 形状。
  - 每条分析结果至少包含：
    - `analysisId`
    - `videoSampleId`
    - `platformVideoId`
    - `sourceSnapshotId`
    - `videoPath`
    - `provider`
    - `model`
    - `status`
    - `descriptionText`
    - `contentSummary`
    - `visualEvidence`
    - `replicationHints`
    - `analysisConfidence`
    - `provenance`
    - `errors`
  - 新增 sample artifact，覆盖：
    - 成功分析的视频
    - 下载缺失的视频
    - 模型调用失败的视频
  - 明确 `provider/model` 默认来自配置，例如：
    - `videoUnderstanding.provider=google`
    - `videoUnderstanding.model=gemini-3-flash-preview`
  - 已新增 focused artifact、默认配置和 gate：
    - `skills/autotiktok-topic-discovery/config/video-understanding.v1.json`
    - `skills/autotiktok-topic-discovery/fixtures/video-content-analysis.sample.json`
    - `skills/autotiktok-topic-discovery/references/video-content-analysis-contract.md`
    - `skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_contract.py`
    - `skills/autotiktok/scripts/validate_video_content_analysis_contract_alignment.py`
  - focused fixture 已覆盖成功分析、下载缺失、模型调用失败三种状态。
- 开发包 2（已完成）：download manifest adapter
  - 把 `autotiktok-video-download` 的下载产物归一化成 `videoDownloadManifest`。
  - 建立 `videoSamples[*] -> downloaded MP4` 的 deterministic join 规则。
  - 优先用 `platformVideoId` 匹配，其次用 share URL / filename fallback。
  - 对缺失、重复、无效 MP4 产出结构化状态，不中断主链路。
  - 已新增 focused artifact、adapter builder 和 gate：
    - `skills/autotiktok-topic-discovery/fixtures/video-samples.download-adapter.sample.json`
    - `skills/autotiktok-topic-discovery/fixtures/video-download-raw.sample.json`
    - `skills/autotiktok-topic-discovery/fixtures/video-download-manifest.sample.json`
    - `skills/autotiktok-topic-discovery/references/video-download-manifest-contract.md`
    - `skills/autotiktok-topic-discovery/scripts/build_video_download_manifest.py`
    - `skills/autotiktok-topic-discovery/scripts/validate_video_download_manifest_adapter.py`
    - `skills/autotiktok/scripts/validate_video_download_manifest_adapter_alignment.py`
  - focused fixture 已覆盖 `downloaded`、`download_missing`、`download_error`、`invalid_file` 和 duplicate raw download。
- 开发包 3（已完成）：视频理解 batch runner
  - 新增脚本按 manifest 批量调用：
    - `openclaw infer video describe --file <mp4> --model google/gemini-3-flash-preview --json`
  - 支持参数覆盖：
    - `--provider`
    - `--model`
    - `--limit`
    - `--force`
    - `--cache-dir`
    - `--continue-on-error`
  - 第一版可以只依赖 OpenClaw CLI，不直接接 Google API。
  - 加入缓存和幂等输出，避免重复分析同一个 MP4。
  - 已新增 batch runner、response fixture、fixture alignment gate：
    - `skills/autotiktok-topic-discovery/fixtures/video-describe-responses.sample.json`
    - `skills/autotiktok-topic-discovery/scripts/run_video_content_analysis_batch.py`
    - `skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_batch_runner.py`
    - `skills/autotiktok/scripts/validate_video_content_analysis_batch_runner_alignment.py`
  - runner 当前行为：
    - 默认从 `skills/autotiktok-topic-discovery/config/video-understanding.v1.json` 读取 `google/gemini-3-flash-preview`
    - 对 `downloaded` MP4 调用 OpenClaw CLI 或读取 response fixture / cache
    - 对 `download_missing`、`download_error`、`invalid_file` 生成结构化 fallback，不阻塞 metadata-only 主链路
    - 产物和 `videoContentAnalysis` focused fixture 保持 deterministic 对齐
- 开发包 4（已完成）：`videoContentAnalysis -> enriched signalItems`
  - 在现有 metadata-only synthetic `signalItems` 基础上做增强，不替换原始字段。
  - 重点增强：
    - `topicSummary`
    - `contentAngles`
    - `requiredAssets`
    - `executionNotes`
    - `recommendedFormats`
    - `expandabilityHint`
  - 新增 evidence 字段或 `rawMeta.videoContentAnalysisReference`，保留可追溯引用。
  - 当 MP4 分析缺失或失败时，自动回退阶段 7 的 metadata-only signal。
  - 已新增 focused base / enriched fixture、builder 和 gate：
    - `skills/autotiktok-topic-discovery/fixtures/signal-items.video-content-analysis-base.sample.json`
    - `skills/autotiktok-topic-discovery/fixtures/signal-items.enriched.sample.json`
    - `skills/autotiktok-topic-discovery/scripts/build_enriched_signal_items.py`
    - `skills/autotiktok-topic-discovery/scripts/validate_enriched_signal_items.py`
    - `skills/autotiktok/scripts/validate_enriched_signal_items_alignment.py`
  - 当前 fixture 覆盖：
    - 1 条 `analysis_succeeded`，增强 `topicSummary / contentAngles / requiredAssets / recommendedFormats / requiredCapabilities / expandabilityHint / executionNotes`
    - 1 条 `download_missing` fallback
    - 2 条 `analysis_failed` fallback，分别覆盖 download error 与 invalid file
  - 所有 enriched / fallback 项都写入 `rawMeta.videoContentAnalysisReference`，保留 `analysisId / videoSampleId / platformVideoId / sourceSnapshotId / provider / model / status`。
- 开发包 5（已完成）：discovery / ranking 联调
  - 跑通完整链路：
    - `trending output -> sourceSnapshots -> videoSamples -> download manifest -> videoContentAnalysis -> enriched signalItems -> discovery -> ranking`
  - 新增对比输出：
    - metadata-only `signalItems`
    - enriched `signalItems`
    - ranking result diff
  - 确保 enriched lane 不改变既有 contract，只增加可消费证据。
  - 已新增 focused integration gate：
    - `skills/autotiktok/scripts/validate_enriched_discovery_ranking_integration.py`
    - `skills/autotiktok/scripts/test_enriched_discovery_ranking_integration.py`
  - 当前 gate 会同时跑 metadata-only lane 和 enriched lane，并验证：
    - enriched lane 仍能通过 snapshot materialization 进入 discovery
    - ranking 仍消费 discovery artifact
    - candidate count 保持一致
    - 成功视频的 `topicSummary / executionProfile / rewrite score` 出现视频理解证据带来的差异
    - 3 条失败/缺失样本仍走 metadata-only fallback
- 开发包 6（已完成）：validator / docs / live-ish smoke 收口
  - 新增 focused validator，证明：
    - download manifest 和 videoSamples 可稳定 join
    - `videoContentAnalysis` artifact 可重复校验
    - enriched signalItems 可回退
    - discovery / ranking 可以消费 enriched lane
  - 新增小样本 live-ish 调试说明，用已下载 MP4 验证 `gemini-3-flash-preview` 链路。
  - 更新 skill 文档，明确模型配置方式、失败降级策略和成本控制边界。
  - 已新增 live-ish runbook 和 docs gate：
    - `skills/autotiktok-topic-discovery/references/video-understanding-live-smoke.md`
    - `skills/autotiktok-topic-discovery/scripts/validate_video_understanding_live_smoke_docs.py`
    - `skills/autotiktok/scripts/validate_video_understanding_live_smoke_docs_alignment.py`
  - runbook 明确默认先跑 deterministic gates；真实视频理解必须显式带 `--limit 1`、`--cache-dir`、`--continue-on-error` 和 `--output`，避免默认触发批量付费调用。
  - 已补齐 merged view 规则：当 `absolute_hot` 与 `fresh_hot` 同时进入 discovery / ranking 时，必须先下载并理解两个 view 的去重并集。
  - `autotiktok-video-download` 已支持 `--bakeoff-view both --per-view-max N`，用于 TopN absolute-hot + TopN fresh-hot 的合并下载，避免全局 `--max N` 只截取 absolute-hot 导致 `fresh_hot` 变成 `download_missing`。
  - 已新增 ranking report builder：`skills/autotiktok-topic-ranking/scripts/build_ranking_report.py` 会把 `ranking-dry-run.json`、`discovery-dry-run.json` 和 `video-content-analysis.json` join 起来，在排名分数总表中输出 `视频文件` 列，只展示本地 MP4 文件名。

完成标准：

- `videoSamples + download manifest` 可以稳定生成 `videoContentAnalysis`。
- 默认模型为 `google/gemini-3-flash-preview`，但可通过配置或 CLI 参数覆盖。
- MP4 缺失、模型失败、单条超时不会阻塞 metadata-only 主链路。
- enriched `signalItems` 保留阶段 7 的 provenance，并新增视频理解证据引用。
- discovery / ranking 能消费 enriched lane，并可和 metadata-only lane 做对比。

## 5. 建议执行顺序

当前阶段 1-8 已全部完成。下一步进入真实环境收口：把同事开发的真实 `autotiktok-trending` / `autotiktok-video-download` 产物和快照存储接到当前 enriched lane，并做小样本 live-ish 验证。

建议按下面顺序推进：

1. 已完成：定义 `videoContentAnalysis` contract 和 sample artifact
2. 已完成：对齐 `autotiktok-video-download` manifest 与 `videoSamples`
3. 已完成：接入 OpenClaw `infer video describe` batch runner，默认使用 `google/gemini-3-flash-preview`
4. 已完成：用多模态分析结果增强 synthetic `signalItems`
5. 已完成：跑 discovery / ranking enriched lane 联调
6. 已完成：validator / docs / live-ish smoke 收口
7. 已完成：merged absolute/fresh view 的下载与视频理解路由补强
8. 已完成：ranking report 总表补充下载后视频文件名
9. 下一步：和真实快照存储 / 长期 retention 接线，并跑真实小样本 live-ish 验证

## 6. 下一步直接执行内容

下一步优先执行：

- 真实环境收口：
  - 用同事的真实 `autotiktok-trending` 输出替换 focused fixture，跑 `build_discovery_inputs_from_trending.py`
  - 用真实 `autotiktok-video-download` 输出替换 focused download raw fixture，跑 `build_video_download_manifest.py`
  - 如需同时纳入 `fresh_hot`，用 `--bakeoff-view both --per-view-max N` 先下载两个 view 的去重并集，再进入 manifest 归一化
  - 按 `video-understanding-live-smoke.md` 先跑 `--limit 1` live-ish video understanding
  - 再跑 enriched lane integration，确认真实 `sourceSnapshots + videoSamples + signalItems + videoContentAnalysis` 能进入 discovery / ranking
  - 最后再接快照存储、retention 和真实目录约定
