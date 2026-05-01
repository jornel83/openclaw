#!/usr/bin/env python3
"""
Helpers for planner-facing optimizer runtime materialization plans.
"""

from __future__ import annotations

from typing import Any

from optimizer_job_input_lib import (
    CHALLENGER_EVALUATION_JOB_KIND,
    POST_PERFORMANCE_SIGNAL_JOB_KIND,
    TOPIC_OUTCOME_BACKFILL_JOB_KIND,
)


OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SAMPLE_SCHEMA_VERSION = (
    "optimizer-runtime-materialization-plan.sample.v1"
)
OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSION = (
    "optimizer-runtime-materialization-plan.v1"
)
OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSIONS = {
    OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSION,
}

MATERIALIZATION_STRATEGIES = (
    "job_run_aggregation",
    "manifest_materialization",
    "offline_cycle_execution",
)


def build_optimizer_runtime_materialization_plan_entry(
    *,
    plan_id: str,
    output_binding_id: str,
    job_family_group: str,
    materialization_profile: str,
    source_class: str,
    source_variant: str,
    materialization_strategy: str,
    upstream_job_families: list[str],
    required_artifact_kinds: list[str],
    include_weekly_promotion: bool | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "planId": plan_id,
        "outputBindingId": output_binding_id,
        "jobFamilyGroup": job_family_group,
        "materializationProfile": materialization_profile,
        "sourceClass": source_class,
        "sourceVariant": source_variant,
        "materializationStrategy": materialization_strategy,
        "upstreamJobFamilies": upstream_job_families,
        "requiredArtifactKinds": required_artifact_kinds,
    }
    if include_weekly_promotion is not None:
        payload["includeWeeklyPromotion"] = include_weekly_promotion
    return payload


def build_optimizer_runtime_materialization_plan_payload(
    *,
    plans: list[dict[str, Any]],
    schema_version: str,
    plan_set_id: str,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": schema_version,
        "planSetId": plan_set_id,
        "generatedAt": generated_at,
        "generatedFrom": {
            "planCount": len(plans),
        },
        "plans": plans,
    }


def build_default_optimizer_runtime_materialization_plans() -> list[dict[str, Any]]:
    return [
        build_optimizer_runtime_materialization_plan_entry(
            plan_id="optimizer_input_manifest_plan",
            output_binding_id="optimizer_input_manifest",
            job_family_group="optimizer_input_jobs",
            materialization_profile="manifest_from_job_runs",
            source_class="optimizer_input",
            source_variant="manifest",
            materialization_strategy="job_run_aggregation",
            upstream_job_families=[
                TOPIC_OUTCOME_BACKFILL_JOB_KIND,
                POST_PERFORMANCE_SIGNAL_JOB_KIND,
                CHALLENGER_EVALUATION_JOB_KIND,
            ],
            required_artifact_kinds=["ranking_output", "scoring_context"],
        ),
        build_optimizer_runtime_materialization_plan_entry(
            plan_id="optimizer_input_bundle_plan",
            output_binding_id="optimizer_input_bundle",
            job_family_group="optimizer_input_jobs",
            materialization_profile="bundle_from_manifest",
            source_class="optimizer_input",
            source_variant="bundle",
            materialization_strategy="manifest_materialization",
            upstream_job_families=[],
            required_artifact_kinds=["optimizer_input_manifest"],
        ),
        build_optimizer_runtime_materialization_plan_entry(
            plan_id="optimizer_offline_cycle_daily_plan",
            output_binding_id="optimizer_offline_cycle_daily",
            job_family_group="optimizer_offline_cycle_jobs",
            materialization_profile="daily_cycle_from_manifest",
            source_class="optimizer_offline_cycle",
            source_variant="daily",
            materialization_strategy="offline_cycle_execution",
            upstream_job_families=[],
            required_artifact_kinds=["optimizer_input_manifest"],
            include_weekly_promotion=False,
        ),
        build_optimizer_runtime_materialization_plan_entry(
            plan_id="optimizer_offline_cycle_weekly_plan",
            output_binding_id="optimizer_offline_cycle_weekly",
            job_family_group="optimizer_offline_cycle_jobs",
            materialization_profile="weekly_cycle_from_bundle",
            source_class="optimizer_offline_cycle",
            source_variant="weekly",
            materialization_strategy="offline_cycle_execution",
            upstream_job_families=[],
            required_artifact_kinds=["optimizer_input_bundle"],
            include_weekly_promotion=True,
        ),
    ]


def _require_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def validate_optimizer_runtime_materialization_plan_payload(
    payload: dict[str, Any],
) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_RUNTIME_MATERIALIZATION_PLAN_SCHEMA_VERSIONS))
        raise ValueError(
            "optimizer runtime materialization plan schemaVersion must be one of "
            f"[{allowed}], got {schema_version!r}"
        )
    _require_string(payload.get("planSetId"), label="planSetId")
    _require_string(payload.get("generatedAt"), label="generatedAt")
    plans = payload.get("plans")
    if not isinstance(plans, list) or not plans:
        raise ValueError(
            "optimizer runtime materialization plan must include a non-empty `plans` list"
        )
    seen_plan_ids: set[str] = set()
    seen_binding_ids: set[str] = set()
    seen_planner_pairs: set[tuple[str, str]] = set()
    for index, plan in enumerate(plans):
        label = f"optimizer runtime materialization plan plans[{index}]"
        if not isinstance(plan, dict):
            raise ValueError(f"{label} must be an object")
        plan_id = _require_string(plan.get("planId"), label=f"{label}.planId")
        if plan_id in seen_plan_ids:
            raise ValueError(
                f"optimizer runtime materialization plan contains duplicate planId {plan_id!r}"
            )
        seen_plan_ids.add(plan_id)
        output_binding_id = _require_string(
            plan.get("outputBindingId"), label=f"{label}.outputBindingId"
        )
        if output_binding_id in seen_binding_ids:
            raise ValueError(
                "optimizer runtime materialization plan contains duplicate "
                f"outputBindingId {output_binding_id!r}"
            )
        seen_binding_ids.add(output_binding_id)
        job_family_group = _require_string(
            plan.get("jobFamilyGroup"), label=f"{label}.jobFamilyGroup"
        )
        materialization_profile = _require_string(
            plan.get("materializationProfile"),
            label=f"{label}.materializationProfile",
        )
        planner_pair = (job_family_group, materialization_profile)
        if planner_pair in seen_planner_pairs:
            raise ValueError(
                "optimizer runtime materialization plan contains duplicate "
                f"jobFamilyGroup/materializationProfile pair {planner_pair!r}"
            )
        seen_planner_pairs.add(planner_pair)
        _require_string(plan.get("sourceClass"), label=f"{label}.sourceClass")
        _require_string(plan.get("sourceVariant"), label=f"{label}.sourceVariant")
        strategy = _require_string(
            plan.get("materializationStrategy"),
            label=f"{label}.materializationStrategy",
        )
        if strategy not in MATERIALIZATION_STRATEGIES:
            allowed = ", ".join(MATERIALIZATION_STRATEGIES)
            raise ValueError(
                f"{label}.materializationStrategy must be one of [{allowed}], got {strategy!r}"
            )
        for list_key in ("upstreamJobFamilies", "requiredArtifactKinds"):
            values = plan.get(list_key)
            if not isinstance(values, list):
                raise ValueError(f"{label}.{list_key} must be a list")
            for value_index, value in enumerate(values):
                _require_string(
                    value, label=f"{label}.{list_key}[{value_index}]"
                )
        include_weekly_promotion = plan.get("includeWeeklyPromotion")
        if include_weekly_promotion is not None and not isinstance(
            include_weekly_promotion, bool
        ):
            raise ValueError(
                f"{label}.includeWeeklyPromotion must be a boolean when present"
            )
