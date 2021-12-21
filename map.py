from importsAndConstants import *

# Different dungeons should have different tile graphics.
# Tile Loading Function.
def tile_list(tile):  # Matches Tile image for all possibilities of tile arrangements.
    tiles = [tile]  # Stores the parameter in case there are no X's.
    indices = []
    for i in range(1, len(tile)):  # Stores indices of the X's in the string.
        if tile[i] == "X":
            indices.append(i)
    if len(indices) != 0:
        for d in range(2 ** (len(indices))):  # gets all possibilities of X values by counting in binary.
            binary_string = format(d, "#0" + str(len(indices) + 2) + "b")[2:]
            new_tile = list(tile)  # Makes the string a list.
            for x_index in range(len(indices)):
                new_tile[indices[x_index]] = binary_string[x_index]  # Replaces the X's with 1s or 0s
            new_tile = "".join(new_tile)  # Converts list back to string
            tiles.append(new_tile)
        tiles = tiles[1:]  # Removes the string with the X's.
    return tiles



dungeons = [os.path.join(os.getcwd(), "images", "Dungeons", file) for file in
            os.listdir(os.path.join(os.getcwd(), "images", "Dungeons")) if file != "Thumbs.db"]
dungeon_dict = {}

for dungeon in dungeons:
    tile_type = [tile_type for tile_type in os.listdir(os.path.join(dungeon)) if tile_type != "Thumbs.db"]
    dungeon_dict[dungeon] = {}
    for i in range(len(tile_type)):
        tiles = [tile for tile in os.listdir(os.path.join(dungeon, tile_type[i])) if tile.endswith(".png")]
        tile_data = {}
        for tile in tiles:
            img = scale(p.image.load(os.path.join(dungeon, tile_type[i], tile)).convert(), TILE_SIZE)
            tile_data[tile] = tile_list(tile) + [img]
        dungeon_dict[dungeon][tile_type[i]] = tile_data

def load_dungeon_data():
    dungeon_data_dict = {}
    with open(os.path.join(os.getcwd(), "GameData", "DungeonData.txt")) as f:
        f = f.readlines()
    f = [line[:-1].split(",") for line in f][1:]
    for dungeon in f:
        temp_dict = {}
        name = dungeon[0]
        temp_dict["MaxPath"] = int(dungeon[1])
        temp_dict["MinRoom"] = int(dungeon[2])
        temp_dict["MaxRoom"] = int(dungeon[3])
        temp_dict["MinDim"] = int(dungeon[4])
        temp_dict["MaxDim"] = int(dungeon[5])
        dungeon_data_dict[name] = temp_dict
    return dungeon_data_dict

dungeon_data_dict = load_dungeon_data()

class Map:
    COLS = 65
    ROWS = 40

    def __init__(self, name):
        self.max_path = dungeon_data_dict[name]["MaxPath"]  # Most number of distinct paths
        self.min_room = dungeon_data_dict[name]["MinRoom"]  # Min number of rooms
        self.max_room = dungeon_data_dict[name]["MaxRoom"]  # Max ^
        self.min_dim = dungeon_data_dict[name]["MinDim"]  # Min dimensions of a room
        self.max_dim = dungeon_data_dict[name]["MaxDim"]  # Max ^
        self.tile_dict = dungeon_dict[os.path.join(os.getcwd(), "images", "Dungeons", name)]
        self.map_image = None
        self.path_coords = []  # Coordinates of all PathTiles
        self.room_coords = []  # ^ RoomTiles
        self.water_coords = []
        self.stairs_coords = ["Down"]
        self.trap_coords = []
        self.floor = [[" " for _ in range(COLS)] for _ in range(ROWS)]  # Map Tile data as a list
        self.specific_floor_tile_images = [["" for _ in range(COLS)] for _ in range(ROWS)]       

    #####################################################################################################################################################
    def calculate_spread(self):
        total_x = total_y = 0
        max_x = min_x = self.path_coords[0][0]
        max_y = min_y = self.path_coords[0][1]

        for coord in self.path_coords:
            x, y = coord[0], coord[1]
            if x > max_x:  # Used in range calc
                max_x = x
            if x < min_x:
                min_x = x
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y
            total_x += x  # Used in COM calc
            total_y += y  # "
            if y < Map.ROWS - 1 and x < Map.COLS - 1:
                if self.floor[y + 1][x] == self.floor[y][x + 1] == self.floor[y + 1][x + 1] == "P":
                    return (0, 0), 0, 0  # Path cannot be naturally wider than 1 tile.

        mass = len(self.path_coords)  # Total mass of system
        x_range = max_x - min_x
        y_range = max_y - min_y
        centre_of_mass = (total_x / mass, total_y / mass)
        return centre_of_mass, x_range, y_range

    def check_valid_paths(self):
        centre_of_mass, x_range, y_range = self.calculate_spread()

        valid_centre_of_mass = abs(centre_of_mass[0] - Map.COLS / 2) < 0.2 * Map.COLS and abs(centre_of_mass[1] - Map.ROWS / 2) < 0.2 * Map.COLS
        valid_x_range = Map.COLS * 0.6 < x_range < COLS
        valid_y_range = ROWS * 0.6 < y_range < ROWS

        return  valid_centre_of_mass and valid_x_range and valid_y_range

    def insert_paths(self):
        pos = (randint(2, COLS - 3), randint(2, ROWS - 3))  # Starting position of path generation
        for y in range(self.max_path):  # generate paths
            direction = randint(0, 3)  # 0 = Up, 1 = Down, 2 = Left, 3 = Right
            if direction == 0:  # Up
                a = randint(2, pos[1])
                for y in range(a, pos[1] + 1):
                    self.floor[y][pos[0]] = "P"
                    self.path_coords.append((pos[0], y))
                pos = (pos[0], a)
            elif direction == 1:  # Down
                a = randint(pos[1], ROWS - 3)
                for y in range(pos[1], a + 1):
                    self.floor[y][pos[0]] = "P"
                    self.path_coords.append((pos[0], y))
                pos = (pos[0], a)
            elif direction == 2:  # Left
                a = randint(2, pos[0])
                for x in range(a, pos[0] + 1):
                    self.floor[pos[1]][x] = "P"
                    self.path_coords.append((x, pos[1]))
                pos = (a, pos[1])
            elif direction == 3:  # Right
                a = randint(pos[0], COLS - 3)
                for x in range(pos[0], a + 1):
                    self.floor[pos[1]][x] = "P"
                    self.path_coords.append((x, pos[1]))
                pos = (a, pos[1])

        self.path_coords = remove_duplicates(self.path_coords)

    def insert_water(self):
        r = randint(self.min_dim, self.max_dim) // 2
        pos = (randint(2 + r, COLS - 2 - self.min_dim - r),
               randint(2 + r, ROWS - 2 - self.min_dim - r))  # topleft corner of room coordinate
        for x in range(-r, r + 1):
            for y in range(-r, r + 1):
                distance = (y ** 2 + x ** 2) ** 0.5
                if self.floor[pos[1] + y][pos[0] + x] == " " and distance <= r:
                    self.floor[pos[1] + y][pos[0] + x] = "F"  # Fill area with Water Tile
                    self.water_coords.append([pos[0] + x, pos[1] + y])

    def check_valid_room(self, position, dimensions):
        x, y = position[0], position[1]
        w, h = dimensions[0], dimensions[1]
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

        valid = False
        if "P" in area:
            valid = True

        return valid

    def insert_rooms(self):
        while True:
            position = (randint(2, COLS - 2 - self.min_dim),
                   randint(2, ROWS - 2 - self.min_dim))  # topleft corner of room coordinate
            dimensions = (randint(self.min_dim, self.max_dim), randint(self.min_dim, self.max_dim))
            if self.check_valid_room(position, dimensions):
                break
        room = []
        for x in range(dimensions[0]):
            for y in range(dimensions[1]):
                self.floor[position[1] + y][position[0] + x] = "R"  # Fill area with Room Tile
                room.append([position[0] + x, position[1] + y])
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
        i = randint(0, len(room_tiles) - 1)
        x, y = room_tiles[i][0], room_tiles[i][1]  # pick a random suitable room tile
        self.stairs_coords.append([x, y])  # Insert Stairs
        del room_tiles[i]

        self.map_image.blit(stairs_image, (x * TILE_SIZE, y * TILE_SIZE))
        for _ in range(TRAPS_PER_FLOOR):  # Insert Traps
            i = randint(0, len(room_tiles) - 1)
            x, y = room_tiles[i][0], room_tiles[i][1]
            self.trap_coords.append([x, y])
            self.map_image.blit(trap_image, (x * TILE_SIZE, y * TILE_SIZE))
            del room_tiles[i]

    def find_specific_floor_tiles(self):
        for y in range(1, len(self.floor) - 1):
            for x in range(1, len(self.floor[y]) - 1):  # Iterate through every non-border tile
                legend = ""  # Image File binary name
                tile = self.floor[y][x]  # Determine the type of tile
                for j in range(-1, 2):
                    for i in range(-1, 2):  # Iterate through every surrounding tile
                        if self.floor[y + j][x + i] == tile:
                            legend = legend + "1"
                        else:
                            legend = legend + "0"
                if tile in ["P", "R"]:  # Ground tiles are used for Paths and Rooms
                    tile = "G"
                elif tile == " ":
                    tile = "W"
                elif tile == "F":
                    tile = "F"
                self.specific_floor_tile_images[y][x] = tile + legend + ".png"  # Stores Tile names in this list similar to self.Floor, but specific to graphics

    def insert_borders(self):  # Surround map with empty/wall tile
        BORDER_IMAGE = "B111111111.png"
        for x in range(COLS):  # Top and Bottom borders
            self.specific_floor_tile_images[0][x] = self.specific_floor_tile_images[ROWS - 1][x] = BORDER_IMAGE
        for y in range(ROWS):  # Left and Right bornders
            self.specific_floor_tile_images[y][0] = self.specific_floor_tile_images[y][COLS - 1] = BORDER_IMAGE

    def draw_map(self):  # Blits tiles onto map.
        map_surface = p.Surface((TILE_SIZE * len(self.floor[0]), TILE_SIZE * len(self.floor)))
        self.insert_borders()
        for y in range(len(self.floor)):
            for x in range(len(self.floor[y])):
                tile = self.specific_floor_tile_images[y][x]
                possible_images = []
                for tile_type in self.tile_dict:
                    for generic_tile in self.tile_dict[tile_type]:
                        if tile in self.tile_dict[tile_type][generic_tile]:
                            possible_images.append(self.tile_dict[tile_type][generic_tile][-1])
                image = possible_images[randint(0, len(possible_images) - 1)]
                map_surface.blit(image, (TILE_SIZE * x, TILE_SIZE * y))

        self.map_image = map_surface

    def build_map(self):
        valid = False
        while not valid:
            self.path_coords = []  # empty each time it is invalid
            self.floor = [[" " for x in range(COLS)] for x in range(ROWS)]  # Generates empty floor layout
            self.insert_paths()  # Inserts the paths onto the floor
            valid = self.check_valid_paths()
        for _ in range(randint(self.min_room, self.max_room)):
            self.insert_water()
        for _ in range(randint(self.min_room, self.max_room)):
            self.insert_rooms()  # Inserts the rooms onto the floor
        self.find_specific_floor_tiles()
        self.draw_map()
        self.insert_misc()  # Inserts stairs and traps
        return self

    def display_map(self, position):
        display.blit(self.map_image, position)
