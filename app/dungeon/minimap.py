import pygame

from app.dungeon.floor import Floor
from app.dungeon.trap import Trap
from app.guicomponents.minimapcomponents import MiniMapComponents
from app.pokemon import pokemon


class MiniMap:
    def __init__(self, floor: Floor, color: pygame.Color):
        self.components = MiniMapComponents(1, color)
        self.floor = floor
        self.visible = set()
        self.surface = self.build_surface()

    def build_surface(self):
        size = self.get_scaled(self.floor.SIZE)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        for pos in [(x, y) for x in range(self.floor.WIDTH) for y in range(self.floor.HEIGHT)]:
            component = None
            if self.floor.is_tertiary(pos):
                component = self.components.get_ground(self.floor.get_cardinal_tile_mask(pos), pos in self.visible)
            if pos in self.visible:
                if self.floor.stairs_spawn == pos:
                    component = self.components.stairs
                elif self.floor[pos].trap is Trap.WONDER_TILE:
                    component = self.components.wonder_tile
                elif self.floor[pos].trap is not None:
                    component = self.components.trap
            if component is not None:
                dest = self.get_scaled(pos)
                self.surface.blit(component, dest)
        return self.surface

    def set_visible(self, position: tuple[int, int]):
        if self.floor.is_room(position):
            if position in self.visible:
                return
            self.set_visible_room(self.floor[position].room_index)
        elif self.floor.is_tertiary(position):
            self.set_visible_surrounding(position)

    def set_visible_room(self, room: int):
        for p in [(x, y) for x in range(self.floor.WIDTH) for y in range(self.floor.HEIGHT)]:
            if self.floor[p].room_index == room:
                self.set_visible_surrounding(p)
        for p in self.floor.room_exits[room]:
            self.set_visible_at(p)

    def set_visible_at(self, position: tuple[int, int]):
        if position in self.visible:
            return
        self.visible.add(position)
        component = None
        if self.floor.stairs_spawn == position:
            component = self.components.stairs
        elif self.floor[position].trap is Trap.WONDER_TILE:
            component = self.components.wonder_tile
        elif self.floor[position].trap is not None:
            component = self.components.trap
        elif self.floor.is_tertiary(position):
            component = self.components.get_ground(self.floor.get_cardinal_tile_mask(position), position in self.visible)
        if component is None:
            return
        self.surface.blit(component, self.get_scaled(position))

    def set_visible_surrounding(self, position: tuple[int, int]):
        x, y = position
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_pos = (x+i, y+j)
                self.set_visible_at(new_pos)
    
    def get_scaled(self, position: tuple[int, int]) -> tuple[int, int]:
        x, y = position
        return (x*self.components.SIZE, y*self.components.SIZE)

    def update(self):
        self.set_visible(self.floor.party.leader.position)

    def render(self) -> pygame.Surface:
        surface = self.surface.copy()
        for p in self.floor.spawned:
            if isinstance(p, pokemon.EnemyPokemon):
                component = self.components.enemy
            elif isinstance(p, pokemon.UserPokemon):
                if p is self.floor.party.leader:
                    component = self.components.user
                else:
                    component = self.components.ally
            surface.blit(component, self.get_scaled(p.position))
        return surface
