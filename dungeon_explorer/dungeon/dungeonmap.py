import random

import pygame
from dungeon_explorer.dungeon import dungeon, tileset


class DungeonMap:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.floor = dungeon.floor
        self.tileset = dungeon.tileset
        self.is_below = dungeon.dungeon_data.is_below
        self.map = self.build_map()

    def build_map(self):
        self.map = {}
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                self.map[x, y] = self.get_tile_coordinate((x, y))
        return self.map

    def get_tile_coordinate(self, position: tuple[int, int]) -> tuple[tuple[int, int], int]:
        mask = self.floor.get_tile_mask(position)
        variant = random.choice([0,0,0,0,1,1,2,2])
        tile_type = self.floor[position].tile_type
        return self.tileset.get_tile_position(tile_type, mask, variant)

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        if not self.floor.in_inner_bounds(position):
            return self.tileset.get_border_tile()
        if position == self.floor.stairs_spawn:
            if self.is_below:
                return self.tileset.stairs_down_tile
            else:
                return self.tileset.stairs_up_tile
        if self.floor.has_shop and self.floor[position].is_shop:
            return self.tileset.shop_tile

        if self.floor[position].trap is not None:
            return self.tileset.trapset[self.floor[position].trap]
        return self.tileset[self.map[position]]
