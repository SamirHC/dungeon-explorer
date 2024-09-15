import functools

from app.dungeon.floor_data import FloorData
import app.db.database as db


_cursor = db.main_db.cursor()


@functools.lru_cache(maxsize=2)
def load(dungeon_id: int, floor_id: int) -> FloorData:
    return FloorData(dungeon_id, floor_id)


def load_floor_list(dungeon_id: int) -> list[FloorData]:
    return [
        load(dungeon_id, floor_id)
        for (floor_id,) in _cursor.execute(
            "SELECT floor_id FROM floors WHERE dungeon_id = ? ORDER BY floor_id",
            (dungeon_id,),
        )
    ]
