from __future__ import annotations

import enum

def value(mask: tuple[bool]):
    res = 0
    for d in mask:
        res <<= 1
        res += int(d)
    return res

BORDER_VALUE = value((True for _ in range(8)))
CARDINAL_BORDER_VALUE = value((True for _ in range(4)))


class TileType(enum.Enum):
    PRIMARY = 0
    SECONDARY = 1
    TERTIARY = 2


class Terrain(enum.Enum):
    WALL = "Wall"
    GROUND = "Ground"
    WATER = "Water"
    VOID = "Void"
    LAVA = "Lava"


class Tile:
    tile_type = TileType.PRIMARY
    room_index = 0
    is_impassable = False
    trap = None
    stairs_index = 0
    can_spawn = False
    is_shop = False
    pokemon_ptr = None
    item_ptr = None
    tile_mask = BORDER_VALUE
    cardinal_tile_mask = CARDINAL_BORDER_VALUE

    @classmethod
    def hallway_tile(cls):
        t = Tile()
        t.tile_type = TileType.TERTIARY
        return t

    @classmethod
    def impassable_tile(cls):
        t = Tile()
        t.is_impassable = True
        return t

    @classmethod
    def secondary_tile(cls):
        t = Tile()
        t.tile_type = TileType.SECONDARY
        return t

    @classmethod
    def room_tile(cls, room_number):
        t = Tile()
        t.tile_type = TileType.TERTIARY
        t.room_index = room_number
        t.can_spawn = True
        return t

    @classmethod
    def shop_tile(cls, room_number):
        t = Tile()
        t.tile_type = TileType.TERTIARY
        t.room_index = room_number
        t.is_shop = True
        return t
