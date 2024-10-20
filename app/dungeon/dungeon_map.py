import pygame

from app.common.constants import RNG as random
import app.db.trap as trap_db
import app.db.tileset as tileset_db
import app.db.dungeon_data as dungeon_data_db
from app.dungeon.dungeon import Dungeon


class DungeonMap:
    def __init__(self, dungeon: Dungeon):
        self.floor = dungeon.floor
        self.tileset = self.floor.tileset

        self.stairs_surface = (
            tileset_db.STAIRS_DOWN_IMAGE
            if dungeon_data_db.load(dungeon.dungeon_id).is_below
            else tileset_db.STAIRS_UP_IMAGE
        )
        self.map = self.build_map()

    def build_map(self):
        self.map = {}
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                self.map[x, y] = self.get_tile_coordinate((x, y))
        return self.map

    def get_tile_coordinate(
        self, position: tuple[int, int]
    ) -> tuple[tuple[int, int], int]:
        mask = self.floor.get_tile_mask(position)
        variant = random.choice([0, 0, 0, 0, 1, 1, 2, 2])
        tile_type = self.floor[position].tile_type
        return self.tileset.get_tile_position(tile_type, mask, variant)

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        return (
            self.tileset.get_border_tile()
            if not self.floor.in_inner_bounds(position)
            else (
                self.stairs_surface
                if position == self.floor.stairs_spawn
                else (
                    tileset_db.SHOP_IMAGE
                    if self.floor.has_shop and self.floor[position].is_shop
                    else (
                        trap_db.load(self.floor[position].trap)
                        if self.floor[position].trap is not None
                        else self.tileset[self.map[position]]
                    )
                )
            )
        )

    def render(self, camera: pygame.Rect) -> pygame.Surface:
        TILE_SIZE = self.floor.tileset.tile_size

        floor_surface = pygame.Surface(
            pygame.Vector2(self.floor.WIDTH + 10, self.floor.HEIGHT + 10) * TILE_SIZE
        )
        tile_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        for xi, x in enumerate(range(-5, self.floor.WIDTH + 5)):
            for yi, y in enumerate(range(-5, self.floor.HEIGHT + 5)):
                tile_rect.topleft = xi * TILE_SIZE, yi * TILE_SIZE
                if tile_rect.colliderect(camera):
                    tile_surface = self[x, y]
                    floor_surface.blit(tile_surface, tile_rect)
                    item = self.floor[x, y].item_ptr
                    if item is not None:
                        floor_surface.blit(item.surface, tile_rect.move(4, 4))
        return floor_surface
