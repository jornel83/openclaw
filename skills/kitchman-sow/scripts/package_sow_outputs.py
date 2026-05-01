#!/usr/bin/env python3
"""Package rendered Kitchman SOW outputs into a single ZIP.

This script is a delivery helper only. It does not interpret drawings, infer
scope, or modify business content beyond recording package output paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CORE_OUTPUTS = [
    ("sow_extraction_json", "sow-extraction.json", "Structured SOW data"),
    ("proposal_md", "proposal.md", "Markdown proposal"),
    ("proposal_docx", "proposal.docx", "Word proposal"),
    ("open_questions_md", "open-questions.md", "Open questions"),
    ("feishu_summary_md", "feishu-summary.md", "Feishu summary"),
]

MANIFEST_FILENAME = "output-manifest.json"


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str, default: str = "kitchman-sow") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or default


def workspace_root_for(output_dir: Path) -> Path:
    if output_dir.name == "output":
        return output_dir.parent
    return output_dir


def output_ref(path: Path, workspace_root: Path) -> str:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return path.name


def package_name(payload: dict[str, Any]) -> str:
    project = payload.get("project") if isinstance(payload.get("project"), dict) else {}
    project_name = ""
    if isinstance(project, dict):
        project_name = str(project.get("project_name") or "").strip()
    sow_id = str(payload.get("sow_id") or "").strip()
    base = project_name or sow_id or "kitchman-sow"
    return f"{slugify(base)}-sow.zip"


def expected_paths(output_dir: Path) -> dict[str, Path]:
    return {key: output_dir / filename for key, filename, _description in CORE_OUTPUTS}


def update_feishu_summary(summary_path: Path, package_ref: str) -> None:
    lines = [
        "",
        "交付包（优先发送 ZIP；如飞书附件失败，可发送下列单文件）：",
        f"- {package_ref}",
        "",
        "ZIP 内容（5 个核心文件 + 技术清单）：",
    ]
    lines.extend(f"- {filename}" for _key, filename, _description in CORE_OUTPUTS)
    lines.append(f"- {MANIFEST_FILENAME}")
    lines.append("")

    existing = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    existing = re.split(r"\n交付包(?:：|（)", existing, maxsplit=1)[0].rstrip()
    summary_path.write_text(existing.rstrip() + "\n" + "\n".join(lines), encoding="utf-8")


def build_manifest(
    *,
    payload: dict[str, Any],
    output_dir: Path,
    workspace_root: Path,
    zip_path: Path,
    file_paths: dict[str, Path],
) -> dict[str, Any]:
    source_documents = payload.get("source_documents")
    files = []
    for key, filename, description in CORE_OUTPUTS:
        path = file_paths[key]
        files.append(
            {
                "key": key,
                "path": filename,
                "description": description,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    return {
        "schema_version": "kitchman-sow-output-manifest.v1",
        "sow_id": payload.get("sow_id"),
        "package": output_ref(zip_path, workspace_root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "source_documents": source_documents if isinstance(source_documents, list) else [],
        "workspace_output_dir": output_ref(output_dir, workspace_root),
    }


def package_outputs(output_dir: Path) -> dict[str, Any]:
    output_dir = output_dir.expanduser().resolve()
    workspace_root = workspace_root_for(output_dir)
    file_paths = expected_paths(output_dir)
    missing = [str(path) for path in file_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("missing required output files: " + ", ".join(missing))

    sow_path = file_paths["sow_extraction_json"]
    payload = load_json(sow_path)
    zip_path = output_dir / package_name(payload)
    manifest_path = output_dir / MANIFEST_FILENAME

    outputs = payload.get("proposal_outputs")
    if not isinstance(outputs, dict):
        outputs = {}
        payload["proposal_outputs"] = outputs
    workspace_refs = {key: output_ref(path, workspace_root) for key, path in file_paths.items()}
    workspace_refs["sow_package_zip"] = output_ref(zip_path, workspace_root)
    workspace_refs["output_manifest_json"] = output_ref(manifest_path, workspace_root)
    package_refs = {key: filename for key, filename, _description in CORE_OUTPUTS}
    package_refs["output_manifest_json"] = MANIFEST_FILENAME
    delivery_refs = dict(package_refs)
    delivery_refs["sow_package_zip"] = zip_path.name

    # Keep v0.4 flat keys for backwards compatibility, and add v0.5 explicit
    # path groups so Feishu flat-download folders can be validated correctly.
    outputs.update(workspace_refs)
    outputs["workspace_refs"] = workspace_refs
    outputs["package_refs"] = package_refs
    outputs["delivery_refs"] = delivery_refs
    write_json(sow_path, payload)

    update_feishu_summary(file_paths["feishu_summary_md"], outputs["sow_package_zip"])
    manifest = build_manifest(
        payload=payload,
        output_dir=output_dir,
        workspace_root=workspace_root,
        zip_path=zip_path,
        file_paths=file_paths,
    )
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    tmp_zip = zip_path.with_suffix(zip_path.suffix + ".tmp")
    with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as package:
        for _key, filename, _description in CORE_OUTPUTS:
            package.write(output_dir / filename, filename)
        package.write(manifest_path, MANIFEST_FILENAME)
    tmp_zip.replace(zip_path)
    return {
        "package": str(zip_path),
        "manifest": str(manifest_path),
        "files": [filename for _key, filename, _description in CORE_OUTPUTS]
        + [MANIFEST_FILENAME],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = package_outputs(args.output_dir)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
