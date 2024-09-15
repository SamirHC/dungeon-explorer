import os
import xml.etree.ElementTree as ET
import pickle

import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.gui.sprite_sheet import SpriteSheet
from app.gui.sprite_collection import SpriteCollection
from app.pokemon.animation_id import AnimationId
from app.pokemon.shadow_size import ShadowSize
import app.db.database as db


base_dir = os.path.join(IMAGES_DIRECTORY, "sprites")
cursor = db.main_db.cursor()


def load(dex: int, variant: int) -> SpriteCollection:
    sprite_dir = os.path.join(base_dir, str(dex))
    if variant != -1:
        sprite_dir = os.path.join(sprite_dir, str(variant).zfill(4))
    cursor.execute(
        """
            SELECT shadow_positions, offset_positions
            FROM sprite_data
            WHERE dex == ? AND variant == ?
        """,
        (dex, variant),
    )
    all_shadow_positions, all_offset_positions = list(
        map(pickle.loads, cursor.fetchone())
    )

    def _load_sprite_sheet(anim: ET.Element) -> SpriteSheet:
        anim_name = anim.find("Name").text
        index = int(anim.find("Index").text)
        frame_width = int(anim.find("FrameWidth").text)
        frame_height = int(anim.find("FrameHeight").text)
        durations = tuple(
            int(d.text) for d in anim.find("Durations").findall("Duration")
        )

        filename = os.path.join(sprite_dir, f"{anim_name}-Anim.png")
        sheet = pygame.image.load(filename).convert_alpha()

        shadow_positions = all_shadow_positions[index]
        offset_positions = all_offset_positions[index]
        return SpriteSheet(
            anim_name,
            sheet,
            (frame_width, frame_height),
            durations,
            shadow_positions,
            offset_positions,
        )

    anim_data_file = os.path.join(sprite_dir, "AnimData.xml")
    anim_root = ET.parse(anim_data_file).getroot()

    shadow_size = ShadowSize(int(anim_root.find("ShadowSize").text))

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
        sprite_sheets[AnimationId(index)] = _load_sprite_sheet(anim)

    return SpriteCollection(sprite_sheets, shadow_size)
