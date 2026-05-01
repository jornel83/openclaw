# TikTok Trending 多源融合 PRD

## 文档状态

- 当前版本：v0.1
- 当前阶段：趋势信号层定义
- 文档定位：先定义最终可用的官方趋势信号层，再逐步迭代抓取、融合、排序、输出和 `SKILL.md`

## 背景

当前 `tiktok-trending` 的实现，本质上仍然是“从官方页面抽若干 hashtag token，再用 `TikTokApi` 按 hashtag feed 抓视频，再按互动指标排序”的方案。

这条链路的问题主要有三类：

- 趋势发现依赖整页文本正则抽取，容易混入页面噪声、UI token、泛词和 SEO 词。
- 趋势定义过度依赖 hashtag，无法表达 keyword、search intent、官方 trending video 等更高价值信号。
- 最终排序更像“高互动视频排序”，而不是“与当前 TikTok 真实趋势最相关的视频排序”。

因此，这个 PRD 的第一步不是直接改脚本，而是先把“趋势信号层”定义清楚：

- 哪些官方来源应当进入趋势信号层
- 每个来源的权威性、结构化程度、实时性、可抓取性如何
- 它们分别表达什么类型的趋势
- 最终哪些来源进入主信号层，哪些只做辅信号或弱参考

## 本阶段目标

本阶段只解决一个问题：

**确定 `tiktok-trending` 的最终趋势信号层。**

也就是先回答：

- TikTok 官方到底有哪些可用趋势来源
- 这些来源各自代表什么含义
- 最终我们应该采哪些，不应该采哪些
- 采到以后在系统里分别扮演什么角色

## 本阶段非目标

本阶段暂不展开：

- 候选视频召回细节
- 最终视频融合排序公式
- 脚本参数设计
- 输出 JSON schema 的最终定稿
- `SKILL.md` 的最终文案
- 浏览器抓取策略、代理、风控绕过等工程实现

这些放到后续迭代。

## 证据基础说明

当前结论主要来自以下几类可验证公开信息：

- TikTok Ads / Creative Center 官方帮助页搜索摘要
- TikTok 官方 Creative Center 页面搜索摘要
- TikTok Newsroom 公告页搜索摘要
- TikTok 主站 `discover/*` 趋势入口搜索摘要
- 仓库内已有调研记录 `topics_source.md`
- 仓库内现有实现与运行样例

说明：当前网络环境对直接读取 TikTok 页面存在超时，因此本版 PRD 依据官方搜索结果摘要和本地已有调研进行第一轮收敛。后续若能稳定直读页面，再补充字段级校验。

## 评估维度

为了避免“官方域名”和“官方趋势产品”混为一谈，本 PRD 用以下维度评估每个来源：

- **权威性**：是否属于 TikTok 明确定义的趋势/洞察产品，而不只是官方域名下的普通页面。
- **信号类型**：它表达的是 hashtag、keyword、search intent、video exemplar，还是年度宏观趋势。
- **结构化程度**：是否具备 region、industry、time frame、analytics 等结构化维度。
- **实时性**：更接近实时热点，还是更偏周/月/季度趋势。
- **可抓取性**：是否可能形成稳定 extractor，还是更容易退化成噪声文本抓取。
- **实操价值**：对“找到值得抓的热门视频”是否真的有帮助。
- **在系统中的角色**：主信号、辅信号、弱参考、或排除。

## 官方趋势来源逐项分析

### 1. Creative Center Trends - Hashtags

- 代表入口：`https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en`
- 官方描述要点：搜索摘要显示它属于 Creative Center 的 Trends / Trend Discovery 体系，支持查看 trending hashtags，并可结合 region、industry、time frame 和 analytics 使用。
- 信号类型：显式 hashtag 趋势信号。

#### 权威性判断

这是 TikTok 官方趋势产品的一部分，不只是一个主站 discover 落地页。它的权威性高于普通 `tiktok.com/discover/*` 页面，因为它明确属于 TikTok For Business 的趋势洞察产品。

#### 信号价值

它能告诉我们：

- 创作者正在显式贴什么标签
- 哪些标签已经进入较广泛的传播状态
- 某些行业或地区的 hashtag 热度分布

它特别适合做：

- 主题别名发现
- hashtag 召回入口
- topic 的外显标签集合

#### 结构化程度

较强：

- 地区
- 行业
- 时间窗
- analytics / trendline / audience insights / related videos 等信号摘要

#### 局限

- hashtag 是创作者显式声明的标签，不等于用户真正关心的主题。
- hashtag 很容易被蹭热度、乱贴标签、营销污染。
- 某些真实趋势先体现在搜索和视频表达上，而不是先体现在 tag 上。
- 当前仓库样例里对该页的正则抽取质量很差，甚至出现 `#nprogress` 这类页面噪声，说明不能再用整页正则扫的方式处理该源。

#### 结论

- **纳入最终趋势信号层**
- **角色：二级主信号**
- **用途：topic alias / hashtag recall / trend corroboration**
- **不能单独主导 topic 定义**

### 2. Creative Center Trends - TikTok Videos

- 代表入口：Creative Center Trends 体系中的 TikTok Videos 页面
- 官方描述要点：搜索摘要显示 Trends 包含 trending TikTok videos，且与 hashtags、songs、creators 并列。
- 信号类型：官方 trending video exemplar 信号。

#### 权威性判断

属于 Creative Center Trends 主产品的一部分，权威性高。

#### 信号价值

这是最接近“我们到底想抓什么”的官方信号之一，因为最终目标不是做 hashtag 榜，而是抓出值得看的热门视频。

它能直接提供：

- 当前趋势是通过什么视频表达出来的
- 哪些视频已经被 TikTok 的趋势产品视为代表性内容
- 反推 caption、话题表达方式、共现 hashtags、创作者模式

#### 结构化程度

中高：

- 通常会有地区、行业、趋势入口上下文
- 不一定像 keyword 或 hashtag 那样天然结构化，但它对下游视频召回价值极高

#### 局限

- video seed 更像 exemplars，不一定天然带出统一 topic 名称。
- 如果只抓 video seed，不做 topic 聚类，最后容易退化成“热视频样例集合”。
- 需要后续 topic normalization，把多个 seed video 反推成统一主题实体。

#### 结论

- **纳入最终趋势信号层**
- **角色：一级主信号**
- **用途：seed video / exemplar / relevance calibration**
- **这是最终热门视频方案不可缺少的一层**

### 3. Creative Center Trends - Creators

- 代表入口：Creative Center Trends 体系中的 Creators 页面
- 官方描述要点：搜索摘要显示 Trends 包含 trending creators。
- 信号类型：创作者趋势信号。

#### 权威性判断

权威性高，因为属于同一套官方趋势产品。

#### 信号价值

它表达的不是“主题是什么”，而是：

- 哪些创作者正在承接或放大当前趋势
- 哪些创作者是某类趋势的重要传播节点

它对下游价值在于：

- 识别 trend carrier
- 防止一个 topic 被单个大号完全劫持
- 用于 creator diversity / per-author-limit 的更智能设计
- 在多源融合中辅助判断某个 topic 是否只是被少数号推动

#### 局限

- creator 不是 topic，本身不能直接定义趋势主题。
- 如果把 creator 直接当作 topic signal，会把“谁在火”和“什么在火”混淆。
- 更适合做 topic 的辅助上下文，不适合作为主 topic seed。

#### 结论

- **纳入最终趋势信号层**
- **角色：辅助信号**
- **用途：topic context / creator diversity / anti-domination / corroboration**
- **不参与主 topic 命名**

### 4. Creative Center Trends - Songs

- 代表入口：Creative Center Trends 体系中的 Songs 页面
- 官方描述要点：搜索摘要显示 Trends 包含 songs，并支持按趋势使用。
- 信号类型：音频趋势信号。

#### 权威性判断

同属官方趋势产品，权威性高。

#### 信号价值

在 TikTok 上，大量趋势先以音频模板、背景音乐、声音 meme 的形式传播。很多 trend 在 hashtag 还不稳定时，song 或 sound 已经成为传播骨架。

它对系统的意义：

- 识别“表达模板型趋势”
- 识别某一类视频为什么会一起爆
- 后续如果有音频字段或可替代代理字段，可用于 topic 聚类和视频相关性增强

#### 局限

- 当前现有脚本并没有音频维度处理能力。
- 公共抓取时未必都能稳定拿到结构化音频字段。
- song signal 对“直接抓热视频”的贡献，短期不如 keyword、search、video direct。

#### 结论

- **纳入最终趋势信号层**
- **角色：辅助信号**
- **用途：template detection / trend clustering / secondary corroboration**
- **第一期可先建接口，第二期再真正用起来**

### 5. Creative Center Keyword Insights

- 代表入口：`https://ads.tiktok.com/business/creativecenter/keyword-insights/pc/en`
- 官方描述要点：搜索摘要显示它是 Creative Center 下的 Keyword Insights，关键词来源于 TikTok 内容中的 voice-over、text、caption 等内容，并提供 trending keywords。
- 信号类型：关键词 / 语义主题信号。

#### 权威性判断

这是官方洞察产品，不只是普通聚合页。虽然它和 Trends 不完全同页，但从产品定位看，它属于 TikTok 官方的创意与趋势洞察体系。

#### 信号价值

这是整个趋势信号层里最重要的来源之一，因为它比 hashtag 更接近“主题本身”。

它提供的是：

- 用户和内容实际围绕什么词表达
- 哪些语义关键词在上升
- 哪些关键词可能是视频脚本、字幕、口播、标题中的核心表达

对“抓热门视频”来说，keyword 比 hashtag 更接近真正的 topic core。

#### 结构化程度

通常较强：

- keyword 本身就是结构化字段
- 可能带时间窗、搜索或相关性上下文
- 更适合做 normalization 和 topic merge

#### 局限

- keyword 可能比 hashtag 更碎片化，需要更强的归一化和聚类。
- 某些关键词是内容表达词，不一定等于独立 trend。
- 如果没有上下文，keyword 可能比 hashtag 更需要合并同义词与短语。

#### 结论

- **纳入最终趋势信号层**
- **角色：一级主信号**
- **用途：topic naming / topic normalization / semantic relevance**
- **这是后续 topic entity 的核心锚点之一**

### 6. Creator Search Insights

- 代表入口：
  - `https://www.tiktok.com/discover/creator-search-insights`
  - `https://newsroom.tiktok.com/en-us/creator-search-insights`
  - `https://support.tiktok.com/en/using-tiktok/growing-your-audience/creator-search-insights`
- 官方描述要点：从官方 Newsroom 与产品入口可以确认这是 TikTok 面向创作者的搜索洞察工具。
- 信号类型：创作者选题导向的搜索/需求信号。

#### 权威性判断

权威性高。它不是普通 discover 聚合页，而是 TikTok 明确命名的产品/功能。

#### 信号价值

这是和 Keyword Insights 并列的高价值来源，原因是它更接近“用户想搜什么、创作者应该做什么”。

它表达的不是单纯热门标签，而是：

- 用户主动搜索的主题需求
- 可能存在内容缺口的话题
- 适合创作者切入的搜索型选题

这类信号对热门视频抓取特别重要，因为它能帮助区分：

- 只是创作者在推的内容
- 用户真的在寻找的内容

#### 结构化程度

中高：

- 通常会以 query 或 topic card 的形式表达
- 对 keyword/topic merge 很友好
- 可能具备一定趋势排序或搜索导向排序

#### 局限

- 它面向创作者选题，不完全等同于“全平台热视频榜”。
- 更偏需求侧，不一定能单独反映传播强度。
- 需要和 trending videos / hashtags 联合使用，才能形成更完整的趋势闭环。

#### 结论

- **纳入最终趋势信号层**
- **角色：一级主信号**
- **用途：search intent / topic demand / query expansion / content gap awareness**
- **它和 Keyword Insights 应该共同构成趋势主题定义的主轴**

### 7. Trending Searches

- 代表入口：`https://www.tiktok.com/discover/trending-searches`
- 官方描述要点：搜索摘要显示它展示 top trending searches，强调“people are talking about and searching for globally”。
- 信号类型：平台搜索热度信号。

#### 权威性判断

官方域名无疑是官方，但从产品化程度看，它介于“正式搜索趋势入口”和“主站 discover 流量页”之间。比 Creative Center 与 Creator Search Insights 稍弱，但仍然比普通 discover 热词页更接近真实需求信号。

#### 信号价值

它直接表达：

- 用户在搜什么
- 哪些 query 已经具有平台级关注度

它的价值高于普通 discover hashtag 页，因为 search 是主动需求，不只是内容被动曝光。

#### 结构化程度

中等：

- query 本身较清晰
- 但页面可能更偏展示，不一定像 Creative Center 那样天然有稳定结构化 analytics

#### 局限

- 可抓取性和结构稳定性可能不如 Creative Center 产品页。
- 结果可能受地域、登录态、页面形态变化影响。
- 需要防止它退化成主站 discover SEO 页面。

#### 结论

- **纳入最终趋势信号层**
- **角色：二级主信号 / 强辅信号**
- **用途：search corroboration / query trend boosting / demand validation**
- **优先级低于 Keyword Insights 和 Creator Search Insights，但高于普通 discover 页**

### 8. TikTok 主站 Discover 泛趋势页

- 代表入口：
  - `https://www.tiktok.com/discover/trending-topics?lang=en`
  - `https://www.tiktok.com/discover/whats-trending-now`
  - 以及类似 `trending-keywords`、`tiktok-trends`、`top-trending` 等 discover 落地页
- 信号类型：泛趋势内容聚合 / 搜索承接页。

#### 权威性判断

这些页面位于 TikTok 官方域名下，当然是官方页面；但这不等于它们是官方趋势产品。相比 Creative Center、Keyword Insights、Creator Search Insights，它们更像：

- 对外流量入口
- 内容聚合页
- SEO 承接页
- 面向普通用户的 discover 展示页

因此，它们的“官方域名权威性”不能等同于“趋势数据产品权威性”。

#### 信号价值

它们仍然有一定价值：

- 能看到平台目前对外显露的热词与热内容表达
- 能提供弱 topic seed
- 有时能提供 discover 命名词和趋势表达方式

#### 局限

这是当前系统误判最多的来源之一：

- 页面文本混杂，极易抽出无效 token
- 可能有泛词、SEO 词、噪声词
- 排序逻辑不透明
- 很难作为最终 topic 主定义依据
- 容易把内容聚合页误当成趋势数据库

当前仓库中把这两页当 primary sources，会导致：

- topic 粒度过粗
- 泛词过多
- 页面噪声误入 topic 集合

#### 结论

- **保留，但降级**
- **角色：弱参考 / 补充发现源**
- **用途：补充 alias / 页面表达补全 / 边缘 topic 弱证据**
- **不得再作为 primary source 主导 topic 排序**

### 9. TikTok Newsroom Trend Reports

- 代表入口：
  - `What's Next 2024 Trend Report`
  - `TikTok What's Next 2025 Trend Report`
- 信号类型：年度 / 季度宏观趋势报告。

#### 权威性判断

极高。这是 TikTok 官方对平台趋势的正式总结与对外发布。

#### 信号价值

它对产品设计有帮助，但不适合直接进入实时抓取主链路。

它最适合：

- 定义长期 topic taxonomy
- 理解大类趋势框架
- 做行业词表和主题分类先验
- 辅助解释为什么某类话题会在当期上升

#### 局限

- 时间粒度太粗
- 不服务于“这几小时/这几天有什么热视频”
- 不能直接做在线 topic seed

#### 结论

- **不进入在线趋势信号层主链路**
- **角色：离线参考 / taxonomy reference**
- **可用于词表、类目、分析报告，不用于实时发现**

## 官方来源最终分层

### A. 一级主信号

这些来源直接参与 `TrendTopic` 定义，是趋势主题层的核心输入。

#### A1. Creative Center Keyword Insights

- 原因：最接近主题语义本体
- 作用：topic naming、semantic clustering、query expansion

#### A2. Creator Search Insights

- 原因：最接近用户主动需求和创作者选题空间
- 作用：search intent、demand-side validation、content gap signal

#### A3. Creative Center Trending Videos

- 原因：直接给出代表性 trending video exemplars
- 作用：seed videos、trend expression pattern、relevance calibration

### B. 二级主信号

这些来源不单独定义 topic 核心语义，但对 topic 合并、增强和验证非常重要。

#### B1. Creative Center Trending Hashtags

- 原因：显式、稳定、结构化，适合召回和别名
- 作用：alias、hashtag recall、topic corroboration

#### B2. Trending Searches

- 原因：接近用户需求，但产品稳定性和结构化略弱于 Keyword / CSI
- 作用：query trend boosting、demand validation、search corroboration

### C. 辅助信号

这些来源保留，但不主导 topic 命名。

#### C1. Creative Center Trending Creators

- 作用：creator diversity、trend carrier、anti-domination、topic context

#### C2. Creative Center Trending Songs

- 作用：template / sound trend、trend clustering、secondary corroboration

### D. 弱参考信号

#### D1. 主站 Discover 泛趋势页

- 作用：补充 alias、补充对外表达、边缘发现
- 约束：不得作为 primary ranking source，不得单独决定 topic

### E. 离线参考层

#### E1. Newsroom Trend Reports

- 作用：taxonomy、长期策略、行业词表
- 约束：不参与在线趋势发现与实时视频召回

## 最终趋势信号层定义

基于以上分析，`tiktok-trending` 的最终趋势信号层定义如下。

### 1. 信号层总体结构

趋势信号层由五层组成：

- **语义主题层**：Keyword Insights、Creator Search Insights
- **代表视频层**：Creative Center Trending Videos
- **显式标签层**：Creative Center Trending Hashtags
- **需求验证层**：Trending Searches
- **辅助上下文层**：Creators、Songs、Discover 泛趋势页

### 2. 主 Topic 定义原则

任何一个最终 `TrendTopic` 必须优先由以下三类主锚点中的至少一种触发：

- keyword anchor
- search-intent anchor
- trending-video anchor

这意味着：

- **纯 hashtag topic 不再允许直接成为最终 topic**，除非它能被 keyword、search 或 seed video 佐证。
- **discover 页抽到的 token 不再允许直接成为最终 topic**，只能作为弱别名或低权重补充信号。

### 3. 各信号在系统中的角色

- **Keyword Insights**：提供 topic 主名称候选与语义中心
- **Creator Search Insights**：提供用户需求与创作者切入方向
- **Trending Videos**：提供趋势表达样例与 seed video
- **Trending Hashtags**：提供显式标签别名与召回入口
- **Trending Searches**：提供搜索热度验证
- **Creators**：提供传播者上下文
- **Songs**：提供模板传播上下文
- **Discover 泛趋势页**：提供弱补充和 alias，但不再主导
- **Newsroom Reports**：只做离线参考

## 对当前仓库实现的直接结论

结合当前实现，趋势信号层的第一轮改造方向已经明确：

### 1. 现有 primary source 定义需要重写

当前 `skills/tiktok-trending/scripts/crawl-official-categories.py` 中的 `OFFICIAL_SOURCE_SPECS` 把两个主站 discover 页和一个 hashtag 页面放在同一层级，这个设计需要重写。

新设计应改为按信号层级定义 sources，而不是按页面列表平铺。

### 2. 当前 `discover/* -> hashtag token` 主链路必须降级

现有“从 discover 页正则抽 hashtag token”的方式只能保留为弱参考链路，不能再作为主 topic discovery。

### 3. topic 模型必须替代 category 模型

现有 `category_id/category_name/query_value` 的模型太偏 hashtag，应升级为可承载：

- keywords
- search queries
- hashtags
- seed videos
- creator signals
- song signals

的 `TrendTopic` 模型。

### 4. 趋势信号层先于抓取层重构

在没把信号层重构清楚前，不应继续扩展抓取逻辑，否则只会把当前 hashtag-only 偏差扩散到更多数据上。

## 第一版最终结论

本 PRD 第一轮收敛后的最终结论是：

- `tiktok-trending` 的最终趋势信号层，不应再由 `discover/*` 页面主导。
- 最终应采用 **Keyword + Creator Search Insights + Trending Videos** 作为一级主信号。
- 采用 **Trending Hashtags + Trending Searches** 作为二级主信号。
- 采用 **Creators + Songs** 作为辅助上下文信号。
- 采用 **Discover 泛趋势页** 作为弱参考信号。
- 采用 **Newsroom Trend Reports** 作为离线参考层。

换句话说，新的趋势信号层不是“hashtag 榜单系统”，而是：

**以语义主题、搜索需求、代表视频为核心，以 hashtag 和 search 进行增强验证的官方多源趋势系统。**

## 对照实验方案 v0

为了避免继续凭直觉在 `topic-first` 与 `direct-hot` 之间做选择，仓库内先落地一个最小可执行 bake-off。

### 目标

这个对照实验不是为了最终定稿排序模型，而是为了先回答三个问题：

- 哪条路线更容易稳定拿到“绝对热门”的视频
- 哪条路线更适合后续做分析与下载
- `topic-first` 是否真的带来了额外价值，还是只是增加了筛选成本

### 当前纳入的路线

第一版对照实验先比较两条路线：

- `topic-first`
  - 复用现有 `scripts/crawl-official-categories.py`
  - 仍然代表“先发现官方 category/topic，再按 category/topic 抓热视频”的路径
- `direct-hot`
  - 新增 `TikTokApi trending feed` 路线
  - 代表“直接抓平台最热视频，再做后续比较”的路径

### 脚本入口

- `skills/tiktok-trending/scripts/bakeoff.py`

### 第一版脚本职责

`bakeoff.py` 当前负责：

- 统一执行 `topic-first` 与 `direct-hot` 两条路线
- 使用相同时间窗、region、per-author-limit 和 min-likes 阈值
- 将两条路线产出的结果统一成同一种 JSON 结构
- 计算每条路线的基础 summary
- 计算 top-N overlap，帮助判断两条路线抓到的是不是同一批视频

### 当前统一输出的核心字段

每条路线当前至少输出：

- `route_id`
- `route_label`
- `status`
- `raw_candidates_seen`
- `eligible_candidates`
- `summary`
- `videos[]`

每个视频当前尽量统一到以下字段：

- `video_id`
- `url`
- `author`
- `create_time`
- `view_count`
- `like_count`
- `comment_count`
- `share_count`
- `engagement`
- `age_hours`
- `hot_score`
- `source_ids`
- `source_labels`
- `matched_categories`
- `route_rank`

### 当前 summary 指标

为了先做第一轮方向判断，脚本当前先计算以下可直接比较的指标：

- `retained_videos`
- `unique_authors`
- `unique_top_authors`
- `median_view_count`
- `median_like_count`
- `median_comment_count`
- `median_share_count`
- `median_engagement`
- `median_hot_score`
- `median_age_hours`

这些指标足够先做第一轮判断：

- `direct-hot` 是否真的更热
- `topic-first` 是否更分散或更聚焦
- 两条路线的 top-N 是否高度重叠

### 当前不做的事情

第一版 bake-off 还没有覆盖：

- Apify 路线
- Research API 路线
- replicability 专项评分
- 音频、字幕、脚本结构等更贴近 AI 复刻的深分析
- 自动下载与视频内容分析

这些放到后续迭代。

### 运行示例

同时跑两条路线：

```bash
python3 {baseDir}/scripts/bakeoff.py \
  --window 24h \
  --topic-category-limit 8 \
  --topic-per-query 50 \
  --topic-per-category 10 \
  --direct-count 100 \
  --direct-keep 50 \
  --top-n 20 \
  --out /tmp/tiktok-bakeoff.json
```

只跑 `direct-hot`：

```bash
python3 {baseDir}/scripts/bakeoff.py \
  --route direct-hot \
  --window 24h \
  --direct-count 100 \
  --direct-keep 50 \
  --out /tmp/tiktok-direct-hot.json
```

只跑 `topic-first`：

```bash
python3 {baseDir}/scripts/bakeoff.py \
  --route topic-first \
  --window 24h \
  --topic-category-limit 8 \
  --topic-per-query 50 \
  --topic-per-category 10 \
  --out /tmp/tiktok-topic-first.json
```

### 第一轮判定标准

第一轮先不求“最终 AI 复刻打分”完全正确，而是先回答：

- `direct-hot` 的 `median_view_count`、`median_engagement` 是否显著高于 `topic-first`
- `topic-first` 的 top-N 是否只是 `direct-hot` 的一个小子集
- 两条路线是否命中大量不同视频
- `topic-first` 是否在保留热视频之外，提供了更高的 category/topic 解释价值

如果第一轮结果显示：

- `direct-hot` 明显更热，且 overlap 低
  - 说明主路线应优先转向 `direct-hot`
- `topic-first` 抓到的视频虽然不一定最热，但明显更适合分析
  - 说明后续要保留它作为补充路线
- 两者各有优势
  - 说明最终方案应演化为 hybrid

### 预期下一步

在 bake-off 第一轮跑通后，下一步需要继续补：

- replicability 维度
- 下载成功率维度
- caption / hashtag / sound 完整率维度
- 更贴近 AI 复刻的结构化分析指标

### 首轮 smoke run 结果

仓库内已经完成第一轮小样本 smoke run，输出文件位于：

- `.openclaw/tiktok-bakeoff-smoke.json`

本轮运行参数：

- `window=24h`
- `topic-category-limit=3`
- `topic-per-query=20`
- `topic-per-category=5`
- `direct-count=30`
- `direct-keep=15`
- `top-n=10`

#### 结果概览

- `topic-first`：`status=empty`
- `direct-hot`：`status=empty`

这不是“脚本没跑通”，而是：

- bake-off 已成功产出统一 JSON 结果
- 两条路线都在过滤阶段或候选阶段暴露出当前设计问题

#### 对 `topic-first` 的观察

当前 `topic-first` 路线的问题已经被首轮运行再次验证：

- official discovery 仍然以 `#tiktok`、`#animals`、`#animalcare` 这类泛 topic 为主
- Creative Center hashtag 抽取仍然出现 `#nprogress` 这类噪声 token
- 在 `24h` 窗口和当前默认 `min_likes=10000` 阈值下，这些 topic 全部返回 `no_results`
- 运行中还触发了 TikTokApi 风控回退，从 headless 切到 headful

这说明：

- 当前 `topic-first` 不只是“结果弱”，而是它的 topic discovery 本身就在输出低价值 topic
- 即使路由本身能跑，现有 discover->hashtag 设计也无法代表真实热点视频入口

#### 对 `direct-hot` 的观察

`direct-hot` 路线这次成功拿到了 30 个 raw candidates，但全部被过滤掉。当前最关键的诊断结果是：

- `missing_video_id = 1`
- `missing_or_old_create_time = 29`
- `accepted = 0`

这说明现阶段 `TikTokApi trending feed` 返回的对象里，至少在当前环境下：

- 很大一部分对象不能直接按“普通短视频 item”处理
- `create_time` 提取逻辑与这条 route 的实际对象类型不匹配
- 命令输出中出现了明显的流媒体 URL / stream 配置字段，说明 trending feed 至少混入了非标准短视频对象

这意味着：

- `direct-hot` 路线依然值得保留
- 但它不能直接复用 hashtag route 的 item 提取与过滤逻辑
- 需要为 `direct-hot` 增加更强的 candidate type 识别与 route-specific extraction

#### bake-off 脚本已根据本轮结果做的调整

为避免“一个 route 失败拖垮整个实验”，以及让下一轮结果可解释，`scripts/bakeoff.py` 已做以下改造：

- `topic-first` route 失败时不再中断整个 bake-off
- 新增 route 级 `error` 输出
- 新增 `filter_diagnostics`
- 将 `direct-hot` 的过滤逻辑拆成显式分类步骤，而不是黑盒 `build_entry` 失败后直接丢弃
- 新增 `live_or_stream` 类型诊断入口，用于后续识别 trend feed 中的非普通视频对象

#### 本轮结果对最终路线选择的启发

首轮 smoke run 还不足以直接宣判哪条路线胜出，但已经足以明确：

- 当前仓库里的 `topic-first` 不能作为“绝对热门视频获取”的可靠主路线
- `direct-hot` 不是没有潜力，而是当前抽取逻辑还不对
- 下一步最值得投入的不是继续优化旧的 discover hashtag 抽取，而是优先把 `direct-hot` 路线的数据对象识别和提取逻辑做对

#### 下一步工程方向

基于这轮结果，下一步优先级调整如下：

- **P1**：给 `direct-hot` 增加更细的 rejection preview 与 candidate type 诊断
- **P1**：为 `direct-hot` 建立 route-specific extractor，而不是完全复用 hashtag item 结构
- **P2**：重新评估 `topic-first` 的默认阈值与用途，必要时把它降级为解释型/补充型路线
- **P2**：将 Creative Center / discover 的 topic discovery 与最终热门视频抓取主链路进一步解耦

### direct-hot 修复后的第二轮结果

在继续修正 `scripts/bakeoff.py` 后，已经完成第二轮 smoke run。当前最重要的变化是：

- `direct-hot` 已从 `status=empty` 变为 `status=ok`
- 当前 smoke run 中 `direct-hot` 成功保留了 `8` 条有效视频

#### 本轮修复点

为让 `direct-hot` 至少能留下有效视频，当前实现增加了 route-specific 的软时间窗策略：

- 先按请求窗口严格过滤
- 若结果为 0，则回退到 `30d`
- 若仍为 0，则再回退到 `any age`

对应输出字段为：

- `age_window_mode`

第二轮结果中，`direct-hot` 的 `age_window_mode` 为：

- `fallback_30d`

这说明在当前环境里，TikTokApi trending feed 里的“绝对热门”视频大多不是 24 小时内的新视频，而更像是近几周内持续强势传播的视频。

#### 第二轮关键观测

`direct-hot` 当前保留下来的候选呈现出以下特点：

- `eligible_candidates = 8`
- `median_view_count = 2,900,000`
- `median_like_count = 95,100`
- `median_engagement = 199,068.5`
- `median_age_hours = 453.843`

这进一步验证：

- 对 `direct-hot` 而言，时间窗更适合作为“偏好”而不是“硬门槛”
- 若目标是抓“绝对热门视频”，平台 trending feed 提供的很多高热视频本身就不是超短时窗爆发项

#### 这对最终方案的意义

第二轮 smoke run 已经足以说明：

- `direct-hot` 是一条可修通的主路线
- 当前最合理的定位是：
  - `direct-hot` 负责先抓全局热门视频
  - `topic-first` 暂时不承担热门视频主召回职责
- 之后应该围绕 `direct-hot` 继续补：
  - replicability 过滤
  - 下载与分析完整度
  - sound / caption / hashtag 的后处理 enrichment

#### 当前阶段性结论

截至第二轮 smoke run：

- `topic-first` 仍然没有证明自己适合作为“绝对热门视频抓取”主路线
- `direct-hot` 已经证明自己可以通过 route-specific 提取逻辑拿到有效热门视频
- 因此，下一步应明确把 `direct-hot` 作为主召回路线继续迭代

### direct-hot 作为 hot recall 主线的当前实现

在进一步收窄目标后，当前阶段不再把“是否适合 AI 复刻”作为召回阶段约束，而是先专注于：

- 抓到更多 `absolute_hot` 视频
- 同时保留一份 `fresh_hot` 排名切片

当前 `scripts/bakeoff.py` 中的 `direct-hot` 已具备以下能力：

- 直接从 TikTokApi trending feed 拉取 raw candidates
- 支持多批次 trending feed 采样
- 支持 batch 间去重统计
- 对 `direct-hot` 单独做 route-specific candidate 解析
- 在请求窗口无结果时，回退到 `30d`，必要时再回退到 `any age`
- 输出双榜：
  - `videos` = `absolute_hot`
  - `fresh_hot_videos` = `fresh_hot`
- 输出 hot recall 诊断：
  - `candidate_age_distribution`
  - `retained_age_distribution`
  - `rejection_preview`
  - `sampling.batch_reports`
  - `sampling.sampling_strategy`

#### absolute_hot / fresh_hot 的当前语义

- `absolute_hot`
  - 更偏向全平台绝对强势传播的视频
  - 更看重播放、互动、分享总量，以及整体 engagement 强度
- `fresh_hot`
  - 更偏向相对更新、仍在快速传播的视频
  - 更看重 velocity 与 freshness，同时仍保留 exposure / engagement 约束

当前这两个榜单都只服务于“更好地抓热门视频”，尚未叠加任何 AI 复刻相关筛选。

### direct-hot-only 最新 smoke run 结果

本轮只跑 `direct-hot`，参数为：

- `window=24h`
- `direct-count=50`
- `direct-batches=2`
- `direct-keep=20`
- `top-n=10`

输出文件：

- `.openclaw/tiktok-bakeoff-direct-hot.json`

#### 最新结果概览

- `status = ok`
- `age_window_mode = fallback_30d`
- `raw_candidates_seen = 60`
- `raw_candidates_unique_ids = 42`
- `eligible_candidates = 9`
- `fresh_hot_summary.retained_videos = 9`

这说明：

- 多批次采样确实扩大了 `direct-hot` 的 raw candidate 覆盖
- 即使请求参数是 `24h`，当前平台 trending feed 仍主要返回近 `30d` 的强热视频
- `fresh_hot` 不是“24 小时内热视频榜”，而是当前候选集合里“相对更新、传播更快”的那一层

#### 最新诊断结论

这轮结果中：

- `candidate_age_distribution.lte_30d = 10`
- `candidate_age_distribution.gt_30d = 48`
- `retained_age_distribution.lte_30d = 9`
- `retained_age_distribution.gt_30d = 0`

这说明当前最主要的召回限制仍然不是 likes threshold，也不是 live 过滤，而是：

- TikTokApi trending feed 的候选总体偏老
- 真正落入近 `30d` 的候选比例仍然偏低

换句话说，`direct-hot` 现在已经可以把“近一个月内仍然非常热”的视频抓出来，但还没有证明它能稳定抓到大量“超新鲜”的爆发项。

#### 采样层的现实结论

这一轮还发现：

- `headless` 模式下有可能出现空 trending feed
- 自动切到 `headful` 后恢复正常
- 较大的单批请求在当前环境下也不稳定，因此实现里增加了更保守的 batch size 回退

因此，当前 `direct-hot` 的 hot recall 主线已经形成一个比较明确的策略：

- 先尽量扩大 trending feed 采样面
- 再通过 `absolute_hot` / `fresh_hot` 双榜切出两种热门视角
- 通过 age distribution 与 rejection preview 判断采样层、时间窗、排序层分别卡在哪里

### direct-hot 参数扫面结果

为了判断当前 trending feed 的最佳采样方式，又补跑了几组 `direct-hot` only 参数：

- `.openclaw/tiktok-sweep-b3-p1.json`
  - `direct-count=30`
  - `direct-batches=3`
  - `direct-batch-pause-seconds=1.0`
- `.openclaw/tiktok-sweep-b5-p2.json`
  - `direct-count=30`
  - `direct-batches=5`
  - `direct-batch-pause-seconds=2.0`
- `.openclaw/tiktok-sweep-c100-b3-p1.json`
  - `direct-count=100`
  - `direct-batches=3`
  - `direct-batch-pause-seconds=1.0`

#### 参数扫面核心结果

- `b3,p1`:
  - `raw_candidates_seen = 90`
  - `raw_candidates_unique_ids = 65`
  - `eligible_candidates = 15`
  - `session_mode_effective = headless`
  - `sampling_strategy = requested_batches`
- `b5,p2`:
  - `raw_candidates_seen = 150`
  - `raw_candidates_unique_ids = 65`
  - `eligible_candidates = 17`
  - `session_mode_effective = headless`
  - `sampling_strategy = requested_batches`
- `c100,b3,p1`:
  - `raw_candidates_seen = 90`
  - `raw_candidates_unique_ids = 57`
  - `eligible_candidates = 14`
  - `session_mode_effective = headful`
  - `sampling_strategy = safe_batch_size_retry_30`

#### 参数扫面后的结论

- 当前环境下，`direct-count=30` 比 `direct-count=100` 更稳
- `direct-batches=3` 已经把 unique coverage 拉到当前观测上限附近
- 从 `3` 批继续加到 `5` 批，没有继续提升 `raw_candidates_unique_ids`
- `b5,p2` 只是在重复池里多拿到了一些额外候选，并没有扩大 candidate universe
- `count=100` 没有提升覆盖，反而更容易触发回退到保守 batch size，并让 effective session 退化成 `headful`

目前最合适的默认采样参数可以先收敛到：

- `direct-count = 30`
- `direct-batches = 3`
- `direct-batch-pause-seconds = 1.0`

这组参数的现实含义不是“它一定最好”，而是：

- 在当前账号 / session / 网络环境下，它是稳定性与 unique coverage 的最好平衡点
- 在还没有引入更多 session diversification 之前，继续单纯增加 batch 数的收益已经明显变小

#### absolute_hot / fresh_hot 双榜观察

对几组 sweep 结果做 top-10 overlap 后，得到：

- `.openclaw/tiktok-bakeoff-direct-hot.json`：`top10_overlap = 9`
- `.openclaw/tiktok-sweep-b3-p1.json`：`top10_overlap = 8`
- `.openclaw/tiktok-sweep-b5-p2.json`：`top10_overlap = 9`
- `.openclaw/tiktok-sweep-c100-b3-p1.json`：`top10_overlap = 9`

这说明当前双榜已经有轻微重排能力，但还没有形成两套明显分离的候选层：

- `absolute_hot` 与 `fresh_hot` 目前大多数时候仍然在重排同一批视频
- `fresh_hot` 的价值主要还是把候选池里相对更新、速度更快的项抬高一些
- 如果后续希望两榜真正分层，需要进一步扩大候选池里的年龄跨度和视频类型差异

### 下一步 hot recall 方向

在不引入 AI 复刻筛选的前提下，下一步最重要的是继续提升 `direct-hot` 的热门召回覆盖：

- 先把 `direct-count=30 / direct-batches=3 / pause=1s` 作为当前默认 sweep 基线
- 尝试 session diversification，而不是继续单纯增加 batch 数
- 测试不同 cookie / msToken / 代理条件下的 unique coverage 是否能突破当前 `~65` 的平台
- 如果要继续强化 `fresh_hot`，优先扩大“更年轻候选”的进入概率，而不是只在当前候选池内重排
- 必要时引入更稳定的 session / cookie / 代理采样方式，提升 trending feed 覆盖面

## 下一步待迭代问题

在这份 PRD 的下一轮迭代里，需要继续明确：

- `TrendTopic` 的最终数据结构
- 多源 topic merge 规则
- 候选视频召回层如何接这些信号
- 视频相关性分如何定义
- 最终热门视频排序公式如何设计
- 输出 JSON schema 如何演进
- `SKILL.md` 如何从“official category crawler”改成“multi-source trending video finder”
