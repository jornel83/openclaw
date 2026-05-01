#!/usr/bin/env python3
"""
Build a planner-facing optimizer runtime materialization plan artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_runtime_plan_lib import (
    OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSION,
    build_default_optimizer_runtime_materialization_plans,
    build_optimizer_runtime_materialization_plan_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    DEFAULT_ROOT / "fixtures" / "optimizer-runtime-materialization-plan.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--plan-set-id",
        default="optimizer-runtime-materialization-plan.autotiktok.fixture.2026-04-15",
    )
    parser.add_argument("--generated-at", default="2026-04-15T06:00:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_optimizer_runtime_materialization_plan_payload(
        plans=build_default_optimizer_runtime_materialization_plans(),
        schema_version=args.schema_version,
        plan_set_id=args.plan_set_id,
        generated_at=args.generated_at,
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer runtime materialization plan to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
