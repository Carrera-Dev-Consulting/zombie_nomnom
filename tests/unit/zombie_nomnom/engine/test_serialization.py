import pytest

from zombie_nomnom.engine.models import Face
from zombie_nomnom.engine.commands import DrawDice, Score
from zombie_nomnom.engine.serialization import (
    format_command,
    parse_command_dict,
    format_to_json_dict,
    parse_game_json_dict,
    ZombieDieGame,
    ZombieDieGameDict,
    DieRecipe,
)


def test_format_command__when_formatting_known_command__uses_fully_qualified_name_for_class():
    command = Score()
    expected = {
        "cls": "zombie_nomnom.engine.commands.Score",
        "args": [],
        "kwargs": {},
    }
    actual = format_command(command)

    assert actual == expected


def test_format_command__when_formatting_command_with_args__puts_args_as_kwargs():
    command = DrawDice(amount_drawn=3)
    expected = {
        "cls": "zombie_nomnom.engine.commands.DrawDice",
        "args": [],
        "kwargs": {
            "amount_drawn": 3,
        },
    }
    actual = format_command(command)

    assert actual == expected


def test_parse_command_dict__when_parsing_will_load_class_and_initialize_correctly__loads_command_class():
    cmd_dict = {
        "cls": "zombie_nomnom.engine.commands.Score",
        "args": [],
        "kwargs": {},
    }

    actual = parse_command_dict(cmd_dict)

    assert isinstance(actual, Score)


def test_parse_command_dict__when_parsing_command_with_parameters_kwargs__loads_command_class():
    cmd_dict = {
        "cls": "zombie_nomnom.engine.commands.DrawDice",
        "args": [],
        "kwargs": {"amount_drawn": 3},
    }

    actual = parse_command_dict(cmd_dict)

    assert isinstance(actual, DrawDice)
    assert actual.amount_drawn == 3


def test_parse_command_dict__when_parsing_command_with_parameters_args__loads_command_class():
    cmd_dict = {
        "cls": "zombie_nomnom.engine.commands.DrawDice",
        "args": [3],
        "kwargs": {},
    }

    actual = parse_command_dict(cmd_dict)

    assert isinstance(actual, DrawDice)
    assert actual.amount_drawn == 3


def test_format_to_json_dict__when_bag_function_is_none_and_bag_recipes_is_empty__raises_value_error():
    with pytest.raises(ValueError):
        game = ZombieDieGame(players=["Player Uno"])
        format_to_json_dict(game)


def test_format_to_json_dict__when_bag_function_is_not_none_and_bag_recipes_exists__returns_valid_dict():
    game = ZombieDieGame(players=["Player Uno"])
    game.bag_recipes = [DieRecipe(faces=[Face.FOOT] * 6, amount=3)]
    game.bag_function = DrawDice(amount_drawn=3)

    game_dict = format_to_json_dict(game)
    assert game_dict
    assert isinstance(game_dict, dict)
    assert game_dict["bag_function"]
    assert game_dict["players"]


def test_parse_game_json_dict__when_given_valid_dict__returns_game_instance():
    expected = ZombieDieGame(players=["Player Uno"])
    expected.bag_recipes = [DieRecipe(faces=[Face.FOOT] * 6, amount=3)]
    expected.bag_function = DrawDice(amount_drawn=3)
    game_dict = format_to_json_dict(expected)
    result = parse_game_json_dict(game_dict)

    assert result
    assert result.bag_recipes == expected.bag_recipes
    assert result.players == expected.players
    assert result.score_threshold == expected.score_threshold
    assert result.round == expected.round


def test_parse_game_json_dict__when_bag_function_is_str_and_bag_function_is_not_standard_bag__raises_value_error():
    with pytest.raises(ValueError):
        expected = ZombieDieGame(players=["Player Uno"])
        expected.bag_recipes = [DieRecipe(faces=[Face.FOOT] * 6, amount=3)]
        expected.bag_function = "DrawDice"
        game_dict = format_to_json_dict(expected)
        game_dict["bag_function"] = "DrawDice"

        parse_game_json_dict(game_dict)
