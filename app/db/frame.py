import os

import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.gui.framecomponents import FrameComponents


base_dir = os.path.join(IMAGES_DIRECTORY, "frame")


def load(variation: int) -> FrameComponents:
    file = os.path.join(base_dir, f"{variation}.png")
    surface = pygame.image.load(file)
    surface.set_colorkey(surface.get_at((0, 0)))
    return FrameComponents(surface)
