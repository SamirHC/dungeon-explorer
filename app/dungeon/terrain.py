from enum import Enum


class Terrain(Enum):
    WALL = "Wall"
    GROUND = "Ground"
    WATER = "Water"
    VOID = "Void"
    LAVA = "Lava"