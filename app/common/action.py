from enum import Enum, auto

"""
Defines a finite number of Actions the user can make.

These actions will each have a key mapping, which is handled elsewhere. These 
enums serve as a layer of abstraction between the handling of input from the
user and the corresponding output.
"""

class Action(Enum):
    INTERACT = auto()
    UP = auto()
    LEFT = auto()
    DOWN = auto()
    RIGHT = auto()

    RUN = auto()
    PASS = auto()
    HOLD = auto()
    MENU = auto()

    # Moves
    MOVE_1 = auto()
    MOVE_2 = auto()
    MOVE_3 = auto()
    MOVE_4 = auto()
    
    # Misc
    FULLSCREEN = auto()
    QUIT = auto()
