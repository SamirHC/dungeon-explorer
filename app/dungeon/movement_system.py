import pygame

from app.common.constants import RNG as random
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common.direction import Direction
from app.common import settings
from app.dungeon.dungeon import Dungeon
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.pokemon.movement_type import MovementType


# Duration of movement in frames.
WALK_TIME = 24
SPRINT_TIME = 4

TILE_SIZE = 24


class MovementSystem:
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon
        self.time_per_tile = WALK_TIME

        self.to_move: list[Pokemon] = []

    @property
    def moving(self) -> list[Pokemon]:
        return [p for p in self.dungeon.floor.spawned if p.moving_entity.is_moving]

    @property
    def user(self):
        return self.dungeon.user

    def add(self, p: Pokemon):
        self.to_move.append(p)
        self.dungeon.floor[p.position].pokemon_ptr = None
        p.move()
        self.dungeon.floor[p.position].pokemon_ptr = p

    def add_all(self, ps: list[Pokemon]):
        for p in ps:
            self.to_move.append(p)
            self.dungeon.floor[p.position].pokemon_ptr = None
        for p in ps:
            p.move()
        for p in ps:
            self.dungeon.floor[p.position].pokemon_ptr = p

    def start(self):
        for p in self.to_move:
            p.animation_id = AnimationId.WALK
            e = p.moving_entity
            src = pygame.Vector2(e.position)
            dest = src + pygame.Vector2(p.direction.value) * TILE_SIZE
            e.start(dest.x, dest.y, self.time_per_tile)
        self.to_move.clear()

    def update(self):
        for p in self.moving:
            p.moving_entity.update()

    def can_move(self, p: Pokemon, d: Direction) -> bool:
        new_position = p.x + d.x, p.y + d.y
        return (
            self.can_walk_on(p, new_position)
            and not self.dungeon.floor.is_occupied(new_position)
            and (
                not self.dungeon.floor.cuts_corner(p.position, d)
                or p.base.movement_type is MovementType.PHASING
            )
        )

    def can_walk_on(self, p: Pokemon, position: tuple[int, int]):
        if self.dungeon.floor.is_impassable(position):
            return False
        terrain = self.dungeon.floor.get_terrain(position)
        return p.base.movement_type.can_traverse(terrain)

    def can_swap(self, p: Pokemon, d: Direction) -> bool:
        new_pos = p.x + d.x, p.y + d.y
        other_p = self.dungeon.floor[new_pos].pokemon_ptr
        if other_p not in self.dungeon.party:
            return False
        self.dungeon.floor[p.position].pokemon_ptr = None
        self.dungeon.floor[new_pos].pokemon_ptr = None
        res = self.can_move(p, d) and self.can_move(other_p, d.flip())
        self.dungeon.floor[p.position].pokemon_ptr = p
        self.dungeon.floor[new_pos].pokemon_ptr = other_p
        return res

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        self.time_per_tile = (
            SPRINT_TIME if kb.is_held(settings.get_key(Action.RUN)) else WALK_TIME
        )

        # Check if nothing to do.
        self.user.has_turn = not kb.is_down(settings.get_key(Action.PASS))
        d = self.get_input_direction(input_stream)
        if not self.user.has_turn or d is None:
            return

        self.user.direction = d

        # Attempt to move.
        if kb.is_held(settings.get_key(Action.HOLD)):
            pass
        elif self.can_move(self.user, d):
            self.add(self.user)
            self.user.has_turn = False
        elif self.can_swap(self.user, d):
            other_p: Pokemon = self.dungeon.floor[
                self.user.facing_position()
            ].pokemon_ptr
            other_p.direction = d.flip()
            self.add_all([self.user, other_p])
            self.user.has_turn = False
            other_p.has_turn = False

    def get_input_direction(self, input_stream: InputStream) -> Direction:
        kb = input_stream.keyboard
        action_dirs = (
            (Action.UP, Direction.NORTH),
            (Action.LEFT, Direction.WEST),
            (Action.DOWN, Direction.SOUTH),
            (Action.RIGHT, Direction.EAST),
        )
        dx = sum(d.x for a, d in action_dirs if kb.is_down(settings.get_key(a)))
        dy = sum(d.y for a, d in action_dirs if kb.is_down(settings.get_key(a)))

        return Direction((dx, dy)) if dx or dy else None

    def ai_move(self, p: Pokemon):
        self.update_ai_target(p)

        if p.target == p.position:
            return

        p.face_target(p.target)
        d = p.direction

        if self.can_move(p, d):
            self.add(p)
        elif self.can_move(p, cw := d.clockwise()):
            p.direction = cw
            self.add(p)
        elif self.can_move(p, acw := p.direction.anticlockwise()):
            p.direction = acw
            self.add(p)

    def update_ai_target(self, p: Pokemon):
        # 1. Target pokemon
        if p in self.dungeon.party:
            target_pokemon = self.user
        elif p in self.dungeon.floor.active_enemies:
            target_pokemon = min(
                self.dungeon.party,
                key=lambda e: max(abs(e.x - p.x), abs(e.y - p.y)),
            )
        if self.dungeon.floor.can_see(p.position, target_pokemon.position):
            p.target = target_pokemon.position
            return
        # 2. Target tracks
        for track in target_pokemon.tracks:
            if self.dungeon.floor.can_see(p.position, track):
                p.target = track
                return
        # 3. Continue to room exit if not yet reached
        if p.position != p.target:
            if self.dungeon.floor.is_room(p.position):
                room_number = self.dungeon.floor[p.position].room_index
                if p.target in self.dungeon.floor.room_exits[room_number]:
                    return
        # 4. Target corridor
        possible_directions: list[Direction] = []
        for d in Direction:
            target = p.x + d.x, p.y + d.y
            if (
                not self.dungeon.floor.in_same_room(target, p.position)
                and target != p.tracks[0]
                and self.can_move(p, d)
            ):
                possible_directions.append(d)
        if possible_directions:
            d = random.choice(possible_directions)
            p.target = p.x + d.x, p.y + d.y
            return
        elif not self.dungeon.floor.is_room(p.position):
            p.target = p.tracks[0]
            return
        # 5. Target other room exit
        if self.dungeon.floor.is_room(p.position):
            room_number = self.dungeon.floor[p.position].room_index
            room_exits = [
                r for r in self.dungeon.floor.room_exits[room_number] if r != p.position
            ]
            if room_exits:
                p.target = random.choice([r for r in room_exits if r != p.position])
                return
        # 6. Random
        if possible_directions := [d for d in Direction if self.can_move(p, d)]:
            d = random.choice(possible_directions)
            p.target = p.x + d.x, p.y + d.y
