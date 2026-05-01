#!/usr/bin/env python3
"""
Build a runtime artifact registry for planner-oriented optimizer source descriptors.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_eval_window_set_lib import (
    OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSION,
    build_default_optimizer_runtime_artifact_registry_bindings,
    build_optimizer_runtime_artifact_registry_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    DEFAULT_ROOT / "fixtures" / "optimizer-runtime-artifact-registry.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_RUNTIME_ARTIFACT_REGISTRY_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--registry-id",
        default="optimizer-runtime-artifact-registry.autotiktok.fixture.2026-04-15",
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument(
        "--input-manifest-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-manifest.sample.json",
    )
    parser.add_argument(
        "--input-bundle-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-input-bundle.sample.json",
    )
    parser.add_argument(
        "--input-offline-cycle-daily-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle-daily.sample.json",
    )
    parser.add_argument(
        "--input-offline-cycle-weekly-path",
        default="skills/autotiktok-strategy-optimizer/fixtures/optimizer-offline-cycle.sample.json",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_optimizer_runtime_artifact_registry_payload(
        bindings=build_default_optimizer_runtime_artifact_registry_bindings(
            input_manifest_path=args.input_manifest_path,
            input_bundle_path=args.input_bundle_path,
            input_offline_cycle_daily_path=args.input_offline_cycle_daily_path,
            input_offline_cycle_weekly_path=args.input_offline_cycle_weekly_path,
        ),
        schema_version=args.schema_version,
        registry_id=args.registry_id,
        generated_at=args.generated_at,
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer runtime artifact registry to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
