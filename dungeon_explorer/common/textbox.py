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

class Frame(pygame.Surface):
    def __init__(self, size: tuple[int, int], alpha=255):
        w, h = size
        super().__init__((w*8, h*8), pygame.SRCALPHA)
        variation = settings.get_frame()
        components = FrameComponents(variation)

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
        divider = text.text_divider(self.container_rect.width - 3)
        self.blit(divider, pygame.Vector2(self.container_rect.topleft) + (2, 13))
        return self
    
    def with_footer_divider(self):
        divider = text.text_divider(self.container_rect.width - 3)
        self.blit(divider, pygame.Vector2(self.container_rect.bottomleft) + (2, -16))
        return self
        

class TextBox:
    def __init__(self, size: tuple[int, int], max_lines: int):
        self.size = size
        self.max_lines = max_lines
        self.frame = Frame(self.size)
        self.contents: list[pygame.Surface] = []
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        self.surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.surface.blit(self.frame, (0, 0))
        self.draw_contents()
        return self.surface

    def draw_contents(self):
        x, y = 12, 10
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
        self.frame = Frame(size)
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
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .write(word + " ", color)
                .build()
            )
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