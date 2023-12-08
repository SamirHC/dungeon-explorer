from enum import Enum

import pygame
from app.common import constants
from app.guicomponents.font import Font
import app.db.database as db


# Text Colors
RED = pygame.Color(248, 0, 0)
CYAN = pygame.Color(0, 248, 248)
BLUE = pygame.Color(0, 152, 248)
YELLOW = pygame.Color(248, 248, 0)
PALE_YELLOW = pygame.Color(248, 248, 160)
WHITE = pygame.Color(248, 248, 248)
LIME = pygame.Color(0, 248, 0)
BLACK = pygame.Color(0, 0, 0)
BROWN = pygame.Color(248, 192, 96)


class Align(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class Text:
    def __init__(self, chars: list[pygame.Surface], canvas: pygame.Surface, positions: list[tuple[int, int]]):
        self.canvas = canvas
        self.chars = chars
        self.positions = positions

    def render(self):
        surface = self.canvas.copy()
        for char, position in zip(self.chars, self.positions):
            surface.blit(char, position)
        return surface

    def get_rect(self, **kwargs) -> pygame.Rect:
        return self.canvas.get_rect(**kwargs)


class TextBuilder:
    def __init__(self):
        self.lines: list[list[pygame.Surface]] = [[]]
        self.font = db.font_db.normal_font
        self.color = WHITE
        self.align = Align.LEFT
        self.shadow = False
        self.line_spacing = 1

    def set_font(self, font: Font):
        self.font = font
        return self

    def set_color(self, color: pygame.Color):
        self.color = color
        self.font.color = color
        return self

    def set_alignment(self, align: Align):
        self.align = align
        return self

    def set_shadow(self, val: bool):
        self.shadow = val
        return self
    
    def write(self, text: str):
        for char in text:
            if char == "\n":
                self.lines.append([])
            else:
                self.write_char(char)
        return self
    
    def write_char(self, char: str):
        char_surface = self.font[char]
        final_surface = pygame.Surface(char_surface.get_size(), pygame.SRCALPHA)
        if self.shadow:
            char_surface.set_palette_at(self.font.editable_palette, BLACK)
            final_surface.blit(char_surface, (1, 0))
            final_surface.blit(char_surface, (0, 1))
            char_surface.set_palette_at(self.font.editable_palette, self.color)
        final_surface.blit(char_surface, (0, 0))
        self.lines[-1].append(final_surface)

    def get_canvas(self):
        width = max(map(self.get_line_width, self.lines))
        height = len(self.lines) * (self.font.size + self.line_spacing)
        return pygame.Surface((width, height), pygame.SRCALPHA)

    def get_line_width(self, line: list[pygame.Surface]) -> int:
        return sum(char.get_width() for char in line)

    def get_positions(self) -> list[tuple[int, int]]:
        positions = []
        y = 0
        for line in self.lines:
            x = self.get_line_start_position(line)
            for char in line:
                positions.append((x, y))
                x += char.get_width()
            y += self.font.size + self.line_spacing
        return positions
            
    def get_line_start_position(self, line) -> int:
        if self.align is Align.LEFT:
            return 0
        canvas_width = self.get_canvas().get_width()
        line_width = self.get_line_width(line)
        if self.align is Align.CENTER:
            return (canvas_width - line_width) / 2
        if self.align is Align.RIGHT:
            return canvas_width - line_width

    def build(self) -> Text:
        chars = []
        for line in self.lines:
            chars += line
        canvas = self.get_canvas()
        positions = self.get_positions()
        return Text(chars, canvas, positions)


def divider(length: int, color: pygame.Color=WHITE) -> pygame.Surface:
    surface = pygame.Surface((length, 2))
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, length, 1))
    pygame.draw.rect(surface, BLACK, pygame.Rect(0, 1, length, 1))
    return surface


class ScrollText:
    def __init__(self, text: Text):
        self.text = text
        self.t = 0

    def update(self):
        if not self.is_done:
            self.t += 1

    def render(self) -> pygame.Surface:
        surface = self.text.canvas.copy()
        for i in range(min(self.t, len(self.text.chars))):
            surface.blit(self.text.chars[i], self.text.positions[i])
        return surface

    def get_rect(self, **kwargs) -> pygame.Rect:
        return self.text.get_rect(**kwargs)

    @property
    def is_done(self) -> bool:
        return self.t >= len(self.text.chars)
