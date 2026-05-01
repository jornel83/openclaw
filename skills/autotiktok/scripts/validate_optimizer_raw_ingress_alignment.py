#!/usr/bin/env python3
"""
Validate that raw optimizer ingress fixtures normalize to the same canonical inputs.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
OPTIMIZER_SCRIPT_DIR = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts"
)
if str(OPTIMIZER_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(OPTIMIZER_SCRIPT_DIR))

from optimizer_input_adapters import load_daily_review_runtime_inputs
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)


RANKING_SAMPLE = (
    ROOT / "skills" / "autotiktok-topic-ranking" / "fixtures" / "ranking-dry-run.sample.json"
)
CONTEXT_SAMPLE = (
    ROOT / "skills" / "autotiktok" / "fixtures" / "scoring-context.fixture.json"
)
BACKFILLS_SAMPLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "topic-outcome-backfills.sample.json"
)
BACKFILLS_RAW_SAMPLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "topic-outcome-backfills-raw.sample.json"
)
PERFORMANCE_SAMPLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "post-performance-signals.sample.json"
)
PERFORMANCE_RAW_SAMPLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "post-performance-raw.sample.json"
)
CHALLENGER_SAMPLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "challenger-observations.sample.json"
)
CHALLENGER_RAW_SAMPLE = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "challenger-observations-raw.sample.json"
)


def _load_inputs(
    *,
    backfills_input: Path,
    performance_input: Path,
    challenger_input: Path,
):
    return load_daily_review_runtime_inputs(
        ranking_input=RANKING_SAMPLE,
        context_input=CONTEXT_SAMPLE,
        backfills_input=backfills_input,
        performance_input=performance_input,
        challenger_input=challenger_input,
        contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
        validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    )


def _assert_equal(label: str, left, right) -> None:
    if _semantic_payload(left) != _semantic_payload(right):
        raise ValueError(f"{label} normalized payloads drifted")


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _semantic_payload(payload: dict) -> dict:
    normalized = json.loads(json.dumps(payload))
    if isinstance(normalized, dict) and "schemaVersion" in normalized:
        normalized["schemaVersion"] = "__normalized__"
    return normalized


def main() -> int:
    try:
        canonical_inputs = _load_inputs(
            backfills_input=BACKFILLS_SAMPLE,
            performance_input=PERFORMANCE_SAMPLE,
            challenger_input=CHALLENGER_SAMPLE,
        )
        raw_direct_inputs = _load_inputs(
            backfills_input=BACKFILLS_RAW_SAMPLE,
            performance_input=PERFORMANCE_RAW_SAMPLE,
            challenger_input=CHALLENGER_RAW_SAMPLE,
        )
        _assert_equal(
            "backfills direct raw",
            canonical_inputs.backfills_payload,
            raw_direct_inputs.backfills_payload,
        )
        _assert_equal(
            "performance direct raw",
            canonical_inputs.performance_payload,
            raw_direct_inputs.performance_payload,
        )
        _assert_equal(
            "challenger direct raw",
            canonical_inputs.challenger_payload,
            raw_direct_inputs.challenger_payload,
        )

        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-raw-ingress-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            raw_backfills_payload = json.loads(
                BACKFILLS_RAW_SAMPLE.read_text(encoding="utf-8")
            )
            raw_backfills_payload["schemaVersion"] = "topic-outcome-backfills-raw.v1"
            raw_performance_payload = json.loads(
                PERFORMANCE_RAW_SAMPLE.read_text(encoding="utf-8")
            )
            raw_performance_payload["schemaVersion"] = "post-performance-raw.v1"
            raw_challenger_payload = json.loads(
                CHALLENGER_RAW_SAMPLE.read_text(encoding="utf-8")
            )
            raw_challenger_payload["schemaVersion"] = "challenger-observations-raw.v1"
            _write_json(
                temp_root / "backfills.json",
                {
                    "schemaVersion": "topic-outcome-backfill-run.v1",
                    "jobRunId": "job.runtime.backfill.raw-alignment.2026-04-18",
                    "jobKind": "topic_outcome_backfill",
                    "generatedAt": "2026-04-18T00:05:00Z",
                    "generatedFrom": {"sourceKind": "alignment_test"},
                    "payload": raw_backfills_payload,
                },
            )
            _write_json(
                temp_root / "performance.json",
                {
                    "schemaVersion": "post-performance-signal-run.v1",
                    "jobRunId": "job.runtime.performance.raw-alignment.2026-04-18",
                    "jobKind": "post_performance_signal",
                    "generatedAt": "2026-04-18T00:10:00Z",
                    "generatedFrom": {"sourceKind": "alignment_test"},
                    "payload": raw_performance_payload,
                },
            )
            _write_json(
                temp_root / "challenger.json",
                {
                    "schemaVersion": "challenger-evaluation-run.v1",
                    "jobRunId": "job.runtime.challenger.raw-alignment.2026-04-18",
                    "jobKind": "challenger_evaluation",
                    "generatedAt": "2026-04-18T00:15:00Z",
                    "generatedFrom": {"sourceKind": "alignment_test"},
                    "payload": raw_challenger_payload,
                },
            )
            raw_envelope_inputs = _load_inputs(
                backfills_input=temp_root / "backfills.json",
                performance_input=temp_root / "performance.json",
                challenger_input=temp_root / "challenger.json",
            )
        _assert_equal(
            "backfills raw envelope",
            canonical_inputs.backfills_payload,
            raw_envelope_inputs.backfills_payload,
        )
        _assert_equal(
            "performance raw envelope",
            canonical_inputs.performance_payload,
            raw_envelope_inputs.performance_payload,
        )
        _assert_equal(
            "challenger raw envelope",
            canonical_inputs.challenger_payload,
            raw_envelope_inputs.challenger_payload,
        )
        print("Validated optimizer raw ingress alignment for direct artifacts and job-run envelopes.")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
