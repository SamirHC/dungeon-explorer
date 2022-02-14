from . import floor, tile
import os
import pygame
import pygame.image


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

    def __init__(self, variation: int):
        self.variation = self.update_variation(variation)

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        return self.components.subsurface((x*self.SIZE, y*self.SIZE), (self.SIZE, self.SIZE))

    def update_variation(self, value):
        file = os.path.join(os.getcwd(), "assets", "images", "misc", f"minimap{value}.png")
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
                return self[x, y+offset]


class MiniMap:
    def __init__(self, floor: floor.Floor):
        self.components = MiniMapComponents(1)
        self.floor = floor
        self.visible = {}
        self.minimap = {}
        self.surface = self.build_surface()

    def __setitem__(self, position: tuple[int, int], value: tuple[int, int]):
        self.minimap[position] = value

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        return self.minimap.get(position, self.components[0, 0])

    def update(self, position: tuple[int, int]):
        if position in self.visible:
            return
        if self.floor.is_room(position):
            for p in self.floor:
                if self.floor[p].room_index == self.floor[position].room_index:
                    self.visible[p] = True
            self.surface = self.build_surface()
        elif self.floor.is_ground(position):
            x, y = position
            for i in range(-1, 2):
                for j in range(-1, 2):
                    self.visible[x+i, y+j] = True
            self.surface = self.build_surface()

    def build_surface(self):
        surface = pygame.Surface((4*self.floor.WIDTH, 4*self.floor.HEIGHT), pygame.SRCALPHA)
        for x, y in self.floor:
            if self.floor.is_ground((x, y)):
                self.minimap[x, y] = self.components.get_ground(self.floor.get_tile_mask((x, y)), self.visible.get((x, y), False))

        for (x, y), item in self.minimap.items():
            surface.blit(item, (x*self.components.SIZE, y*self.components.SIZE))
        if self.floor.stairs_spawn in self.visible:
            x, y = self.floor.stairs_spawn
            surface.blit(self.components.stairs, (x*self.components.SIZE, y*self.components.SIZE))

        return surface

    def render(self) -> pygame.Surface:
        return self.surface