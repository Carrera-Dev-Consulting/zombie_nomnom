"""
Module that contains the click entrypoint for our cli interface.

Currently this only contains code to run the game form the cli but this will be extended 
to also run this as a web app including a built in server with react spa app.
"""

import click

from zombie_nomnom.cli.edit import run_editor
from .cli import run_game


@click.group()
def main():
    """
    main group that represents the top-level: ***zombie-nomnom***

    This will be used to decorate sub-commands for zombie-nomnom.

    ***Example Usage:***
    ```python
    @main.command("sub-command")
    def sub_command():
        # do actual meaningful work.
        pass
    ```
    """
    pass


@main.command("cli")
def cli():
    """
    Command to start the zombie_dice game from the command line.
    """
    try:
        game = None
        while True:
            game = run_game(game)
    except KeyboardInterrupt:
        click.echo("Thank you for playing!!")


@main.command("edit")
def edit():
    run_editor()
