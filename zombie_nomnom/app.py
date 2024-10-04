import click
from .cli import run_game


@click.group()
def main():
    pass


@main.command("cli")
def cli():
    """
    Command to start the zombie_dice game from the command line.
    """
    run_game()

    # ask after we finish a single game assume they will quit when they want to.
    while click.confirm(text="Play another game of zombie dice?"):
        run_game()

    click.echo("Thank you for playing!!")
