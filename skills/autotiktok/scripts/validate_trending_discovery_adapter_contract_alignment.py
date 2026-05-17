#!/usr/bin/env python3
"""
Validate focused trending-output fixtures against the discovery adapter contract.
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
    / "validate_trending_discovery_adapter_contract.py"
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
    if "already canonical" not in result.stdout:
        print("[ERROR] canonical trending fixture was not recognized")
        return 1
    if "requires normalization" not in result.stdout:
        print("[ERROR] consolidated trending fixture was not recognized as raw/ranked rows")
        return 1
    print("Trending discovery adapter contract fixtures are aligned.")
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
