#!/usr/bin/env python3
"""
Build a scheduler-facing optimizer job shadow-compare batch artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from optimizer_job_shadow_compare_lib import (
    build_optimizer_job_shadow_compare_batch_payload,
    load_optimizer_job_shadow_compare,
    load_optimizer_job_shadow_compare_batch_manifest,
    resolve_optimizer_job_shadow_compare_path,
    validate_optimizer_job_shadow_compare_batch_payload,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BATCH_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch-manifest.sample.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-shadow-compare-batch.sample.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-batch-manifest", type=Path, default=DEFAULT_BATCH_MANIFEST)
    parser.add_argument(
        "--batch-id",
        default="optimizer-job-shadow-compare-batch.autotiktok.fixture.2026-04-18",
    )
    parser.add_argument("--generated-at", default="2026-04-18T06:15:00Z")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        batch_manifest = load_optimizer_job_shadow_compare_batch_manifest(
            args.input_batch_manifest
        )
        compare_payloads = [
            load_optimizer_job_shadow_compare(
                resolve_optimizer_job_shadow_compare_path(
                    path_label,
                    manifest_path=args.input_batch_manifest.resolve(),
                )
            )
            for path_label in batch_manifest["compareArtifactPaths"]
        ]
        payload = build_optimizer_job_shadow_compare_batch_payload(
            compare_payloads=compare_payloads,
            batch_id=args.batch_id,
            generated_at=args.generated_at,
            source_mode="compare_manifest",
            source_descriptor={
                "batchManifestSchemaVersion": batch_manifest.get("schemaVersion"),
                "batchManifestId": batch_manifest.get("manifestId"),
                "comparisonDimension": batch_manifest.get("comparisonDimension"),
                "batchWindowLabel": batch_manifest.get("batchWindowLabel"),
                "compareArtifactCount": len(batch_manifest["compareArtifactPaths"]),
            },
            comparison_dimension=batch_manifest["comparisonDimension"],
            batch_window_label=batch_manifest["batchWindowLabel"],
        )
        validate_optimizer_job_shadow_compare_batch_payload(payload)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer job shadow compare batch to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
