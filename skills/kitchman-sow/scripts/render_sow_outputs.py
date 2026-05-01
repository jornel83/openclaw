#!/usr/bin/env python3
"""Render Kitchman SOW outputs from sow-extraction.json.

This script formats already-structured SOW state. It does not interpret
drawings, infer scope, OCR files, or decide business inclusions.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

MISSING_MARKERS = {"", "TBC", "UNKNOWN", "N/A", "NA", "NONE", "NULL"}
HIGH_RISK_TBC_CATEGORIES = {
    "appliance",
    "building",
    "electrical",
    "fireplace",
    "glass",
    "lighting",
    "mirror",
    "painting",
    "plaster",
    "plumbing",
    "shower",
    "stone",
    "tiling",
}

CONFIRMED_SOURCE_TYPES = {
    "client_confirmed",
    "estimator_confirmed",
    "company_default",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("sow-extraction.json must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    tmp_path.replace(path)


def output_ref(path: Path, workspace_root: Path) -> str:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return path.name


def workspace_root_for(input_path: Path, output_dir: Path) -> Path:
    if input_path.parent.name == "output":
        return input_path.parent.parent
    if output_dir.name == "output":
        return output_dir.parent
    return output_dir


def set_proposal_outputs(
    payload: dict[str, Any],
    *,
    input_path: Path,
    output_dir: Path,
    include_summary: bool,
    include_docx: bool,
) -> None:
    workspace_root = workspace_root_for(input_path, output_dir)
    outputs = {
        "sow_extraction_json": output_ref(input_path, workspace_root),
        "proposal_md": output_ref(output_dir / "proposal.md", workspace_root),
    }
    if include_docx:
        outputs["proposal_docx"] = output_ref(output_dir / "proposal.docx", workspace_root)
    outputs["open_questions_md"] = output_ref(output_dir / "open-questions.md", workspace_root)
    if include_summary:
        outputs["feishu_summary_md"] = output_ref(output_dir / "feishu-summary.md", workspace_root)
    payload["proposal_outputs"] = outputs


def as_text(value: Any, default: str = "TBC") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return str(value)


def is_missing_text(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().upper() in MISSING_MARKERS
    return False


def optional_text(value: Any) -> str:
    if is_missing_text(value):
        return ""
    return as_text(value, "")


def display_text(value: Any, default: str = "To be confirmed") -> str:
    text = optional_text(value)
    return text if text else default


def salutation_text(value: Any, client_name: str) -> str:
    salutation = optional_text(value)
    if salutation:
        return salutation
    if client_name:
        return client_name.split()[0]
    return "Client"


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def table_row(values: list[str]) -> str:
    escaped = [value.replace("\n", "<br>") for value in values]
    return "| " + " | ".join(escaped) + " |"


def format_refs(row: dict[str, Any]) -> str:
    refs: list[str] = []
    drawing_refs = list_value(row.get("drawing_refs"))
    source_pages = list_value(row.get("source_pages"))
    if drawing_refs:
        refs.extend(as_text(ref) for ref in drawing_refs if has_display_value(ref))
    if source_pages:
        refs.extend(f"p.{as_text(page)}" for page in source_pages if has_display_value(page))
    return ", ".join(refs) if refs else "TBC"


def exclusion_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        area = as_text(value.get("area"), "")
        item = as_text(value.get("item") or value.get("description") or value.get("note"))
        if area:
            return f"{area}: {item}"
        return item
    return as_text(value)


def question_text(value: dict[str, Any]) -> str:
    question = as_text(value.get("question"))
    applies_to = as_text(value.get("applies_to"), "")
    reason = as_text(value.get("reason"), "")
    parts = [question]
    if applies_to:
        parts.append(f"Applies to: {applies_to}")
    if reason:
        parts.append(f"Reason: {reason}")
    return " — ".join(parts)


def item_name(item: dict[str, Any]) -> str:
    return as_text(item.get("item") or item.get("name") or item.get("description"))


def included_state(item: dict[str, Any]) -> str:
    value = item.get("included")
    if value is True:
        return "included"
    if value is False:
        return "excluded"
    if isinstance(value, str) and value.strip().lower() == "tbc":
        return "tbc"
    return "tbc"


def is_high_risk_item(item: dict[str, Any]) -> bool:
    category = as_text(item.get("category"), "").strip().lower()
    name = item_name(item).strip().lower()
    if category in HIGH_RISK_TBC_CATEGORIES:
        return True
    return any(token in name for token in HIGH_RISK_TBC_CATEGORIES)


def responsibility_is_confirmed(item: dict[str, Any]) -> bool:
    source_type = as_text(item.get("source_type"), "").strip().lower()
    return (
        item.get("responsibility_confirmed") is True
        or item.get("client_confirmed") is True
        or bool(optional_text(item.get("confirmed_by")))
        or source_type in CONFIRMED_SOURCE_TYPES
    )


def effective_included_state(item: dict[str, Any]) -> str:
    state = included_state(item)
    if state != "included":
        return state
    if is_high_risk_item(item) and not responsibility_is_confirmed(item):
        return "tbc"
    return state


def room_joinery_finish(room: dict[str, Any], row: dict[str, Any] | None = None) -> str:
    if row and has_display_value(row.get("joinery_finish")):
        return as_text(row.get("joinery_finish"))
    finishes = []
    for finish in list_value(room.get("finishes")):
        finish_obj = dict_value(finish)
        if not finish_obj:
            continue
        label = as_text(finish_obj.get("item") or finish_obj.get("name"), "")
        value = as_text(finish_obj.get("value") or finish_obj.get("description"), "")
        if label and value:
            finishes.append(f"{label}: {value}")
        elif value:
            finishes.append(value)
    return "; ".join(finishes) if finishes else "TBC"


def has_display_value(value: Any) -> bool:
    return bool(optional_text(value))


def existing_working_rows_by_room(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in list_value(payload.get("working_area_rows")):
        row_obj = dict_value(row)
        if not row_obj:
            continue
        room_id = optional_text(row_obj.get("room_id"))
        room_name = optional_text(row_obj.get("room"))
        if room_id:
            rows[room_id.lower()] = row_obj
        if room_name:
            rows[room_name.lower()] = row_obj
    return rows


def source_documents_as_provided(payload: dict[str, Any]) -> list[dict[str, Any]]:
    provided = list_value(payload.get("documents_provided"))
    if provided:
        return [dict_value(row) for row in provided]

    rows: list[dict[str, Any]] = []
    for doc in list_value(payload.get("source_documents")):
        doc_obj = dict_value(doc)
        if not doc_obj:
            continue
        rows.append(
            {
                "type": as_text(doc_obj.get("type"), "Unknown").replace("_", " ").title(),
                "file_name": as_text(doc_obj.get("file_name")),
                "received_on": "TBC",
            }
        )
    return rows


def working_area_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rooms = [dict_value(room) for room in list_value(payload.get("rooms"))]
    rooms = [room for room in rooms if room]
    existing_rows = existing_working_rows_by_room(payload)
    if rooms:
        rows: list[dict[str, Any]] = []
        for room in rooms:
            room_name = as_text(room.get("name"))
            row = existing_rows.get(as_text(room.get("id"), "").lower())
            if row is None:
                row = existing_rows.get(room_name.lower())
            included_items = [
                item_name(item)
                for item in list_value(room.get("scope_items"))
                if isinstance(item, dict) and effective_included_state(item) == "included"
            ]
            rows.append(
                {
                    "room": room_name,
                    "description": ", ".join(included_items) if included_items else "Scope TBC",
                    "joinery_finish": room_joinery_finish(room, row),
                    "source_pages": room.get("source_pages") or (row or {}).get("source_pages"),
                    "drawing_refs": room.get("drawing_refs") or (row or {}).get("drawing_refs"),
                }
            )
        return rows

    rows = [dict_value(row) for row in list_value(payload.get("working_area_rows"))]
    rows = [row for row in rows if row]
    if rows:
        return rows

    fallback: list[dict[str, Any]] = []
    for room in list_value(payload.get("rooms")):
        room_obj = dict_value(room)
        if not room_obj:
            continue
        included_items = [
            as_text(item.get("item"))
            for item in list_value(room_obj.get("scope_items"))
            if isinstance(item, dict) and effective_included_state(item) == "included"
        ]
        tbc_items = [
            as_text(item.get("item"))
            for item in list_value(room_obj.get("scope_items"))
            if isinstance(item, dict) and effective_included_state(item) == "tbc"
        ]
        description_parts = []
        if included_items:
            description_parts.append(" / ".join(included_items))
        if tbc_items:
            description_parts.append("TBC: " + ", ".join(tbc_items))
        fallback.append(
            {
                "room": as_text(room_obj.get("name")),
                "description": "; ".join(description_parts) or "TBC",
                "joinery_finish": "TBC",
            }
        )
    return fallback


def tbc_item_rows(payload: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    for room in list_value(payload.get("rooms")):
        room_obj = dict_value(room)
        room_name = as_text(room_obj.get("name"))
        for item in list_value(room_obj.get("scope_items")):
            item_obj = dict_value(item)
            if not item_obj or effective_included_state(item_obj) != "tbc":
                continue
            category = as_text(item_obj.get("category"), "other")
            description = as_text(item_obj.get("description"), "Responsibility to be confirmed.")
            rows.append([room_name, item_name(item_obj), category, description])
    return rows


def schedule_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict_value(row) for row in list_value(payload.get("finish_schedule"))]
    rows.extend(dict_value(row) for row in list_value(payload.get("hardware_schedule")))
    return [row for row in rows if row]


def standard_term(payload: dict[str, Any], key: str, default: str) -> str:
    terms = dict_value(payload.get("standard_terms"))
    value = dict_value(terms.get(key)).get("value")
    if isinstance(value, str) and value.strip().upper() == "TBC":
        return default
    return as_text(value, default)


def render_proposal(payload: dict[str, Any]) -> str:
    project = dict_value(payload.get("project"))
    header = dict_value(payload.get("proposal_header"))
    pricing = dict_value(payload.get("pricing"))

    client = optional_text(header.get("client_name") or project.get("client_name"))
    salutation = salutation_text(header.get("salutation"), client)
    proposal_date = display_text(header.get("proposal_date"), "Date to be confirmed")
    quote_id = display_text(header.get("quote_id") or project.get("quote_id"), "To be confirmed")
    revision = optional_text(header.get("revision"))
    project_name = display_text(
        header.get("project_name") or project.get("project_name"),
        "Project to be confirmed",
    )
    site = display_text(
        header.get("site_address") or project.get("project_address"),
        "Site to be confirmed",
    )
    prepared_by = display_text(header.get("prepared_by"), "Kitchman")
    client_line = f"**{client}**" if client else "**Client: To be confirmed**"
    quote_line = f"**Quote: {quote_id}{(' ' + revision) if revision else ''}**"

    lines = [
        "# Project Proposal",
        "",
        client_line,
        "",
        f"**{proposal_date}**",
        "",
        quote_line,
        "",
        f"**Project: {project_name}**",
        "",
        f"**Site:** {site}",
        "",
        f"Dear {salutation},",
        "",
        "Thank you for giving us the opportunity to submit a proposal for the above-mentioned project.",
        "This draft is prepared from the current project materials and is subject to estimator review.",
        "",
        "## Design and Planning",
        "",
        "- Analyze project materials provided by client to understand joinery requirements.",
        "- Confirm working areas in accordance with current project files and further discussion.",
        "- Prepare the SOW for estimator pricing. Final pricing is not generated by this demo output.",
        "",
        "## Documents Provided by Client",
        "",
        table_row(["Type", "File name", "Received on"]),
        table_row(["---", "---", "---"]),
    ]

    for row in source_documents_as_provided(payload):
        lines.append(
            table_row(
                [
                    as_text(row.get("type")),
                    as_text(row.get("file_name")),
                    as_text(row.get("received_on")),
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Joinery Working Areas",
            "",
            table_row(["Room", "Confirmed Joinery Scope", "Joinery Finish", "Drawing Ref"]),
            table_row(["---", "---", "---", "---"]),
        ]
    )
    for row in working_area_rows(payload):
        lines.append(
            table_row(
                [
                    as_text(row.get("room")),
                    as_text(row.get("description")),
                    as_text(row.get("joinery_finish")),
                    format_refs(row),
                ]
            )
        )

    tbc_rows = tbc_item_rows(payload)
    lines.extend(
        [
            "",
            "## TBC Items",
            "",
        ]
    )
    if tbc_rows:
        lines.extend(
            [
                table_row(["Room", "Item", "Category", "Confirmation Required"]),
                table_row(["---", "---", "---", "---"]),
            ]
        )
        for row in tbc_rows:
            lines.append(table_row(row))
    else:
        lines.append("No TBC scope items recorded.")

    lines.extend(
        [
            "",
            "## Joinery Finish Schedule",
            "",
            table_row(["Item / Abbr", "Description", "Area", "Status"]),
            table_row(["---", "---", "---", "---"]),
        ]
    )
    schedules = schedule_rows(payload)
    if schedules:
        for row in schedules:
            lines.append(
                table_row(
                    [
                        as_text(row.get("item_abbr") or row.get("item"), "TBC"),
                        as_text(row.get("description") or row.get("spec")),
                        as_text(row.get("area")),
                        as_text(row.get("status")),
                    ]
                )
            )
    else:
        lines.append(table_row(["TBC", "Finish / hardware schedule", "All areas", "TBC"]))

    lines.extend(
        [
            "",
            "## Shop Drawings and Site Remeasure",
            "",
            "- Create shop drawings in accordance with joinery items assigned to Kitchman.",
            "- Remeasure the site prior to fabrication to confirm dimensions and site conditions.",
            "- Client must approve and sign off shop drawings before fabrication commences.",
            "",
            "## Material Preparation and Production",
            "",
            "- Create manufacturing files and purchase materials according to approved shop drawings.",
            "- Cut, edge, finish, and assemble joinery parts according to the approved finish schedule.",
            "",
            "## Joinery Delivery",
            "",
            "- Deliver cabinets, doors, panels, and other joinery goods to site.",
            "- Client must provide clean and safe access for delivery.",
            "- Client must provide clear storage space in each room where joinery is to be installed.",
            "",
            "## Joinery Installation",
            "",
            "- Install cabinets, fixtures, panels, doors, drawers, shelves, and hardware as per approved shop drawings.",
            "- If LED wiring runs through cabinets, wiring responsibility must be confirmed before installation.",
            "",
            "## Pricing",
            "",
            "**Estimator to complete.**",
            "",
            as_text(
                pricing.get("note"),
                "Pricing is excluded from this demo output and must be completed by the estimator.",
            ),
            "",
            "## Exclusions",
            "",
        ]
    )

    exclusions = [exclusion_text(item) for item in list_value(payload.get("exclusions"))]
    if exclusions:
        lines.extend(f"- {item}" for item in exclusions)
    else:
        lines.append("- TBC")

    lines.extend(
        [
            "",
            "## Lead Time",
            "",
            standard_term(
                payload,
                "lead_time",
                "Lead time is TBC and must be confirmed by Kitchman after scope, samples, and shop drawings are approved.",
            ),
            "",
            "## Payment Terms",
            "",
            standard_term(
                payload,
                "payment_terms",
                "Payment terms are TBC and must be completed by Kitchman / estimator.",
            ),
            "",
            "## Items Requiring Confirmation",
            "",
        ]
    )

    questions = [dict_value(item) for item in list_value(payload.get("open_questions"))]
    questions = [item for item in questions if item]
    if questions:
        for index, question in enumerate(questions, start=1):
            lines.append(f"{index}. {question_text(question)}")
    else:
        lines.append("No open questions recorded.")

    lines.extend(
        [
            "",
            "If you would like to discuss this matter further, please contact Kitchman.",
            "",
            "Kindest Regards,",
            "",
            prepared_by,
            "",
        ]
    )
    return "\n".join(lines)


def render_open_questions(payload: dict[str, Any]) -> str:
    project = dict_value(payload.get("project"))
    questions = [dict_value(item) for item in list_value(payload.get("open_questions"))]
    questions = [item for item in questions if item]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for question in questions:
        grouped[as_text(question.get("priority"), "medium").lower()].append(question)

    lines = [
        f"# Open Questions — {as_text(project.get('project_name'))}",
        "",
        f"**SOW ID:** {as_text(payload.get('sow_id'))}",
        f"**Status:** {as_text(payload.get('sow_status'))}",
        "",
    ]

    order = [("high", "High Priority"), ("medium", "Medium Priority"), ("low", "Low Priority")]
    question_index = 1
    for priority_key, title in order:
        items = grouped.get(priority_key, [])
        if not items:
            continue
        lines.extend([f"## {title}", ""])
        for question in items:
            lines.extend(
                [
                    f"### Q{question_index}. {as_text(question.get('question'))}",
                    f"- **Applies to:** {as_text(question.get('applies_to'))}",
                    f"- **Reason:** {as_text(question.get('reason'))}",
                    f"- **Current status:** {as_text(question.get('status'))}",
                    "",
                ]
            )
            question_index += 1

    lines.extend(
        [
            "## Summary",
            "",
            table_row(["Priority", "Count"]),
            table_row(["---", "---"]),
        ]
    )
    for priority_key, title in order:
        lines.append(table_row([title.replace(" Priority", ""), str(len(grouped.get(priority_key, [])))]))
    lines.append(table_row(["Total", str(len(questions))]))
    lines.append("")
    lines.append("All open questions must be resolved before final pricing and production commitment.")
    lines.append("")
    return "\n".join(lines)


def count_scope_items(payload: dict[str, Any]) -> int:
    total = 0
    for room in list_value(payload.get("rooms")):
        room_obj = dict_value(room)
        total += len(list_value(room_obj.get("scope_items")))
    return total


def scope_state_counts(payload: dict[str, Any]) -> dict[str, int]:
    counts = {"included": 0, "tbc": 0, "excluded": 0}
    for room in list_value(payload.get("rooms")):
        room_obj = dict_value(room)
        for item in list_value(room_obj.get("scope_items")):
            item_obj = dict_value(item)
            if not item_obj:
                continue
            state = effective_included_state(item_obj)
            counts[state] = counts.get(state, 0) + 1
    return counts


def delivery_output_files(output_files: dict[str, Any]) -> dict[str, str]:
    refs = output_files.get("delivery_refs")
    if isinstance(refs, dict):
        return {key: as_text(value, "") for key, value in refs.items()}
    return {key: as_text(value, "") for key, value in output_files.items()}


def render_feishu_summary(payload: dict[str, Any]) -> str:
    rooms = [dict_value(room) for room in list_value(payload.get("rooms"))]
    rooms = [room for room in rooms if room]
    questions = [dict_value(item) for item in list_value(payload.get("open_questions"))]
    questions = [item for item in questions if item]
    sources = source_documents_as_provided(payload)
    output_files = dict_value(payload.get("proposal_outputs"))
    output_refs = delivery_output_files(output_files)
    counts = scope_state_counts(payload)

    lines = [
        "SOW 已生成。",
        "",
        (
            f"识别到 {len(sources)} 份资料、{len(rooms)} 个区域、"
            f"{counts.get('included', 0)} 个 confirmed scope items、"
            f"{counts.get('tbc', 0)} 个 TBC items、"
            f"{len(questions)} 个待确认问题。"
        ),
        "proposal 已按 Kitchman 正式文档结构整理，价格字段已留空，没有生成最终报价金额。",
        "",
        "关键预览：",
    ]

    for room in rooms[:5]:
        item_names = [
            as_text(item.get("item"))
            for item in list_value(room.get("scope_items"))
            if isinstance(item, dict) and effective_included_state(item) == "included"
        ][:5]
        preview = ", ".join(item_names) if item_names else "scope TBC"
        lines.append(f"- {as_text(room.get('name'))}: {preview}.")

    if len(rooms) > 5:
        lines.append(f"- 另有 {len(rooms) - 5} 个区域已整理到 proposal.md。")

    lines.extend(
        [
            "",
            "输出文件：",
        ]
    )
    if output_refs.get("sow_package_zip"):
        lines.extend(
            [
                f"- {as_text(output_refs.get('sow_package_zip'))}",
                "",
                "ZIP 内容（5 个核心文件）：",
            ]
        )
    lines.extend(
        [
            f"- {as_text(output_refs.get('sow_extraction_json'), 'sow-extraction.json')}",
            f"- {as_text(output_refs.get('proposal_md'), 'proposal.md')}",
        ]
    )
    if output_refs.get("proposal_docx"):
        lines.append(f"- {as_text(output_refs.get('proposal_docx'))}")
    lines.append(f"- {as_text(output_refs.get('open_questions_md'), 'open-questions.md')}")
    if output_refs.get("feishu_summary_md"):
        lines.append(f"- {as_text(output_refs.get('feishu_summary_md'))}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to sow-extraction.json")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for markdown outputs")
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Do not write feishu-summary.md",
    )
    parser.add_argument(
        "--docx",
        action="store_true",
        help="Also write proposal.docx from the rendered proposal.md",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = args.input.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    payload = load_json(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    set_proposal_outputs(
        payload,
        input_path=input_path,
        output_dir=output_dir,
        include_summary=not args.no_summary,
        include_docx=args.docx,
    )
    proposal_text = render_proposal(payload)
    open_questions_text = render_open_questions(payload)
    feishu_summary_text = None if args.no_summary else render_feishu_summary(payload)

    (output_dir / "proposal.md").write_text(proposal_text, encoding="utf-8")
    (output_dir / "open-questions.md").write_text(open_questions_text, encoding="utf-8")
    if args.docx:
        from render_docx import render_docx_from_markdown

        render_docx_from_markdown(proposal_text, output_dir / "proposal.docx")
    if not args.no_summary:
        (output_dir / "feishu-summary.md").write_text(feishu_summary_text or "", encoding="utf-8")
    write_json(input_path, payload)
    print(f"updated {input_path}")
    print(f"wrote {output_dir / 'proposal.md'}")
    if args.docx:
        print(f"wrote {output_dir / 'proposal.docx'}")
    print(f"wrote {output_dir / 'open-questions.md'}")
    if not args.no_summary:
        print(f"wrote {output_dir / 'feishu-summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
