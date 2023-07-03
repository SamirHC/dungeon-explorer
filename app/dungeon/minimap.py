import pygame

from app.dungeon import dungeon, trap
from app.guicomponents.minimapcomponents import MiniMapComponents


class MiniMap:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.components = MiniMapComponents(1, dungeon.tileset.minimap_color)
        self.dungeon = dungeon
        self.visible = set()
        self.surface = self.build_surface()

    @property
    def floor(self):
        return self.dungeon.floor

    @property
    def user(self):
        return self.dungeon.user

    @property
    def allies(self):
        return self.dungeon.party

    @property
    def enemies(self):
        return self.dungeon.active_enemies

    def build_surface(self):
        size = self.get_scaled(self.floor.SIZE)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        for pos in [(x, y) for x in range(self.floor.WIDTH) for y in range(self.floor.HEIGHT)]:
            component = None
            if self.floor.is_ground(pos):
                component = self.components.get_ground(self.floor.get_cardinal_tile_mask(pos), pos in self.visible)
            if pos in self.visible:
                if self.floor.stairs_spawn == pos:
                    component = self.components.stairs
                elif self.floor[pos].trap is trap.Trap.WONDER_TILE:
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
        elif self.floor.is_ground(position):
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
        elif self.floor[position].trap is trap.Trap.WONDER_TILE:
            component = self.components.wonder_tile
        elif self.floor[position].trap is not None:
            component = self.components.trap
        elif self.floor.is_ground(position):
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
        self.set_visible(self.dungeon.user.position)

    def render(self) -> pygame.Surface:
        surface = self.surface.copy()
        for ally in self.allies:
            surface.blit(self.components.ally, self.get_scaled(ally.position))
        surface.blit(self.components.user, self.get_scaled(self.user.position))
        for enemy in self.enemies:
            surface.blit(self.components.enemy, self.get_scaled(enemy.position))
        return surface
