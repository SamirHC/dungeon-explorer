import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants
from app.gui.font import Font, GraphicFont


def load_banner_font():
    sheet_path = os.path.join(constants.FONT_DIRECTORY, "banner", "banner.png")
    sheet = pygame.image.load(sheet_path)
    sheet.set_colorkey(constants.BLACK)
    metadata_path = os.path.join(constants.FONT_DIRECTORY, "banner", "banner.xml")
    metadata = load_metadata(metadata_path)
    return Font(sheet, metadata)


def load_normal_font():
    sheet_path = os.path.join(constants.FONT_DIRECTORY, "normal", "normal_font.png")
    sheet = pygame.image.load(sheet_path)
    metadata_path = os.path.join(constants.FONT_DIRECTORY, "normal", "normal_font.xml")
    metadata = load_metadata(metadata_path)
    char_map = {"♂": 189, "♀": 190}  # CURRENTLY HARDCODED
    return Font(sheet, metadata, char_map).set_colorable(15, constants.WHITE)


def _load_graphic(file_name: str) -> pygame.Surface:
    base_dir = os.path.join(constants.FONT_DIRECTORY, "graphic")
    path = os.path.join(base_dir, file_name)
    return pygame.image.load(path)


def load_graphic_font():
    NUM_GRAPHICS = 69
    sheet = {
        i: _load_graphic(f"FONT_markfont_00{i:02d}.png") for i in range(NUM_GRAPHICS)
    }
    return GraphicFont(sheet)


def load_metadata(path: str):
    metadata = ET.parse(path).getroot()
    widths = {}
    elements = metadata.find("Table").findall("Char")
    for el in elements:
        char_id = int(el.get("id"))
        width = int(el.get("width"))
        widths[char_id] = width
    return widths


banner_font = None
normal_font = None
graphic_font = None


def init_fonts():
    global banner_font
    global normal_font
    global graphic_font

    banner_font = load_banner_font()
    normal_font = load_normal_font()
    graphic_font = load_graphic_font()

    normal_font.init()
    graphic_font.init()
