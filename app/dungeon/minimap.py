import pygame

from app.common import constants
from app.dungeon.floor import Floor
from app.dungeon.trap import Trap
from app.dungeon.darkness_level import DarknessLevel
from app.db.minimap_components import MinimapComponents, Visibility


class Minimap:
    def __init__(
        self,
        floor: Floor,
        color: pygame.Color,
        darkness_level: DarknessLevel = DarknessLevel.NO_DARKNESS,
    ):
        self.components = MinimapComponents(1, color)
        self.darkness_level = darkness_level
        self.floor = floor
        self.visible_tiles = set()
        self.visible_rooms = set()

        self.surface_size = self._scale(self.floor.SIZE)

        self.lower_surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                pos = self._scale((x, y))
                self.lower_surface.blit(self.get_component((x, y)), pos)

        self.upper_surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)

    def update(self):
        self.set_visible(self.floor.party.leader.position)

    def render(self) -> pygame.Vector2:
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        surface.blit(self.lower_surface, (0, 0))
        surface.blit(self.upper_surface, (0, 0))

        surface.blits(
            (self.components.enemy, self._scale(p.position))
            for p in self.floor.active_enemies
        )
        surface.blit(
            self.components.user,
            self._scale(self.floor.party.leader.position),
        )
        surface.blits(
            (self.components.ally, self._scale(p.position))
            for p in self.floor.party
            if p is not self.floor.party.leader
        )

        return surface

    def _scale(self, pos: tuple[int, int]) -> pygame.Vector2:
        return pygame.Vector2(pos) * self.components.SIZE

    def get_component(self, pos: tuple[int, int]) -> pygame.Surface:
        if pos not in self.visible_tiles and self.floor.is_tertiary(pos):
            return self.components.get_ground(
                self.floor.get_cardinal_tile_mask(pos), Visibility.PART
            )
        if self.floor.stairs_spawn == pos:
            return self.components.stairs
        if self.floor[pos].trap is Trap.WONDER_TILE:
            return self.components.wonder_tile
        if self.floor[pos].trap is not None:
            return self.components.trap
        if self.floor[pos].item_ptr is not None:
            return self.components.item
        if self.floor.is_tertiary(pos):
            return self.components.get_ground(
                self.floor.get_cardinal_tile_mask(pos), Visibility.FULL
            )
        return constants.EMPTY_SURFACE

    def set_visible(self, position: tuple[int, int]):
        if (
            self.floor.is_room(position)
            and self.floor[position].room_index not in self.visible_rooms
        ):
            self.set_visible_room(self.floor[position].room_index)
        elif not self.floor.is_room(position):
            self.set_visible_surrounding(
                position,
                radius=1 if self.darkness_level is DarknessLevel.HEAVY_DARKNESS else 2,
            )

    def set_visible_room(self, room: int):
        self.visible_rooms.add(room)
        for p in (
            (x, y)
            for x in range(self.floor.WIDTH)
            for y in range(self.floor.HEIGHT)
            if self.floor[x, y].room_index == room
        ):
            self.set_visible_surrounding(p)

    def set_visible_at(self, position: tuple[int, int]):
        if (
            not 0 <= position[0] < self.floor.WIDTH
            or not 0 <= position[1] < self.floor.HEIGHT
        ):
            return
        if position in self.visible_tiles:
            return
        self.visible_tiles.add(position)
        self.upper_surface.blit(self.get_component(position), self._scale(position))
        offset_x, offset_y = (c * self.components.SIZE for c in position)
        for x in range(self.components.SIZE):
            for y in range(self.components.SIZE):
                self.lower_surface.set_at(
                    (x + offset_x, y + offset_y), constants.TRANSPARENT
                )

    def set_visible_surrounding(self, position: tuple[int, int], radius=1):
        x, y = position
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                self.set_visible_at((x + i, y + j))
