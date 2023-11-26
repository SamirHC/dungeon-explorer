import random

import pygame
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common.direction import Direction
from app.common import settings
from app.dungeon.dungeon import Dungeon
from app.pokemon.pokemon import Pokemon
from app.pokemon.movement_type import MovementType
from app.model.moving_entity import MovingEntity


WALK_ANIMATION_TIME = 24  # Frames
SPRINT_ANIMATION_TIME = 4  # Frames

TILE_SIZE = 24


class MovementSystem:
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon
        self.motion_time_left = 0
        self.time_for_one_tile = WALK_ANIMATION_TIME

        self.to_move: list[Pokemon] = []
        self.moving_pokemon_entities: dict[Pokemon, MovingEntity] = {}
        for p in self.dungeon.floor.spawned:
            e = MovingEntity()
            e.x = TILE_SIZE * (p.x + 5)
            e.y = TILE_SIZE * (p.y + 5)
            self.moving_pokemon_entities[p] = e

    @property
    def moving(self) -> list[Pokemon]:
        return [p for p, e in self.moving_pokemon_entities.items() if e.is_moving]

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
            p.set_walk_animation()
            e = self.moving_pokemon_entities[p]
            src = pygame.Vector2(e.position)
            dest = src + pygame.Vector2(p.direction.value) * TILE_SIZE
            e.start(dest.x, dest.y, self.time_for_one_tile)
        self.to_move.clear()

    def update(self):
        for p in self.moving:
            e = self.moving_pokemon_entities[p]
            e.update()

    def can_move(self, p: Pokemon, d: Direction) -> bool:
        new_position = p.x + d.x, p.y + d.y
        traversable = self.can_walk_on(p, new_position)
        unoccupied = not self.dungeon.floor.is_occupied(new_position)
        not_corner = not self.dungeon.floor.cuts_corner(
            p.position, d) or p.movement_type is MovementType.PHASING
        return traversable and unoccupied and not_corner

    def can_walk_on(self, p: Pokemon, position: tuple[int, int]):
        if self.dungeon.floor.is_impassable(position):
            return False
        terrain = self.dungeon.floor.get_terrain(position)
        return p.movement_type.can_traverse(terrain)

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
        self.input_speed_up_game(input_stream)
        if self.input_skip_turn(input_stream): return
        if self.input_change_direction(input_stream): return
        if self.input_move(input_stream): return

    def input_speed_up_game(self, input_stream: InputStream) -> bool:
        if input_stream.keyboard.is_held(settings.get_key(Action.RUN)):
            self.time_for_one_tile = SPRINT_ANIMATION_TIME
            return True
        self.time_for_one_tile = WALK_ANIMATION_TIME
        return False
    
    def input_skip_turn(self, input_stream: InputStream) -> bool:
        if input_stream.keyboard.is_pressed(settings.get_key(Action.PASS)) or input_stream.keyboard.is_held(settings.get_key(Action.PASS)):
            self.user.has_turn = False
            return True
        return False

    def get_input_direction(self, input_stream: InputStream) -> Direction:
        kb = input_stream.keyboard
        dx = 0
        dy = 0
        if kb.is_pressed(settings.get_key(Action.UP)) or kb.is_held(settings.get_key(Action.UP)):
            dy -= 1
        if kb.is_pressed(settings.get_key(Action.LEFT)) or kb.is_held(settings.get_key(Action.LEFT)):
            dx -= 1
        if kb.is_pressed(settings.get_key(Action.DOWN)) or kb.is_held(settings.get_key(Action.DOWN)):
            dy += 1
        if kb.is_pressed(settings.get_key(Action.RIGHT)) or kb.is_held(settings.get_key(Action.RIGHT)):
            dx += 1
        if dx == dy == 0:
            return None
        return Direction((dx, dy))

    def input_change_direction(self, input_stream: InputStream) -> bool:
        if not input_stream.keyboard.is_held(settings.get_key(Action.HOLD)):
            return False
        d = self.get_input_direction(input_stream)
        if d is not None:
            self.user.direction = d
            return True
        return False
    
    def input_move(self, input_stream: InputStream) -> bool:
        d = self.get_input_direction(input_stream)
        if d is None:
            return False
        self.user.direction = d
        if self.can_move(self.user, d):
            self.add(self.user)
            self.user.has_turn = False
            return True
        elif self.can_swap(self.user, d):
            other_p = self.dungeon.floor[self.user.facing_position()].pokemon_ptr
            other_p.direction = d.flip()
            self.add_all([self.user, other_p])
            self.user.has_turn = False
            other_p.has_turn = False
            return True
        return False

    def ai_move(self, p: Pokemon):
        self.update_ai_target(p)
        if p.target == p.position:
            return
        p.face_target(p.target)
        if p.target == p.facing_position():
            if self.dungeon.floor.is_occupied(p.target):
                if p.direction.is_cardinal():
                    return
                elif not self.dungeon.floor.cuts_corner(p.position, p.direction):
                    return
        if self.can_move(p, p.direction):
            self.add(p)
            return
        cw = p.direction.clockwise()
        if self.can_move(p, cw):
            p.direction = cw
            self.add(p)
            return
        acw = p.direction.anticlockwise()
        if self.can_move(p, acw):
            p.direction = acw
            self.add(p)
            return

    def update_ai_target(self, p: Pokemon):
        # 1. Target pokemon
        if p in self.dungeon.party:
            target_pokemon = self.user
        elif p in self.dungeon.floor.active_enemies:
            target_pokemon = min(self.dungeon.party, key=lambda e: max(abs(e.x - p.x), abs(e.y - p.y)))
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
            if self.dungeon.floor.in_same_room(target, p.position):
                continue
            if target == p.tracks[0]:
                continue
            if not self.can_move(p, d):
                continue
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
            room_exits = [r for r in self.dungeon.floor.room_exits[room_number] if r != p.position]
            if room_exits:
                p.target = random.choice([r for r in room_exits if r != p.position])
                return
        # 6. Random
        possible_directions = []
        for d in list(Direction):
            if not self.can_move(p, d):
                continue
            possible_directions.append(d)
        if possible_directions:
            d = random.choice(possible_directions)
            p.target = p.x + d.x, p.y + d.y
            return
