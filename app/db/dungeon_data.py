import functools

from app.dungeon.dungeon_data import DungeonData
import app.db.database as db
import app.db.floor_data as floor_data_db


_cursor = db.main_db.cursor()


@functools.lru_cache(maxsize=1)
def load(dungeon_id: int) -> DungeonData:
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
        turn_limit,
    ) = _cursor.execute(
        "SELECT name, banner, is_below, exp_enabled, recruiting_enabled,"
        "level_reset, money_reset, iq_enabled, reveal_traps,enemies_drop_boxes,"
        "max_rescue,max_items,max_party,turn_limit "
        "FROM dungeons "
        "WHERE id = ?",
        (dungeon_id,),
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
        floor_list=floor_data_db.load_floor_list(dungeon_id),
    )
