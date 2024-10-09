import pytest
from zombie_nomnom.models.bag import DieBag
from zombie_nomnom.models.dice import Die, Face
from zombie_nomnom.engine import (
    DrawDice,
    PlayerScore,
    RoundState,
    ZombieDieGame,
    Command,
)

from pydantic import ValidationError

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


@pytest.fixture
def starter_round(bag_function, existing_player):
    return RoundState(bag=bag_function(), player=existing_player)


@pytest.fixture
def ended_command():
    class BasicCommand(Command):
        def execute(self, state: RoundState) -> RoundState:
            state.ended = True

    return BasicCommand()


@pytest.fixture
def do_nothing_command():
    class DoNothingCommand(Command):
        def execute(self, state: RoundState) -> RoundState:
            pass

    return DoNothingCommand()


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


def create_die(selected_face: Face):
    return Die(
        faces=[selected_face or Face.SHOTGUN] * 6,
        current_face=selected_face,
    )


def test__player_score__when_hand_has_three_shotguns__player_death():
    sut = PlayerScore(
        name="death",
        hand=[
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
        ],
    )

    assert sut.is_player_dead(), "He isn't dead bobby"

def test__player_score__when_hand_has_two_shotguns__player_is_alive():
    sut = PlayerScore(
        name="death",
        hand=[
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
        ],
    )

    assert not sut.is_player_dead(), "He isn't alive bobby"

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


def test__zombie_die_game__reset_players__sets_current_player_to_none(
    basic_game,
    existing_player,
):
    # arrange
    basic_game.current_player = existing_player

    # act
    basic_game.reset_players()

    # assert
    assert basic_game.current_player == None


def test__zombie_die_game__reset_players__calls_player_reset_one_time_per_player(
    basic_game,
    mocker,
):
    # arrange
    # mock called functions to only test the unit of code in act
    mocked_reset = mocker.patch("zombie_nomnom.engine.PlayerScore")
    mocked_reset.reset.return_value = None
    # act
    basic_game.reset_players()

    # assert
    mocked_reset.assert_called_once()


def test__zombie_die_game__reset_game__calls_reset_bag_and_reset_players(
    basic_game,
    mocker,
):
    # arrange
    # mock called functions to only test the unit of code in act
    mocked_reset_bag = mocker.patch("zombie_nomnom.engine.ZombieDieGame.reset_bag")
    mocked_reset_bag.return_value = None
    mocked_reset_players = mocker.patch(
        "zombie_nomnom.engine.ZombieDieGame.reset_players"
    )
    mocked_reset_players.return_value = None

    # act
    basic_game.reset_game()

    # assert
    mocked_reset_bag.assert_called_once()
    mocked_reset_players.assert_called_once()


def test__zombie_die_game__reset_game__sets_round_to_None_and_commands_to_empty_list(
    basic_game,
    mocker,
    bag_function,
):
    # arrange
    # mock called functions to only test the unit of code in act
    mocked_reset_bag = mocker.patch("zombie_nomnom.engine.ZombieDieGame.reset_bag")
    mocked_reset_bag.return_value = None
    mocked_reset_players = mocker.patch(
        "zombie_nomnom.engine.ZombieDieGame.reset_players"
    )
    mocked_reset_players.return_value = None
    basic_game.round = RoundState(
        bag=bag_function(),
        player=basic_game.players[0],
    )
    basic_game.commands = None

    # act
    basic_game.reset_game()

    # assert
    assert basic_game.round == None
    assert basic_game.commands == []


def test__zombie_die_game__next_round__calls_reset_bag(
    basic_game,
    mocker,
):
    # arrange
    # mock called functions to only test the unit of code in act
    mocked_reset_bag = mocker.patch("zombie_nomnom.engine.ZombieDieGame.reset_bag")
    mocked_reset_bag.side_effect = None
    basic_game.bag = basic_game.bag_function()

    # act
    basic_game.next_round()

    # assert
    mocked_reset_bag.assert_called_once()


def test__zombie_die_game__next_round__sets_current_player_to_zero_if_current_player_is_None(
    basic_game,
):
    # arrange
    basic_game.current_player = None

    # act
    basic_game.next_round()

    # assert
    basic_game.current_player == 0


def test__zombie_die_game__next_round__sets_current_player_to_next_index_if_current_player_index_is_less_than_length_of_players(
    basic_game,
    existing_player,
):
    # arrange
    basic_game.players.append(existing_player)
    basic_game.current_player = 0

    # act
    basic_game.next_round()

    # assert
    basic_game.current_player == 1


def test__zombie_die_game__next_round__sets_current_player_to_zero_when_current_player_index_is_the_last_player_in_list(
    basic_game,
    existing_player,
):
    # arrange
    basic_game.players.append(existing_player)
    basic_game.current_player = 1

    # act
    basic_game.next_round()

    # assert
    basic_game.current_player = 0


def test__zombie_die_game__next_round__sets_round_to_new_round_instance_based_on_new_current_player_index(
    basic_game,
    existing_player,
):
    # arrange
    basic_game.round = None
    basic_game.bag = basic_game.bag_function()

    # act
    basic_game.next_round()

    # assert
    assert isinstance(basic_game.round, RoundState)
    assert basic_game.round.bag == basic_game.bag
    assert basic_game.round.player == basic_game.players[basic_game.current_player]


def test__zombie_die_game__process_command__raises_value_eror_when_game_over_is_true(
    basic_game,
    ended_command,
):
    # arrange
    basic_game.game_over = True

    # act/assert
    with pytest.raises(ValueError):
        basic_game.process_command(ended_command)


def test__zombie_die_game__process_command__appends_passed_command_to_commands_list(
    basic_game,
    ended_command,
    starter_round,
):
    # arrange
    basic_game.commands = []
    basic_game.round = starter_round

    # act
    basic_game.process_command(ended_command)

    # assert
    assert len(basic_game.commands) == 1
    assert basic_game.commands[0] == ended_command


def test__zombie_die_game__process_command__calls_next_round_if_round_is_none(
    basic_game,
    do_nothing_command,
    mocker,
):
    # arrange
    basic_game.round = None
    mocked_next_round = mocker.patch("zombie_nomnom.engine.ZombieDieGame.next_round")

    # act
    basic_game.process_command(do_nothing_command)

    # assert
    mocked_next_round.assert_called_once()


def test__zombie_die_game__process_command__calls_check_for_game_over(
    basic_game,
    do_nothing_command,
    mocker,
):
    # arrange
    mocked_game_over = mocker.patch(
        "zombie_nomnom.engine.ZombieDieGame.check_for_game_over"
    )

    # act
    basic_game.process_command(do_nothing_command)

    # assert
    mocked_game_over.assert_called_once()


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