import constants
import direction
import dungeon
import inputstream
import pokemon
import pygame
import random
import tile


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

            for p in self.moving:
                self.motion_animation(p)
        else:
            self.clear()
            self.is_active = False

    def can_move(self, p: pokemon.Pokemon) -> bool:
        new_position = p.facing_position()
        traversable = p.is_traversable_tile(
            self.dungeon.dungeon_map[new_position])
        unoccupied = not self.dungeon.is_occupied(new_position)
        not_corner = not self.dungeon.dungeon_map.cuts_corner(
            p.grid_pos, p.direction) or p.is_traversable_terrain(tile.Terrain.WALL)
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
                self.user.animation_name = "Walk"
                if self.can_move(self.user):
                    self.add(self.user)
                    self.user.move()
                    self.user.has_turn = False
                break

    def ai_move(self, p: pokemon.Pokemon):
        if self.dungeon.tile_is_visible_from(p.grid_pos, self.user.grid_pos):
            p.target = self.user.grid_pos
        else:
            for track in self.user.tracks:
                if self.dungeon.tile_is_visible_from(p.grid_pos, track):
                    p.target = track
                    break
        if p.target is None:
            if self.dungeon.dungeon_map.is_room(p.grid_pos):
                room_number = self.dungeon.dungeon_map[p.grid_pos].room_index
                p.target = random.choice(self.dungeon.dungeon_map.room_exits[room_number])
            else:
                return
        
        p.face_target(p.target)
        if self.can_move(p):
            p.move()
            return
        original_direction = p.direction
        p.direction = original_direction.clockwise()
        if self.can_move(p):
            p.move()
            return
        p.direction = original_direction.anticlockwise()
        if self.can_move(p):
            p.move()
            return
        p.direction = original_direction  # Do nothing

    def motion_animation(self, p: pokemon.Pokemon):
        p.animation_name = "Walk"
        p.animation.update()

        x = (p.grid_pos[0] - (p.direction.x * self.movement_fraction)) * constants.TILE_SIZE
        y = (p.grid_pos[1] - (p.direction.y * self.movement_fraction)) * constants.TILE_SIZE
        p.blit_pos = (x, y)