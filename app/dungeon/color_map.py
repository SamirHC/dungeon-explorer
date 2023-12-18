import pygame
import numpy as np


class ColorMap:
    def __init__(self, colors: list[pygame.Color]):
        self.colors = colors
        self.reds = [color.r for color in self.colors]
        self.greens = [color.g for color in self.colors]
        self.blues = [color.b for color in self.colors]

        self.t_r = np.vectorize(lambda r: self.reds[r])
        self.t_g = np.vectorize(lambda g: self.greens[g])
        self.t_b = np.vectorize(lambda b: self.blues[b])

    def transform_color(self, color: pygame.Color) -> pygame.Color:
        return pygame.Color(
            self.reds[color.r], self.greens[color.g], self.blues[color.b]
        )

    def transform_surface(self, surface: pygame.Surface):
        pixels_array = pygame.surfarray.pixels3d(surface)
        pixels_array[:, :, 0] = self.t_r(pixels_array[:, :, 0])
        pixels_array[:, :, 1] = self.t_g(pixels_array[:, :, 1])
        pixels_array[:, :, 2] = self.t_b(pixels_array[:, :, 2])
