#!/usr/bin/env python3
"""
Validate metadata-only signalItems generation from AutoTikTok trending fixtures.
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

from discovery_lib import validate_signal_items_fixture  # noqa: E402
from trending_discovery_adapter_lib import build_source_snapshots_from_trending  # noqa: E402
from trending_discovery_adapter_lib import build_video_samples_from_trending  # noqa: E402


BUILDER = DISCOVERY_SCRIPT_DIR / "build_trending_signal_items.py"
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
            f"{BUILDER.relative_to(ROOT)} failed\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def snapshot_refs_for(payload: dict[str, Any]) -> set[str]:
    source_snapshots = build_source_snapshots_from_trending(payload)
    return {
        str(snapshot["sourceSnapshotId"])
        for snapshot in source_snapshots["sourceSnapshots"]
    }


def video_sample_ids_for(payload: dict[str, Any]) -> set[str]:
    video_samples = build_video_samples_from_trending(payload)
    return {
        str(sample["videoSampleId"])
        for sample in video_samples["videoSamples"]
    }


def validate_payload(
    label: str,
    payload: dict[str, Any],
    fixture_payload: dict[str, Any],
) -> list[str]:
    errors, _type_counter = validate_signal_items_fixture(
        payload,
        snapshot_refs=snapshot_refs_for(fixture_payload),
    )
    if errors:
        return [f"{label}: {error}" for error in errors]
    signal_items = payload.get("signalItems") or []
    if not signal_items:
        return [f"{label}: signalItems must not be empty"]
    video_sample_ids = video_sample_ids_for(fixture_payload)
    for index, signal in enumerate(signal_items):
        prefix = f"{label}: signalItems[{index}]"
        if signal.get("sourceType") != "public_video_sample":
            return [f"{prefix}: sourceType must be public_video_sample"]
        if signal.get("videoSampleId") not in video_sample_ids:
            return [f"{prefix}: videoSampleId must point to normalized videoSamples"]
        if signal.get("recommendedMode") != "growth":
            return [f"{prefix}: recommendedMode must default to growth"]
        if signal.get("freshnessWindow") != "daily":
            return [f"{prefix}: freshnessWindow must default to daily"]
        if "metadata-derived synthetic signal" not in signal.get("executionNotes", ""):
            return [f"{prefix}: executionNotes must identify metadata-only derivation"]
    if label == "consolidated":
        first_signal = signal_items[0]
        if first_signal.get("topicTitle") != "TikTok trend: #eyefilter #doeeyes #eyemakeup":
            return [f"{label}: hashtag-derived topicTitle is not stable"]
        if first_signal.get("signalConfidence") != 0.87:
            return [f"{label}: hot_score-derived signalConfidence is not stable"]
    return []


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-trending-signal-items-") as temp_dir:
            errors: list[str] = []
            for label, fixture_path in FIXTURES.items():
                output_path = Path(temp_dir) / f"{label}.signal-items.json"
                fixture_payload = load_json(fixture_path)
                run_builder(fixture_path, output_path)
                payload = load_json(output_path)
                errors.extend(validate_payload(label, payload, fixture_payload))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print("Trending metadata-only signalItems generation is aligned.")
    print(f"Builder: {BUILDER.relative_to(ROOT)}")
    for label, fixture_path in FIXTURES.items():
        print(f"- {label}: {fixture_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
