import os
import xml.etree.ElementTree as ET

from app.common.constants import GAMEDATA_DIRECTORY
from app.dungeon.dungeon_data import DungeonData
from app.dungeon.floor_data import FloorData
import app.db.database as db


class DungeonDataDatabase:
    def __init__(self):
        self.base_dir = os.path.join(GAMEDATA_DIRECTORY, "dungeons")
        self.cursor = db.main_db.cursor()
        
        for i in range(100):
            self.load(i)
        print("loaded")

    def load(self, dungeon_id: int) -> DungeonData:
        (
            name,
            banner,
            is_below,
            exp_enabled,
            recruiting_enabled,
            level_reset,
            money_reset,
            iq_enabled,
            reveal_traps,
            enemies_drop_boxes,
            max_rescue,
            max_items,
            max_party,
            turn_limit
        ) = self.cursor.execute(
            "SELECT name, banner, is_below, exp_enabled, recruiting_enabled,"
                "level_reset, money_reset, iq_enabled, reveal_traps,enemies_drop_boxes,"
                "max_rescue,max_items,max_party,turn_limit "
            "FROM dungeons "
            "WHERE id = ?",
            (dungeon_id,)
        ).fetchone()

        return DungeonData(
            dungeon_id=dungeon_id,
            name=name,
            banner=banner,
            is_below=bool(is_below),
            exp_enabled=bool(exp_enabled),
            recruiting_enabled=bool(recruiting_enabled),
            level_reset=bool(level_reset),
            money_reset=bool(money_reset),
            iq_enabled=bool(iq_enabled),
            reveal_traps=bool(reveal_traps),
            enemies_drop_boxes=bool(enemies_drop_boxes),
            max_rescue=max_rescue,
            max_items=max_items,
            max_party=max_party,
            turn_limit=turn_limit,
            floor_list=self.load_floor_list(dungeon_id),
        )

    def load_floor_list(self, dungeon_id: int):
        file = os.path.join(self.base_dir, f"floor_list{dungeon_id}.xml")
        root = ET.parse(file).getroot()
        res: list[FloorData] = []
        for r in root.findall("Floor"):
            res.append(FloorData(dungeon_id, r))
        return res
