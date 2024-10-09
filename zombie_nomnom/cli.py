"""
The cli version of zombie_dice this is where we manage the state of the game and how we 
format commands from the cli to apply to the engine and render that to the user.
"""

import click

from .engine import Player, ZombieDieGame


def run_game():
    game = setup_game()
    # TODO(Milo): Figure out how to do the thingy
    render_players(game)


def render_players(game: ZombieDieGame):
    players_listed = ", ".join(
        f"{player.name} ({player.total_brains})" for player in game.players
    )
    print(f"Players: {players_listed}")


def setup_game() -> ZombieDieGame:
    names = prompt_list(
        "Enter Player Name",
        _type=str,
        confirmation_prompt="Add Another Player?",
    )
    # TODO(Milo): Figure out a bunch of game types to play that we can use as templates for the die.
    return ZombieDieGame(
        players=[Player(name=name) for name in names],
    )


def prompt_list(
    prompt: str,
    _type: type,
    confirmation_prompt: str = "Add Another?",
) -> list:
    inputs = []
    inputs.append(click.prompt(prompt, type=_type))

    while click.confirm(confirmation_prompt):
        inputs.append(click.prompt(prompt, type=_type))
    return inputs
