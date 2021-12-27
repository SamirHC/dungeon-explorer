from constants import *
from tile import Tile
from utils import *
import random
from pattern import Pattern
from tileset import TileSet
import os

class DungeonMap:
    DUNGEON_DATA_DIR = os.path.join(os.getcwd(), "GameData", "DungeonData.txt")
    ROWS = 40
    COLS = 65
    TRAPS_PER_FLOOR = 6
    DEFAULT_TILE = Tile.WALL
    TRAP_IMAGE = p.image.load(os.path.join(os.getcwd(), "images", "Traps", "WonderTile.png")).convert()
    STAIRS_IMAGE = p.image.load(os.path.join(os.getcwd(), "images", "Stairs", "StairsDown.png")).convert()


    def __init__(self, name: str):
        self.name = name
        self.load_generator_data()
        self.generate()

    def load_generator_data(self):
        with open(DungeonMap.DUNGEON_DATA_DIR) as f:
            f = f.readlines()
        f = [line[:-1].split(",") for line in f][1:]
        for dungeon in f:
            if dungeon[0] == self.name:
                self.max_path = int(dungeon[1])
                self.min_room = int(dungeon[2])
                self.max_room = int(dungeon[3])
                self.min_dim = int(dungeon[4])
                self.max_dim = int(dungeon[5])
                self.tile_set = TileSet(self.name)

    def generate(self):
        self.insert_paths()
        self.insert_lakes()
        self.insert_rooms()
        self.insert_misc()
        self.draw()

    def insert_paths(self):
        MIN_ROW, MAX_ROW = 2, DungeonMap.ROWS - 2
        MIN_COL, MAX_COL = 2, DungeonMap.COLS - 2
        while True:
            self.empty_floor()
            self.path_coords = []
            start_row = random.randrange(MIN_ROW, MAX_ROW)
            start_col = random.randrange(MIN_COL, MAX_COL)
            for _ in range(self.max_path):
                is_vertical = random.random() < 0.5
                if is_vertical:
                    end_row = random.randrange(MIN_ROW, MAX_ROW)
                    end_col = start_col
                else:
                    end_row = start_row
                    end_col = random.randrange(MIN_COL, MAX_COL)
                self.insert_path((start_row, start_col), (end_row, end_col))
                start_row, start_col = end_row, end_col
            if self.is_valid_paths():
                break
        self.path_coords = remove_duplicates(self.path_coords)

    def empty_floor(self):
        self.floor = dict()

    def insert_path(self, start: tuple[int, int], end: tuple[int, int]):
        start_row, start_col = start
        end_row, end_col = end
        for i in range(min(start_row, end_row), max(start_row, end_row) + 1):
            for j in range(min(start_col, end_col), max(start_col, end_col) + 1):
                self.set_at(i, j, Tile.GROUND)
                self.path_coords.append((j, i))

    def is_valid_paths(self) -> bool:
        return self.is_valid_centre_of_mass() and self.is_valid_spread() and self.is_valid_path_thickness()

    def is_valid_centre_of_mass(self) -> bool:
        centre_of_mass = p.Vector2(tuple(map(sum, zip(*self.path_coords)))) / len(self.path_coords)
        valid_x = abs(centre_of_mass.x - DungeonMap.COLS / 2) < 0.2 * DungeonMap.COLS
        valid_y = abs(centre_of_mass.y - DungeonMap.ROWS / 2) < 0.2 * DungeonMap.ROWS
        return valid_x and valid_y

    def is_valid_spread(self) -> bool:
        min_x, min_y = map(min, zip(*self.path_coords))
        max_x, max_y = map(max, zip(*self.path_coords))
        x_spread, y_spread = max_x - min_x, max_y - min_y
        valid_x_range = DungeonMap.COLS * 0.6 < x_spread < DungeonMap.COLS
        valid_y_range = DungeonMap.ROWS * 0.6 < y_spread < DungeonMap.ROWS
        return valid_x_range and valid_y_range

    # Path cannot be naturally wider than 1 tile.
    def is_valid_path_thickness(self) -> bool:
        for x, y in self.path_coords:
            if y < DungeonMap.ROWS - 1 and x < DungeonMap.COLS - 1:
                if self.get_at(y + 1, x) == self.get_at(y, x + 1) == self.get_at(y + 1, x + 1) == Tile.GROUND:
                    return False
        return True

    def insert_lakes(self):
        self.water_coords = []
        for _ in range(random.randint(self.min_room, self.max_room)):
            radius = random.randint(self.min_dim, self.max_dim) // 2
            centre_row = random.randint(2 + radius, DungeonMap.ROWS - 3 - radius)
            centre_col = random.randint(2 + radius, DungeonMap.COLS - 3 - radius)
            self.insert_lake((centre_row, centre_col), radius)
        self.water_coords = remove_duplicates(self.water_coords)

    def insert_lake(self, centre: tuple[int, int], radius: int):
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                row, col = centre[0] + i, centre[1] + j
                if self.get_at(row, col) == Tile.WALL and p.Vector2(i, j).length() <= radius:
                    self.set_at(row, col, Tile.SECONDARY)
                    self.water_coords.append((col, row))

    def insert_rooms(self):
        self.room_coords = []
        for _ in range(random.randint(self.min_room, self.max_room)):
            while True:
                width, height = random.randint(self.min_dim, self.max_dim), random.randint(self.min_dim, self.max_dim)
                row, col = random.randint(2, DungeonMap.ROWS - 2 - height), random.randint(2, DungeonMap.COLS - 2 - width)
                if self.is_valid_room((col, row), (width, height)):
                    break
            self.insert_room((row, col), (width, height))

    def is_valid_room(self, position: tuple[int, int], dimensions: tuple[int, int]) -> bool:
        x, y = position
        w, h = dimensions
        # Within map boundaries
        if x + w >= DungeonMap.COLS - 1 or y + h >= DungeonMap.ROWS - 1:  
            return False
        top_left_corner = (x - 1, y - 1)
        top_right_corner = (x + w, y - 1)
        bottom_left_corner = (x - 1, y + h)
        bottom_right_corner = (x + w, y + h)
        # Gets the area where the room would be placed (including surroundings)
        area = [(j, i) for i in range(y - 1, y + h + 1) for j in range(x - 1, x + w + 1) if (j, i) not in (top_left_corner, top_right_corner, bottom_left_corner, bottom_right_corner)]  
        top_edge = [(j, y - 1) for j in range(x, x + w)]
        right_edge = [(x + w, i) for i in range(y, y + h)]
        bottom_edge = [(j, y + h) for j in range(x + w - 1, x - 1, -1)]
        left_edge = [(x - 1, i) for i in range(y + h - 1, y - 1, -1)]
        border = [top_left_corner] + top_edge + [top_right_corner] + right_edge + [bottom_right_corner] + bottom_edge + [bottom_left_corner] + left_edge + [top_left_corner]
        # Check for room intersection
        for room in self.room_coords:
            for coord in area:
                if coord in room:
                    return False
        # Check for adjacent path_coords along the border
        for i in range(len(border) - 1):
            if border[i] in self.path_coords and border[i + 1] in self.path_coords:
                return False
        # Check for connectivity
        for i in range(len(area)):
            if area[i] in self.path_coords:
                return True
        return False

    def insert_room(self, position: tuple[int, int], dimensions: tuple[int, int]):
        row, col = position
        width, height = dimensions
        room = []
        for x in range(width):
            for y in range(height):
                self.set_at(row + y, col + x, Tile.GROUND)
                room.append((col + x, row + y))
        self.room_coords.append(room)

    def insert_misc(self):
        self.misc_coords = []
        self.insert_stairs()
        self.insert_traps()
    
    def insert_stairs(self):
        x, y = self.get_random_misc_coords()
        self.misc_coords.append((x, y))
        self.stairs_coords = (x, y)
    
    def insert_traps(self):
        self.trap_coords = []
        for _ in range(DungeonMap.TRAPS_PER_FLOOR):
            x, y = self.get_random_misc_coords()
            self.misc_coords.append((x, y))
            self.trap_coords.append((x, y))
        
    def get_random_misc_coords(self) -> tuple[int, int]:
        # Cannot be next to a path and must be in a room
        possible_coords = []
        for room in self.room_coords:
            for x, y in room:
                if (x, y) in self.misc_coords:
                    continue
                if (x, y + 1) not in self.path_coords and (x, y - 1) not in self.path_coords and (x - 1, y) not in self.path_coords and \
                        (x + 1, y) not in self.path_coords:
                    possible_coords.append((x, y))
        return random.choice(possible_coords)

    def get_tile_surface(self, row, col):
        # Edge tiles are borders
        if row == 0 or row == DungeonMap.ROWS - 1 or col == 0 or col == DungeonMap.COLS - 1:
            surface =  self.tile_set.get_tile(Tile.WALL, Pattern(), 0)
        elif (col, row) == self.stairs_coords:
            surface =  DungeonMap.STAIRS_IMAGE
        elif (col, row) in self.trap_coords:
            surface =  DungeonMap.TRAP_IMAGE
        else:
            pattern = Pattern()
            tile = self.get_at(row, col)
            offset = 0
            for i in range(-1, 2):
                for j in range(-1, 2):  # Iterate through every surrounding tile
                    if i == j == 0:
                        offset = -1
                        continue
                    pattern.pattern[(i + 1) * 3 + j + 1 + offset] = int(self.get_at(row + i, col + j) == tile)
            surface = self.tile_set.get_tile(tile, pattern, 0)
        return surface

    def draw(self):
        self.surface = p.Surface((TILE_SIZE * DungeonMap.COLS, TILE_SIZE * DungeonMap.ROWS))
        for i in range(DungeonMap.ROWS):
            for j in range(DungeonMap.COLS):
                image = self.get_tile_surface(i, j)
                self.surface.blit(scale(image, TILE_SIZE), (TILE_SIZE * j, TILE_SIZE * i))
        return self.surface

    def get_at(self, row: int, col: int) -> Tile:
        return self.floor.get((row, col), DungeonMap.DEFAULT_TILE)

    def set_at(self, row: int, col: int, tile: Tile):
        self.floor[row, col] = tile

