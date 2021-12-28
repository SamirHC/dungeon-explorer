import dungeon_map
import os
import random
import pokemon

class Dungeon:

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.floor_number = 1
        self.turns = 0
        self.dungeon_map = dungeon_map.DungeonMap(self.dungeon_id)
        self.foes = self.load_dungeon_specific_pokemon_data()
        
    def load_dungeon_specific_pokemon_data(self):
        dungeon_dict = {}
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", self.dungeon_id, "PokemonData.txt")
        f = pokemon.Pokemon.load_pokemon_data_file(file)
        for line in f:
            poke_id = line[0]
            dungeon_dict[poke_id] = pokemon.Pokemon.parse_pokemon_data_file_line(line)
        return dungeon_dict

    def get_random_pokemon(self) -> pokemon.Pokemon:
        return pokemon.Pokemon(random.choice(list(self.foes.keys())), "Enemy", self)

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.dungeon_map = dungeon_map.DungeonMap(self.dungeon_id)

    def next_turn(self):
        self.turns += 1
