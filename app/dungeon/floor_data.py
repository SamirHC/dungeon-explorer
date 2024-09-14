from dataclasses import dataclass
import random

from app.common.constants import RNG
from app.dungeon.weather import Weather
from app.dungeon.trap import Trap
from app.dungeon.darkness_level import DarknessLevel
from app.dungeon.structure import Structure
import app.db.database as db


class FloorData:
    """
    A class that stores the data for the floor generation algorithm.
    """
    @dataclass(frozen=True)
    class SpawnableEnemy:
        poke_id: int
        level: int
        weight: int
        weight_2: int

    def __init__(self, dungeon_id: int, floor_id: int):
        """
        Parses an XML element containing all floor data required for generation.
        """
        cursor = db.main_db.cursor()
        (
            self.structure, self.tileset, self.bgm, self.weather, self.fixed_floor_id, self.darkness_level,
            self.room_density, self.floor_connectivity, self.initial_enemy_density, self.dead_ends, self.item_density, self.trap_density, self.extra_hallway_density,
             self.buried_item_density, self.water_density, self.max_coin_amount, self.shop, self.monster_house, self.sticky_item, self.empty_monster_house, self.hidden_stairs,
             self.secondary_used, self.secondary_percentage, self.imperfect_rooms, self.unkE, self.kecleon_shop_item_positions, self.hidden_stairs_type, self.enemy_iq, self.iq_booster_boost
        ) = cursor.execute(
            "SELECT structure, tileset, bgm, weather, fixed_floor_id, darkness_level,"
            "room_density, floor_connectivity, initial_enemy_density, dead_ends, item_density, trap_density, extra_hallway_density,"
            "buried_item_density, water_density, max_coin_amount, shop, monster_house, sticky_item, empty_monster_house, hidden_stairs,"
            "secondary_used, secondary_percentage, imperfect_rooms, unkE, kecleon_shop_item_positions, hidden_stairs_type, enemy_iq, iq_booster_boost "
            "FROM floors WHERE dungeon_id = ? AND floor_id = ?",
            (dungeon_id, floor_id)
        ).fetchone()

        self.structure = Structure(self.structure)
        self.weather = Weather(self.weather)
        self.darkness_level = DarknessLevel(self.darkness_level)

        self.monster_list = [FloorData.SpawnableEnemy(*r) for r in cursor.execute(
            "SELECT poke_id, level, weight, weight_2 "
            "FROM floor_monsters "
            "WHERE dungeon_id = ? AND floor_id = ?"
            "ORDER BY weight",
            (dungeon_id, floor_id)
        ).fetchall()]

        self.trap_list, self.trap_weights = zip(*cursor.execute(
            "SELECT name, weight FROM floor_traps "
            "WHERE dungeon_id = ? AND floor_id = ?"
            "ORDER BY weight",
            (dungeon_id, floor_id)
        ).fetchall())

        self.item_list = cursor.execute(
            "SELECT item_list_type, item_id, weight FROM floor_items "
            "WHERE dungeon_id = ? AND floor_id = ?",
            (dungeon_id, floor_id)
        ).fetchall()
        self.item_categories = cursor.execute(
            "SELECT item_list_type, category_name, weight FROM floor_item_categories "
            "WHERE dungeon_id = ? AND floor_id = ?",
           (dungeon_id, floor_id)
        )

    def get_random_pokemon(self, generator: random.Random = RNG) -> tuple[int, int]:
        return generator.choices(
            [(m.poke_id, m.level) for m in self.monster_list],
            cum_weights=[m.weight for m in self.monster_list]
        )[0]

    def get_random_trap(self, generator: random.Random = RNG) -> Trap:
        return Trap(generator.choices(self.trap_list, self.trap_weights)[0])

    def get_room_density_value(self, generator: random.Random = RNG) -> int:
        """
        Interprets value stored in room_density.
        A negative room_density is an exact value (positive).
        Otherwise, some random value added.

        :return: Max number of cells to be rooms.
        """
        if self.room_density < 0:
            return -self.room_density
        return self.room_density + generator.randrange(0, 3)
