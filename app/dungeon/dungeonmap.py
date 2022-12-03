import random

import pygame
from app.dungeon import dungeon, tileset, trap, floor


class DungeonMap:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon
        self.is_below = dungeon.dungeon_data.is_below
        self.map = self.build_map()

    @property
    def floor(self) -> floor.Floor:
        return self.dungeon.floor
    
    @property
    def tileset(self) -> tileset.Tileset:
        return self.dungeon.tileset

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
                return tileset.STAIRS_DOWN_IMAGE
            else:
                return tileset.STAIRS_UP_IMAGE
        if self.floor.has_shop and self.floor[position].is_shop:
            return tileset.SHOP_IMAGE

        if self.floor[position].trap is not None:
            return trap.trap_tileset[self.floor[position].trap]
        return self.tileset[self.map[position]]
