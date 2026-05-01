#!/usr/bin/env python3
"""
Run a deterministic dry-run ranking pass over the shared AutoTikTok fixtures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ranking_lib import (
    DEFAULT_DISCOVERY_ARTIFACT,
    DEFAULT_RUBRIC,
    DEFAULT_SHARED_FIXTURE_ROOT,
    build_output,
    load_json,
    validate_rubric,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_DISCOVERY_ARTIFACT,
    )
    parser.add_argument(
        "--context",
        type=Path,
        default=DEFAULT_SHARED_FIXTURE_ROOT / "scoring-context.fixture.json",
    )
    parser.add_argument(
        "--profiles",
        type=Path,
        default=DEFAULT_SHARED_FIXTURE_ROOT / "scoring-profiles.fixture.json",
    )
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument("--profile-id", default="auto")
    parser.add_argument("--snapshot-id", default="snap.autotiktok.fixture.2026-04-15")
    parser.add_argument("--run-id", default="run.autotiktok.ranking.fixture.2026-04-15")
    parser.add_argument("--created-at", default="2026-04-15T00:00:00Z")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        candidates_payload = load_json(args.candidates)
        context_payload = load_json(args.context)
        profiles_payload = load_json(args.profiles)
        rubric_payload = load_json(args.rubric)
        rubric_errors = validate_rubric(rubric_payload)
        if rubric_errors:
            raise ValueError("; ".join(rubric_errors))
        payload = build_output(
            candidates_payload=candidates_payload,
            context=context_payload,
            profiles_payload=profiles_payload,
            rubric=rubric_payload,
            profile_id=args.profile_id,
            snapshot_id=args.snapshot_id,
            run_id=args.run_id,
            created_at=args.created_at,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote ranking dry-run output to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
