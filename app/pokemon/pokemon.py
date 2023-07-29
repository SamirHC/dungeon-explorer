from __future__ import annotations
import dataclasses

import os
import random
import xml.etree.ElementTree as ET

import pygame
import pygame.draw
import pygame.sprite
from app.common import direction, text
from app.move import moveset
from app.pokemon import pokemondata, pokemonsprite, genericpokemon
from app.db import genericpokemon_db, pokemonsprite_db
from app.model.type import PokemonType

from app.common.constants import USERDATA_DIRECTORY


# Stores basic pokemon info
@dataclasses.dataclass
class PokemonModel:
    generic_data: genericpokemon.GenericPokemon
    stats: pokemondata.PokemonStatistics
    moveset: moveset.Moveset


class PokemonBuilder:
    def __init__(self, poke_id: int):
        self.generic_data = genericpokemon_db[poke_id]
        self.stats = pokemondata.PokemonStatistics()
        self.moveset = moveset.Moveset()

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

    def set_moves(self, move_ids: list[int]):
        for move_id in move_ids:
            self.moveset.learn(move_id)
        return self

    def set_moves_from_level(self):
        level_val = self.stats.level.value
        possible_move_ids = self.generic_data.get_level_up_move_ids(level_val)
        if len(possible_move_ids) > 4:
            selected_move_ids = random.sample(possible_move_ids, 4)
        else:
            selected_move_ids = possible_move_ids
        return self.set_moves(selected_move_ids)

    def build(self) -> PokemonModel:
        return PokemonModel(
            self.generic_data,
            self.stats,
            self.moveset
        )

    def build_level(self, level: int) -> PokemonModel:
        return (
            self.set_level(level)
            .set_stats_from_level()
            .set_moves_from_level()
            .build()
        )


class Pokemon:
    def __init__(self, model: PokemonModel):
        self.model = model
        self.poke_id = model.generic_data.poke_id
        self.generic_data = model.generic_data
        self.sprite = pokemonsprite.PokemonSprite(pokemonsprite_db[self.generic_data.pokedex_number])
        self.stats = model.stats
        self.moveset = model.moveset
        self.name_color = text.CYAN
        self.init_status()
        self.direction = direction.Direction.SOUTH

    def init_status(self):
        self.status = pokemondata.PokemonStatus()
        self.status.hp.value = self.status.hp.max_value = self.hp

    def idle_animation_id(self):
        return self.sprite.IDLE_ANIMATION_ID

    def walk_animation_id(self):
        return self.sprite.WALK_ANIMATION_ID

    def hurt_animation_id(self):
        return self.sprite.HURT_ANIMATION_ID

    def spawn(self, position: tuple[int, int]):
        self.position = position
        self.target = self.position
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
    def type(self) -> PokemonType:
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

    def init_tracks(self):
        self.tracks = [self.position] * 4

    def move(self, d: direction.Direction=None):
        if d is None:
            d = self.direction
        self.tracks.pop()
        self.tracks.insert(0, self.position)
        self.position = self.x + d.x, self.y + d.y

    def render(self) -> pygame.Surface:
        return self.sprite.render()

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
    def __init__(self, user_id: int):
        self.user_id = user_id
        root = self.get_root()
        poke_id = int(root.find("PokeID").text)
        model = (
            PokemonBuilder(poke_id)
            .set_level(int(root.find("Level").text))
            .set_xp(int(root.find("XP").text))
            .set_hp(int(root.find("HP").text))
            .set_attack(int(root.find("Attack").text))
            .set_defense(int(root.find("Defense").text))
            .set_sp_attack(int(root.find("SpAttack").text))
            .set_sp_defense(int(root.find("SpDefense").text))
            .set_moves([int(m.get("id")) for m in root.find("Moveset").findall("Move")])
            .build()
        )
        super().__init__(model)

    def get_root(self) -> ET.Element:
        file = os.path.join(USERDATA_DIRECTORY, "userteam.xml")
        team_data = ET.parse(file).getroot()
        for el in team_data.findall("Pokemon"):
            if int(el.get("id")) == self.user_id:
                return el


class EnemyPokemon(Pokemon):
    def __init__(self, poke_id: str, level: int):
        model = (
            PokemonBuilder(poke_id)
            .build_level(level)
        )
        super().__init__(model)
