# Deprecated, but may return later.
"""
import os

from app.common.constants import IMAGES_DIRECTORY
from app.dungeon.color_map import ColorMap

base_dir = os.path.join(IMAGES_DIRECTORY, "colormap")


def load(weather: Weather) -> ColorMap:
    surface_path = os.path.join(base_dir, f"{weather.value}.png")
    surface = pygame.image.load(surface_path)
    colors = [surface.get_at((i % 16, i // 16)) for i in range(256)]
    return ColorMap(colors)
"""
import pygame

from app.dungeon.weather import Weather


def get_filter_color(weather: Weather) -> pygame.Color:
    match weather:
        case Weather.CLEAR:
            return (255, 255, 255, 5)
        case Weather.CLOUDY:
            return (151, 151, 255, 63)
        case Weather.FOG:
            return (220, 220, 220, 102)
        case Weather.HAIL:
            return (0, 101, 178, 53)
        case Weather.RAINY:
            return (0, 0, 233, 33)
        case Weather.SANDSTORM:
            return (255, 255, 83, 80)
        case Weather.SNOW:
            return (41, 148, 255, 34)
        case Weather.SUNNY:
            return (255, 255, 255, 29)
        case _:
            return (255, 255, 255, 255)
