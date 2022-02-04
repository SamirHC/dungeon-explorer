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
import tileset
import xml.etree.ElementTree as ET


class Dungeon:
    NUMBER_OF_ENEMIES = 6

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
        self.hud = HUD()

    def load_floor_list(self):
        file = os.path.join(os.getcwd(), "gamedata",
                            "dungeons", f"floor_list{self.dungeon_id}.xml")
        tree = ET.parse(file)
        root = tree.getroot()
        return root.findall("Floor")

    def has_next_floor(self) -> bool:
        return self.floor_number < len(self.floor_list)

    def next_floor(self):
        self.floor_number += 1
        self.turns = 0
        self.monster_list = self.get_monster_list()
        self.dungeon_map = self.floor_builder.build_floor()
        self.tileset = tileset.TileSet(self.get_tileset_id())
        self.minimap = dungeon_mini_map.MiniMap(self.dungeon_map)
        self.draw()
        self.spawn_team(self.active_team)
        self.spawn_enemies()

    def get_monster_list(self) -> list[ET.Element]:
        return self.floor_list[self.floor_number - 1].find("MonsterList").findall("Monster")
    
    def get_tileset_id(self) -> str:
        return self.floor_list[self.floor_number - 1].find("FloorLayout").get("tileset")

    @property
    def user(self) -> pokemon.Pokemon:
        return self.active_team[0]

    @property
    def all_sprites(self) -> list[pokemon.Pokemon]:
        return self.active_team + self.active_enemies

    @property
    def floor_builder(self) -> dungeon_map.FloorBuilder:
        return dungeon_map.FloorBuilder2(self.dungeon_id, self.floor_number)
        #return dungeon_map.OutdatedFloorBuilder(self.dungeon_id)

    def get_random_pokemon(self) -> pokemon.Pokemon:
        cumulative_weights = [0]
        for p in self.monster_list:
            w = int(p.get("weight"))
            cumulative_weights.append(w + cumulative_weights[-1])
        rnd = random.random() * cumulative_weights[-1]
        for i in range(len(cumulative_weights[:-1])):
            if cumulative_weights[i] <= rnd < cumulative_weights[i+1]:
                element = self.monster_list[i]
        return pokemon.EnemyPokemon(element.get("id"), int(element.get("level")))

    def user_at_stairs(self) -> bool:
        return self.active_team[0].grid_pos == self.dungeon_map.stairs_spawn

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
        for position in self.dungeon_map:
            if self.dungeon_map.is_room(position) and not self.is_occupied(position) and self.dungeon_map[position].can_spawn:
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
        for _ in range(Dungeon.NUMBER_OF_ENEMIES):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)
            self.active_enemies.append(enemy)

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
        elif (x, y) == self.dungeon_map.stairs_spawn:
            tile_surface = self.tileset.get_stair_tile()
        elif self.dungeon_map.has_shop and self.dungeon_map[x, y].is_shop:
            tile_surface = self.tileset.get_shop_tile()
        #elif (x, y) in self.dungeon_map.trap_coords:
        #    tile_surface = self.tileset.get_trap_tile()
        else:
            terrain = self.dungeon_map[x, y].terrain
            surrounding_terrain = self.dungeon_map.surrounding_terrain((x, y))
            p = pattern.Pattern(terrain, surrounding_terrain)
            tile_surface = self.tileset.get_tile_surface(terrain, p, 0)
        return tile_surface

    def tile_is_visible_from(self, observer: tuple[int, int], target: tuple[int, int]) -> bool:
        if abs(observer[0] - target[0]) <= 2:
            if abs(observer[1] - target[1]) <= 2:
                return True
        return self.dungeon_map.in_same_room(observer, target)


class HUD:
    HUD_COMPONENTS_FILE = os.path.join(
        os.getcwd(), "assets", "images", "misc", "hud_components.png")

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
