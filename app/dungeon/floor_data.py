from dataclasses import dataclass
import random

from app.common.constants import RNG
from app.dungeon.weather import Weather
from app.dungeon.trap import Trap
from app.dungeon.darkness_level import DarknessLevel
from app.dungeon.structure import Structure


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
    trap_list: list[Trap]
    trap_weights: list[int]
    item_list: list
    item_categories: list

    def get_random_pokemon(self, generator: random.Random = RNG) -> tuple[int, int]:
        return generator.choices(
            [(m.poke_id, m.level) for m in self.monster_list],
            cum_weights=[m.weight for m in self.monster_list],
        )[0]

    def get_random_trap(self, generator: random.Random = RNG) -> Trap:
        return generator.choices(self.trap_list, self.trap_weights)[0]

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
