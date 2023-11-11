import enum


class Terrain(enum.Enum):
    WALL = "Wall"
    GROUND = "Ground"
    WATER = "Water"
    VOID = "Void"
    LAVA = "Lava"