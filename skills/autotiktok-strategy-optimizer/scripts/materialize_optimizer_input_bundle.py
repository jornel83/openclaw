#!/usr/bin/env python3
"""
Materialize an optimizer input bundle from an optimizer input manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from optimizer_bundle_lib import (
    OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSION,
    materialize_optimizer_input_bundle_from_manifest,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = DEFAULT_ROOT / "fixtures" / "optimizer-input-manifest.sample.json"
DEFAULT_OUTPUT = DEFAULT_ROOT / "fixtures" / "optimizer-input-bundle.sample.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--schema-version",
        default=OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
        choices=(
            OPTIMIZER_INPUT_BUNDLE_SAMPLE_SCHEMA_VERSION,
            OPTIMIZER_INPUT_BUNDLE_SCHEMA_VERSION,
        ),
    )
    parser.add_argument("--bundle-id")
    parser.add_argument("--generated-at")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        payload, _ = materialize_optimizer_input_bundle_from_manifest(
            manifest_path=args.input_manifest,
            bundle_schema_version=args.schema_version,
            bundle_id=args.bundle_id,
            generated_at=args.generated_at,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote optimizer input bundle to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
