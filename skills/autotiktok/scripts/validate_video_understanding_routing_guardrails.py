#!/usr/bin/env python3
"""
Validate AutoTikTok video-understanding routing guardrails across skills.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

REQUIRED_SNIPPETS_BY_FILE = {
    "skills/autotiktok/SKILL.md": (
        "download plus video understanding",
        "openclaw infer video describe through run_video_content_analysis_batch.py",
        "google/gemini-3-flash-preview",
        "must not be replaced by ffmpeg frame",
        "auto-selected alternate video model",
        "complete AutoTikTok chain",
        "run_video_content_analysis_batch.py",
        "openclaw infer video describe",
        "deduped union of both views",
        "--bakeoff-view both --per-view-max N",
        "Do not run",
        "`autotiktok-video-download --from-bakeoff ... --max N`",
        "`视频文件` column",
        "build_ranking_report.py",
        "Do not satisfy AutoTikTok video understanding by extracting MP4 frames",
        "one-off `report_gen.py`",
    ),
    "skills/autotiktok-topic-discovery/SKILL.md": (
        "downloaded TikTok MP4 analysis",
        "read this skill first",
        "must not use ffmpeg",
        "google/gemini-3-flash-preview",
        "auto-selected alternate models",
        "official path is native OpenClaw video",
        "run_video_content_analysis_batch.py",
        "openclaw infer video describe",
        "`--view both` only when",
        "--bakeoff-view both --per-view-max N",
        "those `fresh_hot` sample IDs must appear as `downloaded`",
        "Do not extract frames",
        "image-description tools",
        "rebuild or correct the normalized `videoDownloadManifest`",
    ),
    "skills/autotiktok-video-download/SKILL.md": (
        "also read autotiktok-topic-discovery",
        "must not use ffmpeg",
        "normalized `videoDownloadManifest`",
        "deduped union of both views",
        "--bakeoff-view <all|both|absolute_hot|fresh_hot>",
        "--per-view-max <n>",
        "leave `fresh_hot` as `download_missing`",
        "Do not extract frames",
        "image analysis",
        "openclaw infer video describe --model google/gemini-3-flash-preview",
    ),
    "skills/autotiktok-topic-discovery/references/video-understanding-live-smoke.md": (
        "only official live-ish MP4 understanding entry point",
        "openclaw infer video describe",
        "google/gemini-3-flash-preview",
        "download the deduped union of both views",
        "view out of the final recommendation pool",
        "Do not extract frames",
        "openclaw infer image describe",
        "one-off report",
    ),
}


def main() -> int:
    errors: list[str] = []
    for relative_path, snippets in REQUIRED_SNIPPETS_BY_FILE.items():
        path = ROOT / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{relative_path}: {exc}")
            continue
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{relative_path}: missing {snippet!r}")

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    print("Video understanding routing guardrails are valid.")
    for relative_path in REQUIRED_SNIPPETS_BY_FILE:
        print(f"- {relative_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
