import random

import pygame
from dungeon_explorer.common import constants, direction, inputstream
from dungeon_explorer.dungeon import dungeon
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
        self.moving.append(p)
        self.dungeon.floor[p.position].pokemon_ptr = None
        p.move()
        self.dungeon.floor[p.position].pokemon_ptr = p

    def deactivate(self):
        self.moving.clear()
        self.is_active = False

    def start(self):
        self.motion_time_left = self.time_for_one_tile
        self.is_active = True

    def update(self):
        if not self.is_active:
            return
        for p in self.moving:
            p.animation_id = p.walk_animation_id()
        if self.motion_time_left > 0:
            self.motion_time_left -= 1
        else:
            self.deactivate()

    def can_move(self, p: pokemon.Pokemon, d: direction.Direction) -> bool:
        new_position = p.x + d.x, p.y + d.y
        traversable = self.can_walk_on(p, new_position)
        unoccupied = not self.dungeon.is_occupied(new_position)
        not_corner = not self.dungeon.cuts_corner(
            p.position, d) or p.movement_type is pokemondata.MovementType.PHASING
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
        for key, d in self.direction_keys.items():
            if not(input_stream.keyboard.is_pressed(key) or input_stream.keyboard.is_held(key)):
                continue
            self.user.direction = d
            if self.can_move(self.user, d):
                self.add(self.user)
                self.user.has_turn = False
                return True
        return False

    def ai_move(self, p: pokemon.Pokemon):
        self.update_ai_target(p)
        if p.target == p.position:
            return
        p.face_target(p.target)
        if self.dungeon.is_occupied(p.target) and p.target == p.facing_position():
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

    def tile_is_visible_from(self, observer: tuple[int, int], target: tuple[int, int]) -> bool:
        if abs(observer[0] - target[0]) <= 2:
            if abs(observer[1] - target[1]) <= 2:
                return True
        return self.dungeon.floor.in_same_room(observer, target)

    def update_ai_target(self, p: pokemon.Pokemon):
        # 1. Target user
        if self.tile_is_visible_from(p.position, self.user.position):
            p.target = self.user.position
            return
        # 2. Target user tracks
        for track in self.user.tracks:
            if self.tile_is_visible_from(p.position, track):
                p.target = track
                return
        # 3. Continue to room exit if not yet reached
        if p.position != p.target:
            if self.dungeon.floor.is_room(p.position):
                room_number = self.dungeon.floor[p.position].room_index
                if p.target in self.dungeon.floor.room_exits[room_number]:
                    return
        # 4. Target corridor
        possible_directions: list[direction.Direction] = []
        for d in direction.Direction:
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
            room_exits = self.dungeon.floor.room_exits[room_number]
            if len(room_exits) > 1:
                p.target = random.choice([r for r in room_exits if r != p.position])
            elif len(room_exits) == 1 and p.position == room_exits[0]:
                p.target = p.tracks[0]
            return
        # 6. Random
        possible_directions = []
        for d in list(direction.Direction):
            if not self.can_move(p, d):
                continue
            possible_directions.append(d)
        if possible_directions:
            d = random.choice(possible_directions)
            p.target = p.x + d.x, p.y + d.y
            return
