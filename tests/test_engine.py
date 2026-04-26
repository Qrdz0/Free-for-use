from pathlib import Path

from pydialogue.engine import DialogueEngine


def test_engine_loads_and_branches() -> None:
    engine = DialogueEngine(Path("examples/guard_dialogue.json"))
    state = {
        "reputation": 0,
        "npc_trust": 0,
        "items": set(),
        "active_quests": set(),
        "completed_quests": set(),
    }

    engine.start("intro")
    node = engine.get_current_node()
    assert node.node_id == "intro"

    available = engine.get_available_choices(state)
    assert len(available) == 2

    engine.choose(0, state)
    assert engine.get_current_node().node_id == "ask_reason"
    assert state["reputation"] == 1

    engine.choose(0, state)
    assert engine.get_current_node().node_id == "reward_pass"
    assert "city_pass" in state["items"]
    assert "sick_child" in state["active_quests"]


def test_end_conversation_returns_none() -> None:
    engine = DialogueEngine(Path("examples/tavern_dialogue.json"))
    state = {
        "items": set(),
        "active_quests": set(),
        "completed_quests": set(),
    }

    engine.start("welcome")
    result = engine.choose(1, state)
    assert result is None
