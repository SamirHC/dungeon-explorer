import os

import pygame
import pygame.image

from app.common import constants, settings, text

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


class Frame(pygame.Surface):
    def __init__(self, size: tuple[int, int], alpha=255):
        w, h = size
        super().__init__((w*8, h*8), pygame.SRCALPHA)
        variation = settings.get_frame()
        components = get_variant(variation)

        bg = pygame.Surface(((w-2)*components.SIZE+2, (h-2)*components.SIZE+2), pygame.SRCALPHA)
        bg.set_alpha(alpha)
        bg.fill(constants.OFF_BLACK)
        self.blit(bg, (7, 7))

        self.blit(components.topleft, (0, 0))
        self.blit(components.topright, ((w-1)*components.SIZE, 0))
        self.blit(components.bottomleft, (0, (h-1)*components.SIZE))
        self.blit(components.bottomright, ((w-1)*components.SIZE, (h-1)*components.SIZE))

        for i in range(1, w-1):
            self.blit(components.top, (i*components.SIZE, 0))
            self.blit(components.bottom, (i*components.SIZE, (h-1)*components.SIZE))

        for j in range(1, h-1):
            self.blit(components.left, (0, j*components.SIZE))
            self.blit(components.right, ((w-1)*components.SIZE, j*components.SIZE))

        container_topleft = (components.SIZE, components.SIZE)
        container_size = (self.get_width()-components.SIZE*2, self.get_height()-components.SIZE*2)
        self.container_rect = pygame.Rect(container_topleft, container_size)

    def with_header_divider(self):
        divider = text.divider(self.container_rect.width - 3)
        self.blit(divider, pygame.Vector2(self.container_rect.topleft) + (2, 13))
        return self
    
    def with_footer_divider(self):
        divider = text.divider(self.container_rect.width - 3)
        self.blit(divider, pygame.Vector2(self.container_rect.bottomleft) + (2, -16))
        return self


class PortraitFrame(pygame.Surface):
    def __init__(self):
        super().__init__((56, 56), pygame.SRCALPHA)
        variation = settings.get_frame()
        components = get_variant(variation)
        self.blit(components.portrait_topleft, (0, 0))
        self.blit(components.portrait_topright, (48, 0))
        self.blit(components.portrait_bottomleft, (0, 48))
        self.blit(components.portrait_bottomright, (48, 48))

        for i in range(1, 6):
            self.blit(components.portrait_top, (components.SIZE*i, 0))
            self.blit(components.portrait_bottom, (components.SIZE*i, 48))
            self.blit(components.portrait_left, (0, components.SIZE*i))
            self.blit(components.portrait_right, (48, components.SIZE*i))

        self.container_rect = pygame.Rect(8, 8, 40, 40)