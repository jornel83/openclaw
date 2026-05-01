#!/usr/bin/env python3
"""
Validate that the committed optimizer input bundle matches current deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "materialize_optimizer_input_bundle.py"
)
MANIFEST_BUILD_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_manifest.py"
)
COMMITTED_BUNDLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-bundle.sample.json"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-optimizer-bundle-") as temp_dir:
            manifest_path = Path(temp_dir) / "optimizer-input-manifest.json"
            bundle_path = Path(temp_dir) / "optimizer-input-bundle.json"
            run_script(MANIFEST_BUILD_SCRIPT, "--output", str(manifest_path))
            run_script(BUILD_SCRIPT, "--input-manifest", str(manifest_path), "--output", str(bundle_path))
            generated_bundle = load_json(bundle_path)
            committed_bundle = load_json(COMMITTED_BUNDLE)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_bundle != committed_bundle:
        print("[ERROR] committed optimizer-input-bundle.sample.json is out of sync")
        print("Run: python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_input_bundle.py")
        return 1

    print("Optimizer input bundle is aligned with current deterministic generation.")
    print(f"Input bundle: {COMMITTED_BUNDLE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
