#!/usr/bin/env python3
"""
Rehearse a future ranking-to-optimizer contract upgrade without changing the live default contract.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
    prepare_ranking_payload_for_optimizer,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RANKING_PATH = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING_PATH)
    parser.add_argument(
        "--validation-mode",
        default=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        choices=(
            RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            RANKING_OPTIMIZER_CONTRACT_COMPAT_VALIDATION_MODE,
        ),
    )
    args = parser.parse_args()

    try:
        payload = load_json(args.ranking_input)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    try:
        prepare_ranking_payload_for_optimizer(
            payload,
            contract_version=RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
            validation_mode=args.validation_mode,
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    print("Ranking output satisfies the vNext preview optimizer-facing contract.")
    print(f"Validation mode: {args.validation_mode}")
    print(f"Ranking input: {args.ranking_input}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
