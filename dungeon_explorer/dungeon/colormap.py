import os
import pygame
import pygame.image

from dungeon_explorer.common import animation
from dungeon_explorer.dungeon.dungeonstatus import Weather


class ColorMap:
    def __init__(self, colors: list[pygame.Color]):
        self.colors = colors

    def __getitem__(self, value: int) -> pygame.Color:
        return self.colors[value]

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

    def transform_palette_animation(self, anim: animation.PaletteAnimation) -> animation.PaletteAnimation:
        frames = anim.frames
        durations = anim.durations
        new_frames = [[self.transform_color(col) for col in palette] for palette in frames]
        return animation.PaletteAnimation(new_frames, durations)


class ColorMapDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "colormap")
        self.loaded: dict[Weather, ColorMap]  = {}

    def __getitem__(self, weather: Weather):
        if weather not in self.loaded:
            self.load(weather)
        return self.loaded[weather]

    def load(self, weather: Weather):
        surface_path = os.path.join(self.base_dir, f"{weather.value}.png")
        surface = pygame.image.load(surface_path)
        colors = [surface.get_at((i % 16, i // 16)) for i in range(256)]
        self.loaded[weather] = ColorMap(colors)


db = ColorMapDatabase()
