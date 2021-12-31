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
        self.possible_enemies = self.load_dungeon_specific_pokemon_data()
        self.active_enemies: list[pokemon.Pokemon] = []
        self.active_team: list[pokemon.Pokemon] = []
        self.spawn_enemies()

    @property
    def all_sprites(self) -> set[pokemon.Pokemon]:
        return set(self.active_team + self.active_enemies)

    def load_dungeon_specific_pokemon_data(self) -> list[pokemon.SpecificPokemon]:
        foes = []
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", self.dungeon_id, "PokemonData.txt")
        f = pokemon.Pokemon.load_pokemon_data_file(file)
        for line in f:
            foes.append(pokemon.Pokemon.parse_pokemon_data_file_line(line))
        return foes

    def get_random_pokemon(self) -> pokemon.Pokemon:
        return pokemon.Pokemon(random.choice(self.possible_enemies).poke_id, "Enemy", self)

    def user_at_stairs(self) -> bool:
        return self.active_team[0].grid_pos == self.dungeon_map.stairs_coords

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.dungeon_map = dungeon_map.DungeonMap(self.dungeon_id)
        self.draw()
        self.spawn_team(self.active_team)
        self.spawn_enemies()

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.all_sprites])

    def next_turn(self):
        self.turns += 1
        for sprite in self.all_sprites:
            sprite.has_turn = True
            if self.turns % pokemon.Pokemon.REGENRATION_RATE == 0 and sprite.status_dict["Regen"]:
                sprite.hp += 1

    def spawn(self, p: pokemon.Pokemon):
        possible_spawn = []
        for room in self.dungeon_map.room_coords:
            for x, y in room:
                if (x, y) not in map(lambda s: s.grid_pos, self.all_sprites):
                    possible_spawn.append((x, y))
        p.grid_pos = random.choice(possible_spawn)
        p.blit_pos = (p.grid_pos[0] * constants.TILE_SIZE, p.grid_pos[1] * constants.TILE_SIZE)

    def spawn_team(self, team: list[pokemon.Pokemon]):
        self.active_team = []
        for member in team:
            self.spawn(member)
            self.active_team.append(member)

    def spawn_enemies(self):
        self.active_enemies = []
        for _ in range(Dungeon.NUMBER_OF_ENEMIES):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)
            self.active_enemies.append(enemy)

    def remove_dead(self):
        for p in self.all_sprites:
            if p.hp == 0:
                msg = p.name + " fainted!"
                textbox.message_log.append(text.Text(msg))
                if p.poke_type == "Enemy":
                    self.active_enemies.remove(p)
                else:
                    self.active_team.remove(p)

    def user_is_dead(self) -> bool:
        return not self.active_team

    def draw(self) -> pygame.Surface:
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