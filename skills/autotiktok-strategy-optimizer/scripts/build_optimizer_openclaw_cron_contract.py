#!/usr/bin/env python3
"""
Build the committed AutoTikTok OpenClaw cron contract artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from openclaw_cron_contract_lib import (
    OPENCLAW_CRON_CONTRACT_ID,
    OPENCLAW_CRON_CONTRACT_SCHEMA_VERSION,
    ROOT,
    build_optimizer_openclaw_cron_contract_payload,
)


DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-openclaw-cron-contract.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract-id",
        default=OPENCLAW_CRON_CONTRACT_ID,
    )
    parser.add_argument(
        "--generated-at",
        default="2026-04-21T12:00:00Z",
    )
    parser.add_argument(
        "--schema-version",
        default=OPENCLAW_CRON_CONTRACT_SCHEMA_VERSION,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_optimizer_openclaw_cron_contract_payload(
        generated_at=args.generated_at,
        contract_id=args.contract_id,
        schema_version=args.schema_version,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer OpenClaw cron contract to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
