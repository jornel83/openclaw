#!/usr/bin/env python3
"""
Validate the video understanding live-ish smoke runbook from the AutoTikTok hub.
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
    / "validate_video_understanding_live_smoke_docs.py"
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
    print("Video understanding live-ish smoke docs are aligned.")
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
