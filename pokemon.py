from __future__ import annotations
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
import pygame.sprite
import random
import pokemonsprite
import tile
import xml.etree.ElementTree as ET


class BattleStats:
    xp = 0
    level = 0
    hp = 0
    attack = 0
    defense = 0
    sp_attack = 0
    sp_defense = 0
    accuracy = 100
    evasion = 0


class MovementType(enum.Enum):
    NORMAL = 0
    # UNUSED = 1
    LEVITATING = 2
    PHASING = 3
    LAVA_WALKER = 4
    WATER_WALKER = 5


class BehaviourType(enum.Enum):
    RANDOM = 0  # Wanders around aimlessly in random directions
    FOLLOW = 1  # Follows the leader pokemon
    SEEK = 2  # Seeks out enemies
    LEAD = 3  # Based on user input
    PETRIFIED = 4  # Avoids enemies


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
        file = os.path.join(os.getcwd(), "gamedata",
                            "pokemon", f"{self.poke_id}.xml")
        tree = ET.parse(file)
        self.root = tree.getroot()

    @property
    def name(self) -> str:
        return self.root.find("Strings").find("English").find("Name").text

    @property
    def pokedex_number(self) -> int:
        return int(self.root.find("GenderedEntity").find("PokedexNumber").text)

    @property
    def base_stats(self) -> BattleStats:
        node = self.root.find("GenderedEntity").find("BaseStats")
        base_stats = BattleStats()
        base_stats.hp = int(node.find("HP").text)
        base_stats.attack = int(node.find("Attack").text)
        base_stats.defense = int(node.find("Defense").text)
        base_stats.sp_attack = int(node.find("SpAttack").text)
        base_stats.sp_defense = int(node.find("SpDefense").text)
        return base_stats

    @property
    def type(self) -> PokemonType:
        primary_type = damage_chart.Type(
            int(self.root.find("GenderedEntity").find("PrimaryType").text))
        secondary_type = damage_chart.Type(
            int(self.root.find("GenderedEntity").find("SecondaryType").text))
        return PokemonType(primary_type, secondary_type)

    @property
    def movement_type(self) -> MovementType:
        return MovementType(
            int(self.root.find("GenderedEntity").find("MovementType").text))

    @property
    def level_up_moves(self) -> list[ET.Element]:
        move_elements = self.root.find("Moveset").find(
            "LevelUpMoves").findall("Learn")
        return move_elements

    @property
    def hm_tm_moves(self) -> list[ET.Element]:
        return self.root.find("Moveset").find("HmTmMoves").findall("MoveID")

    def get_stats_growth_by_xp(self, xp: int) -> BattleStats:
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

    def get_stats_growth_by_level(self, level: int) -> BattleStats:
        stats_growth_node = self.root.find("StatsGrowth")
        stats_growth = BattleStats()
        for node in stats_growth_node.findall("Level")[:level]:
            stats_growth.level += 1
            stats_growth.hp += int(node.find("HP").text)
            stats_growth.attack += int(node.find("Attack").text)
            stats_growth.sp_attack += int(node.find("SpAttack").text)
            stats_growth.defense += int(node.find("Defense").text)
            stats_growth.sp_defense += int(node.find("SpDefense").text)
        return stats_growth


class Moveset:
    MAX_MOVES = 4
    REGULAR_ATTACK = move.Move("0000")

    def __init__(self, moveset: list[move.Move] = []):
        self.moveset = [self.REGULAR_ATTACK] + moveset

    def __getitem__(self, i: int) -> move.Move:
        return self.moveset[i]

    def knows_move(self, m: move.Move) -> bool:
        return m in self.moveset


class SpecificPokemon:
    stat_boosts = BattleStats()
    moveset = Moveset()


class Pokemon:
    poke_type = "None"
    REGENRATION_RATE = 2

    def __init__(self, poke_id: str):
        self.poke_id = poke_id
        self.generic_data = GenericPokemon(self.poke_id)
        self.sprite_sheets = pokemonsprite.PokemonSprite(str(self.generic_data.pokedex_number))
        self.load_stats()

    def load_stats(self):
        self.status_dict = {}
        self.actual_stats = BattleStats()

    @property
    def current_image(self) -> pygame.Surface:
        return self.animation.render()

    @property
    def animation(self) -> animation.Animation:
        return self.sprite_sheets.get_animation(self.animation_name, self.direction)

    def on_enter_new_floor(self):
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.animation_name = "Walk"
        self.target = None
        self.animation.restart()

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

    def init_tracks(self):
        self.tracks = [self.grid_pos] * 4

    def move(self):
        self.tracks.pop()
        self.tracks.insert(0, self.grid_pos)
        self.grid_pos = self.facing_position()

    def is_traversable_tile(self, t: tile.Tile) -> bool:
        # TO DO: Differentiate between Lava, Water and Void Secondary tiles (given by Dungeon property)
        if t.is_impassable:
            return False
        return self.is_traversable_terrain(t.terrain)

    def is_traversable_terrain(self, t: tile.Terrain) -> bool:
        if t == tile.Terrain.WALL:
            return self.movement_type == MovementType.PHASING
        elif t == tile.Terrain.SECONDARY:
            return self.movement_type != MovementType.NORMAL
        return True

    def draw(self) -> pygame.Surface:
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

    def facing_position(self) -> tuple[int, int]:
        x, y = self.grid_pos
        dx, dy = self.direction.value
        return x + dx, y + dy

    def face_target(self, target: tuple[int, int]):
        if target == self.facing_position():
            return
        if target == self.grid_pos:
            return
        x1, y1 = self.grid_pos
        x2, y2 = target
        dx, dy = 0, 0
        if x1 < x2:
            dx = 1
        elif x1 > x2:
            dx = -1
        if y1 < y2:
            dy = 1
        elif y1 > y2:
            dy = -1
        self.direction = direction.Direction((dx, dy))

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


class UserPokemon(Pokemon):
    poke_type = "User"
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.specific_data = self.load_user_specific_pokemon_data()
        super().__init__(self.poke_id)

    def load_user_specific_pokemon_data(self) -> SpecificPokemon:
        file = os.path.join(os.getcwd(), "userdata", "userteam.xml")
        tree = ET.parse(file)
        root = tree.getroot()
        for p in root.findall("Pokemon"):
            if p.get("id") != self.user_id:
                continue
            self.poke_id = p.find("PokeID").text
            specific_data = SpecificPokemon()
            specific_data.stat_boosts.xp = int(p.find("XP").text)
            specific_data.stat_boosts.hp = int(p.find("HP").text)
            specific_data.stat_boosts.attack = int(p.find("Attack").text)
            specific_data.stat_boosts.defense = int(p.find("Defense").text)
            specific_data.stat_boosts.sp_attack = int(
                p.find("SpAttack").text)
            specific_data.stat_boosts.sp_defense = int(
                p.find("SpDefense").text)
            specific_data.moveset = Moveset(
                [move.Move(m.find("ID").text) for m in p.find("Moveset").findall("Move")])
            return specific_data

    def load_stats(self):
        actual_stats = self.generic_data.get_stats_growth_by_xp(
            self.specific_data.stat_boosts.xp)
        actual_stats.hp += self.generic_data.base_stats.hp + \
            self.specific_data.stat_boosts.hp
        actual_stats.attack += self.generic_data.base_stats.attack + \
            self.specific_data.stat_boosts.attack
        actual_stats.defense += self.generic_data.base_stats.defense + \
            self.specific_data.stat_boosts.defense
        actual_stats.sp_attack += self.generic_data.base_stats.sp_attack + \
            self.specific_data.stat_boosts.sp_attack
        actual_stats.sp_defense += self.generic_data.base_stats.sp_defense + \
            self.specific_data.stat_boosts.sp_defense
        self.actual_stats = actual_stats

        self.move_set = self.specific_data.moveset

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


class EnemyPokemon(Pokemon):
    poke_type = "Enemy"

    def __init__(self, poke_id: str, level: int):
        self._level = level
        self.poke_id = poke_id
        self.specific_data = SpecificPokemon()
        self.generic_data = GenericPokemon(self.poke_id)
        self.sprite_sheets = pokemonsprite.PokemonSprite(str(self.generic_data.pokedex_number))
        self.load_stats()
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.animation_name = "Walk"

    def load_stats(self):
        self.actual_stats = self.generic_data.get_stats_growth_by_level(self._level)
        self.actual_stats.hp += self.generic_data.base_stats.hp
        self.actual_stats.attack += self.generic_data.base_stats.attack
        self.actual_stats.defense += self.generic_data.base_stats.defense
        self.actual_stats.sp_attack += self.generic_data.base_stats.sp_attack
        self.actual_stats.sp_defense += self.generic_data.base_stats.sp_defense

        self.move_set = Moveset()

        self.status_dict = {
            "HP": self.actual_stats.hp,
            "ATK": 10,
            "DEF": 10,
            "SPATK": 10,
            "SPDEF": 10,
            "ACC": 100,
            "EVA": 0,
            "Regen": 1,
        }