from __future__ import annotations

import enum


class TileMask:
    LENGTH = 8

    def __init__(self, mask: str):
        assert len(mask) == TileMask.LENGTH, "Mask length must be 8!"
        self.mask = mask

    @classmethod
    def border(cls) -> TileMask:
        return cls("1"*TileMask.LENGTH)

    def matches(self, other: TileMask) -> bool:
        for i in range(TileMask.LENGTH):
            if self.mask[i] not in "01":
                continue
            if other.mask[i] not in "01":
                continue
            if self.mask[i] != other.mask[i]:
                return False
        return True


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
