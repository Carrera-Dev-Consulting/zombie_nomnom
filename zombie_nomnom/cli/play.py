import json
import os
from typing import Any, Callable
import click

from zombie_nomnom.cli.utils import StrippedStr, prompt_list, select_dict_item

from ..engine import DrawDice, Player, RoundState, Score, ZombieDieGame
from ..engine.serialization import format_to_json_dict, parse_game_json_dict

draw_command = DrawDice()
"""Command used to draw the dice required for a turn."""

score_command = Score()
"""Command used to score a players hand during the game."""


def draw_dice(game: ZombieDieGame):
    """Applys the DrawDice command to the game instance and
    renders the result to the console.

    **Parameters**
    - game (`zombie_nomnom.ZombieDieGame`): instance of the game to apply the draw command too.
    """
    click.echo("Drawing dice...")
    turn = game.process_command(draw_command)
    if not turn.ended:
        click.echo(_format_turn_info(turn))
    else:
        click.echo(f"Ohh no!! {turn.player.name} Has Died(T_T) R.I.P")


def score_hand(game: ZombieDieGame):
    """Applys the score command to a game instance and
    prints out result to the console.

    **Parameters**
    - game (`zombie_nomnom.ZombieDieGame`): game instance you want to score with.
    """
    click.echo("Scoring hand...")
    turn = game.process_command(score_command)
    click.echo(_format_turn_info(turn))


def exit_game(game: ZombieDieGame):
    """
    Exits the game by marking the game as over for players
    who wish to finish the current game they are playing
    and prints out to the console.

    **Parameters**
    - game (`zombie_nomnom.ZombieDieGame`): game instance you want to end.
    """
    click.echo("Ending game...")
    game.game_over = True


def save_game(game: ZombieDieGame):
    click.echo("Saving game...")
    filepath = click.prompt(
        "Enter savefile name to save to",
        type=click.Path(
            dir_okay=False,
            writable=True,
        ),
    )

    if os.path.exists(filepath):
        if not click.confirm("Overwrite existing file?", abort=False):
            return

    with open(filepath, "w") as fp:
        json.dump(format_to_json_dict(game), fp)
    click.echo(f"Saved game to {filepath} succesfully!!")


_actions: dict[str, Callable[[ZombieDieGame], None]] = {
    "Exit": exit_game,
    "Save Game": save_game,
    "Score hand": score_hand,
    "Draw dice": draw_dice,
}


def render_winner(game: ZombieDieGame):
    """Prints out the current winner of the game instance to the console.

    **Parmeters**
    - game (`zombie_nomnom.ZombieDieGame`): instance that we are looking for the winner on.
    """
    formatted_player = _format_player(game.winner)
    click.echo(f"{formatted_player} Has Won!!")


def play_turn(game: ZombieDieGame):
    """Prompts the user on the console to select action for the turn and prints out the current turn information.

    **Parameters**
    - game (`zombie_nomnom.ZombieDieGame`): game we want to do a turn action on.
    """
    render_turn(game.round)
    select_dict_item(_actions)(game)


def _format_turn_info(turn: RoundState):
    player = turn.player
    bag = turn.bag

    return f"{player.name}, Hand: Brains({len(player.brains)}), Feet({len(player.rerolls)}), Shots({len(player.shots)}), Dice Remaining: {len(bag)}"


def render_turn(turn: RoundState):
    """Prints turn info to the console for a given RoundState.

    **Parameters**
    - turn (`zombie_nomnom.RoundState`): RoundState we are printing.
    """
    click.echo(f"Currently Playing {_format_turn_info(turn)}")


def _format_player(player: Player):
    """
    Formats a player object into a string for our rendering fuctions.

    **Parameters**
    - player (`zombie_nomnom.Player`): player we want to format as string

    **Returns**
    - `str`: Stringified version of player
    """
    return f"{player.name} ({player.total_brains})"


def render_players(game: ZombieDieGame):
    """Prints out the players currently playing in
    game instance. Will put them all on a single line.

    **Parameters**
    - game (`zombie_nomnom.ZombieDieGame`): game instance that we are getting players from.
    """
    players_listed = ", ".join(_format_player(player) for player in game.players)
    click.echo(f"Players: {players_listed}")


def new_game() -> ZombieDieGame:
    names = prompt_list(
        "Enter Player Name",
        _type=StrippedStr(),
        confirmation_prompt="Add Another Player?",
    )
    # TODO(Milo): Figure out a bunch of game types to play that we can use as templates for the die.
    return ZombieDieGame(
        players=[Player(name=name) for name in names],
    )


def load_game() -> ZombieDieGame:
    filepath = click.prompt(
        "Enter savefile name to load",
        type=click.Path(
            dir_okay=False,
            exists=True,
            readable=True,
        ),
    )

    with open(filepath, "r") as fp:
        data = json.load(fp)

    return parse_game_json_dict(data)


def remake_game(game: ZombieDieGame) -> ZombieDieGame:
    players = [player.reset() for player in game.players]
    click.echo(f"Current Players: {[player.name for player in players]}")
    if click.prompt("Would you like to add more players?"):
        players.extend(
            prompt_list(
                "Enter Player Name",
                _type=StrippedStr(),
                confirmation_prompt="Add Another Player?",
            )
        )
    return ZombieDieGame(players=players)


def setup_game(game: ZombieDieGame | None) -> ZombieDieGame:
    """Runs the setup game cli prompts for users to enter the players in the game.
    This will prompt you for each player in the game then create and return the
    game instance you have with those players.

    **Returns**
    - `zombie_nomnom.ZombieDieGame`: The instance of the game you setup.
    """
    menu = {
        "Exit": lambda: exit(0),
        "New Game": new_game,
        "Load Game": load_game,
    }

    if game is not None:
        menu["Replay Game"] = lambda: remake_game(game)

    callback = select_dict_item(menu)
    return callback()
