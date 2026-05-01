# Kitchman SOW Review Guardrails

Use these rules before finalizing `sow-extraction.json`, `proposal.md`, `proposal.docx`, or `open-questions.md`.

## Non-Negotiable Rules

- Do not generate final prices.
- Do not invent materials, finishes, dimensions, hardware, stone, lighting, appliances, lead times, or installation commitments.
- Do not hide uncertainty in client-facing prose.
- Do not treat the 709 case reference as proof for a different project.
- Do not treat a golden sample proposal as runtime project evidence.
- Do not copy golden sample facts such as client names, quote IDs, dates, prices, finish codes, hardware codes, lead times, or payment terms into a new project unless those facts appear in current-project inputs.
- Do not use scripts to parse drawings or match scope in the current demo version.
- PDF-to-PNG rendering is allowed only as a mechanical format conversion step.
- Do not use image generation or creative image production when preparing drawing page images.
- Do not call `image` or `image_generate`, including list/status calls, during SOW generation.
- Read rendered PNG drawing pages with the normal file `read` capability.
- Do not present visually ambiguous drawing details as confirmed scope.
- Do not manually write `proposal.md`, `proposal.docx`, or `open-questions.md` when `scripts/render_sow_outputs.py` is available.
- Do not write long page-by-page drawing commentary into the client-facing proposal.
- Do not generate proposal outputs from a truncated render. If `render-manifest.json` or `drawing-index.json` reports unrendered pages, rerender or clearly label the output as partial only with user approval.
- Do not place uncertain or supplier-responsibility items inside the confirmed working-area scope table. Move them to `TBC Items` and `Items Requiring Confirmation`.

## TBC Rules

Use `TBC` when:

- A rendered drawing page is too small, dense, cropped, rotated, blurred, or otherwise hard to read.
- Door finish is unclear.
- Panel finish is unclear.
- Carcass material is unclear.
- Hardware brand/model is unclear.
- Mirror, glass, stone, LED, appliance, plumbing, electrical, painting, or building works are not confirmed.
- A drawing shows an item but the supplier responsibility is unclear.
- A user revision is ambiguous.

## Confidence Rules

Use `high` only when the item is explicit in the supplied materials or user message.

Use `medium` when the item is visible or strongly implied but still requires human review.

Use `low` when the item is inferred, unclear, or based mainly on case reference.

## Source Type Rules

Use `observed_from_drawing` for visible drawing facts.

Use `client_confirmed` for explicit user messages or client notes.

Use `proposal_sample` for wording or structure copied from a sample proposal.

Use `case_reference` for 709 demo notes.

Use `inferred` only when needed, and pair it with `needs_confirmation`.

Use `unknown` when no reliable source exists.

## Information Priority Rules

When sources conflict, use this priority:

1. Current user message or explicit current-project requirement.
2. Current uploaded project files.
3. Approved company defaults or knowledge base content.
4. Visual observations from rendered drawing pages.
5. Model inference.

Golden samples sit outside this priority list. They define output form and quality, not project facts.

If a value only appears in a golden sample, use `TBC` or an open question for the current project.

## Exclusion Rules

Keep exclusions separate from included scope.

Common exclusions:

- Stone benchtops.
- Appliances.
- LED strips and electrical work.
- Plumbing.
- Building works.
- Painting.
- Door structure or operating hardware for cladding-only doors.
- Mirrors or glass when responsibility is unclear.

Do not put the same item in both TBC and exclusions. Use exactly one customer-facing state:

- Confirmed Kitchman scope: `included: true`.
- Responsibility or inclusion unclear: `included: "tbc"` plus an open question.
- Explicitly excluded: `included: false` or a clear exclusion entry.

High-risk items default to TBC unless the current project input confirms responsibility. This includes stone, lighting/LED, appliances, plumbing, electrical, mirrors, glass, shower screens/niches, fireplace/specialist contractor scope, building, painting, tiling, and plaster.

## Open Question Rules

Create an open question when:

- The proposal would otherwise imply a commitment.
- The estimator needs confirmation before pricing.
- The scope is visible but supplier responsibility is unclear.
- A finish or hardware selection is not confirmed.
- A user asks for something that conflicts with the current SOW.

Each open question should include:

```text
question
applies_to
reason
priority
```

## Final Review Checklist

- `proposal.md` contains no final price.
- `proposal.md` follows the formal Kitchman proposal structure, not an internal drawing-analysis memo.
- `proposal.md` includes working areas and finish schedule tables, even if many fields are `TBC`.
- `proposal.md` separates confirmed working-area scope from `TBC Items`.
- `proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md` were rendered from `sow-extraction.json` when the renderer was available.
- The ZIP package contains `sow-extraction.json`, `proposal.md`, `proposal.docx`, `open-questions.md`, `feishu-summary.md`, and `output-manifest.json`.
- `output-manifest.json` exists in the output directory and records package contents.
- `render-manifest.json` and `drawing-index.json` do not report unrendered pages.
- Unknown content is marked `TBC` or moved to open questions.
- Exclusions are explicit.
- Scope items include confidence/source information.
- Visual observations cite a source page or note when they came from rendered drawing pages.
- `sow-extraction.json`, `proposal.md`, `proposal.docx`, and `open-questions.md` agree on room counts and open question counts where applicable.
- `proposal_outputs` includes `workspace_refs`, `package_refs`, and `delivery_refs` after packaging.
- The output does not claim full automatic drawing interpretation.
- Feishu summary is concise and does not paste the full proposal.
