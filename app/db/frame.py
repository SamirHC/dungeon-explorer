import os
import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.guicomponents.framecomponents import FrameComponents


class FrameDatabase:
    def __init__(self):
        self.base_dir = os.path.join(IMAGES_DIRECTORY, "frame")
        self.loaded: dict[int, FrameComponents] = {}

    def __getitem__(self, variation: int) -> FrameComponents:
        if variation not in self.loaded:
            self.load(variation)
        return self.loaded[variation]

    def load(self, variation: int) -> pygame.Surface:
        file = os.path.join(self.base_dir, f"{variation}.png")
        surface = pygame.image.load(file)
        surface.set_colorkey(surface.get_at((0, 0)))
        self.loaded[variation] = FrameComponents(surface)
