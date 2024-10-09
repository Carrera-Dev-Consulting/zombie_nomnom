import pytest
from zombie_nomnom.models.bag import DieBag
from zombie_nomnom.models.dice import Die, Face
from zombie_nomnom.engine import (
    DrawDice,
    PlayerScore,
    RoundState,
    Score,
    ZombieDieGame,
    Command,
    uuid_str,
)

from pydantic import ValidationError


def test_uuid_str__when_generating_new_id__returns_str():
    value = uuid_str()

    assert isinstance(value, str), f"Value we got back was not a str: {value}"


def test_player_score__when_reset__resets_game_info_but_keeps_identity():
    # act
    sut = PlayerScore(
        name="Bill The Kid",
        hand=[create_die()],
        total_brains=69,
    )

    new_player = sut.reset()

    # assert
    assert new_player.name == sut.name
    assert new_player.id == sut.id
    assert new_player.total_brains == 0
    assert new_player.hand == []


def test_player_score__when_clearing_hand__returns_hand_empty():
    sut = PlayerScore(
        name="Sergie",
        total_brains=22,
        hand=[
            create_die(),
        ],
    )

    new_player = sut.clear_hand()
    assert new_player is not sut, "Returned the same player."
    assert new_player.total_brains == sut.total_brains, "Score was lost in translation."
    assert new_player.hand == [], "Hand was not cleared."
    assert new_player.id == sut.id, "Created a new player id."
    assert new_player.name == sut.name, "Changed name."


def test_player_score__when_adding_die__adds_to_hand():
    # arrange
    existing_player = PlayerScore(name="tester", total_brains=0, hand=[])
    die = Die(faces=[Face.BRAIN] * 6)
    # act
    sut = existing_player.add_dice(die)

    # assert

    assert sut.hand == [die]


def test_player_score__when_adding_dice__keeps_dice_in_hand():
    # arrange
    sut = PlayerScore(
        name="tester",
        total_brains=0,
        hand=[create_die(Face.BRAIN)] * 3,
    )

    # act
    sut = sut.add_dice(create_die(Face.FOOT))

    # assert

    assert len(sut.hand) == 4


def create_die(selected_face: Face | None = None):
    return Die(
        faces=[selected_face or Face.SHOTGUN] * 6,
        current_face=selected_face,
    )


def test_player_score__when_hand_has_three_shotguns__player_death():
    sut = PlayerScore(
        name="death",
        hand=[
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
        ],
    )

    assert sut.is_player_dead(), "He isn't dead bobby"


def test_player_score__when_hand_has_two_shotguns__player_is_alive():
    sut = PlayerScore(
        name="death",
        hand=[
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
        ],
    )

    assert not sut.is_player_dead(), "He isn't alive bobby"


def test_zombie_die_game__when_creating_game_with_no_players__raises_exception():
    with pytest.raises(ValueError):
        ZombieDieGame(
            players=[],
        )


def test_zombie_die_game__when_resetting_players__sets_current_player_to_none():
    basic_game = ZombieDieGame(
        players=["Player One", "Player Two"],
    )

    # arrange
    basic_game.current_player = 1

    # act
    basic_game.reset_players()

    # assert
    assert basic_game.current_player is None


def test_zombie_die_game__when_resetting_players__each_player_is_reset():
    sut = ZombieDieGame(players=["David", "Ackerman"])

    sut.reset_players()

    assert all(player.total_brains == 0 and player.hand == [] for player in sut.players)


def test_zombie_die_game__when_resetting_game__calls_resets_all_game_state():
    sut = ZombieDieGame(players=["Jiren"])

    sut.reset_game()

    assert len(sut.players) == 1
    assert sut.round is None
    assert sut.current_player == None


def test_zombie_die_game__when_round_transitioned__uses_new_round():
    known_player = PlayerScore(name="Gray Man")
    sut = ZombieDieGame(
        players=[known_player],
        round=RoundState(
            bag=DieBag.standard_bag(),
            player=known_player,
        ),
        current_player=0,
    )
    old_round = sut.round

    # next round
    sut.next_round()

    assert sut.round == old_round


def test_zombie_die_game__when_round_transitioned__transitions_player():
    sut = ZombieDieGame(players=["Player One", "Player Two"])

    sut.next_round()

    assert sut.current_player == 0


def test_zombie_die_game__when_round_transitioned__transitions_player():
    sut = ZombieDieGame(
        players=["Player One", "Player Two"],
        current_player=1,
    )

    sut.next_round()

    assert sut.current_player == 0


def test_zombie_die_game__when_transitioning_round__updates_the_current_player_to_next():
    sut = ZombieDieGame(players=["First", "Second"], current_player=0)

    sut.next_round()

    assert sut.current_player == 1


def test_zombie_die_game__when_transitioning_round_and_currently_on_last_player__next_player_is_first_player():
    sut = ZombieDieGame(
        players=["Milo", "Xander"],
        current_player=1,
    )

    sut.next_round()

    assert sut.current_player == 0


def test_zombie_die_game__when_transitioning_round_for_single_player__next_player_is_first_player():
    sut = ZombieDieGame(
        players=["Dean"],
        current_player=0,
    )

    sut.next_round()

    assert sut.current_player == 0


class NoOpCommand(Command):
    def execute(self, round: RoundState) -> RoundState:
        return round


def test__zombie_die_game__process_command__raises_value_eror_when_game_over_is_true():
    sut = ZombieDieGame(players=["Lily"], game_over=True)

    with pytest.raises(ValueError):
        sut.process_command(NoOpCommand())


def test_zombie_die_game__when_processing_command__stores_command_in_commands():
    sut = ZombieDieGame(players=["Game"])

    assert not sut.commands

    sut.process_command(NoOpCommand())

    assert sut.commands


def test_zombie_die_game__when_processing_command_on_first_round_of_game__transitions_round_to_first_player():
    sut = ZombieDieGame(players=["Billy", "Mandy"])

    assert sut.round is None, "Was not None before game is ran"

    sut.process_command(NoOpCommand())

    assert sut.round is not None
    assert sut.round.player.name == "Billy"  # billy didn't start the round.


def test_draw_dice__when_given_a_valid_round__draws_dice_and_rolls_them():
    sut = DrawDice()
    player = PlayerScore(name="Ready Player One", hand=[], total_brains=0)
    round_info = RoundState(
        bag=DieBag.standard_bag(),
        player=player,
        ended=False,
    )

    new_info = sut.execute(round_info)

    assert isinstance(
        new_info, RoundState
    ), f"Was not give a round state but instead {type(new_info)}"
    new_player = new_info.player
    assert new_player.name == player.name
    assert new_player.hand, "Hand is empty"


def test_draw_dice__when_drawing_dice__only_gets_three_from_bag():
    sut = DrawDice()
    player = PlayerScore(name="Ready Player One", hand=[], total_brains=0)
    round_info = RoundState(
        bag=DieBag.standard_bag(),
        player=player,
        ended=False,
    )

    new_info = sut.execute(round_info)
    old_bag = round_info.bag
    new_bag = new_info.bag
    assert (
        len(old_bag) - len(new_bag) == 3
    ), f"you have pull not 3 dice: {len(old_bag) - len(new_bag)}"


def test_draw_dice__when_drawing_dice__check_if_player_is_dead():
    sut = DrawDice()
    player = PlayerScore(name="Ready Player One", hand=[], total_brains=0)
    round_info = RoundState(
        bag=DieBag.standard_bag(),
        player=player,
        ended=False,
    )

    new_info = sut.execute(round_info)
    new_player = new_info.player
    assert new_player.is_player_dead() == new_info.ended


def test_draw_dice__when_round_is_already_over__returns_round_as_is():
    sut = DrawDice()
    bag = DieBag.standard_bag().draw_dice()
    player = PlayerScore(name="Ready Player One", hand=bag.drawn_dice, total_brains=0)
    round_info = RoundState(
        bag=bag,
        player=player,
        ended=True,
    )

    new_info = sut.execute(round_info)

    assert new_info is round_info, "Created a new round when it should not have."


def test_draw_dice__when_give_not_a_goddamn_round__raises_validation_error():
    sut = DrawDice()
    with pytest.raises(ValidationError):
        sut.execute(object())


def test_score__when_scoring__calculates_based_on_players_hand():
    sut = Score()
    player = PlayerScore(name="Billy the Goat")
    round = RoundState(
        bag=DieBag.standard_bag(),
        player=player,
        ended=False,
    )
    new_round = sut.execute(round)

    assert new_round.player.total_brains == 0, "Did not calculate score correctly."
