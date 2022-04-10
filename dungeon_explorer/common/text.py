import os

import pygame
import pygame.draw
import pygame.font
import pygame.image
import xml.etree.ElementTree as ET
from dungeon_explorer.common import constants


class Font:
    LEFT_ALIGN = 0
    CENTER_ALIGN = 1
    RIGHT_ALIGN = 2

    def __init__(self, source: pygame.Surface, metadata: ET.ElementTree, editable_palette: int=-1):
        self.source = source
        self.metadata = metadata.getroot()
        self.size = source.get_width() // 16
        self.editable_palette = editable_palette

    def __getitem__(self, char: str) -> pygame.Surface:
        char_id = ord(char)
        x = (char_id % 16) * self.size
        y = (char_id // 16) * self.size
        w, h = self.get_width(char), self.size
        return self.source.subsurface((x, y, w, h))

    def get_width(self, char: str) -> int:
        char_id = ord(char)
        elements = self.metadata.find("Table").findall("Char")
        for el in elements:
            if int(el.get("id")) == char_id:
                return int(el.get("width"))
        return 0

    def is_colorable(self):
        return 0 <= self.editable_palette < 16

    def render(self, message: str, align=LEFT_ALIGN, color: pygame.Color=constants.OFF_WHITE) -> pygame.Surface:
        lines = message.splitlines()
        if not lines:
            return pygame.Surface((0, 0))
        if self.is_colorable():
            self.source.set_palette_at(self.editable_palette, color)
        line_surfaces = [self.build_line(line) for line in lines]
        w = max([line.get_width() for line in line_surfaces])
        h = self.size * len(line_surfaces)
        surface = pygame.Surface((w, h))
        for i, line_surface in enumerate(line_surfaces):
            if align == Font.LEFT_ALIGN:
                rect = line_surface.get_rect(left=surface.get_rect().left, y=i*self.size)
            elif align == Font.CENTER_ALIGN:
                rect = line_surface.get_rect(centerx=surface.get_rect().centerx, y=i*self.size)
            elif align == Font.RIGHT_ALIGN:
                rect = line_surface.get_rect(right=surface.get_rect().right, y=i*self.size)
            surface.blit(line_surface, rect.topleft)
        return surface

    def build_line(self, line: str) -> pygame.Surface:
        char_surfaces = [self[c] for c in line]
        surface = pygame.Surface((sum([c.get_width() for c in char_surfaces]), self.size))
        x = 0
        for c in char_surfaces:
            surface.blit(c, (x, 0))
            x += c.get_width()
        return surface


banner_font = Font(
    pygame.image.load(os.path.join("assets", "font", "banner", "banner.png")),
    ET.parse(os.path.join("assets", "font", "banner", "banner.xml"))
)
normal_font = Font(
    pygame.image.load(os.path.join("assets", "font", "normal", "normal_font.png")),
    ET.parse(os.path.join("assets", "font", "normal", "normal_font.xml")),
    15
)

def build(text: str, text_color: pygame.Color=constants.OFF_WHITE):
    if not text:
        return pygame.Surface((0, 0))
    text_surface = normal_font.render(text, Font.LEFT_ALIGN, text_color)
    shadow_surface = normal_font.render(text, Font.LEFT_ALIGN, constants.BLACK)
    text_surface.set_colorkey(text_surface.get_at((0, 0)))
    shadow_surface.set_colorkey(shadow_surface.get_at((0, 0)))
    w, h = text_surface.get_size()
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    surface.blit(shadow_surface, (0, 1))
    surface.blit(shadow_surface, (1, 0))
    surface.blit(text_surface, (0, 0))
    return surface

def build_multicolor(items: list[tuple[str, pygame.Color]]):
    surfaces: list[pygame.Surface] = []
    w, h = 0, 0
    for text, color in items:
        surfaces.append(build(text, color))
        w += surfaces[-1].get_width()
        h = max(h, surfaces[-1].get_height())
    
    result = pygame.Surface((w, h), pygame.SRCALPHA)
    w = 0
    for surface in surfaces:
        result.blit(surface, (w, 0))
        w += surface.get_width()
    return result

def text_divider(length: int) -> pygame.Surface:
    surface = pygame.Surface((length, 2))
    pygame.draw.rect(surface, constants.OFF_WHITE, pygame.Rect(0, 0, length, 1))
    pygame.draw.rect(surface, constants.BLACK, pygame.Rect(0, 1, length, 1))
    return surface
