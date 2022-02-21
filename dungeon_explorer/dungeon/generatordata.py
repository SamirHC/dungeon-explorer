import xml.etree.ElementTree as ET


class FloorGeneratorData:
    def __init__(self, root: ET.Element):
        floor_layout = root.find("FloorLayout")
        self.structure = floor_layout.get("structure")
        self.tileset = floor_layout.get("tileset")
        self.bgm = floor_layout.get("bgm")
        self.weather = floor_layout.get("weather")
        self.fixed_floor_id = floor_layout.get("fixed_floor_id")
        self.darkness_level = floor_layout.get("darkness_level")
        
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
    