import os
import pygame
import pygame.image


class ColorMap:
    def __init__(self, id_: int):
        path = os.path.join("assets", "images", "colormap", f"{id_}.png")
        self.surface = pygame.image.load(path)

    def __getitem__(self, value: int) -> pygame.Color:
        return self.surface.get_at((value % 16, value // 16))

    def get_r(self, value: int) -> int:
        return self[value].r

    def get_g(self, value: int) -> int:
        return self[value].g

    def get_b(self, value: int) -> int:
        return self[value].b

    def transform_color_ip(self, color: pygame.Color):
        color.update(self.transform_color(color))

    def transform_color(self, color: pygame.Color) -> pygame.Color:
        r = self.get_r(color.r)
        g = self.get_g(color.g)
        b = self.get_b(color.b)
        return pygame.Color(r, g, b)

    def transform_surface_ip(self, surface: pygame.Surface):
        surface.set_palette([self.transform_color(color) for color in surface.get_palette()])

    def transform_surface(self, surface: pygame.Surface) -> pygame.Surface:
        new_surface = surface.copy()
        self.transform_surface_ip(new_surface)
        return new_surface