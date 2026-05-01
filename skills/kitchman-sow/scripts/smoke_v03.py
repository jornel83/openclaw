#!/usr/bin/env python3
"""Run the local v0.3 plumbing smoke test for the kitchman-sow skill.

This verifies rendering, DOCX packaging, output-status recovery, revision
metadata recording, and validation. It does not interpret natural language or
modify SOW business content.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_FIXTURE = SKILL_DIR / "fixtures" / "709-demo"
SMOKE_SOW_ID = "709-demo"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        joined = " ".join(command)
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({joined}): {stderr}")
    return result


def load_json_output(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("expected JSON object output")
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
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        return
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


def package_outputs(root: Path) -> None:
    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "package_sow_outputs.py"),
            "--output-dir",
            str(root / "output"),
        ]
    )


def assert_outputs_status(workspace: Path) -> None:
    result = run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sow_state.py"),
            "outputs-status",
            "--workspace",
            str(workspace),
            "--sow-id",
            SMOKE_SOW_ID,
        ]
    )
    status = load_json_output(result)
    if status.get("next_action") != "return_existing_outputs":
        raise RuntimeError(f"expected return_existing_outputs, got {status.get('next_action')}")


def append_revision(workspace: Path, message: str, summary: str, change_type: str, area: str) -> None:
    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sow_state.py"),
            "append-revision",
            "--workspace",
            str(workspace),
            "--sow-id",
            SMOKE_SOW_ID,
            "--message",
            message,
            "--summary",
            summary,
            "--change-type",
            change_type,
            "--affected-area",
            area,
            "--changed-file",
            "output/sow-extraction.json",
            "--changed-file",
            "output/proposal.md",
            "--changed-file",
            "output/proposal.docx",
            "--changed-file",
            "output/open-questions.md",
            "--changed-file",
            "output/feishu-summary.md",
            "--changed-file",
            "output/output-manifest.json",
        ]
    )


def assert_revision_history(root: Path) -> None:
    state_path = root / "sow-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    revisions = state.get("revision_history")
    if not isinstance(revisions, list) or len(revisions) != 2:
        raise RuntimeError("expected two revision history records")
    if state.get("current_output_version") != 2:
        raise RuntimeError("expected current_output_version to be 2")


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


def run_smoke_in_workspace(fixture_root: Path, workspace: Path) -> dict[str, Any]:
    root = copy_fixture(fixture_root, workspace)
    render_outputs(root)
    package_outputs(root)
    assert_outputs_status(workspace)
    append_revision(
        workspace,
        "Kitchen stone 全部排除",
        "Kitchen stone moved to exclusions after agent JSON update",
        "exclusion",
        "GF Kitchen",
    )
    append_revision(
        workspace,
        "Pantry 门只写 cladding",
        "Pantry door wording confirmed as cladding only after agent JSON update",
        "scope",
        "GF Pantry",
    )
    assert_revision_history(root)
    validate_outputs(root)
    return {
        "status": "ok",
        "workspace": str(root),
        "checked": [
            "render_sow_outputs --docx",
            "package_sow_outputs",
            "proposal.docx package",
            "outputs-status return_existing_outputs",
            "append-revision metadata",
            "validate_sow_outputs",
        ],
    }


def run_smoke(fixture_root: Path, keep_workspace: bool) -> dict[str, Any]:
    if keep_workspace:
        workspace = Path(tempfile.mkdtemp(prefix="kitchman-sow-v03-"))
        result = run_smoke_in_workspace(fixture_root, workspace)
        result["workspace_retained"] = True
        return result

    with tempfile.TemporaryDirectory(prefix="kitchman-sow-v03-") as tmp:
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
