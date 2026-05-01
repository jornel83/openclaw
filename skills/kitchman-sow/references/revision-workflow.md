# Revision Workflow

Use this reference when a Feishu user asks to modify an existing Kitchman SOW.

## Boundary

- The agent interprets the user's revision against the current `sow-extraction.json`.
- Do not use rule-matching scripts to interpret revision text.
- `sow_state.py` only records revision metadata.
- `render_sow_outputs.py` only regenerates output files from JSON.
- If the target room, item, or responsibility is ambiguous, ask a short follow-up question.

## Revision Flow

1. Resolve the active `sow_id` from the current conversation or user message.
2. Call `scripts/sow_state.py outputs-status`.
3. If `sow-extraction.json` is missing, ask the user to provide the project materials or target SOW.
4. Load `output/sow-extraction.json`.
5. Apply the requested change to the structured JSON.
6. Keep uncertain changed values as `TBC` or open questions.
7. Run `scripts/render_sow_outputs.py --docx`.
8. Run `scripts/validate_sow_outputs.py`.
9. Call `scripts/sow_state.py append-revision` with summary metadata.
10. Reply with the revision summary and output file list.

For local plumbing validation, run:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/smoke_v03.py
```

## Supported Revision Types

- Exclude a scope item.
- Mark a scope item, finish, material, hardware, or responsibility as `TBC`.
- Add a confirmed scope item from the user's explicit instruction.
- Update `working_area_rows` wording.
- Add, update, or close an open question.
- Add or update an exclusion.
- Update client/project metadata when the user provides it.

## JSON Update Rules

- Keep `rooms`, `working_area_rows`, `exclusions`, and `open_questions` consistent.
- Do not delete evidence fields unless the user explicitly says the prior evidence is wrong.
- If a confirmed scope becomes excluded, set the item to excluded or TBC and add/update `exclusions`.
- If a finish becomes unknown, set the finish to `TBC` and add/update an open question.
- If the user supplies a confirmed fact, set `source_type` to `client_confirmed` and `confidence` to `high`.
- Update `sow_status` to `revision_completed` after outputs are regenerated.

## Direct Script Invocation

Render updated outputs:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/render_sow_outputs.py --input /absolute/path/to/sow-workspace/output/sow-extraction.json --output-dir /absolute/path/to/sow-workspace/output --docx
```

Append revision metadata:

```text
python3 /absolute/path/to/skills/kitchman-sow/scripts/sow_state.py append-revision --workspace /absolute/path/to/sow-workspace --sow-id sow-709-riversdale-road-20260426 --message "Kitchen stone 全部排除" --summary "Kitchen stone moved to exclusions" --change-type exclusion --affected-area "GF Kitchen" --changed-file output/sow-extraction.json --changed-file output/proposal.md --changed-file output/proposal.docx --changed-file output/open-questions.md --changed-file output/feishu-summary.md
```

## Feishu Reply Pattern

```text
已更新：Kitchen stone 已标记为 excluded，并已重新生成 proposal。

输出文件：
- sow-extraction.json
- proposal.md
- proposal.docx
- open-questions.md
- feishu-summary.md
```

Do not paste the full proposal into Feishu.
