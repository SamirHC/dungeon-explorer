from functools import lru_cache
import os
import sqlite3

import pygame

from app.common import constants
from app.model.animation import Animation

# Databases
main_db = sqlite3.connect(os.path.join(constants.GAMEDATA_DIRECTORY, "gamedata.db"))


def get_icon() -> pygame.Surface:
    icon_path = os.path.join(constants.IMAGES_DIRECTORY, "icon", "icon.png")
    return pygame.image.load(icon_path)


@lru_cache(maxsize=1)
def get_pointer() -> pygame.Surface:
    pointer_surface_path = os.path.join(
        constants.IMAGES_DIRECTORY, "misc", "pointer.png"
    )
    pointer_surface = pygame.image.load(pointer_surface_path)
    pointer_surface.set_colorkey(pointer_surface.get_at((0, 0)))
    return pointer_surface


@lru_cache(maxsize=1)
def get_pointer_animation() -> Animation:
    return Animation([get_pointer(), constants.EMPTY_SURFACE], [30, 30])


@lru_cache(maxsize=1)
def get_darkness() -> pygame.Surface:
    path = os.path.join(constants.IMAGES_DIRECTORY, "misc", "darkness_level_gfx.png")
    surface = pygame.image.load(path)
    surface.set_colorkey(surface.get_at(surface.get_rect().center))
    surface.set_alpha(128)
    surface = surface.convert_alpha()
    return surface

def get_darkness_quarter(n: int) -> pygame.Surface:
    SIZE = 48
    x, y = (n % 2) * SIZE, (n // 2) * SIZE
    return get_darkness().subsurface((x, y, SIZE, SIZE))