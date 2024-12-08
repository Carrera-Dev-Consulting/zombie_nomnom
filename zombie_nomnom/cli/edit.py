import os
from typing import Callable

import click
import yaml
from zombie_nomnom.cli.utils import (
    replayable_menu,
    prompt_list,
    select_dict_item,
    select_list_item,
)
from zombie_nomnom.engine.models import DieRecipe


def run_editor():
    menu = {
        "Edit Bag": edit_bag,
        "Add Bag": add_bag,
        "View Bags": view_bags,
    }
    replayable_menu(menu)


def _get_bags(directory: str | None = None):
    directory = directory or os.getcwd()
    with open(os.path.join(directory, "bags.yaml")) as fp:
        bags = yaml.safe_load(fp)
    return {
        key: [DieRecipe.model_validate(v) for v in value] for key, value in bags.items()
    }


def save_bags(bags):
    with open("bags.yaml", "w") as fp:
        yaml.safe_dump(
            {key: [v.model_dump() for v in value] for key, value in bags.items()},
            fp,
        )


def _render_recipe(recipe: list[DieRecipe]):
    total_dice = sum(v.amount for v in recipe)
    formatted_dice = "\n\t".join([f"{v.amount}x {v.name}[{v.faces}]" for v in recipe])
    click.echo(f"Total Dice: {total_dice}\n\t{formatted_dice}")


def remove_die(recipe: list[DieRecipe]):
    pass


def add_die(recipe: list[DieRecipe]):
    pass


def update_name(recipe: DieRecipe):
    name = click.prompt("Enter New Name", type=str)
    recipe.name = name


def update_sides(recipe: DieRecipe):
    side = select_list_item(recipe.faces)
    pass


def edit_die(recipe: list[DieRecipe]):
    die_recipe = select_dict_item(
        {v.name or ",".join(map(str, v.faces)): v for v in recipe}
    )
    menu = {
        "Update Name": update_name,
        "Update Sides": update_sides,
    }

    replayable_menu(menu, die_recipe)


def edit_bag(bags: dict[str, list[DieRecipe]]):

    recipe = select_dict_item(bags)
    menu = {
        "Remove Die": remove_die,
        "Add Die": add_die,
        "Edit Die": edit_die,
    }
    replayable_menu(menu, recipe, pre=_render_recipe)


def view_bags():
    pass


def add_bag():
    pass
