import animation
import constants
import direction
import damage_chart
import enum
import move
import os
import pygame
import pygame.constants
import pygame.draw
import pygame.image
import pygame.sprite
import pygame.transform
import random
import pokemonsprite
import tile
import xml.etree.ElementTree as ET


class BattleStats:
    def __init__(self):
        self.xp = 0
        self.level = 0
        self.hp = 0
        self.attack = 0
        self.defense = 0
        self.sp_attack = 0
        self.sp_defense = 0
        self.accuracy = 100
        self.evasion = 0


class MovementType(enum.Enum):
    NORMAL = 0
    # UNUSED = 1
    LEVITATING = 2
    PHASING = 3
    LAVA_WALKER = 4
    WATER_WALKER = 5


class PokemonType:
    def __init__(self, primary_type: damage_chart.Type, secondary_type: damage_chart.Type):
        self.primary_type = primary_type
        self.secondary_type = secondary_type

    @property
    def types(self) -> tuple(damage_chart.Type):
        return (self.primary_type, self.secondary_type)

    def is_type(self, type: damage_chart.Type) -> bool:
        return type in self.types

    def get_damage_multiplier(self, move_type: damage_chart.Type) -> float:
        primary_multiplier = damage_chart.TypeChart.get_multiplier(
            move_type, self.primary_type)
        secondary_multiplier = damage_chart.TypeChart.get_multiplier(
            move_type, self.secondary_type)
        return primary_multiplier * secondary_multiplier


class GenericPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.parse_file()

    def parse_file(self):
        file = os.path.join(os.getcwd(), "GameData",
                            "pokemon", f"{self.poke_id}.xml")
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.name = self.root.find("Strings").find("English").find("Name").text
        base_stats = self.root.find("GenderedEntity").find("BaseStats")
        self.base_stats = BattleStats()
        self.base_stats.hp = int(base_stats.find("HP").text)
        self.base_stats.attack = int(base_stats.find("Attack").text)
        self.base_stats.defense = int(base_stats.find("Defense").text)
        self.base_stats.sp_attack = int(base_stats.find("SpAttack").text)
        self.base_stats.sp_defense = int(base_stats.find("SpDefense").text)
        primary_type = damage_chart.Type(
            int(self.root.find("GenderedEntity").find("PrimaryType").text))
        secondary_type = damage_chart.Type(
            int(self.root.find("GenderedEntity").find("SecondaryType").text))
        self.type = PokemonType(primary_type, secondary_type)
        self.movement_type = MovementType(
            int(self.root.find("GenderedEntity").find("MovementType").text))

    def get_stats_growth(self, xp: int) -> BattleStats:
        stats_growth_node = self.root.find("StatsGrowth")
        stats_growth = BattleStats()
        for level in stats_growth_node.findall("Level"):
            if int(level.find("RequiredExp").text) <= xp:
                stats_growth.level += 1
                stats_growth.hp += int(level.find("HP").text)
                stats_growth.attack += int(level.find("Attack").text)
                stats_growth.sp_attack += int(level.find("SpAttack").text)
                stats_growth.defense += int(level.find("Defense").text)
                stats_growth.sp_defense += int(level.find("SpDefense").text)
        return stats_growth


class SpecificPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.stat_boosts = BattleStats()
        self.moveset = Moveset()


class Moveset:
    MAX_MOVES = 4
    REGULAR_ATTACK = move.Move("0000")

    def __init__(self, moveset=[]):
        self.moveset = moveset

    def knows_move(self, m: move.Move) -> bool:
        return m in self.moveset


class Pokemon:
    REGENRATION_RATE = 2
    AGGRO_RANGE = 5

    def __init__(self, poke_id: str, poke_type: str, dungeon):
        self.poke_id = poke_id
        self.poke_type = poke_type
        self.dungeon = dungeon
        self.sprite_sheets = pokemonsprite.PokemonSprite(self.poke_id)
        self.load_pokemon_object()
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.animation_name = "Walk"

    @property
    def current_image(self) -> pygame.Surface:
        return self.animation.get_current_frame()

    @property
    def animation(self) -> animation.Animation:
        return self.sprite_sheets.get_animation(self.animation_name, self.direction)

    def load_pokemon_object(self):
        if self.poke_type in ("User", "Team"):
            specific_pokemon_data = self.load_user_specific_pokemon_data()
        elif self.poke_type == "Enemy":
            for foe in self.dungeon.possible_enemies:
                if foe.poke_id == self.poke_id:
                    specific_pokemon_data = foe

        self.generic_data = GenericPokemon(self.poke_id)

        actual_stats = self.generic_data.get_stats_growth(
            specific_pokemon_data.stat_boosts.xp)
        actual_stats.hp += self.generic_data.base_stats.hp + \
            specific_pokemon_data.stat_boosts.hp
        actual_stats.attack += self.generic_data.base_stats.attack + \
            specific_pokemon_data.stat_boosts.attack
        actual_stats.defense += self.generic_data.base_stats.defense + \
            specific_pokemon_data.stat_boosts.defense
        actual_stats.sp_attack += self.generic_data.base_stats.sp_attack + \
            specific_pokemon_data.stat_boosts.sp_attack
        actual_stats.sp_defense += self.generic_data.base_stats.sp_defense + \
            specific_pokemon_data.stat_boosts.sp_defense
        self.actual_stats = actual_stats

        self.move_set = specific_pokemon_data.moveset

        self.status_dict = {
            "HP": actual_stats.hp,
            "ATK": 10,
            "DEF": 10,
            "SPATK": 10,
            "SPDEF": 10,
            "ACC": 100,
            "EVA": 0,
            "Regen": 1,
        }

    @property
    def name(self) -> str:
        return self.generic_data.name

    @property
    def type(self) -> PokemonType:
        return self.generic_data.type

    @property
    def movement_type(self) -> MovementType:
        return self.generic_data.movement_type

    @property
    def max_hp(self) -> int:
        return self.actual_stats.hp

    @property
    def attack(self) -> int:
        return self.actual_stats.attack

    @property
    def sp_attack(self) -> int:
        return self.actual_stats.sp_attack

    @property
    def defense(self) -> int:
        return self.actual_stats.defense

    @property
    def sp_defense(self) -> int:
        return self.actual_stats.sp_defense

    @property
    def level(self) -> int:
        return self.actual_stats.level

    @property
    def xp(self) -> int:
        return self.actual_stats.xp

    @property
    def hp(self) -> int:
        return self.status_dict["HP"]

    @hp.setter
    def hp(self, hp: int):
        if hp < 0:
            self.status_dict["HP"] = 0
        elif hp > self.max_hp:
            self.status_dict["HP"] = self.max_hp
        else:
            self.status_dict["HP"] = hp

    @property
    def attack_status(self) -> int:
        return self.status_dict["ATK"]

    @attack_status.setter
    def attack_status(self, attack_status):
        if attack_status < 0:
            self.status_dict["ATK"] = 0
        elif attack_status > 20:
            self.status_dict["ATK"] = 20
        else:
            self.status_dict["ATK"] = attack_status

    @property
    def defense_status(self) -> int:
        return self.status_dict["DEF"]

    @defense_status.setter
    def defense_status(self, defense_status):
        if defense_status < 0:
            self.status_dict["DEF"] = 0
        elif defense_status > 20:
            self.status_dict["DEF"] = 20
        else:
            self.status_dict["DEF"] = defense_status

    @property
    def sp_attack_status(self) -> int:
        return self.status_dict["SPATK"]

    @sp_attack_status.setter
    def sp_attack_status(self, sp_attack_status):
        if sp_attack_status < 0:
            self.status_dict["SPATK"] = 0
        elif sp_attack_status > 20:
            self.status_dict["SPATK"] = 20
        else:
            self.status_dict["SPATK"] = sp_attack_status

    @property
    def sp_defense_status(self) -> int:
        return self.status_dict["SPDEF"]

    @sp_defense_status.setter
    def sp_defense_status(self, sp_defense_status):
        if sp_defense_status < 0:
            self.status_dict["SPDEF"] = 0
        elif sp_defense_status > 20:
            self.status_dict["SPDEF"] = 20
        else:
            self.status_dict["SPDEF"] = sp_defense_status

    @property
    def accuracy_status(self) -> int:
        return self.status_dict["ACC"]

    @accuracy_status.setter
    def accuracy_status(self, accuracy_status):
        if accuracy_status < 0:
            self.status_dict["ACC"] = 0
        elif accuracy_status > 20:
            self.status_dict["ACC"] = 20
        else:
            self.status_dict["ACC"] = accuracy_status

    @property
    def evasion_status(self) -> int:
        return self.status_dict["EVA"]

    @evasion_status.setter
    def evasion_status(self, evasion_status):
        if evasion_status < 0:
            self.status_dict["EVA"] = 0
        elif evasion_status > 20:
            self.status_dict["EVA"] = 20
        else:
            self.status_dict["EVA"] = evasion_status

    def load_user_specific_pokemon_data(self):
        file = os.path.join(os.getcwd(), "UserData", "UserTeamData.txt")
        f = Pokemon.load_pokemon_data_file(file)
        for line in f:
            if self.poke_id == line[0]:
                return Pokemon.parse_pokemon_data_file_line(line)

    def load_pokemon_data_file(file):
        with open(file) as f:
            f = [line[:-1].split(",") for line in f.readlines()[1:]]
        return f

    def parse_pokemon_data_file_line(line):
        specific_data = SpecificPokemon(line[0])
        specific_data.stat_boosts.xp = int(line[1])
        specific_data.stat_boosts.hp = int(line[2])
        specific_data.stat_boosts.attack = int(line[3])
        specific_data.stat_boosts.defense = int(line[4])
        specific_data.stat_boosts.sp_attack = int(line[5])
        specific_data.stat_boosts.sp_defense = int(line[6])
        specific_data.moveset = Moveset([move.Move(m) for m in line[7:]])
        return specific_data

    def move_on_grid(self, target):
        possible_directions = self.possible_directions()
        self.move_in_direction_of_minimal_distance(target, possible_directions)

        x = self.grid_pos[0] + self.direction.value[0]
        y = self.grid_pos[1] + self.direction.value[1]
        if self.direction in possible_directions:
            self.grid_pos = (x, y)

    def possible_directions(self) -> list[direction.Direction]:
        return [d for d in direction.Direction if self.possible_direction(d)]

    def possible_direction(self, direction: direction.Direction) -> bool:
        new_x = self.grid_pos[0] + direction.value[0]
        new_y = self.grid_pos[1] + direction.value[1]
        new_tile = self.dungeon.dungeon_map.get_at(new_x, new_y)
        return self.is_traversable_tile(new_tile) and not self.dungeon.is_occupied((new_x, new_y)) and (not self.cuts_corner(direction) or self.is_traversable_tile(tile.Tile.WALL))

    def is_traversable_tile(self, tile: tile.Tile) -> bool:
        # TO DO: Differentiate between Lava, Water and Void Secondary tiles (given by Dungeon property)
        if tile == tile.WALL:
            return self.movement_type == MovementType.PHASING
        elif tile == tile.SECONDARY:
            return self.movement_type != MovementType.NORMAL
        return True

    def cuts_corner(self, direction: direction.Direction) -> bool:
        if not direction.is_diagonal():
            return False
        if direction == direction.NORTH_EAST:
            return tile.Tile.WALL in (self.tile_in_direction(direction.NORTH), self.tile_in_direction(direction.EAST))
        if direction == direction.NORTH_WEST:
            return tile.Tile.WALL in (self.tile_in_direction(direction.NORTH), self.tile_in_direction(direction.WEST))
        if direction == direction.SOUTH_EAST:
            return tile.Tile.WALL in (self.tile_in_direction(direction.SOUTH), self.tile_in_direction(direction.EAST))
        if direction == direction.SOUTH_WEST:
            return tile.Tile.WALL in (self.tile_in_direction(direction.SOUTH), self.tile_in_direction(direction.WEST))

    def tile_in_direction(self, direction: direction.Direction) -> tile.Tile:
        return self.dungeon.dungeon_map.get_at(self.grid_pos[0] + direction.value[0], self.grid_pos[1] + direction.value[1])

    def draw(self):
        surface = pygame.Surface(
            self.current_image.get_size(), pygame.constants.SRCALPHA)
        w, h = constants.TILE_SIZE * 2 / 3, constants.TILE_SIZE / 3
        shadow_boundary = pygame.Rect(0, 0, w, h)
        shadow_boundary.centerx = surface.get_rect().centerx
        shadow_boundary.y = surface.get_rect().centery

        if self.poke_type in ["User", "Team"]:
            pygame.draw.ellipse(surface, (255, 247, 0),
                                shadow_boundary)  # Yellow edge
            # Lightbrown fade
            pygame.draw.ellipse(surface, (222, 181, 0),
                                (shadow_boundary.inflate(-2, -2)))
            pygame.draw.ellipse(
                surface, (165, 107, 0), (shadow_boundary.inflate(-4, -4)))  # Brown ellipse
        else:
            pygame.draw.ellipse(surface, constants.BLACK,
                                shadow_boundary)  # BlackShadow

        surface.blit(self.current_image, (0, 0))
        return surface
    ##############

    def vector_to(self, point):
        return (point[0] - self.grid_pos[0], point[1] - self.grid_pos[1])

    def distance_to(self, point):
        vector = self.vector_to(point)
        return (vector[0] * vector[0] + vector[1] * vector[1]) ** (0.5)

    def check_aggro(self, target):
        same_room = False
        for room in self.dungeon.dungeon_map.room_coords:
            if self.grid_pos in room and target.grid_pos in room:
                same_room = True
                break
        return self.distance_to(target.grid_pos) <= Pokemon.AGGRO_RANGE or same_room

    def move_in_direction_of_minimal_distance(self, target, possible_directions: list[direction.Direction]):
        if not possible_directions:
            self.has_turn = False
            return
        if not target:
            return
        elif target.grid_pos == (self.grid_pos[0] + self.direction.value[0], self.grid_pos[1] + self.direction.value[1]):
            return  # Already facing target, no need to change direction
        if self.check_aggro(target):
            distance = self.distance_to(target.grid_pos)
            if distance < 2:
                for dir in direction.Direction:
                    if dir.value == self.vector_to(target.grid_pos):
                        self.direction = dir
                        return
            self.direction = sorted(possible_directions, key=(lambda d: (
                self.grid_pos[0] - target.grid_pos[0] + d.value[0])**2 + (self.grid_pos[1] - target.grid_pos[1] + d.value[1])**2))[0]
        else:  # Face a random, but valid direction if not aggro
            if len(possible_directions):
                self.direction = random.choice(possible_directions)

    ################
    # ANIMATIONS
    def motion_animation(self, motion_time_left, time_for_one_tile):
        if self.blit_pos != (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
            self.animation_name = "Walk"
            self.animation.play(motion_time_left, time_for_one_tile)

            x = (self.grid_pos[0] - (self.direction.value[0] *
                 motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            y = (self.grid_pos[1] - (self.direction.value[1] *
                 motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            self.blit_pos = (x, y)
            if self.blit_pos == (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
                self.animation.index = 0

    def set_attack_animation(self, m: move.Move):
        category = m.category
        if category == move.MoveCategory.PHYSICAL:
            self.animation_name = "Attack"
        elif category == move.MoveCategory.SPECIAL:
            self.animation_name = "Attack"
        elif category == move.MoveCategory.STATUS:
            self.animation_name = "Charge"
        else:
            self.animation_name = "Idle"
