import constants
import dungeon_map
import os
import random
import pattern
import pokemon
import pygame
import pygame.draw
import text
import textbox
import tileset
import utils
import xml.etree.ElementTree as ET


class Dungeon:
    NUMBER_OF_ENEMIES = 6

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.floor_number = 1
        self.turns = 0
        self.tileset = tileset.TileSet(self.dungeon_id)
        self.dungeon_map = dungeon_map.OutdatedDungeonMap(self.dungeon_id)
        self.draw()
        self.possible_enemies = self.load_dungeon_specific_pokemon_data()
        self.active_enemies: list[pokemon.Pokemon] = []
        self.active_team: list[pokemon.Pokemon] = []
        self.spawn_enemies()

    @property
    def all_sprites(self) -> list[pokemon.Pokemon]:
        return self.active_team + self.active_enemies

    def load_floor_list(self):
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", f"{self.dungeon_id}.xml")
        tree = ET.parse(file)
        root = tree.getroot()
        self.floor_list = root.find("FloorList").findall("Floor")

    def load_dungeon_specific_pokemon_data(self) -> list[pokemon.SpecificPokemon]:
        foes = []
        file = os.path.join(os.getcwd(), "GameData", "Dungeons",
                            self.dungeon_id, "PokemonData.txt")
        f = pokemon.Pokemon.load_pokemon_data_file(file)
        for line in f:
            foes.append(pokemon.Pokemon.parse_pokemon_data_file_line(line))
        return foes

    def get_random_pokemon(self) -> pokemon.Pokemon:
        return pokemon.Pokemon(random.choice(self.possible_enemies).poke_id, "Enemy", self)

    def user_at_stairs(self) -> bool:
        return self.active_team[0].grid_pos == self.dungeon_map.stairs_coords

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return any(map(lambda s: s.grid_pos == position, self.all_sprites))

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.dungeon_map = dungeon_map.OutdatedDungeonMap(self.dungeon_id)
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
        p.blit_pos = (p.grid_pos[0] * constants.TILE_SIZE,
                      p.grid_pos[1] * constants.TILE_SIZE)

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
                msg = f"{p.name} fainted!"
                textbox.message_log.append(text.Text(msg))
                if p.poke_type == "Enemy":
                    self.active_enemies.remove(p)
                else:
                    self.active_team.remove(p)

    def user_is_dead(self) -> bool:
        return not self.active_team

    def draw(self) -> pygame.Surface:
        self.surface = pygame.Surface(
            (constants.TILE_SIZE * self.dungeon_map.WIDTH, constants.TILE_SIZE * self.dungeon_map.HEIGHT))
        for y in range(self.dungeon_map.HEIGHT):
            for x in range(self.dungeon_map.WIDTH):
                tile_surface = self.get_tile_surface(x, y)
                self.surface.blit(
                    tile_surface, (constants.TILE_SIZE * x, constants.TILE_SIZE * y))
        return self.surface

    def get_tile_surface(self, x: int, y: int) -> pygame.Surface:
        # Edge tiles are borders
        if y == 0 or y == self.dungeon_map.HEIGHT - 1 or x == 0 or x == self.dungeon_map.WIDTH - 1:
            tile_surface = self.tileset.get_border_tile()
        elif (x, y) == self.dungeon_map.stairs_coords:
            tile_surface = self.tileset.get_stair_tile()
        elif (x, y) in self.dungeon_map.trap_coords:
            tile_surface = self.tileset.get_trap_tile()
        else:
            t = self.dungeon_map.get_at(x, y)
            surrounding = self.dungeon_map.get_surrounding_tiles_at(x, y)
            p = pattern.Pattern(t, surrounding)
            tile_surface = self.tileset.get_tile_surface(t, p, 0)
        return tile_surface

    # Draws HP bar, User level, and floor number
    def draw_hud(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        # FloorNo
        utils.cool_font(f"{self.floor_number}F",
                        constants.RED, (0, 0), surface)
        # Level
        utils.cool_font(f"Lv{self.active_team[0].actual_stats.level}", constants.RED, (
            constants.DISPLAY_WIDTH * (0.1), 0), surface)
        # HP
        utils.cool_font(f"HP{self.active_team[0].hp}of{self.active_team[0].max_hp}",
                        constants.RED, (constants.DISPLAY_WIDTH * (0.2), 0), surface)
        # HP BAR
        BAR_HEIGHT = constants.DISPLAY_HEIGHT * 0.042
        BAR_POSITION = (constants.DISPLAY_WIDTH * (0.5), 0)
        WIDTH_SCALE = 1.5
        pygame.draw.rect(surface, constants.RED, (
            BAR_POSITION[0], BAR_POSITION[1], self.active_team[0].max_hp * WIDTH_SCALE, BAR_HEIGHT))
        if self.active_team[0].hp > 0:
            pygame.draw.rect(surface, constants.GREEN, (
                BAR_POSITION[0], BAR_POSITION[1], self.active_team[0].hp * WIDTH_SCALE, BAR_HEIGHT))
        pygame.draw.rect(surface, constants.BLACK, (
            BAR_POSITION[0], BAR_POSITION[1], self.active_team[0].max_hp * WIDTH_SCALE, 2))
        pygame.draw.rect(surface, constants.BLACK, (
            BAR_POSITION[0], BAR_POSITION[1] + BAR_HEIGHT - 2, self.active_team[0].max_hp * WIDTH_SCALE, 2))
        pygame.draw.rect(surface, constants.WHITE, (
            BAR_POSITION[0], BAR_POSITION[1], self.active_team[0].max_hp * WIDTH_SCALE, 1))
        pygame.draw.rect(surface, constants.WHITE, (
            BAR_POSITION[0], BAR_POSITION[1] + BAR_HEIGHT - 2, self.active_team[0].max_hp * WIDTH_SCALE, 1))
        return surface
