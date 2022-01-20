from __future__ import annotations
import generatordata
import os
import pygame
import random
import direction
import tile


class FloorBuilder:
    def build_floor(self) -> Floor:
        return Floor()

    def load_generator_data(self):
        pass


class OutdatedFloorBuilder(FloorBuilder):
    DUNGEON_DATA_DIR = os.path.join(os.getcwd(), "gamedata", "DungeonData.txt")
    TRAPS_PER_FLOOR = 6
    HEIGHT = 32
    WIDTH = 56
    DEFAULT_TILE = tile.Tile

    def __init__(self, dungeon_id: str):
        self.dungeon_id = dungeon_id

    def build_floor(self):
        self._floor = Floor()
        self.hallways = set()
        self.rooms = list()
        self.load_generator_data()
        self._insert_paths()
        self._insert_lakes()
        self._insert_rooms()
        self._insert_misc()
        self._find_room_exits()
        return self._floor

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
                self._floor[x, y] = tile.Tile.hallway_tile()
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
                if self._floor[x, y + 1].terrain == self._floor[x + 1, y].terrain == self._floor[x + 1, y + 1].terrain == tile.Terrain.GROUND:
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
                if self._floor[x, y].terrain == tile.Terrain.WALL and pygame.Vector2(i, j).length() <= radius:
                    self._floor[x, y] = tile.Tile.secondary_tile()

    def _insert_rooms(self):
        self.rooms = []
        for room_number in range(1, random.randint(self.min_room, self.max_room)+1):
            while True:
                width, height = random.randint(
                    self.min_dim, self.max_dim), random.randint(self.min_dim, self.max_dim)
                x = random.randint(2, self.WIDTH - 2 - width)
                y = random.randint(2, self.HEIGHT - 2 - height)
                if self._is_valid_room((x, y), (width, height)):
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
                self._floor[col + x, row + y] = tile.Tile.room_tile(room_number)
                room.add((col + x, row + y))
        self.rooms.append(room)

    def _insert_misc(self):
        self.misc_coords = set()
        self._insert_stairs()
        self._insert_traps()

    def _insert_stairs(self):
        x, y = self._get_random_misc_coords()
        self.misc_coords.add((x, y))
        self._floor.stairs_spawn = (x, y)
        self._floor[x, y].stairs_index = 1

    def _insert_traps(self):
        self.trap_coords = set()
        for _ in range(self.TRAPS_PER_FLOOR):
            x, y = self._get_random_misc_coords()
            self._floor[x, y].trap_index = 1
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

    def _find_room_exits(self):
        for room in self.rooms:
            for position in room:
                if not self._is_exit(position):
                    continue
                room_number = self._floor[position].room_index
                if room_number in self._floor.room_exits:
                    self._floor.room_exits[room_number].append(position)
                else:
                    self._floor.room_exits[room_number] = [position]

    def _is_exit(self, position: tuple[int, int]):
        return self._is_north_exit(position) or self._is_east_exit(position) or self._is_south_exit(position) or self._is_west_exit(position)

    def _is_north_exit(self, position: tuple[int, int]):
        x, y = position
        return self._floor.is_ground((x, y - 1)) and not self._floor.is_ground((x - 1, y - 1)) and not self._floor.is_ground((x + 1, y - 1))
    
    def _is_east_exit(self, position: tuple[int, int]):
        x, y = position
        return self._floor.is_ground((x + 1, y)) and not self._floor.is_ground((x + 1, y - 1)) and not self._floor.is_ground((x + 1, y + 1))

    def _is_south_exit(self, position: tuple[int, int]):
        x, y = position
        return self._floor.is_ground((x, y + 1)) and not self._floor.is_ground((x - 1, y + 1)) and not self._floor.is_ground((x + 1, y + 1))

    def _is_west_exit(self, position: tuple[int, int]):
        x, y = position
        return self._floor.is_ground((x - 1, y)) and not self._floor.is_ground((x - 1, y - 1)) and not self._floor.is_ground((x - 1, y + 1))


class FloorBuilder2(FloorBuilder):
    MERGE_CHANCE = 5

    def __init__(self, dungeon_id, floor_number):
        self.dungeon_id = dungeon_id
        self.floor_number = floor_number
        self.floor_size = 0
        self.data = self.load_generator_data()

    class Cell:
        def __init__(self):
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            self.valid_cell = False
            self.unk1 = 0
            self.is_room = False
            self.is_connected = False
            self.unk2 = 0
            self.unk3 = 0
            self.is_mh = 0
            self.unk4 = 0
            self.is_maze = 0
            self.is_merged = False
            self.connections: set[direction.Direction] = set()
            self.unk5 = 0
            self.imperfect = False
            self.secondary = False

    def load_generator_data(self):
        return generatordata.FloorGeneratorData(self.dungeon_id, self.floor_number)

    def build_floor(self) -> Floor:
        self.floor = super().build_floor()

        if self.data.fixed_floor_id != "0":
            return self.build_fixed_floor()

        self.generate_floor_structure()
        self.floor._find_room_exits()
        return self.floor

    def build_fixed_floor(self):
        pass

    def generate_floor_structure(self):
        s = self.data.structure
        if s == "SMALL":
            self.grid_size = (4, random.randrange(2)+2)
            self.floor_size = 1
            return self.generate_normal_floor()
        if s == "ONE_ROOM_MH":
            return None
        if s == "RING":
            return self.generate_ring()
        if s == "CROSSROADS":
            return self.generate_crossroads()
        if s == "TWO_ROOMS_MH":
            return None
        if s == "LINE":
            return self.generate_line()
        if s == "CROSS":
            return self.generate_cross()
        if s == "BETTLE":  # Typo: To be changed to BEETLE
            return self.generate_beetle()
        if s == "OUTER_ROOMS":
            return None
        if s == "MEDIUM":
            self.grid_size = 4, random.randrange(2)+2
            self.floor_size = 2
            return self.generate_normal_floor()
        if s == "SMALL_MEDIUM":
            self.grid_size = random.randrange(2, 5), random.randrange(2, 4)
        else:
            self.grid_size = random.randrange(2, 7), random.randrange(2, 5)
            return self.generate_normal_floor()

    def generate_normal_floor(self):
        self.grid = self.init_grid()
        self.grid_xs, self.grid_ys = self.grid_positions()
        self.assign_rooms()
        self.create_rooms()
        self.connect_cells()
        self.create_hallways()
        self.merge_rooms()
        self.join_isolated_rooms()
        self.insert_stairs()

    def generate_ring(self):
        pass

    def generate_crossroads(self):
        pass

    def generate_line(self):
        pass

    def generate_cross(self):
        pass

    def generate_beetle(self):
        pass

    def grid_positions(self) -> tuple[list[int], list[int]]:
        cell_size_x = self.floor.WIDTH // self.grid_size[0]
        cell_size_y = self.floor.HEIGHT // self.grid_size[1]
        xs = list(range(0, self.floor.WIDTH+1, cell_size_x))
        ys = list(range(0, self.floor.HEIGHT+1, cell_size_y))
        return xs, ys

    def init_grid(self) -> dict[tuple[int, int], Cell]:
        grid = {(x, y):self.Cell() for x in range(self.grid_size[0]) for y in range(self.grid_size[1])}
        for (x, _), cell in grid.items():
            if self.floor_size == 1 and x >= self.grid_size[0]//2:
                cell.valid_cell = False
            elif self.floor_size == 2 and x >= self.grid_size[0]*3//4:
                cell.valid_cell = False
            else:
                cell.valid_cell = True
        return grid

    def assign_rooms(self):
        room_density = self.data.room_density
        if room_density < 0:
            room_density = -room_density
        else:
            room_density = room_density + random.randrange(0, 3)

        rooms_ok = [(i < room_density) for i in range(len(self.grid))]
        while True:
            random.shuffle(rooms_ok)
            placed = 0
            for i, cell in enumerate(self.grid.values()):
                if not cell.valid_cell:
                    continue
                if rooms_ok[i]:
                    cell.is_room = True
                    placed += 1
            if placed >= 2:
                return

    def create_rooms(self):
        room_number = 1
        for (x, y), cell in self.grid.items():
            if not cell.valid_cell:
                continue
            x0, x1 = self.grid_xs[x:x+2]
            y0, y1 = self.grid_ys[y:y+2]
            max_w = x1 - x0 - 4
            max_h = y1 - y0 - 3
            if cell.is_room:
                w = random.randrange(5, max_w)
                h = random.randrange(4, max_h)
                w = min(w, h*3//2)
                h = min(h, w*3//2)
                cell.start_x = random.randrange(max_w-w)+x0+2
                cell.start_y = random.randrange(max_h-h)+y0+2
                cell.end_x = cell.start_x + w
                cell.end_y = cell.start_y + h
                for tile_x in range(cell.start_x, cell.end_x):
                    for tile_y in range(cell.start_y, cell.end_y):
                        self.floor[tile_x, tile_y] = tile.Tile.room_tile(room_number)
                cell.imperfect = random.randrange(100) < self.data.imperfect_rooms
                cell.secondary = random.randrange(100) < self.data.secondary_percentage
                room_number += 1
            else:  # Dummy room
                l_margin = 1 if x == 0 else 2
                r_margin = 2 if x == self.grid_size[0]-1 else 4
                u_margin = 1 if y == 0 else 2
                b_margin = 2 if y == self.grid_size[1]-1 else 4
                cell.start_x = random.randrange(x0+2+l_margin, x0+2+max_w-r_margin)
                cell.start_y = random.randrange(y0+2+u_margin, y0+2+max_h-b_margin)
                cell.end_x = cell.start_x + 1
                cell.end_y = cell.start_y + 1
                self.floor[cell.start_x, cell.start_y] = tile.Tile.hallway_tile()

    def connect_cells(self):
        position = random.choice([p for p, cell in self.grid.items() if cell.valid_cell])
        for _ in range(self.data.floor_connectivity):
            position = self.connect_cell(position)
        self.remove_dead_ends()

    def connect_cell(self, position: tuple[int, int]):
        x, y = position
        ds = direction.Direction.get_non_diagonal_directions()
        if x == 0:
            ds.remove(direction.Direction.WEST)
        elif x == self.grid_size[0]-1 or not self.grid[x+1, y].valid_cell:
            ds.remove(direction.Direction.EAST)
        if y == 0:
            ds.remove(direction.Direction.NORTH)
        elif y == self.grid_size[1]-1 or not self.grid[x, y+1].valid_cell:
            ds.remove(direction.Direction.SOUTH)
        d = random.choice(list(ds))
        dx, dy = d.value
        self.grid[x, y].connections.add(d)
        self.grid[x+dx, y+dy].connections.add(d.flip())
        return x+dx, y+dy
    
    def remove_dead_ends(self):
        if self.data.dead_ends:
            return
        checking_dead_ends = True
        while checking_dead_ends:
            checking_dead_ends = False
            for p, cell in self.grid.items():
                if not cell.valid_cell or cell.is_room:
                    continue
                if len(cell.connections) == 1:
                    checking_dead_ends = True
                    self.connect_cell(p)

    def create_hallways(self):
        seen = []
        for (x, y), cell in self.grid.items():
            if not cell.valid_cell:
                return
            for d in cell.connections:
                if (cell, d) in seen:
                    continue
                self.create_hallway((x, y), d)
                seen.append((cell, d))
                dx, dy = d.value
                seen.append((self.grid[x+dx, y+dy], d.flip()))

    def create_hallway(self, cell_position: tuple[int, int], d: direction.Direction):
        cell = self.grid[cell_position]
        if not cell.is_room:
            x0, y0 = cell.start_x, cell.start_y
        else:
            x0 = random.randrange(cell.start_x+1, cell.end_x-1)
            y0 = random.randrange(cell.start_y+1, cell.end_y-1)
        x, y = cell_position
        dx, dy = d.value
        other_cell = self.grid[x+dx, y+dy]
        cell.is_connected = True
        other_cell.is_connected = True
        if not other_cell.is_room:
            x1 = other_cell.start_x
            y1 = other_cell.start_y
        else:
            x1 = random.randrange(other_cell.start_x+1, other_cell.end_x-1)
            y1 = random.randrange(other_cell.start_y+1, other_cell.end_y-1)
        cur_x, cur_y = x0, y0
        if d.is_horizontal():
            if d == direction.Direction.EAST:
                border = self.grid_xs[x+1]
            else:
                border = self.grid_xs[x]
            while cur_x != border:
                if not self.floor[cur_x, cur_y].room_index:
                    self.floor[cur_x, cur_y] = tile.Tile.hallway_tile()
                cur_x += dx
            while cur_y != y1:
                if self.floor[cur_x, cur_y].terrain == tile.Terrain.GROUND:
                    return
                self.floor[cur_x, cur_y] = tile.Tile.hallway_tile()
                if cur_y >= y1:
                    cur_y -= 1
                else:
                    cur_y += 1
            while cur_x != x1:
                if self.floor[cur_x, cur_y].terrain == tile.Terrain.GROUND:
                    return
                self.floor[cur_x, cur_y] = tile.Tile.hallway_tile()
                cur_x += dx
        elif d.is_vertical():
            if d == direction.Direction.SOUTH:
                border = self.grid_ys[y+1]
            else:
                border = self.grid_ys[y]
            while cur_y != border:
                if not self.floor[cur_x, cur_y].room_index:
                    self.floor[cur_x, cur_y] = tile.Tile.hallway_tile()
                cur_y += dy
            while cur_x != x1:
                if self.floor[cur_x, cur_y].terrain == tile.Terrain.GROUND:
                    return
                self.floor[cur_x, cur_y] = tile.Tile.hallway_tile()
                if cur_x >= x1:
                    cur_x -= 1
                else:
                    cur_x += 1
            while cur_y != y1:
                if self.floor[cur_x, cur_y].terrain == tile.Terrain.GROUND:
                    return
                self.floor[cur_x, cur_y] = tile.Tile.hallway_tile()
                cur_y += dy

    def merge_rooms(self):
        for (x, y), cell in self.grid.items():
            if not cell.valid_cell:
                continue
            if cell.is_merged:
                continue
            if not cell.is_room:
                continue
            if not cell.is_connected:
                continue
            if cell.unk1:  # Normal cell?
                continue
            if not (random.randrange(100) < self.MERGE_CHANCE):
                continue
            d = random.choice(list(cell.connections))
            dx, dy = d.value
            other_cell = self.grid[x+dx, y+dy]
            if other_cell.is_merged:
                continue
            if not other_cell.is_room:
                continue
            if other_cell.unk1:
                continue
            self.merge_specific_rooms(cell, other_cell)

    def merge_specific_rooms(self, cell: Cell, other_cell: Cell):
        room_index = self.floor[cell.start_x, cell.start_y].room_index
        x0 = other_cell.start_x = min(cell.start_x, other_cell.start_x)
        y0 = other_cell.start_y = min(cell.start_y, other_cell.start_y)
        x1 = other_cell.end_x = max(cell.end_x, other_cell.end_x)
        y1 = other_cell.end_y = max(cell.end_y, other_cell.end_y)
        for x in range(x0, x1):
            for y in range(y0, y1):
                self.floor[x, y] = tile.Tile.room_tile(room_index)
        cell.is_merged = True
        other_cell.is_merged = True

    def join_isolated_rooms(self):
        for (x, y), cell in self.grid.items():
            if not cell.valid_cell:
                continue
            if cell.is_connected:
                continue
            if cell.is_merged:
                continue
            if cell.is_room and not cell.unk1:
                self.connect_cell((x, y))
                for d in cell.connections:
                    self.create_hallway((x, y), d)
            else:
                self.floor[cell.start_x, cell.start_y] = tile.Tile()

    def insert_stairs(self):
        for position in self.floor:
            if self.floor[position].can_spawn:
                self.floor.stairs_spawn = position
                return


class Floor:
    WIDTH = 56
    HEIGHT = 32

    def __init__(self):
        self._floor: dict[tuple[int, int], tile.Tile] = {}
        self._stairs_spawn = None
        self.room_exits: dict[int, list[tuple[int, int]]] = {}

    def __getitem__(self, position: tuple[int, int]) -> tile.Tile:
        if not self.in_bounds(position):
            return tile.Tile.impassable_tile()
        return self._floor.get(position, tile.Tile())

    def __setitem__(self, position: tuple[int, int], item: tile.Tile):
        self._floor[position] = item

    def __iter__(self):
        return iter(self._floor)

    @property
    def stairs_spawn(self) -> tuple[int, int]:
        return self._stairs_spawn

    @stairs_spawn.setter
    def stairs_spawn(self, position: tuple[int, int]):
        if self._stairs_spawn is None:
            self._stairs_spawn = position

    def surrounding_tiles(self, position: tuple[int, int]) -> list[tile.Tile]:
        x, y = position
        surrounding_tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                surrounding_tiles.append(self[x + j, y + i])
        return surrounding_tiles

    def surrounding_terrain(self, position: tuple[int, int]) -> list[tile.Terrain]:
        return [t.terrain for t in self.surrounding_tiles(position)]

    def in_bounds(self, position: tuple[int, int]) -> bool:
        x, y = position
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def clear(self):
        self._floor.clear()

    def is_room(self, p: tuple[int, int]) -> bool:
        return self[p].room_index

    def in_same_room(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.is_room(p1) and self[p1].room_index == self[p2].room_index

    def cuts_corner(self, p: tuple[int, int], d: direction.Direction) -> bool:
        if not d.is_diagonal():
            return False
        surrounding = self.surrounding_terrain(p)
        if d == direction.Direction.NORTH_EAST:
            return tile.Terrain.WALL in {surrounding[1], surrounding[4]}
        if d == direction.Direction.NORTH_WEST:
            return tile.Terrain.WALL in {surrounding[1], surrounding[3]}
        if d == direction.Direction.SOUTH_EAST:
            return tile.Terrain.WALL in {surrounding[6], surrounding[4]}
        if d == direction.Direction.SOUTH_WEST:
            return tile.Terrain.WALL in {surrounding[6], surrounding[3]}

    def is_ground(self, position: tuple[int, int]):
        return self[position].terrain == tile.Terrain.GROUND

    def is_wall(self, position: tuple[int, int]):
        return self[position].terrain == tile.Terrain.WALL

    def _find_room_exits(self):
        for position in self._floor:
            if not self.is_room(position):
                continue
            if not self._is_exit(position):
                continue
            room_number = self._floor[position].room_index
            if room_number in self.room_exits:
                self.room_exits[room_number].append(position)
            else:
                self.room_exits[room_number] = [position]

    def _is_exit(self, position: tuple[int, int]):
        return self._is_north_exit(position) or self._is_east_exit(position) or self._is_south_exit(position) or self._is_west_exit(position)

    def _is_north_exit(self, position: tuple[int, int]):
        x, y = position
        return self.is_ground((x, y - 1)) and not self.is_ground((x - 1, y - 1)) and not self.is_ground((x + 1, y - 1))
    
    def _is_east_exit(self, position: tuple[int, int]):
        x, y = position
        return self.is_ground((x + 1, y)) and not self.is_ground((x + 1, y - 1)) and not self.is_ground((x + 1, y + 1))

    def _is_south_exit(self, position: tuple[int, int]):
        x, y = position
        return self.is_ground((x, y + 1)) and not self.is_ground((x - 1, y + 1)) and not self.is_ground((x + 1, y + 1))

    def _is_west_exit(self, position: tuple[int, int]):
        x, y = position
        return self.is_ground((x - 1, y)) and not self.is_ground((x - 1, y - 1)) and not self.is_ground((x - 1, y + 1))