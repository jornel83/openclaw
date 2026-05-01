#!/usr/bin/env python3
"""
Validate resolver-based real-shadow optimizer input generation plus runtime alignment.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OPTIMIZER_SCRIPT_DIR = ROOT / "skills" / "autotiktok-strategy-optimizer" / "scripts"
if str(OPTIMIZER_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(OPTIMIZER_SCRIPT_DIR))

from optimizer_input_adapters import load_daily_review_runtime_inputs_from_manifest
from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
    RANKING_OPTIMIZER_CONTRACT_VERSION,
)


BUILD_JOB_ARTIFACT_RESOLVER_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_job_artifact_resolver.py"
)
BUILD_SOURCE_ARTIFACT_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_source_artifact_catalog.py"
)
BUILD_SOURCE_PROVIDER_CATALOG_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_source_provider_catalog.py"
)
BUILD_SOURCE_PROVIDER_REGISTRY_SCRIPT = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "scripts"
    / "build_optimizer_source_provider_registry.py"
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
COMMITTED_SOURCE_PROVIDER_CATALOG = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-source-provider-catalog.sample.json"
)
COMMITTED_SOURCE_ARTIFACT_CATALOG = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-source-artifact-catalog.sample.json"
)
COMMITTED_SOURCE_PROVIDER_REGISTRY = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-source-provider-registry.sample.json"
)
COMMITTED_JOB_ARTIFACT_RESOLVER = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-job-artifact-resolver.sample.json"
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
COMMITTED_REAL_SHADOW_MANIFEST = (
    ROOT
    / "skills"
    / "autotiktok-strategy-optimizer"
    / "fixtures"
    / "optimizer-input-manifest.real-shadow.sample.json"
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
        raise ValueError(f"{label} drifted between shadow lanes")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(
            prefix="autotiktok-optimizer-real-shadow-input-"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            generated_artifact_catalog = (
                temp_root / "optimizer-source-artifact-catalog.json"
            )
            generated_provider_registry = (
                temp_root / "optimizer-source-provider-registry.json"
            )
            generated_provider_catalog = (
                temp_root / "optimizer-source-provider-catalog.json"
            )
            generated_resolver = temp_root / "optimizer-job-artifact-resolver.json"
            generated_registry = temp_root / "optimizer-input-source-registry.json"
            generated_real_shadow_manifest = (
                temp_root / "optimizer-input-manifest.real-shadow.json"
            )
            _run_script(
                BUILD_SOURCE_ARTIFACT_CATALOG_SCRIPT,
                "--output",
                str(generated_artifact_catalog),
            )
            _run_script(
                BUILD_SOURCE_PROVIDER_REGISTRY_SCRIPT,
                "--input-source-artifact-catalog",
                str(COMMITTED_SOURCE_ARTIFACT_CATALOG),
                "--output",
                str(generated_provider_registry),
            )
            _run_script(
                BUILD_SOURCE_PROVIDER_CATALOG_SCRIPT,
                "--input-source-provider-registry",
                str(COMMITTED_SOURCE_PROVIDER_REGISTRY),
                "--output",
                str(generated_provider_catalog),
            )
            _run_script(
                BUILD_JOB_ARTIFACT_RESOLVER_SCRIPT,
                "--input-source-provider-catalog",
                str(COMMITTED_SOURCE_PROVIDER_CATALOG),
                "--output",
                str(generated_resolver),
            )
            _run_script(
                BUILD_SOURCE_REGISTRY_SCRIPT,
                "--input-artifact-resolver",
                str(COMMITTED_JOB_ARTIFACT_RESOLVER),
                "--output",
                str(generated_registry),
            )
            _run_script(
                BUILD_MANIFEST_SCRIPT,
                "--input-source-registry",
                str(COMMITTED_SOURCE_REGISTRY),
                "--source-lane",
                "real_provider_shadow",
                "--manifest-id",
                "optimizer-input-manifest.real-shadow.autotiktok.fixture.2026-04-18",
                "--generated-at",
                "2026-04-18T03:12:00Z",
                "--output",
                str(generated_real_shadow_manifest),
            )
            if _load_json(generated_provider_registry) != _load_json(
                COMMITTED_SOURCE_PROVIDER_REGISTRY
            ):
                raise ValueError(
                    "committed optimizer-source-provider-registry.sample.json is out of sync"
                )
            if _load_json(generated_artifact_catalog) != _load_json(
                COMMITTED_SOURCE_ARTIFACT_CATALOG
            ):
                raise ValueError(
                    "committed optimizer-source-artifact-catalog.sample.json is out of sync"
                )
            if _load_json(generated_provider_catalog) != _load_json(
                COMMITTED_SOURCE_PROVIDER_CATALOG
            ):
                raise ValueError(
                    "committed optimizer-source-provider-catalog.sample.json is out of sync"
                )
            if _load_json(generated_resolver) != _load_json(COMMITTED_JOB_ARTIFACT_RESOLVER):
                raise ValueError(
                    "committed optimizer-job-artifact-resolver.sample.json is out of sync"
                )
            if _load_json(generated_registry) != _load_json(COMMITTED_SOURCE_REGISTRY):
                raise ValueError(
                    "committed optimizer-input-source-registry.sample.json is out of sync"
                )
            if _load_json(generated_real_shadow_manifest) != _load_json(
                COMMITTED_REAL_SHADOW_MANIFEST
            ):
                raise ValueError(
                    "committed optimizer-input-manifest.real-shadow.sample.json is out of sync"
                )
        committed_real_shadow_manifest = _load_json(COMMITTED_REAL_SHADOW_MANIFEST)
        if committed_real_shadow_manifest["generatedFrom"].get("sourceLane") != "real_provider_shadow":
            raise ValueError(
                "committed optimizer-input-manifest.real-shadow.sample.json must resolve real_provider_shadow"
            )
        if committed_real_shadow_manifest["generatedFrom"].get("optimizerInputSourceProviderClass") != "artifact_catalog_service":
            raise ValueError(
                "committed optimizer-input-manifest.real-shadow.sample.json must preserve provider-backed source class provenance"
            )
        if committed_real_shadow_manifest["generatedFrom"].get("optimizerInputArtifactLocatorKind") != "provider_locator":
            raise ValueError(
                "committed optimizer-input-manifest.real-shadow.sample.json must preserve provider-backed artifact locator provenance"
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
        real_shadow_inputs = load_daily_review_runtime_inputs_from_manifest(
            input_manifest=COMMITTED_REAL_SHADOW_MANIFEST,
            contract_version=RANKING_OPTIMIZER_CONTRACT_VERSION,
            validation_mode=RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
        )
        for label, canonical_payload, raw_shadow_payload, real_shadow_payload in (
            (
                "backfills runtime payload",
                canonical_inputs.backfills_payload,
                raw_shadow_inputs.backfills_payload,
                real_shadow_inputs.backfills_payload,
            ),
            (
                "performance runtime payload",
                canonical_inputs.performance_payload,
                raw_shadow_inputs.performance_payload,
                real_shadow_inputs.performance_payload,
            ),
            (
                "challenger runtime payload",
                canonical_inputs.challenger_payload,
                raw_shadow_inputs.challenger_payload,
                real_shadow_inputs.challenger_payload,
            ),
        ):
            _assert_equal(label, canonical_payload, raw_shadow_payload)
            _assert_equal(label, raw_shadow_payload, real_shadow_payload)
        print(
            "Optimizer real-shadow source artifact catalog, provider registry, source provider catalog, resolver, source registry, and manifest are aligned with deterministic generation."
        )
        print(
            "Canonical, raw-shadow, and real-shadow manifests normalize to the same runtime optimizer inputs."
        )
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
