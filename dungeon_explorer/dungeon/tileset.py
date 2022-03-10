import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import animation
from dungeon_explorer.dungeon import tile

WONDER_TILE_IMAGE = pygame.image.load(os.path.join("assets", "images", "traps", "WonderTile.png"))
STAIRS_DOWN_IMAGE = pygame.image.load(os.path.join("assets", "images", "stairs", "StairsDown.png"))
STAIRS_UP_IMAGE = pygame.image.load(os.path.join("assets", "images", "stairs", "StairsUp.png"))
SHOP_IMAGE = pygame.image.load(os.path.join("assets", "images", "traps", "KecleonCarpet.png"))


class TileSet:
    TILE_SET_DIR = os.path.join("assets", "images", "tilesets")

    def __init__(self, tileset_id: str):
        self.tileset_id = tileset_id
        self.tile_masks = self.get_tile_masks()

        base_dir = os.path.join(TileSet.TILE_SET_DIR, tileset_id)
        self.metadata = ET.parse(os.path.join(base_dir, "tileset.dtef.xml")).getroot()
        self.tile_size = int(self.metadata.get("dimensions"))
        self.animation_10_node, self.animation_11_node = self.metadata.findall("Animation")
        self.is_animated_10 = bool(list(self.animation_10_node))
        self.is_animated_11 = bool(list(self.animation_11_node))
        if self.is_animated_10:
            self.animation_10 = self.get_animation_10()
        if self.is_animated_11:
            self.animation_11 = self.get_animation_11()

        self.tile_set: list[pygame.Surface] = []
        for i in range(3):
            self.tile_set.append(pygame.image.load(os.path.join(base_dir, f"tileset_{i}.png")))

        self.invalid_color = self.tile_set[0].get_at((5*self.tile_size, 2*self.tile_size))

    def get_tile_masks(self) -> list[tile.TileMask]:
        pattern_dir = os.path.join("assets", "images", "tilesets", "patterns.txt")
        with open(pattern_dir) as f:
            return [tile.TileMask(line) for line in f.read().splitlines()]

    def get_animation_10(self) -> animation.PaletteAnimation:
        return self.get_animation(self.animation_10_node)

    def get_animation_11(self) -> animation.PaletteAnimation:
        return self.get_animation(self.animation_11_node)

    def get_animation(self, node) -> animation.PaletteAnimation:
        return animation.PaletteAnimation(node)

    def __getitem__(self, position: tuple[tuple[int, int], int]) -> pygame.Surface:
        (x, y), v = position
        return self.tile_set[v].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))

    def get_tile_position(self, terrain: tile.Terrain, pattern: tile.TileMask, variation: int=0) -> tuple[tuple[int, int], int]:
        return (self.get_position(terrain, pattern), variation)

    def get_position(self, terrain: tile.Terrain, mask: tile.TileMask) -> tuple[int, int]:
        for i, p in enumerate(self.tile_masks):
            if i == 17:
                continue
            if p.matches(mask):
                x, y = (i % 6, i // 6)
                break
        return (x + 6 * terrain.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self[(1, 1), 0]

    def is_valid(self, tile_surface: pygame.Surface) -> bool:
        return tile_surface.get_at((0, 0)) != self.invalid_color

    def update(self):
        if not (self.is_animated_10 or self.is_animated_11):
            return

        updated = False
        if self.is_animated_10:
            updated = self.animation_10.update()
        if self.is_animated_11:
            updated = self.animation_11.update() or updated
        if not updated:
            return

        for surf in self.tile_set:
            if self.is_animated_10:
                palette = self.animation_10.current_palette()
                for i in range(16):
                    surf.set_palette_at(10*16+i, palette[i])
            if self.is_animated_11:
                palette = self.animation_11.current_palette()
                for i in range(16):
                    surf.set_palette_at(11*16+i, palette[i])
