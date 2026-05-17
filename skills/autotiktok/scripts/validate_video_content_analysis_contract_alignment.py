#!/usr/bin/env python3
"""
Validate the focused video-content analysis contract from the AutoTikTok hub.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = (
    ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "scripts"
    / "validate_video_content_analysis_contract.py"
)


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"[ERROR] {VALIDATOR.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        return 1
    for expected in (
        "analysis_succeeded",
        "download_missing",
        "analysis_failed",
        "google/gemini-3-flash-preview",
    ):
        if expected not in result.stdout:
            print(f"[ERROR] video content analysis validator did not report {expected}")
            return 1
    print("Video content analysis contract fixture is aligned.")
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
