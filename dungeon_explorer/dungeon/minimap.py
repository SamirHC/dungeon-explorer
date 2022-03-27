import os

import pygame
import pygame.image
from dungeon_explorer.dungeon import dungeon, tile


class MiniMapComponents:
    SIZE = 4
    pattern_dict: dict[str, tuple[int, int]] = {
        "X1X11X1X": (0, 0),
        "X1X11X0X": (1, 0),
        "X1X10X1X": (2, 0),
        "X1X10X0X": (3, 0),
        "X0X11X1X": (4, 0),
        "X0X11X0X": (5, 0),
        "X0X10X1X": (6, 0),
        "X0X10X0X": (7, 0),
        "X1X01X1X": (0, 1),
        "X1X01X0X": (1, 1),
        "X1X00X1X": (2, 1),
        "X1X00X0X": (3, 1),
        "X0X01X1X": (4, 1),
        "X0X01X0X": (5, 1),
        "X0X00X1X": (6, 1),
        "X0X00X0X": (7, 1)
    }

    def __init__(self, variation: int, color: pygame.Color):
        self.variation = self.update_variation(variation)
        self.color = color

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        return self.components.subsurface((x*self.SIZE, y*self.SIZE), (self.SIZE, self.SIZE))

    def update_variation(self, value):
        file = os.path.join("assets", "images", "minimap", f"minimap{value}.png")
        self.components = pygame.image.load(file)
        self.components.set_colorkey(self.components.get_at((0, 0)))
    
    @property
    def enemy(self) -> pygame.Surface:
        return self[2, 0]

    @property
    def item(self) -> pygame.Surface:
        return self[3, 0]

    @property
    def trap(self) -> pygame.Surface:
        return self[4, 0]

    @property
    def warp_zone(self) -> pygame.Surface:
        return self[5, 0]

    @property
    def stairs(self) -> pygame.Surface:
        return self[6, 0]

    @property
    def wonder_tile(self) -> pygame.Surface:
        return self[7, 0]

    @property
    def user(self) -> pygame.Surface:
        return self[0, 1]

    @property
    def ally(self) -> pygame.Surface:
        return self[2, 1]

    @property
    def hidden_stairs(self) -> pygame.Surface:
        return self[5, 1]

    def get_ground(self, mask: tile.TileMask, is_filled: bool = True) -> pygame.Surface:
        offset = 2 if is_filled else 4
        for pattern, (x, y) in MiniMapComponents.pattern_dict.items():
            if mask.matches(tile.TileMask(pattern)):
                surface = self[x, y+offset]
                surface.set_palette_at(7, self.color)
                return surface


class MiniMap:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.components = MiniMapComponents(1, dungeon.tileset.minimap_color)
        self.floor = dungeon.floor
        self.user = dungeon.user
        self.allies = dungeon.party
        self.enemies = dungeon.active_enemies
        self.visible = set()
        self.surface = self.build_surface()

    def build_surface(self):
        size = self.get_scaled(self.floor.SIZE)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        for position in self.floor:
            if self.floor.is_ground(position):
                self.blit_ground(position)
        return self.surface

    def set_visible(self, position: tuple[int, int]):
        if self.floor.is_room(position):
            self.set_visible_room(self.floor[position].room_index)
        elif self.floor.is_ground(position):
            self.set_visible_surrounding(position)

    def set_visible_room(self, room: int):
        for p in self.floor:
            if self.floor[p].room_index == room:
                self.set_visible_surrounding(p)
        for p in self.floor.room_exits[room]:
            self.set_visible_at(p)

    def set_visible_at(self, position: tuple[int, int]):
        if position in self.visible:
            return
        self.visible.add(position)
        if self.floor.stairs_spawn == position:
            self.surface.blit(self.components.stairs, self.get_scaled(position))
            return
        if self.floor.is_ground(position):
            self.blit_ground(position)

    def set_visible_surrounding(self, position: tuple[int, int]):
        x, y = position
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_pos = (x+i, y+j)
                self.set_visible_at(new_pos)
    
    def get_scaled(self, position: tuple[int, int]) -> tuple[int, int]:
        x, y = position
        return (x*self.components.SIZE, y*self.components.SIZE)

    def blit_ground(self, position):
        component = self.components.get_ground(self.floor.get_tile_mask(position), position in self.visible)
        self.surface.blit(component, self.get_scaled(position))

    def render(self) -> pygame.Surface:
        surface = self.surface.copy()
        for ally in self.allies:
            surface.blit(self.components.ally, self.get_scaled(ally.position))
        surface.blit(self.components.user, self.get_scaled(self.user.position))
        for enemy in self.enemies:
            surface.blit(self.components.enemy, self.get_scaled(enemy.position))
        return surface
    