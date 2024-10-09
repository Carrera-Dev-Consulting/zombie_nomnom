from copy import deepcopy
import random
from typing import Iterable

from pydantic import BaseModel

from .dice import Die, create_die, DieColor


class DieBag(BaseModel):
    dice: list[Die]
    drawn_dice: list[Die] = []

    @property
    def is_empty(self):
        return len(self) == 0

    def clear_drawn_dice(self):
        return DieBag(
            dice=self.dice,
        )

    def add_dice(self, dice: Iterable[Die]) -> "DieBag":
        new_dice = [
            *(deepcopy(die) for die in self.dice),
            *(deepcopy(die) for die in dice),
        ]
        return DieBag(dice=new_dice, drawn_dice=[])

    def draw_dice(self, amount: int = 1) -> "DieBag":
        if amount < 0 or amount > len(self):
            raise ValueError("The die bag does not have enough dice.")

        total = len(self)
        selected_dice = set()
        while len(selected_dice) < amount:
            selected_dice.add(random.randint(0, total - 1))
        return DieBag(
            dice=[
                die for index, die in enumerate(self.dice) if index not in selected_dice
            ],
            drawn_dice=[self.dice[index] for index in selected_dice],
        )

    def __len__(self):
        return len(self.dice)

    def __bool__(self):
        return len(self) > 0

    @classmethod
    def standard_bag(cls):
        return cls(
            dice=[
                *(create_die(DieColor.GREEN) for _ in range(6)),
                *(create_die(DieColor.YELLOW) for _ in range(4)),
                *(create_die(DieColor.RED) for _ in range(3)),
            ],
        )
