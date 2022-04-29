import os
import enum

import pygame
import pygame.draw
import pygame.font
import pygame.image
import xml.etree.ElementTree as ET
from dungeon_explorer.common import constants


class Align(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class Font:
    def __init__(self, font_path: str, metadata_path: str, editable_palette=None, colorkey=None):
        self.editable_palette = editable_palette
        self.colorkey = colorkey

        self.font_sheet = pygame.image.load(font_path)
        self.load_metadata(metadata_path)
        self.CHARS_PER_ROW = 16
        self.size = self.font_sheet.get_width() // self.CHARS_PER_ROW

    def load_metadata(self, path: str):
        metadata = ET.parse(path).getroot()
        self.widths = {}
        elements = metadata.find("Table").findall("Char")
        for el in elements:
            char_id = int(el.get("id"))
            width = int(el.get("width"))
            self.widths[char_id] = width

    def __getitem__(self, char: str) -> pygame.Surface:
        char_id = ord(char)
        x = (char_id % self.CHARS_PER_ROW) * self.size
        y = (char_id // self.CHARS_PER_ROW) * self.size
        w, h = self.get_width(char), self.size
        return self.font_sheet.subsurface((x, y, w, h))

    def get_width(self, char: str) -> int:
        char_id = ord(char)
        return self.widths.get(char_id, 0)

    def is_colorable(self):
        return self.editable_palette is not None

    @property
    def color(self) -> pygame.Color:
        return self.font_sheet.get_palette_at(self.editable_palette)

    @color.setter
    def color(self, new_color: pygame.Color):
        if not self.is_colorable:
            return
        if new_color == self.colorkey:
            return
        self.font_sheet.set_palette_at(self.editable_palette, new_color)



banner_font = Font(
    os.path.join("assets", "font", "banner", "banner.png"),
    os.path.join("assets", "font", "banner", "banner.xml")
)
normal_font = Font(
    os.path.join("assets", "font", "normal", "normal_font.png"),
    os.path.join("assets", "font", "normal", "normal_font.xml"),
    15,
    constants.WHITE
)


class TextBuilder:
    def __init__(self):
        self.lines: list[list[pygame.Surface]] = [[]]
        self.font = normal_font
        self.align = Align.LEFT
        self.shadow = False
        self.line_spacing = 2

    def set_font(self, font: Font):
        self.font = font
        return self

    def set_color(self, color: pygame.Color):
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
                char_surface = self.font[char]
                self.lines[-1].append(char_surface)
        return self

    def build_canvas(self):
        width = max([self.get_line_width(line) for line in self.lines])
        height = len(self.lines) * (self.font.size + self.line_spacing)
        return pygame.Surface((width, height), pygame.SRCALPHA)

    def get_line_width(self, line: list[pygame.Surface]) -> int:
        return sum([char.get_width() for char in line])

    def get_positions(self) -> list[list[tuple[int, int]]]:
        positions = []
        y = 0
        for line in self.lines:
            line_positions = []
            x = self.get_line_start_position(line)
            for char in line:
                line_positions.append((x, y))
                x += char.get_width()
            positions.append(line_positions)
            y += self.font.size + self.line_spacing
        return positions
            
    def get_line_start_position(self, line) -> int:
        if self.align is Align.LEFT:
            return 0
        canvas_width = self.build_canvas().get_width()
        line_width = self.get_line_width(line)
        if self.align is Align.CENTER:
            return (canvas_width - line_width) / 2
        if self.align is Align.RIGHT:
            return canvas_width - line_width

    def build(self):
        self.canvas = self.build_canvas()
        self.positions = self.get_positions()
        return self
        
    def render(self):
        surface = self.canvas.copy()
        text_surface = self.canvas.copy()
        text_surface.set_colorkey(self.font.colorkey)
        if self.shadow:
            shadow_surface = self.canvas.copy()
            shadow_surface.set_colorkey(self.font.colorkey)
        for line, line_positions in zip(self.lines, self.positions):
            for char, char_position in zip(line, line_positions):
                text_surface.blit(char, char_position)
                if self.shadow:
                    shadow_char = char.copy()
                    shadow_char.set_palette_at(self.font.editable_palette, constants.BLACK)
                    shadow_surface.blit(shadow_char, char_position)
        if self.shadow:
            surface.blit(shadow_surface, (1, 0))
            surface.blit(shadow_surface, (0, 1))
        surface.blit(text_surface, (0, 0))
        return surface


def divider(length: int, color: pygame.Color=constants.OFF_WHITE) -> pygame.Surface:
    surface = pygame.Surface((length, 2))
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, length, 1))
    pygame.draw.rect(surface, constants.BLACK, pygame.Rect(0, 1, length, 1))
    return surface


class ScrollText:
    def __init__(self, msg: str, align: Align=Align.LEFT):
        self.msg = msg
        self.align = align
        self.t = 0
        self.empty_surface = self.render()

    def update(self):
        self.t += 1

    def render(self) -> pygame.Surface:
        visible_text = self.msg[:self.t]
        invisible_text = self.msg[self.t:]
        return (
            TextBuilder()
            .set_alignment(self.align)
            .set_shadow(True)
            .set_color(constants.OFF_WHITE)
            .write(visible_text)
            .set_color(constants.TRANSPARENT)
            .write(invisible_text)
            .build()
            .render()
        )
