import enum
import os

import pygame
import pygame.image
from app.common import constants


class ShadowSize(enum.Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


_base_dir = os.path.join("assets", "images", "spriteshadow")


def _get_shadows(name: str) -> pygame.Surface:
    return pygame.image.load(os.path.join(_base_dir, name))


_black_shadows = _get_shadows("black_shadows.png")
_gold_shadows = _get_shadows("gold_shadows.png")


def _get_small_black_shadow() -> pygame.Surface:
    colors = pygame.PixelArray(_black_shadows)
    colors.replace((255, 0, 0), constants.TRANSPARENT)
    colors.replace((0, 255, 0), constants.BLACK)
    colors.replace((0, 0, 255), constants.TRANSPARENT)
    return colors.make_surface()


def _get_medium_black_shadow() -> pygame.Surface:
    colors = pygame.PixelArray(_black_shadows)
    colors.replace((255, 0, 0), constants.BLACK)
    colors.replace((0, 255, 0), constants.BLACK)
    colors.replace((0, 0, 255), constants.TRANSPARENT)
    return colors.make_surface()


def _get_large_black_shadow() -> pygame.Surface:
    colors = pygame.PixelArray(_black_shadows)
    colors.replace((255, 0, 0), constants.BLACK)
    colors.replace((0, 255, 0), constants.BLACK)
    colors.replace((0, 0, 255), constants.BLACK)
    return colors.make_surface()


SMALL_BLACK = _get_small_black_shadow()
MEDIUM_BLACK = _get_medium_black_shadow()
LARGE_BLACK = _get_large_black_shadow()

SMALL_GOLD = _gold_shadows.subsurface((0, 0), (24, 10))
MEDIUM_GOLD = _gold_shadows.subsurface((0, 10), (24, 10))
LARGE_GOLD = _gold_shadows.subsurface((0, 20), (24, 10))
