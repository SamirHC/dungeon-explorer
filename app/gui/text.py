from __future__ import annotations
from enum import Enum

import pygame

from app.common import mixer
from app.gui.font import Font
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
        self.font = db.font_db.normal_font
        self.color = WHITE
        self.align = Align.LEFT
        self.shadow = False
        self.line_spacing = 1

    @staticmethod
    def build_white(text: str) -> Text:
        return TextBuilder.build_color(WHITE, text)

    @staticmethod
    def build_color(color: pygame.Color, text: str) -> Text:
        return (
            TextBuilder().set_shadow(True).set_color(color).write(text).build()
        )

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
            char_surface.set_palette_at(self.font.editable_palette, BLACK)
            final_surface.blit(char_surface, (1, 0))
            final_surface.blit(char_surface, (0, 1))
            char_surface.set_palette_at(self.font.editable_palette, self.color)
        final_surface.blit(char_surface, (0, 0))
        self.lines[-1].append(final_surface)

    def get_canvas(self) -> pygame.Surface:
        width = max(map(self.get_line_width, self.lines)) + db.pointer_surface.get_width()
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


def divider(length: int, color: pygame.Color = WHITE) -> pygame.Surface:
    surface = pygame.Surface((length, 2))
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, length, 1))
    pygame.draw.rect(surface, BLACK, pygame.Rect(0, 1, length, 1))
    return surface


class ScrollText:
    def __init__(self, tokens: str, with_sound=False, start_t=0):
        self.with_sound = with_sound
        self.is_paused = False
        self.t = 0
        self.pointer_animations: list[int] = []
        command_map = {
            "A": lambda x: tb.set_alignment(Align(int(x))),
            "C": lambda x: tb.set_color(globals()[x]),
            "G": lambda x: tb.set_font(db.font_db.graphic_font)
                .write([int(x)])
                .set_font(db.font_db.normal_font),
            "K": lambda x: self.pointer_animations.append(self.t)
        }
                
        tb = TextBuilder()
        i = 0
        n = len(tokens)
        while i < n:
            token = tokens[i]
            if token == '[':
                i += 1
                j = tokens.index("]", i)
                components = tokens[i:j].split(":", maxsplit=2)
                command = components[0]
                arg = components[1] if len(components) > 1 else None
                command_map[command](arg)
                i = j
                if command == "G":
                    self.t += 1
            else:
                tb.write(token)
                if token != "\n":
                    self.t += 1
            i += 1
        
        self.t = start_t
        self.text = tb.build()

    def unpause(self):
        self.is_paused = False
        self.t += 1

    def update(self):
        if self.is_paused:
            db.pointer_animation.update()
        if self.is_done:
            return
        if self.t in self.pointer_animations:
            self.is_paused = True
            return
        self.t += 1
        if self.with_sound and not mixer.misc_sfx_channel.get_busy():
            text_tick_sfx = db.sfx_db["SystemSE", 5]
            mixer.misc_sfx_channel.play(text_tick_sfx)
            print(text_tick_sfx.get_length())

    def render(self) -> pygame.Surface:
        surface = self.text.canvas.copy()
        for i in range(min(self.t, len(self.text.chars))):
            item = self.text.chars[i]
            pos = self.text.positions[i]
            surface.blit(item, pos)
        if self.t in self.pointer_animations:
            pos = pos[0] + item.get_width(), pos[1]
            item = db.pointer_animation.render()
            surface.blit(item, pos)
        return surface

    def get_rect(self, **kwargs) -> pygame.Rect:
        return self.text.get_rect(**kwargs)

    @property
    def is_done(self) -> bool:
        return self.t >= len(self.text.chars)
