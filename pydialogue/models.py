from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Choice:
    """A player-facing option from a dialogue node."""

    text: str
    next_node: str | None = None
    conditions: list[dict[str, Any]] = field(default_factory=list)
    effects: list[dict[str, Any]] = field(default_factory=list)
    end_conversation: bool = False


@dataclass(slots=True)
class DialogueNode:
    """A single dialogue node containing speaker text and choices."""

    node_id: str
    speaker: str
    text: str
    choices: list[Choice] = field(default_factory=list)


@dataclass(slots=True)
class DialogueData:
    """Parsed dialogue data loaded from JSON."""

    start_node: str
    nodes: dict[str, DialogueNode]
