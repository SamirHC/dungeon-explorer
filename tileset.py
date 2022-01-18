import os
import pattern
import pygame
import pygame.image
import tile


class TileSet:
    TILE_SET_DIR = os.path.join(os.getcwd(), "assets", "images", "tilesets")
    TRAP_IMAGE = pygame.image.load(os.path.join(
        os.getcwd(), "assets", "images", "traps", "WonderTile.png"))
    STAIRS_IMAGE = pygame.image.load(os.path.join(
        os.getcwd(), "assets", "images", "stairs", "StairsDown.png"))

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.tile_set: list[pygame.Surface] = []
        for i in range(3):
            tile_set_dir = os.path.join(
                TileSet.TILE_SET_DIR, dungeon_id, f"tileset_{i}.png")
            self.tile_set.append(pygame.image.load(tile_set_dir))

    def get_tile_size(self) -> int:
        return self.tile_set[0].get_width() // 18

    def get_tile_surface(self, terrain: tile.Terrain, pattern: pattern.Pattern, variation: int) -> pygame.Surface:
        tile_surface = self.tile_set[variation].subsurface(
            self.get_rect(terrain, pattern))
        return tile_surface

    def get_rect(self, terrain: tile.Terrain, pattern: pattern.Pattern) -> pygame.Rect:
        side_length = self.get_tile_size()
        x, y = self.get_position(terrain, pattern)
        return pygame.Rect((x * self.get_tile_size(), y * self.get_tile_size()), (side_length, side_length))

    def get_position(self, terrain: tile.Terrain, pattern: pattern.Pattern) -> tuple[int, int]:
        x, y = pattern.get_position()
        return (x + 6 * terrain.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self.get_tile_surface(tile.Terrain.WALL, pattern.Pattern.border_pattern(), 0)

    def get_stair_tile(self) -> pygame.Surface:
        return self.STAIRS_IMAGE

    def get_trap_tile(self) -> pygame.Surface:
        return self.TRAP_IMAGE
