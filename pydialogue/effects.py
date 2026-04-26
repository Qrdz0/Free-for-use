from __future__ import annotations

from typing import Any


def _ensure_set(value: Any) -> set[Any]:
    if isinstance(value, set):
        return value
    if value is None:
        return set()
    if isinstance(value, list):
        return set(value)
    raise ValueError(f"Expected set-compatible value, got: {type(value)!r}")


def apply_effect(effect: dict[str, Any], game_state: dict[str, Any]) -> None:
    """Apply one effect object to the game state in-place."""
    effect_type = effect.get("type")
    if not effect_type:
        raise ValueError("Effect is missing required field: type")

    if effect_type == "set":
        variable = effect.get("variable")
        game_state[variable] = effect.get("value")
        return

    if effect_type == "add":
        variable = effect.get("variable")
        amount = effect.get("value", 0)
        game_state[variable] = game_state.get(variable, 0) + amount
        return

    if effect_type == "add_item":
        items = _ensure_set(game_state.get("items"))
        items.add(effect.get("item"))
        game_state["items"] = items
        return

    if effect_type == "remove_item":
        items = _ensure_set(game_state.get("items"))
        items.discard(effect.get("item"))
        game_state["items"] = items
        return

    if effect_type == "start_quest":
        active = _ensure_set(game_state.get("active_quests"))
        active.add(effect.get("quest"))
        game_state["active_quests"] = active
        return

    if effect_type == "complete_quest":
        quest = effect.get("quest")
        active = _ensure_set(game_state.get("active_quests"))
        completed = _ensure_set(game_state.get("completed_quests"))
        active.discard(quest)
        completed.add(quest)
        game_state["active_quests"] = active
        game_state["completed_quests"] = completed
        return

    if effect_type == "end_conversation":
        game_state["conversation_ended"] = True
        return

    raise ValueError(f"Unknown effect type: {effect_type}")


def apply_effects(effects: list[dict[str, Any]] | None, game_state: dict[str, Any]) -> None:
    """Apply effect objects in sequence."""
    if not effects:
        return
    for effect in effects:
        apply_effect(effect, game_state)
