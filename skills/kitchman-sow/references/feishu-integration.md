# Feishu Integration

This reference defines the Feishu interaction behavior for `kitchman-sow`.

The skill does not listen to Feishu directly. OpenClaw Feishu Channel receives messages, attachment references, conversation metadata, and reply targets. The skill only describes when it should be used and how to handle the task after OpenClaw routes the conversation to the agent.

## Trigger Recognition

Use this skill when the Feishu message asks to create, revise, review, or package a Kitchman SOW/proposal for cabinetry or whole-home custom joinery.

High-confidence trigger intents:

```text
出 SOW
生成 SOW
整理 Scope of Work
生成 proposal
整理 project proposal
根据图纸整理 working areas
根据图纸整理 open questions
根据客户需求整理柜体范围
根据 proposal 模板生成客户版文档
```

High-confidence material context:

```text
图纸
joinery drawing
cabinetry drawing
proposal 样本
golden sample
客户定制需求
装修说明
材料表
五金表
working areas
scope items
exclusions
finishes
hardware
```

Typical new SOW messages:

```text
我现在要出一下 709 Riversdale Road 项目的 SOW，上传的文件是项目图纸和客户定制需求。
帮我根据这些图纸生成一版 Kitchman proposal 的 SOW，价格先空着。
根据这份 proposal 模板和客户图纸，先整理 working areas 和 open questions。
```

## Non-Trigger Cases

Do not use this skill for:

- Generic chat unrelated to project proposal or SOW work.
- Pure final price calculation.
- Standalone visual render generation unrelated to SOW/proposal preparation.
- General project status updates unrelated to SOW/proposal generation.
- Support questions about OpenClaw itself.

If the user asks only for final pricing, reply that the skill does not generate final quotation amounts and offer to prepare the SOW for estimator pricing.

## Intent Decision Flow

Use this decision flow after receiving a Feishu message:

1. If the message asks for SOW/proposal/working areas/open questions from project materials, handle as `generate_sow`.
2. If the current conversation has an active `sow_id` and the message asks to change, exclude, mark TBC, regenerate, or update content, handle as `revise_sow`.
3. If the message asks to review or package existing SOW/proposal content, handle as `review_sow` or `package_sow`.
4. If the message is ambiguous but mentions drawings, proposal, cabinetry, joinery, or customer requirements, ask one concise clarification.
5. If the message is unrelated, do not force this skill.

Do not implement this as a keyword-matching script. This flow is guidance for the agent's natural-language decision.

## New SOW Preflight Intake

For `generate_sow`, confirm the proposal header and drawing inputs before starting any PDF rendering, visual review, or output generation.

Required proposal header fields:

```text
client_name: proposal recipient, for example Calvin Huang
quote_id: quote number, for example Q2248
revision: quote revision, for example Rev1
project_name: proposal project name
site_address: project site address
proposal_date: proposal date
```

Required drawing input:

```text
at least one readable joinery/cabinetry drawing or architectural drawing attachment
```

If the user already supplied all required values and the attachment is readable, reply with a concise confirmation and wait for approval:

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

If any required values are missing, ask for only the missing information:

```text
我可以生成 SOW，但开始前需要先补充 / 确认以下信息：
1. 客户姓名
2. Quote 编号和 revision
3. Proposal 日期
4. 客户橱柜图纸或建筑图纸 PDF

请直接按“客户姓名 / Quote / Project / Site / Date”回复，并上传图纸。
```

If a project name or site can be inferred from the message or file name, include the inferred value in the confirmation instead of asking for it again. If the proposal date is not supplied, ask whether to use today's date; do not silently choose a date for a customer-facing proposal.

Do not proceed to SOW generation when:

- No readable drawing attachment is available.
- The user has not confirmed the proposal header values.
- The only project facts come from a golden sample that the user described as an output standard.

After the user confirms the preflight values, store them in `project`, `proposal_header`, and `documents_provided` in `sow-extraction.json` with `source_type: client_confirmed` when they came from the Feishu user.

## Revision Recognition

Revision messages can be short and may not mention SOW explicitly. Treat them as revisions only when the conversation has an active `sow_id` or the user clearly points to an existing output.

Revision examples:

```text
Kitchen stone 全部排除
LED 也排除
Pantry 门只写 cladding
Master WIR mirror 改成 TBC
重新生成客户版 proposal
把 Laundry 的 open question 写得更清楚
```

If there is no active `sow_id`, ask:

```text
我没有找到当前会话中的 SOW。请先发送要处理的项目资料，或说明要修改哪一份 SOW。
```

If the target is ambiguous, ask:

```text
这条修改可能对应多个区域。请确认要修改 Kitchen、Pantry 还是其他区域？
```

## Attachment Intake

OpenClaw owns attachment retrieval and permissions. The skill should work with whichever attachment information OpenClaw exposes to the agent.

Expected attachment inventory fields when available:

```json
{
  "source_message_id": "msg-001",
  "file_name": "709 Riversdale Road, Camberwell_JD.pdf",
  "mime_type": "application/pdf",
  "local_path": "optional/local/path",
  "type_hint": "joinery_drawing"
}
```

If attachment content is unavailable, reply:

```text
我能看到这条 SOW 请求，但当前没有可读取的附件内容。请重新上传图纸、proposal 样本或客户需求文件。
```

For a new SOW, a proposal sample alone is not sufficient. If no customer joinery/cabinetry drawing or architectural drawing is available, ask the user to upload one before generation:

```text
我还没有看到可读取的客户橱柜图纸或建筑图纸。请上传图纸 PDF 后，我再开始生成 SOW。
```

Do not deep import Feishu extension internals from this skill. Use OpenClaw-provided message, file, and channel capabilities.

If a proposal sample or golden sample is attached, determine whether it is a current-project material or an output-quality reference:

- Current-project proposal/reference: use only facts that clearly belong to the current project.
- Golden sample/output standard: use structure, section order, and tone only; do not copy project facts, prices, finishes, hardware, lead times, or payment terms.

For PDF drawings, locate the local PDF file exposed by OpenClaw and render pages to PNG before visual review. The skill should not ask the model to analyze the PDF file path directly as an image. The rendered PNG pages are the source for visual drawing review, while the PDF metadata remains part of the source document inventory. Open rendered PNG files with the normal file `read` capability.

Do not use image generation or creative image production to create these PNG pages. Do not call `image` or `image_generate`, including list/status calls. The only valid conversion path is `scripts/render_pdf_pages.py` or an equivalent deterministic PDF renderer explicitly approved by the user.

After rendering, read `render-manifest.json`. If it reports `page_count_truncated: true`, rerender with a higher page cap before proceeding. Then build `intermediate/drawing-index.json` with `scripts/build_drawing_index.py` so page count, drawing numbers, and area title candidates are visible before visual review.

On retries after timeout, check the active SOW workspace with `scripts/sow_state.py outputs-status`. If returnable files already exist, send those files instead of restarting the drawing review.

## Feishu Reply Layers

Use layered replies instead of posting the full proposal in chat.

Recommended reply sequence:

1. Task acknowledgment.
2. Preflight field and drawing confirmation.
3. Source/attachment summary.
4. Processing progress.
5. SOW completion summary.
6. Key room preview.
7. Open question summary.
8. ZIP package and output file list.

Task acknowledgment:

```text
收到，我会先确认 proposal 基础信息和图纸，再基于本次消息和附件整理 SOW，不会生成最终报价金额。
```

Attachment summary:

```text
已识别资料：joinery drawing、proposal 样本、客户需求说明。接下来会整理 working areas、scope 和待确认项。
```

Completion summary:

```text
Use the generated `feishu-summary.md` as the completion reply body.
```

Revision summary:

```text
已更新：Kitchen stone 已标记为 excluded，并已重新生成 proposal。
```

## Output Files

Return one ZIP package as the primary deliverable when available:

```text
<project-slug>-sow.zip
```

The ZIP must contain these five core files:

```text
sow-extraction.json
proposal.md
proposal.docx
open-questions.md
feishu-summary.md
```

`output-manifest.json` should be kept in the output directory and included in the ZIP as a technical manifest. The five files above remain the customer-facing core files. For the demo, Markdown remains the canonical source output and `proposal.docx` is a formatted export. Do not promise high-fidelity Word/PDF export unless it is actually available.

If Feishu ZIP upload fails:

1. Do not silently rely on the platform `Media failed` message.
2. Tell the user the ZIP upload failed.
3. Send the five core files individually when possible.
4. If the user asks for email delivery, send the full ZIP package by email.
5. Use `delivery_refs` from `proposal_outputs` for user-facing filenames, not workspace `output/...` paths.

## Smoke Test Checklist

Use this checklist for Feishu integration smoke testing:

1. Send a new SOW trigger message with 709 attachments.
2. Confirm the skill acknowledges the task and states no final pricing will be generated.
3. Confirm client name, quote/revision, project, site, proposal date, and drawing availability are requested or confirmed before generation.
4. Confirm missing drawings are clearly requested when no joinery/cabinetry or architectural drawing is attached.
5. Confirm attachments are summarized or missing attachments are clearly requested.
6. Confirm PDF drawings are rendered to PNG pages before visual review.
7. Confirm `render-manifest.json` has no unrendered pages.
8. Confirm `drawing-index.json` is produced and covers all PDF pages.
9. Confirm `sow_id` is created or reused.
10. Confirm `sow-extraction.json`, `proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md` are produced.
11. Confirm the ZIP package is produced and contains the five core files plus `output-manifest.json`.
12. Confirm the Feishu response contains a concise summary, not the full proposal body.
13. Simulate or observe ZIP upload failure and confirm fallback wording is clear.
14. Send `Kitchen stone 全部排除`.
15. Confirm the same `sow_id` is used.
16. Confirm revision history is updated if `sow_state.py` is used.
17. Confirm updated output files are repackaged and returned.
