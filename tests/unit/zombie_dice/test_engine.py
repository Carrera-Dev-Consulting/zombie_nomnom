import pytest
from zombie_nomnom.models.bag import DieBag
from zombie_nomnom.models.dice import Die, Face
from zombie_nomnom.engine import PlayerScore, RoundState, ZombieDieGame


@pytest.fixture
def existing_player():
    return PlayerScore(
        name="tester", total_brains=2, hand=[Die(faces=[Face.BRAIN] * 6)]
    )


@pytest.fixture
def bag_function():
    def func():
        return DieBag.standard_bag()

    return func


@pytest.fixture
def basic_game(bag_function):
    return ZombieDieGame(
        players=[PlayerScore(name="tester")],
        bag_function=bag_function,
    )


def test__player_score__reset__resets_total_brains_and_hand_but_keeps_name(
    existing_player,
):
    # act
    sut = existing_player.reset()

    # assert
    assert sut.name == existing_player.name
    assert sut.total_brains == 0
    assert sut.hand == []


def test__player_score__clear__empties_hand_but_keeps_brains_and_name(existing_player):
    # act
    sut = existing_player.clear()

    # assert
    assert sut.name == existing_player.name
    assert sut.total_brains == existing_player.total_brains
    assert sut.hand == []


def test__player_score__add_dice__joins_passed_dice_with_existing_empty_hand():
    # arrange
    existing_player = PlayerScore(name="tester", total_brains=0, hand=[])

    # act
    sut = existing_player.add_dice(Die(faces=[Face.BRAIN] * 6))

    # assert

    assert sut.hand == [Die(faces=[Face.BRAIN] * 6)]


def test__player_score__add_dice__joins_passed_dice_with_existing_filled_hand():
    # arrange
    existing_player = PlayerScore(
        name="tester", total_brains=0, hand=[Die(faces=[Face.BRAIN] * 6)] * 3
    )

    # act
    sut = existing_player.add_dice(Die(faces=[Face.BRAIN] * 6))

    # assert

    assert sut.hand == [Die(faces=[Face.BRAIN] * 6)] * 4


def test__player_score__add_brains__adds_brains_to_total_brains(existing_player):
    # act
    sut = existing_player.add_brains(5)

    # assert
    assert sut.total_brains == 7


def test__zombie_die_game__init_raises_value_error_when_players_is_zero():
    with pytest.raises(ValueError):
        ZombieDieGame(
            players=[],
        )


def test__zombie_die_game__reset_bag_calls_passed_bag_function_and_sets_to_standard_bag(
    basic_game,
):
    # act
    assert basic_game.bag is None  # make sure there is no bag before we reset
    basic_game.reset_bag()

    # assert
    assert isinstance(basic_game.bag, DieBag)
    assert basic_game.bag.dice == DieBag.standard_bag().dice
