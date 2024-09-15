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


def get_pointer() -> pygame.Surface:
    pointer_surface_path = os.path.join(
        constants.IMAGES_DIRECTORY, "misc", "pointer.png"
    )
    pointer_surface = pygame.image.load(pointer_surface_path)
    pointer_surface.set_colorkey(pointer_surface.get_at((0, 0)))
    return pointer_surface


def get_pointer_animation() -> Animation:
    return Animation([get_pointer(), constants.EMPTY_SURFACE], [30, 30])
