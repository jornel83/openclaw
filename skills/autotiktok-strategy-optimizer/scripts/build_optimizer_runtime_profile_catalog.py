#!/usr/bin/env python3
"""
Build a planner-facing optimizer runtime profile catalog artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_runtime_profile_lib import (
    DEFAULT_RUNTIME_PROFILE_CATALOG_FAMILY,
    DEFAULT_RUNTIME_PROFILE_CATALOG_ID,
    DEFAULT_RUNTIME_PROFILE_CATALOG_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSION,
    RUNTIME_PROFILE_CATALOG_LANES,
    RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
    build_default_optimizer_runtime_profile_entries,
    get_default_runtime_profile_catalog_metadata,
    build_optimizer_runtime_profile_catalog_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    DEFAULT_ROOT / "fixtures" / "optimizer-runtime-profile-catalog.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--catalog-lane",
        default=RUNTIME_PROFILE_CATALOG_LANE_CURRENT,
        choices=RUNTIME_PROFILE_CATALOG_LANES,
    )
    parser.add_argument(
        "--catalog-id",
    )
    parser.add_argument(
        "--catalog-family",
    )
    parser.add_argument(
        "--catalog-version",
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    catalog_defaults = get_default_runtime_profile_catalog_metadata(
        catalog_lane=args.catalog_lane
    )
    catalog_id = args.catalog_id or catalog_defaults["catalogId"]
    catalog_family = args.catalog_family or catalog_defaults["catalogFamily"]
    catalog_version = args.catalog_version or catalog_defaults["catalogVersion"]

    payload = build_optimizer_runtime_profile_catalog_payload(
        profiles=build_default_optimizer_runtime_profile_entries(
            catalog_lane=args.catalog_lane
        ),
        schema_version=args.schema_version,
        catalog_id=catalog_id,
        catalog_family=catalog_family,
        catalog_version=catalog_version,
        generated_at=args.generated_at,
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer runtime profile catalog to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
