from . import floor, tile
import os
import pygame
import pygame.image


class MiniMapComponents:
    COMPONENT_WIDTH = 4
    COMPONENT_HEIGHT = 4
    COMPONENT_SIZE = (COMPONENT_WIDTH, COMPONENT_HEIGHT)
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

    def __init__(self, floor: floor.Floor):
        self.dungeon_map = floor
        variation = 1
        file = os.path.join(os.getcwd(), "assets", "images", "misc", f"minimap{variation}.png")
        self.minimap_components = pygame.image.load(file)
        self.minimap_components.set_colorkey(self.minimap_components.get_at((0, 0)))
        self._minimap: dict[tuple[int, int], pygame.Surface] = {}
        self.update()

    def update(self):
        for position in self.dungeon_map:
            if self.dungeon_map[position].terrain is tile.Terrain.GROUND:
                self.set_pattern(position)
            
    def set_pattern(self, position: tuple[int, int], is_filled: bool = True):
        offset = 2 if is_filled else 4
        p = self.dungeon_map.get_tile_mask(position)
        for pat, (x, y) in MiniMapComponents.pattern_dict.items():
            if p.matches(tile.TileMask(pat)):
                self[position] = self.get_component((x, y+offset))

    def render(self) -> pygame.Surface:
        surface = pygame.Surface((4*self.dungeon_map.WIDTH, 4*self.dungeon_map.HEIGHT), pygame.SRCALPHA)
        for (x, y), item in self._minimap.items():
            surface.blit(item, (x*4, y*4))
        x, y = self.dungeon_map.stairs_spawn
        surface.blit(self.get_component((6, 0)), (x*4, y*4))
        return surface

    def user_dot(self) -> pygame.Surface:
        return self.get_component((0, 1))

    def enemy_dot(self) -> pygame.Surface:
        return self.get_component((2, 0))

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        return self._minimap.get(position, self.get_component((0, 0)))

    def __setitem__(self, position: tuple[int, int], item: pygame.Surface):
        self._minimap[position] = item

    def get_component(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        return self.minimap_components.subsurface((x*MiniMapComponents.COMPONENT_WIDTH, y*MiniMapComponents.COMPONENT_HEIGHT), MiniMapComponents.COMPONENT_SIZE)