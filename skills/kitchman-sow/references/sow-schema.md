# Kitchman SOW Schema

`sow-extraction.json` is the canonical structured output. Generate the customer-facing proposal from this JSON rather than directly from raw drawing notes.

The schema remains `kitchman-sow.v1`, with v0.2 fields added for formal proposal rendering.

## Top-Level Shape

```json
{
  "schema_version": "kitchman-sow.v1",
  "sow_id": "sow-709-riversdale-road-20260425",
  "sow_status": "awaiting_review",
  "project": {},
  "proposal_header": {},
  "documents_provided": [],
  "source_documents": [],
  "rooms": [],
  "working_area_rows": [],
  "finish_schedule": [],
  "hardware_schedule": [],
  "standard_terms": {},
  "pricing": {},
  "exclusions": [],
  "special_notes": [],
  "open_questions": [],
  "review_flags": [],
  "proposal_outputs": {}
}
```

## Size Budget

Keep `sow-extraction.json` compact enough for Feishu runs:

- Target under 20 KB for normal demo projects.
- Use short scope descriptions.
- Use short evidence notes.
- Do not copy page-by-page visual notes into JSON.
- Prefer room-level evidence when the same drawing page supports multiple scope items.
- Keep top-level `open_questions` to the most important 12 unless exhaustive output is requested.

## Source Priority

Use this order when fields conflict:

1. Current user message or explicit current-project requirement.
2. Current uploaded project files.
3. Approved company defaults or knowledge base content.
4. Visual observations from rendered drawing pages.
5. Inference from model reasoning.

Golden samples are style and quality references only. They must not provide project facts, pricing, finishes, hardware, lead time, or payment terms for a new SOW.

## Project

```json
{
  "project_name": "709 Riversdale Road Camberwell",
  "project_address": "709 Riversdale Road, Camberwell",
  "client_name": "Calvin Huang",
  "quote_id": "Q2248",
  "requested_by": "from-openclaw",
  "source_type": "client_confirmed",
  "confidence": "high"
}
```

For a new SOW, `project_name`, `project_address`, `client_name`, and `quote_id` should be confirmed in Feishu before output generation. Do not rely on a golden sample for these fields.

## Proposal Header

Use this object to render the formal proposal header.

```json
{
  "client_name": "Calvin Huang",
  "salutation": "Calvin",
  "proposal_date": "18 March 2026",
  "quote_id": "Q2248",
  "revision": "Rev1",
  "project_name": "709 Riversdale Road Camberwell",
  "site_address": "709 Riversdale Road, Camberwell",
  "prepared_by": "Kitchman",
  "source_type": "client_confirmed",
  "confidence": "high"
}
```

For a new SOW, do not generate the customer-facing proposal until `client_name`, `proposal_date`, `quote_id`, `revision`, `project_name`, and `site_address` are confirmed by the user or current-project materials. If a field is unknown during intake, ask the user before rendering. Do not copy header facts from a golden sample.

## Source Document

```json
{
  "id": "doc-001",
  "source_message_id": "msg-001",
  "file_name": "709 Riversdale Road, Camberwell_JD.pdf",
  "type": "joinery_drawing",
  "source_type": "uploaded_attachment",
  "confidence": "high",
  "notes": []
}
```

Allowed `type` values:

```text
joinery_drawing
cabinetry_drawing
architectural_drawing
proposal_sample
finish_schedule
fixture_schedule
client_note
unknown
```

For a new SOW, at least one `joinery_drawing`, `cabinetry_drawing`, or `architectural_drawing` source document is required before drawing review starts.

## Document Provided Row

Use this for the `Documents Provided by Client` table.

```json
{
  "type": "Joinery Drawing",
  "file_name": "709 Riversdale Road, Camberwell_JD.pdf",
  "received_on": "TBC",
  "source_document_id": "doc-001",
  "confidence": "high"
}
```

## Room

```json
{
  "id": "room-gf-kitchen",
  "name": "GF Kitchen",
  "level": "Ground Floor",
  "scope_items": [],
  "finishes": [],
  "exclusions": [],
  "special_notes": [],
  "open_questions": [],
  "source_pages": [4, 5],
  "drawing_refs": ["JD 04", "JD 05"],
  "evidence_summary": "Kitchen plan and elevations show overheads, base units and appliance towers.",
  "source_type": "observed_from_drawing",
  "confidence": "medium",
  "evidence": []
}
```

## Working Area Row

Use this for the customer-facing `Joinery Working Areas` table. This row is the rendered business summary of one room's scope.

```json
{
  "room_id": "room-gf-kitchen",
  "room": "GF Kitchen",
  "description": "Overheads / base cabinets / drawers / fridge cupboard / oven tower / wall panels.",
  "joinery_finish": "Door/Panel: TBC; Carcass: TBC",
  "source_pages": [4, 5],
  "drawing_refs": ["JD 04", "JD 05"],
  "evidence_summary": "Confirmed scope is visible on kitchen plan and elevations.",
  "status": "awaiting_review",
  "source_type": "observed_from_drawing",
  "confidence": "medium"
}
```

Rules:

- One row per proposal room/area.
- Keep descriptions concise, client-facing, and limited to confirmed scope.
- Do not mix TBC scope items into the working-area description. Use `scope_items` with `included: "tbc"` and `open_questions` for uncertain items.
- Include short `source_pages` and `drawing_refs` so the proposal can show compact traceability.
- Do not include evidence notes or page-by-page observations.
- Use `TBC` in `joinery_finish` when no current-project finish source exists.

## Scope Item

```json
{
  "id": "scope-gf-kitchen-overheads",
  "item": "Overhead cabinets",
  "category": "cabinet",
  "included": true,
  "description": "Provide overhead cabinets as shown in the kitchen joinery drawings.",
  "source_pages": [4, 5],
  "drawing_refs": ["JD 04", "JD 05"],
  "evidence_summary": "Shown in kitchen elevations.",
  "source_type": "observed_from_drawing",
  "confidence": "medium",
  "review_status": "approved_for_proposal",
  "evidence": []
}
```

Allowed `included` values:

```text
true
false
tbc
```

These states are mutually exclusive in customer-facing output:

- `true`: confirmed Kitchman joinery scope. It may render in `Joinery Working Areas`.
- `tbc`: visible or requested item where inclusion, supplier responsibility, finish, or hardware is not confirmed. It must render in `TBC Items` / open questions, not in confirmed scope or exclusions.
- `false`: explicitly excluded item. It may render in `Exclusions`, not in confirmed scope or TBC.

High-risk categories such as stone, lighting/LED, appliance, plumbing, electrical, mirror, glass, shower, fireplace, building, painting, tiling, and plaster should default to `tbc` unless the current project input explicitly confirms Kitchman responsibility.

Allowed `category` values:

```text
cabinet
drawer
panel
shelf
door
mirror
glass
hardware
stone
lighting
appliance
other
```

Allowed `source_type` values:

```text
observed_from_drawing
client_confirmed
company_default
case_reference
inferred
unknown
```

Allowed `confidence` values:

```text
high
medium
low
```

Allowed `review_status` values:

```text
unreviewed
needs_confirmation
approved_for_proposal
excluded_from_proposal
```

Review status guidance:

- Use `approved_for_proposal` when the item is included in `proposal.md`.
- Use `needs_confirmation` when `included` is `tbc` or responsibility is unclear.
- Use `excluded_from_proposal` when the item is explicitly excluded.
- Avoid leaving items as `unreviewed` after proposal generation.
- Include `source_pages`, `drawing_refs`, or `evidence_summary` for included items when the item comes from drawing review.

## Evidence

```json
{
  "file_name": "709 Riversdale Road, Camberwell_JD.pdf",
  "page_number": 4,
  "drawing_ref": "GF Kitchen",
  "view_ref": "Elevation",
  "message_ref": "msg-001",
  "evidence_type": "visual_reading",
  "confidence": "medium",
  "note": "Kitchen overhead and base cabinet scope visible in drawing."
}
```

Allowed `evidence_type` values:

```text
text_layer
visual_reading
client_note
proposal_sample
case_reference
inferred
```

Use evidence sparingly. Do not repeat the same long evidence object for every item in a room.

## Finish Schedule Row

```json
{
  "item_abbr": "TBC",
  "description": "Door/panel finish",
  "area": "GF Kitchen",
  "status": "TBC",
  "source_type": "unknown",
  "confidence": "low"
}
```

## Hardware Schedule Row

```json
{
  "item_abbr": "TBC",
  "description": "Drawer runners",
  "area": "GF Kitchen",
  "status": "TBC",
  "source_type": "unknown",
  "confidence": "low"
}
```

## Standard Terms

Use current-project input or approved company defaults only. If not available, use safe placeholders.

```json
{
  "lead_time": {
    "value": "TBC",
    "status": "estimator_required",
    "source_type": "unknown"
  },
  "installation": {
    "value": "TBC",
    "status": "estimator_required",
    "source_type": "unknown"
  },
  "payment_terms": {
    "value": "TBC",
    "status": "estimator_required",
    "source_type": "unknown"
  }
}
```

## Pricing

No final pricing in demo output.

```json
{
  "status": "estimator_required",
  "note": "Pricing is excluded from this demo output and must be completed by the estimator."
}
```

Avoid these fields anywhere in the JSON:

```text
final_price
total_price
quote_total
grand_total
subtotal
amount_due
```

## Proposal Outputs

```json
{
  "sow_extraction_json": "output/sow-extraction.json",
  "proposal_md": "output/proposal.md",
  "proposal_docx": "output/proposal.docx",
  "open_questions_md": "output/open-questions.md",
  "feishu_summary_md": "output/feishu-summary.md",
  "sow_package_zip": "output/709-riversdale-road-camberwell-sow.zip",
  "output_manifest_json": "output/output-manifest.json",
  "workspace_refs": {
    "sow_extraction_json": "output/sow-extraction.json",
    "proposal_md": "output/proposal.md",
    "proposal_docx": "output/proposal.docx",
    "open_questions_md": "output/open-questions.md",
    "feishu_summary_md": "output/feishu-summary.md",
    "sow_package_zip": "output/709-riversdale-road-camberwell-sow.zip",
    "output_manifest_json": "output/output-manifest.json"
  },
  "package_refs": {
    "sow_extraction_json": "sow-extraction.json",
    "proposal_md": "proposal.md",
    "proposal_docx": "proposal.docx",
    "open_questions_md": "open-questions.md",
    "feishu_summary_md": "feishu-summary.md",
    "output_manifest_json": "output-manifest.json"
  },
  "delivery_refs": {
    "sow_extraction_json": "sow-extraction.json",
    "proposal_md": "proposal.md",
    "proposal_docx": "proposal.docx",
    "open_questions_md": "open-questions.md",
    "feishu_summary_md": "feishu-summary.md",
    "sow_package_zip": "709-riversdale-road-camberwell-sow.zip",
    "output_manifest_json": "output-manifest.json"
  }
}
```

`proposal.md`, `proposal.docx`, `open-questions.md`, and `feishu-summary.md` should be rendered from this JSON with `scripts/render_sow_outputs.py --docx` whenever available.

Path groups:

- `workspace_refs`: workspace-relative paths used by the agent and local validator.
- `package_refs`: filenames inside the primary SOW ZIP package. The package contains the five core customer files plus `output-manifest.json`.
- `delivery_refs`: filenames the user may see after Feishu download or fallback single-file delivery. Use this group in Feishu summaries.

## Open Question

```json
{
  "id": "question-gf-kitchen-door-finish",
  "question": "Confirm kitchen door and panel finish.",
  "applies_to": "GF Kitchen",
  "reason": "Finish is not sufficiently confirmed from the provided materials.",
  "priority": "high",
  "source_type": "unknown",
  "confidence": "low"
}
```

Allowed `priority` values:

```text
high
medium
low
```

## Review Flag

```json
{
  "id": "flag-missing-finish-schedule",
  "severity": "warning",
  "message": "No current-project finish schedule was supplied; finish fields are TBC.",
  "applies_to": "proposal"
}
```

Allowed `severity` values:

```text
error
warning
info
```
