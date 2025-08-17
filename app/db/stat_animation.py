from enum import Enum
import os
from typing import Literal

import pygame
import pygame.image

from app.common.constants import IMAGES_DIRECTORY
from app.model.animation import Animation
from app.pokemon.stat import Stat


BASE_DIR = os.path.join(IMAGES_DIRECTORY, "moves", "stat")


class StatAnimationType(Enum):
    FALL = (0, (32, 48))
    RISE = (1, (40, 48))
    RESET = (2, (16, 16))

    def __init__(self, stat_anim_type_id: int, size: tuple[int, int]):
        path = os.path.join(BASE_DIR, f"{stat_anim_type_id}.png")
        self.sheet = pygame.image.load(path)
        self.size = size


STAT_PALETTES = {
    Stat.ACCURACY: (
        (0, 0, 0, 255),
        (241, 152, 249, 255),
        (243, 196, 237, 255),
        (255, 255, 255, 255),
    ), 
    Stat.ATTACK: (
        (0, 0, 0, 255),
        (236, 32, 32, 255),
        (250, 100, 100, 255),
        (255, 255, 255, 255),
    ),
    Stat.DEFENSE: (
        (0, 0, 0, 255),
        (42, 204, 42, 255),
        (121, 237, 56, 255),
        (255, 255, 255, 255),
    ),
    Stat.SP_ATTACK: (
        (0, 0, 0, 255),
        (222, 127, 231, 255),
        (239, 164, 230, 255),
        (255, 255, 255, 255),
    ),
    Stat.SP_DEFENSE: (
        (0, 0, 0, 255),
        (153, 176, 183, 255),
        (182, 213, 226, 255),
        (255, 255, 255, 255),
    ),
    Stat.EVASION: (
        (0, 0, 0, 255),
        (255, 210, 29, 255),
        (255, 241, 174, 255),
        (255, 255, 255, 255),
    ),
    "speed": (
        (0, 0, 0, 255),
        (24, 156, 231, 255),
        (140, 222, 255, 255),
        (255, 255, 255, 255),
    ),
}


def get_animation(
    sheet: pygame.Surface,
    palette: list[pygame.Color],
    size: tuple[int, int]
) -> Animation:
    W, H = size
    NUM_FRAMES = sheet.get_width() // W

    new_sheet = sheet.copy()
    new_sheet.set_palette(palette)

    frames = [new_sheet.subsurface((x*W, 0, W, H)) for x in range(NUM_FRAMES)]
    durations = [2] * NUM_FRAMES
    return Animation(frames, durations)


_anims = {
    (stat_name, anim_type): get_animation(
        anim_type.sheet,
        STAT_PALETTES[stat_name],
        anim_type.size
    )
    for stat_name in STAT_PALETTES
    for anim_type in StatAnimationType
}


def load(stat: Stat | Literal["speed"], anim_id: int) -> Animation:
    return _anims[stat, anim_id]
