import os
import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.dungeon.color_map import ColorMap
from app.dungeon.floor_status import Weather


class ColorMapDatabase:
    def __init__(self):
        self.base_dir = os.path.join(IMAGES_DIRECTORY, "colormap")
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
