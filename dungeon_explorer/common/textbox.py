import os

import pygame
import pygame.draw
import pygame.image
from dungeon_explorer.common import constants, settings, text


class FrameComponents:
    SIZE = 8
    def __init__(self, variation: int):
        self.variation = variation
        self.components = self.load_components()
        self.get_components()

    def load_components(self) -> pygame.Surface:
        file = os.path.join("assets", "images", "textboxframe", f"{self.variation}.png")
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

class TextBoxFrame(pygame.Surface):
    # Size: given in terms of number of blocks instead of pixels (where each block is 8x8 pixels)
    # Variation: Different styles to choose from [0,4]
    def __init__(self, size: tuple[int, int]):
        w, h = size
        super().__init__((w*8, h*8), pygame.SRCALPHA)
        variation = settings.get_frame()

        file = os.path.join("assets", "images", "textboxframe", f"{variation}.png")
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
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.frame = TextBoxFrame(size)
        self.cursor = 0, 0
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height), pygame.SRCALPHA)

    @property
    def canvas_topleft(self) -> tuple[int, int]:
        return 12, 10
    
    @property
    def canvas_topright(self) -> tuple[int, int]:
        x, y = self.size
        x *= 8
        y *= 8
        dx, dy = self.canvas_topleft
        return x - dx, y - dy

    @property
    def canvas_width(self):
        return self.canvas_topright[0] - self.canvas_topleft[0]

    @property
    def canvas_height(self):
        return self.size[1] * 8 - 20

    def write(self, message: str, color: pygame.Color):
        words = message.split(" ")
        for word in words:
            text_surface = text.build(word + " ", color)
            if self.canvas.get_width() < self.cursor[0] + text_surface.get_width():
                self.cursor = 0, self.cursor[1] + 14
            self.canvas.blit(text_surface, self.cursor)
            self.cursor = self.cursor[0] + text_surface.get_width(), self.cursor[1]
    
    def write_multicolor(self, items: tuple[str, pygame.Color]):
        for item in items:
            self.write(item[0], item[1])

    def write_line(self, items: tuple[str, pygame.Color]):
        self.write_multicolor(items)
        self.cursor = 0, self.cursor[1] + 14
        self.canvas.blit(text.text_divider(self.canvas_width), self.cursor)
        self.cursor = 0, self.cursor[1] + 2

    def render(self):
        surface = self.frame
        surface.blit(self.canvas, self.canvas_topleft)
        return surface