"""
The cli version of zombie_dice this is where we manage the state of the game and how we 
format commands from the cli to apply to the engine and render that to the user.
"""

from typing import Callable, TypeVar
import click

from .engine import DrawDice, Player, RoundState, Score, ZombieDieGame

draw_command = DrawDice()
score_command = Score()


def draw_dice(game: ZombieDieGame):
    click.echo("Drawing dice...")
    turn = game.process_command(draw_command)
    if not turn.ended:
        click.echo(_format_turn_info(turn))
    else:
        click.echo(f"Ohh no!! {turn.player.name} Has Died(T_T) R.I.P")


def score_hand(game: ZombieDieGame):
    click.echo("Scoring Hand...")
    turn = game.process_command(score_command)
    click.echo(_format_turn_info(turn))


def exit(game: ZombieDieGame):
    click.echo("Ending Game...")
    game.game_over = True


actions: dict[str, Callable[[ZombieDieGame], None]] = {
    "Exit": exit,
    "Draw dice": draw_dice,
    "Score hand": score_hand,
}


def run_game(game: ZombieDieGame | None = None):
    game = game or setup_game()
    if game.round is None:
        game.next_round()

    while not game.game_over:
        # prime game with initial turn.
        render_players(game)
        play_turn(game)
    render_winner(game)
    return game


def render_winner(game: ZombieDieGame):
    formatted_player = _format_player(game.winner)
    click.echo(f"{formatted_player} Has Won!!")


def play_turn(game: ZombieDieGame):
    render_turn(game.round)
    select_dict_item(actions)(game)


def _format_turn_info(turn: RoundState):
    player = turn.player
    bag = turn.bag

    return f"{player.name}, Hand: Brains({len(player.brains)}), Feet({len(player.rerolls)}), Shots({len(player.shots)}), Dice Remaining: {len(bag)}"


def render_turn(turn: RoundState):
    click.echo(f"Currently Playing {_format_turn_info(turn)}")


def _format_player(player: Player):
    return f"{player.name} ({player.total_brains})"


def render_players(game: ZombieDieGame):
    players_listed = ", ".join(_format_player(player) for player in game.players)
    click.echo(f"Players: {players_listed}")


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


TVar = TypeVar("TVar")


def select_dict_item(value: dict[str, TVar]) -> TVar:
    menu_items = list(value)
    menu = "\n".join(f"{index}) {item}" for index, item in enumerate(menu_items))
    click.echo(menu)
    selected_index = click.prompt(
        f"Select Item (0-{len(menu_items) - 1})",
        type=click.IntRange(0, len(menu_items) - 1),
    )
    return value[menu_items[selected_index]]


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
