from abc import ABC, abstractmethod
import operator
from typing import Callable
import uuid
from pydantic import BaseModel, Field

from zombie_nomnom.models.dice import Die, Face
from .models.bag import DieBag
from pydantic import validate_call


def uuid_str() -> str:
    return str(uuid.uuid4())


class Player(BaseModel):
    id: str = Field(default_factory=uuid_str)
    name: str
    total_brains: int = 0
    hand: list[Die] = []

    @property
    def rerolls(self):
        return [die for die in self.hand if die.current_face == Face.FOOT]

    @property
    def brains(self):
        return [die for die in self.hand if die.current_face == Face.BRAIN]

    @property
    def shots(self):
        return [die for die in self.hand if die.current_face == Face.SHOTGUN]

    def is_player_dead(self) -> bool:
        # check how many shotguns are in our hand.
        total = 0
        for _ in self.shots:
            # TODO(Milo): Later refactor to look at the die and then add whatever number is on these die.
            total += 1
        # if you have 3 shots you are dead XP
        return total >= 3

    def add_dice(self, *dice: Die) -> "Player":
        """
        Creates a playe score with the dice added to your hand.
        """
        return Player(
            id=self.id,
            name=self.name,
            hand=[*self.hand, *dice],
            total_brains=self.total_brains,
        )

    def clear_hand(self) -> "Player":
        return Player(
            id=self.id,
            name=self.name,
            total_brains=self.total_brains,
        )

    def reset(self) -> "Player":
        return Player(
            id=self.id,
            name=self.name,
            total_brains=0,
            hand=[],
        )

    def calculate_score(self) -> "Player":
        additional_score = 0
        for _ in self.brains:
            # TODO (Milo): For future update where will allow other dice to score a variable amount of points.
            additional_score += 1
        return Player(
            id=self.id,
            name=self.name,
            total_brains=additional_score + self.total_brains,
        )


class RoundState(BaseModel):
    """
    Object representing the state of a round in the game. Keeps track of the bag, player,
    and whether or not the round has ended.
    """

    bag: DieBag
    player: Player
    ended: bool = False


class Command(ABC):
    """
    Used to modify round state. Cannot be used to reset game.
    """

    @abstractmethod
    def execute(self, round: RoundState) -> RoundState:  # pragma: no cover
        """
        Method to generate a new RoundState that represents modifications on the command.

        **Parameters**
        - round(`RoundState`): the round we are on.

        **Returns** `RoundState`

        New instance of round with modified state.
        """


class DrawDice(Command):
    """
    A command that encapsulates drawing dice and calculating whether or not they died.
    """

    amount_drawn: int

    def __init__(self, amount_drawn: int = 3) -> None:
        if amount_drawn <= 0:
            raise ValueError("Cannot draw a no or a negative amount of dice.")
        self.amount_drawn = amount_drawn

    @validate_call
    def execute(self, round: RoundState) -> RoundState:
        """
        Executes a dice draw on a round that is active.

        If round is already over will return given round context.

        **Parameters**
        - round(`RoundState`): the round we are on.

        **Returns** `RoundState`

        New instance of a round with player adding dice to hand.
        """
        if round.ended:
            return round
        player = round.player
        dice_to_roll = player.rerolls
        total_dice = len(dice_to_roll)
        try:
            bag = (
                round.bag.clear_drawn_dice()
                if total_dice == self.amount_drawn
                else round.bag.draw_dice(amount=self.amount_drawn - total_dice)
            )
        except ValueError as exc:
            return self.execute(
                round=RoundState(
                    bag=round.bag.add_dice(player.brains),
                    player=player,
                    ended=round.ended,
                )
            )
        dice_to_roll.extend(bag.drawn_dice)
        player = player.add_dice(*bag.drawn_dice)

        for die in dice_to_roll:
            die.roll()

        ended = player.is_player_dead()
        if ended:
            player = player.clear_hand()

        return RoundState(
            bag=bag,
            player=player,
            ended=ended,
        )


class Score(Command):
    """
    Command to score the hand of a player and add the brains they have as points to their total.
    """

    def execute(self, round: RoundState) -> RoundState:
        """
        Scores the hand of the current player by rolling up all the scoring faces and adding it to their hand.

        **Parameters**
        - round (`RoundState`): The round we are currently in.

        **Returns** `RoundState`

        Roundstate that is now ended with the player with hand cleared and new score added to them.
        """
        if round.ended:
            return round
        player = round.player.calculate_score()
        return RoundState(
            bag=round.bag,
            player=player,
            ended=True,
        )


class ZombieDieGame:
    """Instance of the zombie dice that that manages a bag of dice that will be used to coordinate how the game is played.

    **Required Fields**
    - players (`list[PlayerScore]`)

    **Raises**
    - `ValueError`: When there is not enough players to play a game.
    """

    players: list[Player]
    commands: list[tuple[Command, RoundState]]
    bag_function: Callable[[], DieBag]
    round: RoundState | None
    current_player: int | None
    first_winning_player: int | None
    game_over: bool
    score_threshold: int

    def __init__(
        self,
        players: list[str | Player],
        commands: list[Command] | None = None,
        bag_function: Callable[[], DieBag] | None = None,
        score_threshold: int = 13,
        current_player: int | None = None,
        first_winning_player: int | None = None,
        game_over: bool = False,
        round: RoundState | None = None,
    ) -> None:
        if len(players) == 0:
            raise ValueError("Not enough players for the game we need at least one.")

        self.commands = list(commands) if commands else []
        self.players = [
            (
                Player(name=name_or_score)
                if isinstance(name_or_score, str)
                else name_or_score
            )
            for name_or_score in players
        ]
        self.bag_function = bag_function or DieBag.standard_bag
        self.score_threshold = score_threshold

        self.round = round
        self.current_player = current_player
        self.first_winning_player = first_winning_player
        self.game_over = game_over

        if self.round is None and self.current_player is None:
            self.next_round()

    @property
    def winner(self):
        return max(self.players, key=operator.attrgetter("total_brains"))

    def reset_players(self):
        self.players = [player.reset() for player in self.players]
        self.current_player = None

    def reset_game(self):
        self.reset_players()
        self.commands = []
        self.next_round()

    def next_round(self):
        if self.current_player is not None and self.round:
            self.players[self.current_player] = self.round.player

        if self.current_player is None:
            self.current_player = 0
        elif self.current_player + 1 < len(self.players):
            self.current_player = self.current_player + 1
        else:
            self.current_player = 0
        self.round = RoundState(
            bag=self.bag_function(),
            player=self.players[self.current_player],
            ended=False,
        )

    def check_for_game_over(self):
        if not self.round.ended:
            return  # Still not done with their turns.
        game_over = False
        # GAME IS OVER WHEN THE LAST PLAYER IN A ROUND TAKES THERE TURN
        # I.E. IF SOMEONE MEETS THRESHOLD AND LAST PLAYER HAS HAD A TURN
        if len(self.players) == 1 and self.winner.total_brains >= self.score_threshold:
            game_over = True

        if self.first_winning_player is None:
            if self.players[self.current_player].total_brains >= self.score_threshold:
                self.first_winning_player = self.current_player
        else:
            if (
                self.first_winning_player == 0
                and self.current_player == len(self.players) - 1
            ):
                game_over = True
            elif (
                self.first_winning_player > self.current_player
                and self.first_winning_player - self.current_player == 1
            ):
                game_over = True

        self.game_over = game_over

    def update_player(self):
        self.players[self.current_player] = self.round.player

    def process_command(self, command: Command):
        if self.game_over:
            raise ValueError("Cannot command an ended game please reset game.")

        self.commands.append((command, self.round))

        resulting_round = command.execute(self.round)
        self.round = resulting_round
        if self.round.ended:
            self.update_player()
            self.check_for_game_over()
            self.next_round()
        return resulting_round
