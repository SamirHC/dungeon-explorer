from . import dungeon_map, pattern, tile
import os
import pygame
import pygame.image


class MiniMap:
    COMPONENT_SIZE = 4
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

    def __init__(self, floor: dungeon_map.Floor):
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
        offset = 0
        if not is_filled:
            offset = 2
        p = pattern.Pattern(tile.Terrain.GROUND, self.dungeon_map.surrounding_terrain(position))
        for pat, (x, y) in MiniMap.pattern_dict.items():
            if p.matches(pat):
                size = MiniMap.COMPONENT_SIZE
                rect = pygame.Rect(size*x, size*(y+2+offset), size, size)
                self[position] = self.minimap_components.subsurface(rect)

    def render(self) -> pygame.Surface:
        surface = pygame.Surface((4*self.dungeon_map.WIDTH, 4*self.dungeon_map.HEIGHT), pygame.SRCALPHA)
        for (x, y), item in self._minimap.items():
            surface.blit(item, (x*4, y*4))
        x, y = self.dungeon_map.stairs_spawn
        surface.blit(self.minimap_components.subsurface(pygame.Rect(4*6, 0, 4, 4)), (x*4, y*4))
        return surface

    def user_dot(self) -> pygame.Surface:
        return self.minimap_components.subsurface(pygame.Rect(0, 4, 4, 4))

    def enemy_dot(self) -> pygame.Surface:
        return self.minimap_components.subsurface(pygame.Rect(2*4, 0, 4, 4))

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        return self._minimap.get(position, self.minimap_components.subsurface(pygame.Rect(0, 0, 4, 4)))

    def __setitem__(self, position: tuple[int, int], item: pygame.Surface):
        self._minimap[position] = item

