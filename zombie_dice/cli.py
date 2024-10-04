"""
The cli version of zombie_dice this is where we manage the state of the game and how we 
format commands from the cli to apply to the engine and render that to the user.
"""

import click

from .engine import PlayerScore, ZombieDieGame


def run_game():
    game = setup_game()
    # TODO(Milo): Figure out how to do the thingy


def setup_game() -> ZombieDieGame:
    names = prompt_list(
        "Enter Player Name: ",
        _type=str,
        confirmation_prompt="Add Another Player?",
    )
    # TODO(Milo): Figure out a bunch of game types to play that we can use as templates for the die.
    return ZombieDieGame(
        players=[PlayerScore(name=name) for name in names],
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
