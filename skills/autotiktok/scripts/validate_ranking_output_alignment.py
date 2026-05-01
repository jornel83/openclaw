#!/usr/bin/env python3
"""
Validate that the committed ranking sample output matches current deterministic generation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RANKING_SCRIPT = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "scripts" / "dry_run_ranking.py"
)
COMMITTED_RANKING = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
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
        with tempfile.TemporaryDirectory(prefix="autotiktok-ranking-alignment-") as temp_dir:
            ranking_path = Path(temp_dir) / "ranking.json"
            run_script(RANKING_SCRIPT, "--output", str(ranking_path))
            generated_ranking = load_json(ranking_path)
            committed_ranking = load_json(COMMITTED_RANKING)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if generated_ranking != committed_ranking:
        print("[ERROR] committed ranking-dry-run.sample.json is out of sync")
        print("Run: python3 skills/autotiktok/scripts/sync_ranking_sample_output.py")
        return 1

    print("Ranking sample output is aligned with current deterministic generation.")
    print(f"Ranking sample: {COMMITTED_RANKING}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
