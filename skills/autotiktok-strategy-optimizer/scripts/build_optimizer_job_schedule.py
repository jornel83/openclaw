#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job schedule plan fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_bundle_lib import load_optimizer_input_manifest, load_optimizer_input_source_registry
from optimizer_input_rollout_lib import load_optimizer_input_rollout_policy
from optimizer_input_rollout_lib import (
    DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_FAMILY,
    DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_ID,
    DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_VERSION,
    OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
    build_default_optimizer_input_rollout_classes,
    build_default_optimizer_input_rollout_intents,
    build_default_optimizer_input_rollout_schedule_policies,
    build_optimizer_input_rollout_policy_payload,
)
from optimizer_job_schedule_lib import build_optimizer_job_schedule_payload
from optimizer_job_schedule_lib import (
    build_default_optimizer_job_schedule_rollout_intents,
)
from optimizer_runtime_profile_rollout_lib import (
    validate_optimizer_runtime_profile_rollout_policy_payload,
)
from optimizer_lib import DEFAULT_POLICY
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.sample.json"
)
DEFAULT_WEEKLY_REVIEW_WINDOW = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-weekly-review-window.sample.json"
)
DEFAULT_INPUT_SOURCE_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-source-registry.sample.json"
)
DEFAULT_INPUT_ROLLOUT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-rollout-policy.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-schedule.sample.json"
)
DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-runtime-profile-rollout-policy.sample.json"
)
DEFAULT_EXTERNAL_OUTPUT_ROOT = "artifacts/optimizer-job-runs"


def _render_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_INPUT_MANIFEST)
    parser.add_argument(
        "--weekly-review-window-input",
        type=Path,
        default=DEFAULT_WEEKLY_REVIEW_WINDOW,
    )
    parser.add_argument(
        "--input-source-registry",
        type=Path,
        default=DEFAULT_INPUT_SOURCE_REGISTRY,
    )
    parser.add_argument(
        "--input-rollout-policy",
        type=Path,
        default=DEFAULT_INPUT_ROLLOUT_POLICY,
    )
    parser.add_argument(
        "--runtime-profile-rollout-policy",
        type=Path,
        default=DEFAULT_RUNTIME_PROFILE_ROLLOUT_POLICY,
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--schedule-profile",
        choices=("fixture_replay", "external_scheduler"),
        default="fixture_replay",
    )
    parser.add_argument(
        "--default-output-root",
        default=DEFAULT_EXTERNAL_OUTPUT_ROOT,
    )
    parser.add_argument(
        "--schedule-plan-id",
        default="optimizer-job-schedule.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T04:20:00Z")
    parser.add_argument(
        "--ranking-contract-version",
        default=RANKING_OPTIMIZER_CONTRACT_VERSION,
    )
    parser.add_argument(
        "--ranking-contract-validation-mode",
        default=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        manifest_payload, _ = load_optimizer_input_manifest(args.input_manifest)
        runtime_profile_rollout_policy_payload = json.loads(
            args.runtime_profile_rollout_policy.read_text(encoding="utf-8")
        )
        validate_optimizer_runtime_profile_rollout_policy_payload(
            runtime_profile_rollout_policy_payload
        )
        if args.input_rollout_policy.exists():
            input_rollout_policy_payload = load_optimizer_input_rollout_policy(
                args.input_rollout_policy
            )
        else:
            source_registry_payload, _ = load_optimizer_input_source_registry(
                args.input_source_registry
            )
            input_rollout_policy_payload = build_optimizer_input_rollout_policy_payload(
                policy_id=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_ID,
                schema_version=OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
                policy_family=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_FAMILY,
                policy_version=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_VERSION,
                generated_at=args.generated_at,
                input_source_registry_reference={
                    "schemaVersion": source_registry_payload.get("schemaVersion"),
                    "registryId": source_registry_payload.get("registryId"),
                    "path": _render_repo_relative(args.input_source_registry),
                },
                rollout_classes=build_default_optimizer_input_rollout_classes(),
                rollout_intents=build_default_optimizer_input_rollout_intents(),
                schedule_policies=build_default_optimizer_input_rollout_schedule_policies(),
            )
        payload = build_optimizer_job_schedule_payload(
            schedule_plan_id=args.schedule_plan_id,
            generated_at=args.generated_at,
            schedule_profile=args.schedule_profile,
            input_manifest_path=None
            if args.schedule_profile == "external_scheduler"
            else _render_repo_relative(args.input_manifest),
            weekly_review_window_path=None
            if args.schedule_profile == "external_scheduler"
            else _render_repo_relative(args.weekly_review_window_input),
            input_source_registry_path=None
            if args.schedule_profile == "external_scheduler"
            else _render_repo_relative(args.input_source_registry),
            input_manifest_payload=manifest_payload,
            input_rollout_policy_payload=input_rollout_policy_payload,
            runtime_profile_rollout_policy_payload=runtime_profile_rollout_policy_payload,
            rollout_intent_catalog=build_default_optimizer_job_schedule_rollout_intents(
                runtime_profile_rollout_policy_payload=runtime_profile_rollout_policy_payload
            ),
            input_rollout_policy_path=None
            if args.schedule_profile == "external_scheduler"
            else _render_repo_relative(args.input_rollout_policy),
            runtime_profile_rollout_policy_path=_render_repo_relative(
                args.runtime_profile_rollout_policy
            ),
            policy_path=None
            if args.schedule_profile == "external_scheduler"
            else _render_repo_relative(args.policy),
            ranking_contract_version=args.ranking_contract_version,
            ranking_contract_validation_mode=args.ranking_contract_validation_mode,
            default_output_root=args.default_output_root
            if args.schedule_profile == "external_scheduler"
            else None,
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job schedule plan to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
