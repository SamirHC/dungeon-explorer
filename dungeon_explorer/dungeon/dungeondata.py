import os
import random
import xml.etree.ElementTree as ET

from dungeon_explorer.dungeon import dungeonstatus, trap


class DungeonData:
    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.directory = os.path.join("data", "gamedata", "dungeons", self.dungeon_id)

        self.load_dungeon_data()
        self.floor_list = self.load_floor_list()

    def load_dungeon_data(self):
        file = os.path.join(self.directory, f"dungeon_data{self.dungeon_id}.xml")
        root = ET.parse(file).getroot()
        self.name = root.find("Name").text
        self.banner = root.find("Banner").text if root.find("Banner") is not None else self.name
        self.is_below = bool(int(root.find("IsBelow").text))
        self.exp_enabled = bool(int(root.find("ExpEnabled").text))
        self.recruiting_enabled = bool(int(root.find("RecruitingEnabled").text))
        self.level_reset = bool(int(root.find("LevelReset").text))
        self.money_reset = bool(int(root.find("MoneyReset").text))
        self.iq_enabled = bool(int(root.find("IqEnabled").text))
        self.reveal_traps = bool(int(root.find("RevealTraps").text))
        self.enemies_drop_boxes = bool(int(root.find("EnemiesDropBoxes").text))
        self.max_rescue = int(root.find("MaxRescue").text)
        self.max_items = int(root.find("MaxItems").text)
        self.max_party = int(root.find("MaxParty").text)
        self.turn_limit = int(root.find("TurnLimit").text)
    
    def load_floor_list(self):
        file = os.path.join(self.directory, f"floor_list{self.dungeon_id}.xml")
        root = ET.parse(file).getroot()
        return [FloorData(r) for r in root.findall("Floor")]

    @property
    def number_of_floors(self) -> int:
        return len(self.floor_list)


class FloorData:
    def __init__(self, root: ET.Element):
        floor_layout = root.find("FloorLayout")
        self.structure = dungeonstatus.Structure(floor_layout.get("structure"))
        self.tileset = int(floor_layout.get("tileset"))
        self.bgm = int(floor_layout.get("bgm"))
        self.weather = dungeonstatus.Weather(floor_layout.get("weather"))
        self.fixed_floor_id = floor_layout.get("fixed_floor_id")
        self.darkness_level = dungeonstatus.DarknessLevel(floor_layout.get("darkness_level"))
        
        generator_settings = floor_layout.find("GeneratorSettings")
        self.room_density = int(generator_settings.get("room_density"))
        self.floor_connectivity = int(generator_settings.get("floor_connectivity"))
        self.initial_enemy_density = int(generator_settings.get("initial_enemy_density"))
        self.dead_ends = int(generator_settings.get("dead_ends"))
        self.item_density = int(generator_settings.get("item_density"))
        self.trap_density = int(generator_settings.get("trap_density"))
        self.extra_hallway_density = int(generator_settings.get("extra_hallway_density"))
        self.buried_item_density = int(generator_settings.get("buried_item_density"))
        self.water_density = int(generator_settings.get("water_density"))
        self.max_coin_amount = int(generator_settings.get("max_coin_amount"))
    
        chances = floor_layout.find("Chances")
        self.shop = int(chances.get("shop"))
        self.monster_house = int(chances.get("monster_house"))
        self.sticky_item = int(chances.get("sticky_item"))
        self.empty_monster_house = int(chances.get("empty_monster_house"))
        self.hidden_stairs = int(chances.get("hidden_stairs"))
    
        terrain_settings = floor_layout.find("TerrainSettings")
        self.secondary_used = int(terrain_settings.get("secondary_used"))
        self.secondary_percentage = int(terrain_settings.get("secondary_percentage"))
        self.imperfect_rooms = int(terrain_settings.get("imperfect_rooms"))

        misc_settings = floor_layout.find("MiscSettings")
        self.kecleon_shop_item_positions = int(misc_settings.get("kecleon_shop_item_positions"))
        self.unk_hidden_stairs = int(misc_settings.get("unk_hidden_stairs"))
        self.enemy_iq = int(misc_settings.get("enemy_iq"))
        self.iq_booster_boost = int(misc_settings.get("iq_booster_boost"))

        self.monster_list = root.find("MonsterList").findall("Monster")
        self.trap_list = root.find("TrapList").findall("Trap")
        self.item_lists = root.findall("ItemList")

    def get_weights(self, elements: list[ET.Element]) -> list[int]:
        return [int(el.get("weight")) for el in elements]

    def pick_random_element(self, elements: list[ET.Element]) -> ET.Element:
        return random.choices(elements, self.get_weights(elements))[0]

    def get_random_pokemon(self) -> tuple[int, int]:
        el = self.pick_random_element(self.monster_list)
        return int(el.get("id")), int(el.get("level"))

    def get_random_trap(self) -> trap.Trap:
        el = self.pick_random_element(self.trap_list)
        return trap.Trap(el.get("name"))
