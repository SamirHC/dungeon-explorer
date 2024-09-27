from __future__ import annotations
from enum import Enum

from app.common import utils


def _clamp(x: int) -> int:
    """
    Clamp a given integer between -1 and 1.

    This function utilizes the `clamp` utility function from the common module
    to restrict the input value within the specified range.

    :param int x: The integer to be clamped.
    :return: The clamped integer value.
    :rtype: int
    """
    return utils.clamp(-1, x, 1)


class Direction(Enum):
    """
    An enumeration representing directions in a 2D grid.

    Each direction is represented as a tuple of two integers, indicating
    changes in the x and y coordinates.

    :cvar EAST: Represents the east direction (1, 0).
    :cvar WEST: Represents the west direction (-1, 0).
    :cvar SOUTH: Represents the south direction (0, 1).
    :cvar NORTH: Represents the north direction (0, -1).
    :cvar NORTH_EAST: Represents the north-east direction (1, -1).
    :cvar NORTH_WEST: Represents the north-west direction (-1, -1).
    :cvar SOUTH_EAST: Represents the south-east direction (1, 1).
    :cvar SOUTH_WEST: Represents the south-west direction (-1, 1).
    """

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
        """
        Get the x-component of the direction.

        :return: The x-component of the direction.
        :rtype: int
        """
        return self.value[0]

    @property
    def y(self):
        """
        Get the y-component of the direction.

        :return: The y-component of the direction.
        :rtype: int
        """
        return self.value[1]

    def is_vertical(self) -> bool:
        """
        Check if the direction is vertical.

        A direction is considered vertical if the x-component is zero.

        :return: True if the direction is vertical, False otherwise.
        :rtype: bool
        """
        return not self.x

    def is_horizontal(self) -> bool:
        """
        Check if the direction is horizontal.

        A direction is considered horizontal if the y-component is zero.

        :return: True if the direction is horizontal, False otherwise.
        :rtype: bool
        """
        return not self.y

    def is_diagonal(self) -> bool:
        """
        Check if the direction is diagonal.

        A direction is considered diagonal if neither component is zero.

        :return: True if the direction is diagonal, False otherwise.
        :rtype: bool
        """
        return 0 not in self.value

    def is_cardinal(self) -> bool:
        """
        Check if the direction is cardinal (not diagonal).

        A direction is considered cardinal if at least one component is zero.

        :return: True if the direction is cardinal, False otherwise.
        :rtype: bool
        """
        return 0 in self.value

    def clockwise(self) -> Direction:
        """
        Rotate the direction clockwise by 45 degrees.

        The direction is rotated around the origin by 45 degrees clockwise.

        :return: The new direction after rotation.
        :rtype: Direction
        """
        return Direction((_clamp(self.x - self.y), _clamp(self.x + self.y)))

    def anticlockwise(self) -> Direction:
        """
        Rotate the direction anticlockwise by 45 degrees.

        The direction is rotated around the origin by 45 degrees anticlockwise.

        :return: The new direction after rotation.
        :rtype: Direction
        """
        return Direction((_clamp(self.x + self.y), _clamp(self.y - self.x)))

    def clockwise90(self) -> Direction:
        """
        Rotate the direction clockwise by 90 degrees.

        :return: The new direction after a 90-degree clockwise rotation.
        :rtype: Direction
        """
        return self.clockwise().clockwise()

    def anticlockwise90(self) -> Direction:
        """
        Rotate the direction anticlockwise by 90 degrees.

        :return: The new direction after a 90-degree anticlockwise rotation.
        :rtype: Direction
        """
        return self.anticlockwise().anticlockwise()

    def flip(self) -> Direction:
        """
        Reverse the direction to point in the opposite direction.

        :return: The flipped direction.
        :rtype: Direction
        """
        return Direction((-self.x, -self.y))

    @staticmethod
    def get_cardinal_directions() -> tuple[Direction]:
        """
        Get a tuple of all cardinal directions (NORTH, SOUTH, EAST, WEST).

        :return: A tuple containing the cardinal directions.
        :rtype: tuple[Direction, ...]
        """
        return (
            Direction.NORTH,
            Direction.SOUTH,
            Direction.EAST,
            Direction.WEST,
        )

    @staticmethod
    def get_diagonal_directions() -> tuple[Direction]:
        """
        Get a tuple of all diagonal directions (NORTH_WEST, NORTH_EAST, SOUTH_EAST, SOUTH_WEST).

        :return: A tuple containing the diagonal directions.
        :rtype: tuple[Direction, ...]
        """
        return (
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
            Direction.SOUTH_EAST,
            Direction.SOUTH_WEST,
        )
