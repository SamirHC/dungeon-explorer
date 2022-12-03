import os
import pygame
import xml.etree.ElementTree as ET

from app.common.font import Font, GraphicFont
from app.common import constants


class FontDatabase:
    def __init__(self):
        self.banner_font = self.load_banner_font()
        self.normal_font = self.load_normal_font()
        self.graphic_font = self.load_graphic_font()
        self.init_fonts()

    def load_banner_font(self):
        sheet_path = os.path.join("assets", "font", "banner", "banner.png")
        sheet = pygame.image.load(sheet_path)
        metadata_path = os.path.join("assets", "font", "banner", "banner.xml")
        metadata = self.load_metadata(metadata_path)
        return Font(sheet, metadata)

    def load_normal_font(self):
        sheet_path = os.path.join(
            "assets", "font", "normal", "normal_font.png")
        sheet = pygame.image.load(sheet_path)
        metadata_path = os.path.join(
            "assets", "font", "normal", "normal_font.xml")
        metadata = self.load_metadata(metadata_path)
        return Font(sheet, metadata, 15, constants.WHITE)

    def load_graphic_font(self):
        NUM_GRAPHICS = 69
        base_dir = os.path.join("assets", "font", "graphic")
        sheet = {i: pygame.image.load(os.path.join(
            base_dir, f"FONT_markfont_00{i:02d}.png")) for i in range(NUM_GRAPHICS)}
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
        self.normal_font.font_sheet.set_colorkey(self.normal_font.colorkey)
        self.graphic_font.set_colorkey()
