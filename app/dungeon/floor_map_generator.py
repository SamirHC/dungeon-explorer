from app.dungeon.floor_map_builder import FloorMapBuilder
from app.dungeon.floor_data import FloorData
from app.common.direction import Direction
from app.dungeon import tile
import app.dungeon.tile_type

from random import Random

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
    
class Grid:
    def __init__(self, size: tuple[int, int], xs: [int], ys: [int], floor_size: int=0):
        self.size = size
        self.w, self.h = size
        self.xs = xs
        self.ys = ys
        self.floor_size = floor_size
        self.cells = {
            (x, y): Cell() for x in range(self.w) for y in range(self.h)
        }

        for x in range(self._get_max_cell_x()):
            for y in range(self.h):
                self.set_valid_cell((x, y))
    
    def __getitem__(self, xy: tuple[int, int]) -> Cell:
        return self.cells[xy]
    
    def _get_max_cell_x(self):
        max_x = self.w
        if self.floor_size == 1:
            max_x = self.w // 2
        elif self.floor_size == 2:
            max_x = (self.w * 3) // 4
        return max_x
    
    def set_valid_cell(self, xy):
        self[xy].valid_cell = True

class FloorMapGenerator:
    def __init__(self, data: FloorData, random: Random):
        self.data = data
        self.random = random

        self.floor_map_builder = FloorMapBuilder()
        self.floor = self.floor_map_builder.floor
        self.grid: Grid = None
    
    def reset(self):
        self.floor_map_builder.reset()

    def init_grid(self, size: (int, int), xs: [int], ys: [int], floor_size: int=0):
        self.grid = Grid(size, xs, ys, floor_size)

    def assign_rooms(self):
        room_density = self.data.room_density
        if room_density < 0:
            room_density = -room_density
        else:
            room_density = room_density + self.random.randrange(0, 3)

        rooms_ok = [(i < room_density) for i in range(len(self.grid.cells))]
        while True:
            self.random.shuffle(rooms_ok)
            placed = 0
            for i, cell in enumerate(self.grid.cells.values()):
                if not cell.valid_cell:
                    continue
                if rooms_ok[i]:
                    cell.is_room = True
                    placed += 1
            if placed >= 2:
                return

    def create_rooms(self):
        room_number = 1
        for (x, y), cell in self.grid.cells.items():
            if not cell.valid_cell:
                continue
            x0, x1 = self.grid.xs[x:x+2]
            y0, y1 = self.grid.ys[y:y+2]
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
        position = self.random.choice([p for p, cell in self.grid.cells.items() if cell.valid_cell])
        for _ in range(self.data.floor_connectivity):
            position = self.connect_cell(position)
        self.remove_dead_ends()

    def connect_cell(self, position: tuple[int, int]):
        x, y = position
        ds: list[Direction] = []
        if x != 0:
            ds.append(Direction.WEST)
        if x != self.grid.w-1 and self.grid[x+1, y].valid_cell:
            ds.append(Direction.EAST)
        if y != 0:
            ds.append(Direction.NORTH)
        if y != self.grid.h-1 and self.grid[x, y+1].valid_cell:
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
            for p, cell in self.grid.cells.items():
                if not cell.valid_cell or cell.is_room:
                    continue
                if len(cell.connections) == 1:
                    checking_dead_ends = True
                    self.connect_cell(p)

    def create_hallways(self):
        seen = []
        for (x, y), cell in self.grid.cells.items():
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
                border = self.grid.xs[x+1]-1
            else:
                border = self.grid.xs[x]
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
                border = self.grid.ys[y+1]-1
            else:
                border = self.grid.ys[y]
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
        MERGE_CHANCE = 5
        for (x, y), cell in self.grid.cells.items():
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
            if not (self.random.randrange(100) < MERGE_CHANCE):
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
        for (x, y), cell in self.grid.cells.items():
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
        grid_items = [item for item in self.grid.cells.items()]
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
            x = self.random.randrange(self.grid.w)
            y = self.random.randrange(self.grid.h)
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
            if x != self.grid.w-1:
                ds.append(Direction.EAST)
            if y != 0:
                ds.append(Direction.NORTH)
            if y != self.grid.h-1:
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
                    if cur_x >= 32 and self.grid.floor_size == 1 and d is Direction.EAST:
                        break
                    if cur_x >= 48 and self.grid.floor_size == 2 and d is Direction.EAST:
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
        for (x, y), cell in self.grid.cells.items():
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
        for (x, y), cell in self.grid.cells.items():
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
