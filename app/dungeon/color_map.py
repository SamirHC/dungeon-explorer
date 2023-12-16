import pygame
import pygame.image
import numpy as np


class ColorMap:
    def __init__(self, colors: list[pygame.Color]):
        self.colors = colors

    def __getitem__(self, value: int) -> pygame.Color:
        return self.colors[value]

    def transform_color(self, color: pygame.Color):
        return np.array([self[color[0]].r, self[color[1]].g, self[color[2]].b])

    def transform_surface(self, surface: pygame.Surface) -> pygame.Surface:
        return pygame.surfarray.make_surface(
            np.apply_along_axis(
                self.transform_color, 2, pygame.surfarray.pixels3d(surface)
            )
        )
