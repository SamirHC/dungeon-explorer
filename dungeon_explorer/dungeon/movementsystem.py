import random

import pygame
from dungeon_explorer.common import constants, direction, inputstream
from dungeon_explorer.dungeon import dungeon, tile
from dungeon_explorer.pokemon import pokemon, pokemondata


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
        self.dungeon.floor[p.position].pokemon_ptr = None
        p.move()
        self.dungeon.floor[p.position].pokemon_ptr = p

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
        traversable = self.can_walk_on(p, new_position)
        unoccupied = not self.dungeon.is_occupied(new_position)
        not_corner = not self.dungeon.cuts_corner(
            p.position, p.direction) or p.movement_type is pokemondata.MovementType.PHASING
        return traversable and unoccupied and not_corner

    def can_walk_on(self, p: pokemon.Pokemon, position: tuple[int, int]):
        if self.dungeon.is_impassable(position):
            return False
        if self.dungeon.is_ground(position):
            return True
        if p.movement_type is pokemondata.MovementType.NORMAL:
            return False
        if p.movement_type is pokemondata.MovementType.PHASING:
            return True
        if self.dungeon.is_wall(position):
            return False
        if p.movement_type is pokemondata.MovementType.LEVITATING:
            return True
        if self.dungeon.is_water(position):
            return p.movement_type is pokemondata.MovementType.WATER_WALKER
        if self.dungeon.is_lava(position):
            return p.movement_type is pokemondata.MovementType.LAVA_WALKER
        return False

    def input(self, input_stream: inputstream.InputStream):
        self.input_speed_up_game(input_stream)
        if self.input_skip_turn(input_stream): return
        if self.input_change_direction(input_stream): return
        if self.input_move(input_stream): return

    def input_speed_up_game(self, input_stream: inputstream.InputStream) -> bool:
        if input_stream.keyboard.is_held(pygame.K_LCTRL):
            self.time_for_one_tile = constants.SPRINT_ANIMATION_TIME
            return True
        self.time_for_one_tile = constants.WALK_ANIMATION_TIME
        return False
    
    def input_skip_turn(self, input_stream: inputstream.InputStream) -> bool:
        if input_stream.keyboard.is_pressed(pygame.K_x) or input_stream.keyboard.is_held(pygame.K_x):
            self.user.has_turn = False
            return True
        return False

    def input_change_direction(self, input_stream: inputstream.InputStream) -> bool:
        if not input_stream.keyboard.is_held(pygame.K_LSHIFT):
            return False
        for key in self.direction_keys:
            if input_stream.keyboard.is_pressed(key) or input_stream.keyboard.is_held(key):
                self.user.direction = self.direction_keys[key]
                return True
        return False
    
    def input_move(self, input_stream: inputstream.InputStream) -> bool:
        for key in self.direction_keys:
            if not(input_stream.keyboard.is_pressed(key) or input_stream.keyboard.is_held(key)):
                continue
            self.user.direction = self.direction_keys[key]
            if self.can_move(self.user):
                self.add(self.user)
                self.user.has_turn = False
                return True
        return False

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
