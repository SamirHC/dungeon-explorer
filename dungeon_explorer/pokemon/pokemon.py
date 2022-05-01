from __future__ import annotations
import dataclasses

import os
import random
import xml.etree.ElementTree as ET

import pygame
import pygame.draw
import pygame.sprite
from dungeon_explorer.common import constants, direction
from dungeon_explorer.move import move
from dungeon_explorer.pokemon import pokemondata, pokemonsprite


# Stores basic pokemon info
@dataclasses.dataclass
class PokemonModel:
    poke_id: str
    stats: pokemondata.PokemonStatistics
    moveset: pokemondata.Moveset


class PokemonBuilder:
    def __init__(self, poke_id: str):
        self.generic_data = pokemondata.GenericPokemon(poke_id)
        self.stats = pokemondata.PokemonStatistics()
        self.moveset = pokemondata.Moveset()

    def set_level(self, val: int):
        self.stats.level.set_value(val)
        return self

    def set_xp_from_level(self):
        level_val = self.stats.level.value
        xp_val = self.generic_data.get_required_xp(level_val)
        self.stats.xp.set_value(xp_val)
        return self

    def set_xp(self, val: int):
        self.stats.xp.set_value(val)
        return self

    def set_hp(self, val: int):
        self.stats.hp.set_value(val)
        return self

    def set_attack(self, val: int):
        self.stats.attack.set_value(val)
        return self

    def set_defense(self, val: int):
        self.stats.defense.set_value(val)
        return self

    def set_sp_attack(self, val: int):
        self.stats.sp_attack.set_value(val)
        return self

    def set_sp_defense(self, val: int):
        self.stats.sp_defense.set_value(val)
        return self

    def set_stats_from_level(self):
        self.set_xp_from_level()
        level_val = self.stats.level.value
        self.set_hp(self.generic_data.get_hp(level_val))
        self.set_attack(self.generic_data.get_attack(level_val))
        self.set_defense(self.generic_data.get_defense(level_val))
        self.set_sp_attack(self.generic_data.get_sp_attack(level_val))
        self.set_sp_defense(self.generic_data.get_sp_defense(level_val))
        return self

    def set_moves(self, moves: list[move.Move]):
        for m in moves:
            self.moveset.learn(m)
        return self

    def build(self):
        return PokemonModel(
            self.generic_data.poke_id,
            self.stats,
            self.moveset
        )


class Pokemon:
    def __init__(self, poke_id: str):
        self.poke_id = poke_id
        self.generic_data = pokemondata.GenericPokemon(self.poke_id)
        self.sprite = pokemonsprite.PokemonSprite(str(self.generic_data.pokedex_number))
        self.stats = self.get_stats()
        self.init_status()

    def get_stats(self):
        return pokemondata.PokemonStatistics()

    def get_moveset(self):
        return pokemondata.Moveset()

    def init_status(self):
        self.status = pokemondata.PokemonStatus()
        self.status.hp.value = self.status.hp.max_value = self.hp
        self.moveset = self.get_moveset()

    def idle_animation_id(self):
        return self.sprite.idle_animation_id()

    def walk_animation_id(self):
        return self.sprite.walk_animation_id()

    def hurt_animation_id(self):
        return self.sprite.hurt_animation_id()

    def spawn(self, position: tuple[int, int]):
        self.position = position
        self.target = self.position
        self.direction = direction.Direction.SOUTH
        self.animation_id = self.idle_animation_id()
        self.has_turn = True
        self.init_tracks()

    def update(self):
        self.sprite.update()

    @property
    def x(self) -> int:
        return self.position[0]

    @property
    def y(self) -> int:
        return self.position[1]

    @property
    def direction(self) -> direction.Direction:
        return self.sprite.direction
    @direction.setter
    def direction(self, value):
        self.sprite.direction = value

    @property
    def animation_id(self) -> int:
        return self.sprite.animation_id
    @animation_id.setter
    def animation_id(self, value):
        self.sprite.animation_id = value

    @property
    def name(self) -> str:
        return self.generic_data.name

    @property
    def type(self) -> pokemondata.PokemonType:
        return self.generic_data.type

    @property
    def movement_type(self) -> pokemondata.MovementType:
        return self.generic_data.movement_type

    # Statuses
    @property
    def hp_status(self) -> int:
        return self.status.hp.value

    @property
    def attack_status(self) -> int:
        return self.status.attack.value

    @property
    def defense_status(self) -> int:
        return self.status.defense.value

    @property
    def sp_attack_status(self) -> int:
        return self.status.sp_attack.value

    @property
    def sp_defense_status(self) -> int:
        return self.status.sp_defense.value

    @property
    def evasion_status(self) -> int:
        return self.status.evasion.value

    @property
    def accuracy_status(self) -> int:
        return self.status.accuracy.value

    # Stats
    @property
    def level(self) -> int:
        return self.stats.level.value

    @property
    def xp(self) -> int:
        return self.stats.xp.value

    @property
    def hp(self) -> int:
        return self.stats.hp.value

    @property
    def attack(self) -> int:
        return self.stats.attack.value

    @property
    def sp_attack(self) -> int:
        return self.stats.sp_attack.value

    @property
    def defense(self) -> int:
        return self.stats.defense.value

    @property
    def sp_defense(self) -> int:
        return self.stats.sp_defense.value

    @property
    def name_color(self) -> pygame.Color:
        return constants.CYAN

    def init_tracks(self):
        self.tracks = [self.position] * 4

    def move(self):
        self.tracks.pop()
        self.tracks.insert(0, self.position)
        self.position = self.facing_position()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(self.sprite.size, pygame.SRCALPHA)
        surface.blit(self.sprite.get_shadow(), (0, 0))
        surface.blit(self.sprite.render(), (0, 0))
        return surface

    def facing_position(self) -> tuple[int, int]:
        x, y = self.position
        dx, dy = self.direction.value
        return x + dx, y + dy

    def face_target(self, target: tuple[int, int]):
        if target == self.facing_position():
            return
        if target == self.position:
            return
        x1, y1 = self.position
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
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.poke_id = self.get_root().find("PokeID").text
        super().__init__(self.poke_id)

    def get_root(self) -> ET.Element:
        file = os.path.join("data", "userdata", "userteam.xml")
        team_data = ET.parse(file).getroot()
        for el in team_data.findall("Pokemon"):
            if el.get("id") == self.user_id:
                return el

    def get_stats(self) -> pokemondata.PokemonStatistics:
        p = self.get_root()
        stats = super().get_stats()
        stats.level.set_value(int(p.find("Level").text))
        stats.xp.set_value(int(p.find("XP").text))
        stats.hp.set_value(int(p.find("HP").text))
        stats.attack.set_value(int(p.find("Attack").text))
        stats.defense.set_value(int(p.find("Defense").text))
        stats.sp_attack.set_value(int(p.find("SpAttack").text))
        stats.sp_defense.set_value(int(p.find("SpDefense").text))
        return stats

    def get_moveset(self) -> pokemondata.Moveset:
        root = self.get_root()
        return pokemondata.Moveset([move.load_move(m.find("ID").text) for m in root.find("Moveset").findall("Move")])

    @property
    def name_color(self) -> pygame.Color:
        return constants.BLUE if self.user_id == "0" else constants.YELLOW


class EnemyPokemon(Pokemon):
    def __init__(self, poke_id: str, level: int):
        self._level = level
        super().__init__(poke_id)

    def get_stats(self):
        stats = super().get_stats()
        stats.level.set_value(self._level)
        stats.xp.set_value(self.generic_data.get_required_xp(self._level))
        stats.hp.set_value(self.generic_data.get_hp(self._level))
        stats.attack.set_value(self.generic_data.get_attack(self._level))
        stats.defense.set_value(self.generic_data.get_defense(self._level))
        stats.sp_attack.set_value(self.generic_data.get_sp_attack(self._level))
        stats.sp_defense.set_value(self.generic_data.get_sp_defense(self._level))
        return stats

    def get_moveset(self):
        possible_moves = self.generic_data.get_level_up_moves(self._level)
        if len(possible_moves) <= 4:
            return pokemondata.Moveset(possible_moves)
        return pokemondata.Moveset(random.sample(possible_moves, 4))
