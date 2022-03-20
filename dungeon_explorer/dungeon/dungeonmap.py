import random

import pygame
from dungeon_explorer.dungeon import floor, tileset


class DungeonMap:
    def __init__(self, floor: floor.Floor, tileset: tileset.Tileset, is_below: bool):
        self.floor = floor
        self.tileset = tileset
        self.is_below = is_below
        self.map = self.build_map()

    def build_map(self):
        self.map = {}
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                self.map[x, y] = self.get_tile_coordinate((x, y))
        return self.map

    def get_tile_coordinate(self, position: tuple[int, int]) -> tuple[tuple[int, int], int]:
        p = self.floor.get_tile_mask(position)
        variant = random.choice([0,0,0,0,1,1,2,2])
        terrain = self.floor[position].tile_type
        res = self.tileset.get_tile_position(terrain, p, variant)
        if variant != 0 and not self.tileset.is_valid(self.tileset[res]):
            res = self.tileset.get_tile_position(terrain, p)
        return res

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        if not self.floor.in_inner_bounds(position):
            return self.tileset.get_border_tile()
        if position == self.floor.stairs_spawn:
            if self.is_below:
                return tileset.STAIRS_DOWN_IMAGE
            else:
                return tileset.STAIRS_UP_IMAGE
        if self.floor.has_shop and self.floor[position].is_shop:
            return tileset.SHOP_IMAGE
        return self.tileset[self.map[position]]
