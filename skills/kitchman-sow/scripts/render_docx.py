#!/usr/bin/env python3
"""Render a simple DOCX proposal from proposal.md.

This script is a formatter only. It converts already-rendered Markdown into a
readable Word document and does not interpret drawings, infer scope, or change
business content.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import zipfile
from pathlib import Path


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SCRIPT_DIR = Path(__file__).resolve().parent
ASSET_DIR = SCRIPT_DIR.parent / "assets"


def xml_escape(value: str) -> str:
    return html.escape(value, quote=False)


def strip_inline_markdown(value: str) -> str:
    value = value.replace("**", "")
    value = re.sub(r"`([^`]+)`", r"\1", value)
    return value


def paragraph_xml(text: str, style: str | None = None) -> str:
    text = strip_inline_markdown(text)
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    if not text:
        return "<w:p/>"
    return (
        "<w:p>"
        f"{style_xml}"
        "<w:r>"
        f"<w:t xml:space=\"preserve\">{xml_escape(text)}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def table_xml(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    parts = [
        "<w:tbl>",
        "<w:tblPr>",
        '<w:tblStyle w:val="TableGrid"/>',
        "<w:tblBorders>",
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>',
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>',
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>',
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>',
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>',
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>',
        "</w:tblBorders>",
        "</w:tblPr>",
    ]
    for row in rows:
        parts.append("<w:tr>")
        for cell in row:
            cell_parts = [
                paragraph_xml(part.strip())
                for part in cell.replace("<br>", "\n").splitlines()
                if part.strip()
            ]
            if not cell_parts:
                cell_parts = [paragraph_xml("")]
            parts.append("<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>")
            parts.extend(cell_parts)
            parts.append("</w:tc>")
        parts.append("</w:tr>")
    parts.append("</w:tbl>")
    return "".join(parts)


def is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return cells


def body_xml(markdown: str) -> str:
    lines = markdown.splitlines()
    parts: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        cells = parse_table_row(line)
        if cells is not None:
            table_rows: list[list[str]] = []
            while index < len(lines):
                row_cells = parse_table_row(lines[index])
                if row_cells is None:
                    break
                if not is_table_separator(row_cells):
                    table_rows.append(row_cells)
                index += 1
            parts.append(table_xml(table_rows))
            continue

        stripped = line.strip()
        if not stripped:
            parts.append(paragraph_xml(""))
        elif stripped.startswith("### "):
            parts.append(paragraph_xml(stripped[4:], "Heading3"))
        elif stripped.startswith("## "):
            parts.append(paragraph_xml(stripped[3:], "Heading2"))
        elif stripped.startswith("# "):
            parts.append(paragraph_xml(stripped[2:], "Heading1"))
        elif stripped.startswith("- "):
            parts.append(paragraph_xml(f"- {stripped[2:]}", "ListParagraph"))
        elif re.match(r"^\d+\.\s+", stripped):
            parts.append(paragraph_xml(stripped, "ListParagraph"))
        else:
            parts.append(paragraph_xml(stripped))
        index += 1

    return "".join(parts)


def document_xml(markdown: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
        "<w:body>"
        f"{body_xml(markdown)}"
        "<w:sectPr>"
        '<w:headerReference w:type="default" r:id="rIdHeader"/>'
        '<w:footerReference w:type="default" r:id="rIdFooter"/>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1800" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr>"
        "</w:body>"
        "</w:document>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:styles xmlns:w="{W_NS}">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/>'
        '<w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="22"/></w:rPr>'
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading1">'
        '<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
        '<w:rPr><w:b/><w:sz w:val="32"/></w:rPr>'
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading2">'
        '<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
        '<w:rPr><w:b/><w:sz w:val="26"/></w:rPr>'
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading3">'
        '<w:name w:val="heading 3"/><w:basedOn w:val="Normal"/>'
        '<w:rPr><w:b/><w:sz w:val="23"/></w:rPr>'
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="ListParagraph">'
        '<w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:ind w:left="720"/></w:pPr>'
        "</w:style>"
        '<w:style w:type="table" w:styleId="TableGrid">'
        '<w:name w:val="Table Grid"/>'
        '<w:tblPr><w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        "</w:tblBorders></w:tblPr>"
        "</w:style>"
        "</w:styles>"
    )


def content_types_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="jpeg" ContentType="image/jpeg"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/header1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
        '<Override PartName="/word/footer1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        "</Types>"
    )


def rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )


def document_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdHeader" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" '
        'Target="header1.xml"/>'
        '<Relationship Id="rIdFooter" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
        'Target="footer1.xml"/>'
        "</Relationships>"
    )


def header_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdLogo" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
        'Target="media/kitchman-logo.jpeg"/>'
        "</Relationships>"
    )


def header_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:hdr xmlns:w="{W_NS}" xmlns:r="{R_NS}" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="4572000" cy="1325000"/>'
        '<wp:docPr id="1" name="Kitchman logo"/>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="Kitchman logo"/>'
        '<pic:cNvPicPr/></pic:nvPicPr><pic:blipFill>'
        '<a:blip r:embed="rIdLogo"/><a:stretch><a:fillRect/></a:stretch>'
        '</pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        '<a:ext cx="4572000" cy="1325000"/></a:xfrm><a:prstGeom prst="rect">'
        '<a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
        '</wp:inline></w:drawing></w:r></w:p>'
        '<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="8" w:space="1" w:color="000000"/>'
        '</w:pBdr></w:pPr></w:p>'
        '</w:hdr>'
    )


def footer_xml() -> str:
    footer_text = (
        "Kitchman Pty Ltd    A 75 Indian Drive, Keysborough VIC 3173    "
        "P +61 3 9768 7218"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
        '<w:p><w:pPr><w:jc w:val="center"/><w:rPr>'
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="FF5800"/>'
        '<w:sz w:val="18"/></w:rPr></w:pPr><w:r><w:rPr>'
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="FF5800"/>'
        '<w:sz w:val="18"/></w:rPr>'
        f'<w:t xml:space="preserve">{xml_escape(footer_text)}</w:t>'
        '</w:r></w:p>'
        '</w:ftr>'
    )


def logo_bytes() -> bytes:
    binary_asset = ASSET_DIR / "kitchman-logo.jpeg"
    if not binary_asset.exists():
        raise FileNotFoundError(f"missing DOCX header logo asset: {binary_asset}")
    return binary_asset.read_bytes()


def render_docx_from_markdown(markdown: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types_xml())
        docx.writestr("_rels/.rels", rels_xml())
        docx.writestr("word/document.xml", document_xml(markdown))
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/_rels/document.xml.rels", document_rels_xml())
        docx.writestr("word/header1.xml", header_xml())
        docx.writestr("word/footer1.xml", footer_xml())
        docx.writestr("word/_rels/header1.xml.rels", header_rels_xml())
        docx.writestr("word/media/kitchman-logo.jpeg", logo_bytes())
    tmp_path.replace(output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to proposal.md")
    parser.add_argument("--output", type=Path, required=True, help="Path to proposal.docx")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        input_path = args.input.expanduser().resolve()
        output_path = args.output.expanduser().resolve()
        markdown = input_path.read_text(encoding="utf-8")
        render_docx_from_markdown(markdown, output_path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
