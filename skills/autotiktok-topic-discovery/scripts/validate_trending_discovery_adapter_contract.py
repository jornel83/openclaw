#!/usr/bin/env python3
"""
Validate AutoTikTok trending outputs before converting them into discovery inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trending_discovery_adapter_lib import build_trending_adapter_contract
from trending_discovery_adapter_lib import load_json
from trending_discovery_adapter_lib import validate_trending_adapter_contract


DEFAULT_INPUTS = (
    Path(__file__).resolve().parents[1] / "fixtures" / "trending-bakeoff.sample.json",
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "trending-consolidated-hot.sample.json",
)


def validate_path(path: Path, *, print_summary: bool) -> list[str]:
    payload = load_json(path)
    errors = validate_trending_adapter_contract(payload)
    if print_summary:
        contract = build_trending_adapter_contract(payload)
        print(json.dumps(contract, ensure_ascii=True, indent=2))
    if errors:
        return [f"{path}: {error}" for error in errors]
    contract = build_trending_adapter_contract(payload)
    print(
        f"Validated {path}: {contract['payloadKind']} with {contract['artifactCount']} video sample artifact(s)."
    )
    for artifact in contract["artifacts"]:
        normalization = (
            "requires normalization"
            if artifact["requiresAdapterNormalization"]
            else "already canonical"
        )
        print(
            "- "
            f"{artifact['artifactPath']}: {artifact['dominantSampleShape']} "
            f"({artifact['sampleCount']} rows, {normalization})"
        )
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append")
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    inputs = tuple(args.input or DEFAULT_INPUTS)
    errors: list[str] = []
    try:
        for path in inputs:
            errors.extend(validate_path(path, print_summary=args.print_summary))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print("Trending discovery adapter contract is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
