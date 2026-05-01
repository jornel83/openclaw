#!/usr/bin/env python3
"""
Build a planner-facing optimizer runtime profile rollout policy artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_runtime_profile_lib import (
    DEFAULT_RUNTIME_PROFILE_FAMILY_ID,
    validate_optimizer_runtime_profile_family_registry_payload,
)
from optimizer_runtime_profile_rollout_lib import (
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS,
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_FAMILY,
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_ID,
    DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSION,
    build_default_optimizer_runtime_profile_rollout_family_policies,
    build_default_runtime_profile_family_registry_rollout_reference,
    build_optimizer_runtime_profile_rollout_policy_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    DEFAULT_ROOT
    / "fixtures"
    / "optimizer-runtime-profile-rollout-policy.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_RUNTIME_PROFILE_ROLLOUT_POLICY_SCHEMA_VERSION,
        ),
    )
    parser.add_argument("--policy-id", default=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_ID)
    parser.add_argument(
        "--policy-family", default=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_FAMILY
    )
    parser.add_argument(
        "--policy-version", default=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY_VERSION
    )
    parser.add_argument("--input-runtime-profile-family-registry", type=Path)
    parser.add_argument("--family-id", default=DEFAULT_RUNTIME_PROFILE_FAMILY_ID)
    parser.add_argument(
        "--default-rollout-class",
        default=DEFAULT_RUNTIME_PROFILE_ROLLOUT_CLASS,
    )
    parser.add_argument(
        "--active-lane",
        choices=("current", "preview"),
        default="current",
    )
    parser.add_argument(
        "--default-lane",
        choices=("current", "preview"),
        default=None,
    )
    parser.add_argument(
        "--preview-enabled",
        choices=("true", "false"),
        default="true",
    )
    parser.add_argument(
        "--generated-at",
        default="2026-04-15T06:00:00Z",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.input_runtime_profile_family_registry is not None:
        family_registry_payload = json.loads(
            args.input_runtime_profile_family_registry.read_text(encoding="utf-8")
        )
        validate_optimizer_runtime_profile_family_registry_payload(
            family_registry_payload
        )
        family_registry_reference = {
            "registryId": family_registry_payload["registryId"],
            "schemaVersion": family_registry_payload["schemaVersion"],
        }
    else:
        family_registry_reference = (
            build_default_runtime_profile_family_registry_rollout_reference()
        )

    payload = build_optimizer_runtime_profile_rollout_policy_payload(
        policy_id=args.policy_id,
        schema_version=args.schema_version,
        policy_family=args.policy_family,
        policy_version=args.policy_version,
        generated_at=args.generated_at,
        runtime_profile_family_registry_reference=family_registry_reference,
        family_policies=build_default_optimizer_runtime_profile_rollout_family_policies(
            family_id=args.family_id,
            active_lane=args.active_lane,
            default_lane=args.default_lane,
            default_rollout_class=args.default_rollout_class,
            preview_enabled=args.preview_enabled == "true",
        ),
    )
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer runtime profile rollout policy to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
