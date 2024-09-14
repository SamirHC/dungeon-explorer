from app.dungeon.dungeon_data import DungeonData
from app.dungeon.floor_data import FloorData
import app.db.database as db


class DungeonDataDatabase:
    def __init__(self):
        self.cursor = db.main_db.cursor()

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
        return [FloorData(dungeon_id, floor_id) for (floor_id,) in self.cursor.execute(
            "SELECT floor_id FROM floors "
            "WHERE dungeon_id = ? "
            "ORDER BY floor_id",
            (dungeon_id, )
        )]
