#!/usr/bin/env python3
"""
Validate videoSamples normalization from focused AutoTikTok trending fixtures.
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

from discovery_lib import validate_video_samples_fixture  # noqa: E402
from trending_discovery_adapter_lib import build_source_snapshots_from_trending  # noqa: E402
from trending_discovery_adapter_lib import build_video_samples_from_trending  # noqa: E402


BUILDER = DISCOVERY_SCRIPT_DIR / "build_trending_video_samples.py"
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


def validate_payload(
    label: str,
    payload: dict[str, Any],
    fixture_payload: dict[str, Any],
) -> list[str]:
    errors = validate_video_samples_fixture(
        payload,
        snapshot_refs=snapshot_refs_for(fixture_payload),
    )
    if errors:
        return [f"{label}: {error}" for error in errors]
    video_samples = payload.get("videoSamples") or []
    if not video_samples:
        return [f"{label}: videoSamples must not be empty"]
    if not payload.get("snapshotId", "").startswith("snap.discovery.tiktok-trending."):
        return [f"{label}: unexpected top-level snapshotId: {payload.get('snapshotId')}"]

    for index, sample in enumerate(video_samples):
        prefix = f"{label}: videoSamples[{index}]"
        if "video_id" in sample or "create_time" in sample or "view_count" in sample:
            return [f"{prefix}: raw snake_case collector fields leaked to canonical top level"]
        if not str(sample["videoSampleId"]).startswith("tt:"):
            return [f"{prefix}: videoSampleId must use tt:<video_id>"]

    if label == "consolidated":
        sample = video_samples[0]
        if sample.get("platformVideoId") != "7625618372616555808":
            return [f"{label}: platformVideoId mapping failed"]
        if sample.get("authorHandle") != "paulinettee.s":
            return [f"{label}: author handle mapping failed"]
        if sample.get("metrics", {}).get("views") != 182000:
            return [f"{label}: view_count -> metrics.views mapping failed"]
        if (
            sample.get("shareUrl")
            != "https://www.tiktok.com/@paulinettee.s/video/7625618372616555808"
        ):
            return [f"{label}: share_url/url -> shareUrl mapping failed"]
        raw_meta = sample.get("rawMeta") or {}
        for field in ("hot_score", "ranking_mode", "ranking_rank", "route_rank"):
            if field not in raw_meta:
                return [f"{label}: {field} was not preserved in rawMeta"]

    return []


def validate_hashtag_fallback() -> list[str]:
    payload = load_json(FIXTURES["consolidated"])
    first_row = payload["absolute_hot_video_samples"]["videoSamples"][0]
    first_row.pop("hashtags", None)
    normalized = build_video_samples_from_trending(payload)
    first_sample = normalized["videoSamples"][0]
    if first_sample.get("hashtags") != ["eyefilter", "doeeyes", "eyemakeup"]:
        return ["consolidated: description hashtag fallback failed"]
    return []


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="autotiktok-trending-video-samples-") as temp_dir:
            errors: list[str] = []
            for label, fixture_path in FIXTURES.items():
                output_path = Path(temp_dir) / f"{label}.video-samples.json"
                fixture_payload = load_json(fixture_path)
                run_builder(fixture_path, output_path)
                payload = load_json(output_path)
                errors.extend(validate_payload(label, payload, fixture_payload))
            errors.extend(validate_hashtag_fallback())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print("Trending videoSamples normalization is aligned.")
    print(f"Builder: {BUILDER.relative_to(ROOT)}")
    for label, fixture_path in FIXTURES.items():
        print(f"- {label}: {fixture_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
