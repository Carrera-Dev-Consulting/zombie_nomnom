from typing import Any, TypedDict


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
    name: str
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
