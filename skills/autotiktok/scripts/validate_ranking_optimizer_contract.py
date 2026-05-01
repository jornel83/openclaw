#!/usr/bin/env python3
"""
Validate the ranking-output subset that the optimizer layer depends on.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ranking_optimizer_contract_lib import validate_ranking_payload_for_optimizer


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
    args = parser.parse_args()

    try:
        payload = load_json(args.ranking_input)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    errors = validate_ranking_payload_for_optimizer(payload)
    if errors:
        print("[ERROR] ranking output does not satisfy the optimizer-facing contract:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Ranking output satisfies the optimizer-facing contract.")
    print(f"Ranking input: {args.ranking_input}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
