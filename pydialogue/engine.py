from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydialogue.conditions import conditions_pass
from pydialogue.effects import apply_effects
from pydialogue.models import Choice, DialogueData, DialogueNode
from pydialogue.validator import normalize_effects, validate_dialogue_data


class DialogueEngine:
    """Loads dialogue JSON and drives runtime node/choice flow."""

    def __init__(self, dialogue_file: str | Path) -> None:
        self.dialogue_path = Path(dialogue_file)
        with self.dialogue_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)
        validate_dialogue_data(raw_data)
        self.dialogue = self._parse_dialogue(raw_data)
        self.current_node_id: str | None = None

    def start(self, start_node: str | None = None) -> None:
        """Start a conversation from a node or default start node."""
        node_id = start_node or self.dialogue.start_node
        if node_id not in self.dialogue.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        self.current_node_id = node_id

    def get_current_node(self) -> DialogueNode:
        """Return current node object."""
        if self.current_node_id is None:
            raise RuntimeError("Dialogue has not started. Call start() first.")
        return self.dialogue.nodes[self.current_node_id]

    def get_available_choices(self, game_state: dict[str, Any]) -> list[Choice]:
        """Return choices whose conditions pass for the current state."""
        node = self.get_current_node()
        return [
            choice
            for choice in node.choices
            if conditions_pass(choice.conditions, game_state)
        ]

    def choose(self, choice_index: int, game_state: dict[str, Any]) -> DialogueNode | None:
        """Apply selected choice effects and move to the next node."""
        choices = self.get_available_choices(game_state)
        if choice_index < 0 or choice_index >= len(choices):
            raise IndexError("Invalid choice index")

        selected = choices[choice_index]
        apply_effects(selected.effects, game_state)

        if selected.end_conversation or selected.next_node is None:
            self.current_node_id = None
            return None

        self.current_node_id = selected.next_node
        return self.get_current_node()

    @staticmethod
    def _parse_dialogue(raw_data: dict[str, Any]) -> DialogueData:
        nodes: dict[str, DialogueNode] = {}
        for node_id, node_data in raw_data["nodes"].items():
            choices: list[Choice] = []
            for choice_data in node_data["choices"]:
                choices.append(
                    Choice(
                        text=choice_data["text"],
                        next_node=choice_data.get("next"),
                        conditions=choice_data.get("conditions", []),
                        effects=normalize_effects(choice_data.get("effects")),
                        end_conversation=choice_data.get("end_conversation", False),
                    )
                )
            nodes[node_id] = DialogueNode(
                node_id=node_id,
                speaker=node_data["speaker"],
                text=node_data["text"],
                choices=choices,
            )

        return DialogueData(start_node=raw_data["start_node"], nodes=nodes)
