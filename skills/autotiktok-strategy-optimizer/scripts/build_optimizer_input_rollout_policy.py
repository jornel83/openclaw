#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer input rollout policy fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_bundle_lib import load_optimizer_input_source_registry
from optimizer_input_rollout_lib import (
    DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_FAMILY,
    DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_ID,
    DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_VERSION,
    OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSION,
    build_default_optimizer_input_rollout_classes,
    build_default_optimizer_input_rollout_intents,
    build_default_optimizer_input_rollout_schedule_policies,
    build_optimizer_input_rollout_policy_payload,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_SOURCE_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-source-registry.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-rollout-policy.sample.json"
)


def _render_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-source-registry", type=Path, default=DEFAULT_INPUT_SOURCE_REGISTRY
    )
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--policy-id",
        default=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_ID,
    )
    parser.add_argument(
        "--policy-family",
        default=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_FAMILY,
    )
    parser.add_argument(
        "--policy-version",
        default=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_VERSION,
    )
    parser.add_argument("--generated-at", default="2026-04-18T03:15:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        registry_payload, _ = load_optimizer_input_source_registry(
            args.input_source_registry
        )
        payload = build_optimizer_input_rollout_policy_payload(
            policy_id=args.policy_id,
            schema_version=args.schema_version,
            policy_family=args.policy_family,
            policy_version=args.policy_version,
            generated_at=args.generated_at,
            input_source_registry_reference={
                "schemaVersion": registry_payload.get("schemaVersion"),
                "registryId": registry_payload.get("registryId"),
                "path": _render_repo_relative(args.input_source_registry),
            },
            rollout_classes=build_default_optimizer_input_rollout_classes(),
            rollout_intents=build_default_optimizer_input_rollout_intents(),
            schedule_policies=build_default_optimizer_input_rollout_schedule_policies(),
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer input rollout policy to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
