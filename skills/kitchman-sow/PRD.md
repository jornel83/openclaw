# PRD: Kitchman SOW / Project Proposal 生成 Skill

## 1. 文档目的

本文定义 `kitchman-sow` skill 的产品需求、demo 版本规划和第一版交付范围。该 skill 基于 OpenClaw 实现，用户主要通过飞书对话触发，不通过独立 Web 项目工作台操作。

本文不是完整报价系统 PRD。第一版目标是打通“飞书消息 + 附件 -> SOW 结构化结果 -> Proposal -> 待确认项 -> 飞书内迭代修改”的演示闭环。

## 2. 背景

Kitchman 当前生成 quotation / project proposal 时，需要人工阅读客户提供的建筑图、joinery 图、材料清单、客户沟通记录和历史 proposal，然后编写 proposal 前半部分的 SOW（Scope of Work）。

会议中明确：SOW 是报价文档的一部分，通常位于价格信息之前，主要说明：

- 这个项目包含哪些服务。
- 涉及哪些房间或区域。
- 每个房间或区域做什么 joinery。
- 使用哪些材料、五金、配件。
- 哪些项目包含，哪些项目排除。
- 生产、送货、安装流程是什么。
- 哪些内容需要客户或 estimator 确认。

709 Riversdale Road Camberwell 案例显示，SOW 生成不是简单 OCR。它需要同时理解图纸事实、客户沟通、公司默认规则和历史项目经验。Demo 阶段暂不接企业知识库，优先展示当前附件内信息的抽取、组织和可审核输出。

## 3. 产品定位

### 3.1 定位

`kitchman-sow` 是飞书对话式 SOW 起草助手，不是自动报价系统，也不是完整项目管理系统。

用户在飞书里发送自然语言请求并上传附件，OpenClaw 识别意图后调用 skill。Skill 在同一飞书会话中反馈进度、追问缺失信息、输出初版 SOW，并支持用户继续用自然语言修正。

### 3.2 核心原则

- 对话触发：用户不需要打开 project 页面，通过飞书消息触发任务。
- 附件优先：Demo 只基于本次消息、会话上下文和上传附件工作。
- 不编造：无法确认的材料、尺寸、工艺、价格必须标记为 `TBC` 或进入待确认项。
- 可追溯：每条 room scope、finish、exclusion、special note 都必须关联来源或说明来源类型。
- 可审核：输出必须让 estimator / project owner 快速判断哪些内容可以保留，哪些需要修改。
- 价格后置：Demo 不自动生成最终报价金额。
- 知识库后置：企业历史项目库、材料库、五金库、相似项目召回不进入 demo v0.1。

## 4. 用户和使用场景

### 4.1 主要用户

- 销售 / 项目负责人：在飞书里发起 SOW 任务，查看 proposal 和待确认问题。
- Estimator / 设计人员：在飞书里审核图纸解析、材料判断、特殊工艺、included / excluded scope。
- 管理者：后续维护历史项目库、材料库、五金库和标准条款。

### 4.2 典型触发语

用户可在飞书中发送：

```text
我现在要出一下 709 Riversdale Road 项目的 SOW，上传的文件是项目图纸和客户定制需求。
```

```text
帮我根据这些图纸生成一版 Kitchman proposal 的 SOW，价格先空着。
```

```text
根据这份 proposal 模板和客户图纸，先整理 working areas 和 open questions。
```

### 4.3 典型对话流程

1. 用户在飞书发送触发消息并上传附件。
2. OpenClaw Feishu channel 收到消息和附件。
3. Skill 判断意图为 `generate_sow`。
4. Skill 解析或创建内部 `sow_id`，不要求用户打开项目。
5. Skill 检查项目名、客户名、quote id、附件等输入是否足够。
6. 如果缺少关键信息，Skill 在飞书里追问。
7. Skill 下载并分类附件。
8. Skill 发送阶段性进度消息。
9. Skill 分析图纸、proposal、客户说明。
10. Skill 返回 SOW 摘要、待确认项、proposal 和附件文件。
11. 用户继续在飞书里发修正指令。
12. Skill 更新内部 SOW JSON 并重新生成输出文件。

## 5. 当前人工流程

从会议和 709 案例看，当前人工流程如下：

1. 收到客户资料。
2. 判断资料类型：建筑图、joinery 图、客户手绘图、材料清单、装修说明、沟通记录。
3. 找 proposal 模板或历史 proposal。
4. 记录客户提供了哪些资料。
5. 阅读图纸，识别公司需要提供服务的范围。
6. 按房间 / 区域拆分 scope。
7. 综合平面图、立面图、剖面图，描述每个区域的柜体、门板、抽屉、开放格、五金、镜子、玻璃、金属件等。
8. 结合公司经验写入 caveat，例如板材尺寸限制、纹路无法连续、某些门只做 cladding 不做门体。
9. 补充材料表和五金表。
10. 补充生产、送货、安装流程。
11. 补充 exclusions、lead time、payment terms。
12. 人工确认价格后输出最终 proposal。

## 6. Demo 版本范围

### 6.1 Demo 目标

Demo 版本优先展示客户能直接感知的效果：

- 发一句飞书消息并上传资料即可触发 SOW 任务。
- 系统能识别附件类型和资料完整度。
- 系统能拆出房间和 scope。
- 系统能输出待确认项。
- 用户能用飞书消息继续修正。
- 系统能返回一份可审核的 proposal。

### 6.2 Demo v0.1 范围

v0.1 以 709 golden sample 为主，打通飞书触发到 SOW 输出的完整链路。

包含：

- 飞书消息触发 `generate_sow`。
- 读取当前消息正文和附件元数据。
- 下载并保存附件到内部 `sow_id` workspace。
- 识别附件类型：PDF、docx、图片、Excel、unknown。
- 使用 709 案例和通用规则生成结构化 SOW。
- 返回飞书进度消息。
- 返回摘要、open questions、Markdown proposal。
- 支持用户在飞书里发简单修正指令并重新生成 SOW 输出。

### 6.3 Demo v0.2 范围

v0.2 开始支持真实新项目的初步泛化。

新增：

- PDF 页标题识别。
- room / area 基础抽取。
- 图纸页和 room 的关联。
- `source_documents` 清单。
- evidence / confidence 展示。
- 缺失项目字段自动追问。

### 6.4 Demo v0.3 范围

v0.3 强化对话式审核。

新增：

- 支持更多自然语言修正，例如修改 material、exclusion、included scope。
- 支持重新生成 `proposal.md`。
- 支持输出简版 docx。
- 支持当前会话内多个 revision。

### 6.5 Demo 非范围

Demo 不做：

- 企业知识库接入。
- 历史项目自动相似召回。
- 自动精准报价。
- 自动发送客户。
- 完整 shop drawing 生成。
- 完整材料用量计算。
- 复杂手绘图的完全自动判断。
- 多人审批 UI。
- CRM / ERP 集成。
- 高保真 Word 排版。

## 7. OpenClaw / 飞书交互设计

### 7.1 触发方式

Skill 由 OpenClaw 在飞书消息中触发。触发条件包括：

- 消息包含 `SOW`、`scope of work`、`proposal`、`报价前半部分`、`working areas` 等意图词。
- 消息包含“出一下”“生成”“整理”“根据图纸”等动作。
- 消息带附件，或会话近期已有附件。

触发后，Skill 应回复一条确认消息：

```text
收到，我会先确认 proposal 基础信息和图纸。当前会基于本次消息和附件分析，不会生成最终报价金额。
```

### 7.2 前置信息确认

新建 SOW 任务在正式生成前必须先确认 proposal 抬头信息和图纸输入。

必须确认的基础信息：

- 客户姓名。
- Quote 编号和 revision。
- Project 名称。
- Site 地址。
- Proposal 日期。

必须确认的图纸输入：

- 至少一份可读取的客户橱柜 / joinery 图纸，或建筑图纸。

如果信息完整，Skill 应先让用户确认：

```text
我先确认一下基础信息，确认后再开始生成 SOW：
- 客户姓名：Calvin Huang
- Quote：Q2248 Rev1
- Project：709 Riversdale Road Camberwell
- Site：709 Riversdale Road, Camberwell
- Date：18 March 2026
- 图纸：已收到客户橱柜图纸 PDF

请回复“确认开始生成”，或直接修改上述任一字段。
```

如果信息缺失，Skill 应只追问缺失项，并停止生成流程：

```text
我可以生成 SOW，但开始前需要先补充 / 确认以下信息：
1. 客户姓名
2. Quote 编号和 revision
3. Proposal 日期
4. 客户橱柜图纸或建筑图纸 PDF
```

### 7.3 附件处理

Skill 应从飞书消息中获取附件并建立内部 `sow_id` 对应的 SOW state。

附件处理步骤：

1. 读取附件列表。
2. 下载附件到内部临时目录。
3. 记录附件原始文件名、大小、类型、来源消息。
4. 对 PDF / docx / image / spreadsheet 做基础识别。
5. 输出 `source_documents` 清单。

如果没有附件，Skill 应追问：

```text
我还没有看到可读取的客户橱柜图纸或建筑图纸。请上传图纸 PDF 后，我再开始生成 SOW。
```

### 7.4 进度反馈

长任务必须在飞书中发送阶段性反馈。

建议进度节点：

- 已收到任务，正在检查附件。
- 已确认客户姓名、Quote、Project、Site、Date。
- 已识别附件类型。
- 正在读取 proposal / 图纸。
- 已识别 room / area。
- 正在生成 SOW。
- SOW 已生成，等待人工确认。

进度消息示例：

```text
已识别 2 份资料：
1. 709 Riversdale Road, Camberwell_JD.pdf：Joinery drawing，25 页，需要视觉读取。
2. Proposal Res1.docx：Proposal 样本，可读取文本。

我会先提取房间列表和 working areas。
```

### 7.4 飞书回复分层

不要把完整 proposal 一次性贴进群里。回复分三层：

- 摘要消息：识别到多少文件、多少房间、多少 scope items、多少待确认项。
- 关键预览：展示重点房间和高风险项，例如 Kitchen、Pantry、WIR。
- 输出文件：发送 `sow-extraction.json`、`proposal.md`、`proposal.docx`、`open-questions.md`、`feishu-summary.md`。

### 7.5 对话式修正

用户可以继续在同一会话里发修正指令。

示例：

```text
Kitchen 里面 stone 全部排除，LED 也排除。
```

```text
Pantry 那个门只写我们提供 cladding，不提供门和五金。
```

```text
把 Master WIR 的 mirror 改成 TBC。
```

```text
生成客户版 proposal。
```

Skill 应解析修正意图，更新内部 SOW JSON，并重新生成对应输出。

### 7.6 SOW State

OpenClaw 负责维护飞书会话、消息路由、agent session 和回复目标。Skill 不应重新创建或管理这些运行时上下文。

Skill 内部只维护 SOW 业务状态，用 `sow_id` 标识当前 SOW 任务。用户不需要感知 project 页面。

状态示例：

```json
{
  "sow_id": "sow-709-riversdale-road-20260425",
  "sow_status": "awaiting_review",
  "runtime_ref": {
    "channel": "feishu",
    "conversation_id": "from-openclaw",
    "requested_by": "from-openclaw"
  },
  "project": {
    "name": "709 Riversdale Road",
    "client_name": "TBC",
    "quote_id": "TBC"
  },
  "files": [],
  "extraction": {},
  "proposal_markdown": "",
  "open_questions": []
}
```

SOW 业务状态生命周期：

- `collecting_inputs`
- `analyzing_files`
- `sow_ready_for_review`
- `awaiting_review`
- `revision_requested`
- `sow_ready_for_export`
- `failed_needs_manual_review`

## 8. 输入契约

### 8.1 飞书消息输入

| 字段              | 类型   | 要求     | 缺失时行为         |
| ----------------- | ------ | -------- | ------------------ |
| `message_text`    | string | 必填     | 无法判断意图时追问 |
| `attachments`     | file[] | 建议必填 | 追问上传资料       |
| `conversation_id` | string | 必填     | 无法维持上下文     |
| `sender_id`       | string | 必填     | 记录请求人         |
| `reply_target`    | string | 必填     | 用于进度和结果回复 |

### 8.2 项目信息输入

| 字段                | 类型   | 要求     | 缺失时行为                            |
| ------------------- | ------ | -------- | ------------------------------------- |
| `project_name`      | string | 建议必填 | 从消息推断并标记 `inferred`，否则追问 |
| `site_address`      | string | 建议必填 | 进入待确认项                          |
| `client_name`       | string | 可选     | 使用 `TBC` 并进入待确认项             |
| `quote_id`          | string | 可选     | 使用 `TBC`                            |
| `proposal_template` | file   | 可选     | 使用默认 Markdown 模板                |

### 8.3 本地开发 fallback

为便于开发和测试，skill 也应支持本地文件路径输入：

- `message_text`
- `source_files`
- `conversation_id` 可用 mock 值
- `sender_id` 可用 mock 值

该 fallback 只用于开发，不是客户演示主入口。

### 8.4 可选资料类型

| 类型             | 示例                            | 用途                                         |
| ---------------- | ------------------------------- | -------------------------------------------- |
| 建筑图           | Architectural drawing PDF       | 房屋结构、楼层、高度、房间位置、送货安装判断 |
| Joinery 图       | Cabinetry / joinery drawing PDF | 具体柜体、平面图、立面图、剖面图、特殊工艺   |
| 室内设计图       | Interior design PDF             | 材料、饰面、设计 intent                      |
| Finish schedule  | PDF / Excel / docx              | 材料和颜色确认                               |
| Fixture schedule | PDF / Excel / docx              | sink、basin、appliance 等 FFE 判断           |
| 客户手写标注     | image / PDF                     | 客户补充要求，低置信度处理                   |
| 沟通记录         | txt / markdown / exported chat  | 客户确认材料、范围变化、口头约定             |
| Proposal 样本    | docx / PDF                      | 模板结构和措辞参考                           |

## 9. 图纸理解要求

### 9.1 建筑图

建筑图用于理解：

- 房屋整体结构。
- 房间位置。
- 楼层。
- ceiling height。
- 大尺寸。
- 通道、送货、安装限制。
- 灯位、墙体、饰面等上下文。

建筑图通常不直接决定 joinery scope，但会影响交付假设和风险提示。

### 9.2 Joinery 图

Joinery 图用于理解：

- 每个 room / area 的柜体设计。
- 平面图、立面图、剖面图之间的对应关系。
- 门板、抽屉、开放格、shaving cabinet、vanity、robe、pantry、island、mirror、glass door、metal frame、LED、hanging rail 等元素。
- 特殊结构，例如 curved island back、pantry pivot door cladding、polished plaster interface。

### 9.3 视图关联

厨房等复杂区域不能只看单页。Skill 应尝试关联：

- Plan view。
- Elevation view。
- Section view。
- 图纸编号，例如 `JD 01`、`JD 02`。
- 平面图上的方向编号，例如 `1`、`2`、`3`、`4`、`5`。

无法可靠关联时，必须进入待确认项。

## 10. 来源类型和证据要求

### 10.1 Source Type

每条输出内容必须标记来源类型：

| `source_type`           | 含义                                   | 是否可直接进入 proposal    |
| ----------------------- | -------------------------------------- | -------------------------- |
| `observed_from_drawing` | 从图纸明确读到                         | 可以，但需保留 evidence    |
| `client_confirmed`      | 从客户沟通或客户提供 schedule 明确确认 | 可以，但需保留 evidence    |
| `company_default`       | 来自 demo 内置默认规则或模板           | 可以，但建议人工审核       |
| `historical_reference`  | 来自相似历史项目                       | Demo v0.1 不启用           |
| `inferred`              | 模型根据上下文推断                     | 不应直接进入客户可见最终稿 |
| `unknown`               | 无法确认                               | 必须进入待确认项           |

### 10.2 Evidence

每条 room scope、finish、hardware、exclusion、special note 都必须带 evidence。

Evidence 至少包含：

- `file_name`
- `page_number` 或 `section`
- `drawing_ref`，例如 `JD 01`
- `view_ref`，例如 `Kitchen Elevation 3`
- `message_ref`，例如飞书消息 ID
- `evidence_type`，例如 `text_layer`、`ocr`、`visual_reading`、`client_note`、`demo_rule`
- `confidence`，取值 `high`、`medium`、`low`

如果 evidence 不足，内容必须进入 `open_questions` 或标记 `TBC`。

## 11. 输出设计

### 11.1 飞书消息输出

Demo 必须在飞书中输出：

- 任务确认消息。
- 附件识别摘要。
- 分析进度。
- SOW 摘要。
- 关键 room preview。
- 待确认问题摘要。
- 输出文件链接或附件。

摘要消息示例：

```text
SOW 已生成。

识别到 9 个区域、38 个 scope items、12 条材料 / 五金项、8 个待确认问题。

价格字段已留空，没有生成最终报价金额。
```

关键 room preview 示例：

```text
GF Kitchen
- Overheads / Base / Drawers / Fridge CUPD / Oven Tower / Wall Panel
- 2 curved structures at back of island
- Pantry door: cladding only, door structure and hardware TBC
- Finish: Door/Panel TBC, Carcass White Melamine
```

### 11.2 文件输出

MVP 输出 3 个核心文件：

- `sow-extraction.json`：结构化中间数据。
- `proposal.md`：Markdown proposal。
- `open-questions.md`：待人工确认项。

Phase 2 再输出：

- `proposal.docx`
- `proposal.pdf`

### 11.3 Proposal 结构

Markdown proposal 应对应现有 proposal 文档结构：

- Header：客户名、日期、Quote 编号、Project、Site。
- Opening letter：公司固定开场信。
- Design and Planning。
- Documents Provided by Client。
- Joinery Working Areas。
- Joinery Finish Schedule。
- Material Preparation and Production。
- Joinery Delivery。
- Joinery Installation。
- Pricing placeholder。
- Notes and assumptions。
- Exclusions。
- Lead time。
- Payment terms。
- Closing。

### 11.4 Joinery Working Areas

核心表格字段：

| Room | Description | Joinery Finish | Review Status |
| ---- | ----------- | -------------- | ------------- |

`Description` 应只包含 scope 级描述，不应混入无法确认的价格、工期或供应商承诺。

`Review Status` 取值：

- `ready_for_review`
- `needs_confirmation`
- `low_confidence`

## 12. 中间数据结构

```json
{
  "sow_state": {
    "sow_id": "sow-709-riversdale-road-20260425",
    "sow_status": "awaiting_review",
    "runtime_ref": {
      "channel": "feishu",
      "conversation_id": "from-openclaw",
      "requested_by": "from-openclaw"
    }
  },
  "project": {
    "client_name": "TBC",
    "quote_id": "TBC",
    "project_name": "709 Riversdale Road Camberwell",
    "site_address": "709 Riversdale Road Camberwell",
    "proposal_date": "2026-04-25"
  },
  "source_messages": [
    {
      "message_id": "msg-001",
      "text": "我现在要出一下 709 Riversdale Road 项目的 SOW，上传的文件是项目图纸和客户定制需求。",
      "created_at": "2026-04-25T10:00:00+08:00"
    }
  ],
  "source_documents": [
    {
      "id": "doc-001",
      "type": "joinery_drawing",
      "file_name": "709 Riversdale Road, Camberwell_JD.pdf",
      "source_message_id": "msg-001",
      "text_extractable": false,
      "requires_visual_reading": true,
      "notes": ["PDF text layer only exposes page titles reliably"]
    }
  ],
  "rooms": [
    {
      "id": "room-kitchen",
      "name": "GF Kitchen",
      "normalized_name": "GF Kitchen",
      "floor": "GF",
      "source_pages": ["JD 01", "JD 02", "JD 03", "JD 04"],
      "scope_items": [
        {
          "item": "Wall panel",
          "category": "panel",
          "included": true,
          "source_type": "observed_from_drawing",
          "confidence": "medium",
          "evidence": [
            {
              "file_name": "709 Riversdale Road, Camberwell_JD.pdf",
              "page_number": 1,
              "drawing_ref": "JD 01",
              "view_ref": "Kitchen Plan",
              "message_ref": "msg-001",
              "evidence_type": "visual_reading"
            }
          ]
        }
      ],
      "finish": [
        {
          "area": "Door/Panel",
          "material": "TBC",
          "source_type": "unknown",
          "confidence": "low",
          "review_status": "needs_confirmation"
        },
        {
          "area": "Carcass",
          "material": "White Melamine",
          "source_type": "company_default",
          "confidence": "medium",
          "review_status": "ready_for_review"
        }
      ],
      "special_notes": [
        {
          "note": "Wall panels may require joints due to board size limitation.",
          "source_type": "company_default",
          "confidence": "medium",
          "review_status": "ready_for_review"
        }
      ],
      "open_questions": ["Confirm final door/panel material against latest client selection."]
    }
  ],
  "finish_schedule": [],
  "exclusions": [],
  "commercial_terms": {
    "total": null,
    "gst": null,
    "grand_total": null,
    "lead_time": "8-10 weeks after approved samples and shop drawings",
    "payment_terms": ["50% Deposit", "30% On Delivery", "20% Upon Completion"]
  },
  "open_questions": []
}
```

## 13. 功能需求

### FR1: 飞书消息触发

Skill 应能从飞书自然语言消息识别 SOW 生成意图。

验收：

- 能识别“出 SOW”“生成 proposal”“根据图纸整理 working areas”等表达。
- 能在触发后回复任务确认消息。
- 不生成最终报价金额。

### FR2: 附件 intake

Skill 应读取当前消息附件并建立内部 SOW state。

验收：

- 能列出附件文件名、类型、大小、来源消息。
- 能下载附件到 `sow_id` workspace。
- 无附件时在飞书追问。

### FR3: 文件分类

Skill 应识别输入文件类型，并输出 `source_documents` 清单。

验收：

- 能区分 proposal 样本、建筑图、joinery 图、材料表、手写图、沟通记录。
- 能标记 PDF 是否可直接抽取文本。
- 能标记是否需要视觉理解。

### FR4: 项目信息提取

Skill 应从飞书消息和附件中提取或确认：

- client name
- quote id
- project name
- site address
- proposal date

验收：

- 新建 SOW 生成前必须先确认 client name、quote id/revision、project name、site address、proposal date。
- 缺失字段先在飞书追问，不直接生成客户版 proposal。
- 从消息推断的字段需要在前置确认消息中展示给用户确认。
- 不从文件名中强行推断客户名，除非标记为 `inferred`。
- `proposal.md` 不应出现 `Dear TBC`、`Quote: TBC TBC` 或独立的 `TBC` 抬头行。

### FR5: 房间和区域识别

Skill 应提取 room / area 列表，并做命名归一。

验收：

- 能识别 709 案例中的 GF Kitchen、GF Pantry、GF Living、CLOAK、LIN/LAU、ENS / BATH、Master WIR、B2 Robe、B3 Robe。
- 能保留原图纸名称和 proposal normalized name。

### FR6: Room Scope 提取

Skill 应为每个 room 输出 scope items。

验收：

- 每个 item 有 `category`、`included`、`source_type`、`confidence`、`evidence`。
- 无 evidence 的 item 不进入最终 proposal 正文，只进入待确认项。

### FR7: 平面图和立面图关联

Skill 应尝试关联 plan、elevation、section。

验收：

- 对厨房等复杂区域，输出关联过的 source pages。
- 无法关联的视图进入待确认项。

### FR8: Demo 默认规则应用

Skill 应使用 demo 内置规则生成 caveat 和 exclusions。

初始规则包括：

- 板材尺寸限制可能导致墙板拼接。
- 超出板材尺寸的木纹板无法保证完整 grain matching。
- Pantry cabinet door through to pantry 可能只做 cladding，不提供门体和特殊五金。
- Curved island back 属于特殊结构。
- Stone bench、polished plaster、LED、sinks、basins、FFE 默认需要确认是否排除。

验收：

- 规则输出必须标记为 `company_default`。
- 规则不得覆盖客户明确确认内容。

### FR9: 材料和五金表

Skill 应生成 finish schedule。

验收：

- 材料来源必须标记。
- 不确定材料使用 `TBC`。
- 不得编造品牌、颜色、型号。

### FR10: Proposal 生成

Skill 应从结构化 JSON 生成 Markdown proposal。

验收：

- Proposal 结构对应 Kitchman proposal。
- 价格字段为空或占位，不生成最终报价。
- 低置信度内容不直接写成确定承诺。

### FR11: 飞书内修正和再生成

Skill 应支持用户在同一飞书会话中修改 scope、finish、exclusions、open questions。

验收：

- 能解析“Kitchen stone 全部排除”一类修改。
- 能更新 SOW JSON。
- 能重新生成 proposal。
- 能回复变更摘要。

### FR12: 待确认项生成

Skill 应生成 `open-questions.md` 并在飞书中摘要展示。

待确认项至少覆盖：

- 缺失项目信息。
- 低置信度图纸识别。
- 图纸和沟通记录冲突。
- 材料 / 颜色 / 五金未确认。
- 是否包含安装。
- 是否包含 stone / LED / plaster / FFE。
- 特殊工艺是否加价。
- 价格是否由人工填写。

## 14. 人工审核流程

Demo 输出后，人工在飞书中按以下顺序审核：

1. 确认项目基础信息。
2. 确认客户提供资料清单。
3. 确认 room / area 列表。
4. 逐房间确认 included scope。
5. 逐房间确认 excluded scope。
6. 确认材料、颜色、五金。
7. 确认特殊工艺 caveat。
8. 确认 production / delivery / installation 是否适用。
9. 确认 exclusions。
10. 人工填写或确认价格。
11. 确认 lead time 和 payment terms。
12. 请求 skill 生成客户版 proposal。

审核状态：

- `unreviewed`
- `needs_confirmation`
- `approved_for_proposal`
- `excluded_from_proposal`

## 15. 知识库设计

Demo v0.1 不接企业知识库，但 PRD 保留后续知识库分层。

### 15.1 历史项目库

内容：

- 历史 proposal。
- 历史 room descriptions。
- 历史 exclusions。
- 历史 special notes。

用途：

- 相似措辞参考。
- 常见 scope pattern 参考。
- 不作为当前项目事实。

### 15.2 公司规则库

内容：

- 板材尺寸限制。
- Grain matching 规则。
- 默认 exclusions。
- 标准 production / delivery / installation 段落。
- 常见特殊工艺说明。

用途：

- 自动补充 caveat。
- 自动生成待确认项。
- 输出时标记 `company_default`。

### 15.3 材料和五金库

内容：

- 常用 door / panel 材料。
- Carcass 默认材料。
- Hinges。
- Drawer runners。
- Bins。
- Mirrors。
- Glass。
- Metal frames。
- Hanging rails。

用途：

- 生成 finish schedule。
- 校验材料名称。
- 标记 TBC。

## 16. 验收数据集

第一版不应只用 709 案例验收。至少需要 4 类样本。

### Case A: 709 Golden Sample

目标：

- 资料完整。
- 有 proposal 样本。
- 有 joinery 图。
- 有复杂厨房、pantry、living、laundry、bathroom、WIR、robes。

验收重点：

- 飞书触发和附件 intake。
- 房间识别。
- Kitchen 特殊项。
- Wall panel / grain matching caveat。
- Pantry cladding only。
- Finish schedule。

### Case B: 只有建筑图

目标：

- 测试资料不足时的降级行为。

验收重点：

- 不编造 joinery scope。
- 输出缺失 joinery drawing 的待确认项。
- 只能提取房间上下文和风险提示。

### Case C: 有手写 / 低清晰度资料

目标：

- 测试低置信度处理。

验收重点：

- 手写内容标记为低置信度。
- 不把模糊内容写成确定承诺。
- 输出明确待确认项。

### Case D: 材料未最终确认

目标：

- 测试材料来源和 TBC 行为。

验收重点：

- 图纸材料和客户沟通冲突时，标记冲突。
- 未确认材料使用 `TBC`。
- 不从历史项目套用具体材料为当前事实。

## 17. 量化验收标准

Demo v0.1 通过标准：

- 飞书触发成功率在 709 演示语料中达到 90%。
- 附件识别能列出全部上传文件。
- 709 案例房间召回率不少于 85%。
- 709 案例关键特殊项召回率不少于 70%。
- 所有 proposal 正文中的 scope item 都有 evidence 或 source_type。
- 所有 `inferred`、`unknown` 内容都进入待确认项。
- 不生成最终报价金额。
- 未确认材料不出现具体编造型号。
- Markdown proposal 结构与 Kitchman proposal 样本一致。
- 至少输出 5 个有效待确认项。
- 用户通过飞书发出 3 类修改指令后，系统能更新 SOW JSON 和输出文件。

## 18. 风险和缓解

| 风险                        | 影响                      | 缓解                                                 |
| --------------------------- | ------------------------- | ---------------------------------------------------- |
| 飞书附件下载失败            | 任务无法分析              | 明确提示用户重新上传，保留 SOW state                 |
| 长任务无反馈                | 用户以为卡住              | 阶段性进度消息                                       |
| PDF 文字层弱                | 文本抽取不足              | 使用视觉理解，保留 evidence 和 confidence            |
| 图纸视图关联复杂            | 漏掉 scope 或误读墙面     | 对复杂区域强制输出 source pages 和待确认项           |
| 材料来自口头沟通            | 图纸与实际成交不一致      | 区分 `observed_from_drawing` 和 `client_confirmed`   |
| 历史项目过拟合              | 把历史 scope 当作当前事实 | Demo 不接历史项目库，后续标记 `historical_reference` |
| AI 把图纸内容误认为包含范围 | 商业承诺风险              | 输出 included / excluded / TBC，人工审核必需         |
| 飞书消息过长                | 群里刷屏、难读            | 分层回复，完整结果用附件                             |
| Word 排版消耗过多           | 偏离 SOW 质量验证         | v0.3 只输出简版 DOCX，高保真 Word 模板后置           |

## 19. Phase 规划

### Phase 1: Feishu Demo v0.1

- 飞书消息触发。
- 附件 intake。
- 709 案例 reference。
- Demo 默认规则。
- SOW JSON schema。
- Markdown proposal。
- Open questions 输出。
- 简单飞书内修正。

### Phase 2: Feishu Demo v0.2

- 真实 PDF 页标题识别。
- Room / area 基础抽取。
- Evidence / confidence 展示。
- 缺失字段自动追问。
- 多轮修正稳定性。

### Phase 3: 文档导出和模板化

- Word docx 模板填充。
- Proposal 表格格式保持。
- 简单版本对比。
- 用户修改后重新生成。

### Phase 4: 企业知识库增强

- 历史 proposal 批量切片。
- 材料 / 五金库结构化。
- 相似项目召回。
- 规则库维护流程。

### Phase 5: 报价辅助

- 房间级复杂度评估。
- 特殊工艺加价提醒。
- 相似项目报价参考。
- 人工确认价格后补全 proposal。

## 20. 待确认问题

- 飞书附件下载和文件大小限制是多少？
- Demo v0.1 是否只用 709 golden sample 演示？
- 飞书结果文件应直接上传到会话，还是生成下载链接？
- 是否允许 skill 在群聊中回复详细 scope，还是只发摘要和附件？
- 飞书会话上下文保留多久？
- 是否需要支持用户指定“不要发群里，只私聊我结果”？
- 第一版是否只输出 Markdown，docx 是否推迟到 Phase 3？
- Evidence 是否需要在客户可见 proposal 中隐藏，仅保留在内部 JSON？
- 企业知识库接入预计在哪个阶段开始？
- 709 之外还可以提供哪些验收样本？

## 21. 核心结论

`kitchman-sow` demo 应专注于“飞书对话式、可追溯、可审核的 SOW 起草”。客户看到的核心体验不是打开一个项目页面，而是在飞书里发起任务、上传资料、收到初版 proposal、继续修正，并最终得到一份可审核的 proposal。
