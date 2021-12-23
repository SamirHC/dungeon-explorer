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

    def calculate_spread(self) -> p.Vector2:
        min_x, min_y = map(min, zip(*self.path_coords))
        max_x, max_y = map(max, zip(*self.path_coords))
        return p.Vector2(max_x - min_x, max_y - min_y)

    def calculate_centre_of_mass(self) -> p.Vector2:
        return p.Vector2(tuple(map(sum, zip(*self.path_coords)))) / len(self.path_coords)

    # Path cannot be naturally wider than 1 tile.
    def check_thick_paths(self) -> bool:
        for x, y in self.path_coords:
            if y < Map.ROWS - 1 and x < Map.COLS - 1:
                if self.floor[y + 1][x] == self.floor[y][x + 1] == self.floor[y + 1][x + 1] == "P":
                    return True
        return False

    def check_valid_paths(self) -> bool:
        centre_of_mass = self.calculate_centre_of_mass()
        spread = self.calculate_spread()

        valid_centre_of_mass = abs(centre_of_mass.x - Map.COLS / 2) < 0.2 * Map.COLS and abs(centre_of_mass.y - Map.ROWS / 2) < 0.2 * Map.COLS
        valid_x_range = Map.COLS * 0.6 < spread.x < COLS
        valid_y_range = ROWS * 0.6 < spread.y < ROWS

        return  valid_centre_of_mass and valid_x_range and valid_y_range and not self.check_thick_paths()

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
            
            if self.check_valid_paths():
                break

        self.path_coords = remove_duplicates(self.path_coords)

    def insert_path(self, start: tuple[int, int], end: tuple[int, int]):
        start_row, start_col = start
        end_row, end_col = end

        for i in range(min(start_row, end_row), max(start_row, end_row) + 1):
            for j in range(min(start_col, end_col), max(start_col, end_col) + 1):
                self.floor[i][j] = "P"
                self.path_coords.append((j, i))

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
                if self.floor[row][col] == " " and v.length() <= radius:
                    self.floor[row][col] = "F"  # Fill area with Water Tile
                    self.water_coords.append((col, row))


    def check_valid_room(self, position: tuple[int, int], dimensions: tuple[int, int]) -> bool:
        x, y = position
        w, h = dimensions
        if x + w >= COLS - 1 or y + h >= ROWS - 1:  # Should be within map boundaries
            return False

        area = [self.floor[y + i - 1][x - 1: x + w + 1] for i in
                range(h + 2)]  # Gets the tile info of the area where the room would be placed (including surroundings)
        area = sum(area, [])

        top_left_corner = [area[0]]
        top_right_corner = [area[w + 1]]
        bottom_left_corner = [area[-w - 2]]
        bottom_right_corner = [area[-1]]
        top_edge = area[1:w + 1]
        bottom_edge = area[-w - 1:-1][::-1]
        left_edge = [area[i] for i in range(1, (w + 2) * (h + 1)) if i % (w + 2) == 0][::-1]
        right_edge = [area[i] for i in range(w + 2, (w + 2) * (h + 1)) if i % (w + 2) == (w + 1)]

        border = top_left_corner + top_edge + top_right_corner + right_edge + bottom_right_corner + bottom_edge + bottom_left_corner + left_edge + top_left_corner
        del area[-w - 2]
        del area[-1]  # Removes corners
        del area[w + 1]
        del area[0]

        if "R" in area:
            return False
        for i in range(len(border) - 1):
            if border[i] == border[i + 1] == "P":
                return False

        return "P" in area


    def insert_rooms(self):
        self.room_coords = []
        for _ in range(random.randint(self.min_room, self.max_room)):
            while True:
                width, height = random.randint(self.min_dim, self.max_dim), random.randint(self.min_dim, self.max_dim)
                row, col = random.randint(2, Map.ROWS - 2 - height), random.randint(2, Map.COLS - 2 - width)
                if self.check_valid_room((col, row), (width, height)):
                    break
            self.insert_room((row, col), (width, height))

    def insert_room(self, position: tuple[int, int], dimensions: tuple[int, int]):
        row, col = position
        width, height = dimensions
        room = []
        for x in range(width):
            for y in range(height):
                self.floor[row + y][col + x] = "R"  # Fill area with Room Tile
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
            x, y = coord[0], coord[1]
            if self.floor[y + 1][x] != "P" and self.floor[y - 1][x] != "P" and self.floor[y][x - 1] != "P" and \
                    self.floor[y][x + 1] != "P":
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

                if tile in ["P", "R"]:  # Ground tiles are used for Paths and Rooms
                    tile = Tile.GROUND
                elif tile == " ":
                    tile = Tile.WALL
                elif tile == "F":
                    tile = Tile.SECONDARY
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

    def empty_floor(self):
        self.floor = [[" " for x in range(Map.COLS)] for x in range(Map.ROWS)]

    def build_map(self):
        self.insert_paths()
        self.insert_lakes()
        self.insert_rooms()
        self.find_specific_floor_tiles()
        self.draw_map()
        self.insert_misc()  # Inserts stairs and traps
        return self

    def display_map(self, position):
        display.blit(self.map_image, position)
