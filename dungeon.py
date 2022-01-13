import constants
import dungeon_map
import dungeon_mini_map
import os
import random
import pattern
import pokemon
import pygame
import pygame.constants
import pygame.draw
import pygame.image
import text
import textbox
import tileset
import xml.etree.ElementTree as ET


class Dungeon:
    NUMBER_OF_ENEMIES = 6

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self.is_below = True
        self.floor_number = 1
        self.turns = 0
        self.tileset = tileset.TileSet(self.dungeon_id)
        self.dungeon_map = dungeon_map.OutdatedDungeonMap(self.dungeon_id)
        self.minimap = dungeon_mini_map.MiniMap(self.dungeon_map)
        self.draw()
        self.possible_enemies = self.load_dungeon_specific_pokemon_data()
        self.active_enemies: list[pokemon.Pokemon] = []
        self.active_team: list[pokemon.Pokemon] = []
        self.spawn_enemies()
        self.hud = HUD()

    @property
    def all_sprites(self) -> list[pokemon.Pokemon]:
        return self.active_team + self.active_enemies

    def load_floor_list(self):
        file = os.path.join(os.getcwd(), "GameData",
                            "Dungeons", f"{self.dungeon_id}.xml")
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
        self.minimap = dungeon_mini_map.MiniMap(self.dungeon_map)
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
        for room in self.dungeon_map.rooms:
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
                name_item = (p.name, constants.BLUE if p.poke_type == "User" else constants.YELLOW)
                msg_item = (" fainted!", constants.WHITE)
                textbox.message_log.append(text.MultiColoredText([name_item, msg_item]))
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
            t = self.dungeon_map[x, y]
            surrounding = self.dungeon_map.get_surrounding_tiles_at(x, y)
            p = pattern.Pattern(t, surrounding)
            tile_surface = self.tileset.get_tile_surface(t, p, 0)
        return tile_surface


class HUD:
    HUD_COMPONENTS_FILE = os.path.join(
        os.getcwd(), "assets", "misc", "hud_components.png")

    def __init__(self):
        self.hud_components = pygame.image.load(HUD.HUD_COMPONENTS_FILE)
        self.hud_components.set_colorkey(self.hud_components.get_at((0, 0)))
        self.hud_components.set_palette_at(12, constants.ORANGE)  # Makes the labelling text (e.g. B, F, Lv, HP) orange

    def get_8_by_8_component(self, x: int, y: int) -> pygame.Surface:
        return self.hud_components.subsurface(x, y, 8, 8)

    def parse_number(self, n: int) -> pygame.Surface:
        variant = 0  # Colour of number can be either white(0) or green(1)
        s = str(n)
        surface = pygame.Surface((8*len(s), 8), pygame.constants.SRCALPHA)
        for i, c in enumerate(s):
            surface.blit(self.get_8_by_8_component(
                int(c)*8, variant*8), (i*8, 0))
        return surface

    def get_f_lv(self) -> pygame.Surface:
        return self.hud_components.subsurface(pygame.Rect(10*8, 0, 3*8, 8))

    def get_b(self) -> pygame.Surface:
        return self.get_8_by_8_component(13*8, 1*8)

    def get_hp(self) -> pygame.Surface:
        return self.hud_components.subsurface(pygame.Rect(10*8, 1*8, 2*8, 8))

    def get_slash(self) -> pygame.Surface:
        return self.hud_components.subsurface(pygame.Rect(12*8, 1*8, 8, 8))

    def draw(self, is_below: bool, floor_number: int, level: int, hp: int, max_hp: int) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        x = 0
        # Floor
        if is_below:
            surface.blit(self.get_b(), (x, 0))
            x += 8
        surface.blit(self.parse_number(floor_number), (x, 0))
        x += len(str(floor_number)) * 8
        surface.blit(self.get_f_lv(), (x, 0))
        x += 3 * 8
        # Level
        surface.blit(self.parse_number(level), (x, 0))
        x += 4 * 8
        # HP
        surface.blit(self.get_hp(), (x, 0))
        x += 2 * 8
        j = x
        surface.blit(self.parse_number(hp), (x, 0))
        x += len(str(hp)) * 8
        surface.blit(self.get_slash(), (x, 0))
        x += 8
        surface.blit(self.parse_number(max_hp), (x, 0))
        x = j + 7 * 8  # 3 digit hp, slash, 3 digit max hp
        # HP bar
        pygame.draw.rect(surface, constants.RED, (x, 0, max_hp, 8))
        if hp > 0:
            pygame.draw.rect(surface, constants.GREEN, (x, 0, hp, 8))
        pygame.draw.rect(surface, constants.BLACK, (x, 0, max_hp, 2))
        pygame.draw.rect(surface, constants.BLACK, (x, 6, max_hp, 2))
        pygame.draw.rect(surface, constants.WHITE, (x, 0, max_hp, 1))
        pygame.draw.rect(surface, constants.WHITE, (x, 6, max_hp, 1))
        return surface
