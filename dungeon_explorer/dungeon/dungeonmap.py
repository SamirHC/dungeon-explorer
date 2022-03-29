import random

import pygame
from dungeon_explorer.dungeon import dungeon, dungeonstatus, tileset


class DungeonMap:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon
        self.tileset = dungeon.tileset
        self.floor = dungeon.floor
        self.status = dungeon.status
        self.is_below = dungeon.dungeon_data.is_below
        self.filtered_tilesets: dict[dungeonstatus.Weather, tileset.Tileset] = self.load_filtered_tilesets()
        self.map = self.build_map()

    def load_filtered_tilesets(self):
        res = {}
        for weather in dungeonstatus.Weather:
            new_tileset = tileset.Tileset(self.dungeon.current_floor_data.tileset)
            weather_filter = weather.colormap()
            for surf in new_tileset.tile_set:
                weather_filter.transform_surface_ip(surf)
                res[weather] = new_tileset
            for frame_palette in new_tileset.animation_10.colors:
                for color in frame_palette:
                    weather_filter.transform_color_ip(color)
        return res

    def build_map(self):
        self.map = {}
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                self.map[x, y] = self.get_tile_coordinate((x, y))
        return self.map

    def get_tile_coordinate(self, position: tuple[int, int]) -> tuple[tuple[int, int], int]:
        p = self.floor.get_tile_mask(position)
        variant = random.choice([0,0,0,0,1,1,2,2])
        tile_type = self.floor[position].tile_type
        res = self.tileset.get_tile_position(tile_type, p, variant)
        if variant != 0 and not self.tileset.is_valid(self.tileset[res]):
            res = self.tileset.get_tile_position(tile_type, p)
        return res

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        ts = self.filtered_tilesets[self.status.weather]
        if not self.floor.in_inner_bounds(position):
            return ts.get_border_tile()
        if position == self.floor.stairs_spawn:
            if self.is_below:
                return tileset.STAIRS_DOWN_IMAGE
            else:
                return tileset.STAIRS_UP_IMAGE
        if self.floor.has_shop and self.floor[position].is_shop:
            return tileset.SHOP_IMAGE
        return ts[self.map[position]]
