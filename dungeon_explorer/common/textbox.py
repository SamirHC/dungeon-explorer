import os

import pygame
import pygame.image
from dungeon_explorer.common import constants, settings


class TextBoxFrame(pygame.Surface):
    # Size: given in terms of number of blocks instead of pixels (where each block is 8x8 pixels)
    # Variation: Different styles to choose from [0,4]
    def __init__(self, size: tuple[int, int]):
        w, h = size
        super().__init__((w*8, h*8), pygame.SRCALPHA)
        variation = settings.get_frame()

        file = os.path.join("assets", "images", "misc",
                            f"FONT_frame{variation}.png")
        self.frame_components = pygame.image.load(file)
        self.frame_components.set_colorkey(self.frame_components.get_at((0, 0)))

        topleft = self.get_component((0, 0))
        top = self.get_component((1, 0))
        topright = self.get_component((2, 0))
        left = self.get_component((0, 1))
        right = self.get_component((2, 1))
        bottomleft = self.get_component((0, 2))
        bottom = self.get_component((1, 2))
        bottomright = self.get_component((2, 2))

        self.blit(topleft, (0, 0))
        self.blit(topright, ((w-1)*8, 0))
        self.blit(bottomleft, (0, (h-1)*8))
        self.blit(bottomright, ((w-1)*8, (h-1)*8))

        for i in range(1, w-1):
            self.blit(top, (i*8, 0))
            self.blit(bottom, (i*8, (h-1)*8))

        for j in range(1, h-1):
            self.blit(left, (0, j*8))
            self.blit(right, ((w-1)*8, j*8))

        bg = pygame.Surface(((w-2)*8+2, (h-2)*8+2), pygame.SRCALPHA)
        bg.set_alpha(128)
        bg.fill(constants.BLACK)
        self.blit(bg, (7, 7))

    def get_component(self, position: tuple[int, int]) -> pygame.Surface:
        return self.frame_components.subsurface(pygame.Vector2(position)*8, (8, 8))


class TextBox:
    def __init__(self, dimensions: tuple[int, int], max_lines: int):
        self.dimensions = dimensions
        self.max_lines = max_lines
        self.contents: list[pygame.Surface] = []
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        self.surface = TextBoxFrame(self.dimensions)
        self.draw_contents()
        return self.surface

    def draw_contents(self):
        x = 12
        y = 10
        spacing = 2
        while len(self.contents) > self.max_lines:
            self.contents.pop(0)
        for item in self.contents:
            self.surface.blit(item, (x, y))
            y += item.get_height() + spacing

    def append(self, item):
        self.contents.append(item)


class TextLog:
    T = 12
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.contents: list[pygame.Surface] = []
        self.frame = TextBoxFrame(size)
        self.index = 0
        self.is_active = False

    def append(self, text_surface: pygame.Surface):
        self.contents.append(text_surface)
        if len(self.contents) > 3:
            self.is_active = True

    def update(self):
        if not self.is_active:
            return
        if not self.timer:
            self.timer = self.T
        self.timer -= 1
        if not self.timer:
            self.is_active = False
            self.index = 0

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        surface.blit(self.frame, (0, 0))
        if not self.is_active:
            pass
        return surface

