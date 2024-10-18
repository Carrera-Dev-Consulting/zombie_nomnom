from zombie_nomnom.engine.commands import DrawDice, Score
from zombie_nomnom.engine.serialization import format_command, parse_command_dict


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
