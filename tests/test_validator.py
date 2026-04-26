import pytest

from pydialogue.validator import DialogueValidationError, normalize_effects, validate_dialogue_data


def valid_dialogue() -> dict:
    return {
        "start_node": "intro",
        "nodes": {
            "intro": {
                "speaker": "Guard",
                "text": "Hello",
                "choices": [{"text": "Go", "next": "end"}],
            },
            "end": {
                "speaker": "Guard",
                "text": "Bye",
                "choices": [{"text": "Leave", "end_conversation": True}],
            },
        },
    }


def test_validator_accepts_valid_dialogue() -> None:
    validate_dialogue_data(valid_dialogue())


def test_validator_missing_start_node() -> None:
    data = valid_dialogue()
    data.pop("start_node")
    with pytest.raises(DialogueValidationError):
        validate_dialogue_data(data)


def test_validator_broken_next_link() -> None:
    data = valid_dialogue()
    data["nodes"]["intro"]["choices"][0]["next"] = "missing"
    with pytest.raises(DialogueValidationError):
        validate_dialogue_data(data)


def test_normalize_legacy_effects() -> None:
    effects = normalize_effects({"reputation": 1, "quest_started": True})
    assert {"type": "add", "variable": "reputation", "value": 1} in effects
    assert {"type": "set", "variable": "quest_started", "value": True} in effects
