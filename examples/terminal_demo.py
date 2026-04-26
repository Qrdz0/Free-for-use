from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydialogue import DialogueEngine


def main() -> None:
    dialogue_path = Path(__file__).with_name("guard_dialogue.json")
    engine = DialogueEngine(dialogue_path)

    game_state = {
        "has_key": False,
        "reputation": 0,
        "quest_started": False,
        "npc_trust": 0,
        "items": set(),
        "active_quests": set(),
        "completed_quests": set(),
    }

    engine.start("intro")

    print("=== PyDialogue Terminal Demo ===")
    print("You are speaking with the city guard.\n")

    while True:
        try:
            node = engine.get_current_node()
        except RuntimeError:
            break

        print(f"{node.speaker}: {node.text}\n")

        choices = engine.get_available_choices(game_state)
        if not choices:
            print("No available choices. Conversation ended.")
            break

        for idx, choice in enumerate(choices, start=1):
            print(f"{idx}. {choice.text}")

        selection = input("\nChoose an option: ").strip()
        if not selection.isdigit() or int(selection) < 1 or int(selection) > len(choices):
            print("Please enter a valid choice number.\n")
            continue

        engine.choose(int(selection) - 1, game_state)
        print("\n---\n")

    print("Conversation finished.")
    print("Final game state:")
    for key, value in game_state.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
