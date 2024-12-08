import click
from zombie_nomnom.cli.play import play_turn, render_players, render_winner, setup_game
from zombie_nomnom.engine.game import ZombieDieGame
from .utils import select_dict_item


def run_game(game: ZombieDieGame | None = None):
    """
    Main entrypoint for prompting and running the game,
    either an existing instance or creates a new one if not given.
    Will allow users to get prompted and play the game as well as run setup if no game
    is given.

    **Parameters**
    - game (`zombie_nomnom.ZombieDieGame` | `None`, optional): game instance that we want to run. Defaults to None.

    **Returns**
    - `zombie_nomnom.ZombieDieGame`: The instance of the game that has been played.
    """
    # ask after we finish a single game assume they will quit when they want to.

    game = setup_game(game)
    while not game.game_over:
        # prime game with initial turn.
        render_players(game)
        play_turn(game)
    render_winner(game)

    return game


def run_diebag_builder(game: ZombieDieGame | None = None):
    pass
