from __future__ import annotations

import pygame
from app.common.direction import Direction
from app.common import utils
from app.gui import text
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon_status import PokemonStatus
from app.pokemon.generic_pokemon import GenericPokemon
from app.pokemon.pokemon_sprite import PokemonSprite
from app.pokemon.pokemon_statistics import PokemonStatistics
from app.move.moveset import Moveset
from app.model.moving_entity import MovingEntity
import app.db.database as db


TILE_SIZE = 24


class Pokemon:
    def __init__(
        self,
        data: GenericPokemon,
        stats: PokemonStatistics,
        moveset: Moveset,
        is_enemy=False,
    ):
        self.is_enemy = is_enemy
        self.data = data
        self.sprite = PokemonSprite(db.pokemonsprite_db[self.data.pokedex_number])
        self.stats = stats
        self.moveset = moveset
        self.name_color = text.CYAN
        self.status = PokemonStatus(self.stats.hp.value)
        self.direction = Direction.SOUTH
        self.has_turn = True
        self.has_started_turn = False
        self.moving_entity = MovingEntity()

    def spawn(self, position: tuple[int, int]):
        self.position = position
        self.target = self.position
        self.animation_id = AnimationId.IDLE
        self.has_turn = True
        self.init_tracks()

        self.moving_entity.x = TILE_SIZE * (self.x + 5)
        self.moving_entity.y = TILE_SIZE * (self.y + 5)

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
        self.sprite.set_direction(value)

    @property
    def animation_id(self) -> int:
        return self.sprite.animation_id

    @animation_id.setter
    def animation_id(self, value):
        self.sprite.set_animation_id(value)

    def init_tracks(self):
        self.tracks = [self.position] * 4

    def move(self, d: Direction = None):
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
        if target == self.position:
            return
        x1, y1 = self.position
        x2, y2 = target
        dx = utils.sign(x2 - x1)
        dy = utils.sign(y2 - y1)
        self.direction = Direction((dx, dy))
