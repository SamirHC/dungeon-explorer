from ..common import constants, textbox
from . import floor, generatordata, minimap, tileset
import os
import random
from ..pokemon import pokemon
import pygame
import pygame.draw
import pygame.image
import xml.etree.ElementTree as ET


class Dungeon:
    def __init__(self, dungeon_id: str, party: list[pokemon.Pokemon]):
        # Dungeon-wide
        self.dungeon_id = dungeon_id
        self.active_team: list[pokemon.Pokemon] = party
        self.floor_list = self.load_floor_list()
        self.is_below = True
        # Floor specific
        self.floor_number = 0
        self.active_enemies = []
        self.next_floor()
        self.message_log = textbox.TextBox((30, 7), 3)

    def load_floor_list(self):
        file = os.path.join(os.getcwd(), "data", "gamedata", "dungeons", f"floor_list{self.dungeon_id}.xml")
        tree = ET.parse(file)
        return [generatordata.FloorGeneratorData(r) for r in tree.getroot().findall("Floor")]

    def has_next_floor(self) -> bool:
        return self.floor_number < len(self.floor_list)

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.monster_list = self.current_floor_data.monster_list()
        self.floor = self.floor_builder.build_floor()
        self.tileset = tileset.TileSet(self.current_floor_data.tileset)
        self.minimap = minimap.MiniMap(self.floor)
        self.draw()
        self.spawn_team(self.active_team)
        self.spawn_enemies()
    
    @property
    def current_floor_data(self) -> generatordata.FloorGeneratorData:
        return self.floor_list[self.floor_number - 1]

    @property
    def user(self) -> pokemon.Pokemon:
        return self.active_team[0]

    @property
    def all_sprites(self) -> list[pokemon.Pokemon]:
        return self.active_team + self.active_enemies

    @property
    def floor_builder(self) -> floor.FloorBuilder:
        return floor.FloorBuilder(self.current_floor_data)

    def get_random_pokemon(self) -> pokemon.Pokemon:
        element = random.choices(self.monster_list, [int(el.get("weight")) for el in self.monster_list])[0]
        return pokemon.EnemyPokemon(element.get("id"), int(element.get("level")))

    def user_at_stairs(self) -> bool:
        return self.active_team[0].grid_pos == self.floor.stairs_spawn

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return any(map(lambda s: s.grid_pos == position, self.all_sprites))

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

        p.grid_pos = random.choice(possible_spawn)
        p.blit_pos = (p.grid_pos[0] * constants.TILE_SIZE,
                      p.grid_pos[1] * constants.TILE_SIZE)
        p.init_tracks()
        p.on_enter_new_floor()

    def spawn_team(self, team: list[pokemon.Pokemon]):
        self.active_team = []
        for member in team:
            self.spawn(member)
            self.active_team.append(member)

    def spawn_enemies(self):
        self.active_enemies = []
        for _ in range(self.current_floor_data.initial_enemy_density):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)
            self.active_enemies.append(enemy)

    def user_is_dead(self) -> bool:
        return not self.active_team

    def draw(self) -> pygame.Surface:
        self.surface = pygame.Surface(
            (constants.TILE_SIZE * self.floor.WIDTH, constants.TILE_SIZE * self.floor.HEIGHT))
        for y in range(self.floor.HEIGHT):
            for x in range(self.floor.WIDTH):
                tile_surface = self.get_tile_surface(x, y)
                self.surface.blit(
                    tile_surface, (constants.TILE_SIZE * x, constants.TILE_SIZE * y))
        return self.surface

    def get_tile_surface(self, x: int, y: int) -> pygame.Surface:
        # Edge tiles are borders
        if y == 0 or y == self.floor.HEIGHT - 1 or x == 0 or x == self.floor.WIDTH - 1:
            tile_surface = self.tileset.get_border_tile()
        elif (x, y) == self.floor.stairs_spawn:
            tile_surface = tileset.STAIRS_DOWN_IMAGE
        elif self.floor.has_shop and self.floor[x, y].is_shop:
            tile_surface = tileset.SHOP_IMAGE
        #elif (x, y) in self.dungeon_map.trap_coords:
        #    tile_surface = tileset.WONDER_TILE_IMAGE
        else:
            p = self.floor.get_tile_mask((x, y))
            variant = random.choice([0,0,0,0,1,1,2,2])
            terrain = self.floor[x, y].terrain
            tile_surface = self.tileset.get_tile_surface(terrain, p, variant)
            if variant != 0 and not self.tileset.is_valid(tile_surface):
                tile_surface = self.tileset.get_tile_surface(terrain, p)
        return tile_surface

    def tile_is_visible_from(self, observer: tuple[int, int], target: tuple[int, int]) -> bool:
        if abs(observer[0] - target[0]) <= 2:
            if abs(observer[1] - target[1]) <= 2:
                return True
        return self.floor.in_same_room(observer, target)
