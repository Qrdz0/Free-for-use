from __future__ import annotations

from typing import Any


def evaluate_condition(condition: dict[str, Any], game_state: dict[str, Any]) -> bool:
    """Evaluate one condition object against the game state."""
    condition_type = condition.get("type")
    if not condition_type:
        raise ValueError("Condition is missing required field: type")

    if condition_type == "equals":
        variable = condition.get("variable")
        expected = condition.get("value")
        return game_state.get(variable) == expected

    if condition_type == "not_equals":
        variable = condition.get("variable")
        expected = condition.get("value")
        return game_state.get(variable) != expected

    if condition_type == "greater_than":
        variable = condition.get("variable")
        expected = condition.get("value")
        return game_state.get(variable, 0) > expected

    if condition_type == "less_than":
        variable = condition.get("variable")
        expected = condition.get("value")
        return game_state.get(variable, 0) < expected

    if condition_type == "has_item":
        item = condition.get("item")
        return item in game_state.get("items", set())

    if condition_type == "quest_active":
        quest = condition.get("quest")
        return quest in game_state.get("active_quests", set())

    if condition_type == "quest_completed":
        quest = condition.get("quest")
        return quest in game_state.get("completed_quests", set())

    raise ValueError(f"Unknown condition type: {condition_type}")


def conditions_pass(conditions: list[dict[str, Any]] | None, game_state: dict[str, Any]) -> bool:
    """Return True only when all conditions pass."""
    if not conditions:
        return True
    return all(evaluate_condition(condition, game_state) for condition in conditions)
