from app.common.direction import Direction
from app.db import tileset_db
from app.dungeon import floor_data, floor_map_builder, floor_status, tile
import app.dungeon.tile_type
from app.dungeon.structure import Structure
from app.dungeon.floor import Floor
from app.pokemon.party import Party
from app.dungeon.spawner import Spawner


import random


class FloorBuilder:
    MERGE_CHANCE = 5

    def __init__(self, data: floor_data.FloorData, party: Party, seed: int):
        self.data = data
        self.party = party
        self.floor_size = 0
        self.floor_map_builder = floor_map_builder.FloorMapBuilder()
        self.floor = self.floor_map_builder.floor
        self.random = random.Random(seed)
        self.spawner = Spawner(self.floor, self.party, self.data, self.random)

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
            self.connections: set[Direction] = set()
            self.imperfect = False
            self.secondary = False

    def build_floor(self) -> Floor:
        self.build_floor_structure()
        self.spawner.fill_floor_with_spawns()
        self.floor.status = floor_status.FloorStatus(
            self.data.darkness_level,
            self.data.weather
        )
        return self.floor

    def build_floor_structure(self) -> Floor:
        if self.data.fixed_floor_id != "0":
            return self.build_fixed_floor()

        while True:
            self.floor_map_builder.reset()

            self.generate_floor_structure()
            if self.is_strongly_connected():
                break
            print("Restarting...")
        self.set_tile_masks()
        self.floor.tileset = tileset_db[self.data.tileset]
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
            self.connect_cell_in_direction((x, 0), Direction.EAST)
            self.connect_cell_in_direction((x, 3), Direction.EAST)
        for y in range(3):
            self.connect_cell_in_direction((0, y), Direction.SOUTH)
            self.connect_cell_in_direction((5, y), Direction.SOUTH)
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
                self.connect_cell_in_direction((x, y), Direction.SOUTH)
        for x in range(4):
            for y in range(1, 3):
                self.connect_cell_in_direction((x, y), Direction.EAST)
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
            self.connect_cell_in_direction((x, 1), Direction.EAST)
        for y in range(2):
            self.connect_cell_in_direction((1, y), Direction.SOUTH)
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
                self.connect_cell_in_direction((x, y), Direction.EAST)
        for y in range(2):
            self.connect_cell_in_direction((1, y), Direction.SOUTH)
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

                self.floor_map_builder.set_rect_room(
                    (cell.start_x, cell.start_y), (w, h), room_number)
                
                cell.imperfect = self.random.randrange(100) < self.data.imperfect_rooms
                cell.secondary = self.random.randrange(100) < self.data.secondary_percentage
                room_number += 1
            else:  # Dummy room
                cell.start_x = self.random.randrange(x0+2, x1-2)
                cell.start_y = self.random.randrange(y0+2, y1-2)
                cell.end_x = cell.start_x + 1
                cell.end_y = cell.start_y + 1

                self.floor_map_builder.set_hallway(
                    [(cell.start_x, cell.start_y)]
                )

    def connect_cells(self):
        position = self.random.choice([p for p, cell in self.grid.items() if cell.valid_cell])
        for _ in range(self.data.floor_connectivity):
            position = self.connect_cell(position)
        self.remove_dead_ends()

    def connect_cell(self, position: tuple[int, int]):
        x, y = position
        ds: list[Direction] = []
        if x != 0:
            ds.append(Direction.WEST)
        if x != self.grid_size[0]-1 and self.grid[x+1, y].valid_cell:
            ds.append(Direction.EAST)
        if y != 0:
            ds.append(Direction.NORTH)
        if y != self.grid_size[1]-1 and self.grid[x, y+1].valid_cell:
            ds.append(Direction.SOUTH)
        d = self.random.choice(ds)
        dx, dy = d.value
        self.connect_cell_in_direction(position, d)
        return x+dx, y+dy

    def connect_cell_in_direction(self, position: tuple[int, int], d: Direction):
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

    def create_hallway(self, cell_position: tuple[int, int], d: Direction):
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
            if d is Direction.EAST:
                border = self.grid_xs[x+1]-1
            else:
                border = self.grid_xs[x]
            while cur_x != border:
                if not self.floor[cur_x, cur_y].room_index:
                    self.floor[cur_x, cur_y].hallway_tile()
                cur_x += dx
            while cur_y != y1:
                if self.floor[cur_x, cur_y].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                if cur_y >= y1:
                    cur_y -= 1
                else:
                    cur_y += 1
            while cur_x != x1:
                if self.floor[cur_x, cur_y].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                cur_x += dx
        elif d.is_vertical():
            if d is Direction.SOUTH:
                border = self.grid_ys[y+1]-1
            else:
                border = self.grid_ys[y]
            while cur_y != border:
                if not self.floor[cur_x, cur_y].room_index:
                    self.floor[cur_x, cur_y].hallway_tile()
                cur_y += dy
            while cur_x != x1:
                if self.floor[cur_x, cur_y].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                if cur_x >= x1:
                    cur_x -= 1
                else:
                    cur_x += 1
            while cur_y != y1:
                if self.floor[cur_x, cur_y].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
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
            ds: list[Direction] = []
            if x != 0:
                ds.append(Direction.WEST)
            if x != self.grid_size[0]-1:
                ds.append(Direction.EAST)
            if y != 0:
                ds.append(Direction.NORTH)
            if y != self.grid_size[1]-1:
                ds.append(Direction.SOUTH)
            d = self.random.choice(ds)
            dx, dy = d.value

            # Walk to room edge
            cur_x, cur_y = x0, y0
            while self.floor[cur_x, cur_y].room_index:
                cur_x += dx
                cur_y += dy

            # Walk to non-ground tile
            while self.floor[cur_x, cur_y].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
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
            if self.floor[cur_x + dx_cw, cur_y + dy_cw].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                continue
            d_acw = d.anticlockwise().anticlockwise()
            dx_acw, dy_acw = d_acw.value
            if self.floor[cur_x + dx_acw, cur_y + dy_acw].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                continue

            # Start extra hallway generation
            segment_length = self.random.randrange(3, 6)
            while True:
                # Stop if:
                if cur_x <= 1 or cur_y <= 1 or self.floor.WIDTH - 2 <= cur_x or self.floor.HEIGHT - 2 <= cur_y:
                    break
                if self.floor[cur_x, cur_y].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is app.dungeon.tile_type.TileType.TERTIARY
                    for d in [
                        Direction.NORTH,
                        Direction.NORTH_EAST,
                        Direction.EAST
                        ]
                    ]
                ):
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is app.dungeon.tile_type.TileType.TERTIARY
                    for d in [
                        Direction.NORTH,
                        Direction.NORTH_WEST,
                        Direction.WEST
                        ]
                    ]
                ):
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is app.dungeon.tile_type.TileType.TERTIARY
                    for d in [
                        Direction.SOUTH,
                        Direction.SOUTH_EAST,
                        Direction.EAST
                        ]
                    ]
                ):
                    break
                if all(
                    [self.floor[cur_x + d.x, cur_y + d.y].tile_type is app.dungeon.tile_type.TileType.TERTIARY
                    for d in [
                        Direction.SOUTH,
                        Direction.SOUTH_WEST,
                        Direction.WEST
                        ]
                    ]
                ):
                    break

                # Turn into hallway
                self.floor[cur_x, cur_y].hallway_tile()
                # Check tiles perpendicular to direction from current
                d_cw = d.clockwise().clockwise()
                dx_cw, dy_cw = d_cw.value
                if self.floor[cur_x + dx_cw, cur_y + dy_cw].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
                    break
                d_acw = d.anticlockwise().anticlockwise()
                dx_acw, dy_acw = d_acw.value
                if self.floor[cur_x + dx_acw, cur_y + dy_acw].tile_type is app.dungeon.tile_type.TileType.TERTIARY:
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
                    if cur_x >= 32 and self.floor_size == 1 and d is Direction.EAST:
                        break
                    if cur_x >= 48 and self.floor_size == 2 and d is Direction.EAST:
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
        for d in Direction.get_cardinal_directions():
            d_pos = x + d.x, y + d.y
            if self.floor.is_tertiary(d_pos) and not self.floor.is_room(d_pos):
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
                d = Direction.NORTH
                y = MAX_HEIGHT
            else:
                d = Direction.SOUTH
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
                    if self.floor[x, y].tile_type is app.dungeon.tile_type.TileType.SECONDARY:
                        end = True
                        break
                    if self.floor[x, y].tile_type is app.dungeon.tile_type.TileType.PRIMARY:
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
                        if self.floor[cx, cy].tile_type is not app.dungeon.tile_type.TileType.PRIMARY:
                            continue
                        for cd in Direction:
                            if self.floor[cx + cd.x, cy + cd.y].tile_type is app.dungeon.tile_type.TileType.SECONDARY:
                                self.floor[cx, cy].secondary_tile()
                                break
                    for i in range(-3, 4):
                        for j in range(-3, 4):
                            sec_count = 0
                            if not (MIN_WIDTH <= x+i <= MAX_WIDTH and MIN_HEIGHT <= y+j <= MAX_HEIGHT):
                                continue
                            if self.floor[x+i, y+j].tile_type is not app.dungeon.tile_type.TileType.PRIMARY:
                                continue
                            for cd in Direction:
                                if self.floor[x+i+cd.x, y+j+cd.y].tile_type is app.dungeon.tile_type.TileType.SECONDARY:
                                    sec_count += 1
                                if sec_count == 4:
                                    self.floor[x + i, y + j].secondary_tile()
                                    break
                if not end:
                    if d.is_horizontal():
                        d = d0
                    else:
                        if self.random.randrange(100) < 50:
                            d = Direction.EAST
                        else:
                            d = Direction.WEST
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
                for d in Direction.get_cardinal_directions():
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
                    if self.floor[pos_x, pos_y].tile_type is app.dungeon.tile_type.TileType.PRIMARY:
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
                Direction.NORTH_WEST,
                Direction.NORTH,
                Direction.NORTH_EAST,
                Direction.WEST,
                Direction.EAST,
                Direction.SOUTH_WEST,
                Direction.SOUTH,
                Direction.SOUTH_EAST,
            ]:
                other_tile = self.floor[x+d.x, y+d.y]
                is_same = this_tile.tile_type is other_tile.tile_type
                mask.append(is_same)
                if d.is_cardinal():
                    cardinal_mask.append(is_same)
            this_tile.tile_mask = tile.value(tuple(mask))
            this_tile.cardinal_tile_mask = tile.value(tuple(cardinal_mask))
