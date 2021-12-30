import constants
import dungeon_map
import os
import random
import pokemon
import text
import textbox

class Dungeon:
    NUMBER_OF_ENEMIES = 6

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.floor_number = 1
        self.turns = 0
        self.dungeon_map = dungeon_map.DungeonMap(self.dungeon_id)
        self.foes = self.load_dungeon_specific_pokemon_data()
        self.all_sprites: set[pokemon.Pokemon] = set()
        self.spawn_enemies()

    def load_dungeon_specific_pokemon_data(self) -> list[pokemon.SpecificPokemon]:
        foes = []
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", self.dungeon_id, "PokemonData.txt")
        f = pokemon.Pokemon.load_pokemon_data_file(file)
        for line in f:
            foes.append(pokemon.Pokemon.parse_pokemon_data_file_line(line))
        return foes

    def get_random_pokemon(self) -> pokemon.Pokemon:
        return pokemon.Pokemon(random.choice(self.foes).poke_id, "Enemy", self)

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.dungeon_map = dungeon_map.DungeonMap(self.dungeon_id)

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.all_sprites])

    def next_turn(self):
        self.turns += 1
        for sprite in self.all_sprites:
            sprite.has_turn = True
            if self.turns % pokemon.Pokemon.REGENRATION_RATE == 0 and sprite.battle_info.status["Regen"]:
                sprite.battle_info.status["HP"] = min(1 + sprite.battle_info.status["HP"], sprite.battle_info.base["HP"])

    def spawn(self, p: pokemon.Pokemon):
        possible_spawn = []
        for room in self.dungeon_map.room_coords:
            for x, y in room:
                if (x, y) not in map(lambda s: s.grid_pos, self.all_sprites):
                    possible_spawn.append((x, y))
        p.grid_pos = random.choice(possible_spawn)
        p.blit_pos = (p.grid_pos[0] * constants.TILE_SIZE, p.grid_pos[1] * constants.TILE_SIZE)
        self.all_sprites.add(p)

    def spawn_enemies(self):
        for _ in range(Dungeon.NUMBER_OF_ENEMIES):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)

    def remove_dead(self):
        for p in self.all_sprites.copy():
            if p.battle_info.status["HP"] == 0:
                msg = p.battle_info.name + " fainted!"
                textbox.message_log.append(text.Text(msg))
                self.all_sprites.remove(p)

    def user_is_dead(self) -> bool:
        return "User" not in [sprite.poke_type for sprite in self.all_sprites]
