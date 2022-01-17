import dungeon_map
import os
import xml.etree.ElementTree as ET


class FloorData:
    def __init__(self, dungeon_id, floor_number):
        self.dungeon_id = dungeon_id
        self.floor_number = floor_number
        file = os.path.join(os.getcwd(), "gamedata", "dungeons", f"{dungeon_id}.xml")
        tree = ET.parse(file)
        self.root = tree.getroot().findall("Floor")[floor_number]


