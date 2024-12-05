import json
import os
import tempfile
from typing import Callable
from click.testing import CliRunner, Result
import pytest

from zombie_nomnom.app import main
from zombie_nomnom.engine.game import ZombieDieGame
from zombie_nomnom.engine.serialization import format_to_json_dict


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def run_game_with_input(runner: CliRunner):
    def _run_with_input(cli_input: str = "") -> Result:
        return runner.invoke(main, args=["cli"], input=cli_input)

    return _run_with_input


def test_app__when_user_types_name__prints_name_to_screen(
    run_game_with_input: Callable[[str], Result]
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """1
    milo

    0
    """
    result = run_game_with_input(cli_input)
    assert "Players: milo" in result.output


def test_app__when_replaying_game__setups_game_again(
    run_game_with_input: Callable[[str], Result]
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """1
    milo

    0
    y
    1
    milo
    
    0
    n
    """
    result = run_game_with_input(cli_input)
    assert "Players: milo" in result.output


def test_app__when_setting_up__allows_multiple_players(
    run_game_with_input: Callable[[str], Result]
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """1
    milo
y
Dean

    0
    """
    result = run_game_with_input(cli_input)
    assert "Players: milo" in result.output
    assert "Dean (0)" in result.output


def test_app__when_playing_and_drawing_dice__dice_goes_down_by_3_for_first_draw(
    run_game_with_input: Callable[[str], Result]
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """1
    milo
    
    3
    3
    3
    3
    3
    0
    """
    result = run_game_with_input(cli_input)
    assert "Drawing dice..." in result.output, "Did not display drawing dice"
    assert "Dice Remaining: 10" in result.output, result.output


def test_app__when_playing_and_scoring_hand__scores_dice_and_transitions_turn(
    run_game_with_input: Callable[[str], Result]
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """1
    milo
    y
    dean
    n
    2
    0
    """
    result = run_game_with_input(cli_input)
    assert "Scoring hand..." in result.output, "Did not display scoring hand..."
    assert "Currently Playing dean" in result.output, "Did not display deans turn..."


def test_app__when_playing_and_scoring_hand__scores_dice_and_transitions_turn(
    run_game_with_input: Callable[[str], Result],
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """1
    milo
    y
    dean
    n
    2
    0
    """
    result = run_game_with_input(cli_input)
    assert "Scoring hand..." in result.output, "Did not display scoring hand..."
    assert "Currently Playing dean" in result.output, "Did not display deans turn..."


def test_app__when_playing_and_rolling_until_death__transitions_turn_to_other_player(
    run_game_with_input: Callable[[str], Result]
):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    all_the_rolls = "\n".join(["3"] * 26)
    cli_input = f"""1
    milo
    y
    dean

    {all_the_rolls}
    0
    """
    result = run_game_with_input(cli_input)
    assert "milo Has Died" in result.output, "He is a god gamer and survived."


@pytest.fixture
def tmp_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


def test_app__when_playing_save_game_writes_to_file(
    run_game_with_input: Callable[[str], Result],
    tmp_path: str,
):
    save_file_path = os.path.join(tmp_path, "test_save.json")
    result = run_game_with_input(
        f"""1
milo
y
dean

3
2
1
{save_file_path}
0
"""
    )
    assert result.exit_code == 0, result.output
    assert os.path.exists(save_file_path), "Save file was not created"


def test_app_when_playing_an_existing_game__loads_from_save_file(
    run_game_with_input: Callable[[str], Result],
    tmp_path: str,
):
    save_file_path = os.path.join(tmp_path, "test_save.json")
    with open(save_file_path, "w") as fp:
        json.dump(format_to_json_dict(ZombieDieGame(["Milo"])), fp)
    input_text = f"""2
{save_file_path}
3
0
"""

    result = run_game_with_input(input_text)
    assert result.exit_code == 0, result.output
    assert "Players: Milo" in result.output


def test_app__when_starting_game__can_immediately_exit(
    run_game_with_input: Callable[[str], Result],
):
    input_text = """0
"""

    result = run_game_with_input(input_text)
    assert result.exit_code == 0


def test_app__when_saving_on_existing_file__prompts_for_overwrite(
    run_game_with_input: Callable[[str], Result],
    tmp_path: str,
):
    save_file_path = os.path.join(tmp_path, "test_save.json")
    with open(save_file_path, "w") as fp:
        json.dump(format_to_json_dict(ZombieDieGame(["Milo"])), fp)

    input_text = f"""2
{save_file_path}
3
1
{save_file_path}
y
0
"""

    result = run_game_with_input(input_text)
    assert result.exit_code == 0
    assert "Overwrite existing file?" in result.output


def test_app__when_saving_on_existing_file__does_not_overwrite(
    run_game_with_input: Callable[[str], Result],
    tmp_path: str,
):
    save_file_path = os.path.join(tmp_path, "test_save.json")
    with open(save_file_path, "w") as fp:
        json.dump(format_to_json_dict(ZombieDieGame(["Milo"])), fp)

    input_text = f"""2
{save_file_path}
3
1
{save_file_path}
n
0
"""

    result = run_game_with_input(input_text)
    assert result.exit_code == 0
    assert "Overwrite existing file?" in result.output
