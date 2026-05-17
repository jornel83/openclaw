#!/usr/bin/env python3
"""
Validate enriched signalItems against deterministic videoContentAnalysis input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from build_enriched_signal_items import DEFAULT_SIGNAL_ITEMS
from build_enriched_signal_items import DEFAULT_VIDEO_CONTENT_ANALYSIS
from discovery_lib import validate_signal_items_fixture
from video_signal_enrichment_lib import SAMPLE_SCHEMA_VERSION
from video_signal_enrichment_lib import build_enriched_signal_items
from video_signal_enrichment_lib import load_json_object


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EXPECTED = SKILL_DIR / "fixtures" / "signal-items.enriched.sample.json"


def _validate_payload(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return ["summary must be an object"]
    expected_summary = {
        "requested": 4,
        "enriched": 1,
        "metadataOnlyFallback": 3,
        "metadataOnlyUnmatched": 0,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            errors.append(f"summary.{key} must be {expected}")

    signal_items = payload.get("signalItems")
    if not isinstance(signal_items, list) or len(signal_items) != 4:
        return [*errors, "signalItems must contain 4 entries"]
    first_item = signal_items[0]
    if not isinstance(first_item, dict):
        return [*errors, "signalItems[0] must be an object"]
    raw_meta = first_item.get("rawMeta")
    if not isinstance(raw_meta, dict):
        errors.append("signalItems[0].rawMeta must exist")
    elif raw_meta.get("enrichmentLane") != "video_content_analysis":
        errors.append("signalItems[0] must use video_content_analysis lane")
    if "MP4 analysis adds" not in str(first_item.get("topicSummary")):
        errors.append("signalItems[0].topicSummary must include video analysis summary")
    if "videoContentAnalysis" not in str(first_item.get("executionNotes")):
        errors.append("signalItems[0].executionNotes must mention videoContentAnalysis")

    for index in range(1, len(signal_items)):
        item = signal_items[index]
        if not isinstance(item, dict):
            errors.append(f"signalItems[{index}] must be an object")
            continue
        raw_meta = item.get("rawMeta")
        if not isinstance(raw_meta, dict):
            errors.append(f"signalItems[{index}].rawMeta must exist")
            continue
        if raw_meta.get("enrichmentLane") != "metadata_only_fallback":
            errors.append(f"signalItems[{index}] must preserve metadata-only fallback")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signal-items", type=Path, default=DEFAULT_SIGNAL_ITEMS)
    parser.add_argument("--video-content-analysis", type=Path, default=DEFAULT_VIDEO_CONTENT_ANALYSIS)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    args = parser.parse_args()

    try:
        signal_items_payload = load_json_object(args.signal_items)
        actual = build_enriched_signal_items(
            signal_items_payload,
            load_json_object(args.video_content_analysis),
            schema_version=SAMPLE_SCHEMA_VERSION,
        )
        expected = load_json_object(args.expected)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if actual != expected:
        print("[ERROR] enriched signalItems fixture is stale")
        print("ACTUAL:")
        print(json.dumps(actual, ensure_ascii=True, indent=2))
        return 1

    errors = _validate_payload(expected)
    signal_item_errors, _ = validate_signal_items_fixture(expected)
    errors.extend(signal_item_errors)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    print("Validated enriched signalItems fixture.")
    print("- enriched: 1")
    print("- metadata_only_fallback: 3")
    print("- video_content_analysis_reference: present")
    print("Enriched signalItems are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
