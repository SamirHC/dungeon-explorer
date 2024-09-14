import random
import xml.etree.ElementTree as ET

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

    def __init__(self, dungeon_id: int, root: ET.Element):
        """
        Parses an XML element containing all floor data required for generation.
        """        
        floor_layout = root.find("FloorLayout")
        self.number = int(floor_layout.get("number"))

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
            (dungeon_id, self.number)
        ).fetchone()
        
        self.structure = Structure(self.structure)
        self.weather = Weather(self.weather)
        self.darkness_level = DarknessLevel(self.darkness_level)

        self.monster_list = root.find("MonsterList").findall("Monster")
        self.trap_list = root.find("TrapList").findall("Trap")
        self.item_lists = root.findall("ItemList")


    def get_weights(self, elements: list[ET.Element]) -> list[int]:
        return [int(el.get("weight")) for el in elements]

    def pick_random_element(
        self, elements: list[ET.Element], generator: random.Random = RNG
    ) -> ET.Element:
        return generator.choices(elements, cum_weights=self.get_weights(elements))[0]

    def get_random_pokemon(self, generator: random.Random = RNG) -> tuple[int, int]:
        el = self.pick_random_element(self.monster_list, generator)
        return int(el.get("id")), int(el.get("level"))

    def get_random_trap(self) -> Trap:
        el = self.pick_random_element(self.trap_list)
        return Trap(el.get("name"))

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
