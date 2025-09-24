from __future__ import annotations
from enum import Enum

import pygame

from app.common import constants
from app.gui.font import Font
import app.db.database as db
import app.db.font as font_db


class Align(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class Text:
    def __init__(
        self,
        chars: list[pygame.Surface],
        canvas: pygame.Surface,
        positions: list[tuple[int, int]],
    ):
        self.canvas = canvas
        self.chars = chars
        self.positions = positions

    def render(self) -> pygame.Surface:
        surface = self.canvas.copy()
        for char, position in zip(self.chars, self.positions):
            surface.blit(char, position)
        return surface

    def get_rect(self, **kwargs) -> pygame.Rect:
        return self.canvas.get_rect(**kwargs)


class TextBuilder:
    def __init__(self):
        self.lines: list[list[pygame.Surface]] = [[]]
        self.font = font_db.normal_font
        self.color = constants.OFF_WHITE
        self.align = Align.LEFT
        self.shadow = False
        self.line_spacing = 1

    @staticmethod
    def build_white(text: str) -> Text:
        return TextBuilder.build_color(constants.OFF_WHITE, text)

    @staticmethod
    def build_color(color: pygame.Color, text: str) -> Text:
        return TextBuilder().set_shadow(True).set_color(color).write(text).build()

    def set_font(self, font: Font) -> TextBuilder:
        self.font = font
        return self

    def set_color(self, color: pygame.Color) -> TextBuilder:
        self.color = color
        self.font.color = color
        return self

    def set_alignment(self, align: Align) -> TextBuilder:
        self.align = align
        return self

    def set_shadow(self, val: bool) -> TextBuilder:
        self.shadow = val
        return self

    def write(self, text: str) -> TextBuilder:
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
            char_surface.set_palette_at(self.font.editable_palette, constants.BLACK)
            final_surface.blit(char_surface, (1, 0))
            final_surface.blit(char_surface, (0, 1))
            char_surface.set_palette_at(self.font.editable_palette, self.color)
        final_surface.blit(char_surface, (0, 0))
        self.lines[-1].append(final_surface)

    def get_canvas(self) -> pygame.Surface:
        width = max(map(self.get_line_width, self.lines)) + db.get_pointer().get_width()
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


def divider(length: int, color: pygame.Color = constants.OFF_WHITE) -> pygame.Surface:
    surface = pygame.Surface((length, 2))
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, length, 1))
    pygame.draw.rect(surface, constants.BLACK, pygame.Rect(0, 1, length, 1))
    return surface
