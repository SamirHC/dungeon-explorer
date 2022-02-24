from ..common import constants, direction, inputstream
from . import dungeon, tile
from ..pokemon import pokemon
import pygame
import random


class MovementSystem:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon
        self.is_active = False
        self.motion_time_left = 0
        self.time_for_one_tile = constants.WALK_ANIMATION_TIME

        self.moving: list[pokemon.Pokemon] = []

    @property
    def user(self):
        return self.dungeon.user

    @property
    def direction_keys(self) -> dict[int, direction.Direction]:
        return {
            pygame.K_q: direction.Direction.NORTH_WEST,
            pygame.K_w: direction.Direction.NORTH,
            pygame.K_e: direction.Direction.NORTH_EAST,
            pygame.K_a: direction.Direction.WEST,
            pygame.K_s: direction.Direction.SOUTH,
            pygame.K_d: direction.Direction.EAST,
            pygame.K_z: direction.Direction.SOUTH_WEST,
            pygame.K_c: direction.Direction.SOUTH_EAST
        }

    @property
    def movement_fraction(self):
        return self.motion_time_left / self.time_for_one_tile

    def add(self, p: pokemon.Pokemon):
        p.animation_name = "Walk"
        self.moving.append(p)
        p.move()

    def clear(self):
        self.moving.clear()

    def start(self):
        self.motion_time_left = self.time_for_one_tile

    def update(self):
        if not self.is_active:
            self.is_active = True
            self.start()

        if self.motion_time_left > 0:
            self.motion_time_left -= 1
        else:
            self.clear()
            self.is_active = False

    def can_move(self, p: pokemon.Pokemon) -> bool:
        new_position = p.facing_position()
        traversable = p.is_traversable_tile(
            self.dungeon.floor[new_position])
        unoccupied = not self.dungeon.is_occupied(new_position)
        not_corner = not self.dungeon.floor.cuts_corner(
            p.position, p.direction) or p.is_traversable_terrain(tile.Terrain.WALL)
        return traversable and unoccupied and not_corner

    def input(self, input_stream: inputstream.InputStream):
        # Sprint
        if input_stream.keyboard.is_held(pygame.K_LSHIFT):
            self.time_for_one_tile = constants.SPRINT_ANIMATION_TIME
        else:
            self.time_for_one_tile = constants.WALK_ANIMATION_TIME
        for key in self.direction_keys:
            if input_stream.keyboard.is_pressed(key) or input_stream.keyboard.is_held(key):
                self.user.direction = self.direction_keys[key]
                if self.can_move(self.user):
                    self.add(self.user)
                    self.user.has_turn = False
                break

    def ai_move(self, p: pokemon.Pokemon):
        self.update_ai_target(p)
        p.face_target(p.target)
        if self.can_move(p):
            self.add(p)
            return
        original_direction = p.direction
        p.direction = original_direction.clockwise()
        if self.can_move(p):
            self.add(p)
            return
        p.direction = original_direction.anticlockwise()
        if self.can_move(p):
            self.add(p)
            return
        p.direction = original_direction  # Do nothing

    def update_ai_target(self, p: pokemon.Pokemon):
        # 1. Target user
        if self.dungeon.tile_is_visible_from(p.position, self.user.position):
            p.target = self.user.position
            return
        # 2. Target user tracks
        for track in self.user.tracks:
            if self.dungeon.tile_is_visible_from(p.position, track):
                p.target = track
                return
        # 3. Continue to current target if not yet reached
        if p.position != p.target:
            return
        # 4. Target corridor that isn't in their tracks
        possible_targets = []
        for d in list(direction.Direction):
            p.direction = d
            target = p.facing_position()
            if self.dungeon.floor.in_same_room(target, p.position):
                continue
            if target in p.tracks:
                 continue
            if not self.can_move(p):
                continue
            possible_targets.append(target)
        if possible_targets:
            p.target = random.choice(possible_targets)
            return
        # 5. Target other room exit
        if self.dungeon.floor.is_room(p.position):
            room_number = self.dungeon.floor[p.position].room_index
            p.target = random.choice(self.dungeon.floor.room_exits[room_number])
            return
        # 6. Random
        possible_targets = []
        for d in list(direction.Direction):
            p.direction = d
            target = p.facing_position()
            if not self.can_move(p):
                continue
            possible_targets.append(target)
        if possible_targets:
            p.target = random.choice(possible_targets)
            return
