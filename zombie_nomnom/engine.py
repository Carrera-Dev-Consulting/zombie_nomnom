"""Module that contains the code to run the core game engine.
You can create an instance directly by using the `ZombieDieGame`.

```python
from zombie_nomnom import ZombieDieGame, DrawDice, Score

score = Score()
draw_dice = DrawDice(3)

game = ZombieDieGame(players=["Mellow"])

game.process_command(draw_dice)
game.process_command(score)

```

For the core of the engine it doesn't actually know how to play but only 
how to manage a turn based on tracking the changes in a round with a `RoundState` object.

This allows you to extend the game by creating your own custom actions with the `Command` class.
This class defines the `execute` method and then allows you to specify what that action does to the game state.
You will need to return an new instance of `RoundState` objects that represents the effect of game state after the round is over.

```python
from zombie_nomnom import Command, ZombieDieGame

class CustomCommand(Command):
    def execute(self, round: RoundState) -> RoundState:
        # do meaningful work to define what you want this command to do to the round.
        return round  # return either a new command or the exact same command unchanged.

custom_command = CustomCommand()
game = ZombieDieGame(players=["Meelow"])

game.process_command(custom_command) # now it just works in the game!!

```

This only allows you to modify the state of the current player or the current turn that is active in the engine.
That being said it should provide a nice way to extend the app with custom actions for a players.

The core objects that we use in our engine are three:
- `Player`
- `RoundState`

```python
from zombie_nomnom.models import DieBag, Die, Face
from zombie_nomnom.engine import Player, RoundState

player = Player(
    name="Mega Man"
)

# you can add dice to their hand.
player_with_die_added = player.add_dice(
    Die(
        faces=[Face.BRAIN] * 6
    )
)
player_with_die_added.hand # dice is now updated with new die.

player.rerolls # pulls the dice that are re-rollable in hand
player.brains # pulls all the scoring dice in hand.
player.shots # pulls all the damaging dice in hand.

# counts the shots in the hand and see if you have been shot 3 or more times.
player.is_player_dead() # player is not dead

# new player with nothing in their hand.
new_player = player.clear_hand()
new_player.hand # is empty list

# resets the players game stats
new_player = player.reset() 
new_player.total_brains # now 0
new_player.hand # empty list

# counts the dice in the hand and adds to score.
new_player = player.calculate_score()
new_player.total_brains # player had 1 brain so it will now be 1
new_player.hand # is not empty list

# no methods just holds value to package it in a single object.
round = RoundState(
    bag=DieBag.standard_bag(),
    player=player,
)
```
"""

from abc import ABC, abstractmethod
import operator
from typing import Callable
import uuid
from pydantic import BaseModel, Field

from zombie_nomnom.models.dice import Die, Face
from .models.bag import DieBag
from pydantic import validate_call


def uuid_str() -> str:
    """Creates a stringified uuid that we can use.

    **Returns**
    - `str`: stringified uuid
    """
    return str(uuid.uuid4())


class Player(BaseModel):
    """Player in the game. This manages the total points
    they have and the dice they pulled from the bag. Has
    methods to manage the hand and then calculate points.
    Also has ways to be able to tell if players turn should finish.
    """

    id: str = Field(default_factory=uuid_str)
    """id field used to identify the player more unqiuely"""
    name: str
    """name of the player that we display on the screen"""
    total_brains: int = 0
    """total points they currently have in the game"""
    hand: list[Die] = []
    """the dice the player is currently holding"""

    @property
    def rerolls(self) -> list[Die]:
        """A view of the hand that shows all the dice that are re-rollable.

        **Returns**:
        - `list[zombie_nomnom.Die]`: re-rollable dice
        """
        return [die for die in self.hand if die.current_face == Face.FOOT]

    @property
    def brains(self) -> list[Die]:
        """A view of the hand that shows all the dice that scores points.

        **Returns**
        - `list[zombie_nomnom.Die]`: scoreable dice
        """
        return [die for die in self.hand if die.current_face == Face.BRAIN]

    @property
    def shots(self) -> list[Die]:
        """A view of the hand that shows the shots you have taken.

        **Returns**
        - `list[zombie_nomnom.Die]`: damaging dice
        """
        return [die for die in self.hand if die.current_face == Face.SHOTGUN]

    def is_player_dead(self) -> bool:
        """Calculates whether or not the player should be dead based on the shots in their hand.

        **Returns**
        - bool: True when player is considered dead.
        """
        total = 0
        for _ in self.shots:
            # TODO(Milo): Later refactor to look at the die and then add whatever number is on these die.
            total += 1
        # if you have 3 shots you are dead XP
        return total >= 3

    def add_dice(self, *dice: Die) -> "Player":
        """Creates a new player adding the dice the caller gives plus any dice in their hand currently.

        **Returns**
        - `Player`: New player instance with updated hand.
        """
        return Player(
            id=self.id,
            name=self.name,
            hand=[*self.hand, *dice],
            total_brains=self.total_brains,
        )

    def clear_hand(self) -> "Player":
        """Creates a new player with no dice in their hand.

        **Returns**
        - `Player`: New player instance with empty hand.
        """
        return Player(
            id=self.id,
            name=self.name,
            total_brains=self.total_brains,
        )

    def reset(self) -> "Player":
        """Creates a new player instance with all the game related fields set back to their default values.

        **Returns**
        - `Player`: New player instance with all values reset.
        """
        return Player(
            id=self.id,
            name=self.name,
            total_brains=0,
            hand=[],
        )

    def calculate_score(self) -> "Player":
        """Creates a new player that has added the score of the current hand and leaves an empty hand.

        **Returns**
        - `Player`: New player instance with score adjusted for scoring dice in hand and hand reset back to empty list.
        """
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
    """Bag that is currently being played in the round"""
    player: Player
    """Player that is currently playing"""
    ended: bool = False
    """Records whether or not the current round is over"""


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
    The core command that represents handling a draw action in the game.
    This will attempt to draw dice in your hand to fill in any dice that
    are not re-rollable then roll the dice for the turn. Then it will
    check to make sure you are still alive and if so keep dice in your hand
    and return a new round object.

    **Parameters**
    - amount_drawn (`int`): Dice this action will attempt to draw.
    """

    amount_drawn: int
    """Amount of dice that this action will attempt to draw."""

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

    **Parameters**
    - players (`list[PlayerScore]`): players in the game
    - commands (`list[tuple[Command, RoundState]]`, optional): previous commands that have been run before in the game. Defaults to `[]`
    - bag_function (`Callable[[], DieBag]`, optional): function that will generate a `zombie_nomnom.DieBag` that will be used in the round transitions. Defaults to `zombie_nomnom.DieBag.standard_bag`
    - score_threshold (`int`, optional): the score threshold that will trigger the end game. Defaults to `13`
    - current_player (`int | None` optional): the index in the player array to represent the current player. Defaults to `None`
    - first_winning_player (`int | None` optional): the index in the player array that represents the first player to meet or exceed the score threshold. Defaults to `None`
    - game_over (`bool`, optional): marks whether or not game is over. Defaults to `False`
    - round (`RoundState | None`, optional): the current round of the game being played. Defaults to a new instance that is created for the first player in the player array.

    **Raises**
    - `ValueError`: When there is not enough players to play a game.
    """

    players: list[Player]
    """Players that are in the game."""
    commands: list[tuple[Command, RoundState]]
    """Commands that have been processed in the game and the round state they were in before it started."""
    bag_function: Callable[[], DieBag]
    """Function that we use when we need to create a new bag for a round."""
    round: RoundState | None
    """Current round that we are on."""
    current_player: int | None
    """Index of player in the players array who's turn it currently is."""
    first_winning_player: int | None
    """Index of player who first exceeded or matched the `score_threshold`."""
    game_over: bool
    """Marker for when the game is over."""
    score_threshold: int
    """Threshold required for a player to start the end game."""

    def __init__(
        self,
        players: list[str | Player],
        commands: list[tuple[Command, RoundState]] | None = None,
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
    def winner(self) -> Player:
        """The player with the highest score in the players array. On Ties uses the player with the lowest index.

        **Returns**
        - `Player`: The winning player
        """
        return max(self.players, key=operator.attrgetter("total_brains"))

    def reset_players(self):
        """Resets the game state so that players scores are set to zero and the current_player is reset to `None` as well as the first_winning_player"""
        self.players = [player.reset() for player in self.players]
        self.current_player = None
        self.first_winning_player = None

    def reset_game(self):
        """Resets the game state by resetting the players, clearing commands, and transitioning to the next round which will be the first players round."""
        self.reset_players()
        self.commands = []
        self.next_round()

    def next_round(self):
        """Transitions the current player index point to the next players turn and then sets the round field with that player and a new bag to play the round."""
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

    def check_for_game_over(self) -> bool:
        """Checks if game is over and sets the game_over field."""
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
        """Updates the player in the players array with the instance that is currently on the round field for the current player index."""
        self.players[self.current_player] = self.round.player

    def process_command(self, command: Command) -> RoundState:
        """Applies the given command to the active round and transitions to the next round if the current round is over.

        **Parameters**
        - command (`Command`): command that will modify the round state.

        **Raises**
        - `ValueError`: When trying to process a command when the game is already over.

        **Returns**
        - `RoundState`: The round information that happened due to the command.
        """
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
