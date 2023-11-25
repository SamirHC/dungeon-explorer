import os
import xml.etree.ElementTree as ET
from PIL import Image
import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.pokemon.pokemon_sprite import SpriteSheet, SpriteCollection
from app.pokemon import shadow
from app.common import constants


class PokemonSpriteDatabase:
    def __init__(self):
        self.base_dir = os.path.join(IMAGES_DIRECTORY, "sprites")
        self.loaded: dict[int, SpriteCollection] = {}

    def __getitem__(self, dex: int) -> SpriteCollection:
        if dex not in self.loaded:
            self.load(dex)
        return self.loaded[dex]

    def load(self, dex: int):
        sprite_dir = os.path.join(self.base_dir, str(dex))

        def _get_file(filename):
            return os.path.join(sprite_dir, filename)            

        def _load_sprite_sheet(anim: ET.Element) -> SpriteSheet:
            anim_name = anim.find("Name").text
            filename = _get_file(f"{anim_name}-Anim.png")
            sheet = pygame.image.load(filename).convert_alpha()
            frame_size = int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text)
            durations = tuple([int(d.text) for d in anim.find("Durations").findall("Duration")])
            colors = [pygame.Color(c[1]) for c in Image.open(filename).convert("RGBA").getcolors() if c[1] != constants.TRANSPARENT]
            return SpriteSheet(anim_name, sheet, frame_size, durations, colors)
        
        anim_data_file = _get_file("AnimData.xml")
        anim_root = ET.parse(anim_data_file).getroot()

        shadow_size = shadow.ShadowSize(int(anim_root.find("ShadowSize").text))

        anims = anim_root.find("Anims").findall("Anim")
        sprite_sheets = {}
        for anim in anims:
            index_elem = anim.find("Index")
            if index_elem is None:
                continue
            index = int(index_elem.text)
            if anim.find("CopyOf") is not None:
                copy_anim_name = anim.find("CopyOf").text
                for anim_ in anims:
                    if anim_.find("Name").text == copy_anim_name:
                        anim = anim_
            sprite_sheets[index] = _load_sprite_sheet(anim)

        sprite_collection = SpriteCollection(
            sprite_sheets,
            shadow_size
        )
        self.loaded[dex] = sprite_collection
