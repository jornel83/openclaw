#!/usr/bin/env python3
"""Build a lightweight drawing page index for Kitchman SOW review.

This script extracts embedded PDF text only to identify page labels, drawing
numbers, and coarse area title candidates. It does not OCR, interpret drawings,
extract joinery scope, decide inclusions, or replace visual page review.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "kitchman-sow-drawing-index.v1"

AREA_PATTERNS: tuple[tuple[str, str], ...] = (
    ("Kitchen", r"\bKITCHEN\b"),
    ("Pantry", r"\bPANTRY\b"),
    ("Living", r"\bLIVING\b|\bTV\s+UNIT\b"),
    ("Cloak", r"\bCLOAK\b|\bCOAT\b"),
    ("Laundry", r"\bLAUNDRY\b|\bLINEN\b"),
    ("Ensuite", r"\bENSUITE\b"),
    ("Master WIR", r"\bMASTER\s+WIR\b|\bWIR\b|\bWALK[- ]?IN\s+ROBE\b"),
    ("Bathroom", r"\bBATHROOM\b|\bBATH\b"),
    ("Robe 2", r"\bROBE\s*2\b|\bBED\s*2\b|\bB2\s+ROBE\b"),
    ("Robe 3", r"\bROBE\s*3\b|\bBED\s*3\b|\bB3\s+ROBE\b"),
    ("Bedroom", r"\bBED(?:ROOM)?\s*[1-5]\b"),
)

DRAWING_NUMBER_RE = re.compile(
    r"\b(?:JD|WD|A|ID)\s*[- ]?\d{1,3}(?:\s*[-–]\s*\d{1,3})?\b",
    re.I,
)


@dataclass(frozen=True)
class TextPage:
    page_number: int
    text: str


def ensure_pdf(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"PDF not found: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"PDF path is not a file: {resolved}")
    if resolved.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file: {resolved}")
    return resolved


def candidate_node_resolution_roots() -> list[Path]:
    roots: list[Path] = []

    def add(path: Path) -> None:
        resolved = path.expanduser().resolve()
        if resolved not in roots:
            roots.append(resolved)

    add(Path.cwd())
    for parent in Path(__file__).resolve().parents:
        add(parent)

    openclaw_bin = shutil.which("openclaw")
    if openclaw_bin:
        resolved_bin = Path(openclaw_bin).resolve()
        for parent in resolved_bin.parents:
            add(parent)

    return roots


def resolve_node_module(module_spec: str) -> str:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not installed")

    resolver = """
const root = process.argv[1];
const moduleSpec = process.argv[2];
try {
  console.log(require.resolve(moduleSpec, { paths: [root] }));
} catch (err) {
  process.exit(1);
}
"""

    for root in candidate_node_resolution_roots():
        result = subprocess.run(
            [node, "-e", resolver, str(root), module_spec],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    raise RuntimeError(f"{module_spec} was not found from Node resolution roots")


def extract_text_with_pymupdf(pdf_path: Path) -> list[TextPage]:
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed") from exc

    pages: list[TextPage] = []
    document = fitz.open(pdf_path)
    try:
        for index in range(document.page_count):
            page = document.load_page(index)
            pages.append(TextPage(page_number=index + 1, text=page.get_text("text")))
    finally:
        document.close()
    return pages


def extract_text_with_node_pdfjs(pdf_path: Path) -> list[TextPage]:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not installed")

    pdfjs_path = resolve_node_module("pdfjs-dist/legacy/build/pdf.mjs")
    script = r"""
import fs from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const [pdfPath, pdfjsPath] = process.argv.slice(2);
const pdfjs = await import(pathToFileURL(pdfjsPath).href);
const data = new Uint8Array(await fs.readFile(pdfPath));
const pdf = await pdfjs.getDocument({ data, disableWorker: true }).promise;
const pages = [];

for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
  const page = await pdf.getPage(pageNumber);
  const content = await page.getTextContent();
  const text = content.items
    .map((item) => (typeof item.str === 'string' ? item.str : ''))
    .filter(Boolean)
    .join('\n');
  pages.push({ page_number: pageNumber, text });
}

console.log(JSON.stringify({ pages }));
"""

    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)

    try:
        result = subprocess.run(
            [node, str(script_path), str(pdf_path), pdfjs_path],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)

    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Node PDF text extraction failed: {stderr}")

    payload = json.loads(result.stdout)
    raw_pages = payload.get("pages")
    if not isinstance(raw_pages, list):
        raise RuntimeError("Node PDF text extraction returned an invalid payload")
    pages: list[TextPage] = []
    for raw_page in raw_pages:
        if isinstance(raw_page, dict):
            pages.append(
                TextPage(
                    page_number=int(raw_page["page_number"]),
                    text=str(raw_page.get("text") or ""),
                )
            )
    return pages


def extract_pdf_text_pages(pdf_path: Path) -> tuple[str, list[TextPage]]:
    for extractor_name, extractor in (
        ("pymupdf", extract_text_with_pymupdf),
        ("node-pdfjs", extract_text_with_node_pdfjs),
    ):
        try:
            return extractor_name, extractor(pdf_path)
        except Exception:
            continue
    return "none", []


def compact_lines(text: str, limit: int = 30) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        if len(line) > 140:
            line = line[:137] + "..."
        lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def drawing_numbers(text: str) -> list[str]:
    seen: list[str] = []
    for match in DRAWING_NUMBER_RE.finditer(text):
        value = re.sub(r"\s+", " ", match.group(0).upper()).strip()
        if value not in seen:
            seen.append(value)
    return seen


def area_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for label, pattern in AREA_PATTERNS:
        if re.search(pattern, text, re.I) and label not in candidates:
            candidates.append(label)
    return candidates


def title_candidate(lines: list[str], areas: list[str], drawing_nos: list[str]) -> str:
    selected: list[str] = []
    for line in lines:
        upper = line.upper()
        if any(area.upper() in upper for area in areas) or DRAWING_NUMBER_RE.search(line):
            selected.append(line)
        if len(selected) >= 3:
            break
    if not selected:
        selected = lines[:2]
    if drawing_nos and not any(drawing_no in " ".join(selected).upper() for drawing_no in drawing_nos):
        selected.insert(0, drawing_nos[0])
    return " / ".join(selected)[:240]


def load_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"render manifest not found: {resolved}")
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("render manifest must contain a JSON object")
    return payload


def image_paths_by_page(manifest: dict[str, Any]) -> dict[int, str]:
    result: dict[int, str] = {}
    images = manifest.get("images")
    if not isinstance(images, list):
        return result
    for image in images:
        if not isinstance(image, dict):
            continue
        page_number = image.get("page_number")
        image_path = image.get("image_path")
        if isinstance(page_number, int) and isinstance(image_path, str):
            result[page_number] = image_path
    return result


def build_index(pdf_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    text_extractor, text_pages = extract_pdf_text_pages(pdf_path)
    text_by_page = {page.page_number: page.text for page in text_pages}
    image_by_page = image_paths_by_page(manifest)
    render_coverage_known = bool(manifest)

    source_page_count = manifest.get("source_page_count")
    if not isinstance(source_page_count, int):
        source_page_count = len(text_pages) if text_pages else None

    page_numbers: set[int] = set(text_by_page)
    page_numbers.update(image_by_page)
    if source_page_count:
        page_numbers.update(range(1, source_page_count + 1))

    pages: list[dict[str, Any]] = []
    area_summary: dict[str, list[int]] = {}
    for page_number in sorted(page_numbers):
        text = text_by_page.get(page_number, "")
        lines = compact_lines(text)
        drawing_nos = drawing_numbers(text)
        areas = area_candidates(text)
        for area in areas:
            area_summary.setdefault(area, []).append(page_number)
        pages.append(
            {
                "page_number": page_number,
                "rendered": page_number in image_by_page,
                "image_path": image_by_page.get(page_number),
                "drawing_numbers": drawing_nos,
                "area_title_candidates": areas,
                "title_candidate": title_candidate(lines, areas, drawing_nos),
                "text_excerpt": lines[:8],
            }
        )

    rendered_count = len(image_by_page) if render_coverage_known else None
    if render_coverage_known:
        unrendered_pages = [
            page_number
            for page_number in sorted(page_numbers)
            if source_page_count and page_number <= source_page_count and page_number not in image_by_page
        ]
        page_count_truncated: bool | None = bool(unrendered_pages)
    else:
        unrendered_pages = []
        page_count_truncated = None

    return {
        "schema_version": SCHEMA_VERSION,
        "source_pdf": str(pdf_path),
        "text_extractor": text_extractor,
        "source_page_count": source_page_count,
        "render_coverage_known": render_coverage_known,
        "rendered_page_count": rendered_count,
        "page_count_truncated": page_count_truncated,
        "unrendered_pages": unrendered_pages,
        "area_candidates": [
            {"area": area, "pages": pages}
            for area, pages in sorted(area_summary.items(), key=lambda item: item[0])
        ],
        "pages": pages,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    tmp_path.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True, help="Input PDF drawing path")
    parser.add_argument("--render-manifest", type=Path, help="render-manifest.json path")
    parser.add_argument("--output", type=Path, required=True, help="Output drawing-index.json path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        pdf_path = ensure_pdf(args.pdf)
        manifest = load_manifest(args.render_manifest)
        index = build_index(pdf_path, manifest)
        output_path = args.output.expanduser().resolve()
        write_json(output_path, index)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "drawing_index": str(output_path),
                "source_page_count": index.get("source_page_count"),
                "rendered_page_count": index.get("rendered_page_count"),
                "page_count_truncated": index.get("page_count_truncated"),
                "area_candidate_count": len(index.get("area_candidates", [])),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
