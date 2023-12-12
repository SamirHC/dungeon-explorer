import pygame
import os
import xml.etree.ElementTree as ET
import sqlite3
import pickle

from app.common import constants


loaded = {}


def load(dex: str):
    anim_data_file = os.path.join(
        constants.IMAGES_DIRECTORY, "sprites", dex, "AnimData.xml"
    )
    root = ET.parse(anim_data_file).getroot()

    anims = root.find("Anims").findall("Anim")
    shadow_position_map = {}
    for anim_node in anims:
        index_elem = anim_node.find("Index")
        if index_elem is None:
            continue
        index = int(index_elem.text)
        if anim_node.find("CopyOf") is not None:
            copy_anim_name = anim_node.find("CopyOf").text
            for anim in anims:
                if anim.find("Name").text == copy_anim_name:
                    anim_node = anim
        shadow_position_map[index] = get_shadow_positions(dex, anim_node)

    loaded[dex] = shadow_position_map
    return loaded[dex]


def get_shadow_positions(dex, anim: ET.Element):
    anim_name = anim.find("Name").text
    frame_size = int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text)
    shadow_filename = os.path.join(
        constants.IMAGES_DIRECTORY, "sprites", dex, f"{anim_name}-Shadow.png"
    )
    shadow_sheet = pygame.image.load(shadow_filename)
    width, height = shadow_sheet.get_size()
    shadow_positions: list[list[tuple[int, int]]] = []
    for y in range(height):
        if y % frame_size[1] == 0:
            shadow_positions.append([])
        for x in range(width):
            pixel_color = shadow_sheet.get_at((x, y))
            if pixel_color == (255, 255, 255):
                shadow_positions[-1].append((x, y))
    return [
        [(x % frame_size[0], y % frame_size[1]) for x, y in sorted(row)]
        for row in shadow_positions
    ]


def pretty_print(k, v):
    print(f"Dex: {k}")
    for index, positions in v.items():
        print(f"Index: {index}")
        print(f"Positions ({len(positions[0])}x{len(positions)}) {positions}")


def main():
    db = sqlite3.connect(os.path.join(constants.GAMEDATA_DIRECTORY, "gamedata.db"))
    db.execute(
        f"CREATE TABLE IF NOT EXISTS sprite_data (dex INTEGER PRIMARY KEY NOT NULL, shadow_positions BINARY NOT NULL)"
    )
    for dex in range(896):
        try:
            data = load(str(dex))
            pickled_data = pickle.dumps(data)
            db.execute(
                f"INSERT INTO sprite_data (dex, shadow_positions) VALUES (?, ?) ON CONFLICT DO UPDATE SET shadow_positions=shadow_positions",
                (dex, pickled_data),
            )
            db.commit()
        except:
                pass
    """
    get = db.execute(f"SELECT shadow_positions FROM sprite_data WHERE dex = ?", (1,))
    row = get.fetchone()
    pretty_print(dex, pickle.loads(row[0]))
    """
    db.close()


main()
