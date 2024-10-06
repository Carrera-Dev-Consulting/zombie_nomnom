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
