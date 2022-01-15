import constants
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
                p.motion_animation(self.motion_time_left,
                                   self.time_for_one_tile)
        else:
            self.clear()
            self.is_active = False

    def can_move(self, p: pokemon.Pokemon) -> bool:
        new_position = p.facing_position()
        traversable = p.is_traversable_tile(self.dungeon.dungeon_map[new_position])
        unoccupied = not self.dungeon.is_occupied(new_position)
        not_corner = not self.cuts_corner(p) or p.is_traversable_tile(tile.Tile.WALL)
        return traversable and unoccupied and not_corner

    def cuts_corner(self, p: pokemon.Pokemon) -> bool:
        if not p.direction.is_diagonal():
            return False
        surrounding = self.dungeon.dungeon_map.get_surrounding_tiles_at(
            *p.grid_pos)
        if p.direction == p.direction.NORTH_EAST:
            return tile.Tile.WALL in {surrounding[1], surrounding[4]}
        if p.direction == p.direction.NORTH_WEST:
            return tile.Tile.WALL in {surrounding[1], surrounding[3]}
        if p.direction == p.direction.SOUTH_EAST:
            return tile.Tile.WALL in {surrounding[6], surrounding[4]}
        if p.direction == p.direction.SOUTH_WEST:
            return tile.Tile.WALL in {surrounding[6], surrounding[3]}

    def input(self, input_stream: inputstream.InputStream):
        # Sprint
        if input_stream.keyboard.is_held(pygame.K_LSHIFT):
            self.time_for_one_tile = constants.SPRINT_ANIMATION_TIME
        else:
            self.time_for_one_tile = constants.WALK_ANIMATION_TIME
        for key in constants.direction_keys:
            if input_stream.keyboard.is_pressed(key) or input_stream.keyboard.is_held(key):
                self.dungeon.active_team[0].direction = constants.direction_keys[key]
                self.dungeon.active_team[0].animation_name = "Walk"
                if self.can_move(self.dungeon.active_team[0]):
                    self.add(self.dungeon.active_team[0])
                    self.dungeon.active_team[0].move()
                    self.dungeon.active_team[0].has_turn = False
                break