from dataclasses import dataclass
import random

from app.common.constants import RNG
from app.dungeon.weather import Weather
from app.dungeon.trap import Trap
from app.dungeon.darkness_level import DarknessLevel
from app.dungeon.structure import Structure
import app.db.database as db


@dataclass(frozen=True)
class SpawnableEnemy:
    poke_id: int
    level: int
    weight: int
    weight_2: int


@dataclass(frozen=True)
class FloorData:
    structure: Structure
    tileset: int
    bgm: int
    weather: Weather
    fixed_floor_id: int
    darkness_level: DarknessLevel
    room_density: int
    floor_connectivity: int
    initial_enemy_density: int
    dead_ends: int
    item_density: int
    trap_density: int
    extra_hallway_density: int
    buried_item_density: int
    water_density: int
    max_coin_amount: int
    shop: int
    monster_house: int
    sticky_item: int
    empty_monster_house: int
    hidden_stairs: int
    secondary_used: int
    secondary_percentage: int
    imperfect_rooms: int
    unkE: int
    kecleon_shop_item_positions: int
    hidden_stairs_type: int
    enemy_iq: int
    iq_booster_boost: int
    monster_list: list[SpawnableEnemy]
    trap_list: list
    trap_weights: list[int]
    item_list: list
    item_categories: list

    @classmethod
    def from_db(cls, dungeon_id: int, floor_id: int):
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
            monster_list, trap_list, trap_weights, item_list, item_categories,
        )

    def get_random_pokemon(self, generator: random.Random = RNG) -> tuple[int, int]:
        return generator.choices(
            [(m.poke_id, m.level) for m in self.monster_list],
            cum_weights=[m.weight for m in self.monster_list],
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


if __name__ == "__main__":
    data = FloorData.from_db(6, 1)
    print(data)
