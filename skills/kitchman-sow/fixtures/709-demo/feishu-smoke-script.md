# 709 Feishu Smoke Script

Use this script to verify the Feishu interaction flow.

## Step 1: New SOW Trigger

User message:

```text
我现在要出一下 709 Riversdale Road 项目的 SOW，上传的文件是项目图纸和客户定制需求。
```

Attachments:

```text
709 Riversdale Road, Camberwell_JD_客户橱柜图纸.pdf
```

The human-written proposal can be used separately as a golden sample for output-quality review, but it is not runtime project input for this smoke script.

Expected skill behavior:

```text
收到，我会先确认 proposal 基础信息和图纸，再基于本次消息和附件整理 SOW，不会生成最终报价金额。
```

Expected preflight prompt:

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

Expected output:

```text
709-riversdale-road-camberwell-sow.zip
```

## Step 2: Summary Reply

Expected reply shape:

```text
SOW 已生成。

识别到 1 份资料、3 个示例区域、4 个 confirmed scope items、3 个 TBC items、4 个待确认问题。
proposal 已按 Kitchman 正式文档结构整理，价格字段已留空，没有生成最终报价金额。

关键预览：
- GF Kitchen ...
- Pantry ...
- Master WIR ...

输出文件：
- 709-riversdale-road-camberwell-sow.zip

ZIP 内容：
- sow-extraction.json
- proposal.md
- proposal.docx
- open-questions.md
- feishu-summary.md
- output-manifest.json
```

## Step 3: ZIP Fallback

If the ZIP attachment fails in Feishu, expected fallback behavior:

```text
ZIP 附件上传失败，我先发送 5 个核心文件作为 fallback；如需完整 ZIP，我可以再通过邮箱发送。
```

The skill must not leave only the platform `Media failed` message as the user-facing result.

## Step 4: First Revision

User message:

```text
Kitchen stone 全部排除
```

Expected behavior:

- Reuse the active `sow_id`.
- Update GF Kitchen stone from `tbc` to excluded.
- Add or update an exclusion note.
- Reassemble `proposal.md`.
- Reassemble `proposal.docx`.
- Append a revision record if using `sow_state.py`.

Expected reply:

```text
已更新：Kitchen stone 已标记为 excluded，并已重新生成 proposal。
```

## Step 5: Second Revision

User message:

```text
Pantry 门只写 cladding
```

Expected behavior:

- Keep Pantry scope as cladding only.
- Keep door structure and hardware as excluded or TBC unless explicitly confirmed.
- Reassemble `proposal.md`.
- Reassemble `proposal.docx`.

Expected reply:

```text
已更新：Pantry door scope 保留为 cladding only，door structure 和 hardware 仍需确认或排除。
```

## Step 6: Missing Active SOW

User message in a fresh conversation:

```text
LED 也排除
```

Expected reply:

```text
我没有找到当前会话中的 SOW。请先发送要处理的项目资料，或说明要修改哪一份 SOW。
```

## Pass Criteria

- Trigger message routes to `kitchman-sow`.
- The skill does not generate final prices.
- The response is layered and concise.
- A ZIP package is returned as the primary deliverable.
- The ZIP package contains the five core files plus `output-manifest.json`.
- ZIP attachment failure has an explicit fallback message.
- Revisions reuse the same `sow_id`.
- `proposal.docx` includes the Kitchman logo header/footer structure.
- Revision metadata is recorded in `sow-state.json`.
- Ambiguous revision without active state results in a clarification question.

Before or after the Feishu smoke, run:

```bash
python3 skills/kitchman-sow/scripts/smoke_v04.py
python3 skills/kitchman-sow/scripts/smoke_v05.py
```
