import os
import random
import xml.etree.ElementTree as ET

from dungeon_explorer.common import textbox
from dungeon_explorer.dungeon import (dungeondata, dungeonmap, floor, minimap, tileset)
from dungeon_explorer.pokemon import party, pokemon


class Dungeon:
    def __init__(self, dungeon_id: str, party: party.Party):
        # Dungeon-wide
        self.dungeon_id = dungeon_id
        self.party = party
        self.floor_list = self.load_floor_list()
        self.load_data()
        # Floor specific
        self.floor_number = 0
        self.active_enemies = []
        self.next_floor()
        self.message_log = textbox.TextBox((30, 7), 3)

    def load_data(self):
        file = os.path.join("data", "gamedata", "dungeons", self.dungeon_id, f"dungeon_data{self.dungeon_id}.xml")
        root = ET.parse(file).getroot()
        self.name = root.find("Name").text
        self.is_below = bool(int(root.find("IsBelow").text))

    def load_floor_list(self):
        file = os.path.join("data", "gamedata", "dungeons", self.dungeon_id, f"floor_list{self.dungeon_id}.xml")
        tree = ET.parse(file)
        return [dungeondata.FloorData(r) for r in tree.getroot().findall("Floor")]

    def has_next_floor(self) -> bool:
        return self.floor_number < len(self.floor_list)

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.monster_list = self.current_floor_data.monster_list
        self.floor = self.floor_builder.build_floor()
        self.tileset = tileset.TileSet(self.current_floor_data.tileset)
        self.minimap = minimap.MiniMap(self.floor)
        self.dungeonmap = dungeonmap.DungeonMap(self.floor, self.tileset, self.is_below)
        self.spawned = []
        self.spawn_party(self.party)
        self.spawn_enemies()
    
    @property
    def current_floor_data(self) -> dungeondata.FloorData:
        return self.floor_list[self.floor_number - 1]

    @property
    def user(self) -> pokemon.Pokemon:
        return self.party.user

    @property
    def all_sprites(self) -> list[pokemon.Pokemon]:
        return self.spawned

    @property
    def floor_builder(self) -> floor.FloorBuilder:
        return floor.FloorBuilder(self.current_floor_data)

    def get_random_pokemon(self) -> pokemon.Pokemon:
        id, level = self.current_floor_data.get_random_pokemon()
        return pokemon.EnemyPokemon(id, level)

    def user_at_stairs(self) -> bool:
        return self.party.user.position == self.floor.stairs_spawn

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return any(map(lambda s: s.position == position, self.all_sprites))

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.all_sprites])

    def next_turn(self):
        self.turns += 1
        for sprite in self.all_sprites:
            sprite.has_turn = True
            if self.turns % pokemon.Pokemon.REGENRATION_RATE == 0 and sprite.current_status["Regen"]:
                sprite.hp += 1

    def spawn(self, p: pokemon.Pokemon):
        possible_spawn = []
        for position in self.floor:
            if self.floor.is_room(position) and not self.is_occupied(position) and self.floor[position].can_spawn:
                possible_spawn.append(position)

        self.spawned.append(p)
        p.position = random.choice(possible_spawn)
        p.init_tracks()
        p.on_enter_new_floor()

    def spawn_party(self, party: party.Party):
        self.party = party
        for member in party:
            self.spawn(member)

    def spawn_enemies(self):
        self.active_enemies = []
        for _ in range(self.current_floor_data.initial_enemy_density):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)
            self.active_enemies.append(enemy)

    def user_is_dead(self) -> bool:
        return self.party.is_defeated()

    def tile_is_visible_from(self, observer: tuple[int, int], target: tuple[int, int]) -> bool:
        if abs(observer[0] - target[0]) <= 2:
            if abs(observer[1] - target[1]) <= 2:
                return True
        return self.floor.in_same_room(observer, target)
