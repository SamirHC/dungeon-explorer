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
