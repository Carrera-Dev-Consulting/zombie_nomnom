from enum import Enum
import importlib
from typing import Any, TypedDict

from zombie_nomnom.engine.commands import Command
from zombie_nomnom.engine.game import ZombieDieGame


class DieDict(TypedDict):
    sides: list[str]
    current_face: str | None


class PlayerDict(TypedDict):
    id: str
    name: str
    total_brains: int
    hand: list[DieDict]


class DieBagDict(TypedDict):
    dice: list[DieDict]
    drawn_dice: list[DieDict] | None


class RoundStateDict(TypedDict):
    diebag: DieBagDict


class CommandDict(TypedDict):
    cls: str
    args: list[Any]
    kwargs: dict[str, Any]


class DieRecipe(TypedDict):
    name: str
    sides: list[str]
    amount: int


class ZombieDieGameDict(TypedDict):
    players: list[PlayerDict]
    commands: list[tuple[CommandDict, RoundStateDict]]
    current_player: int | None
    first_winning_player: int | None
    round: RoundStateDict
    game_over: bool
    score_threshold: int
    bag_function: str | list[DieRecipe]


class KnownFunctions(str, Enum):
    STANDARD = "standard"


def format_command(command: Command) -> CommandDict:
    cmd_type = type(command)
    module = cmd_type.__module__
    qual_name = cmd_type.__qualname__
    return {
        "cls": f"{module}.{qual_name}",
        "args": [],
        # only works if the field on the class matches the param in __init__.py
        "kwargs": command.__dict__,
    }


def parse_command_dict(command: CommandDict) -> Command:
    [*module_path, cls_name] = command.get("cls").split(".")
    module_name = ".".join(module_path)
    module = importlib.import_module(module_name)
    cls = getattr(module, cls_name)
    return cls(*command.get("args"), **command.get("kwargs"))


def format_to_json_dict(game: ZombieDieGame) -> ZombieDieGameDict:
    return {
        "players": [player.model_dump(mode="json") for player in game.players],
        "bag_function": KnownFunctions.STANDARD,
        "commands": [
            (format_command(command), state.model_dump(mode="json"))
            for command, state in game.commands
        ],
        "current_player": game.current_player,
        "first_winning_player": game.first_winning_player,
        "game_over": game.game_over,
        "round": game.round.model_dump(mode="json"),
        "score_threshold": game.score_threshold,
    }


def game_from_json_dict(game_data: ZombieDieGameDict) -> ZombieDieGame:
    pass
