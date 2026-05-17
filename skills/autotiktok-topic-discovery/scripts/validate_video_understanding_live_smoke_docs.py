#!/usr/bin/env python3
"""
Validate the video understanding live-ish smoke runbook.
"""

from __future__ import annotations

import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
RUNBOOK = SKILL_DIR / "references" / "video-understanding-live-smoke.md"
REQUIRED_SNIPPETS = (
    "validate_video_content_analysis_batch_runner.py",
    "validate_enriched_signal_items.py",
    "validate_enriched_discovery_ranking_integration.py",
    "run_video_content_analysis_batch.py",
    "build_enriched_signal_items.py",
    "openclaw infer video describe",
    "Do not extract frames",
    "openclaw infer image describe",
    "one-off report",
    "--limit 1",
    "--cache-dir",
    "--continue-on-error",
    "google",
    "gemini-3-flash-preview",
    "google/gemini-3-flash-preview",
    "Do not run broad paid analysis by default.",
    "download the deduped union of both views",
    "--bakeoff-view both",
    "--per-view-max <N>",
    "view out of the final recommendation pool",
)


def main() -> int:
    try:
        text = RUNBOOK.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[ERROR] {exc}")
        return 1

    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        for snippet in missing:
            print(f"[ERROR] runbook missing: {snippet}")
        return 1

    print("Video understanding live-ish smoke runbook is valid.")
    print(f"Runbook: {RUNBOOK.relative_to(SKILL_DIR.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
