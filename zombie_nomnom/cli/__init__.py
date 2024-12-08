"""
Module containing the code to run the cli for zombie dice and expose the first implemenation of the game.

If you want to just play a game using click's interface for getting users inputs from the cli 
you may use the `run_game` function.

```python
from zombie_nomnom import ZombieDieGame
from zombie_nomnom.cli import run_game


# Starts a full game from setup to full play by play.
run_game() 

existing_game = ZombieDieGame(players=["Me", "You", "Mr. McGee"])

# Run the cli for an already running/existing game.
run_game(existing_game)

```

If you would like to just use some of the functions we have to render different objects
you can use our print functions such as: `render_players`, `render_turn`, `render_winner`

```python
from zombie_nomnom import ZombieDieGame
from zombie_nomnom.cli import render_players, render_turn, render_winner

existing_game = ZombieDieGame(players=["Billy", "Zabka"])

# Prints out the details of the players of the game and their scores.
render_players(existing_game)

# Prints out the given round information object.
render_turn(existing_game.round)

# Prints out the highest scoring player 
# defaults to the player that went first in the case of a tie.
render_winner(existing_game)

```

This module is primarly used by app and should not be used by other parts of our library.

"""

from .main import *
from .play import *
from .utils import *

__all__ = []
