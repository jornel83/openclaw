#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job artifact retention policy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_job_orchestration_lib import (
    build_optimizer_job_artifact_retention_policy_payload,
    validate_optimizer_job_artifact_retention_policy_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    DEFAULT_ROOT
    / "fixtures"
    / "optimizer-job-artifact-retention-policy.sample.json"
)


def _build_default_artifact_policies() -> list[dict[str, object]]:
    return [
        {
            "artifactKind": "input_manifest",
            "retentionTier": "ephemeral",
            "keepLatestCount": 3,
            "keepFailureArtifacts": False,
            "partitionDimensions": ["scheduleId", "schedulerRolloutIntent"],
        },
        {
            "artifactKind": "input_bundle",
            "retentionTier": "ephemeral",
            "keepLatestCount": 3,
            "keepFailureArtifacts": False,
            "partitionDimensions": ["scheduleId", "schedulerRolloutIntent"],
        },
        {
            "artifactKind": "job_run",
            "retentionTier": "operational",
            "keepLatestCount": 20,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["scheduleId", "schedulerRolloutIntent"],
        },
        {
            "artifactKind": "shadow_compare",
            "retentionTier": "operational",
            "keepLatestCount": 20,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["scheduleId", "candidateSchedulerRolloutIntent"],
        },
        {
            "artifactKind": "shadow_compare_batch",
            "retentionTier": "operational",
            "keepLatestCount": 10,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["comparisonDimension"],
        },
        {
            "artifactKind": "recent_run_summaries",
            "retentionTier": "operational",
            "keepLatestCount": 30,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["generatedDate"],
        },
        {
            "artifactKind": "recent_compare_summaries",
            "retentionTier": "operational",
            "keepLatestCount": 30,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["generatedDate"],
        },
        {
            "artifactKind": "recent_weekly_decisions",
            "retentionTier": "operational",
            "keepLatestCount": 30,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["generatedDate"],
        },
        {
            "artifactKind": "recent_failure_summaries",
            "retentionTier": "failure_audit",
            "keepLatestCount": 30,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["generatedDate", "ownerHint"],
        },
        {
            "artifactKind": "orchestration_cycle",
            "retentionTier": "audit",
            "keepLatestCount": 30,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["generatedDate"],
        },
        {
            "artifactKind": "job_error",
            "retentionTier": "failure_audit",
            "keepLatestCount": 50,
            "keepFailureArtifacts": True,
            "partitionDimensions": ["errorCode", "scheduleId"],
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy-id",
        default="optimizer-job-artifact-retention-policy.autotiktok.fixture.2026-04-19",
    )
    parser.add_argument("--generated-at", default="2026-04-19T03:18:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_optimizer_job_artifact_retention_policy_payload(
        policy_id=args.policy_id,
        generated_at=args.generated_at,
        artifact_policies=_build_default_artifact_policies(),
    )
    validate_optimizer_job_artifact_retention_policy_payload(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer job artifact retention policy to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
