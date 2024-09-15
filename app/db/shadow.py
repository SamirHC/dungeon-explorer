import os

import pygame
import pygame.image

from app.common import constants
from app.common.constants import IMAGES_DIRECTORY
from app.pokemon.shadow_size import ShadowSize


base_dir = os.path.join(IMAGES_DIRECTORY, "spriteshadow")


def get_black_shadow(size: ShadowSize):
    return black_dict[size]


def get_gold_shadow(size: ShadowSize):
    return gold_dict[size]


def get_dungeon_shadow(size: ShadowSize, is_enemy: bool):
    return (get_black_shadow if is_enemy else get_gold_shadow)(size)


def _get_shadows(name: str) -> pygame.Surface:
    return pygame.image.load(os.path.join(base_dir, name))


def _get_small_black_shadow() -> pygame.Surface:
    colors = pygame.PixelArray(_black_shadows.copy())
    colors.replace((255, 0, 0), constants.TRANSPARENT)
    colors.replace((0, 255, 0), constants.BLACK)
    colors.replace((0, 0, 255), constants.TRANSPARENT)
    return colors.make_surface()


def _get_medium_black_shadow() -> pygame.Surface:
    colors = pygame.PixelArray(_black_shadows.copy())
    colors.replace((255, 0, 0), constants.BLACK)
    colors.replace((0, 255, 0), constants.BLACK)
    colors.replace((0, 0, 255), constants.TRANSPARENT)
    return colors.make_surface()


def _get_large_black_shadow() -> pygame.Surface:
    colors = pygame.PixelArray(_black_shadows.copy())
    colors.replace((255, 0, 0), constants.BLACK)
    colors.replace((0, 255, 0), constants.BLACK)
    colors.replace((0, 0, 255), constants.BLACK)
    return colors.make_surface()


_black_shadows = _get_shadows("black_shadows.png")
_gold_shadows = _get_shadows("gold_shadows.png")

black_dict = {
    ShadowSize.SMALL: _get_small_black_shadow(),
    ShadowSize.MEDIUM: _get_medium_black_shadow(),
    ShadowSize.LARGE: _get_large_black_shadow(),
}

gold_dict = {
    ShadowSize.SMALL: _gold_shadows.subsurface((0, 0), (24, 10)),
    ShadowSize.MEDIUM: _gold_shadows.subsurface((0, 10), (24, 10)),
    ShadowSize.LARGE: _gold_shadows.subsurface((0, 20), (24, 10)),
}
