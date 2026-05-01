#!/usr/bin/env python3
"""
Helpers for scheduler-facing optimizer input rollout policies.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION = (
    "optimizer-input-rollout-policy.sample.v1"
)
OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSION = "optimizer-input-rollout-policy.v1"
OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSIONS = {
    OPTIMIZER_INPUT_ROLLOUT_POLICY_SAMPLE_SCHEMA_VERSION,
    OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSION,
}
OPTIMIZER_INPUT_ROLLOUT_SELECTION_SOURCES = {
    "explicit",
    "policy_schedule_default",
    "policy_global_default",
}
OPTIMIZER_INPUT_ROLLOUT_INTENT_SELECTION_SOURCES = {
    "explicit_rollout_class",
    "explicit_rollout_intent",
    "policy_schedule_default",
    "policy_global_default",
}
OPTIMIZER_INPUT_ROLLOUT_CLASS_SELECTION_SOURCES = {
    "explicit_rollout_class",
    "mapped_from_explicit_rollout_intent",
    "mapped_from_schedule_rollout_intent_default",
    "mapped_from_global_rollout_intent_default",
}
OPTIMIZER_INPUT_ROLLOUT_PRECEDENCE_STEPS = {
    "explicit_rollout_class",
    "explicit_rollout_intent",
    "schedule_rollout_intent_default",
    "global_rollout_intent_default",
}

DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_ID = (
    "optimizer-input-rollout-policy.autotiktok.fixture.2026-04-18"
)
DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_FAMILY = "autotiktok-optimizer-input-rollout"
DEFAULT_OPTIMIZER_INPUT_ROLLOUT_POLICY_VERSION = "2026-04-18"
DEFAULT_OPTIMIZER_INPUT_ROLLOUT_STRATEGY = "shadow_lane_progression"

DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS = "production"
RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS = "raw_shadow_validation"
REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS = "real_shadow_validation"

DEFAULT_OPTIMIZER_INPUT_ROLLOUT_INTENT = "production_run"
RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_INTENT = "raw_shadow_validation"
REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_INTENT = "real_provider_shadow_validation"

DEFAULT_OPTIMIZER_INPUT_SOURCE_LANE = "sample_canonical"
RAW_SHADOW_OPTIMIZER_INPUT_SOURCE_LANE = "sample_raw_shadow"
REAL_SHADOW_OPTIMIZER_INPUT_SOURCE_LANE = "real_provider_shadow"

DEFAULT_OPTIMIZER_INPUT_ROLLOUT_PRECEDENCE = [
    "explicit_rollout_class",
    "explicit_rollout_intent",
    "schedule_rollout_intent_default",
    "global_rollout_intent_default",
]


def _require_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def build_optimizer_input_rollout_class_entry(
    *, rollout_class: str, source_lane: str
) -> dict[str, str]:
    return {
        "rolloutClass": rollout_class,
        "sourceLane": source_lane,
    }


def build_optimizer_input_rollout_intent_entry(
    *, rollout_intent: str, rollout_class: str
) -> dict[str, str]:
    return {
        "rolloutIntent": rollout_intent,
        "rolloutClass": rollout_class,
    }


def build_optimizer_input_rollout_schedule_policy_entry(
    *,
    schedule_id: str,
    default_rollout_intent: str,
    allowed_rollout_intents: list[str],
    default_rollout_class: str,
    allowed_rollout_classes: list[str],
) -> dict[str, Any]:
    return {
        "scheduleId": schedule_id,
        "defaultRolloutIntent": default_rollout_intent,
        "allowedRolloutIntents": list(allowed_rollout_intents),
        "defaultRolloutClass": default_rollout_class,
        "allowedRolloutClasses": list(allowed_rollout_classes),
    }


def build_default_optimizer_input_rollout_classes() -> list[dict[str, str]]:
    return [
        build_optimizer_input_rollout_class_entry(
            rollout_class=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS,
            source_lane=DEFAULT_OPTIMIZER_INPUT_SOURCE_LANE,
        ),
        build_optimizer_input_rollout_class_entry(
            rollout_class=RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS,
            source_lane=RAW_SHADOW_OPTIMIZER_INPUT_SOURCE_LANE,
        ),
        build_optimizer_input_rollout_class_entry(
            rollout_class=REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS,
            source_lane=REAL_SHADOW_OPTIMIZER_INPUT_SOURCE_LANE,
        ),
    ]


def build_default_optimizer_input_rollout_intents() -> list[dict[str, str]]:
    return [
        build_optimizer_input_rollout_intent_entry(
            rollout_intent=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_INTENT,
            rollout_class=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS,
        ),
        build_optimizer_input_rollout_intent_entry(
            rollout_intent=RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_INTENT,
            rollout_class=RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS,
        ),
        build_optimizer_input_rollout_intent_entry(
            rollout_intent=REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_INTENT,
            rollout_class=REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS,
        ),
    ]


def build_default_optimizer_input_rollout_schedule_policies() -> list[dict[str, Any]]:
    allowed_rollout_classes = [
        DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS,
        RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS,
        REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_CLASS,
    ]
    allowed_rollout_intents = [
        DEFAULT_OPTIMIZER_INPUT_ROLLOUT_INTENT,
        RAW_SHADOW_OPTIMIZER_INPUT_ROLLOUT_INTENT,
        REAL_SHADOW_OPTIMIZER_INPUT_ROLLOUT_INTENT,
    ]
    return [
        build_optimizer_input_rollout_schedule_policy_entry(
            schedule_id="daily_optimizer_job",
            default_rollout_intent=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_INTENT,
            allowed_rollout_intents=allowed_rollout_intents,
            default_rollout_class=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS,
            allowed_rollout_classes=allowed_rollout_classes,
        ),
        build_optimizer_input_rollout_schedule_policy_entry(
            schedule_id="weekly_optimizer_job",
            default_rollout_intent=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_INTENT,
            allowed_rollout_intents=allowed_rollout_intents,
            default_rollout_class=DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS,
            allowed_rollout_classes=allowed_rollout_classes,
        ),
    ]


def build_optimizer_input_rollout_policy_payload(
    *,
    policy_id: str,
    schema_version: str,
    policy_family: str,
    policy_version: str,
    generated_at: str,
    input_source_registry_reference: dict[str, Any],
    rollout_classes: list[dict[str, Any]],
    rollout_intents: list[dict[str, Any]],
    schedule_policies: list[dict[str, Any]],
    default_rollout_intent: str = DEFAULT_OPTIMIZER_INPUT_ROLLOUT_INTENT,
    default_rollout_class: str = DEFAULT_OPTIMIZER_INPUT_ROLLOUT_CLASS,
    rollout_strategy: str = DEFAULT_OPTIMIZER_INPUT_ROLLOUT_STRATEGY,
    rollout_selection_precedence: list[str] | None = None,
) -> dict[str, Any]:
    effective_rollout_selection_precedence = (
        list(rollout_selection_precedence)
        if rollout_selection_precedence is not None
        else list(DEFAULT_OPTIMIZER_INPUT_ROLLOUT_PRECEDENCE)
    )
    return {
        "schemaVersion": schema_version,
        "policyId": policy_id,
        "policyFamily": policy_family,
        "policyVersion": policy_version,
        "generatedAt": generated_at,
        "generatedFrom": {
            "optimizerInputSourceRegistrySchemaVersion": input_source_registry_reference.get(
                "schemaVersion"
            ),
            "optimizerInputSourceRegistryId": input_source_registry_reference.get(
                "registryId"
            ),
            "optimizerInputSourceRegistryPath": input_source_registry_reference.get(
                "path"
            ),
            "rolloutClassCount": len(rollout_classes),
            "rolloutIntentCount": len(rollout_intents),
            "schedulePolicyCount": len(schedule_policies),
            "rolloutSelectionPrecedenceCount": len(
                effective_rollout_selection_precedence
            ),
        },
        "defaultRolloutIntent": default_rollout_intent,
        "defaultRolloutClass": default_rollout_class,
        "rolloutStrategy": rollout_strategy,
        "rolloutSelectionPrecedence": effective_rollout_selection_precedence,
        "inputSourceRegistryReference": dict(input_source_registry_reference),
        "rolloutClasses": rollout_classes,
        "rolloutIntents": rollout_intents,
        "schedulePolicies": schedule_policies,
    }


def validate_optimizer_input_rollout_policy_payload(payload: dict[str, Any]) -> None:
    schema_version = payload.get("schemaVersion")
    if schema_version not in OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(OPTIMIZER_INPUT_ROLLOUT_POLICY_SCHEMA_VERSIONS))
        raise ValueError(
            f"optimizer input rollout policy schemaVersion must be one of [{allowed}], "
            f"got {schema_version!r}"
        )
    for field_name in ("policyId", "policyFamily", "policyVersion", "generatedAt"):
        _require_string(payload.get(field_name), label=field_name)
    _require_string(
        payload.get("defaultRolloutIntent"), label="defaultRolloutIntent"
    )
    _require_string(
        payload.get("defaultRolloutClass"), label="defaultRolloutClass"
    )
    _require_string(payload.get("rolloutStrategy"), label="rolloutStrategy")
    registry_reference = payload.get("inputSourceRegistryReference")
    if not isinstance(registry_reference, dict):
        raise ValueError(
            "optimizer input rollout policy must declare inputSourceRegistryReference"
        )
    for field_name in ("schemaVersion", "registryId", "path"):
        _require_string(
            registry_reference.get(field_name),
            label=f"inputSourceRegistryReference.{field_name}",
        )

    rollout_classes = payload.get("rolloutClasses")
    if not isinstance(rollout_classes, list) or not rollout_classes:
        raise ValueError(
            "optimizer input rollout policy must declare a non-empty rolloutClasses list"
        )
    seen_classes: set[str] = set()
    seen_source_lanes: set[str] = set()
    for index, entry in enumerate(rollout_classes):
        if not isinstance(entry, dict):
            raise ValueError(
                f"optimizer input rollout policy rolloutClasses[{index}] must be an object"
            )
        rollout_class = _require_string(
            entry.get("rolloutClass"),
            label=f"rolloutClasses[{index}].rolloutClass",
        )
        source_lane = _require_string(
            entry.get("sourceLane"),
            label=f"rolloutClasses[{index}].sourceLane",
        )
        if rollout_class in seen_classes:
            raise ValueError(
                f"duplicate optimizer input rolloutClass {rollout_class!r}"
            )
        if source_lane in seen_source_lanes:
            raise ValueError(
                f"duplicate optimizer input sourceLane mapping {source_lane!r}"
            )
        seen_classes.add(rollout_class)
        seen_source_lanes.add(source_lane)

    rollout_intents = payload.get("rolloutIntents")
    if not isinstance(rollout_intents, list) or not rollout_intents:
        raise ValueError(
            "optimizer input rollout policy must declare a non-empty rolloutIntents list"
        )
    seen_intents: set[str] = set()
    intent_to_class: dict[str, str] = {}
    class_to_intent: dict[str, str] = {}
    for index, entry in enumerate(rollout_intents):
        if not isinstance(entry, dict):
            raise ValueError(
                f"optimizer input rollout policy rolloutIntents[{index}] must be an object"
            )
        rollout_intent = _require_string(
            entry.get("rolloutIntent"),
            label=f"rolloutIntents[{index}].rolloutIntent",
        )
        rollout_class = _require_string(
            entry.get("rolloutClass"),
            label=f"rolloutIntents[{index}].rolloutClass",
        )
        if rollout_intent in seen_intents:
            raise ValueError(
                f"duplicate optimizer input rolloutIntent {rollout_intent!r}"
            )
        if rollout_class not in seen_classes:
            raise ValueError(
                f"rolloutIntents[{index}] references unknown rolloutClass {rollout_class!r}"
            )
        if rollout_class in class_to_intent:
            raise ValueError(
                f"duplicate optimizer input rolloutClass-to-intent mapping {rollout_class!r}"
            )
        seen_intents.add(rollout_intent)
        intent_to_class[rollout_intent] = rollout_class
        class_to_intent[rollout_class] = rollout_intent

    rollout_selection_precedence = payload.get("rolloutSelectionPrecedence")
    if (
        not isinstance(rollout_selection_precedence, list)
        or not rollout_selection_precedence
    ):
        raise ValueError(
            "optimizer input rollout policy must declare a non-empty rolloutSelectionPrecedence list"
        )
    normalized_precedence: set[str] = set()
    for index, precedence_step in enumerate(rollout_selection_precedence):
        _require_string(
            precedence_step,
            label=f"rolloutSelectionPrecedence[{index}]",
        )
        if precedence_step not in OPTIMIZER_INPUT_ROLLOUT_PRECEDENCE_STEPS:
            raise ValueError(
                f"unsupported optimizer input rollout precedence step {precedence_step!r}"
            )
        normalized_precedence.add(precedence_step)
    if normalized_precedence != OPTIMIZER_INPUT_ROLLOUT_PRECEDENCE_STEPS:
        raise ValueError(
            "optimizer input rollout policy rolloutSelectionPrecedence must cover every supported precedence step"
        )

    if payload["defaultRolloutIntent"] not in seen_intents:
        raise ValueError(
            "optimizer input rollout policy defaultRolloutIntent must exist in rolloutIntents"
        )
    if payload["defaultRolloutClass"] not in seen_classes:
        raise ValueError(
            "optimizer input rollout policy defaultRolloutClass must exist in rolloutClasses"
        )
    if intent_to_class[payload["defaultRolloutIntent"]] != payload["defaultRolloutClass"]:
        raise ValueError(
            "optimizer input rollout policy defaultRolloutIntent must map to defaultRolloutClass"
        )

    schedule_policies = payload.get("schedulePolicies")
    if not isinstance(schedule_policies, list) or not schedule_policies:
        raise ValueError(
            "optimizer input rollout policy must declare a non-empty schedulePolicies list"
        )
    generated_from = payload.get("generatedFrom")
    if not isinstance(generated_from, dict):
        raise ValueError(
            "optimizer input rollout policy must declare generatedFrom metadata"
        )
    if generated_from.get("rolloutClassCount") != len(rollout_classes):
        raise ValueError(
            "optimizer input rollout policy rolloutClassCount mismatch"
        )
    if generated_from.get("rolloutIntentCount") != len(rollout_intents):
        raise ValueError(
            "optimizer input rollout policy rolloutIntentCount mismatch"
        )
    if generated_from.get("schedulePolicyCount") != len(schedule_policies):
        raise ValueError(
            "optimizer input rollout policy schedulePolicyCount mismatch"
        )
    if generated_from.get("rolloutSelectionPrecedenceCount") != len(
        rollout_selection_precedence
    ):
        raise ValueError(
            "optimizer input rollout policy rolloutSelectionPrecedenceCount mismatch"
        )

    seen_schedule_ids: set[str] = set()
    for index, entry in enumerate(schedule_policies):
        if not isinstance(entry, dict):
            raise ValueError(
                f"optimizer input rollout policy schedulePolicies[{index}] must be an object"
            )
        schedule_id = _require_string(
            entry.get("scheduleId"),
            label=f"schedulePolicies[{index}].scheduleId",
        )
        if schedule_id in seen_schedule_ids:
            raise ValueError(
                f"duplicate optimizer input rollout scheduleId {schedule_id!r}"
            )
        seen_schedule_ids.add(schedule_id)
        default_rollout_intent = _require_string(
            entry.get("defaultRolloutIntent"),
            label=f"schedulePolicies[{index}].defaultRolloutIntent",
        )
        if default_rollout_intent not in seen_intents:
            raise ValueError(
                f"schedulePolicies[{index}].defaultRolloutIntent {default_rollout_intent!r} "
                "must exist in rolloutIntents"
            )
        allowed_rollout_intents = entry.get("allowedRolloutIntents")
        if not isinstance(allowed_rollout_intents, list) or not allowed_rollout_intents:
            raise ValueError(
                f"schedulePolicies[{index}].allowedRolloutIntents must be a non-empty list"
            )
        normalized_allowed_intents: set[str] = set()
        for allowed_index, allowed_intent in enumerate(allowed_rollout_intents):
            _require_string(
                allowed_intent,
                label=(
                    "schedulePolicies"
                    f"[{index}].allowedRolloutIntents[{allowed_index}]"
                ),
            )
            if allowed_intent not in seen_intents:
                raise ValueError(
                    f"schedulePolicies[{index}] references unknown rolloutIntent "
                    f"{allowed_intent!r}"
                )
            normalized_allowed_intents.add(allowed_intent)
        if default_rollout_intent not in normalized_allowed_intents:
            raise ValueError(
                f"schedulePolicies[{index}] defaultRolloutIntent must be allowed"
            )
        default_rollout_class = _require_string(
            entry.get("defaultRolloutClass"),
            label=f"schedulePolicies[{index}].defaultRolloutClass",
        )
        if default_rollout_class not in seen_classes:
            raise ValueError(
                f"schedulePolicies[{index}].defaultRolloutClass {default_rollout_class!r} "
                "must exist in rolloutClasses"
            )
        allowed_rollout_classes = entry.get("allowedRolloutClasses")
        if not isinstance(allowed_rollout_classes, list) or not allowed_rollout_classes:
            raise ValueError(
                f"schedulePolicies[{index}].allowedRolloutClasses must be a non-empty list"
            )
        normalized_allowed: set[str] = set()
        for allowed_index, allowed_class in enumerate(allowed_rollout_classes):
            _require_string(
                allowed_class,
                label=(
                    "schedulePolicies"
                    f"[{index}].allowedRolloutClasses[{allowed_index}]"
                ),
            )
            if allowed_class not in seen_classes:
                raise ValueError(
                    f"schedulePolicies[{index}] references unknown rolloutClass "
                    f"{allowed_class!r}"
                )
            normalized_allowed.add(allowed_class)
        if default_rollout_class not in normalized_allowed:
            raise ValueError(
                f"schedulePolicies[{index}] defaultRolloutClass must be allowed"
            )
        mapped_allowed_classes = {
            intent_to_class[allowed_intent]
            for allowed_intent in normalized_allowed_intents
        }
        if normalized_allowed != mapped_allowed_classes:
            raise ValueError(
                f"schedulePolicies[{index}] allowedRolloutClasses must match allowedRolloutIntents"
            )
        if intent_to_class[default_rollout_intent] != default_rollout_class:
            raise ValueError(
                f"schedulePolicies[{index}] defaultRolloutIntent must map to defaultRolloutClass"
            )


def load_optimizer_input_rollout_policy(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"optimizer input rollout policy not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"optimizer input rollout policy is not valid JSON: {path}"
        ) from exc
    validate_optimizer_input_rollout_policy_payload(payload)
    return payload


def resolve_optimizer_input_rollout_selection(
    payload: dict[str, Any],
    *,
    schedule_id: str | None = None,
    explicit_rollout_class: str | None = None,
    explicit_rollout_intent: str | None = None,
) -> dict[str, str]:
    validate_optimizer_input_rollout_policy_payload(payload)
    if explicit_rollout_class is not None and explicit_rollout_intent is not None:
        raise ValueError(
            "optimizer input rollout selection cannot specify both explicit_rollout_class and explicit_rollout_intent"
        )
    rollout_classes = {
        entry["rolloutClass"]: entry
        for entry in payload["rolloutClasses"]
    }
    rollout_intents = {
        entry["rolloutIntent"]: entry
        for entry in payload["rolloutIntents"]
    }
    class_to_intent = {
        entry["rolloutClass"]: entry["rolloutIntent"]
        for entry in payload["rolloutIntents"]
    }
    schedule_policies = {
        entry["scheduleId"]: entry
        for entry in payload["schedulePolicies"]
    }

    if explicit_rollout_class is not None:
        if schedule_id is not None:
            schedule_policy = schedule_policies.get(schedule_id)
            if schedule_policy is None:
                raise ValueError(
                    f"optimizer input rollout scheduleId not found: {schedule_id}"
                )
            if explicit_rollout_class not in schedule_policy["allowedRolloutClasses"]:
                raise ValueError(
                    f"optimizer input rolloutClass {explicit_rollout_class!r} is not "
                    f"allowed for scheduleId {schedule_id!r}"
                )
        rollout_class = explicit_rollout_class
        rollout_intent = class_to_intent.get(rollout_class)
        if rollout_intent is None:
            raise ValueError(
                f"optimizer input rolloutClass is not mapped to a rolloutIntent: {rollout_class!r}"
            )
        selection_source = "explicit"
        rollout_intent_selection_source = "explicit_rollout_class"
        rollout_class_selection_source = "explicit_rollout_class"
    elif explicit_rollout_intent is not None:
        if explicit_rollout_intent not in rollout_intents:
            raise ValueError(
                f"optimizer input rolloutIntent not found: {explicit_rollout_intent!r}"
            )
        if schedule_id is not None:
            schedule_policy = schedule_policies.get(schedule_id)
            if schedule_policy is None:
                raise ValueError(
                    f"optimizer input rollout scheduleId not found: {schedule_id}"
                )
            if explicit_rollout_intent not in schedule_policy["allowedRolloutIntents"]:
                raise ValueError(
                    f"optimizer input rolloutIntent {explicit_rollout_intent!r} is not "
                    f"allowed for scheduleId {schedule_id!r}"
                )
        rollout_intent = explicit_rollout_intent
        rollout_class = rollout_intents[rollout_intent]["rolloutClass"]
        selection_source = "explicit"
        rollout_intent_selection_source = "explicit_rollout_intent"
        rollout_class_selection_source = "mapped_from_explicit_rollout_intent"
    elif schedule_id is not None and schedule_id in schedule_policies:
        schedule_policy = schedule_policies[schedule_id]
        rollout_intent = schedule_policy["defaultRolloutIntent"]
        rollout_class = rollout_intents[rollout_intent]["rolloutClass"]
        selection_source = "policy_schedule_default"
        rollout_intent_selection_source = "policy_schedule_default"
        rollout_class_selection_source = "mapped_from_schedule_rollout_intent_default"
    else:
        rollout_intent = payload["defaultRolloutIntent"]
        rollout_class = rollout_intents[rollout_intent]["rolloutClass"]
        selection_source = "policy_global_default"
        rollout_intent_selection_source = "policy_global_default"
        rollout_class_selection_source = "mapped_from_global_rollout_intent_default"

    rollout_entry = rollout_classes.get(rollout_class)
    if rollout_entry is None:
        raise ValueError(
            f"optimizer input rolloutClass not found: {rollout_class!r}"
        )
    if selection_source not in OPTIMIZER_INPUT_ROLLOUT_SELECTION_SOURCES:
        raise ValueError(
            f"unsupported optimizer input rollout selection source {selection_source!r}"
        )
    if (
        rollout_intent_selection_source
        not in OPTIMIZER_INPUT_ROLLOUT_INTENT_SELECTION_SOURCES
    ):
        raise ValueError(
            "unsupported optimizer input rollout intent selection source "
            f"{rollout_intent_selection_source!r}"
        )
    if (
        rollout_class_selection_source
        not in OPTIMIZER_INPUT_ROLLOUT_CLASS_SELECTION_SOURCES
    ):
        raise ValueError(
            "unsupported optimizer input rollout class selection source "
            f"{rollout_class_selection_source!r}"
        )
    return {
        "rolloutIntent": rollout_intent,
        "rolloutClass": rollout_class,
        "sourceLane": rollout_entry["sourceLane"],
        "selectionSource": selection_source,
        "rolloutIntentSelectionSource": rollout_intent_selection_source,
        "rolloutClassSelectionSource": rollout_class_selection_source,
        "rolloutStrategy": payload["rolloutStrategy"],
    }
