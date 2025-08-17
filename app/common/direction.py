from __future__ import annotations
from enum import Enum

from app.common import utils


def _clamp(x: int) -> int:
    return utils.clamp(-1, x, 1)


class Direction(Enum):
    EAST = (1, 0)
    WEST = (-1, 0)
    SOUTH = (0, 1)
    NORTH = (0, -1)
    NORTH_EAST = (1, -1)
    NORTH_WEST = (-1, -1)
    SOUTH_EAST = (1, 1)
    SOUTH_WEST = (-1, 1)

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def is_vertical(self) -> bool:
        return self.x == 0

    def is_horizontal(self) -> bool:
        return self.y == 0

    def is_diagonal(self) -> bool:
        return 0 not in self.value

    def is_cardinal(self) -> bool:
        return 0 in self.value

    def clockwise(self) -> Direction:
        return Direction((_clamp(self.x - self.y), _clamp(self.x + self.y)))

    def anticlockwise(self) -> Direction:
        return Direction((_clamp(self.x + self.y), _clamp(self.y - self.x)))

    def clockwise90(self) -> Direction:
        return self.clockwise().clockwise()

    def anticlockwise90(self) -> Direction:
        return self.anticlockwise().anticlockwise()

    def flip(self) -> Direction:
        return Direction((-self.x, -self.y))

    @staticmethod
    def get_cardinal_directions() -> tuple[Direction]:
        return (
            Direction.NORTH,
            Direction.SOUTH,
            Direction.EAST,
            Direction.WEST,
        )

    @staticmethod
    def get_diagonal_directions() -> tuple[Direction]:
        return (
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
            Direction.SOUTH_EAST,
            Direction.SOUTH_WEST,
        )
