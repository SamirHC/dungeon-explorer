import os

import pygame
import pygame.image

from app.common import constants
from app.common.constants import IMAGES_DIRECTORY
from app.pokemon.shadow_size import ShadowSize


class ShadowDatabase:
    def __init__(self):
        self.base_dir = os.path.join(IMAGES_DIRECTORY, "spriteshadow")
        self._black_shadows = self._get_shadows("black_shadows.png")
        self._gold_shadows = self._get_shadows("gold_shadows.png")

        self.black_dict = {
            ShadowSize.SMALL: self._get_small_black_shadow(),
            ShadowSize.MEDIUM: self._get_medium_black_shadow(),
            ShadowSize.LARGE: self._get_large_black_shadow(),
        }

        self.gold_dict = {
            ShadowSize.SMALL: self._gold_shadows.subsurface((0, 0), (24, 10)),
            ShadowSize.MEDIUM: self._gold_shadows.subsurface((0, 10), (24, 10)),
            ShadowSize.LARGE: self._gold_shadows.subsurface((0, 20), (24, 10)),
        }

    def get_black_shadow(self, size: ShadowSize):
        return self.black_dict[size]

    def get_gold_shadow(self, size: ShadowSize):
        return self.gold_dict[size]

    def get_dungeon_shadow(self, size: ShadowSize, is_enemy: bool):
        return (self.get_black_shadow if is_enemy else self.get_gold_shadow)(size)

    def _get_shadows(self, name: str) -> pygame.Surface:
        return pygame.image.load(os.path.join(self.base_dir, name))

    def _get_small_black_shadow(self) -> pygame.Surface:
        colors = pygame.PixelArray(self._black_shadows.copy())
        colors.replace((255, 0, 0), constants.TRANSPARENT)
        colors.replace((0, 255, 0), constants.BLACK)
        colors.replace((0, 0, 255), constants.TRANSPARENT)
        return colors.make_surface()

    def _get_medium_black_shadow(self) -> pygame.Surface:
        colors = pygame.PixelArray(self._black_shadows.copy())
        colors.replace((255, 0, 0), constants.BLACK)
        colors.replace((0, 255, 0), constants.BLACK)
        colors.replace((0, 0, 255), constants.TRANSPARENT)
        return colors.make_surface()

    def _get_large_black_shadow(self) -> pygame.Surface:
        colors = pygame.PixelArray(self._black_shadows.copy())
        colors.replace((255, 0, 0), constants.BLACK)
        colors.replace((0, 255, 0), constants.BLACK)
        colors.replace((0, 0, 255), constants.BLACK)
        return colors.make_surface()
