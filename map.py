from pygame import Vector2
from constants import *
from tile import Tile
from utils import *
import random
from pattern import Pattern
from tileset import TileSet

class Map:
    DUNGEON_DATA_DIR = os.path.join(os.getcwd(), "GameData", "DungeonData.txt")
    COLS = COLS
    ROWS = ROWS

    def __init__(self, name: str):
        self.name = name
        self.load_dungeon_data()
        self.map_image = None
        self.stairs_coords = ["Down"]
        self.trap_coords = []
        self.specific_floor_tile_images = [["" for _ in range(Map.COLS)] for _ in range(Map.ROWS)]

    def load_dungeon_data(self):
        with open(Map.DUNGEON_DATA_DIR) as f:
            f = f.readlines()
        f = [line[:-1].split(",") for line in f][1:]
        for dungeon in f:
            if dungeon[0] == self.name:
                self.max_path = int(dungeon[1])  # Most number of distinct paths
                self.min_room = int(dungeon[2])  # Min number of rooms
                self.max_room = int(dungeon[3])  # Max ^
                self.min_dim = int(dungeon[4])  # Min dimensions of a room
                self.max_dim = int(dungeon[5])  # Max ^
                self.tile_set = TileSet(self.name)

    def generate(self):
        self.insert_paths()
        self.insert_lakes()
        self.insert_rooms()

    def insert_paths(self):
        MIN_ROW, MAX_ROW = 2, Map.ROWS - 2
        MIN_COL, MAX_COL = 2, Map.COLS - 2
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
        self.floor = [[Tile.WALL for _ in range(Map.COLS)] for _ in range(Map.ROWS)]

    def insert_path(self, start: tuple[int, int], end: tuple[int, int]):
        start_row, start_col = start
        end_row, end_col = end
        for i in range(min(start_row, end_row), max(start_row, end_row) + 1):
            for j in range(min(start_col, end_col), max(start_col, end_col) + 1):
                self.floor[i][j] = Tile.GROUND
                self.path_coords.append((j, i))

    def is_valid_paths(self) -> bool:
        return self.is_valid_centre_of_mass() and self.is_valid_spread() and self.is_valid_path_thickness()

    def is_valid_centre_of_mass(self) -> bool:
        centre_of_mass = p.Vector2(tuple(map(sum, zip(*self.path_coords)))) / len(self.path_coords)
        valid_x = abs(centre_of_mass.x - Map.COLS / 2) < 0.2 * Map.COLS
        valid_y = abs(centre_of_mass.y - Map.ROWS / 2) < 0.2 * Map.ROWS
        return valid_x and valid_y

    def is_valid_spread(self) -> bool:
        min_x, min_y = map(min, zip(*self.path_coords))
        max_x, max_y = map(max, zip(*self.path_coords))
        spread = p.Vector2(max_x - min_x, max_y - min_y)
        valid_x_range = Map.COLS * 0.6 < spread.x < Map.COLS
        valid_y_range = Map.ROWS * 0.6 < spread.y < Map.ROWS
        return valid_x_range and valid_y_range

    # Path cannot be naturally wider than 1 tile.
    def is_valid_path_thickness(self) -> bool:
        for x, y in self.path_coords:
            if y < Map.ROWS - 1 and x < Map.COLS - 1:
                if self.floor[y + 1][x] == self.floor[y][x + 1] == self.floor[y + 1][x + 1] == Tile.GROUND:
                    return False
        return True

    def insert_lakes(self):
        self.water_coords = []
        for _ in range(random.randint(self.min_room, self.max_room)):
            radius = random.randint(self.min_dim, self.max_dim) // 2
            centre_row = random.randint(2 + radius, Map.ROWS - 3 - radius)
            centre_col = random.randint(2 + radius, Map.COLS - 3 - radius)
            self.insert_lake(Vector2(centre_row, centre_col), radius)
        self.water_coords = remove_duplicates(self.water_coords)

    def insert_lake(self, centre: Vector2, radius: int):
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                v = Vector2(i, j)
                row, col = tuple(map(int, tuple(centre + v)))
                if self.floor[row][col] == Tile.WALL and v.length() <= radius:
                    self.floor[row][col] = Tile.SECONDARY  # Fill area with Water Tile
                    self.water_coords.append((col, row))

    def insert_rooms(self):
        self.room_coords = []
        for _ in range(random.randint(self.min_room, self.max_room)):
            while True:
                width, height = random.randint(self.min_dim, self.max_dim), random.randint(self.min_dim, self.max_dim)
                row, col = random.randint(2, Map.ROWS - 2 - height), random.randint(2, Map.COLS - 2 - width)
                if self.is_valid_room((col, row), (width, height)):
                    break
            self.insert_room((row, col), (width, height))

    def is_valid_room(self, position: tuple[int, int], dimensions: tuple[int, int]) -> bool:
        x, y = position
        w, h = dimensions
        if x + w >= COLS - 1 or y + h >= ROWS - 1:  # Should be within map boundaries
            return False
        top_left_corner = (x - 1, y - 1)
        top_right_corner = (x + w, y - 1)
        bottom_left_corner = (x - 1, y + h)
        bottom_right_corner = (x + w, y + h)
        # Gets the tile info of the area where the room would be placed (including surroundings)
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
                self.floor[row + y][col + x] = Tile.GROUND
                room.append((col + x, row + y))
        self.room_coords.append(room)

    def insert_misc(self):
        room_tiles = []
        type = self.stairs_coords[0]
        stairs_image = scale(
            p.image.load(os.path.join(os.getcwd(), "images", "Stairs", "Stairs" + type + ".png")).convert(), TILE_SIZE)
        trap_image = scale(p.image.load(os.path.join(os.getcwd(), "images", "Traps", "WonderTile.png")).convert(),
                        TILE_SIZE)

        for coord in sum(self.room_coords, []):
            x, y = coord
            if (x, y + 1) not in self.path_coords and (x, y - 1) not in self.path_coords and (x - 1, y) not in self.path_coords and \
                    (x + 1, y) not in self.path_coords:
                room_tiles.append([x, y])  # Cannot be next to a path and must be in a room
        i = random.randint(0, len(room_tiles) - 1)
        x, y = room_tiles[i][0], room_tiles[i][1]  # pick a random suitable room tile
        self.stairs_coords.append([x, y])  # Insert Stairs
        del room_tiles[i]

        self.map_image.blit(stairs_image, (x * TILE_SIZE, y * TILE_SIZE))
        for _ in range(TRAPS_PER_FLOOR):  # Insert Traps
            i = random.randint(0, len(room_tiles) - 1)
            x, y = room_tiles[i][0], room_tiles[i][1]
            self.trap_coords.append([x, y])
            self.map_image.blit(trap_image, (x * TILE_SIZE, y * TILE_SIZE))
            del room_tiles[i]

    def find_specific_floor_tiles(self):
        for y in range(1, len(self.floor) - 1):
            for x in range(1, len(self.floor[y]) - 1):  # Iterate through every non-border tile
                pattern = Pattern()  # Image File binary name
                tile = self.floor[y][x]  # Determine the type of tile
                offset = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):  # Iterate through every surrounding tile
                        if i == j == 0:
                            offset = -1
                            continue
                        pattern.pattern[(i + 1) * 3 + j + 1 + offset] = int(self.floor[y + i][x + j] == tile)
                self.specific_floor_tile_images[y][x] = (tile, pattern)

    def insert_borders(self):  # Surround map with empty/wall tile
        BORDER = (Tile.WALL, Pattern())
        for x in range(COLS):  # Top and Bottom borders
            self.specific_floor_tile_images[0][x] = self.specific_floor_tile_images[ROWS - 1][x] = BORDER
        for y in range(ROWS):  # Left and Right bornders
            self.specific_floor_tile_images[y][0] = self.specific_floor_tile_images[y][COLS - 1] = BORDER

    def draw_map(self):  # Blits tiles onto map.
        map_surface = p.Surface((TILE_SIZE * len(self.floor[0]), TILE_SIZE * len(self.floor)))
        self.insert_borders()
        for i in range(ROWS):
            for j in range(COLS):
                tile, pattern = self.specific_floor_tile_images[i][j]
                image = self.tile_set.get_tile(tile, pattern, 0)
                map_surface.blit(scale(image, TILE_SIZE), (TILE_SIZE * j, TILE_SIZE * i))

        self.map_image = map_surface

    def build_map(self):
        self.generate()
        self.find_specific_floor_tiles()
        self.draw_map()
        self.insert_misc()  # Inserts stairs and traps
        return self

    def display_map(self, position):
        display.blit(self.map_image, position)
