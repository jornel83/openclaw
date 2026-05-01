#!/usr/bin/env python3
"""Render PDF drawing pages to PNG images for visual SOW review.

This script only converts PDF pages into PNG files. It does not OCR, parse
drawings, identify rooms, extract scope, or interpret business content.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_DPI = 160
DEFAULT_MAX_PAGES = 100
MANIFEST_FILE_NAME = "render-manifest.json"


@dataclass(frozen=True)
class RenderedPage:
    page_number: int
    image_path: Path
    width: int | None = None
    height: int | None = None


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def ensure_pdf(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"PDF not found: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"PDF path is not a file: {resolved}")
    if resolved.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file: {resolved}")
    return resolved


def render_with_pymupdf(pdf_path: Path, output_dir: Path, max_pages: int, dpi: int) -> list[RenderedPage]:
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed") from exc

    rendered: list[RenderedPage] = []
    document = fitz.open(pdf_path)
    try:
        page_count = min(document.page_count, max_pages)
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        for index in range(page_count):
            page = document.load_page(index)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image_path = output_dir / f"page-{index + 1:03d}.png"
            pixmap.save(image_path)
            rendered.append(
                RenderedPage(
                    page_number=index + 1,
                    image_path=image_path,
                    width=pixmap.width,
                    height=pixmap.height,
                )
            )
    finally:
        document.close()
    return rendered


def render_with_pdftoppm(pdf_path: Path, output_dir: Path, max_pages: int, dpi: int) -> list[RenderedPage]:
    executable = shutil.which("pdftoppm")
    if not executable:
        raise RuntimeError("pdftoppm is not installed")

    prefix = output_dir / "page"
    command = [
        executable,
        "-png",
        "-r",
        str(dpi),
        "-f",
        "1",
        "-l",
        str(max_pages),
        str(pdf_path),
        str(prefix),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"pdftoppm failed: {stderr}")

    rendered: list[RenderedPage] = []
    for path in sorted(output_dir.glob("page-*.png")):
        stem = path.stem
        page_number_text = stem.rsplit("-", 1)[-1]
        try:
            page_number = int(page_number_text)
        except ValueError:
            continue
        normalized = output_dir / f"page-{page_number:03d}.png"
        if path != normalized:
            path.replace(normalized)
            path = normalized
        rendered.append(RenderedPage(page_number=page_number, image_path=path))

    if not rendered:
        raise RuntimeError("pdftoppm completed but produced no PNG pages")
    return rendered[:max_pages]


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


def resolve_node_modules() -> tuple[str, str]:
    return (
        resolve_node_module("pdfjs-dist/legacy/build/pdf.mjs"),
        resolve_node_module("@napi-rs/canvas"),
    )


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
        if result.returncode != 0:
            continue
        resolved = result.stdout.strip()
        if resolved:
            return resolved

    raise RuntimeError(f"{module_spec} was not found from Node resolution roots")


def get_page_count_with_pymupdf(pdf_path: Path) -> int:
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed") from exc

    document = fitz.open(pdf_path)
    try:
        return int(document.page_count)
    finally:
        document.close()


def get_page_count_with_node_pdfjs(pdf_path: Path) -> int:
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
console.log(JSON.stringify({ page_count: pdf.numPages }));
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
        raise RuntimeError(f"Node PDF page-count failed: {stderr}")

    payload = json.loads(result.stdout)
    page_count = payload.get("page_count")
    if not isinstance(page_count, int):
        raise RuntimeError("Node PDF page-count returned an invalid payload")
    return page_count


def get_page_count_with_pdfinfo(pdf_path: Path) -> int:
    executable = shutil.which("pdfinfo")
    if not executable:
        raise RuntimeError("pdfinfo is not installed")

    result = subprocess.run(
        [executable, str(pdf_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"pdfinfo failed: {stderr}")
    for line in result.stdout.splitlines():
        if line.lower().startswith("pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("pdfinfo output did not include Pages")


def get_pdf_page_count(pdf_path: Path) -> int | None:
    for get_count in (
        get_page_count_with_pymupdf,
        get_page_count_with_node_pdfjs,
        get_page_count_with_pdfinfo,
    ):
        try:
            return get_count(pdf_path)
        except Exception:
            continue
    return None


def render_with_node_pdfjs(
    pdf_path: Path, output_dir: Path, max_pages: int, dpi: int
) -> list[RenderedPage]:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not installed")

    pdfjs_path, canvas_path = resolve_node_modules()
    script = r"""
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [pdfPath, outputDir, maxPagesRaw, dpiRaw, pdfjsPath, canvasPath] = process.argv.slice(2);
const maxPages = Number.parseInt(maxPagesRaw, 10);
const dpi = Number.parseInt(dpiRaw, 10);

const pdfjs = await import(pathToFileURL(pdfjsPath).href);
const canvasModule = await import(pathToFileURL(canvasPath).href);
const createCanvas = canvasModule.createCanvas ?? canvasModule.default?.createCanvas;
if (!createCanvas) {
  throw new Error('@napi-rs/canvas createCanvas export was not found');
}

const data = new Uint8Array(await fs.readFile(pdfPath));
const pdf = await pdfjs.getDocument({ data, disableWorker: true }).promise;
const pageCount = Math.min(pdf.numPages, maxPages);
const scale = dpi / 72;
const images = [];

for (let index = 0; index < pageCount; index += 1) {
  const pageNumber = index + 1;
  const page = await pdf.getPage(pageNumber);
  const viewport = page.getViewport({ scale });
  const canvas = createCanvas(Math.ceil(viewport.width), Math.ceil(viewport.height));
  const canvasContext = canvas.getContext('2d');
  await page.render({ canvasContext, viewport }).promise;
  const imagePath = path.join(outputDir, `page-${String(pageNumber).padStart(3, '0')}.png`);
  await fs.writeFile(imagePath, canvas.toBuffer('image/png'));
  images.push({
    page_number: pageNumber,
    image_path: imagePath,
    width: canvas.width,
    height: canvas.height,
  });
}

console.log(JSON.stringify({ images }));
"""

    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)

    try:
        result = subprocess.run(
            [
                node,
                str(script_path),
                str(pdf_path),
                str(output_dir),
                str(max_pages),
                str(dpi),
                pdfjs_path,
                canvas_path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)

    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Node PDF renderer failed: {stderr}")

    payload = json.loads(result.stdout)
    images = payload.get("images")
    if not isinstance(images, list):
        raise RuntimeError("Node PDF renderer returned an invalid payload")

    rendered: list[RenderedPage] = []
    for image in images:
        if not isinstance(image, dict):
            continue
        rendered.append(
            RenderedPage(
                page_number=int(image["page_number"]),
                image_path=Path(str(image["image_path"])),
                width=int(image["width"]) if image.get("width") is not None else None,
                height=int(image["height"]) if image.get("height") is not None else None,
            )
        )
    if not rendered:
        raise RuntimeError("Node PDF renderer completed but produced no PNG pages")
    return rendered


def render_pdf_pages(pdf_path: Path, output_dir: Path, max_pages: int, dpi: int) -> tuple[str, list[RenderedPage]]:
    output_dir.mkdir(parents=True, exist_ok=True)

    for stale in output_dir.glob("page-*.png"):
        stale.unlink()

    try:
        return "pymupdf", render_with_pymupdf(pdf_path, output_dir, max_pages, dpi)
    except Exception as pymupdf_error:
        try:
            return "node-pdfjs", render_with_node_pdfjs(pdf_path, output_dir, max_pages, dpi)
        except Exception as node_error:
            try:
                return "pdftoppm", render_with_pdftoppm(pdf_path, output_dir, max_pages, dpi)
            except Exception as pdftoppm_error:
                raise RuntimeError(
                    "Unable to render PDF pages. Install PyMuPDF (`python3 -m pip install pymupdf`), "
                    "ensure OpenClaw Node dependencies are available, or install Poppler (`pdftoppm`). "
                    f"PyMuPDF error: {pymupdf_error}. Node renderer error: {node_error}. "
                    f"pdftoppm error: {pdftoppm_error}."
                ) from pdftoppm_error


def build_manifest(
    *,
    pdf_path: Path,
    output_dir: Path,
    renderer: str,
    dpi: int,
    max_pages: int,
    source_page_count: int | None,
    rendered_pages: list[RenderedPage],
) -> dict[str, Any]:
    rendered_page_numbers = {page.page_number for page in rendered_pages}
    if source_page_count is None:
        unrendered_pages: list[int] = []
        page_count_truncated = False
    else:
        unrendered_pages = [
            page_number
            for page_number in range(1, source_page_count + 1)
            if page_number not in rendered_page_numbers
        ]
        page_count_truncated = bool(unrendered_pages)

    return {
        "schema_version": "kitchman-sow-rendered-pages.v1",
        "source_pdf": str(pdf_path),
        "output_dir": str(output_dir),
        "renderer": renderer,
        "dpi": dpi,
        "max_pages": max_pages,
        "source_page_count": source_page_count,
        "page_count_rendered": len(rendered_pages),
        "page_count_truncated": page_count_truncated,
        "unrendered_pages": unrendered_pages,
        "images": [
            {
                "page_number": page.page_number,
                "image_path": str(page.image_path),
                "width": page.width,
                "height": page.height,
            }
            for page in rendered_pages
        ],
    }


def write_manifest(output_dir: Path, manifest: dict[str, Any]) -> Path:
    path = output_dir / MANIFEST_FILE_NAME
    tmp_path = path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    tmp_path.replace(path)
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True, help="Input PDF drawing path")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for rendered PNG pages")
    parser.add_argument("--max-pages", type=positive_int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--dpi", type=positive_int, default=DEFAULT_DPI)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        pdf_path = ensure_pdf(args.pdf)
        output_dir = args.output_dir.expanduser().resolve()
        source_page_count = get_pdf_page_count(pdf_path)
        renderer, pages = render_pdf_pages(pdf_path, output_dir, args.max_pages, args.dpi)
        manifest = build_manifest(
            pdf_path=pdf_path,
            output_dir=output_dir,
            renderer=renderer,
            dpi=args.dpi,
            max_pages=args.max_pages,
            source_page_count=source_page_count,
            rendered_pages=pages,
        )
        manifest_path = write_manifest(output_dir, manifest)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "manifest": str(manifest_path),
                "source_page_count": source_page_count,
                "page_count_rendered": len(pages),
                "page_count_truncated": manifest["page_count_truncated"],
                "unrendered_pages": manifest["unrendered_pages"],
                "images": [str(page.image_path) for page in pages],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
