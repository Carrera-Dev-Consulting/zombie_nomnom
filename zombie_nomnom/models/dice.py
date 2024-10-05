"""
This module contains everything we care about when it comes to the die.
We define a class to contain the faces as well as be able to select one
using the random built-in library.

We can instatation an instance like this
```python
from zombie_nomnom.models.dice import Die, Face

custom_die = Die(faces=[
    Face.BRAIN,
    Face.BRAIN,
    Face.BRAIN,
    Face.SHOTGUN
    Face.SHOTGUN,
    Face.SHOTGUN,
])

# is currently set to None because it was not set.
custom_die.current_face 

# roll and calculate the current face
custom_die.roll()

# will be one of the faces in the in the faces array
custom_die.current_face
```

Most of the time you will want to use a preconfigured recipe
To build your dice which you can use our `create_die` method.

```python
from zombie_nomnom.models.dice import create_die, DieColor

green_die = create_die(DieColor.GREEN)

yellow_die = create_die(DieColor.YELLOW)

red_die = create_die(DieColor.RED)
```

Most of the die in the game are already pre-defined so you can expirement
and use different dice as you make your own custom games.

"""

from enum import Enum
from pydantic import BaseModel, Field
import random


class Face(str, Enum):
    """
    Faces defined in the zombie_dice game:
    - BRAIN
        - The possible point face in the game.
    - FOOT
        - The neutral dice that you will be able to reroll to score more.
    - SHOTGUN
        - The negative counter of which when you get three you will lose out on all possible points per turn.
    """

    BRAIN = "BRAIN"
    FOOT = "FOOT"
    SHOTGUN = "SHOTGUN"


class DieColor(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class Die(BaseModel):
    faces: list[Face] = Field(min_length=6, max_length=6)
    current_face: Face | None = None

    def roll(self) -> Face:
        self.current_face = random.choice(self.faces)
        return self.current_face


_dice_face_mapping = {
    DieColor.RED: {Face.BRAIN: 1, Face.FOOT: 2, Face.SHOTGUN: 3},
    DieColor.YELLOW: {Face.BRAIN: 2, Face.FOOT: 2, Face.SHOTGUN: 2},
    DieColor.GREEN: {Face.BRAIN: 3, Face.FOOT: 2, Face.SHOTGUN: 1},
}


def create_die(color: DieColor) -> Die:
    if color not in _dice_face_mapping:
        raise ValueError(f"Unknown Die Color: {color}")

    mapped_color = _dice_face_mapping[color]
    faces = []
    for face, amount in mapped_color.items():
        faces.extend([face] * amount)
    return Die(faces=faces)
