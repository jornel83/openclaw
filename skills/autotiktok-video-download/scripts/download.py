#!/usr/bin/env python3
"""Download public TikTok videos via yt-dlp and emit a JSON manifest.

This is the script behind the tiktok-video-download skill. It accepts URLs
from --url, --urls-file, or a tiktok-trending bakeoff JSON, downloads each
video to --out-dir, and writes --manifest with per-video status and metadata.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yt_dlp
except ImportError as exc:  # pragma: no cover - handled at runtime
    print("yt-dlp is required. Install with: pip install yt-dlp", file=sys.stderr)
    raise SystemExit(1) from exc


TIKTOK_VIDEO_URL_RE = re.compile(
    r"https?://(?:www\.|m\.|vm\.|vt\.)?tiktok\.com/[^\s\"']+",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download public TikTok videos via yt-dlp")
    parser.add_argument("--url", action="append", default=[], help="TikTok video URL (repeatable)")
    parser.add_argument("--urls-file", help="Text file with one TikTok URL per line")
    parser.add_argument("--from-bakeoff", help="tiktok-trending bakeoff JSON to read URLs from")
    parser.add_argument("--out-dir", required=True, help="Directory for downloaded videos")
    parser.add_argument("--manifest", required=True, help="JSON manifest output path")
    parser.add_argument("--max", type=int, default=0, help="Hard cap on URLs (0 = no cap)")
    parser.add_argument("--format", default="best", help="yt-dlp format selector")
    parser.add_argument(
        "--filename-template",
        default="%(id)s.%(ext)s",
        help="yt-dlp outtmpl filename template (relative to --out-dir)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Re-download even if file exists")
    parser.add_argument("--quiet", action="store_true", help="Suppress yt-dlp progress output")
    return parser.parse_args()


def collect_urls_from_text(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    urls: list[str] = []
    for line in raw.splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        if TIKTOK_VIDEO_URL_RE.search(candidate):
            urls.append(candidate)
    return urls


def collect_urls_from_bakeoff(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    urls: list[str] = []
    routes = data.get("routes") or []
    for route in routes:
        for key in ("videos", "fresh_hot_videos"):
            for video in route.get(key, []) or []:
                url = video.get("url") or video.get("share_url")
                if isinstance(url, str) and url:
                    urls.append(url)
        for sample_key in ("absolute_hot_video_samples", "fresh_hot_video_samples"):
            artifact = route.get(sample_key) or {}
            for sample in artifact.get("videoSamples", []) or []:
                url = sample.get("shareUrl") or sample.get("rawMeta", {}).get("url")
                if isinstance(url, str) and url:
                    urls.append(url)
    return urls


def dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def extract_video_id(url: str) -> str:
    match = re.search(r"/video/(\d+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/v/(\d+)", url)
    if match:
        return match.group(1)
    return ""


def extract_author(url: str) -> str:
    match = re.search(r"/@([^/]+)/", url)
    return match.group(1) if match else ""


def download_one(url: str, out_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    video_id = extract_video_id(url)
    author = extract_author(url)
    base_record: dict[str, Any] = {
        "url": url,
        "video_id": video_id,
        "author": author,
    }

    ydl_opts: dict[str, Any] = {
        "outtmpl": str(out_dir / args.filename_template),
        "format": args.format,
        "noplaylist": True,
        "quiet": args.quiet,
        "no_warnings": args.quiet,
        "overwrites": args.overwrite,
        "retries": 3,
        "fragment_retries": 3,
        "concurrent_fragment_downloads": 1,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not args.overwrite:
                # Pre-check: if a file with the templated name already exists, skip download.
                try:
                    info_only = ydl.extract_info(url, download=False)
                    expected = ydl.prepare_filename(info_only)
                    if expected and Path(expected).is_file():
                        stat = Path(expected).stat()
                        return {
                            **base_record,
                            "video_id": str(info_only.get("id") or video_id),
                            "author": str(info_only.get("uploader") or author),
                            "status": "skipped",
                            "file": str(Path(expected).resolve()),
                            "size_bytes": stat.st_size,
                            "duration_sec": int(info_only.get("duration") or 0),
                            "title": info_only.get("title") or "",
                            "format_id": info_only.get("format_id") or "",
                        }
                except Exception:
                    # Fall through to actual download attempt
                    pass

            info = ydl.extract_info(url, download=True)
            file_path_str = ydl.prepare_filename(info)
            file_path = Path(file_path_str)
            size_bytes = file_path.stat().st_size if file_path.is_file() else 0
            return {
                **base_record,
                "video_id": str(info.get("id") or video_id),
                "author": str(info.get("uploader") or author),
                "status": "ok",
                "file": str(file_path.resolve()),
                "size_bytes": size_bytes,
                "duration_sec": int(info.get("duration") or 0),
                "title": info.get("title") or "",
                "format_id": info.get("format_id") or "",
            }
    except Exception as exc:
        return {
            **base_record,
            "status": "error",
            "error": str(exc),
        }


def main() -> int:
    args = parse_args()

    urls: list[str] = list(args.url)
    if args.urls_file:
        urls.extend(collect_urls_from_text(Path(args.urls_file)))
    if args.from_bakeoff:
        urls.extend(collect_urls_from_bakeoff(Path(args.from_bakeoff)))
    urls = dedupe_urls([u for u in urls if u and TIKTOK_VIDEO_URL_RE.search(u)])
    if args.max and args.max > 0:
        urls = urls[: args.max]

    if not urls:
        print("No TikTok URLs supplied (use --url, --urls-file, or --from-bakeoff)", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for index, url in enumerate(urls, start=1):
        print(f"[{index}/{len(urls)}] {url}", file=sys.stderr)
        record = download_one(url, out_dir, args)
        results.append(record)

    summary = {
        "ok": sum(1 for r in results if r.get("status") == "ok"),
        "skipped": sum(1 for r in results if r.get("status") == "skipped"),
        "error": sum(1 for r in results if r.get("status") == "error"),
        "total": len(results),
    }

    manifest = {
        "skill": "tiktok-video-download",
        "out_dir": str(out_dir.resolve()),
        "summary": summary,
        "downloads": results,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"Wrote {summary['ok']} ok, {summary['skipped']} skipped, "
        f"{summary['error']} error to {manifest_path}",
        file=sys.stderr,
    )
    return 0 if summary["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
