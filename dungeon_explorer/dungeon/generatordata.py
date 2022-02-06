import xml.etree.ElementTree as ET


class FloorGeneratorData:
    def __init__(self, root: ET.Element):
        self.root = root        

    def floor_layout(self):
        return self.root.find("FloorLayout")

    @property
    def structure(self):
        return self.floor_layout().get("structure")

    @property
    def tileset(self):
        return self.floor_layout().get("tileset")

    @property
    def bgm(self):
        return self.floor_layout().get("bgm")

    @property
    def weather(self):
        return self.floor_layout().get("weather")

    @property
    def fixed_floor_id(self):
        return self.floor_layout().get("fixed_floor_id")

    @property
    def darkness_level(self):
        return self.floor_layout().get("darkness_level")

    def generator_settings(self):
        return self.floor_layout().find("GeneratorSettings")

    @property
    def room_density(self):
        return int(self.generator_settings().get("room_density"))

    @property
    def floor_connectivity(self):
        return int(self.generator_settings().get("floor_connectivity"))

    @property
    def initial_enemy_density(self):
        return int(self.generator_settings().get("initial_enemy_density"))

    @property
    def dead_ends(self):
        return int(self.generator_settings().get("dead_ends"))

    @property
    def item_density(self):
        return int(self.generator_settings().get("item_density"))

    @property
    def trap_density(self):
        return int(self.generator_settings().get("trap_density"))

    @property
    def extra_hallway_density(self):
        return int(self.generator_settings().get("extra_hallway_density"))

    @property
    def buried_item_density(self):
        return int(self.generator_settings().get("buried_item_density"))
        
    @property
    def water_density(self):
        return int(self.generator_settings().get("water_density"))

    @property
    def max_coin_amount(self):
        return int(self.generator_settings().get("max_coin_amount"))
    
    def chances(self):
        return self.floor_layout().find("Chances")

    @property
    def shop(self):
        return int(self.chances().get("shop"))

    @property
    def monster_house(self):
        return int(self.chances().get("monster_house"))

    @property
    def sticky_item(self):
        return int(self.chances().get("sticky_item"))

    @property
    def empty_monster_house(self):
        return int(self.chances().get("empty_monster_house"))

    @property
    def hidden_stairs(self):
        return int(self.chances().get("hidden_stairs"))
    
    def terrain_settings(self):
        return self.floor_layout().find("TerrainSettings")

    @property
    def secondary_used(self):
        return int(self.terrain_settings().get("secondary_used"))
        
    @property
    def secondary_percentage(self):
        return int(self.terrain_settings().get("secondary_percentage"))

    @property
    def imperfect_rooms(self):
        return int(self.terrain_settings().get("imperfect_rooms"))

    def misc_settings(self):
        return self.floor_layout().find("MiscSettings")

    @property
    def kecleon_shop_item_positions(self):
        return int(self.misc_settings().get("kecleon_shop_item_positions"))
        
    @property
    def unk_hidden_stairs(self):
        return int(self.misc_settings().get("unk_hidden_stairs"))
    
    @property
    def enemy_iq(self):
        return int(self.misc_settings().get("enemy_iq"))
    
    @property
    def iq_booster_boost(self):
        return int(self.misc_settings().get("iq_booster_boost"))

    def monster_list(self):
        return self.root.find("MonsterList").findall("Monster")

    def trap_list(self):
        return self.root.find("TrapList").findall("Trap")

    def item_lists(self):
        return self.root.findall("ItemList")
    