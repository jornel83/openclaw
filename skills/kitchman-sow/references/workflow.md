# Kitchman SOW Workflow

## Trigger

Use this skill when a Feishu user asks to generate, revise, or package a Kitchman SOW/proposal from project materials.

For detailed trigger recognition, attachment handling, and Feishu reply layering, read `references/feishu-integration.md`.

Typical trigger messages:

```text
我现在要出一下 709 Riversdale Road 项目的 SOW，上传的文件是项目图纸和客户定制需求。
帮我根据这些图纸生成一版 Kitchman proposal 的 SOW，价格先空着。
根据这份 proposal 模板和客户图纸，先整理 working areas 和 open questions。
```

## New SOW Flow

1. Acknowledge the task in Feishu.
2. Run preflight intake before creating output files: confirm client name, quote ID/revision, project name, site address, proposal date, and at least one readable joinery/cabinetry or architectural drawing attachment.
3. If required proposal header fields or drawings are missing, ask a concise follow-up question and stop.
4. If all required fields and drawings are present, summarize them and wait for the user to confirm or correct them.
5. Resolve or create a `sow_id` only after preflight confirmation.
6. If this looks like a retry or timeout recovery, call `scripts/sow_state.py outputs-status` for the active workspace.
7. If `outputs-status` returns `return_existing_outputs`, return the existing files immediately.
8. If `outputs-status` returns `render_outputs_then_return`, call `scripts/render_sow_outputs.py --docx`, then `scripts/package_sow_outputs.py`, and return the package without re-reading the PDF.
9. Build a source document inventory from the confirmed attachment metadata and contents.
10. For PDF drawings, render pages to PNG before visual review.
11. Read only the references needed for the current step. For the fast path, read `sow-schema.md` and `review-guardrails.md`; skip `proposal-template.md` because Markdown is rendered by script.
12. Generate `intermediate/drawing-visual-notes.md` when drawing pages were reviewed.
13. Generate `sow-extraction.json` as the canonical structured state.
14. Call `scripts/render_sow_outputs.py --docx` to render `proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md`.
15. Call `scripts/package_sow_outputs.py` to package the five core files into a ZIP and write `output-manifest.json`.
16. Run `scripts/validate_sow_outputs.py` when available.
17. Return the generated `feishu-summary.md` content and the SOW ZIP package as the primary file.
18. If the ZIP upload fails in Feishu, explicitly state the failure and send the five core files individually or offer email ZIP delivery.

Preflight confirmation should not be treated as a keyword script. Use the conversation and attachment context naturally, but enforce this gate strictly for new SOW generation. Missing proposal header fields may be marked `TBC` inside internal notes only; they should not produce a customer-facing proposal header.

If using `scripts/sow_state.py`, use only direct Python file invocation and the supported `init` command. Do not run shell-chained commands such as `cd ... && python3 ... || echo ...`; OpenClaw may reject them before execution. If the state script cannot be called safely, generate the `sow_id` manually and continue the SOW workflow.

## PDF Drawing Visual Intake Flow

Use this flow when the user uploads architectural, joinery, or cabinetry drawings as PDF files.

1. Locate the local PDF path exposed by OpenClaw.
2. Create or reuse the SOW workspace.
3. Render the PDF pages to PNG with `scripts/render_pdf_pages.py`.
4. Read `render-manifest.json` to identify the rendered page images and page coverage.
5. If `page_count_truncated` is true, rerender with a higher `--max-pages` before visual review. Do not produce SOW outputs from an intentionally truncated drawing set unless the user explicitly approves partial coverage.
6. Build `intermediate/drawing-index.json` with `scripts/build_drawing_index.py`.
7. Read `drawing-index.json` before visual review to confirm source page count, rendered page count, unrendered pages, drawing numbers, and area title candidates.
8. Read and visually review the PNG pages in small batches using normal file reads.
9. Create `intermediate/drawing-visual-notes.md` with compact page observations.
10. Generate `sow-extraction.json` from the visual notes, message text, and references.
11. Mark unclear drawing details as `TBC` or add them to `open-questions.md`.

Direct PDF visual analysis is not the expected path for drawing PDFs. Treat the PDF as a container and use the rendered PNG pages as the visual source.

Do not use any model-based image generation, drawing, or creative image production capability for this step. Do not call `image` or `image_generate`, including list/status calls. The PNG pages must come from `scripts/render_pdf_pages.py`, preserving the uploaded drawing pages. This is a file conversion task, not an image creation task.

Rendered PNG pages should be opened with the normal file `read` capability. Do not call a separate visual-analysis helper for the rendered pages; if a PNG cannot be read directly, stop and report the blocker instead of switching tools.

For large PDFs, do not wait until the end to write files. Persist `intermediate/drawing-visual-notes.md` as soon as page review is complete, then write only the structured JSON manually:

1. `output/sow-extraction.json`
2. Run `scripts/render_sow_outputs.py --docx`
3. Run `scripts/package_sow_outputs.py`
4. Optionally run `scripts/validate_sow_outputs.py`

If the model times out after writing `sow-extraction.json`, the next run should call `scripts/render_sow_outputs.py --docx`, package the outputs, and return files instead of re-reading the PDF.

If the model times out after writing `proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md`, the next run should call `scripts/sow_state.py outputs-status`, package the existing files if the ZIP is missing, and return the package instead of re-rendering or re-reading drawings.

If PDF rendering fails, do not continue as if the SOW is generated. Reply with a concise blocker message:

```text
图纸页面渲染失败，暂时无法基于图片生成 SOW。请管理员确认服务器已安装 PyMuPDF 或 Poppler PDF 渲染依赖。
```

Safe render invocation:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/render_pdf_pages.py --pdf /absolute/path/to/input.pdf --output-dir /absolute/path/to/sow-workspace/intermediate/rendered-pages/doc-001 --max-pages 100 --dpi 160
```

The render script is only a format converter. Do not use scripts to OCR, parse drawings, identify rooms, extract scope, or decide inclusions.

Safe drawing index invocation:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/build_drawing_index.py --pdf /absolute/path/to/input.pdf --render-manifest /absolute/path/to/sow-workspace/intermediate/rendered-pages/doc-001/render-manifest.json --output /absolute/path/to/sow-workspace/intermediate/drawing-index.json
```

The drawing index script is only a page coverage and title-candidate helper. It may extract embedded PDF text but must not be treated as proof of joinery scope.

## Time Budget Rules

Use these rules to avoid Feishu request timeouts:

- Do not manually compose `proposal.md`, `proposal.docx`, or `open-questions.md`; always render them from JSON.
- Keep visual notes short: one line per page plus a compact room summary.
- Keep JSON descriptions short and business-focused.
- Do not duplicate the same long evidence note across many scope items.
- Prefer room-level evidence and short `source_type` / `confidence` fields.
- Cap the top-level open-question list to the most important 12 questions unless the user asks for exhaustive detail.
- After `sow-extraction.json` is written, do not read additional reference files; render outputs and reply.
- If the request is close to timeout or already has generated files, stop analysis and return the generated file paths/summary.

## Progress Reply Pattern

Use short progress replies:

```text
收到，我会先确认 proposal 基础信息和图纸，再整理 SOW，不会生成最终报价金额。
```

```text
基础信息已确认：客户、Quote、Project、Site 和 Date 已记录。资料已识别：图纸、proposal 样本和客户需求说明。接下来会整理 working areas、scope 和待确认项。
```

```text
图纸页面已转为 PNG，接下来会基于页面图片整理 room scope 和待确认项。
```

```text
SOW 已生成。proposal 已按 Kitchman 正式文档结构整理，价格字段已留空，低置信度内容已进入待确认项。
```

## Formal Proposal Assembly Flow

Use this flow after drawing review is complete.

1. Write or update `sow-extraction.json` first.
2. Populate `proposal_header`, `documents_provided`, `working_area_rows`, `finish_schedule`, `hardware_schedule`, `standard_terms`, `pricing`, `exclusions`, and `open_questions`.
3. Client name, quote ID/revision, project name, site address, and proposal date should come from the confirmed Feishu preflight. If any of these remain unknown, stop and ask the user to confirm them before customer-facing output.
4. If finish schedule, hardware schedule, lead time, or payment terms are not supplied by current project inputs, use `TBC` or `Estimator to complete`.
5. Render `proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md` from the structured JSON using `scripts/render_sow_outputs.py --docx`.
6. Package the output with `scripts/package_sow_outputs.py`.
7. Use `references/proposal-template.md` only as a fallback if the render script is unavailable.
8. Validate the output set.

Do not write the proposal directly from page-by-page drawing notes. Page observations are evidence for `sow-extraction.json`; the customer-facing proposal is assembled from the structured state.

Safe markdown render invocation:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/render_sow_outputs.py --input /absolute/path/to/sow-workspace/output/sow-extraction.json --output-dir /absolute/path/to/sow-workspace/output --docx
```

The markdown renderer is a formatter only. It must not be used to infer rooms, parse drawings, or decide inclusions.

Safe ZIP package invocation:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/package_sow_outputs.py --output-dir /absolute/path/to/sow-workspace/output
```

After the renderer and packager run, use `feishu-summary.md` as the Feishu reply body and send the ZIP as the primary deliverable. Do not regenerate a separate long final response. If platform upload fails, use the same summary plus a short fallback note and attach the five core files individually.

## Golden Sample Use

Human-written SOW/proposal files are golden samples only when the user describes them that way.

Allowed:

- Mimic section order, table-first layout, business tone, and proposal completeness.
- Use them as evaluation standards for whether the output looks like a formal Kitchman proposal.

Not allowed:

- Copy project facts, client names, quote numbers, dates, prices, finish codes, hardware codes, lead times, payment terms, or room-specific decisions into a new project.
- Treat a golden sample as evidence for the current project's scope.

## Revision Flow

Revision messages reuse the active `sow_id` in the same conversation when possible. For the detailed v0.3 revision workflow, read `references/revision-workflow.md`.

Examples:

```text
Kitchen stone 全部排除
LED 也排除
Pantry 门只写 cladding
Master WIR mirror 改成 TBC
```

For each revision:

1. Load current SOW state if available.
2. Interpret the user's requested change against the existing SOW JSON.
3. If the target is ambiguous, ask a follow-up question instead of guessing.
4. Update the relevant room, scope item, finish, exclusion, or open question.
5. Reassemble `proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md`.
6. Append a revision record to `sow-state.json` when using `sow_state.py`.
7. Reply with a change summary and updated output list.

Do not use a rule-matching script to interpret revisions in the current demo version.
Do not let state-script failures block the proposal update; state tracking is helpful but optional.

## Feishu Output Structure

Return concise text and files instead of pasting the full proposal into chat.

Suggested message:

```text
SOW 已生成。

识别到 {source_count} 份资料、{room_count} 个区域、约 {scope_item_count} 个 scope items、{open_question_count} 个待确认问题。
proposal 已按 Kitchman 正式文档结构整理，价格字段已留空，没有生成最终报价金额。

关键预览：
- GF Kitchen: overheads, base cabinets, drawers, fridge cupboard, oven tower, wall panel.
- Pantry: cladding only; door structure and hardware TBC.
- Laundry / WIR / Robe: 已整理核心 joinery scope，低置信度项已进入待确认。

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

## Missing Information

Ask follow-up questions when:

- There are no attachments.
- There is no readable joinery/cabinetry drawing or architectural drawing.
- The client name, quote ID/revision, project name, site address, or proposal date is missing or not confirmed for a new SOW.
- A requested revision could apply to multiple rooms/items.
- A material, finish, hardware, stone, mirror, glass, lighting, or appliance detail is unclear.
- The user asks for pricing or final quote totals.

Keep follow-up questions short and actionable.
