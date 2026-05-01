# Kitchman Proposal Template

Generate `proposal.md` from `sow-extraction.json`. The proposal should read like a formal Kitchman client proposal, while remaining safe for estimator review.

Do not use a golden sample as a project data source. Use it only to mirror format, section order, and tone.

## Required Sections

```markdown
# Project Proposal

**{client_name_or_tbc}**

**{proposal_date_or_tbc}**

**Quote: {quote_id_or_to_be_confirmed} {revision_or_empty}**

**Project: {project_name_or_tbc}**

**Site:** {site_address_or_tbc}

Dear {salutation_or_client},

{short_intro}

## Design and Planning

## Documents Provided by Client

## Joinery Working Areas

## Joinery Finish Schedule

## Shop Drawings and Site Remeasure

## Material Preparation and Production

## Joinery Delivery

## Joinery Installation

## Pricing

## Exclusions

## Lead Time

## Payment Terms

## Items Requiring Confirmation

{closing_and_signature}
```

## Header Rules

- Use `proposal_header` when present.
- Use `project` fields as fallback.
- For new SOW generation, client name, quote ID/revision, date, project, and site must be collected or confirmed in Feishu before rendering the customer-facing proposal.
- If a fallback render is unavoidable, use `To be confirmed` or `Client` in natural language; never render standalone `TBC` header lines, `Dear TBC`, or `Quote: TBC TBC`.
- Do not copy client name, quote ID, date, or pricing from a golden sample.

## Documents Provided by Client

Render `documents_provided` as a table:

```markdown
| Type            | File name                              | Received on |
| --------------- | -------------------------------------- | ----------- |
| Joinery Drawing | 709 Riversdale Road, Camberwell_JD.pdf | TBC         |
```

If `documents_provided` is missing, derive a table from `source_documents`.

## Joinery Working Areas

Render the confirmed scope as the main working-area table. This section should be concise and client-facing.

```markdown
| Room       | Confirmed Joinery Scope                                                           | Joinery Finish                | Drawing Ref            |
| ---------- | --------------------------------------------------------------------------------- | ----------------------------- | ---------------------- |
| GF Kitchen | Overheads / base cabinets / drawers / fridge cupboard / oven tower / wall panels. | Door/Panel: TBC; Carcass: TBC | JD 04, JD 05, p.4, p.5 |
```

Rules:

- Use one row per room or area.
- Keep descriptions as confirmed scope commitments only.
- Do not include `TBC` scope in this table.
- Use `Drawing Ref` for short page or drawing references only.
- Avoid long internal evidence notes in this table.
- Do not claim finishes or hardware as confirmed unless they are present in current project inputs or approved company defaults.

## TBC Items

Render uncertain visible items separately from the confirmed working-area scope:

```markdown
| Room       | Item           | Reason                                 | Drawing Ref |
| ---------- | -------------- | -------------------------------------- | ----------- |
| GF Kitchen | Stone benchtop | Supplier responsibility not confirmed. | JD 04, p.4  |
```

Rules:

- Include visible but unconfirmed items such as stone, LED, mirrors, glass, appliances, shower screens, plumbing, electrical works, and cladding-only door structure/hardware.
- Keep the reason short and estimator-friendly.
- Mirror the most important TBC rows in `open-questions.md`.
- Do not also list the same item in `Exclusions` unless the user explicitly confirmed it is excluded.

## Joinery Finish Schedule

Render `finish_schedule` and `hardware_schedule` as a customer-readable table:

```markdown
| Item / Abbr | Description       | Area       | Status |
| ----------- | ----------------- | ---------- | ------ |
| TBC         | Door/panel finish | GF Kitchen | TBC    |
```

Rules:

- Prefer material/hardware codes only when supplied in the current project materials.
- If a finish or hardware item is visible but not specified, use `TBC`.
- If no finish schedule is available, include a short table of `TBC` rows by area instead of omitting the section.

## Operational Sections

Use short standard wording without inventing commitments:

### Shop Drawings and Site Remeasure

Include:

- Shop drawings are to be prepared according to the agreed joinery scope.
- Site remeasure is required before fabrication.
- Client approval/sign-off is required before fabrication.

### Material Preparation and Production

Include:

- Manufacturing files and material purchase are subject to approved shop drawings.
- Fabrication, edging, finishing, and assembly are based on the approved finish schedule.

### Joinery Delivery

Include:

- Client must provide safe site access.
- Client must provide clear space for storage in each room where joinery is to be installed.

### Joinery Installation

Include:

- Install cabinets, panels, doors, drawers, shelves, and hardware according to shop drawings.
- If LED wiring passes through cabinets, wiring responsibility must be confirmed before installation.

## Pricing

Demo output must not include final prices, GST, grand totals, or payment amounts.

Use:

```markdown
**Estimator to complete.**

Pricing is excluded from this demo output and must be completed by the estimator.
```

## Exclusions

Render exclusions as bullets. Keep exclusions separate from scope.

Common exclusion categories:

```text
stone and stone related works
appliances and FFE
LED / lighting fixtures and electrical works
plumbing fixtures and plumbing works
tiling and waterproofing
building / structural works
painting / plaster / polished plaster works
traffic management
hoisting / cranage
door structures and operating hardware for cladding-only doors
```

Only include exclusions that are relevant to the current project or standard company exclusions.

Do not use exclusions as a placeholder for uncertainty. If responsibility is unclear, use `TBC Items` and `Items Requiring Confirmation` instead.

## Lead Time

If no approved lead time is provided:

```markdown
Lead time is TBC and must be confirmed by Kitchman after scope, samples, and shop drawings are approved.
```

Do not copy a lead time from a golden sample.

## Payment Terms

If no approved payment terms are provided:

```markdown
Payment terms are TBC and must be completed by Kitchman / estimator.
```

Do not copy payment percentages from a golden sample.

## Items Requiring Confirmation

Mirror the highest-priority content from `open_questions`.

Keep this section concise in `proposal.md`; put detailed reasoning in `open-questions.md`.

## Tone

- Formal, client-readable, and conservative.
- Table-first for working areas and finish schedule.
- Business proposal tone, not analysis memo tone.
- Use `TBC` visibly.
- Avoid page-by-page drawing commentary in the proposal body.
