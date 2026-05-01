#!/usr/bin/env python3
"""
Build a planner-facing optimizer runtime profile family registry artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_runtime_profile_lib import (
    DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID,
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION,
    build_default_runtime_profile_family_entries,
    build_optimizer_runtime_profile_family_registry_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    DEFAULT_ROOT
    / "fixtures"
    / "optimizer-runtime-profile-family-registry.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_RUNTIME_PROFILE_FAMILY_REGISTRY_SCHEMA_VERSION,
        ),
    )
    parser.add_argument("--registry-id", default=DEFAULT_RUNTIME_PROFILE_FAMILY_REGISTRY_ID)
    parser.add_argument(
        "--catalog-schema-version",
        default=OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_RUNTIME_PROFILE_CATALOG_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_RUNTIME_PROFILE_CATALOG_SCHEMA_VERSION,
        ),
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_optimizer_runtime_profile_family_registry_payload(
        registry_id=args.registry_id,
        schema_version=args.schema_version,
        generated_at=args.generated_at,
        families=build_default_runtime_profile_family_entries(
            catalog_schema_version=args.catalog_schema_version
        ),
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer runtime profile family registry to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
