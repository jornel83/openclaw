#!/usr/bin/env python3
"""
Build an optimizer input source registry for canonical, raw-shadow, and provider-backed real lanes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_INPUT_SOURCE_REGISTRY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSION,
    build_optimizer_input_source_registry_payload,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING = (
    DEFAULT_ROOT.parent / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
DEFAULT_CONTEXT = DEFAULT_ROOT.parent / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
DEFAULT_BACKFILLS = DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-run.sample.json"
DEFAULT_PERFORMANCE = DEFAULT_ROOT / "fixtures" / "post-performance-signal-run.sample.json"
DEFAULT_CHALLENGER = DEFAULT_ROOT / "fixtures" / "challenger-evaluation-run.sample.json"
DEFAULT_BACKFILLS_RAW = (
    DEFAULT_ROOT / "fixtures" / "topic-outcome-backfill-raw-run.sample.json"
)
DEFAULT_PERFORMANCE_RAW = (
    DEFAULT_ROOT / "fixtures" / "post-performance-signal-raw-run.sample.json"
)
DEFAULT_CHALLENGER_RAW = (
    DEFAULT_ROOT / "fixtures" / "challenger-evaluation-raw-run.sample.json"
)
DEFAULT_INPUT_ARTIFACT_RESOLVER = (
    DEFAULT_ROOT / "fixtures" / "optimizer-job-artifact-resolver.sample.json"
)
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-input-source-registry.sample.json"


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
    parser.add_argument("--backfills-input", type=Path, default=DEFAULT_BACKFILLS)
    parser.add_argument("--performance-input", type=Path, default=DEFAULT_PERFORMANCE)
    parser.add_argument("--challenger-input", type=Path, default=DEFAULT_CHALLENGER)
    parser.add_argument("--backfills-raw-input", type=Path, default=DEFAULT_BACKFILLS_RAW)
    parser.add_argument("--performance-raw-input", type=Path, default=DEFAULT_PERFORMANCE_RAW)
    parser.add_argument("--challenger-raw-input", type=Path, default=DEFAULT_CHALLENGER_RAW)
    parser.add_argument(
        "--input-artifact-resolver", type=Path, default=DEFAULT_INPUT_ARTIFACT_RESOLVER
    )
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_INPUT_SOURCE_REGISTRY_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_INPUT_SOURCE_REGISTRY_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_INPUT_SOURCE_REGISTRY_SCHEMA_VERSION,
        ),
    )
    parser.add_argument(
        "--registry-id",
        default="optimizer-input-source-registry.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T03:00:00Z")
    parser.add_argument(
        "--path-style",
        choices=("repo", "absolute", "basename"),
        default="repo",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = DEFAULT_ROOT.parents[1]
    try:
        resolver_path_label = args.input_artifact_resolver.relative_to(repo_root).as_posix()
    except ValueError:
        resolver_path_label = str(args.input_artifact_resolver)
    resolver_payload = json.loads(args.input_artifact_resolver.read_text(encoding="utf-8"))
    sources = [
        {
            "bindingId": "ranking_sample",
            "artifactKey": "ranking",
            "sourceLane": "sample_canonical",
            "path": _path_label(args.ranking_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "context_sample",
            "artifactKey": "context",
            "sourceLane": "sample_canonical",
            "path": _path_label(args.context_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "backfills_sample",
            "artifactKey": "backfills",
            "sourceLane": "sample_canonical",
            "path": _path_label(args.backfills_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "performance_sample",
            "artifactKey": "performance",
            "sourceLane": "sample_canonical",
            "path": _path_label(args.performance_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "challenger_sample",
            "artifactKey": "challengerInput",
            "sourceLane": "sample_canonical",
            "path": _path_label(args.challenger_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "ranking_raw_shadow",
            "artifactKey": "ranking",
            "sourceLane": "sample_raw_shadow",
            "path": _path_label(args.ranking_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "context_raw_shadow",
            "artifactKey": "context",
            "sourceLane": "sample_raw_shadow",
            "path": _path_label(args.context_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "backfills_raw_shadow",
            "artifactKey": "backfills",
            "sourceLane": "sample_raw_shadow",
            "path": _path_label(args.backfills_raw_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "performance_raw_shadow",
            "artifactKey": "performance",
            "sourceLane": "sample_raw_shadow",
            "path": _path_label(args.performance_raw_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "challenger_raw_shadow",
            "artifactKey": "challengerInput",
            "sourceLane": "sample_raw_shadow",
            "path": _path_label(args.challenger_raw_input, style=args.path_style, repo_root=repo_root),
        },
        {
            "bindingId": "ranking_real_shadow",
            "artifactKey": "ranking",
            "sourceLane": "real_provider_shadow",
            "resolutionMode": "job_artifact_resolver",
            "resolverEntryId": "ranking_real_shadow",
        },
        {
            "bindingId": "context_real_shadow",
            "artifactKey": "context",
            "sourceLane": "real_provider_shadow",
            "resolutionMode": "job_artifact_resolver",
            "resolverEntryId": "context_real_shadow",
        },
        {
            "bindingId": "backfills_real_shadow",
            "artifactKey": "backfills",
            "sourceLane": "real_provider_shadow",
            "resolutionMode": "job_artifact_resolver",
            "resolverEntryId": "backfills_real_shadow",
        },
        {
            "bindingId": "performance_real_shadow",
            "artifactKey": "performance",
            "sourceLane": "real_provider_shadow",
            "resolutionMode": "job_artifact_resolver",
            "resolverEntryId": "performance_real_shadow",
        },
        {
            "bindingId": "challenger_real_shadow",
            "artifactKey": "challengerInput",
            "sourceLane": "real_provider_shadow",
            "resolutionMode": "job_artifact_resolver",
            "resolverEntryId": "challenger_real_shadow",
        },
    ]
    payload = build_optimizer_input_source_registry_payload(
        schema_version=args.schema_version,
        registry_id=args.registry_id,
        generated_at=args.generated_at,
        sources=sources,
        input_artifact_resolver_reference={
            "schemaVersion": resolver_payload.get("schemaVersion"),
            "resolverId": resolver_payload.get("resolverId"),
            "path": resolver_path_label,
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote optimizer input source registry to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
