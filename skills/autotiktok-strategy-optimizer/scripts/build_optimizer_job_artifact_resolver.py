#!/usr/bin/env python3
"""
Build an optimizer job artifact resolver for provider-backed real-lane inputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_JOB_ARTIFACT_RESOLVER_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_PROVIDER_CATALOG_SAMPLE_SCHEMA_VERSION,
    build_optimizer_job_artifact_resolver_payload,
    build_optimizer_source_provider_catalog_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING = (
    DEFAULT_ROOT.parent / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
DEFAULT_CONTEXT = DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
DEFAULT_BACKFILLS_RAW = (
    DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-raw-run.sample.json"
)
DEFAULT_PERFORMANCE_RAW = (
    DEFAULT_ROOT / "fixtures" / "post-performance-signal-raw-run.sample.json"
)
DEFAULT_CHALLENGER_RAW = (
    DEFAULT_ROOT / "fixtures" / "challenger-evaluation-raw-run.sample.json"
)
DEFAULT_INPUT_SOURCE_PROVIDER_CATALOG = (
    DEFAULT_ROOT / "fixtures" / "optimizer-source-provider-catalog.sample.json"
)
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-job-artifact-resolver.sample.json"


def _path_label(path: Path, *, style: str, repo_root: Path) -> str:
    if style == "absolute":
        return str(path)
    if style == "basename":
        return path.name
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def _build_default_provider_catalog_payload(
    *, args: argparse.Namespace, repo_root: Path
) -> dict[str, object]:
    return build_optimizer_source_provider_catalog_payload(
        schema_version=OPTIMIZER_SOURCE_PROVIDER_CATALOG_SAMPLE_SCHEMA_VERSION,
        catalog_id="optimizer-source-provider-catalog.autotiktok.fixture.2026-04-18",
        generated_at="2026-04-18T03:06:00Z",
        providers=[
            {
                "sourceProviderId": "ranking_real_shadow_provider",
                "artifactKey": "ranking",
                "providerLane": "real_provider_shadow",
                "providerKind": "materialized_fixture",
                "upstreamJobKind": "ranking_output_materialization",
                "providerClass": "artifact_catalog_service",
                "providerHandle": "autotiktok.optimizer.real_provider.ranking",
                "locatorKind": "artifact_uri",
                "providerEndpoint": "autotiktok://optimizer-source-provider/ranking",
                "path": _path_label(
                    args.ranking_input, style=args.path_style, repo_root=repo_root
                ),
            },
            {
                "sourceProviderId": "context_real_shadow_provider",
                "artifactKey": "context",
                "providerLane": "real_provider_shadow",
                "providerKind": "materialized_fixture",
                "upstreamJobKind": "scoring_context_materialization",
                "providerClass": "artifact_catalog_service",
                "providerHandle": "autotiktok.optimizer.real_provider.context",
                "locatorKind": "artifact_uri",
                "providerEndpoint": "autotiktok://optimizer-source-provider/context",
                "path": _path_label(
                    args.context_input, style=args.path_style, repo_root=repo_root
                ),
            },
            {
                "sourceProviderId": "backfills_real_shadow_provider",
                "artifactKey": "backfills",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "topic_outcome_backfill",
                "providerClass": "artifact_catalog_service",
                "providerHandle": "autotiktok.optimizer.real_provider.backfills",
                "locatorKind": "artifact_uri",
                "providerEndpoint": "autotiktok://optimizer-source-provider/backfills",
                "path": _path_label(
                    args.backfills_raw_input,
                    style=args.path_style,
                    repo_root=repo_root,
                ),
            },
            {
                "sourceProviderId": "performance_real_shadow_provider",
                "artifactKey": "performance",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "post_performance_signal",
                "providerClass": "artifact_catalog_service",
                "providerHandle": "autotiktok.optimizer.real_provider.performance",
                "locatorKind": "artifact_uri",
                "providerEndpoint": "autotiktok://optimizer-source-provider/performance",
                "path": _path_label(
                    args.performance_raw_input,
                    style=args.path_style,
                    repo_root=repo_root,
                ),
            },
            {
                "sourceProviderId": "challenger_real_shadow_provider",
                "artifactKey": "challengerInput",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "challenger_evaluation",
                "providerClass": "artifact_catalog_service",
                "providerHandle": "autotiktok.optimizer.real_provider.challengerInput",
                "locatorKind": "artifact_uri",
                "providerEndpoint": "autotiktok://optimizer-source-provider/challengerInput",
                "path": _path_label(
                    args.challenger_raw_input,
                    style=args.path_style,
                    repo_root=repo_root,
                ),
            },
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING)
    parser.add_argument("--context-input", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--backfills-raw-input", type=Path, default=DEFAULT_BACKFILLS_RAW)
    parser.add_argument("--performance-raw-input", type=Path, default=DEFAULT_PERFORMANCE_RAW)
    parser.add_argument("--challenger-raw-input", type=Path, default=DEFAULT_CHALLENGER_RAW)
    parser.add_argument(
        "--input-source-provider-catalog",
        type=Path,
        default=DEFAULT_INPUT_SOURCE_PROVIDER_CATALOG,
    )
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_JOB_ARTIFACT_RESOLVER_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_JOB_ARTIFACT_RESOLVER_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_JOB_ARTIFACT_RESOLVER_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--resolver-id",
        default="optimizer-job-artifact-resolver.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T03:08:00Z")
    parser.add_argument(
        "--path-style",
        choices=("repo", "absolute", "basename"),
        default="repo",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = DEFAULT_ROOT.parents[1]
    try:
        provider_catalog_path_label = (
            args.input_source_provider_catalog.relative_to(repo_root).as_posix()
        )
    except ValueError:
        provider_catalog_path_label = str(args.input_source_provider_catalog)
    if args.input_source_provider_catalog.exists():
        provider_catalog_payload = json.loads(
            args.input_source_provider_catalog.read_text(encoding="utf-8")
        )
    else:
        provider_catalog_payload = _build_default_provider_catalog_payload(
            args=args, repo_root=repo_root
        )
    entries = [
        {
            "resolverEntryId": "ranking_real_shadow",
            "artifactKey": "ranking",
            "resolverLane": "real_provider_shadow",
            "resolverStrategy": "provider_catalog_locator",
            "providerRequestKey": "ranking.latest",
            "sourceProviderId": "ranking_real_shadow_provider",
        },
        {
            "resolverEntryId": "context_real_shadow",
            "artifactKey": "context",
            "resolverLane": "real_provider_shadow",
            "resolverStrategy": "provider_catalog_locator",
            "providerRequestKey": "context.latest",
            "sourceProviderId": "context_real_shadow_provider",
        },
        {
            "resolverEntryId": "backfills_real_shadow",
            "artifactKey": "backfills",
            "resolverLane": "real_provider_shadow",
            "resolverStrategy": "provider_catalog_locator",
            "providerRequestKey": "backfills.latest",
            "sourceProviderId": "backfills_real_shadow_provider",
        },
        {
            "resolverEntryId": "performance_real_shadow",
            "artifactKey": "performance",
            "resolverLane": "real_provider_shadow",
            "resolverStrategy": "provider_catalog_locator",
            "providerRequestKey": "performance.latest",
            "sourceProviderId": "performance_real_shadow_provider",
        },
        {
            "resolverEntryId": "challenger_real_shadow",
            "artifactKey": "challengerInput",
            "resolverLane": "real_provider_shadow",
            "resolverStrategy": "provider_catalog_locator",
            "providerRequestKey": "challengerInput.latest",
            "sourceProviderId": "challenger_real_shadow_provider",
        },
    ]
    payload = build_optimizer_job_artifact_resolver_payload(
        schema_version=args.schema_version,
        resolver_id=args.resolver_id,
        generated_at=args.generated_at,
        entries=entries,
        input_source_provider_catalog_reference={
            "schemaVersion": provider_catalog_payload.get("schemaVersion"),
            "catalogId": provider_catalog_payload.get("catalogId"),
            "path": provider_catalog_path_label,
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer job artifact resolver to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
