import os
from . import tile
import pygame
import pygame.image
import xml.etree.ElementTree as ET

WONDER_TILE_IMAGE = pygame.image.load(os.path.join(os.getcwd(), "assets", "images", "traps", "WonderTile.png"))
STAIRS_DOWN_IMAGE = pygame.image.load(os.path.join(os.getcwd(), "assets", "images", "stairs", "StairsDown.png"))
SHOP_IMAGE = pygame.image.load(os.path.join(os.getcwd(), "assets", "images", "traps", "KecleonCarpet.png"))


class TileSet:
    TILE_SET_DIR = os.path.join(os.getcwd(), "assets", "images", "tilesets")

    def __init__(self, tileset_id: str):
        self.tileset_id = tileset_id
        self.tile_masks = self.get_tile_masks()

        base_dir = os.path.join(TileSet.TILE_SET_DIR, tileset_id)
        self.metadata = ET.parse(os.path.join(base_dir, "tileset.dtef.xml")).getroot()
        self.tile_size = int(self.metadata.get("dimensions"))

        self.tile_set: list[pygame.Surface] = []
        for i in range(3):
            self.tile_set.append(pygame.image.load(os.path.join(base_dir, f"tileset_{i}.png")))

        self.invalid_color = self.tile_set[0].get_at((5*self.tile_size, 2*self.tile_size))

    def get_tile_masks(self) -> list[tile.TileMask]:
        pattern_dir = os.path.join(os.getcwd(), "assets", "images", "tilesets", "patterns.txt")
        with open(pattern_dir) as f:
            return [tile.TileMask(line) for line in f.read().splitlines()]

    def get_tile_surface(self, terrain: tile.Terrain, pattern: tile.TileMask, variation: int=0) -> pygame.Surface:
        return self.tile_set[variation].subsurface(self.get_rect(terrain, pattern))

    def get_rect(self, terrain: tile.Terrain, pattern: tile.TileMask) -> pygame.Rect:
        x, y = self.get_position(terrain, pattern)
        return pygame.Rect((x * self.tile_size, y * self.tile_size), (self.tile_size, self.tile_size))

    def get_position(self, terrain: tile.Terrain, mask: tile.TileMask) -> tuple[int, int]:
        for i, p in enumerate(self.tile_masks):
            if i == 17:
                continue
            if p.matches(mask):
                x, y = (i % 6, i // 6)
                break
        return (x + 6 * terrain.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self.get_tile_surface(tile.Terrain.WALL, tile.TileMask.border())

    def is_valid(self, tile_surface: pygame.Surface) -> bool:
        return tile_surface.get_at((0, 0)) != self.invalid_color

