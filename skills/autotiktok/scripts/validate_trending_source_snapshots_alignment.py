#!/usr/bin/env python3
"""
Validate sourceSnapshots generation from focused AutoTikTok trending fixtures.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_SCRIPT_DIR = ROOT / "skills" / "autotiktok-topic-discovery" / "scripts"
sys.path.insert(0, str(DISCOVERY_SCRIPT_DIR))

from discovery_lib import validate_source_snapshots_fixture  # noqa: E402


BUILDER = DISCOVERY_SCRIPT_DIR / "build_trending_source_snapshots.py"
FIXTURES = {
    "bakeoff": ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "trending-bakeoff.sample.json",
    "consolidated": ROOT
    / "skills"
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "trending-consolidated-hot.sample.json",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_builder(input_path: Path, output_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{BUILDER.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def validate_payload(label: str, payload: dict[str, Any]) -> list[str]:
    errors = validate_source_snapshots_fixture(payload)
    if errors:
        return [f"{label}: {error}" for error in errors]
    source_snapshots = payload.get("sourceSnapshots") or []
    if not source_snapshots:
        return [f"{label}: sourceSnapshots must not be empty"]
    if any(snapshot.get("source") != "public_tiktok" for snapshot in source_snapshots):
        return [f"{label}: all source snapshots must use source=public_tiktok"]
    subtypes = {str(snapshot.get("sourceSubtype")) for snapshot in source_snapshots}
    if label == "bakeoff" and subtypes != {
        "absolute_hot_video_sample",
        "fresh_hot_video_sample",
    }:
        return [f"{label}: unexpected sourceSubtype set: {sorted(subtypes)}"]
    if label == "consolidated" and subtypes != {"consolidated_hot_video_sample"}:
        return [f"{label}: unexpected sourceSubtype set: {sorted(subtypes)}"]
    if not payload.get("snapshotId", "").startswith("snap.discovery.tiktok-trending."):
        return [f"{label}: unexpected top-level snapshotId: {payload.get('snapshotId')}"]
    return []


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-trending-source-snapshots-") as temp_dir:
            errors: list[str] = []
            for label, fixture_path in FIXTURES.items():
                output_path = Path(temp_dir) / f"{label}.source-snapshots.json"
                run_builder(fixture_path, output_path)
                payload = load_json(output_path)
                errors.extend(validate_payload(label, payload))
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print("Trending sourceSnapshots generation is aligned.")
    print(f"Builder: {BUILDER.relative_to(ROOT)}")
    for label, fixture_path in FIXTURES.items():
        print(f"- {label}: {fixture_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
