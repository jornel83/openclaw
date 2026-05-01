#!/usr/bin/env python3
"""Validate kitchman-sow output artifacts.

This script checks output structure and safety constraints only. It does not
evaluate document understanding quality.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FORBIDDEN_PRICE_KEYS = {
    "final_price",
    "total_price",
    "quote_total",
    "grand_total",
    "subtotal",
    "amount_due",
}

REQUIRED_TOP_LEVEL_KEYS = {
    "sow_id",
    "project",
    "proposal_header",
    "documents_provided",
    "source_documents",
    "rooms",
    "working_area_rows",
    "finish_schedule",
    "hardware_schedule",
    "standard_terms",
    "pricing",
    "exclusions",
    "open_questions",
    "proposal_outputs",
}

EXPECTED_PROPOSAL_OUTPUT_KEYS = {
    "sow_extraction_json",
    "proposal_md",
    "proposal_docx",
    "open_questions_md",
    "feishu_summary_md",
    "sow_package_zip",
    "output_manifest_json",
}

PROPOSAL_OUTPUT_GROUP_KEYS = {
    "workspace_refs",
    "package_refs",
    "delivery_refs",
}

CORE_PACKAGE_FILES = {
    "sow-extraction.json",
    "proposal.md",
    "proposal.docx",
    "open-questions.md",
    "feishu-summary.md",
}

HIGH_RISK_SCOPE_TOKENS = {
    "appliance",
    "building",
    "electrical",
    "fireplace",
    "glass",
    "led",
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

REQUIRED_PROPOSAL_HEADER_FIELDS = {
    "client_name",
    "proposal_date",
    "quote_id",
    "revision",
    "project_name",
    "site_address",
}

DRAWING_DOCUMENT_TYPES = {
    "joinery_drawing",
    "cabinetry_drawing",
    "architectural_drawing",
}

REQUIRED_PROPOSAL_SECTION_PATTERNS = {
    "Design and Planning": r"^##\s+Design and Planning\b",
    "Documents Provided by Client": r"^##\s+Documents Provided by Client\b",
    "Joinery Working Areas": r"^##\s+Joinery Working Areas\b",
    "TBC Items": r"^##\s+TBC Items\b",
    "Joinery Finish Schedule": r"^##\s+Joinery Finish Schedule\b",
    "Joinery Delivery": r"^##\s+Joinery Delivery\b",
    "Joinery Installation": r"^##\s+Joinery Installation\b",
    "Pricing": r"^##\s+Pricing\b",
    "Exclusions": r"^##\s+Exclusions\b",
    "Lead Time": r"^##\s+Lead Time\b",
    "Payment Terms": r"^##\s+Payment Terms\b",
    "Items Requiring Confirmation": r"^##\s+Items Requiring Confirmation\b",
}

GOLDEN_SAMPLE_FACT_PATTERNS = {
    "sample quote id": r"\bQ2248\b",
    "sample client name": r"\bCalvin Huang\b",
    "sample total price": r"\$?\s*69,000\b|\$\s*69000\b",
    "sample grand total": r"\$?\s*75,900\b|\$\s*75900\b",
    "sample finish code": r"\bCN-W1323\b",
    "sample carcass material": r"\bWhite Melamine Board\b",
    "sample hinge brand": r"\bBlum Range Hinges\b",
    "sample drawer runner": r"\bHafele Alto Slim\b",
    "sample bin code": r"\bBIN600\b",
}

MISSING_MARKERS = {"", "TBC", "UNKNOWN", "N/A", "NA", "NONE", "NULL"}


@dataclass
class CheckResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_output_file(root: Path, file_name: str) -> Path:
    direct = root / file_name
    if direct.exists():
        return direct
    nested = root / "output" / file_name
    if nested.exists():
        return nested
    return direct


def has_flat_core_outputs(root: Path) -> bool:
    return all((root / file_name).exists() for file_name in CORE_PACKAGE_FILES)


def candidate_output_paths(root: Path, declared_value: str) -> list[Path]:
    declared_path = Path(declared_value)
    candidates: list[Path] = []
    if declared_path.is_absolute():
        candidates.append(declared_path)
    else:
        candidates.append(root / declared_path)
        candidates.append(root / "output" / declared_path.name)
        candidates.append(root / declared_path.name)

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def declared_output_exists(root: Path, declared_value: str) -> bool:
    return any(candidate.exists() for candidate in candidate_output_paths(root, declared_value))


def find_package_file(root: Path) -> Path | None:
    candidates = sorted((root / "output").glob("*-sow.zip")) if (root / "output").exists() else []
    candidates.extend(sorted(root.glob("*-sow.zip")))
    return candidates[0] if candidates else None


def walk_json(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    out = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            out.extend(walk_json(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.extend(walk_json(child, f"{path}[{index}]"))
    return out


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().upper() not in MISSING_MARKERS
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def current_project_fact_blob(payload: dict[str, Any]) -> str:
    facts: list[str] = []
    for section_name in ("project", "proposal_header"):
        section = payload.get(section_name)
        if not isinstance(section, dict):
            continue
        for value in section.values():
            if isinstance(value, str) and has_value(value):
                facts.append(value)
    return "\n".join(facts)


def validate_no_price_fields(payload: dict[str, Any], errors: list[str]) -> None:
    for path, value in walk_json(payload):
        key = path.rsplit(".", 1)[-1].lower()
        key = re.sub(r"[^a-z0-9_]", "", key)
        if key in FORBIDDEN_PRICE_KEYS and has_value(value):
            errors.append(f"forbidden price field has value: {path}")


def validate_scope_items(payload: dict[str, Any], warnings: list[str]) -> None:
    scope_like = []
    for path, value in walk_json(payload):
        if not isinstance(value, dict):
            continue
        if "item" in value and ("category" in value or "included" in value):
            scope_like.append((path, value))

    if not scope_like:
        warnings.append("no scope item objects detected")
        return

    for path, item in scope_like:
        if "confidence" not in item:
            warnings.append(f"scope item missing confidence: {path}")
        if "source_type" not in item:
            warnings.append(f"scope item missing source_type: {path}")
        if item.get("included") is True and item.get("review_status") == "unreviewed":
            warnings.append(
                f"included scope item is still unreviewed after proposal generation: {path}"
            )
        if item.get("included") is True and item.get("review_status") == "needs_confirmation":
            warnings.append(
                f"included scope item also needs confirmation; use included='tbc' or split confirmed/TBC scope: {path}"
            )
        if item.get("included") == "tbc" and item.get("review_status") != "needs_confirmation":
            warnings.append(
                f"TBC scope item should usually be marked needs_confirmation: {path}"
            )
        if item.get("included") is True and not (
            has_value(item.get("evidence_summary"))
            or has_value(item.get("evidence"))
            or has_value(item.get("source_pages"))
            or has_value(item.get("drawing_refs"))
        ):
            warnings.append(f"included scope item missing evidence/page reference: {path}")


def included_state(item: dict[str, Any]) -> str:
    included = item.get("included")
    if included is True:
        return "included"
    if included is False:
        return "excluded"
    if isinstance(included, str) and included.strip().lower() == "tbc":
        return "tbc"
    return "tbc"


def item_label(item: dict[str, Any]) -> str:
    value = item.get("item") or item.get("name") or item.get("description")
    return str(value or "").strip()


def normalized_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(str(child) for child in value.values()).lower()
    return str(value or "").lower()


def exclusion_blob(payload: dict[str, Any]) -> str:
    chunks = [normalized_text(item) for item in payload.get("exclusions", []) if item]
    rooms = payload.get("rooms")
    if isinstance(rooms, list):
        for room in rooms:
            if isinstance(room, dict) and isinstance(room.get("exclusions"), list):
                chunks.extend(normalized_text(item) for item in room["exclusions"] if item)
    return "\n".join(chunks)


def is_high_risk_item(item: dict[str, Any]) -> bool:
    category = str(item.get("category") or "").strip().lower()
    label = item_label(item).lower()
    if category in HIGH_RISK_SCOPE_TOKENS:
        return True
    return any(token in label for token in HIGH_RISK_SCOPE_TOKENS)


def responsibility_is_confirmed(item: dict[str, Any]) -> bool:
    source_type = str(item.get("source_type") or "").strip().lower()
    return (
        item.get("responsibility_confirmed") is True
        or item.get("client_confirmed") is True
        or has_value(item.get("confirmed_by"))
        or source_type in CONFIRMED_SOURCE_TYPES
    )


def exclusion_matches_item(exclusions: str, item: dict[str, Any]) -> bool:
    label = item_label(item).lower()
    category = str(item.get("category") or "").strip().lower()
    if label and len(label) >= 5 and label in exclusions:
        return True
    return category in HIGH_RISK_SCOPE_TOKENS and category in exclusions


def validate_scope_conflicts(payload: dict[str, Any], warnings: list[str]) -> None:
    exclusions = exclusion_blob(payload)
    rooms = payload.get("rooms")
    if not exclusions or not isinstance(rooms, list):
        return

    for room_index, room in enumerate(rooms):
        if not isinstance(room, dict) or not isinstance(room.get("scope_items"), list):
            continue
        room_name = str(room.get("name") or f"rooms[{room_index}]")
        for item in room["scope_items"]:
            if not isinstance(item, dict):
                continue
            state = included_state(item)
            label = item_label(item) or "<unnamed item>"
            if state in {"included", "tbc"} and exclusion_matches_item(exclusions, item):
                warnings.append(
                    f"{state} scope item also appears in exclusions: {room_name} / {label}"
                )
            if state == "included" and is_high_risk_item(item) and not responsibility_is_confirmed(item):
                warnings.append(
                    f"high-risk scope item should be TBC unless responsibility is confirmed: {room_name} / {label}"
                )


def validate_traceability(payload: dict[str, Any], warnings: list[str]) -> None:
    rooms = payload.get("rooms")
    if not isinstance(rooms, list):
        return
    for room_index, room in enumerate(rooms):
        if not isinstance(room, dict):
            continue
        if not (
            has_value(room.get("source_pages"))
            or has_value(room.get("drawing_refs"))
            or has_value(room.get("evidence"))
            or has_value(room.get("evidence_summary"))
        ):
            warnings.append(
                f"room missing source_pages/drawing_refs/evidence: $.rooms[{room_index}]"
            )

    rows = payload.get("working_area_rows")
    if not isinstance(rows, list):
        return
    for row_index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        if not (
            has_value(row.get("source_pages"))
            or has_value(row.get("drawing_refs"))
            or has_value(row.get("evidence_summary"))
        ):
            warnings.append(
                f"working area row missing source_pages/drawing_refs: $.working_area_rows[{row_index}]"
            )


def validate_preflight_inputs(payload: dict[str, Any], warnings: list[str]) -> None:
    project = payload.get("project") if isinstance(payload.get("project"), dict) else {}
    header = (
        payload.get("proposal_header")
        if isinstance(payload.get("proposal_header"), dict)
        else {}
    )

    field_values = {
        "client_name": header.get("client_name") or project.get("client_name"),
        "proposal_date": header.get("proposal_date"),
        "quote_id": header.get("quote_id") or project.get("quote_id"),
        "revision": header.get("revision"),
        "project_name": header.get("project_name") or project.get("project_name"),
        "site_address": header.get("site_address") or project.get("project_address"),
    }
    for field in sorted(REQUIRED_PROPOSAL_HEADER_FIELDS):
        if not has_value(field_values.get(field)):
            warnings.append(
                f"proposal preflight field missing or unconfirmed: {field}"
            )

    source_documents = payload.get("source_documents")
    drawing_found = False
    if isinstance(source_documents, list):
        for doc in source_documents:
            if not isinstance(doc, dict):
                continue
            doc_type = str(doc.get("type") or "").strip().lower()
            if doc_type in DRAWING_DOCUMENT_TYPES:
                drawing_found = True
                break
    if not drawing_found:
        warnings.append(
            "no joinery/cabinetry or architectural drawing source document detected"
        )


def count_scope_items(payload: dict[str, Any]) -> int:
    rooms = payload.get("rooms")
    if not isinstance(rooms, list):
        return 0
    total = 0
    for room in rooms:
        if isinstance(room, dict) and isinstance(room.get("scope_items"), list):
            total += len(room["scope_items"])
    return total


def validate_json_shape(payload: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(payload))
    for key in missing:
        errors.append(f"sow-extraction.json missing required key: {key}")

    rooms = payload.get("rooms")
    if not isinstance(rooms, list) or not rooms:
        errors.append("sow-extraction.json must include at least one room")
        return

    working_rows = payload.get("working_area_rows")
    if isinstance(working_rows, list) and working_rows:
        if len(working_rows) != len(rooms):
            warnings.append(
                f"working_area_rows count ({len(working_rows)}) does not match rooms count ({len(rooms)})"
            )

    open_questions = payload.get("open_questions")
    if not isinstance(open_questions, list) or not open_questions:
        warnings.append("sow-extraction.json has no top-level open_questions")

    proposal_outputs = payload.get("proposal_outputs")
    if not isinstance(proposal_outputs, dict) or not proposal_outputs:
        warnings.append("sow-extraction.json has empty proposal_outputs")
    else:
        for key in sorted(EXPECTED_PROPOSAL_OUTPUT_KEYS - set(proposal_outputs)):
            warnings.append(f"sow-extraction.json proposal_outputs missing key: {key}")

    seen_scope_ids: set[str] = set()
    for room_index, room in enumerate(rooms):
        if not isinstance(room, dict):
            errors.append(f"room is not an object: $.rooms[{room_index}]")
            continue
        if not room.get("id"):
            warnings.append(f"room missing id: $.rooms[{room_index}]")
        if not room.get("name"):
            warnings.append(f"room missing name: $.rooms[{room_index}]")
        scope_items = room.get("scope_items")
        if not isinstance(scope_items, list):
            warnings.append(f"room missing scope_items array: $.rooms[{room_index}]")
            continue
        for item_index, item in enumerate(scope_items):
            if not isinstance(item, dict):
                warnings.append(
                    f"scope item is not an object: $.rooms[{room_index}].scope_items[{item_index}]"
                )
                continue
            scope_id = item.get("id")
            if not isinstance(scope_id, str) or not scope_id:
                warnings.append(
                    f"scope item missing id: $.rooms[{room_index}].scope_items[{item_index}]"
                )
                continue
            if scope_id in seen_scope_ids:
                errors.append(f"duplicate scope item id: {scope_id}")
            seen_scope_ids.add(scope_id)


def validate_declared_outputs(root: Path, payload: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    proposal_outputs = payload.get("proposal_outputs")
    if not isinstance(proposal_outputs, dict):
        return
    flat_delivery = has_flat_core_outputs(root)

    for key, value in proposal_outputs.items():
        if key in PROPOSAL_OUTPUT_GROUP_KEYS:
            if not isinstance(value, dict):
                warnings.append(f"proposal_outputs.{key} should be an object")
            continue
        if not isinstance(value, str) or not value.strip():
            warnings.append(f"proposal_outputs.{key} is not a usable path")
            continue

        if Path(value).is_absolute():
            warnings.append(f"proposal_outputs.{key} should be workspace-relative, not absolute")
        if declared_output_exists(root, value):
            continue
        message = f"proposal_outputs.{key} points to a missing file: {value}"
        if flat_delivery and key in {"sow_package_zip", "output_manifest_json"}:
            warnings.append(message)
        else:
            errors.append(message)

    for group_key in ("workspace_refs", "delivery_refs"):
        group_value = proposal_outputs.get(group_key)
        if not isinstance(group_value, dict):
            continue
        for key, value in group_value.items():
            if not isinstance(value, str) or not value.strip():
                warnings.append(f"proposal_outputs.{group_key}.{key} is not a usable path")
                continue
            if group_key == "delivery_refs":
                if declared_output_exists(root, value):
                    continue
                if key in {"sow_package_zip", "output_manifest_json"} and flat_delivery:
                    continue
            if group_key == "workspace_refs" and declared_output_exists(root, value):
                continue
            if group_key == "delivery_refs" and key in {"sow_package_zip", "output_manifest_json"}:
                warnings.append(
                    f"proposal_outputs.{group_key}.{key} is not present in this downloaded folder: {value}"
                )
            elif group_key == "delivery_refs":
                errors.append(f"proposal_outputs.{group_key}.{key} points to a missing file: {value}")


def detect_golden_sample_fact_leaks(
    text: str,
    warnings: list[str],
    source_name: str,
    approved_fact_blob: str = "",
) -> None:
    for label, pattern in GOLDEN_SAMPLE_FACT_PATTERNS.items():
        if re.search(pattern, text, re.I):
            if approved_fact_blob and re.search(pattern, approved_fact_blob, re.I):
                continue
            warnings.append(
                f"{source_name} contains possible golden sample fact leakage: {label}"
            )


def extract_stated_area_counts(text: str) -> list[int]:
    counts: list[int] = []
    for match in re.finditer(r"\b(\d+)\s+(?:areas|rooms)\b", text, re.I):
        counts.append(int(match.group(1)))
    for match in re.finditer(r"(\d+)\s*个(?:区域|房间)", text):
        counts.append(int(match.group(1)))
    return counts


def count_question_headings(text: str) -> int:
    return len(re.findall(r"^#{2,4}\s+Q\d+\b", text, re.M))


def validate_open_questions(path: Path, errors: list[str]) -> int:
    text = read_text(path).strip()
    meaningful_lines = [
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not meaningful_lines:
        errors.append("open-questions.md has no meaningful content")
    return count_question_headings(text)


def validate_proposal(
    path: Path,
    errors: list[str],
    warnings: list[str],
    room_count: int,
    approved_fact_blob: str,
) -> None:
    text = read_text(path)
    if re.search(r"([$]\s*\d|AUD\s*\d|total\s+price\s*[:：]\s*\d)", text, re.I):
        errors.append("proposal.md appears to contain a final price")
    if not re.search(
        r"Pricing is excluded from this demo output|Estimator to complete",
        text,
        re.I,
    ):
        warnings.append("proposal.md does not include the standard pricing exclusion")

    for section_name, pattern in REQUIRED_PROPOSAL_SECTION_PATTERNS.items():
        if not re.search(pattern, text, re.M | re.I):
            errors.append(f"proposal.md missing formal proposal section: {section_name}")

    for label, pattern in {
        "standalone TBC header line": r"^\*\*TBC\*\*$",
        "Dear TBC salutation": r"\bDear\s+TBC\b",
        "TBC quote header": r"\bQuote:\s*TBC(?:\s+TBC)?\b",
    }.items():
        if re.search(pattern, text, re.M | re.I):
            warnings.append(f"proposal.md contains weak customer header: {label}")

    working_area_match = re.search(
        r"^##\s+Joinery Working Areas\b(?P<body>[\s\S]*?)(?=^##\s+TBC Items\b|^##\s+Joinery Finish Schedule\b)",
        text,
        re.M | re.I,
    )
    if working_area_match:
        working_area_body = working_area_match.group("body")
        for label, pattern in {
            "inline TBC scope": r"\bTBC\s*:",
            "responsibility uncertainty": r"\bresponsibility\b.*\bconfirm",
            "supplier uncertainty": r"\bsupply\b.*\bconfirm",
        }.items():
            if re.search(pattern, working_area_body, re.I):
                warnings.append(
                    f"proposal.md Joinery Working Areas may mix confirmed scope with uncertainty: {label}"
                )

    detect_golden_sample_fact_leaks(
        text, warnings, "proposal.md", approved_fact_blob
    )

    if room_count:
        for stated_count in extract_stated_area_counts(text):
            if stated_count != room_count:
                warnings.append(
                    f"proposal.md states {stated_count} areas/rooms but sow-extraction.json has {room_count} rooms"
                )


def validate_docx(path: Path, errors: list[str]) -> None:
    if path.suffix.lower() != ".docx":
        errors.append(f"proposal DOCX has wrong extension: {path}")
        return
    try:
        with zipfile.ZipFile(path) as docx:
            names = set(docx.namelist())
            for required_name in (
                "[Content_Types].xml",
                "_rels/.rels",
                "word/document.xml",
                "word/styles.xml",
                "word/header1.xml",
                "word/footer1.xml",
                "word/_rels/header1.xml.rels",
                "word/media/kitchman-logo.jpeg",
            ):
                if required_name not in names:
                    errors.append(f"proposal.docx missing required part: {required_name}")
            document_xml = docx.read("word/document.xml").decode("utf-8")
    except Exception as exc:
        errors.append(f"proposal.docx is not a readable DOCX: {exc}")
        return
    if "Project Proposal" not in document_xml:
        errors.append("proposal.docx does not appear to contain the proposal content")
    if "headerReference" not in document_xml or "footerReference" not in document_xml:
        errors.append("proposal.docx missing header/footer references")


def validate_output_package(root: Path, errors: list[str], warnings: list[str]) -> None:
    package_path = find_package_file(root)
    manifest_path = find_output_file(root, "output-manifest.json")
    flat_delivery = has_flat_core_outputs(root)
    if package_path is None:
        if flat_delivery:
            warnings.append(
                "flat delivery folder contains the five core files but no SOW ZIP package"
            )
        else:
            errors.append("missing SOW output ZIP package")
    if not manifest_path.exists():
        if flat_delivery:
            warnings.append(
                "flat delivery folder is missing output-manifest.json; workspace validation should keep it"
            )
        else:
            errors.append(f"missing required output manifest: {manifest_path}")
    if package_path is None:
        return
    try:
        with zipfile.ZipFile(package_path) as package:
            names = set(package.namelist())
    except Exception as exc:
        errors.append(f"SOW output package is not a readable ZIP: {exc}")
        return
    missing = sorted(CORE_PACKAGE_FILES - names)
    for name in missing:
        errors.append(f"SOW output package missing core file: {name}")
    extra_dirs = [name for name in names if name.endswith("/")]
    if extra_dirs:
        warnings.append(f"SOW output package contains directory entries: {extra_dirs}")

    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
        except Exception as exc:
            warnings.append(f"could not read output-manifest.json: {exc}")
            return
        if not isinstance(manifest, dict):
            warnings.append("output-manifest.json is not a JSON object")
            return
        manifest_files = manifest.get("files")
        if not isinstance(manifest_files, list):
            warnings.append("output-manifest.json missing files list")
            return
        manifest_names = {
            item.get("path")
            for item in manifest_files
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        for name in sorted(CORE_PACKAGE_FILES - manifest_names):
            warnings.append(f"output-manifest.json missing core file row: {name}")


def validate_render_manifests(root: Path, errors: list[str], warnings: list[str]) -> None:
    manifests = sorted(root.rglob("render-manifest.json"))
    for manifest_path in manifests:
        try:
            payload = load_json(manifest_path)
        except Exception as exc:
            warnings.append(f"could not read render manifest {manifest_path}: {exc}")
            continue
        if not isinstance(payload, dict):
            warnings.append(f"render manifest is not a JSON object: {manifest_path}")
            continue
        if payload.get("page_count_truncated") is True:
            errors.append(
                "render-manifest.json indicates unrendered PDF pages: "
                f"{payload.get('unrendered_pages')}"
            )


def validate_drawing_indexes(root: Path, errors: list[str], warnings: list[str]) -> None:
    indexes = sorted(root.rglob("drawing-index.json"))
    for index_path in indexes:
        try:
            payload = load_json(index_path)
        except Exception as exc:
            warnings.append(f"could not read drawing index {index_path}: {exc}")
            continue
        if not isinstance(payload, dict):
            warnings.append(f"drawing index is not a JSON object: {index_path}")
            continue
        if payload.get("page_count_truncated") is True:
            errors.append(
                "drawing-index.json indicates unrendered PDF pages: "
                f"{payload.get('unrendered_pages')}"
            )
        if not payload.get("pages"):
            warnings.append(f"drawing index has no page rows: {index_path}")


def validate_sow_state(root: Path, errors: list[str], warnings: list[str]) -> None:
    state_path = root / "sow-state.json"
    if not state_path.exists():
        return
    try:
        payload = load_json(state_path)
    except Exception as exc:
        warnings.append(f"could not read sow-state.json: {exc}")
        return
    if not isinstance(payload, dict):
        warnings.append("sow-state.json is not a JSON object")
        return
    revisions = payload.get("revision_history")
    if not isinstance(revisions, list):
        errors.append("sow-state.json revision_history must be a list")
        return
    for index, revision in enumerate(revisions):
        if not isinstance(revision, dict):
            errors.append(f"revision_history[{index}] must be an object")
            continue
        for key in (
            "revision_id",
            "timestamp",
            "message",
            "summary",
            "change_type",
            "affected_areas",
            "changed_files",
            "output_version",
        ):
            if key not in revision:
                warnings.append(f"revision_history[{index}] missing key: {key}")


def validate(root: Path) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []

    sow_path = find_output_file(root, "sow-extraction.json")
    proposal_path = find_output_file(root, "proposal.md")
    proposal_docx_path = find_output_file(root, "proposal.docx")
    questions_path = find_output_file(root, "open-questions.md")
    summary_path = find_output_file(root, "feishu-summary.md")

    for path in (sow_path, proposal_path, proposal_docx_path, questions_path, summary_path):
        if not path.exists():
            errors.append(f"missing required output: {path}")

    if not sow_path.exists():
        return CheckResult(errors=errors, warnings=warnings)

    try:
        payload = load_json(sow_path)
    except json.JSONDecodeError as exc:
        errors.append(f"sow-extraction.json is invalid JSON: {exc}")
        return CheckResult(errors=errors, warnings=warnings)

    if not isinstance(payload, dict):
        errors.append("sow-extraction.json must contain a JSON object")
        return CheckResult(errors=errors, warnings=warnings)

    if not payload.get("sow_id"):
        errors.append("sow-extraction.json missing sow_id")

    approved_fact_blob = current_project_fact_blob(payload)
    validate_json_shape(payload, errors, warnings)
    validate_declared_outputs(root, payload, errors, warnings)
    validate_preflight_inputs(payload, warnings)
    validate_no_price_fields(payload, errors)
    validate_scope_items(payload, warnings)
    validate_scope_conflicts(payload, warnings)
    validate_traceability(payload, warnings)
    detect_golden_sample_fact_leaks(
        json.dumps(payload, ensure_ascii=False),
        warnings,
        "sow-extraction.json",
        approved_fact_blob,
    )

    room_count = len(payload.get("rooms", [])) if isinstance(payload.get("rooms"), list) else 0
    top_question_count = (
        len(payload.get("open_questions", []))
        if isinstance(payload.get("open_questions"), list)
        else 0
    )

    if proposal_path.exists():
        validate_proposal(
            proposal_path, errors, warnings, room_count, approved_fact_blob
        )
    if proposal_docx_path.exists():
        validate_docx(proposal_docx_path, errors)
    if questions_path.exists():
        rendered_question_count = validate_open_questions(questions_path, errors)
        detect_golden_sample_fact_leaks(
            read_text(questions_path),
            warnings,
            "open-questions.md",
            approved_fact_blob,
        )
        if top_question_count and rendered_question_count and top_question_count != rendered_question_count:
            warnings.append(
                f"open question count differs: JSON has {top_question_count}, open-questions.md has {rendered_question_count}"
            )
        if room_count:
            for stated_count in extract_stated_area_counts(read_text(questions_path)):
                if stated_count != room_count:
                    warnings.append(
                        f"open-questions.md states {stated_count} areas/rooms but sow-extraction.json has {room_count} rooms"
                    )
    if summary_path.exists():
        summary_text = read_text(summary_path)
        if "SOW 已生成" not in summary_text:
            warnings.append("feishu-summary.md does not look like a completion summary")
        if (
            has_flat_core_outputs(root)
            and find_package_file(root) is None
            and re.search(r"\b[\w.-]+-sow\.zip\b|ZIP", summary_text, re.I)
        ):
            warnings.append(
                "feishu-summary.md mentions a ZIP package, but this folder only contains flat core files"
            )
        detect_golden_sample_fact_leaks(
            summary_text, warnings, "feishu-summary.md", approved_fact_blob
        )

    validate_render_manifests(root, errors, warnings)
    validate_drawing_indexes(root, errors, warnings)
    validate_sow_state(root, errors, warnings)
    validate_output_package(root, errors, warnings)

    return CheckResult(errors=errors, warnings=warnings)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", action="store_true", help="Print machine-readable result")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = validate(args.root)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "errors": result.errors,
                    "warnings": result.warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status}: {args.root}")
        for error in result.errors:
            print(f"ERROR: {error}")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
