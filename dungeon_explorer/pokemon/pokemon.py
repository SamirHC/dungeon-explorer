from __future__ import annotations

import os
import random
import xml.etree.ElementTree as ET

import pygame
import pygame.draw
import pygame.sprite
from dungeon_explorer.common import constants, direction
from dungeon_explorer.dungeon import tile
from dungeon_explorer.pokemon import move, pokemondata, pokemonsprite


class Pokemon:
    REGENRATION_RATE = 2

    def __init__(self, poke_id: str):
        self.poke_id = poke_id
        self.generic_data = pokemondata.GenericPokemon(self.poke_id)
        self.sprite = pokemonsprite.PokemonSprite(str(self.generic_data.pokedex_number))
        self.init_status()

    def init_status(self):
        self.status = pokemondata.PokemonStatus(
            pokemondata.Statistic(self.actual_stats.level, 1, 100),
            pokemondata.Statistic(self.actual_stats.xp, 0, 10_000_000),
            pokemondata.Statistic(self.actual_stats.hp, 0, self.actual_stats.hp)
        )
        self.current_status = {
            "Regen": 1,
            "Moves_pp": [m.pp for m in self.move_set]
        }

    def spawn(self, position: tuple[int, int]):
        self.position = position
        self.target = self.position
        self.direction = direction.Direction.SOUTH
        self.animation_name = "Idle"
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
    def animation_name(self) -> str:
        return self.sprite.animation_name
    @animation_name.setter
    def animation_name(self, value):
        self.sprite.animation_name = value

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
    def hp(self) -> int:
        return self.status.hp.max_value

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
    def move_set(self) -> pokemondata.Moveset:
        return self.actual_stats.moveset

    @property
    def name_color(self) -> pygame.Color:
        return constants.CYAN

    def init_tracks(self):
        self.tracks = [self.position] * 4

    def move(self):
        self.tracks.pop()
        self.tracks.insert(0, self.position)
        self.position = self.facing_position()

    def is_traversable_tile(self, t: tile.Tile) -> bool:
        # TO DO: Differentiate between Lava, Water and Void Secondary tiles (given by Dungeon property)
        if t.is_impassable:
            return False
        return self.is_traversable_terrain(t.terrain)

    def is_traversable_terrain(self, t: tile.Terrain) -> bool:
        if t is tile.Terrain.WALL:
            return self.movement_type == pokemondata.MovementType.PHASING
        elif t is tile.Terrain.SECONDARY:
            return self.movement_type != pokemondata.MovementType.NORMAL
        return True

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
        self.actual_stats = self.get_stats()
        super().__init__(self.poke_id)

    def get_root(self) -> ET.Element:
        file = os.path.join("data", "userdata", "userteam.xml")
        team_data = ET.parse(file).getroot()
        for el in team_data.findall("Pokemon"):
            if el.get("id") == self.user_id:
                return el

    def get_stats(self) -> pokemondata.SpecificPokemon:
        p = self.get_root()
        self.poke_id = p.find("PokeID").text
        specific_data = pokemondata.SpecificPokemon(
            int(p.find("Level").text),
            int(p.find("XP").text),
            int(p.find("HP").text),
            int(p.find("Attack").text),
            int(p.find("Defense").text),
            int(p.find("SpAttack").text),
            int(p.find("SpDefense").text),
            pokemondata.Moveset([move.Move(m.find("ID").text) for m in p.find("Moveset").findall("Move")])
        )
        return specific_data

    @property
    def name_color(self) -> pygame.Color:
        return constants.BLUE if self.user_id == "0" else constants.YELLOW


class EnemyPokemon(Pokemon):
    def __init__(self, poke_id: str, level: int):
        self.poke_id = poke_id
        self._level = level
        self.generic_data = pokemondata.GenericPokemon(self.poke_id)
        self.sprite = pokemonsprite.PokemonSprite(str(self.generic_data.pokedex_number))
        self.actual_stats = self.get_stats()
        self.init_status()

    def get_stats(self):
        actual_stats = pokemondata.SpecificPokemon(
            self._level,
            self.generic_data.get_required_xp(self._level),
            self.generic_data.get_hp(self._level),
            self.generic_data.get_attack(self._level),
            self.generic_data.get_defense(self._level),
            self.generic_data.get_sp_attack(self._level),
            self.generic_data.get_sp_defense(self._level),
            self.get_random_moveset()
        )
        return actual_stats

    def get_random_moveset(self):
        possible_moves = self.generic_data.get_level_up_moves(self._level)
        if len(possible_moves) <= 4:
            return pokemondata.Moveset(possible_moves)
        return pokemondata.Moveset(random.sample(possible_moves, 4))
