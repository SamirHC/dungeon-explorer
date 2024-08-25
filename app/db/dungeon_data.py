import csv
import os
import xml.etree.ElementTree as ET

from app.common.constants import GAMEDATA_DIRECTORY
from app.dungeon.dungeon_data import DungeonData
from app.dungeon.floor_data import FloorData


class DungeonDataDatabase:
    def __init__(self):
        self.base_dir = os.path.join(GAMEDATA_DIRECTORY, "dungeons")

    def load(self, dungeon_id: int) -> DungeonData:
        csvfile = os.path.join(self.base_dir, "dungeons.csv")

        with open(csvfile, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                if i == dungeon_id:
                    break
                i += 1

        return DungeonData(
            dungeon_id=dungeon_id,
            name=row["Name"],
            banner=row["Banner"],
            is_below=bool(int(row["IsBelow"])),
            exp_enabled=bool(int(row["ExpEnabled"])),
            recruiting_enabled=bool(int(row["RecruitingEnabled"])),
            level_reset=bool(int(row["LevelReset"])),
            money_reset=bool(int(row["MoneyReset"])),
            iq_enabled=bool(int(row["IqEnabled"])),
            reveal_traps=bool(int(row["RevealTraps"])),
            enemies_drop_boxes=bool(int(row["EnemiesDropBoxes"])),
            max_rescue=int(row["MaxRescue"]),
            max_items=int(row["MaxItems"]),
            max_party=int(row["MaxParty"]),
            turn_limit=int(row["TurnLimit"]),
            floor_list=self.load_floor_list(dungeon_id),
        )

    def load_floor_list(self, dungeon_id: int):
        file = os.path.join(self.base_dir, f"floor_list{dungeon_id}.xml")
        root = ET.parse(file).getroot()
        return [FloorData(r) for r in root.findall("Floor")]
