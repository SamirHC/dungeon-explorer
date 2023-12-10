import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants
from app.common.constants import FONT_DIRECTORY
from app.guicomponents.font import Font, GraphicFont


class FontDatabase:
    def __init__(self):
        self.banner_font = self.load_banner_font()
        self.normal_font = self.load_normal_font()
        self.graphic_font = self.load_graphic_font()
        self.init_fonts()

    def load_banner_font(self):
        sheet_path = os.path.join(FONT_DIRECTORY, "banner", "banner.png")
        sheet = pygame.image.load(sheet_path)
        metadata_path = os.path.join(FONT_DIRECTORY, "banner", "banner.xml")
        metadata = self.load_metadata(metadata_path)
        return Font(sheet, metadata)

    def load_normal_font(self):
        sheet_path = os.path.join(FONT_DIRECTORY, "normal", "normal_font.png")
        sheet = pygame.image.load(sheet_path)
        metadata_path = os.path.join(FONT_DIRECTORY, "normal", "normal_font.xml")
        metadata = self.load_metadata(metadata_path)
        return Font(sheet, metadata).set_colorable(15, constants.WHITE)

    def _load_graphic(self, file_name: str) -> pygame.Surface:
        base_dir = os.path.join(FONT_DIRECTORY, "graphic")
        path = os.path.join(base_dir, file_name)
        return pygame.image.load(path)

    def load_graphic_font(self):
        NUM_GRAPHICS = 69
        sheet = {
            i: self._load_graphic(f"FONT_markfont_00{i:02d}.png")
            for i in range(NUM_GRAPHICS)
        }
        return GraphicFont(sheet)

    def load_metadata(self, path: str):
        metadata = ET.parse(path).getroot()
        widths = {}
        elements = metadata.find("Table").findall("Char")
        for el in elements:
            char_id = int(el.get("id"))
            width = int(el.get("width"))
            widths[char_id] = width
        return widths

    def init_fonts(self):
        self.normal_font.init()
        self.graphic_font.init()
