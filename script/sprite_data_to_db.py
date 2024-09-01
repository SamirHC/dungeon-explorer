import pygame
import os
import xml.etree.ElementTree as ET
import sqlite3
import pickle


dirname = os.path.dirname(__file__)
base_dir = os.path.join(dirname, "..", "assets", "images", "sprites")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)


def load(path, dex, variant):
    anim_data_file = os.path.join(path, "AnimData.xml")
    root = ET.parse(anim_data_file).getroot()

    anims = root.find("Anims").findall("Anim")
    shadow_position_map = {}
    offset_positions_map = {}
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
        shadow_position_map[index] = get_shadow_positions(dex, variant, anim_node)
        offset_positions_map[index] = get_offset_positions(dex, variant, anim_node)

    return shadow_position_map, offset_positions_map


def get_shadow_positions(dex, variant, anim: ET.Element):
    anim_name = anim.find("Name").text
    frame_size = int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text)
    shadow_filename = os.path.join(base_dir, dex, variant, f"{anim_name}-Shadow.png")
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


def get_offset_positions(dex, variant, anim: ET.Element):
    anim_name = anim.find("Name").text
    frame_size = int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text)
    offset_filename = os.path.join(base_dir, dex, variant, f"{anim_name}-Offsets.png")
    offset_sheet = pygame.image.load(offset_filename)
    width, height = offset_sheet.get_size()

    offsets: dict[tuple[int, int, int], list[list[tuple[int, int]]]] = {
        BLACK: [],
        GREEN: [],
        RED: [],
        BLUE: [],
    }
    for y in range(height):
        if y % frame_size[1] == 0:
            for offset in offsets.values():
                offset.append([])
        for x in range(width):
            pixel_color = tuple(offset_sheet.get_at((x, y)))
            if pixel_color in offsets.keys():
                offsets[pixel_color][-1].append((x, y))
    return {
        offset_color: [
            [(x % frame_size[0], y % frame_size[1]) for x, y in sorted(row)]
            for row in color_offsets
        ]
        for offset_color, color_offsets in offsets.items()
    }


def pretty_print(k, v):
    print(f"Dex: {k}")
    for index, positions in v.items():
        print(f"Index: {index}")
        print(f"Positions ({len(positions[0])}x{len(positions)}) {positions}")


def main():
    db = sqlite3.connect(os.path.join(dirname, "..", "data", "gamedata", "gamedata.db"))
    for dir in os.listdir(base_dir):
        path = os.path.join(base_dir, dir)
        inner_dirs = [d for d in os.listdir(path) if d.startswith("00")]
        for d in inner_dirs:
            ip = os.path.join(path, d)
            
            shadow_position_map, offset_positions_map = load(ip, dir, d)
            pickled_shadows = pickle.dumps(shadow_position_map)
            pickled_offsets = pickle.dumps(offset_positions_map)
            db.execute(
                "INSERT INTO sprite_data (dex, shadow_positions, offset_positions, variant) "
                "VALUES (?, ?, ?, ?) ",
                (dir, pickled_shadows, pickled_offsets, int(d)),
            )
            
    """
    get = db.execute(f"SELECT shadow_positions FROM sprite_data WHERE dex = ?", (1,))
    row = get.fetchone()
    pretty_print(dex, pickle.loads(row[0]))
    """
    get = db.execute(
        "SELECT * FROM sprite_data "
        "WHERE variant != ?", 
        (0, )
    )
    #rows = get.fetchall()
    #for r in rows:
    #    print(r)
    #print(pickle.loads(row[0]))
    db.commit()
    db.close()


def main_2():
    db = sqlite3.connect(os.path.join(dirname, "..", "data", "gamedata", "gamedata.db"))
    db.execute("ALTER TABLE sprite_data ADD offset_positions BINARY")
    for dex in range(896):
        try:
            data = load(str(dex))
            pickled_data = pickle.dumps(data)
            db.execute(
                "UPDATE sprite_data SET offset_positions = ? WHERE dex = ?",
                (pickled_data, dex),
            )
            db.commit()
        except Exception:
            pass
    db.close()

