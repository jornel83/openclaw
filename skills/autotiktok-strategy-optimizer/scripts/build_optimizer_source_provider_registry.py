#!/usr/bin/env python3
"""
Build an optimizer source provider registry for provider-backed real-shadow inputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSION,
    build_optimizer_source_provider_registry_payload,
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
DEFAULT_INPUT_SOURCE_ARTIFACT_CATALOG = (
    DEFAULT_ROOT / "fixtures" / "optimizer-source-artifact-catalog.sample.json"
)
DEFAULT_OUTPUT = (
    DEFAULT_ROOT / "fixtures" / "optimizer-source-provider-registry.sample.json"
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
        "--input-source-artifact-catalog",
        type=Path,
        default=DEFAULT_INPUT_SOURCE_ARTIFACT_CATALOG,
    )
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_SOURCE_PROVIDER_REGISTRY_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--registry-id",
        default="optimizer-source-provider-registry.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T03:04:00Z")
    parser.add_argument(
        "--path-style",
        choices=("repo", "absolute", "basename"),
        default="repo",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = DEFAULT_ROOT.parents[1]
    try:
        artifact_catalog_path_label = (
            args.input_source_artifact_catalog.relative_to(repo_root).as_posix()
        )
    except ValueError:
        artifact_catalog_path_label = str(args.input_source_artifact_catalog)
    if args.input_source_artifact_catalog.exists():
        artifact_catalog_payload = json.loads(
            args.input_source_artifact_catalog.read_text(encoding="utf-8")
        )
        bindings = [
            {
                "providerBindingId": "ranking_real_shadow_binding",
                "artifactKey": "ranking",
                "providerLane": "real_provider_shadow",
                "providerKind": "materialized_fixture",
                "upstreamJobKind": "ranking_output_materialization",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "resolutionMode": "artifact_catalog_entry",
                "artifactCatalogEntryId": "ranking_real_shadow_artifact",
            },
            {
                "providerBindingId": "context_real_shadow_binding",
                "artifactKey": "context",
                "providerLane": "real_provider_shadow",
                "providerKind": "materialized_fixture",
                "upstreamJobKind": "scoring_context_materialization",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "resolutionMode": "artifact_catalog_entry",
                "artifactCatalogEntryId": "context_real_shadow_artifact",
            },
            {
                "providerBindingId": "backfills_real_shadow_binding",
                "artifactKey": "backfills",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "topic_outcome_backfill",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "resolutionMode": "artifact_catalog_entry",
                "artifactCatalogEntryId": "backfills_real_shadow_artifact",
            },
            {
                "providerBindingId": "performance_real_shadow_binding",
                "artifactKey": "performance",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "post_performance_signal",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "resolutionMode": "artifact_catalog_entry",
                "artifactCatalogEntryId": "performance_real_shadow_artifact",
            },
            {
                "providerBindingId": "challenger_real_shadow_binding",
                "artifactKey": "challengerInput",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "challenger_evaluation",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "resolutionMode": "artifact_catalog_entry",
                "artifactCatalogEntryId": "challenger_real_shadow_artifact",
            },
        ]
        artifact_catalog_reference = {
            "schemaVersion": artifact_catalog_payload.get(
                "schemaVersion",
                OPTIMIZER_SOURCE_ARTIFACT_CATALOG_SAMPLE_SCHEMA_VERSION,
            ),
            "catalogId": artifact_catalog_payload.get("catalogId"),
            "path": artifact_catalog_path_label,
        }
    else:
        bindings = [
            {
                "providerBindingId": "ranking_real_shadow_binding",
                "artifactKey": "ranking",
                "providerLane": "real_provider_shadow",
                "providerKind": "materialized_fixture",
                "upstreamJobKind": "ranking_output_materialization",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "path": _path_label(args.ranking_input, style=args.path_style, repo_root=repo_root),
            },
            {
                "providerBindingId": "context_real_shadow_binding",
                "artifactKey": "context",
                "providerLane": "real_provider_shadow",
                "providerKind": "materialized_fixture",
                "upstreamJobKind": "scoring_context_materialization",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "path": _path_label(args.context_input, style=args.path_style, repo_root=repo_root),
            },
            {
                "providerBindingId": "backfills_real_shadow_binding",
                "artifactKey": "backfills",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "topic_outcome_backfill",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "path": _path_label(
                    args.backfills_raw_input, style=args.path_style, repo_root=repo_root
                ),
            },
            {
                "providerBindingId": "performance_real_shadow_binding",
                "artifactKey": "performance",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "post_performance_signal",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "path": _path_label(
                    args.performance_raw_input, style=args.path_style, repo_root=repo_root
                ),
            },
            {
                "providerBindingId": "challenger_real_shadow_binding",
                "artifactKey": "challengerInput",
                "providerLane": "real_provider_shadow",
                "providerKind": "raw_job_envelope",
                "upstreamJobKind": "challenger_evaluation",
                "providerBindingKind": "catalog_service_binding",
                "providerOwner": "autotiktok-upstream-job",
                "bindingLocatorKind": "artifact_locator_reference",
                "path": _path_label(
                    args.challenger_raw_input, style=args.path_style, repo_root=repo_root
                ),
            },
        ]
        artifact_catalog_reference = None
    payload = build_optimizer_source_provider_registry_payload(
        schema_version=args.schema_version,
        registry_id=args.registry_id,
        generated_at=args.generated_at,
        bindings=bindings,
        input_source_artifact_catalog_reference=artifact_catalog_reference,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer source provider registry to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
