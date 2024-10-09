import pytest
from zombie_nomnom.models.bag import DieBag
from zombie_nomnom.models.dice import Die, Face
from zombie_nomnom.engine import (
    DrawDice,
    Player,
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
    sut = Player(
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
    sut = Player(
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
    existing_player = Player(name="tester", total_brains=0, hand=[])
    die = Die(faces=[Face.BRAIN] * 6)
    # act
    sut = existing_player.add_dice(die)

    # assert

    assert sut.hand == [die]


def test_player_score__when_adding_dice__keeps_dice_in_hand():
    # arrange
    sut = Player(
        name="tester",
        total_brains=0,
        hand=[create_die(Face.BRAIN)] * 3,
    )

    # act
    sut = sut.add_dice(create_die(Face.FOOT))

    # assert

    assert len(sut.hand) == 4


def test_player_score__when_scoring__counts_all_brains():
    sut = Player(
        name="Medical",
        hand=[
            create_die(Face.BRAIN),
            create_die(Face.FOOT),
            create_die(Face.SHOTGUN),
        ],
        total_brains=0,
    )

    scored = sut.calculate_score()

    assert scored.total_brains == 1


def test_player_score__when_scoring_hand_with_no_brains__does_not_change_score():
    sut = Player(
        name="Medical",
        hand=[
            create_die(Face.FOOT),
            create_die(Face.FOOT),
            create_die(Face.SHOTGUN),
        ],
        total_brains=0,
    )

    scored = sut.calculate_score()

    assert scored.total_brains == 0


def test_player_score__when_scoring_hand_with_existing_points__adds_points_together():
    sut = Player(
        name="Medical",
        hand=[
            create_die(Face.BRAIN),
            create_die(Face.FOOT),
            create_die(Face.SHOTGUN),
        ],
        total_brains=11,
    )

    scored = sut.calculate_score()

    assert scored.total_brains == 12


def create_die(selected_face: Face | None = None):
    return Die(
        faces=[selected_face or Face.SHOTGUN] * 6,
        current_face=selected_face,
    )


def test_player_score__when_hand_has_three_shotguns__player_death():
    sut = Player(
        name="death",
        hand=[
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
            create_die(Face.SHOTGUN),
        ],
    )

    assert sut.is_player_dead(), "He isn't dead bobby"


def test_player_score__when_hand_has_two_shotguns__player_is_alive():
    sut = Player(
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
    known_player = Player(name="Gray Man")
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


def all_face_bag(
    face: Face | None = None,
    amount_in_bag: int = 12,
):
    return DieBag(
        dice=[create_die(face)] * amount_in_bag,
    )


def test_draw_dice__when_given_a_valid_round__draws_dice_and_rolls_them():
    sut = DrawDice()
    player = Player(name="Ready Player One", hand=[], total_brains=0)
    round_info = RoundState(
        bag=all_face_bag(Face.BRAIN),
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
    player = Player(name="Ready Player One", hand=[], total_brains=0)
    round = RoundState(
        bag=all_face_bag(Face.BRAIN),
        player=player,
        ended=False,
    )

    new_round = sut.execute(round)
    old_bag = round.bag
    new_bag = new_round.bag
    assert (
        len(old_bag) - len(new_bag) == 3
    ), f"you have pull not 3 dice: {len(old_bag) - len(new_bag)}"


def test_draw_dice__when_drawing_dice__check_if_player_is_dead():
    sut = DrawDice()
    player = Player(name="Ready Player One", hand=[], total_brains=0)
    round_info = RoundState(
        bag=all_face_bag(Face.BRAIN),
        player=player,
        ended=False,
    )

    new_info = sut.execute(round_info)
    new_player = new_info.player
    assert new_player.is_player_dead() == new_info.ended


def test_draw_dice__when_round_is_already_over__returns_round_as_is():
    sut = DrawDice()
    bag = all_face_bag(Face.BRAIN).draw_dice()
    player = Player(name="Ready Player One", hand=bag.drawn_dice, total_brains=0)
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


def test_draw_dice__when_creating_command_with_negative_value__raises_exception():
    with pytest.raises(ValueError):
        DrawDice(amount_drawn=-1)


def test_draw_dice__when_creating_command_with_zero__raises_exception():
    with pytest.raises(ValueError):
        DrawDice(amount_drawn=0)


def test_draw_dice__when_rolled_death_for_player__round_is_ended_and_players_hand_is_cleared():
    sut = DrawDice()
    # Damn he is about to throw so hard...
    round = RoundState(
        bag=all_face_bag(Face.SHOTGUN, amount_in_bag=4),
        player=Player(
            name="Billy",
            hand=[
                create_die(Face.BRAIN),
                create_die(Face.BRAIN),
                create_die(Face.BRAIN),
            ],
        ),
        ended=False,
    )

    new_round = sut.execute(round)

    assert new_round.player.hand == []
    assert new_round.ended is True


def test_draw_dice__when_rolling_dice__uses_dice_in_hand_first():
    round = RoundState(
        bag=all_face_bag(Face.BRAIN, amount_in_bag=10),
        player=Player(
            name="OuiOui Bagguette",
            hand=[
                create_die(Face.FOOT),
                create_die(Face.FOOT),
                create_die(Face.FOOT),
            ],
        ),
        ended=False,
    )
    sut = DrawDice()

    new_round = sut.execute(round)

    assert new_round.bag.drawn_dice == []
    assert len(new_round.bag) == 10


def test_draw_dice__when_rolling_dice_with_feet_in_hand__fills_in_remaining_with_die_from_bag():
    round = RoundState(
        bag=all_face_bag(Face.BRAIN, amount_in_bag=10),
        player=Player(
            name="OuiOui Bagguette",
            hand=[
                create_die(Face.FOOT),
            ],
        ),
        ended=False,
    )
    sut = DrawDice()

    new_round = sut.execute(round)

    assert len(new_round.bag.drawn_dice) == 2
    assert len(new_round.bag) == 8


def test_score__when_scoring__calculates_based_on_players_hand():
    sut = Score()
    player = Player(name="Billy the Goat")
    round = RoundState(
        bag=DieBag.standard_bag(),
        player=player,
        ended=False,
    )
    new_round = sut.execute(round)

    assert new_round.player.total_brains == 0, "Did not calculate score correctly."
