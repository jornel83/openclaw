#!/usr/bin/env python3
"""Lightweight SOW state manager for the kitchman-sow skill.

This script manages sow_id workspaces, output status, and revision history only.
It does not parse documents, interpret drawings, extract scope, or process
natural language.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_FILE_NAME = "sow-state.json"
SCHEMA_VERSION = "kitchman-sow-state.v1"


@dataclass(frozen=True)
class RuntimeRef:
    channel: str = "feishu"
    conversation_id: str = "from-openclaw"
    requested_by: str = "from-openclaw"
    message_id: str | None = None
    run_id: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "untitled"


def short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]


def resolve_sow_id(
    *,
    project_name: str | None = None,
    message_text: str | None = None,
    message_id: str | None = None,
    run_id: str | None = None,
    date: str | None = None,
) -> str:
    """Resolve a stable business id for the SOW workspace."""

    stamp = date or datetime.now().strftime("%Y%m%d")
    if project_name:
        return f"sow-{normalize_slug(project_name)}-{stamp}"

    fallback_source = message_id or run_id or message_text or stamp
    return f"sow-msg-{short_hash(fallback_source)}"


def state_path(workspace: Path, sow_id: str) -> Path:
    return workspace / sow_id / STATE_FILE_NAME


def ensure_workspace(workspace: Path, sow_id: str) -> Path:
    root = workspace / sow_id
    for child in ("input", "intermediate", "output"):
        (root / child).mkdir(parents=True, exist_ok=True)
    return root


def default_state(
    *,
    workspace: Path,
    sow_id: str,
    project_name: str | None,
    runtime_ref: RuntimeRef,
) -> dict[str, Any]:
    now = utc_now()
    root = workspace / sow_id
    return {
        "schema_version": SCHEMA_VERSION,
        "sow_id": sow_id,
        "sow_status": "collecting_inputs",
        "created_at": now,
        "updated_at": now,
        "runtime_ref": {
            "channel": runtime_ref.channel,
            "conversation_id": runtime_ref.conversation_id,
            "requested_by": runtime_ref.requested_by,
            "message_id": runtime_ref.message_id,
            "run_id": runtime_ref.run_id,
        },
        "project": {
            "project_name": project_name or "TBC",
        },
        "workspace": {
            "root": str(root),
            "input": str(root / "input"),
            "intermediate": str(root / "intermediate"),
            "output": str(root / "output"),
        },
        "source_messages": [],
        "source_documents": [],
        "outputs": {
            "sow_extraction": "output/sow-extraction.json",
            "proposal": "output/proposal.md",
            "proposal_docx": "output/proposal.docx",
            "open_questions": "output/open-questions.md",
            "feishu_summary": "output/feishu-summary.md",
            "drawing_index": "intermediate/drawing-index.json",
        },
        "current_output_version": 0,
        "revision_history": [],
    }


def load_sow_state(workspace: Path, sow_id: str) -> dict[str, Any]:
    path = state_path(workspace, sow_id)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def save_sow_state(workspace: Path, sow_id: str, state: dict[str, Any]) -> Path:
    root = ensure_workspace(workspace, sow_id)
    state["updated_at"] = utc_now()
    path = root / STATE_FILE_NAME
    tmp_path = path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    tmp_path.replace(path)
    return path


def init_sow_state(
    *,
    workspace: Path,
    project_name: str | None,
    message_text: str | None,
    runtime_ref: RuntimeRef,
    date: str | None,
) -> dict[str, Any]:
    sow_id = resolve_sow_id(
        project_name=project_name,
        message_text=message_text,
        message_id=runtime_ref.message_id,
        run_id=runtime_ref.run_id,
        date=date,
    )
    path = state_path(workspace, sow_id)
    if path.exists():
        return load_sow_state(workspace, sow_id)
    state = default_state(
        workspace=workspace,
        sow_id=sow_id,
        project_name=project_name,
        runtime_ref=runtime_ref,
    )
    save_sow_state(workspace, sow_id, state)
    return state


def append_revision(
    *,
    workspace: Path,
    sow_id: str,
    message: str,
    summary: str | None,
    actor: str | None,
    change_type: str | None,
    affected_areas: list[str],
    changed_files: list[str],
    output_version: int | None,
) -> dict[str, Any]:
    state = load_sow_state(workspace, sow_id)
    revisions = state.setdefault("revision_history", [])
    if not isinstance(revisions, list):
        raise ValueError("revision_history must be a list")
    revision_id = f"rev-{len(revisions) + 1:03d}"
    resolved_output_version = output_version or int(state.get("current_output_version") or 0) + 1
    revisions.append(
        {
            "revision_id": revision_id,
            "timestamp": utc_now(),
            "actor": actor or "from-openclaw",
            "message": message,
            "summary": summary or "",
            "change_type": change_type or "other",
            "affected_areas": affected_areas,
            "changed_files": changed_files,
            "output_version": resolved_output_version,
        }
    )
    state["sow_status"] = "revision_completed"
    state["current_output_version"] = resolved_output_version
    save_sow_state(workspace, sow_id, state)
    return state


def existing_output_status(*, workspace: Path, sow_id: str) -> dict[str, Any]:
    root = workspace / sow_id
    files = {
        "sow_extraction_json": root / "output" / "sow-extraction.json",
        "proposal_md": root / "output" / "proposal.md",
        "proposal_docx": root / "output" / "proposal.docx",
        "open_questions_md": root / "output" / "open-questions.md",
        "feishu_summary_md": root / "output" / "feishu-summary.md",
        "drawing_index_json": root / "intermediate" / "drawing-index.json",
    }

    file_status: dict[str, Any] = {}
    for key, path in files.items():
        exists = path.exists() and path.is_file() and path.stat().st_size > 0
        file_status[key] = {
            "path": str(path),
            "exists": exists,
            "size_bytes": path.stat().st_size if exists else 0,
        }

    has_structured_json = file_status["sow_extraction_json"]["exists"]
    has_returnable_outputs = all(
        file_status[key]["exists"]
        for key in ("proposal_md", "proposal_docx", "open_questions_md", "feishu_summary_md")
    )
    if has_structured_json and has_returnable_outputs:
        next_action = "return_existing_outputs"
    elif has_structured_json:
        next_action = "render_outputs_then_return"
    else:
        next_action = "continue_generation"

    return {
        "schema_version": "kitchman-sow-output-status.v1",
        "sow_id": sow_id,
        "workspace_root": str(root),
        "current_output_version": load_current_output_version(workspace, sow_id),
        "next_action": next_action,
        "ready_to_return": next_action == "return_existing_outputs",
        "files": file_status,
    }


def load_current_output_version(workspace: Path, sow_id: str) -> int | None:
    path = state_path(workspace, sow_id)
    if not path.exists():
        return None
    try:
        state = load_sow_state(workspace, sow_id)
    except Exception:
        return None
    value = state.get("current_output_version")
    return value if isinstance(value, int) else None


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or load SOW state")
    init_parser.add_argument("--workspace", type=Path, required=True)
    init_parser.add_argument("--project-name")
    init_parser.add_argument("--message-text")
    init_parser.add_argument("--message-id")
    init_parser.add_argument("--run-id")
    init_parser.add_argument("--conversation-id", default="from-openclaw")
    init_parser.add_argument("--requested-by", default="from-openclaw")
    init_parser.add_argument("--channel", default="feishu")
    init_parser.add_argument("--date", help="YYYYMMDD override for deterministic demos")

    show_parser = subparsers.add_parser("show", help="Print existing SOW state")
    show_parser.add_argument("--workspace", type=Path, required=True)
    show_parser.add_argument("--sow-id", required=True)

    revision_parser = subparsers.add_parser(
        "append-revision", help="Append a revision record"
    )
    revision_parser.add_argument("--workspace", type=Path, required=True)
    revision_parser.add_argument("--sow-id", required=True)
    revision_parser.add_argument("--message", required=True)
    revision_parser.add_argument("--summary")
    revision_parser.add_argument("--actor")
    revision_parser.add_argument("--change-type")
    revision_parser.add_argument("--affected-area", action="append", default=[])
    revision_parser.add_argument("--changed-file", action="append", default=[])
    revision_parser.add_argument("--output-version", type=int)

    status_parser = subparsers.add_parser(
        "outputs-status", help="Check generated SOW output files for timeout recovery"
    )
    status_parser.add_argument("--workspace", type=Path, required=True)
    status_parser.add_argument("--sow-id", required=True)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "init":
        state = init_sow_state(
            workspace=args.workspace,
            project_name=args.project_name,
            message_text=args.message_text,
            runtime_ref=RuntimeRef(
                channel=args.channel,
                conversation_id=args.conversation_id,
                requested_by=args.requested_by,
                message_id=args.message_id,
                run_id=args.run_id,
            ),
            date=args.date,
        )
        print_json(state)
        return 0
    if args.command == "show":
        print_json(load_sow_state(args.workspace, args.sow_id))
        return 0
    if args.command == "append-revision":
        print_json(
            append_revision(
                workspace=args.workspace,
                sow_id=args.sow_id,
                message=args.message,
                summary=args.summary,
                actor=args.actor,
                change_type=args.change_type,
                affected_areas=args.affected_area,
                changed_files=args.changed_file,
                output_version=args.output_version,
            )
        )
        return 0
    if args.command == "outputs-status":
        print_json(existing_output_status(workspace=args.workspace, sow_id=args.sow_id))
        return 0
    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
