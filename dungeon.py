import dungeon_map
import os
import random
import PokemonStructure

class Dungeon:

    def __init__(self, dungeon_id):
        self.dungeon_id = dungeon_id
        self.dungeon_map = dungeon_map.DungeonMap(dungeon_id)
        self.foes = self.load_dungeon_specific_pokemon_data()
        
    def load_dungeon_specific_pokemon_data(self):
        dungeon_dict = {}
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", self.dungeon_id, "PokemonData.txt")
        f = PokemonStructure.Pokemon.load_pokemon_data_file(file)
        for line in f:
            poke_id = line[0]
            dungeon_dict[poke_id] = PokemonStructure.Pokemon.parse_pokemon_data_file_line(line)
        return dungeon_dict

    def get_random_pokemon(self):
        return PokemonStructure.Pokemon(random.choice(list(self.foes.keys())), "Enemy", self)

    