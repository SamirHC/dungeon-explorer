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

    def get_non_diagonal_directions():
        return {Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST}

    def get_vertical_directions():
        return {Direction.NORTH, Direction.SOUTH}

    def get_horizontal_directions():
        return {Direction.EAST, Direction.WEST}

    def get_diagonal_directions():
        return {Direction.NORTH_EAST, Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST}

    def is_vertical(self) -> bool:
        return self in Direction.get_vertical_directions()

    def is_horizontal(self) -> bool:
        return self in Direction.get_horizontal_directions()

    def is_diagonal(self) -> bool:
        return self in Direction.get_diagonal_directions()
    