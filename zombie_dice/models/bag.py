import random

from pydantic import BaseModel

from .dice import Die, create_die, DieColor


class DieBag(BaseModel):
    dice: list[Die]
    drawn_die: Die | None = None

    @property
    def is_empty(self):
        return len(self.dice) == 0

    def draw_die(self) -> "DieBag":
        total = len(self.dice)
        if total == 0:
            raise ValueError("Cannot draw_die from empty bag")

        selected_die = random.randint(0, total - 1)
        return DieBag(
            dice=[die for index, die in enumerate(self.dice) if index != selected_die],
            selected_die=self.dice[selected_die],
        )

    @classmethod
    def standard_bag(cls):
        return cls(
            dice=[
                *(create_die(DieColor.GREEN) for _ in range(6)),
                *(create_die(DieColor.YELLOW) for _ in range(4)),
                *(create_die(DieColor.RED) for _ in range(3)),
            ],
        )
