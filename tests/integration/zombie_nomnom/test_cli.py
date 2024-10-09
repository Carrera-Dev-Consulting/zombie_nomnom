from click.testing import CliRunner
import pytest

from zombie_nomnom.app import main


@pytest.fixture
def runner():
    return CliRunner()


def test_app__when_user_types_name__prints_name_to_screen(runner: CliRunner):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """milo

    0
    """
    result = runner.invoke(main, args=["cli"], input=cli_input)
    assert "Players: milo" in result.output


def test_app__when_replaying_game__setups_game_again(runner: CliRunner):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """milo

    0
    y
    milo
    
    0
    n
    """
    result = runner.invoke(main, args=["cli"], input=cli_input)
    assert "Players: milo" in result.output


def test_app__when_setting_up__allows_multiple_players(runner: CliRunner):
    # this works by putting in the name of the player then new line to tell it to no more players then zero
    # to select exit option and then final new line to not continue
    cli_input = """milo
y
Dean

    0
    """
    result = runner.invoke(main, args=["cli"], input=cli_input)
    assert "Players: milo" in result.output
    assert "Dean (0)" in result.output
