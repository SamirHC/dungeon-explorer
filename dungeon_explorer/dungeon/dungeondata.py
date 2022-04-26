import os
import random
import xml.etree.ElementTree as ET

import pygame.mixer

from dungeon_explorer.dungeon import dungeonstatus, trap

def load_sound(name: str) -> pygame.mixer.Sound:
        music_dir = os.path.join("assets", "sound", "music")
        filename = os.path.join(music_dir, f"{name}.mp3")
        return pygame.mixer.Sound(filename)

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
        self.tileset = floor_layout.get("tileset")
        self.bgm = floor_layout.get("bgm")
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

    def get_random_pokemon(self) -> tuple[str, int]:
        el = self.pick_random_element(self.monster_list)
        return el.get("id"), int(el.get("level"))

    def get_random_trap(self) -> trap.Trap:
        el = self.pick_random_element(self.trap_list)
        return trap.Trap(el.get("name"))

    def get_sound(self) -> pygame.mixer.Sound:
        return self.bgm_map[self.bgm]

    bgm_map = {
        "0": load_sound("Treasure Town"),
        "1": load_sound("Beach Cave"),
        "2": load_sound("Drenched Bluff"),
        "3": load_sound("Mt. Bristle"),
        "4": load_sound("Waterfall Cave"),
        "5": load_sound("Apple Woods"),
        "6": load_sound("Craggy Coast"),
        "7": load_sound("Cave and Side Path"),
        "8": load_sound("Mt. Horn"),
        "9": load_sound("Foggy Forest"),
        "10": load_sound("Steam Cave"),
        "11": load_sound("Upper Steam Cave"),
        "12": load_sound("Amp Plains"),
        "13": load_sound("Far Amp Plains"),
        "14": load_sound("Northern Desert"),
        "15": load_sound("Quicksand Cave"),
        "16": load_sound("Quicksand Pit"),
        "17": load_sound("Crystal Cave"),
        "18": load_sound("Crystal Crossing"),
        "19": load_sound("Chasm Cave"),
        "20": load_sound("Dark Hill"),
        "21": load_sound("Sealed Ruin"),
        "22": load_sound("Sealed Ruin Pit"),
        "23": load_sound("Dusk Forest"),
        "24": load_sound("Deep Dusk Forest"),
        "25": load_sound("Treeshroud Forest"),
        "26": load_sound("Brine Cave"),
        "27": load_sound("Lower Brine Cave"),
        "28": load_sound("Hidden Land"),
        "29": load_sound("Hidden Highland"),
        "30": load_sound("Temporal Tower"),
        "31": load_sound("Temporal Spire"),
        "32": load_sound("Mystifying Forest"),
        "33": load_sound("Blizzard Island Rescue Team Medley"),
        "34": load_sound("Surrounded Sea"),
        "35": load_sound("Miracle Sea"),
        "36": load_sound("Aegis Cave"),
        "37": load_sound("Concealed Ruins"),
        "38": load_sound("Mt. Travail"),
        "39": load_sound("In The Nightmare"),
        "42": load_sound("Dark Crater"),
        "43": load_sound("Deep Dark Crater"),
        "117": load_sound("Marowak Dojo"),
    }
