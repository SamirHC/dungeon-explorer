from enum import Enum, auto

"""
Defines a finite number of Actions the user can make.

These actions will each have a key mapping, which is handled elsewhere. These 
enums serve as a layer of abstraction between the handling of input from the
user and the corresponding output.
"""

class Action(Enum):
    # Dungeon/Ground
    INTERACT = auto()
    WALK_NORTH = auto()
    WALK_WEST = auto()
    WALK_SOUTH = auto()
    WALK_EAST = auto()
    RUN = auto()

    # Moves
    MOVE_1 = auto()
    MOVE_2 = auto()
    MOVE_3 = auto()
    MOVE_4 = auto()
    NOTHING = auto()

    # Menu
    TOGGLE_MENU = auto()
    SELECT = auto()
    OPTION_UP = auto()
    OPTION_DOWN = auto()
    PAGE_NEXT = auto()
    PAGE_PREV = auto()
    
    # Misc
    TOGGLE_FULLSCREEN = auto()
    QUIT = auto()
