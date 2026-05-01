#!/usr/bin/env python3
"""
Machine-readable inventory of AutoTikTok surfaces that intentionally retain a live-lane default.
"""

from __future__ import annotations

from typing import Any


LIVE_LANE_DEPENDENCY_INVENTORY_SCHEMA_VERSION = (
    "live-lane-dependency-inventory.v1"
)

PREVIEW_FIRST_WRAPPERS = [
    {
        "id": "preview_daily_review",
        "command": "skills/autotiktok-strategy-optimizer/scripts/run_preview_daily_review.py",
        "wraps": "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
        "defaultLane": "preview",
        "defaultContractVersion": "ranking-optimizer-contract.vNext-preview",
        "defaultValidationMode": "exact",
        "fallbackFlag": "--use-current-lane",
    },
    {
        "id": "preview_optimizer_stage_matrix",
        "command": "skills/autotiktok/scripts/run_preview_optimizer_stage_matrix.py",
        "wraps": "skills/autotiktok/scripts/run_optimizer_stage_matrix.py",
        "defaultLane": "preview",
        "defaultContractVersion": "ranking-optimizer-contract.vNext-preview",
        "defaultValidationMode": "exact",
        "fallbackFlag": "--use-current-lane",
    },
    {
        "id": "preview_autotiktok_workflow",
        "command": "skills/autotiktok/scripts/run_preview_autotiktok_workflow.py",
        "wraps": "skills/autotiktok/scripts/run_autotiktok_workflow.py",
        "defaultLane": "preview",
        "defaultContractVersion": "ranking-optimizer-contract.vNext-preview",
        "defaultValidationMode": "exact",
        "fallbackFlag": "--use-current-lane",
    },
]

LIVE_LANE_DEFAULT_DEPENDENCIES = [
    {
        "id": "current_contract_gate",
        "command": "skills/autotiktok/scripts/validate_ranking_optimizer_contract.py",
        "category": "contract_gate",
        "defaultLane": "current",
        "retainedBecause": "This is the explicit live-contract gate for the committed v1/exact handoff.",
        "previewAlternative": "skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py",
        "shrinkStatus": "paired_with_preview_gate",
    },
    {
        "id": "daily_review_runtime_entrypoint",
        "command": "skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py",
        "category": "runtime_entrypoint",
        "defaultLane": "current",
        "retainedBecause": "Current-lane daily review remains the source for committed optimizer output fixtures and current-lane contract replay.",
        "previewAlternative": "skills/autotiktok-strategy-optimizer/scripts/run_preview_daily_review.py",
        "shrinkStatus": "reduced_with_preview_wrapper",
    },
    {
        "id": "optimizer_output_sync",
        "command": "skills/autotiktok/scripts/sync_optimizer_sample_outputs.py",
        "category": "fixture_sync",
        "defaultLane": "current",
        "retainedBecause": "This writes committed daily-review and weekly-promotion sample artifacts that still anchor on the current exact-path lane.",
        "previewAlternative": None,
        "shrinkStatus": "must_stay_live_for_committed_fixtures",
    },
    {
        "id": "optimizer_output_alignment",
        "command": "skills/autotiktok/scripts/validate_optimizer_output_alignment.py",
        "category": "fixture_alignment",
        "defaultLane": "current",
        "retainedBecause": "This alignment gate compares committed optimizer sample artifacts against the current exact-path generators.",
        "previewAlternative": None,
        "shrinkStatus": "must_stay_live_for_committed_fixtures",
    },
    {
        "id": "optimizer_stage_matrix_runner",
        "command": "skills/autotiktok/scripts/run_optimizer_stage_matrix.py",
        "category": "base_runner",
        "defaultLane": "current",
        "retainedBecause": "The base runner keeps the current lane by default because committed stage-matrix fixture sync and alignment still use it.",
        "previewAlternative": "skills/autotiktok/scripts/run_preview_optimizer_stage_matrix.py",
        "shrinkStatus": "reduced_with_preview_wrapper",
    },
    {
        "id": "optimizer_stage_matrix_sync",
        "command": "skills/autotiktok/scripts/sync_optimizer_stage_matrix.py",
        "category": "fixture_sync",
        "defaultLane": "current",
        "retainedBecause": "This regenerates the committed optimizer stage-matrix sample, which intentionally remains current-lane anchored.",
        "previewAlternative": None,
        "shrinkStatus": "must_stay_live_for_committed_fixtures",
    },
    {
        "id": "optimizer_stage_matrix_alignment",
        "command": "skills/autotiktok/scripts/validate_optimizer_stage_matrix_alignment.py",
        "category": "fixture_alignment",
        "defaultLane": "current",
        "retainedBecause": "This validates the committed current-lane optimizer stage-matrix artifact against deterministic generation.",
        "previewAlternative": None,
        "shrinkStatus": "must_stay_live_for_committed_fixtures",
    },
    {
        "id": "workflow_runner",
        "command": "skills/autotiktok/scripts/run_autotiktok_workflow.py",
        "category": "base_runner",
        "defaultLane": "current",
        "retainedBecause": "The base workflow runner keeps the current lane by default because committed workflow summary sync and alignment still use it.",
        "previewAlternative": "skills/autotiktok/scripts/run_preview_autotiktok_workflow.py",
        "shrinkStatus": "reduced_with_preview_wrapper",
    },
    {
        "id": "workflow_summary_sync",
        "command": "skills/autotiktok/scripts/sync_workflow_summary_sample.py",
        "category": "fixture_sync",
        "defaultLane": "current",
        "retainedBecause": "This regenerates the committed workflow summary sample, which intentionally remains current-lane anchored.",
        "previewAlternative": None,
        "shrinkStatus": "must_stay_live_for_committed_fixtures",
    },
    {
        "id": "workflow_summary_alignment",
        "command": "skills/autotiktok/scripts/validate_workflow_summary_alignment.py",
        "category": "fixture_alignment",
        "defaultLane": "current",
        "retainedBecause": "This validates the committed current-lane workflow summary artifact against deterministic generation.",
        "previewAlternative": None,
        "shrinkStatus": "must_stay_live_for_committed_fixtures",
    },
    {
        "id": "artifact_provenance_chain",
        "command": "skills/autotiktok/scripts/validate_artifact_provenance_chain.py",
        "category": "provenance_gate",
        "defaultLane": "current",
        "retainedBecause": "The provenance gate still checks the committed exact-path artifact chain, so its default remains current-lane anchored.",
        "previewAlternative": "skills/autotiktok/scripts/validate_preview_lane_cutover.py",
        "shrinkStatus": "paired_with_preview_gate",
    },
]


def build_live_lane_dependency_inventory() -> dict[str, Any]:
    return {
        "schemaVersion": LIVE_LANE_DEPENDENCY_INVENTORY_SCHEMA_VERSION,
        "scope": "ranking-to-optimizer lane migration",
        "previewFirstWrappers": PREVIEW_FIRST_WRAPPERS,
        "liveLaneDefaultDependencies": LIVE_LANE_DEFAULT_DEPENDENCIES,
    }
