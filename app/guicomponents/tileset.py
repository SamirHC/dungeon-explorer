from __future__ import annotations

import dataclasses
import os

import pygame
from app.model import animation
from app.dungeon import tile
from app.dungeon.colormap import ColorMap

from app.common.constants import IMAGES_DIRECTORY

STAIRS_DOWN_IMAGE = pygame.image.load(os.path.join(IMAGES_DIRECTORY, "stairs", "StairsDown.png"))
STAIRS_UP_IMAGE = pygame.image.load(os.path.join(IMAGES_DIRECTORY, "stairs", "StairsUp.png"))
SHOP_IMAGE = pygame.image.load(os.path.join(IMAGES_DIRECTORY, "traps", "KecleonCarpet.png"))

def get_tile_mask_to_position() -> dict[int, tuple[int, int]]:
    pattern_dir = os.path.join(IMAGES_DIRECTORY, "tilesets", "patterns.txt")
    res = {}
    with open(pattern_dir) as f:
        masks = f.read().splitlines()
    
    for i, mask in enumerate(masks):
        ns = [0]
        for j in range(8):
            if mask[j] == "1":
                ns = [(n << 1) + 1 for n in ns]
            elif mask[j] == "0":
                ns = [n << 1 for n in ns]
            elif mask[j] == "X":
                ns = [n << 1 for n in ns]
                ns += [n + 1 for n in ns]
            else:
                ns = []
                break
        for n in ns:
            res[n] = (i % 6, i // 6)
    return res

tile_masks = get_tile_mask_to_position()


@dataclasses.dataclass(frozen=True)
class Tileset:
    tileset_surfaces: tuple[pygame.Surface]
    tile_size: int
    invalid_color: pygame.Color
    animation_10: animation.PaletteAnimation
    animation_11: animation.PaletteAnimation
    terrains: dict[tile.TileType, tile.Terrain]
    minimap_color: tile.TileType
    underwater: bool

    def get_terrain(self, tile_type: tile.TileType) -> tile.Terrain:
        return self.terrains[tile_type]

    def __getitem__(self, position: tuple[tuple[int, int], int]) -> pygame.Surface:
        (x, y), v = position
        if self.is_valid(position):
            return self.tileset_surfaces[v].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))
        return self.tileset_surfaces[0].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))

    def get_tile_position(self, tile_type: tile.TileType, mask: int, variation: int=0) -> tuple[tuple[int, int], int]:
        return (self.get_position(tile_type, mask), variation)

    def get_position(self, tile_type: tile.TileType, mask: int) -> tuple[int, int]:
        x, y = tile_masks[mask]
        return (x + 6 * tile_type.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self[(1, 1), 0]

    def is_valid(self, position: tuple[tuple[int, int], int]) -> bool:
        (x, y), v = position
        if v == 0:
            return True
        topleft = (x*self.tile_size, y*self.tile_size)
        return self.tileset_surfaces[v].get_at(topleft) != self.invalid_color

    def update(self):
        if self.animation_10 is None and self.animation_11 is None:
            return
        updated = False
        if self.animation_10 is not None:
            updated = self.animation_10.update()
        if self.animation_11 is not None:
            updated |= self.animation_11.update()
        if not updated:
            return

        for surf in self.tileset_surfaces:
            if self.animation_10 is not None:
                palette = self.animation_10.current_palette()
                for i in range(16):
                    surf.set_palette_at(10*16+i, palette[i])
            if self.animation_11 is not None:
                palette = self.animation_11.current_palette()
                for i in range(16):
                    surf.set_palette_at(11*16+i, palette[i])

    def with_colormap(self, col_map: ColorMap) -> Tileset:
        tileset_surfaces = tuple([col_map.transform_surface(t) for t in self.tileset_surfaces])
        invalid_color = col_map.transform_color(self.invalid_color)
        animation_10 = None if self.animation_10 is None else col_map.transform_palette_animation(self.animation_10)
        animation_11 = None if self.animation_11 is None else col_map.transform_palette_animation(self.animation_11)
        return Tileset(
            tileset_surfaces,
            self.tile_size,
            invalid_color,
            animation_10,
            animation_11,
            self.terrains,
            self.minimap_color,
            self.underwater
        )
