import pytest
from zombie_nomnom.models.bag import DieBag


def test_die_bag__when_creating_standard_bag__contains_13_dice():
    bag = DieBag.standard_bag()
    assert len(bag) == 13


def test_die_bag__when_using_bool_check_and_contains_dice__returns_true():
    bag = DieBag.standard_bag()
    assert bag, "Not truthy when has dice"


def test_die_bag__when_using_bool_check_and_does_not_contain_dice__returns_false():
    bag = DieBag(dice=[])
    assert not bag, "Should not be true"


def test_die_bag__when_using_bool_check_for_bag__should_be_opposite_of_is_empty():
    bag = DieBag(dice=[])
    assert bool(bag) == (not bag.is_empty), "Should not match is empty"


def test_die_bag__when_drawing_die_and_bag_empty__raises_value_error():
    bag = DieBag(dice=[])

    with pytest.raises(ValueError):
        bag.draw_die()
