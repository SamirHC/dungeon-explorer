import constants
import direction
import dungeon
import inputstream
import pokemon
import pygame
import tile


class MovementSystem:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon
        self.is_active = False
        self.motion_time_left = 0
        self.time_for_one_tile = constants.WALK_ANIMATION_TIME

        self.moving: list[pokemon.Pokemon] = []

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
            p.grid_pos, p.direction) or p.is_traversable_tile(tile.Tile.WALL)
        return traversable and unoccupied and not_corner

    def input(self, input_stream: inputstream.InputStream):
        # Sprint
        if input_stream.keyboard.is_held(pygame.K_LSHIFT):
            self.time_for_one_tile = constants.SPRINT_ANIMATION_TIME
        else:
            self.time_for_one_tile = constants.WALK_ANIMATION_TIME
        for key in self.direction_keys:
            if input_stream.keyboard.is_pressed(key) or input_stream.keyboard.is_held(key):
                self.dungeon.active_team[0].direction = self.direction_keys[key]
                self.dungeon.active_team[0].animation_name = "Walk"
                if self.can_move(self.dungeon.active_team[0]):
                    self.add(self.dungeon.active_team[0])
                    self.dungeon.active_team[0].move()
                    self.dungeon.active_team[0].has_turn = False
                break

    def ai_move(self, p: pokemon.Pokemon):
        if self.dungeon.tile_is_visible_from(p.grid_pos, self.dungeon.active_team[0].grid_pos):
            p.face_target(self.dungeon.active_team[0].grid_pos)
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
        if p.blit_pos != (p.grid_pos[0] * constants.TILE_SIZE, p.grid_pos[1] * constants.TILE_SIZE):
            p.animation_name = "Walk"
            p.animation.update()

            x = (p.grid_pos[0] - (p.direction.value[0] *
                 self.motion_time_left / self.time_for_one_tile)) * constants.TILE_SIZE
            y = (p.grid_pos[1] - (p.direction.value[1] *
                 self.motion_time_left / self.time_for_one_tile)) * constants.TILE_SIZE
            p.blit_pos = (x, y)