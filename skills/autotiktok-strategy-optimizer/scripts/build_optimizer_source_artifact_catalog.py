#!/usr/bin/env python3
"""
Build an optimizer source artifact catalog for provider-backed real-shadow inputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSION,
    build_optimizer_source_artifact_catalog_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING = (
    DEFAULT_ROOT.parent
    / "autotiktok-topic-ranking"
    / "fixtures"
    / "ranking-dry-run.sample.json"
)
DEFAULT_CONTEXT = (
    DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
)
DEFAULT_BACKFILLS_RAW = (
    DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-raw-run.sample.json"
)
DEFAULT_PERFORMANCE_RAW = (
    DEFAULT_ROOT / "fixtures" / "post-performance-signal-raw-run.sample.json"
)
DEFAULT_CHALLENGER_RAW = (
    DEFAULT_ROOT / "fixtures" / "challenger-evaluation-raw-run.sample.json"
)
DEFAULT_OUTPUT = (
    DEFAULT_ROOT / "fixtures" / "optimizer-source-artifact-catalog.sample.json"
)


def _path_label(path: Path, *, style: str, repo_root: Path) -> str:
    if style == "absolute":
        return str(path)
    if style == "basename":
        return path.name
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking-input", type=Path, default=DEFAULT_RANKING)
    parser.add_argument("--context-input", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--backfills-raw-input", type=Path, default=DEFAULT_BACKFILLS_RAW)
    parser.add_argument("--performance-raw-input", type=Path, default=DEFAULT_PERFORMANCE_RAW)
    parser.add_argument("--challenger-raw-input", type=Path, default=DEFAULT_CHALLENGER_RAW)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--catalog-id",
        default="optimizer-source-artifact-catalog.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T03:03:00Z")
    parser.add_argument(
        "--path-style",
        choices=("repo", "absolute", "basename"),
        default="repo",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = DEFAULT_ROOT.parents[1]
    entries = [
        {
            "artifactCatalogEntryId": "ranking_real_shadow_artifact",
            "artifactKey": "ranking",
            "providerLane": "real_provider_shadow",
            "providerKind": "materialized_fixture",
            "upstreamJobKind": "ranking_output_materialization",
            "artifactLocatorKind": "provider_locator",
            "artifactLocatorUri": "catalog://autotiktok-real-provider/ranking",
            "providerSourceClass": "artifact_catalog_service",
            "path": _path_label(
                args.ranking_input, style=args.path_style, repo_root=repo_root
            ),
        },
        {
            "artifactCatalogEntryId": "context_real_shadow_artifact",
            "artifactKey": "context",
            "providerLane": "real_provider_shadow",
            "providerKind": "materialized_fixture",
            "upstreamJobKind": "scoring_context_materialization",
            "artifactLocatorKind": "provider_locator",
            "artifactLocatorUri": "catalog://autotiktok-real-provider/context",
            "providerSourceClass": "artifact_catalog_service",
            "path": _path_label(
                args.context_input, style=args.path_style, repo_root=repo_root
            ),
        },
        {
            "artifactCatalogEntryId": "backfills_real_shadow_artifact",
            "artifactKey": "backfills",
            "providerLane": "real_provider_shadow",
            "providerKind": "raw_job_envelope",
            "upstreamJobKind": "topic_outcome_backfill",
            "artifactLocatorKind": "provider_locator",
            "artifactLocatorUri": "catalog://autotiktok-real-provider/backfills",
            "providerSourceClass": "artifact_catalog_service",
            "path": _path_label(
                args.backfills_raw_input, style=args.path_style, repo_root=repo_root
            ),
        },
        {
            "artifactCatalogEntryId": "performance_real_shadow_artifact",
            "artifactKey": "performance",
            "providerLane": "real_provider_shadow",
            "providerKind": "raw_job_envelope",
            "upstreamJobKind": "post_performance_signal",
            "artifactLocatorKind": "provider_locator",
            "artifactLocatorUri": "catalog://autotiktok-real-provider/performance",
            "providerSourceClass": "artifact_catalog_service",
            "path": _path_label(
                args.performance_raw_input, style=args.path_style, repo_root=repo_root
            ),
        },
        {
            "artifactCatalogEntryId": "challenger_real_shadow_artifact",
            "artifactKey": "challengerInput",
            "providerLane": "real_provider_shadow",
            "providerKind": "raw_job_envelope",
            "upstreamJobKind": "challenger_evaluation",
            "artifactLocatorKind": "provider_locator",
            "artifactLocatorUri": "catalog://autotiktok-real-provider/challengerInput",
            "providerSourceClass": "artifact_catalog_service",
            "path": _path_label(
                args.challenger_raw_input, style=args.path_style, repo_root=repo_root
            ),
        },
    ]
    payload = build_optimizer_source_artifact_catalog_payload(
        schema_version=args.schema_version,
        catalog_id=args.catalog_id,
        generated_at=args.generated_at,
        entries=entries,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer source artifact catalog to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
