import dungeon_map
import os
import pattern
import pygame
import pygame.constants
import pygame.image
import tile


class MiniMap:
    def __init__(self, dungeon_map: dungeon_map.AbstractDungeonMap):
        self.dungeon_map = dungeon_map
        variation = 1
        file = os.path.join(os.getcwd(), "assets", "images", "misc", f"minimap{variation}.png")
        self.minimap_components = pygame.image.load(file)
        self.minimap_components.set_colorkey(self.minimap_components.get_at((0, 0)))
        self._minimap: dict[tuple[int, int], pygame.Surface] = {}
        self.update()

    def update(self):
        for x, y in self.dungeon_map.hallways:
            self.set_pattern(x, y)
        for room in self.dungeon_map.rooms:
            for x, y in room:
                self.set_pattern(x, y)
            
    def set_pattern(self, x, y, is_filled=True):
        offset = 0
        if not is_filled:
            offset = 2*4
        p = pattern.Pattern(tile.Terrain.GROUND, [t.terrain for t in self.dungeon_map.get_surrounding_tiles_at(x, y)])
        if p.matches("X1X11X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(0, 4*2 + offset, 4, 4))
        elif p.matches("X1X11X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*1, 4*2 + offset, 4, 4))
        elif p.matches("X1X10X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*2, 4*2 + offset, 4, 4))
        elif p.matches("X1X10X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*3, 4*2 + offset, 4, 4))
        elif p.matches("X0X11X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*4, 4*2 + offset, 4, 4))
        elif p.matches("X0X11X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*5, 4*2 + offset, 4, 4))
        elif p.matches("X0X10X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*6, 4*2 + offset, 4, 4))
        elif p.matches("X0X10X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*7, 4*2 + offset, 4, 4))
        elif p.matches("X1X01X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(0, 4*3 + offset, 4, 4))
        elif p.matches("X1X01X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*1, 4*3 + offset, 4, 4))
        elif p.matches("X1X00X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*2, 4*3 + offset, 4, 4))
        elif p.matches("X1X00X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*3, 4*3 + offset, 4, 4))
        elif p.matches("X0X01X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*4, 4*3 + offset, 4, 4))
        elif p.matches("X0X01X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*5, 4*3 + offset, 4, 4))
        elif p.matches("X0X00X1X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*6, 4*3 + offset, 4, 4))
        elif p.matches("X0X00X0X"):
            self[x, y] = self.minimap_components.subsurface(pygame.Rect(4*7, 4*3 + offset, 4, 4))
        else:
            print("Could not match pattern")

    def render(self) -> pygame.Surface:
        surface = pygame.Surface((4*self.dungeon_map.WIDTH, 4*self.dungeon_map.HEIGHT), pygame.constants.SRCALPHA)
        for (x, y), item in self._minimap.items():
            surface.blit(item, (x*4, y*4))
        x, y = self.dungeon_map.stairs_coords
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

