#!/usr/bin/env python3
"""Run the local v0.4 delivery smoke test for the kitchman-sow skill.

This verifies output packaging, proposal TBC separation, traceability validation,
and DOCX header/footer assets. It does not interpret drawings or change SOW
business content.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_FIXTURE = SKILL_DIR / "fixtures" / "709-demo"
SMOKE_SOW_ID = "709-demo"
CORE_PACKAGE_FILES = {
    "sow-extraction.json",
    "proposal.md",
    "proposal.docx",
    "open-questions.md",
    "feishu-summary.md",
}
PACKAGE_FILES = CORE_PACKAGE_FILES | {"output-manifest.json"}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        joined = " ".join(command)
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({joined}): {stderr}")
    return result


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def copy_fixture(fixture_root: Path, workspace: Path) -> Path:
    target = workspace / SMOKE_SOW_ID
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(fixture_root, target)
    rewrite_state_workspace(target)
    return target


def rewrite_state_workspace(root: Path) -> None:
    state_path = root / "sow-state.json"
    if not state_path.exists():
        return
    state = load_json(state_path)
    state["workspace"] = {
        "root": str(root),
        "input": str(root / "input"),
        "intermediate": str(root / "intermediate"),
        "output": str(root / "output"),
    }
    state["current_output_version"] = 0
    state["revision_history"] = []
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_outputs(root: Path) -> None:
    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "render_sow_outputs.py"),
            "--input",
            str(root / "output" / "sow-extraction.json"),
            "--output-dir",
            str(root / "output"),
            "--docx",
        ]
    )


def package_outputs(root: Path) -> dict[str, Any]:
    result = run(
        [
            sys.executable,
            str(SCRIPT_DIR / "package_sow_outputs.py"),
            "--output-dir",
            str(root / "output"),
        ]
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("package_sow_outputs did not return a JSON object")
    return payload


def validate_outputs(root: Path) -> None:
    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "validate_sow_outputs.py"),
            "--root",
            str(root),
            "--json",
        ]
    )


def markdown_section(markdown: str, heading: str, next_heading: str) -> str:
    start_marker = f"## {heading}"
    end_marker = f"## {next_heading}"
    start = markdown.find(start_marker)
    end = markdown.find(end_marker, start + len(start_marker))
    if start == -1 or end == -1:
        raise RuntimeError(f"could not locate markdown section: {heading}")
    return markdown[start:end]


def assert_tbc_split(root: Path) -> None:
    proposal = (root / "output" / "proposal.md").read_text(encoding="utf-8")
    working_areas = markdown_section(proposal, "Joinery Working Areas", "TBC Items")
    tbc_items = markdown_section(proposal, "TBC Items", "Joinery Finish Schedule")

    for tbc_label in ("Stone benchtop", "Pantry door cladding", "Mirror"):
        if tbc_label in working_areas:
            raise RuntimeError(f"TBC item leaked into confirmed working areas: {tbc_label}")
        if tbc_label not in tbc_items:
            raise RuntimeError(f"TBC item missing from TBC Items section: {tbc_label}")


def assert_package(root: Path, package_result: dict[str, Any]) -> None:
    zip_path = Path(str(package_result.get("package") or ""))
    if not zip_path.exists():
        raise RuntimeError(f"missing package zip: {zip_path}")
    with zipfile.ZipFile(zip_path) as package:
        names = set(package.namelist())
    if names != PACKAGE_FILES:
        raise RuntimeError(f"unexpected ZIP contents: {sorted(names)}")

    manifest_path = Path(str(package_result.get("manifest") or ""))
    manifest = load_json(manifest_path)
    files = manifest.get("files")
    if not isinstance(files, list):
        raise RuntimeError("manifest files must be a list")
    manifest_names = {str(item.get("path")) for item in files if isinstance(item, dict)}
    if manifest_names != CORE_PACKAGE_FILES:
        raise RuntimeError(f"unexpected manifest contents: {sorted(manifest_names)}")

    extraction = load_json(root / "output" / "sow-extraction.json")
    proposal_outputs = extraction.get("proposal_outputs")
    if not isinstance(proposal_outputs, dict):
        raise RuntimeError("proposal_outputs missing after packaging")
    for key in ("sow_package_zip", "output_manifest_json"):
        if not proposal_outputs.get(key):
            raise RuntimeError(f"proposal_outputs missing {key}")


def assert_docx_branding(root: Path) -> None:
    docx_path = root / "output" / "proposal.docx"
    with zipfile.ZipFile(docx_path) as docx:
        names = set(docx.namelist())
        required = {
            "word/header1.xml",
            "word/footer1.xml",
            "word/_rels/header1.xml.rels",
            "word/media/kitchman-logo.jpeg",
            "word/_rels/document.xml.rels",
            "word/document.xml",
        }
        missing = sorted(required - names)
        if missing:
            raise RuntimeError(f"proposal.docx missing branding parts: {missing}")
        logo = docx.read("word/media/kitchman-logo.jpeg")
        if not (logo.startswith(b"\xff\xd8\xff") and logo.endswith(b"\xff\xd9")):
            raise RuntimeError("embedded Kitchman logo is not a complete JPEG")
        document_xml = docx.read("word/document.xml").decode("utf-8")
        if "headerReference" not in document_xml or "footerReference" not in document_xml:
            raise RuntimeError("proposal.docx missing header/footer references")


def run_smoke_in_workspace(fixture_root: Path, workspace: Path) -> dict[str, Any]:
    root = copy_fixture(fixture_root, workspace)
    render_outputs(root)
    package_result = package_outputs(root)
    assert_tbc_split(root)
    assert_package(root, package_result)
    assert_docx_branding(root)
    validate_outputs(root)
    return {
        "status": "ok",
        "workspace": str(root),
        "checked": [
            "render_sow_outputs --docx",
            "confirmed scope and TBC split",
            "package_sow_outputs ZIP",
            "output-manifest.json",
            "proposal.docx header/footer/logo",
            "validate_sow_outputs",
        ],
    }


def run_smoke(fixture_root: Path, keep_workspace: bool) -> dict[str, Any]:
    if keep_workspace:
        workspace = Path(tempfile.mkdtemp(prefix="kitchman-sow-v04-"))
        result = run_smoke_in_workspace(fixture_root, workspace)
        result["workspace_retained"] = True
        return result

    with tempfile.TemporaryDirectory(prefix="kitchman-sow-v04-") as tmp:
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
