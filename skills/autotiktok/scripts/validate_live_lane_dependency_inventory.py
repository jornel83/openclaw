#!/usr/bin/env python3
"""
Validate the machine-readable inventory of AutoTikTok live-lane default dependencies.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

from live_lane_dependency_inventory import (
    LIVE_LANE_DEFAULT_DEPENDENCIES,
    LIVE_LANE_DEPENDENCY_INVENTORY_SCHEMA_VERSION,
    PREVIEW_FIRST_WRAPPERS,
    build_live_lane_dependency_inventory,
)


ROOT = Path(__file__).resolve().parents[3]
SHRINK_STATUSES = {
    "must_stay_live_for_committed_fixtures",
    "paired_with_preview_gate",
    "reduced_with_preview_wrapper",
}


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    payload = build_live_lane_dependency_inventory()
    errors: list[str] = []

    expect(
        payload.get("schemaVersion") == LIVE_LANE_DEPENDENCY_INVENTORY_SCHEMA_VERSION,
        "live-lane dependency inventory has unexpected schemaVersion",
        errors,
    )

    preview_wrappers = payload.get("previewFirstWrappers", [])
    live_dependencies = payload.get("liveLaneDefaultDependencies", [])
    expect(isinstance(preview_wrappers, list), "previewFirstWrappers must be a list", errors)
    expect(
        isinstance(live_dependencies, list),
        "liveLaneDefaultDependencies must be a list",
        errors,
    )

    preview_ids: set[str] = set()
    preview_commands: set[str] = set()
    for index, item in enumerate(PREVIEW_FIRST_WRAPPERS):
        prefix = f"previewFirstWrappers[{index}]"
        item_id = item.get("id")
        command = item.get("command")
        wraps = item.get("wraps")
        fallback_flag = item.get("fallbackFlag")
        expect(
            isinstance(item_id, str) and bool(item_id),
            f"{prefix}.id must be a non-empty string",
            errors,
        )
        if isinstance(item_id, str):
            expect(item_id not in preview_ids, f"{prefix}.id must be unique", errors)
            preview_ids.add(item_id)
        expect(
            item.get("defaultLane") == "preview",
            f"{prefix}.defaultLane must be preview",
            errors,
        )
        expect(
            item.get("defaultContractVersion") == "ranking-optimizer-contract.vNext-preview",
            f"{prefix}.defaultContractVersion must be ranking-optimizer-contract.vNext-preview",
            errors,
        )
        expect(
            item.get("defaultValidationMode") == "exact",
            f"{prefix}.defaultValidationMode must be exact",
            errors,
        )
        expect(
            fallback_flag == "--use-current-lane",
            f"{prefix}.fallbackFlag must be --use-current-lane",
            errors,
        )
        expect(
            isinstance(command, str) and bool(command),
            f"{prefix}.command must be a non-empty string",
            errors,
        )
        expect(
            isinstance(wraps, str) and bool(wraps),
            f"{prefix}.wraps must be a non-empty string",
            errors,
        )
        if isinstance(command, str):
            preview_commands.add(command)
            expect((ROOT / command).exists(), f"{prefix}.command does not exist", errors)
        if isinstance(wraps, str):
            expect((ROOT / wraps).exists(), f"{prefix}.wraps does not exist", errors)

    live_ids: set[str] = set()
    shrink_counter: Counter[str] = Counter()
    for index, item in enumerate(LIVE_LANE_DEFAULT_DEPENDENCIES):
        prefix = f"liveLaneDefaultDependencies[{index}]"
        item_id = item.get("id")
        command = item.get("command")
        shrink_status = item.get("shrinkStatus")
        preview_alternative = item.get("previewAlternative")
        retained_because = item.get("retainedBecause")
        expect(
            isinstance(item_id, str) and bool(item_id),
            f"{prefix}.id must be a non-empty string",
            errors,
        )
        if isinstance(item_id, str):
            expect(item_id not in live_ids, f"{prefix}.id must be unique", errors)
            live_ids.add(item_id)
        expect(
            item.get("defaultLane") == "current",
            f"{prefix}.defaultLane must be current",
            errors,
        )
        expect(
            isinstance(command, str) and bool(command),
            f"{prefix}.command must be a non-empty string",
            errors,
        )
        if isinstance(command, str):
            expect((ROOT / command).exists(), f"{prefix}.command does not exist", errors)
        expect(
            isinstance(retained_because, str) and bool(retained_because),
            f"{prefix}.retainedBecause must be a non-empty string",
            errors,
        )
        expect(
            shrink_status in SHRINK_STATUSES,
            f"{prefix}.shrinkStatus is not supported",
            errors,
        )
        if isinstance(shrink_status, str):
            shrink_counter[shrink_status] += 1

        if shrink_status == "reduced_with_preview_wrapper":
            expect(
                isinstance(preview_alternative, str) and bool(preview_alternative),
                f"{prefix}.previewAlternative must be set for reduced_with_preview_wrapper",
                errors,
            )
            if isinstance(preview_alternative, str):
                expect(
                    preview_alternative in preview_commands,
                    f"{prefix}.previewAlternative must point to a known preview-first wrapper",
                    errors,
                )
        if shrink_status == "must_stay_live_for_committed_fixtures":
            expect(
                isinstance(retained_because, str)
                and ("committed" in retained_because.lower() or "fixture" in retained_because.lower()),
                f"{prefix}.retainedBecause should explicitly mention committed fixtures",
                errors,
            )
        if shrink_status == "paired_with_preview_gate" and isinstance(preview_alternative, str):
            expect(
                (ROOT / preview_alternative).exists(),
                f"{prefix}.previewAlternative does not exist",
                errors,
            )

    expect(
        len(preview_wrappers) == len(PREVIEW_FIRST_WRAPPERS),
        "previewFirstWrappers payload length does not match the inventory source",
        errors,
    )
    expect(
        len(live_dependencies) == len(LIVE_LANE_DEFAULT_DEPENDENCIES),
        "liveLaneDefaultDependencies payload length does not match the inventory source",
        errors,
    )
    expect(
        shrink_counter["reduced_with_preview_wrapper"] >= 3,
        "expected at least three reduced_with_preview_wrapper entries",
        errors,
    )
    expect(
        shrink_counter["must_stay_live_for_committed_fixtures"] >= 3,
        "expected fixture-bound live-lane dependencies to remain explicit",
        errors,
    )
    expect(
        shrink_counter["paired_with_preview_gate"] >= 1,
        "expected at least one paired preview gate entry",
        errors,
    )

    if errors:
        print("[ERROR] live-lane dependency inventory is inconsistent:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Live-lane dependency inventory is consistent.")
    print(f"- preview-first wrappers: {len(PREVIEW_FIRST_WRAPPERS)}")
    print(f"- live-lane defaults: {len(LIVE_LANE_DEFAULT_DEPENDENCIES)}")
    for status in sorted(SHRINK_STATUSES):
        print(f"- {status}: {shrink_counter[status]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
