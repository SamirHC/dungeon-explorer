import os

import pygame
import pygame.image

class FrameComponents:
    SIZE = 8
    def __init__(self, variation: int):
        self.variation = variation
        self.components = self.load_components()
        self.get_components()

    def load_components(self) -> pygame.Surface:
        file = os.path.join("assets", "images", "frame", f"{self.variation}.png")
        surface = pygame.image.load(file)
        surface.set_colorkey(surface.get_at((0, 0)))
        return surface

    def __getitem__(self, position: tuple[int, int]):
        x, y = position
        return self.components.subsurface((x*self.SIZE, y*self.SIZE), (self.SIZE, self.SIZE))

    def get_components(self):
        self.topleft = self[0, 0]
        self.top = self[1, 0]
        self.topright = self[2, 0]
        self.left = self[0, 1]
        self.right = self[2, 1]
        self.bottomleft = self[0, 2]
        self.bottom = self[1, 2]
        self.bottomright = self[2, 2]

        self.portrait_topleft = self[3, 0]
        self.portrait_top = self[4, 0]
        self.portrait_topright = self[5, 0]
        self.portrait_left = self[3, 1]
        self.portrait_right = self[5, 1]
        self.portrait_bottomleft = self[3, 2]
        self.portrait_bottom = self[4, 2]
        self.portrait_bottomright = self[5, 2]

FRAME_COMPONENTS = tuple(FrameComponents(i) for i in range(5))

def get_variant(variant: int) -> FrameComponents:
    return FRAME_COMPONENTS[variant]