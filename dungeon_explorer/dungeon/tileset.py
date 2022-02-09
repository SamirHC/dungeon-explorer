import os
from . import pattern, tile
import pygame
import pygame.image
import xml.etree.ElementTree as ET


class TileSet:
    TILE_SET_DIR = os.path.join(os.getcwd(), "assets", "images", "tilesets")
    TRAP_IMAGE = pygame.image.load(os.path.join(
        os.getcwd(), "assets", "images", "traps", "WonderTile.png"))
    STAIRS_IMAGE = pygame.image.load(os.path.join(
        os.getcwd(), "assets", "images", "stairs", "StairsDown.png"))
    SHOP_IMAGE = pygame.image.load(os.path.join(
        os.getcwd(), "assets", "images", "traps", "KecleonCarpet.png"))

    def __init__(self, tileset_id: str):
        self.tileset_id = tileset_id

        base_dir = os.path.join(TileSet.TILE_SET_DIR, tileset_id)
        self.metadata = ET.parse(os.path.join(base_dir, "tileset.dtef.xml")).getroot()
        self.tile_size = int(self.metadata.get("dimensions"))

        self.tile_set: list[pygame.Surface] = []
        for i in range(3):
            self.tile_set.append(pygame.image.load(os.path.join(base_dir, f"tileset_{i}.png")))

    def get_tile_surface(self, terrain: tile.Terrain, pattern: pattern.Pattern, variation: int=0) -> pygame.Surface:
        return self.tile_set[variation].subsurface(self.get_rect(terrain, pattern))

    def get_rect(self, terrain: tile.Terrain, pattern: pattern.Pattern) -> pygame.Rect:
        x, y = self.get_position(terrain, pattern)
        return pygame.Rect((x * self.tile_size, y * self.tile_size), (self.tile_size, self.tile_size))

    def get_position(self, terrain: tile.Terrain, pattern: pattern.Pattern) -> tuple[int, int]:
        x, y = pattern.get_position()
        return (x + 6 * terrain.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self.get_tile_surface(tile.Terrain.WALL, pattern.Pattern.border_pattern())

    def get_stair_tile(self) -> pygame.Surface:
        return self.STAIRS_IMAGE

    def get_trap_tile(self) -> pygame.Surface:
        return self.TRAP_IMAGE

    def get_shop_tile(self) -> pygame.Surface:
        return self.SHOP_IMAGE
