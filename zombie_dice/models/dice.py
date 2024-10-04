from enum import Enum
from pydantic import BaseModel, Field
import random


class Face(str, Enum):
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
