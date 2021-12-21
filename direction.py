from pygame import Vector2
from enum import Enum

class Direction(Enum):
    EAST = Vector2(1, 0)
    WEST = -EAST
    SOUTH = Vector2(0, 1)
    NORTH = -SOUTH
    NORTH_EAST = NORTH + EAST
    NORTH_WEST = NORTH + WEST
    SOUTH_EAST = SOUTH + EAST
    SOUTH_WEST = SOUTH + WEST
