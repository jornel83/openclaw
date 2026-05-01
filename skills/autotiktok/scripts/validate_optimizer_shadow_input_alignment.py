#!/usr/bin/env python3
"""
Validate raw-shadow optimizer input registry and manifest generation plus runtime alignment.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OPTIMIZER_SCRIPT_DIR = (
    ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts"
)
if str(OPTIMIZER_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(OPTIMIZER_SCRIPT_DIR))

from optimizer_input_adapters import load_daily_review_runtime_inputs_from_manifest
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)


BUILD_SOURCE_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_source_registry.py"
)
BUILD_MANIFEST_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_input_manifest.py"
)
COMMITTED_SOURCE_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-source-registry.sample.json"
)
COMMITTED_CANONICAL_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.sample.json"
)
COMMITTED_RAW_SHADOW_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.raw-shadow.sample.json"
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script.relative_to(ROOT)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def _semantic_payload(payload: dict) -> dict:
    normalized = json.loads(json.dumps(payload))
    if isinstance(normalized, dict) and "schemaVersion" in normalized:
        normalized["schemaVersion"] = "__normalized__"
    return normalized


def _assert_equal(label: str, left, right) -> None:
    if _semantic_payload(left) != _semantic_payload(right):
        raise ValueError(f"{label} drifted between canonical and raw-shadow manifests")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-shadow-input-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            generated_registry = temp_root / "optimizer-input-source-registry.json"
            generated_raw_shadow_manifest = (
                temp_root / "optimizer-input-manifest.raw-shadow.json"
            )
            _run_script(
                BUILD_SOURCE_REGISTRY_SCRIPT,
                "--output",
                str(generated_registry),
            )
            _run_script(
                BUILD_MANIFEST_SCRIPT,
                "--input-source-registry",
                str(COMMITTED_SOURCE_REGISTRY),
                "--source-lane",
                "sample_raw_shadow",
                "--manifest-id",
                "optimizer-input-manifest.raw-shadow.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T03:05:00Z",
                "--output",
                str(generated_raw_shadow_manifest),
            )
            if _load_json(generated_registry) != _load_json(COMMITTED_SOURCE_REGISTRY):
                raise ValueError(
                    "committed optimizer-input-source-registry.sample.json is out of sync"
                )
            if _load_json(generated_raw_shadow_manifest) != _load_json(
                COMMITTED_RAW_SHADOW_MANIFEST
            ):
                raise ValueError(
                    "committed optimizer-input-manifest.raw-shadow.sample.json is out of sync"
                )
        canonical_inputs = load_daily_review_runtime_inputs_from_manifest(
            input_manifest=COMMITTED_CANONICAL_MANIFEST,
            contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
            validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        )
        raw_shadow_inputs = load_daily_review_runtime_inputs_from_manifest(
            input_manifest=COMMITTED_RAW_SHADOW_MANIFEST,
            contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
            validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        )
        _assert_equal(
            "backfills runtime payload",
            canonical_inputs.backfills_payload,
            raw_shadow_inputs.backfills_payload,
        )
        _assert_equal(
            "performance runtime payload",
            canonical_inputs.performance_payload,
            raw_shadow_inputs.performance_payload,
        )
        _assert_equal(
            "challenger runtime payload",
            canonical_inputs.challenger_payload,
            raw_shadow_inputs.challenger_payload,
        )
        print(
            "Optimizer raw-shadow source registry and manifest are aligned with deterministic generation."
        )
        print(
            "Canonical and raw-shadow manifests normalize to the same runtime optimizer inputs."
        )
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
