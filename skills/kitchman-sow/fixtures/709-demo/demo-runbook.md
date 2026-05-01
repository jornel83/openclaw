# 709 Demo Runbook

This runbook is for customer-facing demonstrations of the `kitchman-sow` skill. It focuses on the visible Feishu experience and the review quality of the generated SOW outputs.

## Demo Objective

Show that a user can:

1. Trigger SOW generation from a Feishu message.
2. Upload drawing materials and optionally compare against a golden sample proposal standard.
3. Receive a concise progress and result summary.
4. Review the delivered ZIP containing `proposal.md`, `proposal.docx`, `open-questions.md`, `feishu-summary.md`, `sow-extraction.json`, and `output-manifest.json`.
5. Send follow-up revision messages in the same conversation.
6. See updated outputs without opening a separate project workspace.

## Pre-Demo Checklist

- Confirm `fixtures/709-demo/output/sow-extraction.json` exists.
- Confirm `fixtures/709-demo/output/proposal.md` exists.
- Confirm `fixtures/709-demo/output/proposal.docx` exists.
- Confirm `fixtures/709-demo/output/open-questions.md` exists.
- Confirm `fixtures/709-demo/output/feishu-summary.md` exists.
- Confirm `fixtures/709-demo/output/709-riversdale-road-camberwell-sow.zip` exists.
- Confirm `fixtures/709-demo/output/output-manifest.json` exists.
- Run output validation:

```bash
python3 skills/kitchman-sow/scripts/validate_sow_outputs.py --root skills/kitchman-sow/fixtures/709-demo
```

Run the local v0.5 delivery smoke test:

```bash
python3 skills/kitchman-sow/scripts/smoke_v05.py
```

Expected result:

```json
{
  "status": "ok"
}
```

## Demo Materials

Use these materials as the visible project context:

```text
709 Riversdale Road, Camberwell_JD_客户橱柜图纸.pdf
```

Use the human-written proposal only as a golden sample for output quality review. Do not treat it as runtime project input for demo generation.

Use the fixture outputs as the expected result:

```text
fixtures/709-demo/output/sow-extraction.json
fixtures/709-demo/output/proposal.md
fixtures/709-demo/output/proposal.docx
fixtures/709-demo/output/open-questions.md
fixtures/709-demo/output/feishu-summary.md
fixtures/709-demo/output/709-riversdale-road-camberwell-sow.zip
```

## Demo Script

### Step 1: Start The SOW

User says in Feishu:

```text
我现在要出一下 709 Riversdale Road 项目的 SOW，上传的文件是项目图纸和客户定制需求。
```

Expected reply:

```text
收到，我会先确认 proposal 基础信息和图纸，再基于本次消息和附件整理 SOW，不会生成最终报价金额。
```

Explain to the customer:

```text
The skill is triggered from Feishu. It does not require the user to open a project page.
```

### Step 2: Show Source Summary

Expected preflight confirmation shape:

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

Expected reply shape:

```text
已识别资料：joinery drawing、客户需求说明。golden sample 仅用于输出格式评估。接下来会整理 working areas、scope 和待确认项。
```

Explain:

```text
The skill treats uploaded project materials as current conversation context. Golden samples are style standards only, not project fact sources.
```

### Step 3: Show Generated Result

Use `fixtures/709-demo/output/feishu-summary.md` as the expected Feishu summary.

Expected files:

```text
709-riversdale-road-camberwell-sow.zip
```

Explain:

```text
The ZIP is the primary deliverable. It contains the structured JSON, Markdown proposal, Word proposal, open questions, Feishu summary, and technical manifest.
```

### Step 4: Open Proposal

Open `fixtures/709-demo/output/proposal.md`.

Highlight:

- Header uses confirmed client, quote, project, site, and date from the Feishu preflight.
- Joinery working areas are rendered as a formal proposal table.
- TBC items are separated from confirmed scope.
- Joinery finish schedule is rendered as a formal table.
- Exclusions are separate from included scope.
- TBC items and exclusions do not conflict.
- Pricing is explicitly excluded.
- Items requiring confirmation are visible.

### Step 5: Open Questions

Open `fixtures/709-demo/output/open-questions.md`.

Highlight:

- Estimator can quickly see unresolved items.
- The skill does not hide uncertainty in customer-facing prose.
- Missing finish, stone, pantry door hardware, and mirror responsibility are surfaced.

### Step 6: Demonstrate Revision

User says:

```text
Kitchen stone 全部排除
```

Expected behavior:

- Reuse active `sow_id`.
- Update GF Kitchen stone from TBC to excluded.
- Reassemble proposal.
- Regenerate proposal.docx.
- Record revision if `sow_state.py` is used.

Expected reply:

```text
已更新：Kitchen stone 已标记为 excluded，并已重新生成 proposal。
```

### Step 7: Demonstrate Ambiguous Revision Handling

In a fresh conversation without active SOW, user says:

```text
LED 也排除
```

Expected reply:

```text
我没有找到当前会话中的 SOW。请先发送要处理的项目资料，或说明要修改哪一份 SOW。
```

Explain:

```text
The skill should not guess which project or room to modify. It asks for context when no active sow_id exists.
```

## Quality Review Checklist

Review `proposal.md` against these criteria:

- It is readable by a customer.
- It does not include final pricing.
- It does not overstate uncertain materials or finishes.
- It separates included scope from exclusions.
- It uses TBC visibly.
- It has a clear pricing exclusion.
- It has working areas grouped by room.
- It separates confirmed working areas from TBC items.
- It includes estimator-facing confirmation items.

Review `proposal.docx` against these criteria:

- It opens as a readable Word document.
- It contains the same proposal sections as `proposal.md`.
- Tables are visible enough for customer demo review.
- It contains the Kitchman logo header and footer structure.

Review `sow-extraction.json` against these criteria:

- It has `schema_version`.
- It has `sow_id`.
- It has `project`.
- It has `proposal_header`.
- It has `documents_provided`.
- It has `source_documents`.
- It has `rooms`.
- It has `working_area_rows`.
- It has `standard_terms`.
- Scope items include `confidence`.
- Scope items include `source_type`.
- Open questions are present.

Review `open-questions.md` against these criteria:

- It is not empty.
- Questions are actionable.
- High-impact pricing or scope blockers are visible.
- TBC items from the proposal are represented.

## Pass Criteria

The demo passes when:

- The Feishu trigger flow is understandable.
- Output files are present and validation passes.
- The local v0.5 smoke test passes.
- The local v0.5 smoke test passes.
- Proposal quality is acceptable for estimator review.
- Open questions are useful.
- Revision flow is clear.
- The customer understands the demo does not claim full automatic drawing interpretation.

## Demo Boundaries

State these boundaries clearly if asked:

- The demo does not generate final prices.
- The demo does not run PDF/OCR/docx parsing scripts for content interpretation.
- The demo does not use enterprise knowledge base retrieval.
- The demo exports a branded DOCX, but visual layout QA still depends on the runtime having a DOCX renderer such as LibreOffice.
- If Feishu ZIP upload fails, the skill must state that clearly and fall back to individual files or email ZIP delivery.
- The demo uses the 709 reference fixture to demonstrate the business workflow.
