from __future__ import annotations
import generatordata
import os
import pygame
import random
import direction
import tile


class AbstractDungeonMap:
    HEIGHT = 32
    WIDTH = 56
    DEFAULT_TILE = tile.Tile

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id
        self._floor = dict()
        self.hallways = set()
        self.rooms = list()
        self.load_generator_data()
        self.generate()

    def generate(self):
        pass

    def load_generator_data(self):
        pass

    def __getitem__(self, position: tuple[int, int]) -> tile.Tile:
        return self._floor.get(position, self.DEFAULT_TILE)

    def __setitem__(self, position: tuple[int, int], item: tile.Tile):
        self._floor[position] = item

    def get_surrounding_tiles_at(self, x: int, y: int) -> list[tile.Tile]:
        surrounding_tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                surrounding_tiles.append(self[x + j, y + i])
        return surrounding_tiles


class OutdatedDungeonMap(AbstractDungeonMap):
    DUNGEON_DATA_DIR = os.path.join(os.getcwd(), "gamedata", "DungeonData.txt")
    TRAPS_PER_FLOOR = 6

    def __init__(self, dungeon_id: str):
        super().__init__(dungeon_id)

    def generate(self):
        self._insert_paths()
        self._insert_lakes()
        self._insert_rooms()
        self._insert_misc()

    def load_generator_data(self):
        with open(self.DUNGEON_DATA_DIR) as f:
            f = f.readlines()
        f = [line[:-1].split(",") for line in f][1:]
        for dungeon in f:
            if dungeon[0] == self.dungeon_id:
                self.max_path = int(dungeon[1])
                self.min_room = int(dungeon[2])
                self.max_room = int(dungeon[3])
                self.min_dim = int(dungeon[4])
                self.max_dim = int(dungeon[5])

    def in_same_room(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        for room in self.rooms:
            if p1 not in room:
                continue
            return p2 in room
        return False

    def cuts_corner(self, p: tuple[int, int], d: direction.Direction) -> bool:
        if not d.is_diagonal():
            return False
        surrounding = [t.terrain for t in self.get_surrounding_tiles_at(*p)]
        if d == direction.Direction.NORTH_EAST:
            return tile.Terrain.WALL in {surrounding[1], surrounding[4]}
        if d == direction.Direction.NORTH_WEST:
            return tile.Terrain.WALL in {surrounding[1], surrounding[3]}
        if d == direction.Direction.SOUTH_EAST:
            return tile.Terrain.WALL in {surrounding[6], surrounding[4]}
        if d == direction.Direction.SOUTH_WEST:
            return tile.Terrain.WALL in {surrounding[6], surrounding[3]}

    def _insert_paths(self):
        MIN_HEIGHT, MAX_HEIGHT = 2, self.HEIGHT - 2
        MIN_WIDTH, MAX_WIDTH = 2, self.WIDTH - 2
        while True:
            self._empty_floor()
            self.hallways = set()
            start_y = random.randrange(MIN_HEIGHT, MAX_HEIGHT)
            start_x = random.randrange(MIN_WIDTH, MAX_WIDTH)
            for _ in range(self.max_path):
                is_vertical = random.random() < 0.5
                if is_vertical:
                    end_y = random.randrange(MIN_HEIGHT, MAX_HEIGHT)
                    end_x = start_x
                else:
                    end_y = start_y
                    end_x = random.randrange(MIN_WIDTH, MAX_WIDTH)
                self._insert_path((start_y, start_x), (end_y, end_x))
                start_y, start_x = end_y, end_x
            if self._is_valid_paths():
                break

    def _empty_floor(self):
        self._floor.clear()

    def _insert_path(self, start: tuple[int, int], end: tuple[int, int]):
        start_y, start_x = start
        end_y, end_x = end
        for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                self[x, y] = tile.Tile.hallway_tile()
                self.hallways.add((x, y))

    def _is_valid_paths(self) -> bool:
        return self._is_valid_centre_of_mass() and self._is_valid_spread() and self._is_valid_path_thickness()

    def _is_valid_centre_of_mass(self) -> bool:
        centre_of_mass = pygame.Vector2(
            tuple(map(sum, zip(*self.hallways)))) / len(self.hallways)
        valid_x = abs(centre_of_mass.x - self.WIDTH / 2) < 0.2 * self.WIDTH
        valid_y = abs(centre_of_mass.y - self.HEIGHT / 2) < 0.2 * self.HEIGHT
        return valid_x and valid_y

    def _is_valid_spread(self) -> bool:
        min_x, min_y = map(min, zip(*self.hallways))
        max_x, max_y = map(max, zip(*self.hallways))
        x_spread, y_spread = max_x - min_x, max_y - min_y
        valid_x_range = self.WIDTH * 0.6 < x_spread < self.WIDTH
        valid_y_range = self.HEIGHT * 0.6 < y_spread < self.HEIGHT
        return valid_x_range and valid_y_range

    # Path cannot be naturally wider than 1 tile.
    def _is_valid_path_thickness(self) -> bool:
        for x, y in self.hallways:
            if y < self.HEIGHT - 1 and x < self.WIDTH - 1:
                if self[x, y + 1].terrain == self[x + 1, y].terrain == self[x + 1, y + 1].terrain == tile.Terrain.GROUND:
                    return False
        return True

    def _insert_lakes(self):
        for _ in range(random.randint(self.min_room, self.max_room)):
            radius = random.randint(self.min_dim, self.max_dim) // 2
            centre_y = random.randint(
                2 + radius, self.HEIGHT - 3 - radius)
            centre_x = random.randint(
                2 + radius, self.WIDTH - 3 - radius)
            self._insert_lake((centre_y, centre_x), radius)

    def _insert_lake(self, centre: tuple[int, int], radius: int):
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                x, y = centre[0] + i, centre[1] + j
                if self[x, y].terrain == tile.Terrain.WALL and pygame.Vector2(i, j).length() <= radius:
                    self[x, y] = tile.Tile.secondary_tile()

    def _insert_rooms(self):
        self.rooms = []
        for _ in range(random.randint(self.min_room, self.max_room)):
            room_number = 0
            while True:
                width, height = random.randint(
                    self.min_dim, self.max_dim), random.randint(self.min_dim, self.max_dim)
                x = random.randint(2, self.WIDTH - 2 - width)
                y = random.randint(2, self.HEIGHT - 2 - height)
                if self._is_valid_room((x, y), (width, height)):
                    room_number += 1
                    break
            self._insert_room((x, y), (width, height), room_number)

    def _is_valid_room(self, position: tuple[int, int], dimensions: tuple[int, int]) -> bool:
        x, y = position
        w, h = dimensions
        # Within map boundaries
        if x + w >= self.WIDTH - 1 or y + h >= self.HEIGHT - 1:
            return False
        top_left_corner = (x - 1, y - 1)
        top_right_corner = (x + w, y - 1)
        bottom_left_corner = (x - 1, y + h)
        bottom_right_corner = (x + w, y + h)
        # Gets the area where the room would be placed (including surroundings)
        area = {(j, i) for i in range(y - 1, y + h + 1) for j in range(x - 1, x + w + 1) if (j, i)
                not in (top_left_corner, top_right_corner, bottom_left_corner, bottom_right_corner)}
        top_edge = [(j, y - 1) for j in range(x, x + w)]
        right_edge = [(x + w, i) for i in range(y, y + h)]
        bottom_edge = [(j, y + h) for j in range(x + w - 1, x - 1, -1)]
        left_edge = [(x - 1, i) for i in range(y + h - 1, y - 1, -1)]
        border = [top_left_corner] + top_edge + [top_right_corner] + right_edge + \
            [bottom_right_corner] + bottom_edge + \
            [bottom_left_corner] + left_edge + [top_left_corner]
        # Check for room intersection
        if set().union(*self.rooms) & area:
            return False
        # Check for adjacent path_coords along the border
        for i in range(len(border) - 1):
            if border[i] in self.hallways and border[i + 1] in self.hallways:
                return False
        # Check for connectivity
        return area & self.hallways

    def _insert_room(self, position: tuple[int, int], dimensions: tuple[int, int], room_number: int):
        col, row = position
        width, height = dimensions
        room = set()
        for x in range(width):
            for y in range(height):
                self[col + x, row + y] = tile.Tile.room_tile(room_number)
                room.add((col + x, row + y))
        self.rooms.append(room)

    def _insert_misc(self):
        self.misc_coords = set()
        self._insert_stairs()
        self._insert_traps()

    def _insert_stairs(self):
        x, y = self._get_random_misc_coords()
        self.misc_coords.add((x, y))
        self.stairs_coords = (x, y)
        self[x, y].stairs_index = 1

    def _insert_traps(self):
        self.trap_coords = set()
        for _ in range(self.TRAPS_PER_FLOOR):
            x, y = self._get_random_misc_coords()
            self[x, y].trap_index = 1
            self.misc_coords.add((x, y))
            self.trap_coords.add((x, y))

    def _get_random_misc_coords(self) -> tuple[int, int]:
        # Cannot be next to a path and must be in a room
        possible_coords = list(set().union(
            *self.rooms) - self.misc_coords)
        while True:
            x, y = random.choice(possible_coords)
            if not ((x, y + 1) in self.hallways or (x, y - 1) in self.hallways or (x - 1, y) in self.hallways or (x + 1, y) in self.hallways):
                return x, y


class Floor:
    WIDTH = 56
    HEIGHT = 32

    def __init__(self, dungeon_id: str, floor_number: int):
        self.data = generatordata.FloorGeneratorData(dungeon_id, floor_number)
        self._floor = {}

    def __getitem__(self, position: tuple[int, int]):
        return self._floor.get(position, tile.Tile())

    def __setitem(self, position: tuple[int, int], item: tile.Tile):
        self._floor[position] = item

    def get_surrounding_tiles(self, x: int, y: int) -> list[tile.Tile]:
        surrounding_tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                surrounding_tiles.append(self[x + j, y + i])
        return surrounding_tiles

    

    