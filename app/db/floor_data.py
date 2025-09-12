import functools

from app.dungeon.floor_data import FloorData, SpawnableEnemy
from app.dungeon.weather import Weather
from app.dungeon.trap import Trap
from app.dungeon.darkness_level import DarknessLevel
from app.dungeon.structure import Structure
import app.db.database as db


_cursor = db.main_db.cursor()


@functools.lru_cache(maxsize=2)
def load(dungeon_id: int, floor_id: int) -> FloorData:
    cursor = db.main_db.cursor()
    (
        structure,
        tileset,
        bgm,
        weather,
        fixed_floor_id,
        darkness_level,
        room_density,
        floor_connectivity,
        initial_enemy_density,
        dead_ends,
        item_density,
        trap_density,
        extra_hallway_density,
        buried_item_density,
        water_density,
        max_coin_amount,
        shop,
        monster_house,
        sticky_item,
        empty_monster_house,
        hidden_stairs,
        secondary_used,
        secondary_percentage,
        imperfect_rooms,
        unkE,
        kecleon_shop_item_positions,
        hidden_stairs_type,
        enemy_iq,
        iq_booster_boost,
    ) = cursor.execute(
        "SELECT structure, tileset, bgm, weather, fixed_floor_id,"
        " darkness_level, room_density, floor_connectivity,"
        " initial_enemy_density, dead_ends, item_density, trap_density,"
        " extra_hallway_density, buried_item_density, water_density,"
        " max_coin_amount, shop, monster_house, sticky_item,"
        " empty_monster_house, hidden_stairs, secondary_used,"
        " secondary_percentage, imperfect_rooms, unkE,"
        " kecleon_shop_item_positions, hidden_stairs_type, enemy_iq,"
        " iq_booster_boost "
        "FROM floors WHERE dungeon_id = ? AND floor_id = ?",
        (dungeon_id, floor_id),
    ).fetchone()

    structure = Structure(structure)
    weather = Weather(weather)
    darkness_level = DarknessLevel(darkness_level)

    monster_list = [
        SpawnableEnemy(*r)
        for r in cursor.execute(
            "SELECT poke_id, level, weight, weight_2 "
            "FROM floor_monsters "
            "WHERE dungeon_id = ? AND floor_id = ?"
            "ORDER BY weight",
            (dungeon_id, floor_id),
        ).fetchall()
    ]

    trap_list, trap_weights = zip(
        *cursor.execute(
            "SELECT name, weight FROM floor_traps "
            "WHERE dungeon_id = ? AND floor_id = ?"
            "ORDER BY weight",
            (dungeon_id, floor_id),
        ).fetchall()
    )
    trap_list = list(map(Trap, trap_list))

    item_list = cursor.execute(
        "SELECT item_list_type, item_id, weight FROM floor_items "
        "WHERE dungeon_id = ? AND floor_id = ?",
        (dungeon_id, floor_id),
    ).fetchall()
    item_categories = cursor.execute(
        "SELECT item_list_type, category_name, weight FROM floor_item_categories "
        "WHERE dungeon_id = ? AND floor_id = ?",
        (dungeon_id, floor_id),
    ).fetchall()
    return FloorData(
        structure,
        tileset,
        bgm,
        weather,
        fixed_floor_id,
        darkness_level,
        room_density,
        floor_connectivity,
        initial_enemy_density,
        dead_ends,
        item_density,
        trap_density,
        extra_hallway_density,
        buried_item_density,
        water_density,
        max_coin_amount,
        shop,
        monster_house,
        sticky_item,
        empty_monster_house,
        hidden_stairs,
        secondary_used,
        secondary_percentage,
        imperfect_rooms,
        unkE,
        kecleon_shop_item_positions,
        hidden_stairs_type,
        enemy_iq,
        iq_booster_boost,
        monster_list,
        trap_list,
        trap_weights,
        item_list,
        item_categories,
    )


def load_floor_list(dungeon_id: int) -> list[FloorData]:
    return [
        load(dungeon_id, floor_id)
        for (floor_id,) in _cursor.execute(
            "SELECT floor_id FROM floors WHERE dungeon_id = ? ORDER BY floor_id",
            (dungeon_id,),
        )
    ]
