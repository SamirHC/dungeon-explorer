import pygame

from app.common import constants
from app.dungeon.floor import Floor
from app.dungeon.trap import Trap
from app.guicomponents.minimapcomponents import MiniMapComponents


class Minimap:
    def __init__(self, floor: Floor, color: pygame.Color):
        self.components = MiniMapComponents(1, color)
        self.floor = floor
        self.visible = set()
        self.visible_rooms = set()
        self.surface = self.build_surface()

    def get_component(self, pos: tuple[int, int]) -> pygame.Surface:
        if pos not in self.visible and self.floor.is_tertiary(pos):
            return self.components.get_ground(
                self.floor.get_cardinal_tile_mask(pos), False
            )
        return (
            self.components.stairs 
            if self.floor.stairs_spawn == pos
            else self.components.wonder_tile
            if self.floor[pos].trap is Trap.WONDER_TILE
            else  self.components.trap
            if self.floor[pos].trap is not None
            else self.components.item
            if self.floor[pos].item_ptr is not None
            else self.components.get_ground(
                self.floor.get_cardinal_tile_mask(pos), True
            )
            if self.floor.is_tertiary(pos)
            else constants.EMPTY_SURFACE
        )

    def build_surface(self) -> pygame.Surface:
        size = self.get_scaled(self.floor.SIZE)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                dest = self.get_scaled((x, y))
                self.surface.blit(self.get_component((x, y)), dest)
        return self.surface

    def set_visible(self, position: tuple[int, int]):
        if self.floor.is_room(position) and self.floor[position].room_index not in self.visible_rooms:
            self.set_visible_room(self.floor[position].room_index)
        elif self.floor.is_tertiary(position):
            self.set_visible_surrounding(position)

    def set_visible_room(self, room: int):
        self.visible_rooms.add(room)
        for p in (
            (x, y)
            for x in range(self.floor.WIDTH)
            for y in range(self.floor.HEIGHT)
            if self.floor[x, y].room_index == room
        ):
            self.set_visible_surrounding(p)
        for p in self.floor.room_exits[room]:
            self.set_visible_at(p)

    def set_visible_at(self, position: tuple[int, int]):
        if position in self.visible:
            return
        self.visible.add(position)
        self.surface.blit(self.get_component(position), self.get_scaled(position))

    def set_visible_surrounding(self, position: tuple[int, int]):
        x, y = position
        for i in range(-1, 2):
            for j in range(-1, 2):
                self.set_visible_at((x + i, y + j))

    def get_scaled(self, position: tuple[int, int]) -> tuple[int, int]:
        x, y = position
        return (x * self.components.SIZE, y * self.components.SIZE)

    def update(self):
        self.set_visible(self.floor.party.leader.position)

    def render(self) -> pygame.Surface:
        surface = self.surface.copy()
        for p in self.floor.spawned:
            component = (
                self.components.enemy
                if p.is_enemy
                else self.components.user
                if p is self.floor.party.leader
                else self.components.ally
            )
            surface.blit(component, self.get_scaled(p.position))
        return surface
