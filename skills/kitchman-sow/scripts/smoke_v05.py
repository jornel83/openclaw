#!/usr/bin/env python3
"""Run the local v0.5 delivery and quality smoke test for kitchman-sow."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from smoke_v04 import (
    CORE_PACKAGE_FILES,
    DEFAULT_FIXTURE,
    SCRIPT_DIR,
    assert_docx_branding,
    assert_package,
    assert_tbc_split,
    copy_fixture,
    package_outputs,
    render_outputs,
    run,
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_outputs_json(root: Path) -> dict[str, Any]:
    result = run(
        [
            sys.executable,
            str(SCRIPT_DIR / "validate_sow_outputs.py"),
            "--root",
            str(root),
            "--json",
        ]
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("validate_sow_outputs did not return a JSON object")
    return payload


def assert_v05_refs(root: Path) -> None:
    extraction = load_json(root / "output" / "sow-extraction.json")
    outputs = extraction.get("proposal_outputs")
    if not isinstance(outputs, dict):
        raise RuntimeError("proposal_outputs missing after packaging")
    for group_name in ("workspace_refs", "package_refs", "delivery_refs"):
        group = outputs.get(group_name)
        if not isinstance(group, dict) or not group:
            raise RuntimeError(f"proposal_outputs missing {group_name}")
    for key in ("sow_package_zip", "output_manifest_json"):
        if key not in outputs["workspace_refs"]:
            raise RuntimeError(f"workspace_refs missing {key}")
        if key not in outputs["delivery_refs"]:
            raise RuntimeError(f"delivery_refs missing {key}")


def assert_flat_delivery_validates(root: Path, workspace: Path) -> None:
    flat_root = workspace / "flat-download"
    flat_root.mkdir()
    for filename in CORE_PACKAGE_FILES:
        shutil.copy2(root / "output" / filename, flat_root / filename)
    result = validate_outputs_json(flat_root)
    if result.get("ok") is not True:
        raise RuntimeError(f"flat delivery should validate without errors: {result}")
    warnings = "\n".join(str(item) for item in result.get("warnings", []))
    if "flat delivery folder contains the five core files" not in warnings:
        raise RuntimeError("flat delivery warning for missing ZIP was not emitted")


def assert_scope_conflict_warning(fixture_root: Path, workspace: Path) -> None:
    conflict_workspace = workspace / "conflict"
    conflict_workspace.mkdir()
    conflict_root = copy_fixture(fixture_root, conflict_workspace)
    extraction_path = conflict_root / "output" / "sow-extraction.json"
    extraction = load_json(extraction_path)
    exclusions = extraction.setdefault("exclusions", [])
    if not isinstance(exclusions, list):
        raise RuntimeError("fixture exclusions must be a list")
    exclusions.append("Stone benchtop excluded from this proposal.")
    write_json(extraction_path, extraction)
    render_outputs(conflict_root)
    package_outputs(conflict_root)
    result = validate_outputs_json(conflict_root)
    warnings = "\n".join(str(item) for item in result.get("warnings", []))
    if "scope item also appears in exclusions" not in warnings:
        raise RuntimeError(f"scope conflict warning was not emitted: {result}")


def assert_high_risk_items_downgrade_to_tbc(fixture_root: Path, workspace: Path) -> None:
    risk_workspace = workspace / "risk"
    risk_workspace.mkdir()
    risk_root = copy_fixture(fixture_root, risk_workspace)
    extraction_path = risk_root / "output" / "sow-extraction.json"
    extraction = load_json(extraction_path)
    rooms = extraction.get("rooms")
    if not isinstance(rooms, list):
        raise RuntimeError("fixture rooms must be a list")
    for room in rooms:
        if not isinstance(room, dict):
            continue
        for item in room.get("scope_items", []):
            if isinstance(item, dict) and item.get("item") == "Stone benchtop":
                item["included"] = True
                item["review_status"] = "approved_for_proposal"
                item["source_type"] = "observed_from_drawing"
    write_json(extraction_path, extraction)
    render_outputs(risk_root)

    proposal = (risk_root / "output" / "proposal.md").read_text(encoding="utf-8")
    working_start = proposal.index("## Joinery Working Areas")
    tbc_start = proposal.index("## TBC Items")
    finish_start = proposal.index("## Joinery Finish Schedule")
    working_section = proposal[working_start:tbc_start]
    tbc_section = proposal[tbc_start:finish_start]
    if "Stone benchtop" in working_section:
        raise RuntimeError("unconfirmed high-risk stone item leaked into confirmed scope")
    if "Stone benchtop" not in tbc_section:
        raise RuntimeError("unconfirmed high-risk stone item was not downgraded to TBC")


def run_smoke_in_workspace(fixture_root: Path, workspace: Path) -> dict[str, Any]:
    root = copy_fixture(fixture_root, workspace)
    render_outputs(root)
    package_result = package_outputs(root)
    assert_tbc_split(root)
    assert_package(root, package_result)
    assert_docx_branding(root)
    assert_v05_refs(root)
    validate_outputs_json(root)
    assert_flat_delivery_validates(root, workspace)
    assert_scope_conflict_warning(fixture_root, workspace)
    assert_high_risk_items_downgrade_to_tbc(fixture_root, workspace)
    return {
        "status": "ok",
        "workspace": str(root),
        "checked": [
            "render_sow_outputs --docx",
            "package_sow_outputs v0.5 refs",
            "validate_sow_outputs workspace",
            "flat Feishu download validation",
            "scope/exclusion conflict warning",
            "high-risk scope downgraded to TBC",
        ],
    }


def run_smoke(fixture_root: Path, keep_workspace: bool) -> dict[str, Any]:
    if keep_workspace:
        workspace = Path(tempfile.mkdtemp(prefix="kitchman-sow-v05-"))
        result = run_smoke_in_workspace(fixture_root, workspace)
        result["workspace_retained"] = True
        return result

    with tempfile.TemporaryDirectory(prefix="kitchman-sow-v05-") as tmp:
        result = run_smoke_in_workspace(fixture_root, Path(tmp))
        result["workspace_retained"] = False
        result["workspace"] = "temporary workspace removed"
        return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--keep-workspace", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = run_smoke(args.fixture_root.expanduser().resolve(), args.keep_workspace)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
