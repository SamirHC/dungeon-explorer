from __future__ import annotations
from dataclasses import dataclass

from app.dungeon.tile_type import TileType
from app.dungeon.trap import Trap
from app.pokemon.pokemon import Pokemon
from app.item.item import Item


def value(mask: tuple[bool]):
    res = 0
    for d in mask:
        res <<= 1
        res += int(d)
    return res


BORDER_VALUE = value((True for _ in range(8)))
CARDINAL_BORDER_VALUE = value((True for _ in range(4)))



@dataclass
class Tile:
    tile_type: TileType = TileType.PRIMARY
    room_index: int = 0
    is_impassable: bool = False
    trap: Trap = None
    stairs_index: int = 0
    can_spawn: bool = False
    is_shop: bool = False
    pokemon_ptr: Pokemon = None
    item_ptr: Item = None
    tile_mask: tuple[bool] = BORDER_VALUE
    cardinal_tile_mask: tuple[bool] = CARDINAL_BORDER_VALUE

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

    def tertiary_tile(self):
        self.tile_type = TileType.TERTIARY

    def impassable_tile(self):
        self.is_impassable = True

    def secondary_tile(self):
        self.tile_type = TileType.SECONDARY

    def room_tile(self, room_number):
        self.tile_type = TileType.TERTIARY
        self.room_index = room_number
        self.can_spawn = True

    def shop_tile(self, room_number):
        self.tile_type = TileType.TERTIARY
        self.room_index = room_number
        self.is_shop = True
