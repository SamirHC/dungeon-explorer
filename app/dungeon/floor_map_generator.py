from app.common.utils import clamp
from app.dungeon.floor_map_builder import FloorMapBuilder
from app.dungeon.floor_data import FloorData
from app.common.direction import Direction
from app.dungeon.grid_cell import Grid, Cell
from app.dungeon.tile_type import TileType

from random import Random


class FloorMapGenerator:
    """
    A class that can generate the floor structures such as rooms, hallways and 
    lakes.
    """

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

    def _is_tile_type(self, x: int, y: int, tile_type: TileType) -> bool:
        return self.floor[x, y].tile_type == tile_type

    def _is_primary_tile(self, x: int, y: int) -> bool:
        return self._is_tile_type(x, y, TileType.PRIMARY)
    
    def _is_secondary_tile(self, x: int, y: int) -> bool:
        return self._is_tile_type(x, y, TileType.SECONDARY)
    
    def _is_tertiary_tile(self, x: int, y: int) -> bool:
        return self._is_tile_type(x, y, TileType.TERTIARY)

    def _get_room_density_from_data(self) -> int:
        """
        Private method. Calculates room density value based on the value stored 
        in the FloorData object.
        A negative room_density is interpreted as an exact value.
        Otherwise, some random value added.

        :return: Max number of cells to be rooms.
        """
        room_density = self.data.room_density
        if room_density < 0:
            room_density = -room_density
        else:
            room_density = room_density + self.random.randrange(0, 3)
        return room_density

    def assign_rooms(self):
        """
        Sets random cells in the grid to a room cell.
        """
        valid_cells = self.grid.get_valid_cells()
        assert len(valid_cells) >= 2

        MIN_ROOMS = 2
        MAX_ROOMS = len(valid_cells)
        room_density = clamp(MIN_ROOMS, self._get_room_density_from_data(),
                             MAX_ROOMS)

        self.random.shuffle(valid_cells)
        for _ in range(room_density):
            valid_cells.pop().is_room = True

    def create_rooms(self):
        room_number = 1
        for cell in self.grid.get_valid_cells():
            x, y = cell.get_xy()

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
        position = self.random.choice([cell.get_xy() for cell in self.grid.get_valid_cells()])
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
            for cell in self.grid.get_valid_cells():
                if cell.is_room:
                    continue
                if len(cell.connections) == 1:
                    checking_dead_ends = True
                    self.connect_cell(cell.get_xy())

    def create_hallways(self):
        seen = []
        for cell in self.grid.get_valid_cells():
            for d in cell.connections:
                if (cell, d) in seen:
                    continue
                self.create_hallway(cell.get_xy(), d)
                seen.append((cell, d))
                dx, dy = d.value
                seen.append((self.grid[cell.x+dx, cell.y+dy], d.flip()))

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
                if self._is_tertiary_tile(cur_x, cur_y):
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                if cur_y >= y1:
                    cur_y -= 1
                else:
                    cur_y += 1
            while cur_x != x1:
                if self._is_tertiary_tile(cur_x, cur_y):
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
                if self._is_tertiary_tile(cur_x, cur_y):
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                if cur_x >= x1:
                    cur_x -= 1
                else:
                    cur_x += 1
            while cur_y != y1:
                if self._is_tertiary_tile(cur_x, cur_y):
                    return
                self.floor[cur_x, cur_y].hallway_tile()
                cur_y += dy

    def merge_rooms(self):
        MERGE_CHANCE = 5
        for cell in self.grid.get_valid_cells():
            if cell.is_merged:
                continue
            if not cell.is_room:
                continue
            if not cell.is_connected:
                continue
            if not (self.random.randrange(100) < MERGE_CHANCE):
                continue
            d = self.random.choice(list(cell.connections))
            dx, dy = d.value
            other_cell = self.grid[cell.x+dx, cell.y+dy]
            if other_cell.is_merged:
                continue
            if not other_cell.is_room:
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
        for cell in self.grid.get_valid_cells():
            if cell.is_connected:
                continue
            if cell.is_merged:
                continue
            if cell.is_room:
                self.connect_cell(cell.get_xy())
                for d in cell.connections:
                    self.create_hallway(cell.get_xy(), d)
            else:
                self.floor[cell.start_x, cell.start_y].reset()

    def create_shop(self):
        if not self.data.shop or not (self.random.randrange(100) < self.data.shop):
            return
        
        valid_shop_cells = list(filter(
            lambda c: c.is_room and c.is_connected and not c.is_merged and not c.secondary,
            list(self.grid.get_valid_cells())
        ))
        if not valid_shop_cells:
            return
        
        cell = self.random.choice(valid_shop_cells)
        self.floor.has_shop = True
        room_number = self.floor[cell.start_x, cell.start_y].room_index
        for x in range(cell.start_x+1, cell.end_x-1):
            for y in range(cell.start_y+1, cell.end_y-1):
                self.floor[x, y].shop_tile(room_number)
    
    def _find_extra_hallway_start(self) -> tuple[int, int, Direction]:
        # Select a random valid cell
        valid_cells = [c for c in self.grid.get_valid_cells()
                        if c.is_connected and c.is_room]
        cell = self.random.choice(valid_cells)

        # Starting position in cell
        cur_x = self.random.randrange(cell.start_x, cell.end_x)
        cur_y = self.random.randrange(cell.start_y, cell.end_y)

        # Get direction of travel from starting position
        d = self.random.choice(self.grid.get_valid_directions_from_cell(cell.x, cell.y))
        dx, dy = d.value

        # Walk to out of room to first non-ground tile 
        while self.floor.is_room((cur_x, cur_y)) or self._is_tertiary_tile(cur_x, cur_y):
            cur_x += dx
            cur_y += dy
        
        return cur_x, cur_y, d

    def _has_perpendicular_tertiary_tile(self, x: int, y: int, d: Direction) -> bool:
        # Check tiles perpendicular to direction from current
        d_cw = d.clockwise().clockwise()
        d_acw = d.anticlockwise().anticlockwise()

        return self._is_tertiary_tile(x + d_cw.x, y + d_cw.y) or self._is_tertiary_tile(x + d_acw.x, y + d_acw.y)
    
    def _is_valid_extra_hallway_start(self, x0: int, y0: int, d: Direction) -> bool:
        result = True
        # Check if 5x5 surrounding area is in bounds
        result &= all(self.floor.in_bounds((x, y))
                             for x in range(x0 - 2, x0 + 3)
                             for y in range(y0 - 2, y0 + 3))
        result &= not self._has_perpendicular_tertiary_tile(x0, y0, d)
        return result
    
    def create_extra_hallway(self):
        cur_x, cur_y, d = self._find_extra_hallway_start()
        if not self._is_valid_extra_hallway_start(cur_x, cur_y, d):
            return

        # Start extra hallway generation
        segment_length = self.random.randrange(3, 6)
        while True:
            # Stop if:
            if cur_x <= 1 or cur_y <= 1 or self.floor.WIDTH - 2 <= cur_x or self.floor.HEIGHT - 2 <= cur_y:
                break
            if self._is_tertiary_tile(cur_x, cur_y):
                break
            if any((all(self._is_tertiary_tile(cur_x + d.x, cur_y + d.y) 
                       for d in [Direction.NORTH, Direction.NORTH_EAST, Direction.EAST]),
                   all(self._is_tertiary_tile(cur_x + d.x, cur_y + d.y)
                       for d in [Direction.NORTH, Direction.NORTH_WEST, Direction.WEST]),
                   all(self._is_tertiary_tile(cur_x + d.x, cur_y + d.y)
                       for d in [Direction.SOUTH, Direction.SOUTH_EAST, Direction.EAST]),
                   all(self._is_tertiary_tile(cur_x + d.x, cur_y + d.y)
                       for d in [Direction.SOUTH, Direction.SOUTH_WEST, Direction.WEST]))):
                break

            # Turn into hallway
            self.floor[cur_x, cur_y].hallway_tile()
            # Check tiles perpendicular to direction from current
            if self._has_perpendicular_tertiary_tile(cur_x, cur_y, d):
                break
            # Iteration counter
            segment_length -= 1
            # Change direction on end of segment
            if segment_length == 0:
                segment_length = self.random.randrange(3, 6)
                d = self.random.choice((d.clockwise().clockwise(),
                                        d.anticlockwise().anticlockwise()))
                # Exit if out of soft-bounds
                if cur_x >= 32 and self.grid.floor_size == 1 and d is Direction.EAST:
                    break
                if cur_x >= 48 and self.grid.floor_size == 2 and d is Direction.EAST:
                    break
            # Update curs
            cur_x += d.x
            cur_y += d.y

    def create_extra_hallways(self):
        for _ in range(self.data.extra_hallway_density):
            self.create_extra_hallway()
    
    def generate_river_lake(self, x: int, y: int):
        MIN_X, MAX_X = 2, self.floor.WIDTH - 2
        MIN_Y, MAX_Y = 2, self.floor.HEIGHT - 2

        is_in_bounds = lambda x, y: MIN_X <= x < MAX_X and MIN_Y <= y < MAX_Y 

        x0, x1 = x - 3, x + 4
        y0, y1 = y - 3, y + 4
        valid_secondary_positions = list((x, y)
                                         for x in range(x0, x1) for y in range(y0, y1)
                                         if is_in_bounds(x, y) and self._is_primary_tile(x, y))
        if not valid_secondary_positions:
            return
        
        to_secondary = []
        for _ in range(100):
            x, y = self.random.choice(valid_secondary_positions)
            if any(self._is_secondary_tile(x + d.x, y + d.y) for d in Direction):
                to_secondary.append((x, y))
        for x, y in valid_secondary_positions:
            sec_count = sum(1 for d in Direction if self._is_secondary_tile(x + d.x, y + d.y))
            if sec_count >= 4:
                to_secondary.append((x, y))

        self.floor_map_builder.set_secondary(to_secondary)
    
    def generate_lake(self):
        MIN_X, MAX_X = 2, self.floor.WIDTH - 2
        MIN_Y, MAX_Y = 2, self.floor.HEIGHT - 2

        is_border = lambda x, y: x==x0 or y==y0 or x==x1-1 or y==y1-1
        is_in_bounds = lambda x, y: MIN_X <= x < MAX_X and MIN_Y <= y < MAX_Y

        cx = self.random.randrange(MIN_X, MAX_X)
        cy = self.random.randrange(MIN_Y, MAX_Y)
        x0, x1 = cx - 5, cx + 5
        y0, y1 = cy - 5, cy + 5

        wet = {(x, y): not is_border(x, y) and is_in_bounds(x, y)
               for x in range(x0, x1)
               for y in range(y0, y1)}
        
        for _ in range(80):
            x = self.random.randrange(x0+1, x1-1)
            y = self.random.randrange(y0+1, y1-1)
            wet[x, y] = all(wet[x + d.x, y + d.y] 
                            for d in Direction.get_cardinal_directions())

        to_secondary = [xy for xy in wet if wet[xy] and self._is_primary_tile(*xy)]
        self.floor_map_builder.set_secondary(to_secondary)

    def get_river_path(self) -> list[tuple[int, int]]:
        MIN_X, MAX_X = 2, self.floor.WIDTH - 2
        MIN_Y, MAX_Y = 2, self.floor.HEIGHT - 2
        NUM_SECTIONS = 20

        x = self.random.randrange(MIN_X, MAX_X)
        d, y = self.random.choice(
            ((Direction.NORTH, MAX_Y - 1), (Direction.SOUTH, MIN_Y)))
        D0 = d

        xys = []
        for _ in range(NUM_SECTIONS):
            for _ in range(self.random.randrange(2, 8)):
                xys.append((x, y))
                x = clamp(MIN_X, x + d.x, MAX_X - 1)
                y = clamp(MIN_Y, y + d.y, MAX_Y - 1)
            d = D0 if d.is_horizontal() else self.random.choice((Direction.EAST, Direction.WEST))
        return xys
    
    def generate_river(self):
        lake_at = self.random.randrange(10, 60)
        to_secondary = []
        for x, y in self.get_river_path():
            if self._is_secondary_tile(x, y):
                break
            if self._is_primary_tile(x, y):
                to_secondary.append((x, y))
            lake_at -= 1
            if lake_at == 0:
                self.generate_river_lake(x, y)
        
        self.floor_map_builder.set_secondary(to_secondary)

    def generate_secondary(self):
        NUM_RIVERS = self.random.randrange(1, 4)
        for _ in range(NUM_RIVERS):
            self.generate_river()
        for _ in range(self.data.water_density):
            self.generate_lake()

    def is_strongly_connected(self) -> bool:
        """
        Does an iterative depth first search traversal of the cells to check if 
        they are strongly connected, i.e. all valid cells can reach every other 
        valid cell.

        :return: Returns whether valid cells are strongly connected.
        """
        valid_cells = self.grid.get_valid_cells()
        assert valid_cells

        visited = set()
        dfs_stack = [valid_cells[0]]
        
        while dfs_stack:
            cell = dfs_stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            for d in cell.connections:
                other = self.grid.get_adjacent_cell(cell, d)
                if other not in visited:
                    dfs_stack.append(other)
        
        return all(not cell.is_connected or cell in visited for cell in valid_cells)
