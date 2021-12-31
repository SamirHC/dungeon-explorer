import constants
import dungeon_map
import os
import random
import pattern
import pokemon
import pygame
import text
import textbox
import tileset

class Dungeon:
    NUMBER_OF_ENEMIES = 6

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.floor_number = 1
        self.turns = 0
        self.tileset = tileset.TileSet(self.dungeon_id)
        self.dungeon_map = dungeon_map.DungeonMap(self.dungeon_id)
        self.draw()
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
            if self.turns % pokemon.Pokemon.REGENRATION_RATE == 0 and sprite.status_dict["Regen"]:
                sprite.status_dict["HP"] = min(1 + sprite.status_dict["HP"], sprite.actual_stats.hp)

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
            if p.status_dict["HP"] == 0:
                msg = p.name + " fainted!"
                textbox.message_log.append(text.Text(msg))
                self.all_sprites.remove(p)

    def user_is_dead(self) -> bool:
        return "User" not in [sprite.poke_type for sprite in self.all_sprites]

    def draw(self):
        self.surface = pygame.Surface((constants.TILE_SIZE * self.dungeon_map.COLS, constants.TILE_SIZE * self.dungeon_map.ROWS))
        for i in range(self.dungeon_map.ROWS):
            for j in range(self.dungeon_map.COLS):
                tile_surface = self.get_tile_surface(i, j)
                self.surface.blit(tile_surface, (constants.TILE_SIZE * j, constants.TILE_SIZE * i))
        return self.surface

    def get_tile_surface(self, row: int, col: int) -> pygame.Surface:
        # Edge tiles are borders
        if row == 0 or row == self.dungeon_map.ROWS - 1 or col == 0 or col == self.dungeon_map.COLS - 1:
            tile_surface =  self.tileset.get_border_tile()
        elif (col, row) == self.dungeon_map.stairs_coords:
            tile_surface =  self.tileset.get_stair_tile()
        elif (col, row) in self.dungeon_map.trap_coords:
            tile_surface =  self.tileset.get_trap_tile()
        else:
            t = self.dungeon_map.get_at(row, col)
            surrounding = self.dungeon_map.get_surrounding_tiles_at(row, col)
            p = pattern.Pattern(t, surrounding)
            tile_surface = self.tileset.get_tile_surface(t, p, 0)
        return tile_surface