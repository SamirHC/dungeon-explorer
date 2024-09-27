from functools import lru_cache
import os

import pygame

from app.common.constants import IMAGES_DIRECTORY


HUD_COMPONENTS_FILE = os.path.join(IMAGES_DIRECTORY, "misc", "hud_components.png")
SIZE = 8


@lru_cache(maxsize=1)
def _hud_components():
    surface = pygame.image.load(HUD_COMPONENTS_FILE)
    surface.set_colorkey(surface.get_at((0, 0)))
    return surface


@lru_cache
def _get(x: int, y: int):
    return _hud_components().subsurface(x * SIZE, y * SIZE, SIZE, SIZE)


def get_f() -> pygame.Surface:
    return _get(10, 0)


def get_l() -> pygame.Surface:
    return _get(11, 0)


def get_v() -> pygame.Surface:
    return _get(12, 0)


def get_b() -> pygame.Surface:
    return _get(13, 1)


def get_h() -> pygame.Surface:
    return _get(10, 1)


def get_p() -> pygame.Surface:
    return _get(11, 1)


def get_slash() -> pygame.Surface:
    return _get(12, 1)


def get_white_number(n: int) -> pygame.Surface:
    return _get(n, 0)


def get_green_number(n: int) -> pygame.Surface:
    return _get(n, 1)


# Sets the labelling text (e.g. B, F, Lv, HP)
def set_palette_12(color: pygame.Color):
    _hud_components().set_palette_at(12, color)
