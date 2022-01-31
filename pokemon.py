from __future__ import annotations
import animation
import constants
import dataclasses
import direction
import damage_chart
import enum
import move
import os
import pygame
import pygame.constants
import pygame.draw
import pygame.sprite
import pokemonsprite
import pokemondata
import tile
import xml.etree.ElementTree as ET


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


@dataclasses.dataclass
class PokemonType:
    type1: damage_chart.Type
    type2: damage_chart.Type

    def is_type(self, type: damage_chart.Type) -> bool:
        return self.type1 == type or self.type2 == type

    def get_damage_multiplier(self, move_type: damage_chart.Type) -> float:
        m1 = damage_chart.TypeChart.get_multiplier(
            move_type, self.type1)
        m2 = damage_chart.TypeChart.get_multiplier(
            move_type, self.type2)
        return m1 * m2


class GenericPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id

        file = self.get_file()
        tree = ET.parse(file)
        root = tree.getroot()

        self._name = root.find("Strings").find("English").find("Name").text
        self._pokedex_number = int(root.find("GenderedEntity").find("PokedexNumber").text)

        self._type = PokemonType(
            damage_chart.Type(int(root.find("GenderedEntity").find("PrimaryType").text)),
            damage_chart.Type(int(root.find("GenderedEntity").find("SecondaryType").text))
        )
        self._movement_type = MovementType(int(root.find("GenderedEntity").find("MovementType").text))

        base_stats = root.find("GenderedEntity").find("BaseStats")
        self._base_hp = int(base_stats.find("HP").text)
        self._base_attack = int(base_stats.find("Attack").text)
        self._base_defense = int(base_stats.find("Defense").text)
        self._base_sp_attack = int(base_stats.find("SpAttack").text)
        self._base_sp_defense = int(base_stats.find("SpDefense").text)

        stats_growth = root.find("StatsGrowth").findall("Level")
        self._required_xp = []
        self._hp_growth = []
        self._attack_growth = []
        self._defense_growth = []
        self._sp_attack_growth = []
        self._sp_defense_growth = []
        for level in stats_growth:
            self._required_xp.append(int(level.find("RequiredExp").text))
            self._hp_growth.append(int(level.find("HP").text))
            self._attack_growth.append(int(level.find("Attack").text))
            self._defense_growth.append(int(level.find("Defense").text))
            self._sp_attack_growth.append(int(level.find("SpAttack").text))
            self._sp_defense_growth.append(int(level.find("SpDefense").text))

    def get_file(self):
        return os.path.join(os.getcwd(), "gamedata", "pokemon", f"{self.poke_id}.xml")

    @property
    def name(self) -> str:
        return self._name

    @property
    def pokedex_number(self) -> int:
        return self._pokedex_number

    @property
    def type(self) -> PokemonType:
        return self._type

    @property
    def movement_type(self) -> MovementType:
        return self._movement_type

    def get_required_xp(self, level: int):
        return self._required_xp[level]

    def get_hp(self, level: int):
        return self._base_hp + sum(self._hp_growth[:level])

    def get_attack(self, level: int):
        return self._base_attack + sum(self._attack_growth[:level])

    def get_defense(self, level: int):
        return self._base_defense + sum(self._defense_growth[:level])

    def get_sp_attack(self, level: int):
        return self._base_sp_attack + sum(self._sp_attack_growth[:level])

    def get_sp_defense(self, level: int):
        return self._base_sp_defense + sum(self._sp_defense_growth[:level])


class Moveset:
    MAX_MOVES = 4
    REGULAR_ATTACK = move.Move("0000")

    def __init__(self, moveset: list[move.Move] = []):
        self._moveset = [self.REGULAR_ATTACK] + moveset

    def __getitem__(self, i: int) -> move.Move:
        if i is None:
            return None
        return self._moveset[i]

    def __len__(self) -> int:
        return len(self._moveset)


@dataclasses.dataclass
class SpecificPokemon:
    level: int
    xp: int
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    moveset: Moveset


class Pokemon:
    poke_type = "None"
    REGENRATION_RATE = 2

    def __init__(self, poke_id: str):
        self.poke_id = poke_id
        self.generic_data = GenericPokemon(self.poke_id)
        self.sprite_sheets = pokemonsprite.SpriteCollection(str(self.generic_data.pokedex_number))
        self.init_status()

    def init_status(self):
        self.current_status = {
            "HP": self.actual_stats.hp,
            "ATK": 10,
            "DEF": 10,
            "SPATK": 10,
            "SPDEF": 10,
            "ACC": 100,
            "EVA": 0,
            "Regen": 1,
            "Moves_pp": [m.pp for m in self.move_set]
        }

    def on_enter_new_floor(self):
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.animation_name = "Idle"
        self.target = None
        self.animation.restart()

    @property
    def current_image(self) -> pygame.Surface:
        return self.animation.render()

    @property
    def animation(self) -> animation.Animation:
        return self.sprite_sheets.get_animation(self.animation_name, self.direction)

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
        return self.current_status["HP"]

    @hp.setter
    def hp(self, hp: int):
        if hp < 0:
            self.current_status["HP"] = 0
        elif hp > self.max_hp:
            self.current_status["HP"] = self.max_hp
        else:
            self.current_status["HP"] = hp

    @property
    def attack_status(self) -> int:
        return self.current_status["ATK"]

    @attack_status.setter
    def attack_status(self, attack_status):
        if attack_status < 0:
            self.current_status["ATK"] = 0
        elif attack_status > 20:
            self.current_status["ATK"] = 20
        else:
            self.current_status["ATK"] = attack_status

    @property
    def defense_status(self) -> int:
        return self.current_status["DEF"]

    @defense_status.setter
    def defense_status(self, defense_status):
        if defense_status < 0:
            self.current_status["DEF"] = 0
        elif defense_status > 20:
            self.current_status["DEF"] = 20
        else:
            self.current_status["DEF"] = defense_status

    @property
    def sp_attack_status(self) -> int:
        return self.current_status["SPATK"]

    @sp_attack_status.setter
    def sp_attack_status(self, sp_attack_status):
        if sp_attack_status < 0:
            self.current_status["SPATK"] = 0
        elif sp_attack_status > 20:
            self.current_status["SPATK"] = 20
        else:
            self.current_status["SPATK"] = sp_attack_status

    @property
    def sp_defense_status(self) -> int:
        return self.current_status["SPDEF"]

    @sp_defense_status.setter
    def sp_defense_status(self, sp_defense_status):
        if sp_defense_status < 0:
            self.current_status["SPDEF"] = 0
        elif sp_defense_status > 20:
            self.current_status["SPDEF"] = 20
        else:
            self.current_status["SPDEF"] = sp_defense_status

    @property
    def accuracy_status(self) -> int:
        return self.current_status["ACC"]

    @accuracy_status.setter
    def accuracy_status(self, accuracy_status):
        if accuracy_status < 0:
            self.current_status["ACC"] = 0
        elif accuracy_status > 20:
            self.current_status["ACC"] = 20
        else:
            self.current_status["ACC"] = accuracy_status

    @property
    def evasion_status(self) -> int:
        return self.current_status["EVA"]

    @evasion_status.setter
    def evasion_status(self, evasion_status):
        if evasion_status < 0:
            self.current_status["EVA"] = 0
        elif evasion_status > 20:
            self.current_status["EVA"] = 20
        else:
            self.current_status["EVA"] = evasion_status

    @property
    def move_set(self) -> Moveset:
        return self.actual_stats.moveset

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
        

class UserPokemon(Pokemon):
    poke_type = "User"
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.actual_stats = self.load_user_specific_pokemon_data()
        super().__init__(self.poke_id)

    def load_user_specific_pokemon_data(self) -> SpecificPokemon:
        file = os.path.join(os.getcwd(), "userdata", "userteam.xml")
        tree = ET.parse(file)
        root = tree.getroot()
        for p in root.findall("Pokemon"):
            if p.get("id") != self.user_id:
                continue
            self.poke_id = p.find("PokeID").text
            specific_data = SpecificPokemon(
                int(p.find("Level").text),
                int(p.find("XP").text),
                int(p.find("HP").text),
                int(p.find("Attack").text),
                int(p.find("Defense").text),
                int(p.find("SpAttack").text),
                int(p.find("SpDefense").text),
                Moveset([move.Move(m.find("ID").text) for m in p.find("Moveset").findall("Move")])
            )
            return specific_data


class EnemyPokemon(Pokemon):
    poke_type = "Enemy"

    def __init__(self, poke_id: str, level: int):
        self.poke_id = poke_id
        self._level = level
        self.generic_data = GenericPokemon(self.poke_id)
        self.actual_stats = self.get_stats()
        self.sprite_sheets = pokemonsprite.SpriteCollection(str(self.generic_data.pokedex_number))
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.animation_name = "Idle"
        self.init_status()

    def get_stats(self):
        actual_stats = SpecificPokemon(
            self._level,
            self.generic_data.get_required_xp(self._level),
            self.generic_data.get_hp(self._level),
            self.generic_data.get_attack(self._level),
            self.generic_data.get_defense(self._level),
            self.generic_data.get_sp_attack(self._level),
            self.generic_data.get_sp_defense(self._level),
            Moveset()
        )
        return actual_stats
