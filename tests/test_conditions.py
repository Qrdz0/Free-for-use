from pydialogue.conditions import conditions_pass, evaluate_condition


def test_numeric_conditions() -> None:
    state = {"reputation": 3}
    assert evaluate_condition({"type": "greater_than", "variable": "reputation", "value": 2}, state)
    assert evaluate_condition({"type": "less_than", "variable": "reputation", "value": 10}, state)
    assert evaluate_condition({"type": "equals", "variable": "reputation", "value": 3}, state)
    assert evaluate_condition({"type": "not_equals", "variable": "reputation", "value": 0}, state)


def test_inventory_and_quest_conditions() -> None:
    state = {
        "items": {"city_pass"},
        "active_quests": {"sick_child"},
        "completed_quests": {"rat_problem"},
    }
    assert evaluate_condition({"type": "has_item", "item": "city_pass"}, state)
    assert evaluate_condition({"type": "quest_active", "quest": "sick_child"}, state)
    assert evaluate_condition({"type": "quest_completed", "quest": "rat_problem"}, state)


def test_conditions_pass_all() -> None:
    state = {"reputation": 5}
    assert conditions_pass(
        [
            {"type": "greater_than", "variable": "reputation", "value": 2},
            {"type": "less_than", "variable": "reputation", "value": 10},
        ],
        state,
    )
