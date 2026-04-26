from __future__ import annotations

from typing import Any

VALID_CONDITION_TYPES = {
    "equals",
    "not_equals",
    "greater_than",
    "less_than",
    "has_item",
    "quest_active",
    "quest_completed",
}

VALID_EFFECT_TYPES = {
    "set",
    "add",
    "add_item",
    "remove_item",
    "start_quest",
    "complete_quest",
    "end_conversation",
}


class DialogueValidationError(ValueError):
    """Raised when dialogue JSON fails validation."""


def validate_dialogue_data(data: dict[str, Any]) -> None:
    """Validate top-level dialogue data and all nodes/choices."""
    start_node = data.get("start_node")
    nodes = data.get("nodes")

    if not start_node:
        raise DialogueValidationError("Missing required field: start_node")
    if not isinstance(nodes, dict) or not nodes:
        raise DialogueValidationError("Missing or invalid required field: nodes")
    if start_node not in nodes:
        raise DialogueValidationError(f"Start node '{start_node}' not found in nodes")

    for node_id, node_data in nodes.items():
        _validate_node(node_id, node_data)

    for node_id, node_data in nodes.items():
        for index, choice in enumerate(node_data.get("choices", [])):
            next_node = choice.get("next")
            if next_node is not None and next_node not in nodes:
                raise DialogueValidationError(
                    f"Node '{node_id}' choice {index} points to missing node '{next_node}'"
                )


def _validate_node(node_id: str, node_data: Any) -> None:
    if not isinstance(node_data, dict):
        raise DialogueValidationError(f"Node '{node_id}' must be an object")

    for field_name in ("speaker", "text", "choices"):
        if field_name not in node_data:
            raise DialogueValidationError(f"Node '{node_id}' is missing field '{field_name}'")

    if not isinstance(node_data["choices"], list):
        raise DialogueValidationError(f"Node '{node_id}' field 'choices' must be a list")

    for index, choice in enumerate(node_data["choices"]):
        _validate_choice(node_id, index, choice)


def _validate_choice(node_id: str, index: int, choice: Any) -> None:
    if not isinstance(choice, dict):
        raise DialogueValidationError(f"Node '{node_id}' choice {index} must be an object")

    if "text" not in choice:
        raise DialogueValidationError(f"Node '{node_id}' choice {index} is missing field 'text'")

    if "next" not in choice and not choice.get("end_conversation"):
        raise DialogueValidationError(
            f"Node '{node_id}' choice {index} must define 'next' or set 'end_conversation'"
        )

    for condition in choice.get("conditions", []):
        _validate_condition(condition)

    effects = choice.get("effects")
    if isinstance(effects, dict):
        effects = _normalize_legacy_effects(effects)
    for effect in effects or []:
        _validate_effect(effect)


def _validate_condition(condition: Any) -> None:
    if not isinstance(condition, dict):
        raise DialogueValidationError("Condition must be an object")

    condition_type = condition.get("type")
    if condition_type not in VALID_CONDITION_TYPES:
        raise DialogueValidationError(f"Invalid condition type: {condition_type}")


def _validate_effect(effect: Any) -> None:
    if not isinstance(effect, dict):
        raise DialogueValidationError("Effect must be an object")

    effect_type = effect.get("type")
    if effect_type not in VALID_EFFECT_TYPES:
        raise DialogueValidationError(f"Invalid effect type: {effect_type}")


def _normalize_legacy_effects(effects: dict[str, Any]) -> list[dict[str, Any]]:
    """Allow shorthand effects style: {"reputation": 1}."""
    normalized: list[dict[str, Any]] = []
    for variable, value in effects.items():
        if isinstance(value, bool):
            normalized.append({"type": "set", "variable": variable, "value": value})
        elif isinstance(value, (int, float)):
            normalized.append({"type": "add", "variable": variable, "value": value})
        else:
            normalized.append({"type": "set", "variable": variable, "value": value})
    return normalized


def normalize_effects(effects: list[dict[str, Any]] | dict[str, Any] | None) -> list[dict[str, Any]]:
    """Normalize effect structure into list of typed effect objects."""
    if effects is None:
        return []
    if isinstance(effects, list):
        return effects
    if isinstance(effects, dict):
        return _normalize_legacy_effects(effects)
    raise DialogueValidationError("Effects must be either a list or an object")
