from __future__ import annotations


from app.dungeon.tile_type import TileType


def value(mask: tuple[bool]):
    res = 0
    for d in mask:
        res <<= 1
        res += int(d)
    return res


BORDER_VALUE = value((True for _ in range(8)))
CARDINAL_BORDER_VALUE = value((True for _ in range(4)))


class Tile:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tile_type = TileType.PRIMARY
        self.room_index = 0
        self.is_impassable = False
        self.trap = None
        self.stairs_index = 0
        self.can_spawn = False
        self.is_shop = False
        self.pokemon_ptr = None
        self.item_ptr = None
        self.tile_mask = BORDER_VALUE
        self.cardinal_tile_mask = CARDINAL_BORDER_VALUE
        return self

    def tertiary_tile(self):
        self.tile_type = TileType.TERTIARY
        return self

    def impassable_tile(self):
        self.reset()
        self.is_impassable = True
        return self

    def secondary_tile(self):
        self.reset()
        self.tile_type = TileType.SECONDARY
        return self

    def room_tile(self, room_number):
        self.reset()
        self.tile_type = TileType.TERTIARY
        self.room_index = room_number
        self.can_spawn = True
        return self

    def shop_tile(self, room_number):
        self.reset()
        self.tile_type = TileType.TERTIARY
        self.room_index = room_number
        self.is_shop = True
        return self
