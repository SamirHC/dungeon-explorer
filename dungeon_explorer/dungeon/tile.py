from __future__ import annotations
import dataclasses

import enum


@dataclasses.dataclass
class TileMask:
    nw: bool
    n: bool
    ne: bool
    w: bool
    e: bool
    sw: bool
    s: bool
    se: bool

    @classmethod
    def border(cls) -> TileMask:
        return cls(1,1,1,1,1,1,1,1)

    def value(self):
        res = 0
        for d in [self.nw, self.n, self.ne, self.w, self.e, self.sw, self.s, self.se]:
            res <<= 1
            if d:
                res += 1
        return res


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
    trap_index = 0
    stairs_index = 0
    can_spawn = False
    is_shop = False
    pokemon_ptr = None

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
