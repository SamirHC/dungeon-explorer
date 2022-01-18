import enum


class Terrain(enum.Enum):
    WALL = 0
    SECONDARY = 1
    GROUND = 2


class Tile:
    terrain = Terrain.WALL
    room_index = 0
    is_impassable = False
    trap_index = 0
    stairs_index = 0
    can_spawn = False
