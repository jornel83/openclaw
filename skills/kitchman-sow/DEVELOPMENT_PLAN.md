# Kitchman SOW Skill 开发计划

## 1. 目标

本文基于 `PRD.md` 和 `TECHNICAL_DESIGN.md`，细化 `kitchman-sow` demo v0.1 的开发计划。

v0.1 的目标不是实现完整图纸自动解析，也不是实现自动报价系统，而是打通客户可见的飞书演示闭环：

1. 用户在飞书中发起 SOW 请求并上传附件。
2. OpenClaw 触发 `kitchman-sow` skill。
3. Agent 基于附件、709 case reference、SOW schema 和 proposal template 生成结构化输出。
4. Skill 返回 SOW 摘要、`proposal.md`、`open-questions.md` 和 `sow-extraction.json`。
5. 用户继续在飞书中提出修正，skill 复用同一 `sow_id` 更新输出。

## 2. v0.1 开发原则

- `SKILL.md + references/` 优先，先完成可演示业务闭环。
- 文档理解由 agent 基于附件和 references 完成，不做 PDF/docx/OCR 重脚本。
- 不用规则匹配脚本硬编码图纸解析、room 识别、scope 抽取或自然语言修正。
- Python scripts 只做轻量、确定性的状态管理和输出校验。
- Demo 不接企业知识库、不生成最终报价、不做正式 docx/pdf 排版导出。

## 3. 阶段 1：Skill 骨架

目标是让 `kitchman-sow` 能被稳定触发，并让 agent 知道该读取哪些 reference、生成哪些输出。

交付物：

| 文件                               | 作用                                             |
| ---------------------------------- | ------------------------------------------------ |
| `SKILL.md`                         | Skill 入口、触发条件、核心工作流、边界说明       |
| `references/workflow.md`           | 飞书触发、生成、修正、追问流程                   |
| `references/feishu-integration.md` | 飞书触发识别、附件 intake、分层回复和 smoke test |
| `references/sow-schema.md`         | `sow-extraction.json` 字段结构                   |
| `references/proposal-template.md`  | `proposal.md` 输出结构                           |
| `references/review-guardrails.md`  | TBC、confidence、exclusion、禁止报价等审核约束   |
| `references/709-case-notes.md`     | 709 demo 案例结构化说明                          |

验收标准：

- 用户说“帮我出 709 项目的 SOW”时能触发该 skill。
- `SKILL.md` 保持精简，只做工作流和 reference 导航。
- Agent 能根据 references 明确需要输出 `sow-extraction.json`、`proposal.md`、`open-questions.md`。

## 4. 阶段 2：709 Demo 内容准备

目标是先做出客户能直观看到的 demo 效果。

交付物：

| 输出                                | 作用                       |
| ----------------------------------- | -------------------------- |
| `sow-extraction.json` 示例          | 展示结构化 SOW             |
| `proposal.md` 示例                  | 展示客户版 proposal        |
| `open-questions.md` 示例            | 展示待确认项               |
| 飞书摘要文案                        | 展示对话回复效果           |
| 3 条修正指令样例                    | 展示多轮修改能力           |
| `fixtures/709-demo/demo-runbook.md` | 客户演示步骤和质量评审清单 |

说明：

- v0.1 不写自动图纸解析脚本。
- 709 内容由 agent 根据附件、`references/709-case-notes.md`、SOW schema 和 proposal template 组织。
- 每条关键 scope、finish、exclusion、special note 应保留 `source_type`、`confidence` 或 evidence 说明。

验收标准：

- 能输出 709 项目的 room / area。
- 能输出 Kitchen、Pantry、Living、Laundry、WIR、Robe 等核心 scope。
- 能输出 open questions。
- 不生成最终价格。
- 不把低置信度内容写成确定承诺。

## 5. 阶段 3：SOW State Manager

目标是支持同一飞书会话里的多轮修改。

交付物：

| 文件                   | 作用                                                         |
| ---------------------- | ------------------------------------------------------------ |
| `scripts/sow_state.py` | 管理 `sow_id`、`sow-state.json`、workspace、revision history |

核心能力：

```text
resolve_sow_id
init_sow_state
load_sow_state
save_sow_state
append_revision
```

`sow_state.py` 不负责：

```text
不解析 PDF
不解析 docx
不做 OCR
不识别 room
不抽取 scope
不处理自然语言规则匹配
```

建议 workspace：

```text
<sow_workspace>/<sow_id>/
  sow-state.json
  input/
  intermediate/
  output/
    sow-extraction.json
    proposal.md
    open-questions.md
```

验收标准：

- 第一次生成能创建 `sow_id`。
- 后续修正能复用同一个 `sow_id`。
- 每次修正能记录到 `revision_history`。
- 输出文件路径能写回 `sow-state.json`。

## 6. 阶段 4：输出校验

目标是让 demo 输出更稳定，避免 agent 输出跑偏。

交付物：

| 文件                              | 作用                       |
| --------------------------------- | -------------------------- |
| `scripts/validate_sow_outputs.py` | 检查输出 artifact 是否合格 |

校验内容：

```text
sow-extraction.json 是否存在
proposal.md 是否存在
open-questions.md 是否存在
sow_id 是否存在
是否错误生成最终价格
open questions 是否为空
scope item 是否有 confidence/source_type
```

验收标准：

- 校验脚本能对 demo 输出给出 pass/fail。
- 失败时能指出缺少哪个文件或字段。
- 不对文档内容做业务理解，只做结构和安全约束校验。

## 7. 阶段 5：飞书交互接入

目标是让 demo 从本地输出变成飞书对话体验。

交付内容：

| 模块           | 作用                                                                |
| -------------- | ------------------------------------------------------------------- |
| 飞书触发语识别 | 判断是否进入 `generate_sow`                                         |
| 附件 intake    | 获取当前消息附件引用或本地路径                                      |
| 进度回复       | 告诉用户正在处理                                                    |
| 结果回复       | 返回摘要、关键 room preview、待确认项                               |
| 文件返回       | 返回 `proposal.md`、`open-questions.md`、`sow-extraction.json`      |
| 修正消息处理   | 复用 `sow_id`，更新 SOW JSON 和 proposal                            |
| Smoke 脚本     | 使用 `fixtures/709-demo/feishu-smoke-script.md` 验证演示路径        |
| Demo runbook   | 使用 `fixtures/709-demo/demo-runbook.md` 执行客户演示和输出质量评审 |

验收标准：

- 飞书消息能触发 skill。
- 能拿到附件或明确提示附件不可用。
- 能返回分层消息，而不是直接刷完整 proposal。
- 用户发修正指令后能更新输出。

## 8. 阶段 6：Demo 验收和打磨

目标是准备客户演示。

演示脚本：

```text
1. 用户发送 709 SOW 请求并上传附件。
2. Skill 回复任务确认。
3. Skill 输出附件识别摘要。
4. Skill 输出 SOW 摘要。
5. Skill 返回 proposal.md 和 open-questions.md。
6. 用户发送“Kitchen stone 全部排除”。
7. Skill 返回变更摘要和新版 proposal。
8. 用户发送“Pantry 门只写 cladding”。
9. Skill 再次更新输出。
```

验收标准：

- 全流程能在飞书里完成。
- 输出结构稳定。
- 不生成报价金额。
- 待确认项清晰。
- 用户能感知 skill 已经可以帮助起草 proposal。

## 9. 推荐开发顺序

```text
1. SKILL.md
2. references/sow-schema.md
3. references/proposal-template.md
4. references/review-guardrails.md
5. references/709-case-notes.md
6. 709 demo 输出样例
7. scripts/sow_state.py
8. scripts/validate_sow_outputs.py
9. 飞书触发和回复接入
10. 飞书多轮修正 smoke test
```

## 10. v0.1 不做范围

```text
不做 PDF/OCR 重脚本
不做 docx 深度解析脚本
不做规则匹配式 room/scope 抽取
不做规则匹配式自然语言修正
不接企业知识库
不生成最终报价
不做 docx/pdf 正式排版导出
```

## 11. 后续版本方向

v0.2 收尾优先保证 demo 稳定性：

- PDF 渲染 manifest 记录总页数、已渲染页数和未渲染页。
- `drawing-index.json` 记录页标题、drawing number 和 area title candidates，用于避免漏页。
- `outputs-status` 支持超时后复用已有输出，避免重复审图。
- `render_sow_outputs.py` 自动回填 `proposal_outputs`，确保 Feishu 摘要和文件列表一致。
- validator 检查 `feishu-summary.md`、截断渲染和输出一致性。

v0.2 后续可继续增强真实文档理解能力：

- PDF 页截图和 OCR。
- 真实 room / area 抽取。
- 图纸页和 room 自动关联。
- Evidence 展示增强。
- 多项目样本验证。

v0.3 可开始增强交付和迭代能力：

- 更强自然语言 revision。
- 简版 docx 输出。
- 当前会话内 revision history 展示。

v0.4 聚焦生成质量和客户交付可信度：

- 默认交付完整 ZIP 包，避免飞书或邮件漏附件。
- 提升 proposal 渲染质量，明确 confirmed scope、TBC items 和 exclusions 的边界。
- 提升 `sow-extraction.json` 数据质量，补足 evidence、page refs、drawing refs 和 validator 规则。
- 提升 DOCX 模板，使 Word 输出更接近人工 SOW 的正式客户文档。

## 12. v0.3 开发计划

v0.3 的目标是让 demo 从“能生成一版 SOW”升级为“能在飞书里继续修改并交付更正式的文件”。重点是迭代体验和交付格式，不扩大图纸自动理解范围。

### 12.1 Revision 能力

交付物：

| 文件                              | 作用                                                      |
| --------------------------------- | --------------------------------------------------------- |
| `references/revision-workflow.md` | 说明 revision 消息如何由 agent 修改 `sow-extraction.json` |
| `scripts/sow_state.py`            | 记录 revision metadata，不解释自然语言                    |

支持的 revision 类型：

```text
排除某项 scope
把某项改成 TBC
补充 scope item
修改 finish / hardware / exclusion
新增或关闭 open question
```

实现原则：

- Agent 读取用户 revision 原文和当前 `sow-extraction.json` 后更新结构化 JSON。
- 不写规则匹配脚本解释自然语言。
- 如果目标区域或 item 不明确，先追问，不猜。
- 修改后统一重新渲染输出文件。

验收标准：

- 用户发送“Kitchen stone 全部排除”后，相关内容进入 exclusions 或 TBC，不再作为确认 scope。
- 用户发送“Robe 2 finish 改 TBC”后，相关 finish 字段和 open question 能更新。
- 修改后输出文件重新生成，不重新分析整份 PDF。

### 12.2 Revision History

交付物：

| 字段             | 说明                                          |
| ---------------- | --------------------------------------------- |
| `revision_id`    | 递增 revision 编号                            |
| `timestamp`      | 修改时间                                      |
| `actor`          | 修改来源                                      |
| `message`        | 用户原话                                      |
| `summary`        | 本次修改摘要                                  |
| `change_type`    | scope / finish / exclusion / question / other |
| `affected_areas` | 影响区域                                      |
| `changed_files`  | 重新生成的文件                                |
| `output_version` | 当前输出版本                                  |

验收标准：

- 连续修改 3 次后，`sow-state.json` 能看到清晰 revision history。
- 飞书回复只展示本次修改摘要，不刷完整历史。

### 12.3 输出重生成与续跑

交付物：

| 能力       | 说明                                                                   |
| ---------- | ---------------------------------------------------------------------- |
| 只重渲染   | 已有 `sow-extraction.json` 时，只运行输出渲染脚本                      |
| 超时恢复   | 如果文件已生成，下一次直接返回已有文件                                 |
| 输出一致性 | `proposal_outputs` 包含 Markdown、DOCX、open questions、Feishu summary |

验收标准：

- 小修改不会触发 PDF 重新渲染或重新视觉审查。
- timeout 后可通过 `outputs-status` 判断下一步动作。

### 12.4 简版 DOCX 输出

交付物：

| 文件                     | 作用                                      |
| ------------------------ | ----------------------------------------- |
| `scripts/render_docx.py` | 将 `proposal.md` 转成简版 `proposal.docx` |
| `proposal.docx`          | 客户演示用 Word 输出                      |

实现原则：

- DOCX 只做格式转换，不解释业务内容。
- 第一版只要求标题、段落、项目符号和表格可读。
- 不追求和人工 Word 100% 一致。

验收标准：

- `proposal.md` 可生成 `proposal.docx`。
- 飞书能返回 `proposal.md`、`proposal.docx`、`open-questions.md`、`sow-extraction.json`。

### 12.5 客户交付格式优化

交付物：

| 文件                      | 作用                               |
| ------------------------- | ---------------------------------- |
| `proposal.md`             | 面向客户 / estimator 的 proposal   |
| `open-questions.md`       | 只保留待确认事项                   |
| `drawing-index.json`      | 内部页索引，不作为客户主交付       |
| `drawing-visual-notes.md` | 内部视觉审查笔记，不作为客户主交付 |

验收标准：

- `proposal.md` 不像模型分析报告。
- `open-questions.md` 不混入内部 page-by-page evidence。
- 内部审查文件不作为客户主文档发送，除非用户明确要求。

### 12.6 v0.3 Smoke Test

交付物：

| 文件                                       | 作用                           |
| ------------------------------------------ | ------------------------------ |
| `fixtures/709-demo/feishu-smoke-script.md` | 飞书端演示脚本                 |
| `fixtures/709-demo/demo-runbook.md`        | 客户演示 runbook               |
| `scripts/validate_sow_outputs.py`          | 增加 DOCX 和 revision 输出检查 |
| `scripts/smoke_v03.py`                     | 本地 v0.3 管道 smoke test      |

验收流程：

```text
1. 生成 709 SOW。
2. 返回 Markdown、DOCX、open questions 和 JSON。
3. 用户发送“Kitchen stone 全部排除”。
4. Skill 更新 JSON、记录 revision history、重新生成输出。
5. 用户发送“Pantry 门只写 cladding”。
6. Skill 再次更新输出。
7. Validator 检查无报价金额、输出一致、DOCX 文件存在。
```

优先级：

```text
1. Revision history 和 outputs-status 扩展
2. Markdown + DOCX 统一渲染
3. Revision workflow reference
4. Feishu smoke script 更新
5. Validator 增强
```

### 12.7 v0.3 完成标准

v0.3 skill 侧完成需要满足：

- `render_sow_outputs.py --docx` 能生成 `proposal.md`、`proposal.docx`、`open-questions.md`、`feishu-summary.md`。
- `sow_state.py outputs-status` 能在文件已存在时返回 `return_existing_outputs`。
- `sow_state.py append-revision` 能记录完整 revision metadata。
- `validate_sow_outputs.py` 能检查 DOCX、revision history 和核心安全约束。
- `smoke_v03.py` 本地通过。

真实飞书联调不属于本地开发完成条件，但上线前必须执行 `fixtures/709-demo/feishu-smoke-script.md`。

### 12.8 v0.3.1 前置信息确认补强

目标：

- 新建 SOW 生成前先确认客户姓名、Quote/revision、Project、Site、Date。
- 没有客户橱柜 / joinery 图纸或建筑图纸时，先提示用户上传，不进入图纸渲染和 SOW 生成。
- Proposal 抬头不再出现 `Dear TBC`、`Quote: TBC TBC` 或独立 `TBC` 行。

交付物：

| 文件                               | 作用                                                    |
| ---------------------------------- | ------------------------------------------------------- |
| `references/feishu-integration.md` | 增加飞书 preflight intake 和确认话术                    |
| `references/workflow.md`           | 将 preflight gate 放在新建 SOW 流程前置                 |
| `references/sow-schema.md`         | 明确 proposal header 和 drawing attachment 的生成前要求 |
| `scripts/render_sow_outputs.py`    | 对缺失 header 做自然语言兜底                            |
| `scripts/validate_sow_outputs.py`  | 增加 header 和 drawing preflight 检查                   |

验收：

- 缺少任一基础信息或图纸时，Skill 只追问缺失项，不生成 SOW。
- 信息完整时，Skill 先展示确认摘要，用户确认后才生成。
- 本地 smoke test 仍通过。

## 13. v0.4 开发计划

v0.4 的目标是把当前 demo 输出从“能生成”提升到“更像人工 SOW、可稳定交付、方便人工复核”。本版本不引入企业知识库，不做自动报价，不做规则脚本解析图纸；重点是交付可靠性、文档表达、结构化数据质量和 Word 模板质量。

### 13.1 修交付：统一 ZIP 输出包

当前问题：

- 飞书里可能只返回部分文件。
- 邮件发送时可能只附带最后一个附件。
- 用户需要单独追问 `sow-extraction.json` 在哪里。
- 本地路径展示对客户无意义，且容易为空或格式错误。

开发任务：

| 任务                        | 说明                                                                                                              |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 新增输出打包脚本            | 将 `sow-extraction.json`、`proposal.md`、`proposal.docx`、`open-questions.md`、`feishu-summary.md` 打包成一个 ZIP |
| 新增 `output-manifest.json` | 记录 ZIP 内文件、生成时间、sow_id、source 文件摘要                                                                |
| 更新 Feishu 回复规则        | 默认返回 ZIP 包和 `feishu-summary.md` 摘要，不再依赖逐个附件发送                                                  |
| 更新邮件交付规则            | 邮件附件默认只发送完整 ZIP 包，避免多附件丢失                                                                     |
| 更新 validator              | 检查 ZIP 内 5 个核心文件是否完整                                                                                  |

验收：

- 飞书最终回复中能拿到一个完整 SOW ZIP。
- ZIP 内固定包含 5 个核心文件。
- 用户不需要追问 `sow-extraction.json`。
- 邮件交付不会只附带最后一个文件。

### 13.2 修文档渲染：明确 scope / TBC / exclusions 边界

当前问题：

- Proposal 区域描述中仍可能混入 stone、LED、mirror、glass、shower niche、polished plaster 等未确认或非 joinery 内容。
- `TBC` 项和 confirmed scope 混在同一段描述里，客户容易误解为 Kitchman 已确认包含。
- Exclusions 与 Working Areas 描述之间可能互相矛盾。

开发任务：

| 任务                     | 说明                                                            |
| ------------------------ | --------------------------------------------------------------- |
| 拆分 Working Area 描述   | confirmed scope 只写已包含 joinery 内容                         |
| 增加 TBC Items 表        | 将 stone、LED、mirror、glass、shower niche 等待确认内容独立展示 |
| 增强 Exclusions 渲染     | excluded / by others / responsibility TBC 分开表达              |
| 增强 open questions 关联 | 每个 TBC 项需要对应 open question 或 review flag                |
| 更新 proposal 模板规则   | 禁止把待确认项写成客户承诺                                      |

验收：

- `proposal.md` 中 confirmed scope 不包含 responsibility TBC 项。
- TBC 内容集中出现在 `Items Requiring Confirmation` 或专门的 TBC 表。
- Stone / LED / mirror / glass / appliance / shower niche 等高风险项不会被误写成已包含。
- Validator 能提示 confirmed scope 和 TBC/exclusion 冲突。

### 13.3 修数据质量：补 evidence、page refs 和 drawing refs

当前问题：

- 大部分 scope item 缺少 evidence。
- `working_area_rows` 缺少 drawing page / drawing ref。
- 人工复核时难以追溯“这个 scope 来自哪一页图纸”。

开发任务：

| 任务                        | 说明                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| 扩展 schema                 | 为 room、scope item、working area row 增加 `source_pages`、`drawing_refs`、`evidence_summary` |
| 更新视觉审查笔记格式        | 每页视觉笔记记录 page number、drawing number、area candidates、observed scope                 |
| 更新 JSON 生成规则          | 每个房间至少保留 page refs；高/中置信 scope item 尽量保留 evidence                            |
| 更新 drawing index 使用规则 | 用 `drawing-index.json` 辅助 page coverage，不作为 scope 判定脚本                             |
| 增强 validator              | 检查缺页、缺 evidence、缺 source page、room 与 drawing ref 不一致                             |

验收：

- 每个 room 至少有一个 `source_pages` 或 `drawing_refs`。
- 高置信 / 中置信 scope item 至少有 evidence summary 或继承 room-level evidence。
- `working_area_rows` 能追溯到对应 room 和图纸页。
- Validator 对 evidence 缺失给出明确 warning。

### 13.4 提升 DOCX 模板：接近人工 SOW 格式

当前问题：

- 当前 `proposal.docx` 是简版 Markdown 转 Word，结构可读但不像正式 Kitchman proposal。
- 缺少更正式的首页抬头、表格样式、分页控制、字体层级和客户文档观感。
- 没有渲染后的视觉 QA gate。

开发任务：

| 任务               | 说明                                                                           |
| ------------------ | ------------------------------------------------------------------------------ |
| 设计 DOCX 样式系统 | 标题、正文、表格、项目符号、section spacing、page break                        |
| 复用页眉页脚       | 从人工 Proposal golden sample 提取每页页眉、公司 logo、页脚和 section 设置     |
| 优化首页抬头       | 客户姓名、日期、Quote、Project、Site 按人工 SOW 风格排版                       |
| 优化表格样式       | Working Areas、Finish Schedule、TBC Items、Open Questions 使用更清晰列宽和表头 |
| 增加 DOCX 渲染 QA  | 本地有 LibreOffice 时渲染 PNG 检查；无 LibreOffice 时做结构检查并明确提示      |
| 更新 demo fixture  | 709 demo 的 DOCX 输出使用新模板                                                |

验收：

- `proposal.docx` 打开后更接近人工 SOW，不只是 Markdown 包装。
- 每一页包含 Kitchman 页眉 logo 和页脚。
- 首页客户基础信息排版清晰。
- 表格不会过度拥挤，客户可读。
- 如果环境支持 DOCX render，必须完成 PNG 视觉检查。

### 13.5 v0.4 推荐开发顺序

```text
1. package_sow_outputs.py + output-manifest.json
2. Feishu / email 交付规则更新为默认 ZIP
3. schema 增加 source_pages / drawing_refs / evidence_summary
4. render_sow_outputs.py 拆分 confirmed scope、TBC items、exclusions
5. validate_sow_outputs.py 增加 delivery、scope boundary、evidence 检查
6. render_docx.py 模板升级
7. 709 fixture 重新生成并人工对比 golden sample
8. v0.4 smoke test
```

### 13.6 v0.4 详细任务拆分

#### M1：交付包和文件链路

目标是先解决“文件漏发、用户找不到 JSON、邮件只带一个附件”的交付问题。

| 编号      | 任务                          | 涉及文件                                                                 | 验收                                                   |
| --------- | ----------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------ |
| V04-M1-01 | 新增 `package_sow_outputs.py` | `scripts/package_sow_outputs.py`                                         | 输入 output 目录后生成 `709-riversdale-sow.zip`        |
| V04-M1-02 | 生成 `output-manifest.json`   | `scripts/package_sow_outputs.py`                                         | manifest 记录 5 个核心文件、sow_id、生成时间、文件大小 |
| V04-M1-03 | 更新 skill 交付规则           | `SKILL.md`、`references/feishu-integration.md`、`references/workflow.md` | Feishu 默认返回 ZIP，不再逐个附件作为主交付            |
| V04-M1-04 | 更新 Feishu summary           | `scripts/render_sow_outputs.py`                                          | `feishu-summary.md` 显示 ZIP 文件名和 ZIP 内文件清单   |
| V04-M1-05 | 增强 validator                | `scripts/validate_sow_outputs.py`                                        | 检查 ZIP 存在且包含 5 个核心文件                       |

完成标准：

- 新生成项目的 output 目录包含 ZIP 和 `output-manifest.json`。
- ZIP 内固定有 `sow-extraction.json`、`proposal.md`、`proposal.docx`、`open-questions.md`、`feishu-summary.md`。
- 飞书 / 邮件交付说明只把 ZIP 作为主文件。

#### M2：Proposal 渲染边界

目标是解决 proposal 把未确认项写进 confirmed scope 的问题。

| 编号      | 任务                     | 涉及文件                                                           | 验收                                                           |
| --------- | ------------------------ | ------------------------------------------------------------------ | -------------------------------------------------------------- |
| V04-M2-01 | 扩展 scope 分类规则      | `references/sow-schema.md`、`references/review-guardrails.md`      | `included=true/false/tbc` 的 proposal 表达规则清晰             |
| V04-M2-02 | 拆分 Working Areas 描述  | `scripts/render_sow_outputs.py`                                    | confirmed scope 只显示已包含 joinery 内容                      |
| V04-M2-03 | 新增 TBC Items 表        | `scripts/render_sow_outputs.py`、`references/proposal-template.md` | TBC 项独立成表，不混在主描述里                                 |
| V04-M2-04 | 增强 Exclusions 表达     | `scripts/render_sow_outputs.py`                                    | excluded、by others、responsibility TBC 分开展示               |
| V04-M2-05 | 增强 scope boundary 校验 | `scripts/validate_sow_outputs.py`                                  | 如果 confirmed scope 文案包含 responsibility TBC，高亮 warning |

完成标准：

- Stone、LED、mirror、glass、appliance、shower niche 等高风险内容不会默认显示为已包含。
- `proposal.md` 中 confirmed scope、TBC items、exclusions 之间没有明显冲突。
- Open questions 能覆盖主要 TBC 项。

#### M3：数据质量和可追溯性

目标是让人工审核可以从 SOW 追溯回图纸页。

| 编号      | 任务               | 涉及文件                                       | 验收                                                                                       |
| --------- | ------------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------ |
| V04-M3-01 | 扩展 schema 字段   | `references/sow-schema.md`                     | room、scope item、working area row 支持 `source_pages`、`drawing_refs`、`evidence_summary` |
| V04-M3-02 | 更新视觉笔记格式   | `references/workflow.md`                       | `drawing-visual-notes.md` 记录 page、drawing number、area、observed scope                  |
| V04-M3-03 | 更新 JSON 生成要求 | `SKILL.md`、`references/workflow.md`           | 每个 room 至少有 page refs 或 drawing refs                                                 |
| V04-M3-04 | 更新 fixture 数据  | `fixtures/709-demo/output/sow-extraction.json` | 709 demo rooms 和重点 scope items 有追溯字段                                               |
| V04-M3-05 | 增强 validator     | `scripts/validate_sow_outputs.py`              | 缺 page refs / evidence 时给 warning                                                       |

完成标准：

- `sow-extraction.json` 支持按房间追溯图纸页。
- 重点 scope item 有 evidence summary。
- Validator 可以区分“结构缺失”和“业务内容仍需人工确认”。

#### M4：DOCX 模板升级

目标是把 Word 输出从“Markdown 包装”升级为更像人工 Kitchman proposal 的客户文档。

| 编号      | 任务                            | 涉及文件                                        | 验收                                                                           |
| --------- | ------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------ |
| V04-M4-01 | 提取 golden sample 页眉页脚资产 | `assets/`、`scripts/render_docx.py`             | 提取 header/footer XML、logo media、rels                                       |
| V04-M4-02 | 注入页眉页脚                    | `scripts/render_docx.py`                        | 每页包含 Kitchman logo 页眉和页脚                                              |
| V04-M4-03 | 优化首页布局                    | `scripts/render_docx.py`                        | 客户名、日期、Quote、Project、Site 接近人工样式                                |
| V04-M4-04 | 优化表格样式                    | `scripts/render_docx.py`                        | 表格列宽、表头、内边距更适合客户阅读                                           |
| V04-M4-05 | DOCX QA 支持                    | `scripts/validate_sow_outputs.py`、可选 QA 文档 | 能检查 DOCX 必要 parts、header/footer、logo media；有 LibreOffice 时可渲染 PNG |
| V04-M4-06 | 更新 demo fixture               | `fixtures/709-demo/output/proposal.docx`        | 709 demo 使用新 DOCX 模板                                                      |

完成标准：

- `proposal.docx` 每页有 Kitchman logo 页眉和页脚。
- 首页基础信息接近人工 proposal。
- 表格比当前版本更正式、清晰。
- DOCX 结构校验能检查 header/footer 和 logo media。

#### M5：v0.4 Smoke 和回归

| 编号      | 任务                              | 涉及文件                                   | 验收                                                     |
| --------- | --------------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| V04-M5-01 | 新增 v0.4 smoke test              | `scripts/smoke_v04.py`                     | 覆盖 render、package、validate、outputs-status           |
| V04-M5-02 | 更新 demo runbook                 | `fixtures/709-demo/demo-runbook.md`        | 增加 ZIP、TBC boundary、DOCX 页眉页脚检查                |
| V04-M5-03 | 更新 Feishu smoke script          | `fixtures/709-demo/feishu-smoke-script.md` | 飞书验收检查 ZIP 和 preflight                            |
| V04-M5-04 | 人工 golden sample 对比 checklist | `references/golden-sample-standard.md`     | 检查 header/footer、表格结构、scope 边界、open questions |

完成标准：

- `smoke_v04.py` 本地通过。
- 709 demo 能产出 ZIP、结构化 JSON、Markdown、DOCX、open questions、summary。
- 对比人工 SOW 时，主要差距集中在内容判断和报价，不再是文件链路、页眉页脚、表格格式和追溯性。

### 13.7 v0.4 完成标准

- 默认交付一个完整 ZIP，ZIP 内 5 个核心文件齐全。
- `proposal.md` 和 `proposal.docx` 不再把未确认项混入 confirmed scope。
- `sow-extraction.json` 能支持人工按图纸页复核。
- Validator 对交付完整性、TBC 边界、evidence 缺失和 DOCX 基础结构都有检查。
- 709 demo 与人工 SOW 的差距主要剩在“内容判断和报价”，而不是“格式混乱、文件漏发、无法追溯”。

### 13.8 v0.4 当前实现状态

已完成：

- `package_sow_outputs.py` 生成交付 ZIP 和 `output-manifest.json`。
- `feishu-summary.md`、Feishu 规则和 workflow 默认把 ZIP 作为主交付。
- `render_sow_outputs.py` 将 confirmed working areas 与 `TBC Items` 拆分。
- `sow-extraction.json` fixture 增加 `source_pages`、`drawing_refs`、`evidence_summary`。
- `validate_sow_outputs.py` 检查 ZIP、manifest、DOCX header/footer/logo、TBC section 和 evidence/page refs。
- `render_docx.py` 注入 Kitchman logo 页眉和页脚。
- `smoke_v04.py` 覆盖 render、package、manifest、TBC boundary、DOCX branding 和 validator。

仍保留的边界：

- DOCX 已有页眉页脚和 logo。后续 DOCX 页面视觉效果由人工打开 Word/PDF 检查，不作为脚本化开发阻塞项。
- 表格列宽和分页仍是轻量实现，后续可继续向人工 proposal 的高保真 Word 模板靠近。
- v0.4 不解决图纸理解准确率和报价问题，这部分进入 v0.5 / v1.0。

## 14. v0.5 优化计划

v0.5 的目标是基于真实飞书交付结果修复“能生成但交付和语义仍不稳”的问题。优先级高于继续做 DOCX 自动渲染 QA；DOCX 视觉效果由人工验收。

### 14.1 当前发现的问题

飞书实测暴露出以下问题：

- 飞书主附件上传失败，最终消息出现 `Media failed`，用户在飞书里没有拿到主 ZIP。
- 下载目录里只有 5 个散文件，没有 `output-manifest.json` 和 ZIP，但 `sow-extraction.json` 仍声明了 `output/...` 路径和 ZIP 路径。
- `proposal_outputs` 使用的是工作区相对路径，不适合直接用于下载后的平铺交付目录校验。
- `feishu-summary.md` 声明“交付包已打包”，但实际飞书侧 ZIP 没有成功送达。
- 同一类项目同时出现在 `TBC Items` 和 `Exclusions`，例如 stone / LED，客户无法判断是待确认还是已排除。
- mirror、glass、shower niche、stone、LED 等高风险项目有时进入 confirmed working areas，但责任仍在 open questions 中待确认。
- Feishu 总结里的“约 30 个 scope items”与结构化数据里 confirmed / tbc 的区分不够清晰。

### 14.2 M1：修飞书 ZIP 交付和 fallback

目标是确保用户一定能拿到完整交付文件，不能只在消息里看到 `Media failed`。

| 编号      | 任务                     | 涉及文件                                                                 | 验收                                                    |
| --------- | ------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------- |
| V05-M1-01 | 更新交付规则             | `SKILL.md`、`references/feishu-integration.md`、`references/workflow.md` | ZIP 上传失败时必须明确说明失败原因和 fallback           |
| V05-M1-02 | 增加交付前检查           | `package_sow_outputs.py` 或新增交付检查脚本                              | 发送前检查 ZIP 存在、大小大于 0、包含 5 个核心文件      |
| V05-M1-03 | 定义 fallback 策略       | `references/feishu-integration.md`                                       | ZIP 上传失败时发送 5 个散文件，或提示邮件已发送完整 ZIP |
| V05-M1-04 | 更新 Feishu summary 话术 | `render_sow_outputs.py`                                                  | 不在附件失败时继续写“交付包已打包”作为最终成功状态      |

完成标准：

- 飞书附件失败时，用户能看到明确错误，不再只看到 `Media failed`。
- 如果 ZIP 发不出去，系统能退回到散文件或邮件交付说明。
- Feishu summary 不再把“已打包”误表达成“已成功送达”。

### 14.3 M2：修输出路径和 manifest 一致性

目标是让 `sow-extraction.json`、`feishu-summary.md`、ZIP、下载目录和平铺文件都能被 validator 正确理解。

| 编号      | 任务                        | 涉及文件                                  | 验收                                                                   |
| --------- | --------------------------- | ----------------------------------------- | ---------------------------------------------------------------------- |
| V05-M2-01 | 拆分工作区路径和交付路径    | `package_sow_outputs.py`、`sow-schema.md` | `proposal_outputs` 同时记录 workspace refs 和 delivery refs            |
| V05-M2-02 | 支持平铺目录校验            | `validate_sow_outputs.py`                 | 下载后的 5 个散文件目录也能通过结构校验，缺 ZIP 时给明确 warning/error |
| V05-M2-03 | ZIP 内加入 manifest         | `package_sow_outputs.py`                  | ZIP 内可选包含 `output-manifest.json`，减少下载目录丢 manifest 的问题  |
| V05-M2-04 | 校验 summary 与实际文件一致 | `validate_sow_outputs.py`                 | summary 声明 ZIP 时必须存在 ZIP；否则报错                              |

完成标准：

- 服务器 workspace output 目录能通过 validator。
- 解压后的平铺目录能通过 validator 或给出明确交付缺失原因。
- `proposal_outputs` 不再只写 `output/...` 导致下载目录误判。

### 14.4 M3：修 TBC / Exclusions / Confirmed Scope 语义冲突

目标是消除客户最容易误解的 scope 责任问题。

| 编号      | 任务                      | 涉及文件                                       | 验收                                                                              |
| --------- | ------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------- |
| V05-M3-01 | 收紧 `included` 语义      | `sow-schema.md`、`review-guardrails.md`        | `true`、`tbc`、`false` 三种状态互斥，不能同时进多个客户章节                       |
| V05-M3-02 | 渲染互斥章节              | `render_sow_outputs.py`                        | `included=true` 只进 Working Areas，`tbc` 只进 TBC Items，`false` 只进 Exclusions |
| V05-M3-03 | 增加冲突校验              | `validate_sow_outputs.py`                      | 同一 item 同时出现在 TBC 和 Exclusions 时 fail 或 warning                         |
| V05-M3-04 | 更新 fixture 覆盖冲突案例 | `fixtures/709-demo/output/sow-extraction.json` | stone / LED / mirror 等案例覆盖互斥状态                                           |

完成标准：

- Stone / LED 不会同时被表达为 TBC 和 excluded。
- Exclusions 只包含明确排除项，不包含“待确认责任”的项目。
- TBC Items 只包含责任未确认项，不暗示已包含或已排除。

### 14.5 M4：高风险 scope 默认降级策略

目标是避免模型把可见但责任不明的项目写成 Kitchman confirmed scope。

高风险类别：

```text
stone
lighting / LED
appliance
plumbing
electrical
mirror
glass / steel-framed glass door
shower screen / shower niche
fireplace / specialist contractor scope
building / painting / tiling / plaster
```

| 编号      | 任务                         | 涉及文件                                       | 验收                                                                            |
| --------- | ---------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------- |
| V05-M4-01 | 增加高风险类别规则           | `review-guardrails.md`、`proposal-template.md` | 未明确责任时默认进入 TBC 或 Exclusions                                          |
| V05-M4-02 | 渲染时标注责任边界           | `render_sow_outputs.py`                        | mirror/glass/shower niche 等不再默认进入 confirmed scope                        |
| V05-M4-03 | 增加 validator 检查          | `validate_sow_outputs.py`                      | 高风险 category 若 `included=true` 但无 `client_confirmed` 或明确证据则 warning |
| V05-M4-04 | 更新 open questions 生成要求 | `sow-schema.md`                                | 每个高风险 TBC 项必须有对应 open question 或 review flag                        |

完成标准：

- 高风险项目不会因为“图纸可见”就自动成为 Kitchman 承诺。
- Working Areas 更保守，Open Questions 更能指导 estimator。

### 14.6 M5：Feishu 输出摘要质量

目标是让飞书最终消息既短又不误导。

| 编号      | 任务                      | 涉及文件                                   | 验收                                               |
| --------- | ------------------------- | ------------------------------------------ | -------------------------------------------------- |
| V05-M5-01 | 区分 confirmed / TBC 数量 | `render_sow_outputs.py`                    | summary 显示 confirmed scope item 数和 TBC item 数 |
| V05-M5-02 | 精简关键预览              | `render_sow_outputs.py`                    | 只展示前 5 个区域，剩余区域用数量概括              |
| V05-M5-03 | 加入交付状态              | `render_sow_outputs.py` 或交付检查脚本     | summary 明确 ZIP 是否已成功发送、是否走 fallback   |
| V05-M5-04 | 更新 Feishu smoke script  | `fixtures/709-demo/feishu-smoke-script.md` | 验收附件失败和 fallback 文案                       |

完成标准：

- 用户能从飞书消息看出“哪些已确认、哪些待确认、文件是否送达”。
- 不再用“约 30 个 scope items”掩盖 confirmed / TBC 差异。

### 14.7 M6：v0.5 Smoke 和回归

| 编号      | 任务                   | 涉及文件                            | 验收                                                  |
| --------- | ---------------------- | ----------------------------------- | ----------------------------------------------------- |
| V05-M6-01 | 新增 `smoke_v05.py`    | `scripts/smoke_v05.py`              | 覆盖 ZIP 成功、ZIP 缺失、平铺目录、TBC/exclusion 冲突 |
| V05-M6-02 | 增加 validator fixture | `fixtures/709-demo`                 | 至少覆盖正常输出和冲突输出两个样例                    |
| V05-M6-03 | 更新 runbook           | `fixtures/709-demo/demo-runbook.md` | 增加人工 DOCX 检查、交付 fallback、scope 冲突检查     |

完成标准：

- `smoke_v05.py` 能复现这次飞书交付暴露的问题，并验证修复。
- validator 能在本地提前发现 ZIP 缺失、manifest 缺失、路径不一致和 TBC/exclusion 冲突。

### 14.8 v0.5 推荐开发顺序

```text
1. validate_sow_outputs.py：先补交付缺失、平铺目录、TBC/exclusion 冲突检查
2. package_sow_outputs.py：修 manifest 和 delivery refs
3. render_sow_outputs.py：修 TBC / Exclusions / summary 语义
4. SKILL.md + references：更新飞书 fallback 和高风险 scope 规则
5. fixtures：用真实飞书输出构造失败样例和修复样例
6. smoke_v05.py：固化回归
```

### 14.9 v0.5 开发阶段计划

#### Phase 1：失败样例和 validator 先行

目标：先把这次真实飞书交付暴露的问题变成可重复检查的失败用例，避免后续改动只靠人工判断。

| 任务  | 文件                                 | 说明                                                                  | 验收                                              |
| ----- | ------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------- |
| P1-01 | `fixtures/709-demo/failed-delivery/` | 建立真实飞书下载目录样例，包含 5 个散文件、缺 ZIP、缺 manifest        | validator 能稳定复现当前交付失败                  |
| P1-02 | `validate_sow_outputs.py`            | 增加 delivery mode：workspace output、unzipped package、flat download | 能区分 workspace 校验和平铺下载目录校验           |
| P1-03 | `validate_sow_outputs.py`            | 增加 summary/manifest/package 一致性检查                              | summary 声明 ZIP 但目录无 ZIP 时明确报错          |
| P1-04 | `validate_sow_outputs.py`            | 增加 TBC/exclusion 冲突检查                                           | stone / LED 同时 TBC 和 excluded 时失败或 warning |

建议验收命令：

```bash
python3 skills/kitchman-sow/scripts/validate_sow_outputs.py --root skills/kitchman-sow/fixtures/709-demo --json
python3 skills/kitchman-sow/scripts/validate_sow_outputs.py --root skills/kitchman-sow/fixtures/709-demo/failed-delivery --json
```

阶段完成标准：

- 当前真实问题能被 validator 明确识别。
- 正常 fixture 仍然通过。
- 后续修改 package 或 render 时有回归保护。

#### Phase 2：修 package 和交付路径模型

目标：让 workspace 输出、ZIP 内文件、下载后的平铺文件都能被解释清楚。

| 任务  | 文件                      | 说明                                                                           | 验收                                  |
| ----- | ------------------------- | ------------------------------------------------------------------------------ | ------------------------------------- |
| P2-01 | `package_sow_outputs.py`  | ZIP 内加入 `output-manifest.json`                                              | 解压 ZIP 后仍能看到 manifest          |
| P2-02 | `package_sow_outputs.py`  | 在 `proposal_outputs` 中拆分 `workspace_refs`、`package_refs`、`delivery_refs` | 不再只有 `output/...` 一种路径        |
| P2-03 | `sow-schema.md`           | 更新 `proposal_outputs` schema 说明                                            | agent 知道不同路径用途                |
| P2-04 | `validate_sow_outputs.py` | 支持新旧 `proposal_outputs` 兼容校验                                           | v0.4 fixture 和 v0.5 fixture 都可解释 |

建议验收命令：

```bash
python3 skills/kitchman-sow/scripts/package_sow_outputs.py --output-dir skills/kitchman-sow/fixtures/709-demo/output
python3 -m zipfile -l skills/kitchman-sow/fixtures/709-demo/output/709-riversdale-road-camberwell-sow.zip
python3 skills/kitchman-sow/scripts/validate_sow_outputs.py --root skills/kitchman-sow/fixtures/709-demo --json
```

阶段完成标准：

- ZIP 内包含 6 个文件：5 个核心文件 + `output-manifest.json`。
- 平铺下载目录不会因为缺 `output/` 子目录而误判所有文件缺失。
- `feishu-summary.md` 的交付说明和实际文件一致。

#### Phase 3：修 proposal 语义边界

目标：同一个业务项只能有一种客户表达状态，避免“既待确认又排除”。

| 任务  | 文件                                    | 说明                                              | 验收                             |
| ----- | --------------------------------------- | ------------------------------------------------- | -------------------------------- |
| P3-01 | `sow-schema.md`、`review-guardrails.md` | 明确 `included=true/tbc/false` 互斥语义           | 文档规则清晰                     |
| P3-02 | `render_sow_outputs.py`                 | `included=true` 只进入 Working Areas              | confirmed scope 不含责任未确认项 |
| P3-03 | `render_sow_outputs.py`                 | `included=tbc` 只进入 TBC Items 和 open questions | TBC Items 不再与 Exclusions 冲突 |
| P3-04 | `render_sow_outputs.py`                 | `included=false` 只进入 Exclusions                | Exclusions 只表达明确排除        |
| P3-05 | `validate_sow_outputs.py`               | 检查同名/同类 item 跨章节冲突                     | stone / LED 冲突能被拦截         |

建议验收命令：

```bash
python3 skills/kitchman-sow/scripts/render_sow_outputs.py --input skills/kitchman-sow/fixtures/709-demo/output/sow-extraction.json --output-dir skills/kitchman-sow/fixtures/709-demo/output --docx
python3 skills/kitchman-sow/scripts/validate_sow_outputs.py --root skills/kitchman-sow/fixtures/709-demo --json
```

阶段完成标准：

- `proposal.md` 中 TBC Items 与 Exclusions 无明显冲突。
- confirmed working areas 更保守。
- open questions 覆盖主要 TBC 项。

#### Phase 4：高风险 scope 默认降级

目标：把可见但责任不清的高风险项从 confirmed scope 中移出。

| 任务  | 文件                                           | 说明                                                      | 验收                              |
| ----- | ---------------------------------------------- | --------------------------------------------------------- | --------------------------------- |
| P4-01 | `review-guardrails.md`                         | 增加高风险 category 默认处理策略                          | agent 生成 JSON 时有明确规则      |
| P4-02 | `validate_sow_outputs.py`                      | 高风险 category 若 `included=true` 且无明确确认则 warning | mirror/glass/LED/stone 等能被识别 |
| P4-03 | `render_sow_outputs.py`                        | 对高风险 TBC 项输出更清晰责任文案                         | 客户能理解待确认内容              |
| P4-04 | `fixtures/709-demo/output/sow-extraction.json` | 调整 709 demo 中 mirror、LED、stone 等状态                | fixture 体现保守边界              |

阶段完成标准：

- mirror、glass、stone、LED、appliances 等不会仅因图纸可见而成为承诺。
- 高风险 confirmed scope 必须有 `client_confirmed`、明确 company default 或强证据说明。

#### Phase 5：Feishu summary 和 fallback 话术

目标：最终消息能准确表达生成结果和交付状态。

| 任务  | 文件                                   | 说明                                                       | 验收                           |
| ----- | -------------------------------------- | ---------------------------------------------------------- | ------------------------------ |
| P5-01 | `render_sow_outputs.py`                | summary 区分 confirmed scope item、TBC item、open question | 不再只写“约 30 个 scope items” |
| P5-02 | `feishu-integration.md`、`workflow.md` | 明确 ZIP 上传失败 fallback 话术                            | agent 知道失败时如何回复       |
| P5-03 | `feishu-smoke-script.md`               | 增加附件失败、邮件 fallback、散文件 fallback 验收          | 手工联调有脚本可照着走         |
| P5-04 | `demo-runbook.md`                      | 增加人工验收 checklist                                     | 客户 demo 前能快速检查         |

阶段完成标准：

- Feishu 回复能看出文件是否实际送达。
- 发生附件失败时，不再只依赖平台的 `Media failed`。
- 用户能知道下一步该下载 ZIP、查邮件，还是使用散文件。

#### Phase 6：v0.5 smoke 固化

目标：把前面所有修复固化为一键回归。

| 任务  | 文件                           | 说明                                                            | 验收                  |
| ----- | ------------------------------ | --------------------------------------------------------------- | --------------------- |
| P6-01 | `smoke_v05.py`                 | 覆盖 render、package、validate、flat download、conflict fixture | 本地 smoke 通过       |
| P6-02 | `smoke_v03.py`、`smoke_v04.py` | 如路径 schema 变化，保持旧 smoke 兼容                           | 旧版本 smoke 不被破坏 |
| P6-03 | `DEVELOPMENT_PLAN.md`          | 更新 v0.5 实现状态                                              | 计划和实现一致        |

建议验收命令：

```bash
python3 skills/kitchman-sow/scripts/smoke_v05.py
python3 skills/kitchman-sow/scripts/smoke_v04.py
python3 skills/kitchman-sow/scripts/smoke_v03.py
```

阶段完成标准：

- v0.5 主要问题都有自动回归覆盖。
- 真实飞书下载目录这类问题能在本地提前发现。

### 14.10 v0.5 完成标准

- 飞书 ZIP 上传失败不会被静默吞掉。
- 下载目录、ZIP、manifest、`proposal_outputs` 路径一致或能被 validator 明确解释。
- `proposal.md` 不再出现同一项目既 TBC 又 excluded 的冲突表达。
- 高风险 scope 默认保守，不会被误写成 confirmed scope。
- Feishu summary 能区分 confirmed item、TBC item、open question 和交付状态。

### 14.11 v0.5 当前实现状态

已完成：

- `package_sow_outputs.py` 写入 `workspace_refs`、`package_refs`、`delivery_refs`，并将 `output-manifest.json` 一起放入 ZIP。
- `package_sow_outputs.py` 在重复打包时会替换旧交付包段落，避免 `feishu-summary.md` 追加重复 ZIP 清单。
- `validate_sow_outputs.py` 支持 workspace output 和飞书 flat-download 两种校验模式。
- `validate_sow_outputs.py` 对 ZIP / manifest 缺失给出可解释 warning，并检查 summary 与实际文件状态是否一致。
- `validate_sow_outputs.py` 增加 TBC / exclusions 冲突告警，以及高风险 scope 未确认时的 warning。
- `render_sow_outputs.py` 在 Feishu summary 中拆分 confirmed scope items、TBC items 和 open questions。
- `render_sow_outputs.py` 对 stone、lighting/LED、appliance、mirror、glass、shower 等高风险项默认降级为 TBC，除非有明确责任确认。
- `fixtures/709-demo/output/` 已重新生成，stone 等 TBC 项不再同时出现在 exclusions。
- `smoke_v05.py` 覆盖完整 workspace、飞书平铺下载目录、TBC/exclusion 冲突和高风险 scope 降级。

实现取舍：

- 不新增静态 `failed-delivery` fixture 目录，避免维护重复 DOCX/ZIP 二进制样本；`smoke_v05.py` 会从标准 fixture 动态构造 flat-download 场景。
- ZIP 现在包含 6 个文件：5 个核心客户文件 + `output-manifest.json` 技术清单。客户主交付仍然围绕 5 个核心文件说明。

## 15. v0.6 / v1.0 后续方向

v0.6 可继续增强真实图纸理解质量：

- 多项目 golden sample 对比评测。
- 更稳定的房间 / 图纸页覆盖检查。
- 图纸视觉审查分批策略优化，降低超时。
- 人工 review checklist 和差异对比报告。

v1.0 可引入企业能力：

- 企业知识库。
- 历史 proposal 检索。
- 材料 / 五金库。
- 报价辅助。
