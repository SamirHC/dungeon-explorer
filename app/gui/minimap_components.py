from enum import Enum
import os

import pygame

from app.common.constants import IMAGES_DIRECTORY


class Visibility(Enum):
    FULL = 0
    PART = 1
    NONE = 2


class MinimapComponents:
    SIZE = 4

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        return self.components.subsurface(
            (x * self.SIZE, y * self.SIZE), (self.SIZE, self.SIZE)
        )

    def __init__(self, variation: int, color: pygame.Color):
        self.color = color

        file = os.path.join(IMAGES_DIRECTORY, "minimap", f"minimap{variation}.png")
        self.components = pygame.image.load(file)
        self.components.set_colorkey(self.components.get_at((0, 0)))

        self.enemy = self[2, 0]
        self.item = self[3, 0]
        self.trap = self[4, 0]
        self.warp_zone = self[5, 0]
        self.stairs = self[6, 0]
        self.wonder_tile = self[7, 0]
        self.user = self[0, 1]
        self.ally = self[2, 1]
        self.hidden_stairs = self[5, 1]

        self.ground_tiles = {v: self._get_ground(v.value) for v in Visibility}

    def _get_ground(self, offset: int) -> dict[int, pygame.Surface]:
        res = {}
        mask_cardinal_values = [
            15,
            14,
            13,
            12,
            7,
            6,
            5,
            4,
            11,
            10,
            9,
            8,
            3,
            2,
            1,
            0,
        ]
        masks_to_position = {
            m: (i % 8, i // 8) for i, m in enumerate(mask_cardinal_values)
        }
        for k, (x, y) in masks_to_position.items():
            surface = self[x, y + 2 * (1 + offset)]
            surface.set_palette_at(7, self.color)
            res[k] = surface
        return res

    def get_ground(self, cardinal_mask: int, visibility: Visibility) -> pygame.Surface:
        return self.ground_tiles[visibility][cardinal_mask]
