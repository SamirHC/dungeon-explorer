import os
import pattern
import pygame
import pygame.image
import tile

class TileSet:
    TILE_SET_DIR = os.path.join(os.getcwd(), "assets", "tilesets")
    TRAP_IMAGE = pygame.image.load(os.path.join(os.getcwd(), "images", "Traps", "WonderTile.png"))
    STAIRS_IMAGE = pygame.image.load(os.path.join(os.getcwd(), "images", "Stairs", "StairsDown.png"))

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.tile_set: list[pygame.Surface] = []
        for i in range(3):
            tile_set_dir = os.path.join(TileSet.TILE_SET_DIR, dungeon_id, f"tileset_{i}.png")
            self.tile_set.append(pygame.image.load(tile_set_dir))

    def get_tile_size(self) -> int:
        return self.tile_set[0].get_width() // 18

    def get_tile_surface(self, tile: tile.Tile, pattern: pattern.Pattern, variation: int) -> pygame.Surface:
        tile_surface = self.tile_set[variation].subsurface(self.get_rect(tile, pattern))
        return tile_surface

    def get_rect(self, tile: tile.Tile, pattern: pattern.Pattern) -> pygame.Rect:
        side_length = self.get_tile_size()
        row_col = self.get_row_col(tile, pattern)
        return pygame.Rect((row_col[1] * self.get_tile_size(), row_col[0] * self.get_tile_size()), (side_length, side_length))
    
    def get_row_col(self, tile: tile.Tile, pattern: pattern.Pattern) -> tuple[int, int]:
        row_col = pattern.get_row_col()
        return (row_col[0], row_col[1] + 6 * tile.value)

    def get_border_tile(self):
        return self.get_tile_surface(tile.Tile.WALL, pattern.Pattern.border_pattern(), 0)

    def get_stair_tile(self):
        return self.STAIRS_IMAGE

    def get_trap_tile(self):
        return self.TRAP_IMAGE
