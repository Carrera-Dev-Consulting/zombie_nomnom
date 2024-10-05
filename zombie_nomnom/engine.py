from abc import ABC, abstractmethod
from typing import Callable
from pydantic import BaseModel, Field

from zombie_nomnom.models.dice import Die
from .models.bag import DieBag


class PlayerScore(BaseModel):
    name: str
    total_brains: int = 0
    hand: list[Die] = []

    def reset(self) -> "PlayerScore":
        """
        Creates a player score that is the the same name but with no score and hand.
        """
        return PlayerScore(name=self.name)

    def clear(self) -> "PlayerScore":
        """
        Creates a player score that shares the same name and score but reset the hand.
        """
        return PlayerScore(name=self.name, total_brains=self.total_brains)

    def add_dice(self, *dice: Die) -> "PlayerScore":
        """
        Creates a playe score with the dice added to your hand.
        """
        return PlayerScore(
            name=self.name,
            hand=[*self.hand, *dice],
            total_brains=self.total_brains,
        )

    def add_brains(self, brains: int) -> "PlayerScore":
        """
        Creates a new score with a cleared hand and the brains added to your score.
        """
        return PlayerScore(
            name=self.name,
            total_brains=self.total_brains + brains,
        )


class RoundState(BaseModel):
    bag: DieBag
    player: PlayerScore
    ended: bool = False


class Command(ABC):
    """
    Used to modify round state. Cannot be used to reset game.
    """

    @abstractmethod
    def execute(self, state: RoundState) -> RoundState:  # pragma: no cover
        pass


class ZombieDieGame:
    bag: DieBag | None
    players: list[PlayerScore]
    commands: list[Command]
    bag_function: Callable[[], DieBag]
    round: RoundState | None
    current_player: int | None
    game_over: bool

    def __init__(
        self,
        players: list[PlayerScore],
        bag: DieBag | None = None,
        commands: list[Command] | None = None,
        bag_function: Callable[[], DieBag] | None = None,
    ) -> None:
        self.bag = bag
        self.commands = list(commands) if commands else []
        self.players = list(players)
        self.bag_function = bag_function or DieBag.standard_bag
        self.round = None
        self.current_player = None
        self.game_over = False

        if len(self.players) == 0:
            raise ValueError("Not enough players for the game we need at least one.")

    def reset_bag(self):
        self.bag = self.bag_function()

    def reset_players(self):
        self.players = [player.reset() for player in self.players]
        self.current_player = None

    def reset_game(self):
        self.reset_bag()
        self.reset_players()
        self.round = None
        self.commands = []

    def next_round(self):
        self.reset_bag()
        if self.current_player is None:
            self.current_player = 0
        elif self.current_player + 1 < len(self.players):
            self.current_player = self.current_player + 1
        else:
            self.current_player = 0
        self.round = RoundState(bag=self.bag, player=self.players[self.current_player])

    def check_for_game_over(self):
        # TODO(Milo): Check for game over.
        pass

    def process_command(self, command: Command):
        if self.game_over:
            raise ValueError("Cannot command an ended game please reset game.")

        self.commands.append(command)

        if self.round is None or self.round.ended:
            self.next_round()

        self.round = command.execute(self.round)

        self.check_for_game_over()
