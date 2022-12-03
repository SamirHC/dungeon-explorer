import pygame
import pygame.image

from app.model import animation


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

    def transform_surface_colors(self, surface: pygame.Surface, colors: list[pygame.Color]):
        px_arr = pygame.PixelArray(surface.copy())
        for c in colors:
            px_arr.replace(c, self.transform_color(c))
        return px_arr.make_surface()
