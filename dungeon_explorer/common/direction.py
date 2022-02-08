from __future__ import annotations
import enum


class Direction(enum.Enum):
    # (x, y)
    EAST = (1, 0)
    WEST = (-1, 0)
    SOUTH = (0, 1)
    NORTH = (0, -1)
    NORTH_EAST = (1, -1)
    NORTH_WEST = (-1, -1)
    SOUTH_EAST = (1, 1)
    SOUTH_WEST = (-1, 1)

    @property
    def x(self):
        return self.value[0]

    @property
    def y(self):
        return self.value[1]

    def get_non_diagonal_directions() -> set[Direction]:
        return {Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST}

    def get_vertical_directions() -> set[Direction]:
        return {Direction.NORTH, Direction.SOUTH}

    def get_horizontal_directions() -> set[Direction]:
        return {Direction.EAST, Direction.WEST}

    def get_diagonal_directions() -> set[Direction]:
        return {Direction.NORTH_EAST, Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST}

    def is_vertical(self) -> bool:
        return self in Direction.get_vertical_directions()

    def is_horizontal(self) -> bool:
        return self in Direction.get_horizontal_directions()

    def is_diagonal(self) -> bool:
        return self in Direction.get_diagonal_directions()

    def clockwise(self) -> Direction:
        if self is Direction.NORTH: return Direction.NORTH_EAST
        if self is Direction.NORTH_EAST: return Direction.EAST
        if self is Direction.EAST: return Direction.SOUTH_EAST
        if self is Direction.SOUTH_EAST: return Direction.SOUTH
        if self is Direction.SOUTH: return Direction.SOUTH_WEST
        if self is Direction.SOUTH_WEST: return Direction.WEST
        if self is Direction.WEST: return Direction.NORTH_WEST
        if self is Direction.NORTH_WEST: return Direction.NORTH

    def anticlockwise(self) -> Direction:
        if self is Direction.NORTH: return Direction.NORTH_WEST
        if self is Direction.NORTH_WEST: return Direction.WEST
        if self is Direction.WEST: return Direction.SOUTH_WEST
        if self is Direction.SOUTH_WEST: return Direction.SOUTH
        if self is Direction.SOUTH: return Direction.SOUTH_EAST
        if self is Direction.SOUTH_EAST: return Direction.EAST
        if self is Direction.EAST: return Direction.NORTH_EAST
        if self is Direction.NORTH_EAST: return Direction.NORTH

    def flip(self) -> Direction:
        return Direction((-self.x, -self.y))
