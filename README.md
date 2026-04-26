# PyDialogue

PyDialogue is a reusable, beginner-friendly dialogue system for Python games.
It lets you build branching conversations with JSON files and run them in terminal games, pygame projects, RPGs, and visual novels.

## Features

- JSON-based dialogue authoring
- Branching choices with next-node routing
- Conditions (variables, inventory, quest checks)
- Effects (state updates, items, quests, conversation end)
- Dialogue file validation with clear errors
- Terminal demo included
- Typed, dataclass-based, easy-to-extend code

## Installation

### Local project clone

```bash
git clone <your-repo-url>
cd PyDialogue
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### Install test dependencies

```bash
pip install -e .[dev]
```

## Quick Start

```python
from pydialogue import DialogueEngine

engine = DialogueEngine("examples/guard_dialogue.json")
game_state = {
    "reputation": 0,
    "npc_trust": 0,
    "items": set(),
    "active_quests": set(),
    "completed_quests": set(),
}

engine.start("intro")

current = engine.get_current_node()
print(current.speaker, current.text)

choices = engine.get_available_choices(game_state)
for i, choice in enumerate(choices):
    print(i, choice.text)

engine.choose(0, game_state)
```

## JSON Dialogue Format

```json
{
  "start_node": "intro",
  "nodes": {
    "intro": {
      "speaker": "Guard",
      "text": "Halt! What business do you have here?",
      "choices": [
        {
          "text": "I need to enter the city.",
          "next": "ask_reason",
          "effects": {"reputation": 1}
        },
        {
          "text": "None of your business.",
          "next": "angry",
          "effects": {"reputation": -1}
        }
      ]
    }
  }
}
```

### Choice fields

Each choice supports:

- `text` (required): what the player sees
- `next` (optional if ending): next node ID
- `conditions` (optional): list of condition objects
- `effects` (optional): list of effect objects, or shorthand object for variable updates
- `end_conversation` (optional): `true` to end immediately

## Condition Examples

Supported condition types:

- `equals`
- `not_equals`
- `greater_than`
- `less_than`
- `has_item`
- `quest_active`
- `quest_completed`

```json
[
  {"type": "greater_than", "variable": "reputation", "value": 2},
  {"type": "has_item", "item": "city_pass"},
  {"type": "quest_completed", "quest": "rat_problem"}
]
```

## Effect Examples

Supported effect types:

- `set`
- `add`
- `add_item`
- `remove_item`
- `start_quest`
- `complete_quest`
- `end_conversation`

```json
[
  {"type": "add", "variable": "reputation", "value": 1},
  {"type": "add_item", "item": "city_pass"},
  {"type": "start_quest", "quest": "sick_child"}
]
```

Shorthand for simple variable updates is also supported:

```json
{"reputation": 1, "quest_started": true}
```

## Terminal Demo

Run the included guard conversation demo:

```bash
python examples/terminal_demo.py
```

It demonstrates:

- Branching choices
- Reputation and NPC trust updates
- Item rewards
- Quest start outcomes

## pygame Integration Example

```python
from pydialogue import DialogueEngine

engine = DialogueEngine("dialogues/guard.json")
state = {
    "reputation": 0,
    "items": set(),
    "active_quests": set(),
    "completed_quests": set(),
}
engine.start()

# In your game loop / dialogue UI:
node = engine.get_current_node()
render_text_box(f"{node.speaker}: {node.text}")
choices = engine.get_available_choices(state)
render_choice_buttons([c.text for c in choices])

# When player clicks a button:
selected_index = get_clicked_choice_index()
engine.choose(selected_index, state)
```

## Validation

PyDialogue validates files when loading:

- Missing `start_node`
- Broken `next` links
- Missing required node/choice fields
- Invalid condition formats
- Invalid effect formats

If invalid, a `DialogueValidationError` is raised with a clear message.

## Tests

```bash
pytest
```

## License

MIT License. See [LICENSE](LICENSE).
