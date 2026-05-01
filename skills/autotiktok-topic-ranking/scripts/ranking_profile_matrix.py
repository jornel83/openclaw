#!/usr/bin/env python3
"""
Run deterministic ranking replays across multiple scoring stages and emit a compact comparison matrix.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
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


DEFAULT_STAGE_MODES = ("growth", "scale", "search_priority")
DEFAULT_CONTEXT_MATRIX = DEFAULT_SHARED_FIXTURE_ROOT / "scoring-context-matrix.fixture.json"


def build_matrix_entry(stage_mode: str, ranking_payload: dict[str, object]) -> dict[str, object]:
    scores = ranking_payload["scores"]
    ranking_summary = ranking_payload["rankingSummary"]
    prediction_run = ranking_payload["predictionRun"]
    compact_scores = [
        {
            "topicId": row["topicId"],
            "scoreTotal": row["scoreTotal"],
            "priorityLevel": row["priorityLevel"],
            "recommendedUse": row["recommendedUse"],
            "isRejected": row["isRejected"],
        }
        for row in scores
    ]
    return {
        "stageMode": stage_mode,
        "profileId": ranking_payload["profileId"],
        "profileSelection": ranking_payload["profileSelection"],
        "candidateSource": ranking_payload["candidateSource"],
        "rankingSnapshotId": prediction_run["snapshotId"],
        "topTopicId": ranking_summary["topTopicId"],
        "topTopicTitle": ranking_summary["topTopicTitle"],
        "rejectedTopicIds": ranking_summary["rejectedTopicIds"],
        "priorityCounts": ranking_summary["priorityCounts"],
        "rankedTopicIds": prediction_run["rankedTopicIds"],
        "scores": compact_scores,
    }


def resolve_stage_contexts(
    context_matrix_payload: dict[str, object], requested_stage_modes: list[str]
) -> list[tuple[str, dict[str, object]]]:
    stages = context_matrix_payload.get("stages")
    if not isinstance(stages, list) or not stages:
        raise ValueError("context matrix payload must include a non-empty `stages` list")

    stage_map: dict[str, dict[str, object]] = {}
    for stage_entry in stages:
        if not isinstance(stage_entry, dict):
            raise ValueError("context matrix entries must be objects")
        stage_mode = stage_entry.get("stageMode")
        context = stage_entry.get("context")
        if not isinstance(stage_mode, str) or not isinstance(context, dict):
            raise ValueError("context matrix entries must include `stageMode` and `context`")
        stage_map[stage_mode] = context

    resolved: list[tuple[str, dict[str, object]]] = []
    for stage_mode in requested_stage_modes:
        if stage_mode not in stage_map:
            raise ValueError(f"context matrix missing requested stageMode `{stage_mode}`")
        resolved.append((stage_mode, stage_map[stage_mode]))
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_DISCOVERY_ARTIFACT,
    )
    parser.add_argument("--context-matrix", type=Path, default=DEFAULT_CONTEXT_MATRIX)
    parser.add_argument(
        "--profiles",
        type=Path,
        default=DEFAULT_SHARED_FIXTURE_ROOT / "scoring-profiles.fixture.json",
    )
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument(
        "--stage-modes",
        nargs="+",
        default=list(DEFAULT_STAGE_MODES),
    )
    parser.add_argument("--matrix-id", default="ranking-profile-matrix.autotiktok.fixture.2026-04-15")
    parser.add_argument("--generated-at", default="2026-04-15T00:00:00Z")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        candidates_payload = load_json(args.candidates)
        context_matrix_payload = load_json(args.context_matrix)
        profiles_payload = load_json(args.profiles)
        rubric_payload = load_json(args.rubric)
        rubric_errors = validate_rubric(rubric_payload)
        if rubric_errors:
            raise ValueError("; ".join(rubric_errors))

        stage_entries = []
        for stage_mode, stage_context in resolve_stage_contexts(
            context_matrix_payload, args.stage_modes
        ):
            ranking_payload = build_output(
                candidates_payload=candidates_payload,
                context=deepcopy(stage_context),
                profiles_payload=profiles_payload,
                rubric=rubric_payload,
                profile_id="auto",
                snapshot_id=f"snap.autotiktok.matrix.{stage_mode}.fixture.2026-04-15",
                run_id=f"run.autotiktok.matrix.{stage_mode}.fixture.2026-04-15",
                created_at=args.generated_at,
            )
            stage_entries.append(build_matrix_entry(stage_mode, ranking_payload))

        payload = {
            "schemaVersion": "ranking-profile-matrix.v1",
            "matrixId": args.matrix_id,
            "generatedAt": args.generated_at,
            "generatedFrom": {
                "candidateInputSchemaVersion": stage_entries[0]["candidateSource"]["inputSchemaVersion"]
                if stage_entries
                else None,
                "candidateSourceKind": stage_entries[0]["candidateSource"]["sourceKind"]
                if stage_entries
                else None,
                "discoveryPolicyVersion": stage_entries[0]["candidateSource"]["sourcePolicyVersion"]
                if stage_entries
                else None,
                "contextMatrixFixtureVersion": context_matrix_payload.get("fixtureSetVersion"),
                "rubricSchemaVersion": rubric_payload["schemaVersion"],
            },
            "stages": stage_entries,
        }
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote ranking profile matrix to {args.output}")
        return 0

    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
