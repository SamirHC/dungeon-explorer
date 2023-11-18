import os
import xml.etree.ElementTree as ET
import csv

from app.common.constants import GAMEDATA_DIRECTORY
from app.dungeon.floor_data import FloorData


class DungeonData:
    def __init__(self, dungeon_id: int):
        self.dungeon_id = dungeon_id
        self.directory = os.path.join(GAMEDATA_DIRECTORY, "dungeons")

        self.load_dungeon_data()
        self.floor_list = self.load_floor_list()

    def load_dungeon_data(self):
        csvfile = os.path.join(self.directory, "dungeons.csv")

        with open(csvfile, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                if i == self.dungeon_id:
                    break
                i += 1

        self.name = row["Name"]
        self.banner = row["Banner"]
        self.is_below = bool(int(row["IsBelow"]))
        self.exp_enabled = bool(int(row["ExpEnabled"]))
        self.recruiting_enabled = bool(int(row["RecruitingEnabled"]))
        self.level_reset = bool(int(row["LevelReset"]))
        self.money_reset = bool(int(row["MoneyReset"]))
        self.iq_enabled = bool(int(row["IqEnabled"]))
        self.reveal_traps = bool(int(row["RevealTraps"]))
        self.enemies_drop_boxes = bool(int(row["EnemiesDropBoxes"]))
        self.max_rescue = int(row["MaxRescue"])
        self.max_items = int(row["MaxItems"])
        self.max_party = int(row["MaxParty"])
        self.turn_limit = int(row["TurnLimit"])

    def load_floor_list(self):
        file = os.path.join(self.directory, f"floor_list{self.dungeon_id}.xml")
        root = ET.parse(file).getroot()
        return [FloorData(r) for r in root.findall("Floor")]

    @property
    def number_of_floors(self) -> int:
        return len(self.floor_list)


