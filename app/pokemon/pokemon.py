from __future__ import annotations

import pygame
import pygame.draw
import pygame.sprite
from app.common.direction import Direction
from app.common import text
from app.pokemon.pokemon_status import PokemonStatus
from app.pokemon.generic_pokemon import GenericPokemon
from app.pokemon.pokemon_sprite import PokemonSprite
from app.pokemon.pokemon_statistics import PokemonStatistics
from app.pokemon.movement_type import MovementType
from app.move.moveset import Moveset
from app.model.type import PokemonType
from app.db import pokemonsprite_db


class Pokemon:
    def __init__(self, data: GenericPokemon, stats: PokemonStatistics, moveset: Moveset, is_enemy=False):
        self.is_enemy = is_enemy
        self.data = data
        self.sprite = PokemonSprite(pokemonsprite_db[self.data.pokedex_number])
        self.stats = stats
        self.moveset = moveset
        self.name_color = text.CYAN
        self.init_status()
        self.direction = Direction.SOUTH
        self.fainted = False
        self.has_turn = True

    def init_status(self):
        self.status = PokemonStatus()
        self.status.hp.value = self.status.hp.max_value = self.hp

    def set_idle_animation(self):
        self.animation_id = self.sprite.IDLE_ANIMATION_ID

    def set_walk_animation(self):
        self.animation_id = self.sprite.WALK_ANIMATION_ID

    def set_sleep_animation(self):
        self.animation_id = self.sprite.SLEEP_ANIMATION_ID

    def spawn(self, position: tuple[int, int]):
        self.position = position
        self.target = self.position
        self.set_idle_animation()
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
    def direction(self) -> Direction:
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
        return self.data.name

    @property
    def type(self) -> PokemonType:
        return self.data.type

    @property
    def movement_type(self) -> MovementType:
        return self.data.movement_type

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

    def move(self, d: Direction=None):
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
        self.direction = Direction((dx, dy))
