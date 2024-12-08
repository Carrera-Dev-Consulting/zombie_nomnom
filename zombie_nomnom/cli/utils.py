from typing import Callable, TypeVar

import click


class StrippedStr(click.ParamType):
    """Custom `str` parameters that will take in the input from the cli
    and trim any trailing or leading spaces so that I can focus on just the value itself.
    """

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> str:
        """Converts a value from clicks input function into a stripped `str`.
        If given an object will turn the object to a `str` using the `__str__` and then trim the output.

        **Parameters**
        - value (`Any`): Value that was taken by clicks input functions.
        - param (`click.Parameter` | `None`): Optional Parameter form click.
        - ctx (`click.Context` | `None`): Optional context form click.

        **Returns**
        - `str`: str value that has been trimmed.
        """
        if isinstance(value, str):
            return value.strip()
        else:
            return str(value).strip()


def prompt_list(
    prompt: str,
    _type: type,
    confirmation_prompt: str = "Add Another?",
) -> list:
    """Prompts the user to input a list of items using the click library.
    Allows you to define the type of information you want in your list and then return that to you.

    **Parameters**
    - prompt (`str`): Prompt to display to the user.
    - _type (`type`): The type that you wish to get back, can also be a `click.ParamType`
    - confirmation_prompt (`str`, optional): Optional prompt for when the user is asked to add another item. Defaults to "Add Another?".

    **Returns**
    - `list`: Collection of items that the user has given.
    """
    inputs = []
    inputs.append(click.prompt(prompt, type=_type))

    while click.confirm(confirmation_prompt):
        inputs.append(click.prompt(prompt, type=_type))
    return inputs


TVar = TypeVar("TVar")


def select_dict_item(value: dict[str, TVar]) -> TVar:
    """Prompts the user to select an item from a dictionary and
    then return the value stored at that key. The selection is
    based on an array of options that is orded the same as the
    way they are stored in the keys.

    **Parameters**
    - value (`dict[str, TVar]`): dictionary with values the user will select from.

    **Returns**
    - `TVar`: The value that was selected by the user.
    """
    menu_items = list(value)
    menu = "\n".join(
        f"{index}) {item}" for index, item in reversed(list(enumerate(menu_items)))
    )
    click.echo(menu)
    selected_index = click.prompt(
        f"Select Item (0-{len(menu_items) - 1})",
        type=click.IntRange(0, len(menu_items) - 1),
    )
    return value[menu_items[selected_index]]


def select_list_item(value: list[TVar]) -> TVar:
    """Prompts the user to select an item from a list and
    then return the value stored at that index. The selection is
    based on an array of options that is orded the same as the
    way they are stored in the list.

    **Parameters**
    - value (`list[TVar]`): list with values the user will select from.

    **Returns**
    - `TVar`: The value that was selected by the user.
    """
    menu = "\n".join(f"{index}) {item}" for index, item in enumerate(value))
    click.echo(menu)
    selected_index = click.prompt(
        f"Select Item (0-{len(value) - 1})", type=click.IntRange(0, len(value) - 1)
    )
    return value[selected_index]

def replayable_menu(
    actions: dict[str, Callable],
    *args,
    pre: Callable | None = None,
    post: Callable | None = None,
    **kwargs,
):
    if len(dict) == 0:
        raise ValueError("Cannot have an empty menu")
    active = True

    def _exit(*args, **kwargs):
        nonlocal active
        active = False

    _menu = {"Exit": _exit**actions}

    while active:
        if pre:
            pre(*args, **kwargs)

        select_dict_item(_menu)(*args, **kwargs)

        if post:
            post(*args, **kwargs)
