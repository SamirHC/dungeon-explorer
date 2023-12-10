from enum import Enum


class TileType(Enum):
    """
    An enum class with each value corresponding to the types of tiles a floor
    can have. This is a distinct - yet related - notion from Terrain. In
    particular, the mapping from TileType to Terrain is
    determined by the graphical TileSet used. Floor generation is only
    concerned about TileType.

    PRIMARY corresponds to the Walls of the floor.
    SECONDARY corresponds to the Water/Lava/Void of the floor.
    TERTIARY corresponds to the Ground of the floor.
    """

    PRIMARY = 0
    SECONDARY = 1
    TERTIARY = 2
