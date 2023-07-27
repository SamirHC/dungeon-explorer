from __future__ import annotations

import random

from app.common import direction
from app.dungeon import dungeondata, tile
from app.dungeon.dungeondata import Structure
from app.pokemon import party, pokemon


class Floor:
    WIDTH = 56
    HEIGHT = 32
    SIZE = (WIDTH, HEIGHT)

    def __init__(self):
        self._floor = tuple(tile.Tile() for _ in range(self.WIDTH*self.HEIGHT))
        self.room_exits: dict[int, list[tuple[int, int]]] = {}
        self.stairs_spawn = (0, 0)
        self.has_shop = False

        self.active_enemies: list[pokemon.Pokemon] = []
        self.spawned: list[pokemon.Pokemon] = []
        self.party: party.Party = None

    def __getitem__(self, position: tuple[int, int]) -> tile.Tile:
        if not self.in_bounds(position):
            return tile.Tile().impassable_tile()
        x, y = position
        return self._floor[x + y*self.WIDTH]

    def __iter__(self):
        return iter(self._floor)

    def get_tile_mask(self, position: tuple[int, int]) -> int:
        return self[position].tile_mask

    def get_cardinal_tile_mask(self, position: tuple[int, int]) -> int:
        return self[position].cardinal_tile_mask
    
    def in_bounds(self, position: tuple[int, int]) -> bool:
        x, y = position
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT
    
    def in_inner_bounds(self, position: tuple[int, int]) -> bool:
        x, y = position
        return 0 < x < self.WIDTH - 1 and 0 < y < self.HEIGHT - 1

    def clear(self):
        for tile in self._floor:
            tile.reset()

    def is_room(self, p: tuple[int, int]) -> bool:
        return self[p].room_index

    def in_same_room(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.is_room(p1) and self[p1].room_index == self[p2].room_index

    def is_ground(self, position: tuple[int, int]):
        return self[position].tile_type is tile.TileType.TERTIARY

    def is_wall(self, position: tuple[int, int]):
        return self[position].tile_type is tile.TileType.PRIMARY
    
    def is_valid_spawn_location(self, position):
        return self[position].can_spawn and self[position].pokemon_ptr is None

    def get_valid_spawn_locations(self):
        valid_spawns = []
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                position = x, y
                if self.is_valid_spawn_location(position):
                    valid_spawns.append(position)
        return valid_spawns


class FloorBuilder:
    MERGE_CHANCE = 5

    def __init__(self, data: dungeondata.FloorData, party: party.Party, seed: int):
        self.data = data
        self.party = party
        self.floor_size = 0
        self.floor = None
        self.random = random.Random(seed)

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
            self.is_merged = False
            self.connections: set[direction.Direction] = set()
            self.imperfect = False
            self.secondary = False

    def build_floor(self) -> Floor:
        self.build_floor_structure()
        self.fill_floor_with_spawns()
        return self.floor
    
    def build_floor_structure(self) -> Floor:
        if self.data.fixed_floor_id != "0":
            return self.build_fixed_floor()

        while True:
            self.floor = Floor()

            self.generate_floor_structure()
            if self.is_strongly_connected():
                break
            print("Restarting...")
        self.set_tile_masks()
        return self.floor

    def build_fixed_floor(self):
        pass

    def generate_floor_structure(self):
        s = self.data.structure
        if s is Structure.SMALL:
            self.grid_size = (4, self.random.randrange(2)+2)
            self.floor_size = 1
            self.generate_normal_floor()
        elif s is Structure.ONE_ROOM_MH:
            pass
        elif s is Structure.RING:
            self.generate_ring()
        elif s is Structure.CROSSROADS:
            self.generate_crossroads()
        elif s is Structure.TWO_ROOMS_MH:
            pass
        elif s is Structure.LINE:
            self.generate_line()
        elif s is Structure.CROSS:
            self.generate_cross()
        elif s is Structure.BEETLE:
            self.generate_beetle()
        elif s is Structure.OUTER_ROOMS:
            pass
        elif s is Structure.MEDIUM:
            self.grid_size = 4, self.random.randrange(2)+2
            self.floor_size = 2
            self.generate_normal_floor()
        elif s is Structure.SMALL_MEDIUM:
            self.grid_size = self.random.randrange(2, 5), self.random.randrange(2, 4)
            self.generate_normal_floor()
        elif s.is_medium_large():
            self.grid_size = self.random.randrange(2, 7), self.random.randrange(2, 5)
            self.generate_normal_floor()
        self.find_room_exits()
        if self.data.secondary_used:
            self.generate_secondary()

    def generate_normal_floor(self):
        self.grid = self.init_grid()
        self.grid_xs, self.grid_ys = self.grid_positions()
        self.assign_rooms()
        self.create_rooms()
        self.connect_cells()
        self.create_hallways()
        self.merge_rooms()
        self.join_isolated_rooms()
        self.create_extra_hallways()

    def generate_ring(self):
        self.grid_size = (6, 4)
        self.grid = self.init_grid()
        self.grid_xs = [0, 6, 17, 28, 39, 50, 56]
        self.grid_ys = [0, 7, 16, 25, 32]

        for x in range(1, 5):
            for y in range(1, 3):
                self.grid[x, y].is_room = True
        self.create_rooms()

        for x in range(5):
            self.connect_cell_in_direction((x, 0), direction.Direction.EAST)
            self.connect_cell_in_direction((x, 3), direction.Direction.EAST)
        for y in range(3):
            self.connect_cell_in_direction((0, y), direction.Direction.SOUTH)
            self.connect_cell_in_direction((5, y), direction.Direction.SOUTH)
        self.connect_cells()
        self.create_hallways()
        self.merge_rooms()
        self.join_isolated_rooms()
        self.create_extra_hallways()

    def generate_crossroads(self):
        self.grid_size = (5, 4)
        self.grid = self.init_grid()
        self.grid_xs, self.grid_ys = self.grid_positions()

        for x in range(1, 4):
            self.grid[x, 0].is_room = True
            self.grid[x, 3].is_room = True
        for y in range(1, 3):
            self.grid[0, y].is_room = True
            self.grid[4, y].is_room = True
        for x in (0, 4):
            for y in (0, 3):
                self.grid[x, y].valid_cell = False
        self.create_rooms()
        
        for x in range(1, 4):
            for y in range(3):
                self.connect_cell_in_direction((x, y), direction.Direction.SOUTH)
        for x in range(4):
            for y in range(1, 3):
                self.connect_cell_in_direction((x, y), direction.Direction.EAST)
        self.create_hallways()
        self.join_isolated_rooms()
        self.create_extra_hallways()

    def generate_line(self):
        self.grid_size = 5, 1
        self.grid_xs = [0, 11, 22, 33, 44, 56]
        self.grid_ys = [4, 15]
        self.grid = self.init_grid()
        self.assign_rooms()
        self.create_rooms()
        self.connect_cells()
        self.create_hallways()
        self.join_isolated_rooms()
        self.create_extra_hallways()

    def generate_cross(self):
        self.grid_size = (3, 3)
        self.grid_xs = [11, 22, 33, 44]
        self.grid_ys = [2, 11, 20, 31]
        self.grid = self.init_grid()
        for x in (0, 2):
            for y in (0, 2):
                self.grid[x, y].valid_cell = False
        for i in range(3):
            self.grid[i, 1].is_room = True
            self.grid[1, i].is_room = True
        self.create_rooms()
        for x in range(2):
            self.connect_cell_in_direction((x, 1), direction.Direction.EAST)
        for y in range(2):
            self.connect_cell_in_direction((1, y), direction.Direction.SOUTH)
        self.create_hallways()
        self.create_extra_hallways()

    def generate_beetle(self):
        self.grid_size = (3, 3)
        self.grid_xs = [5, 15, 36, 50]
        self.grid_ys = [2, 11, 20, 31]
        self.grid = self.init_grid()
        for _, cell in self.grid.items():
            cell.is_room = True
        self.create_rooms()
        for x in range(2):
            for y in range(3):
                self.connect_cell_in_direction((x, y), direction.Direction.EAST)
        for y in range(2):
            self.connect_cell_in_direction((1, y), direction.Direction.SOUTH)
        self.create_hallways()
        self.merge_specific_rooms(self.grid[1, 0], self.grid[1, 1])
        self.merge_specific_rooms(self.grid[1, 1], self.grid[1, 2])
        self.create_extra_hallways()

    def grid_positions(self) -> tuple[list[int], list[int]]:
        cell_size_x = self.floor.WIDTH // self.grid_size[0]
        cell_size_y = self.floor.HEIGHT // self.grid_size[1]
        xs = list(range(0, self.floor.WIDTH+1, cell_size_x))
        ys = list(range(0, self.floor.HEIGHT+1, cell_size_y))
        return xs, ys

    def init_grid(self) -> dict[tuple[int, int], Cell]:
        grid = {(x, y): self.Cell() for x in range(self.grid_size[0]) for y in range(self.grid_size[1])}
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
            room_density = room_density + self.random.randrange(0, 3)

        rooms_ok = [(i < room_density) for i in range(len(self.grid))]
        while True:
            self.random.shuffle(rooms_ok)
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
            max_w = x1 - x0 - 3
            max_h = y1 - y0 - 3
            if cell.is_room:
                w = self.random.randrange(5, max_w)
                h = self.random.randrange(4, max_h)
                w = min(w, h*3//2)
                h = min(h, w*3//2)
                cell.start_x = self.random.randrange(max_w-w)+x0+2
                cell.start_y = self.random.randrange(max_h-h)+y0+2
                cell.end_x = cell.start_x + w
                cell.end_y = cell.start_y + h
                for tile_x in range(cell.start_x, cell.end_x):
                    for tile_y in range(cell.start_y, cell.end_y):
                        this_tile = self.floor[tile_x, tile_y]
                        this_tile.room_tile(room_number)
                cell.imperfect = self.random.randrange(100) < self.data.imperfect_rooms
                cell.secondary = self.random.randrange(100) < self.data.secondary_percentage
                room_number += 1
            else:  # Dummy room
                cell.start_x = self.random.randrange(x0+2, x1-2)
                cell.start_y = self.random.randrange(y0+2, y1-2)
                cell.end_x = cell.start_x + 1
                cell.end_y = cell.start_y + 1
                this_tile = self.floor[cell.start_x, cell.start_y]
                this_tile.hallway_tile()

    def connect_cells(self):
        position = self.random.choice([p for p, cell in self.grid.items() if cell.valid_cell])
        for _ in range(self.data.floor_connectivity):
            position = self.connect_cell(position)
        self.remove_dead_ends()

    def connect_cell(self, position: tuple[int, int]):
        x, y = position
        ds: list[direction.Direction] = []
        if x != 0:
            ds.append(direction.Direction.WEST)
        if x != self.grid_size[0]-1 and self.grid[x+1, y].valid_cell:
            ds.append(direction.Direction.EAST)
        if y != 0:
            ds.append(direction.Direction.NORTH)
        if y != self.grid_size[1]-1 and self.grid[x, y+1].valid_cell:
            ds.append(direction.Direction.SOUTH)
        d = self.random.choice(ds)
        dx, dy = d.value
        self.connect_cell_in_direction(position, d)
        return x+dx, y+dy

    def connect_cell_in_direction(self, position: tuple[int, int], d: direction.Direction):
        x, y = position
        dx, dy = d.value
        self.grid[x, y].connections.add(d)
        self.grid[x+dx, y+dy].connections.add(d.flip())
    
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
                continue
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
            x0 = self.random.randrange(cell.start_x+1, cell.end_x-1)
            y0 = self.random.randrange(cell.start_y+1, cell.end_y-1)
        x, y = cell_position
        dx, dy = d.value
        other_cell = self.grid[x+dx, y+dy]
        cell.is_connected = True
        other_cell.is_connected = True
        if not other_cell.is_room:
            x1 = other_cell.start_x
            y1 = other_cell.start_y
        else:
            x1 = self.random.randrange(other_cell.start_x+1, other_cell.end_x-1)
            y1 = self.random.randrange(other_cell.start_y+1, other_cell.end_y-1)
        cur_x, cur_y = x0, y0
        if d.is_horizontal():
            if d is direction.Direction.EAST:
                border = self.grid_xs[x+1]-1
            else:
                border = self.grid_xs[x]
            while cur_x != border:
                if not self.floor[cur_x, cur_y].room_index:
                    self.floor[cur_x, cur_y].hallway_tile()
                cur_x += dx
            while cur_y != y1:
                if self.floor[cur_x, cur_y].tile_type is tile.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                if cur_y >= y1:
                    cur_y -= 1
                else:
                    cur_y += 1
            while cur_x != x1:
                if self.floor[cur_x, cur_y].tile_type is tile.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                cur_x += dx
        elif d.is_vertical():
            if d is direction.Direction.SOUTH:
                border = self.grid_ys[y+1]-1
            else:
                border = self.grid_ys[y]
            while cur_y != border:
                if not self.floor[cur_x, cur_y].room_index:
                    self.floor[cur_x, cur_y].hallway_tile()
                cur_y += dy
            while cur_x != x1:
                if self.floor[cur_x, cur_y].tile_type is tile.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                if cur_x >= x1:
                    cur_x -= 1
                else:
                    cur_x += 1
            while cur_y != y1:
                if self.floor[cur_x, cur_y].tile_type is tile.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
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
            if not (self.random.randrange(100) < self.MERGE_CHANCE):
                continue
            d = self.random.choice(list(cell.connections))
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
                self.floor[x, y].room_tile(room_index)
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
                self.floor[cell.start_x, cell.start_y].reset()

    def create_shop(self):
        if not self.data.shop:
            return
        if not (self.random.randrange(100) < self.data.shop):
            return
        grid_items = [item for item in self.grid.items()]
        self.random.shuffle(grid_items)
        for (x, y), cell in grid_items:
            if not cell.valid_cell:
                continue
            if not cell.is_room:
                continue
            if not cell.is_connected:
                continue
            if cell.is_merged:
                continue
            if cell.unk1:
                continue
            if cell.secondary:
                continue
            self.floor.has_shop = True
            room_number = self.floor[cell.start_x, cell.start_y].room_index
            for x in range(cell.start_x+1, cell.end_x-1):
                for y in range(cell.start_y+1, cell.end_y-1):
                    self.floor[x, y].shop_tile(room_number)
            return

    def create_extra_hallways(self):
        for _ in range(self.data.extra_hallway_density):
            # Select a random cell
            x = self.random.randrange(self.grid_size[0])
            y = self.random.randrange(self.grid_size[1])
            cell = self.grid[x, y]

            # Cannot use this cell if:
            if not cell.is_room:
                continue
            if not cell.is_connected:
                continue
            if not cell.valid_cell:
                continue

            # Starting position in cell
            x0 = self.random.randrange(cell.start_x, cell.end_x)
            y0 = self.random.randrange(cell.start_y, cell.end_y)

            # Get direction of travel from starting position
            ds: list[direction.Direction] = []
            if x != 0:
                ds.append(direction.Direction.WEST)
            if x != self.grid_size[0]-1:
                ds.append(direction.Direction.EAST)
            if y != 0:
                ds.append(direction.Direction.NORTH)
            if y != self.grid_size[1]-1:
                ds.append(direction.Direction.SOUTH)
            d = self.random.choice(ds)
            dx, dy = d.value

            # Walk to room edge
            cur_x, cur_y = x0, y0
            while self.floor[cur_x, cur_y].room_index:
                cur_x += dx
                cur_y += dy

            # Walk to non-ground tile
            while self.floor[cur_x, cur_y].tile_type is tile.TileType.TERTIARY:
                cur_x += dx
                cur_y += dy
            
            # Check if 5x5 surrounding area is in bounds
            valid = True
            for i in range(cur_x-2, cur_x+3):
                for j in range(cur_y-2, cur_y+3):
                    if not self.floor.in_bounds((i, j)):
                        valid = False
                        break
                if not valid:
                    break
            if not valid:
                continue
            
            # Check tiles perpendicular to direction from current
            d_cw = d.clockwise().clockwise()
            dx_cw, dy_cw = d_cw.value
            if self.floor[cur_x + dx_cw, cur_y + dy_cw].tile_type is tile.TileType.TERTIARY:
                continue
            d_acw = d.anticlockwise().anticlockwise()
            dx_acw, dy_acw = d_acw.value
            if self.floor[cur_x + dx_acw, cur_y + dy_acw].tile_type is tile.TileType.TERTIARY:
                continue
            
            # Start extra hallway generation
            segment_length = self.random.randrange(3, 6)
            while True:
                # Stop if:
                if cur_x <= 1 or cur_y <= 1 or self.floor.WIDTH - 2 <= cur_x or self.floor.HEIGHT - 2 <= cur_y:
                    break
                if self.floor[cur_x, cur_y].tile_type is tile.TileType.TERTIARY:
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is tile.TileType.TERTIARY 
                    for d in [
                        direction.Direction.NORTH,
                        direction.Direction.NORTH_EAST,
                        direction.Direction.EAST
                        ]
                    ]
                ):
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is tile.TileType.TERTIARY 
                    for d in [
                        direction.Direction.NORTH,
                        direction.Direction.NORTH_WEST,
                        direction.Direction.WEST
                        ]
                    ]
                ):
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is tile.TileType.TERTIARY 
                    for d in [
                        direction.Direction.SOUTH,
                        direction.Direction.SOUTH_EAST,
                        direction.Direction.EAST
                        ]
                    ]
                ):
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is tile.TileType.TERTIARY 
                    for d in [
                        direction.Direction.SOUTH,
                        direction.Direction.SOUTH_WEST,
                        direction.Direction.WEST
                        ]
                    ]
                ):
                    break

                # Turn into hallway
                self.floor[cur_x, cur_y].hallway_tile()
                # Check tiles perpendicular to direction from current
                d_cw = d.clockwise().clockwise()
                dx_cw, dy_cw = d_cw.value
                if self.floor[cur_x + dx_cw, cur_y + dy_cw].tile_type is tile.TileType.TERTIARY:
                    break
                d_acw = d.anticlockwise().anticlockwise()
                dx_acw, dy_acw = d_acw.value
                if self.floor[cur_x + dx_acw, cur_y + dy_acw].tile_type is tile.TileType.TERTIARY:
                    break
                # Iteration counter
                segment_length -= 1
                # Change direction on end of segment
                if segment_length == 0:
                    segment_length = self.random.randrange(3, 6)
                    if self.random.randrange(100) < 50:
                        d = d.clockwise().clockwise()
                    else:
                        d = d.anticlockwise().anticlockwise()
                    dx, dy = d.value
                    # Exit if out of soft-bounds
                    if cur_x >= 32 and self.floor_size == 1 and d is direction.Direction.EAST:
                        break
                    if cur_x >= 48 and self.floor_size == 2 and d is direction.Direction.EAST:
                        break
                # Update curs
                cur_x += dx
                cur_y += dy

    def find_room_exits(self):
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                position = (x, y)
                if not self.is_room_exit(position):
                    continue
                self.floor[position].can_spawn = False
                room_number = self.floor[position].room_index
                if room_number in self.floor.room_exits:
                    self.floor.room_exits[room_number].append(position)
                else:
                    self.floor.room_exits[room_number] = [position]

    def is_room_exit(self, position: tuple[int, int]):
        if not self.floor.is_room(position):
            return False
        x, y = position
        for d in direction.CARDINAL_DIRECTIONS:
            d_pos = x + d.x, y + d.y
            if self.floor.is_ground(d_pos) and not self.floor.is_room(d_pos):
                return True
        return False

    def generate_secondary(self):
        MIN_WIDTH, MAX_WIDTH = 2, self.floor.WIDTH - 2
        MIN_HEIGHT, MAX_HEIGHT = 2, self.floor.HEIGHT - 2

        num_rivers = self.random.randrange(1, 4)
        num_sections = 20
        for _ in range(num_rivers):
            x = self.random.randrange(MIN_WIDTH, MAX_WIDTH)
            if self.random.randrange(64) < 50:
                d = direction.Direction.NORTH
                y = MAX_HEIGHT
            else:
                d = direction.Direction.SOUTH
                y = MIN_HEIGHT
            d0 = d
            lake_at = self.random.randrange(10, 60)
            for _ in range(num_sections):
                section_length = self.random.randrange(2, 8)
                end = False
                for _ in range(section_length):
                    if not (MIN_WIDTH <= x < MAX_WIDTH):
                        continue
                    if not (MIN_HEIGHT <= y < MAX_HEIGHT):
                        continue
                    if self.floor[x, y].tile_type is tile.TileType.SECONDARY:
                        end = True
                        break
                    if self.floor[x, y].tile_type is tile.TileType.PRIMARY:
                        self.floor[x, y].secondary_tile()
                    x += d.x
                    y += d.y
                    if y < 0 or y >= 32:
                        break
                    lake_at -= 1
                    if lake_at != 0:
                        continue
                    # Add river lakes
                    for _ in range(100):
                        cx = self.random.randrange(-3, 4) + x
                        cy = self.random.randrange(-3, 4) + y
                        if not (MIN_WIDTH <= cx <= MAX_WIDTH and MIN_HEIGHT <= cy <= MAX_HEIGHT):
                            continue
                        if self.floor[cx, cy].tile_type is not tile.TileType.PRIMARY:
                            continue
                        for cd in direction.Direction:
                            if self.floor[cx + cd.x, cy + cd.y].tile_type is tile.TileType.SECONDARY:
                                self.floor[cx, cy].secondary_tile()
                                break
                    for i in range(-3, 4):
                        for j in range(-3, 4):
                            sec_count = 0
                            if not (MIN_WIDTH <= x+i <= MAX_WIDTH and MIN_HEIGHT <= y+j <= MAX_HEIGHT):
                                continue
                            if self.floor[x+i, x+j].tile_type is not tile.TileType.PRIMARY:
                                continue
                            for cd in direction.Direction:
                                if self.floor[x+i+cd.x, y+j+cd.y].tile_type is tile.TileType.SECONDARY:
                                    sec_count += 1
                                if sec_count == 4:
                                    self.floor[x + i, y + j].secondary_tile()
                                    break
                if not end:
                    if d.is_horizontal():
                        d = d0
                    else:
                        if self.random.randrange(100) < 50:
                            d = direction.Direction.EAST
                        else:
                            d = direction.Direction.WEST
                if y<0 or y >= 32:
                    break
        # Generate river independent lakes
        for _ in range(self.data.water_density):
            x = self.random.randrange(MIN_WIDTH, MAX_WIDTH)
            y = self.random.randrange(MIN_HEIGHT, MAX_HEIGHT)
            dry = [[(x==0 or y==0 or x==9 or y==9) for x in range(10)] for y in range(10)]
            for _ in range(80):
                dry_x = self.random.randrange(1, 9)
                dry_y = self.random.randrange(1, 9)
                for d in direction.CARDINAL_DIRECTIONS:
                    if dry[dry_y + d.y][dry_x + d.x]:
                        dry[dry_y][dry_x] = True
                        break
            for i in range(10):
                for j in range(10):
                    if dry[i][j]:
                        continue
                    pos_x = x + j - 5
                    pos_y = y + i - 5
                    if not (MIN_WIDTH <= pos_x < MAX_WIDTH and MIN_HEIGHT <= pos_y < MAX_HEIGHT):
                        continue
                    if self.floor[pos_x, pos_y].tile_type is tile.TileType.PRIMARY:
                        self.floor[pos_x, pos_y].secondary_tile()

    def is_strongly_connected(self):
        visited = set()
        stack = []
        for (x, y), cell in self.grid.items():
            if cell.valid_cell:
                stack.append((x, y))
                break
        while stack:
            x, y = stack.pop()
            for d in self.grid[x, y].connections:
                visited.add((x, y))
                dx, dy = d.value
                other = (x+dx, y+dy)
                if other not in visited:
                    stack.append(other)
        for (x, y), cell in self.grid.items():
            if cell.valid_cell and cell.is_connected:
                if (x, y) not in visited:
                    return False
        return True

    def set_tile_masks(self):
        for x, y in [(x, y) for x in range(self.floor.WIDTH) for y in range(self.floor.HEIGHT)]:
            this_tile = self.floor[x, y]
            mask = []
            cardinal_mask = []
            for d in [
                direction.Direction.NORTH_WEST,
                direction.Direction.NORTH,
                direction.Direction.NORTH_EAST,
                direction.Direction.WEST,
                direction.Direction.EAST,
                direction.Direction.SOUTH_WEST,
                direction.Direction.SOUTH,
                direction.Direction.SOUTH_EAST,
            ]:
                other_tile = self.floor[x+d.x, y+d.y]
                is_same = this_tile.tile_type is other_tile.tile_type
                mask.append(is_same)
                if d.is_cardinal():
                    cardinal_mask.append(is_same)
            this_tile.tile_mask = tile.value(tuple(mask))
            this_tile.cardinal_tile_mask = tile.value(tuple(cardinal_mask))

    # END OF FLOOR STRUCTURE BUILDER
    def get_valid_spawn_locations(self):
        return self.floor.get_valid_spawn_locations()
    
    def get_valid_buried_spawn_locations(self):
        valid_buried_spawns = []
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                if self.floor[x, y].tile_type is tile.TileType.PRIMARY:
                    valid_buried_spawns.append((x, y))
        return valid_buried_spawns

    def spawn_stairs(self, position):
        self.floor.stairs_spawn = position

    def spawn_item(self, position):
        self.floor[position].item_ptr = self.get_random_item()

    def spawn_trap(self, position):
        self.floor[position].trap = self.get_random_trap()

    def fill_floor_with_spawns(self):
        valid_spawns = self.floor.get_valid_spawn_locations()
        self.random.shuffle(valid_spawns)
        # Stairs
        self.spawn_stairs(valid_spawns[-1])
        valid_spawns.pop()
        # Traps
        num_traps = self.get_number_of_traps()
        for _ in range(num_traps):
            self.spawn_trap(valid_spawns[-1])
            valid_spawns.pop()
        # Items
        num_items = self.get_number_of_items(self.data.item_density)
        for _ in range(num_items):
            self.spawn_item(valid_spawns[-1])
            valid_spawns.pop()
        # Buried Items
        valid_spawns = self.get_valid_buried_spawn_locations()
        self.random.shuffle(valid_spawns)
        num_items = self.get_number_of_items(self.data.buried_item_density)
        for _ in range(num_items):
            self.spawn_item(valid_spawns[-1])
            valid_spawns.pop()
        # TODO: Shop
        # Characters
        self.spawn_party()
        self.spawn_enemies()

    def spawn_pokemon(self, p: pokemon.Pokemon, position: tuple[int, int]):
        self.floor[position].pokemon_ptr = p
        p.spawn(position)
        self.floor.spawned.append(p)

    def spawn_party(self):
        valid_spawns = self.get_valid_spawn_locations()
        self.random.shuffle(valid_spawns)
        self.spawn_pokemon(self.party.leader, valid_spawns[-1])
        valid_spawns.pop()

        leader_x, leader_y = self.party.leader.position
        
        for member in self.party:
            if member is self.party.leader:
                continue
            # TODO Improve party spawn algorithm
            for d in direction.Direction:
                position = (d.x + leader_x, d.y + leader_y)
                if self.floor.is_valid_spawn_location(position):
                    self.spawn_pokemon(member, position)
                    break

        self.floor.party = self.party

    def spawn_enemies(self):
        valid_spawns = self.get_valid_spawn_locations()
        self.random.shuffle(valid_spawns)
        for _ in range(self.data.initial_enemy_density):
            enemy = pokemon.EnemyPokemon(*self.data.get_random_pokemon())
            self.spawn_pokemon(enemy, valid_spawns[-1])
            valid_spawns.pop()
            self.floor.active_enemies.append(enemy)

    def get_number_of_items(self, density) -> int:
        if density != 0:
            return max(1, self.random.randrange(density-2, density+2))
        return 0
    
    def get_number_of_traps(self):
        n = self.data.trap_density
        return self.random.randint(n//2, n)

    def get_random_item(self):
        return None

    def get_random_trap(self):
        return self.data.get_random_trap()
