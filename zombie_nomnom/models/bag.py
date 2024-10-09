import random

from pydantic import BaseModel

from .dice import Die, create_die, DieColor


class DieBag(BaseModel):
    dice: list[Die]
    drawn_dice: list[Die] | None = None

    @property
    def is_empty(self):
        return len(self) == 0

    def draw_dice(self, amount: int = 1) -> "DieBag":
        if amount < 0 or amount > len(self):
            raise ValueError("The die bag does not have enough dice.")

        total = len(self)
        if total == 0:
            raise ValueError("Cannot draw_die from empty bag")
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
