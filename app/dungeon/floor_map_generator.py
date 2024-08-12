import random

from app.common.constants import RNG
from app.common.utils import clamp
from app.common.direction import Direction
from app.dungeon.floor_map_builder import FloorMapBuilder
from app.dungeon.floor_data import FloorData
from app.dungeon.grid_cell import Grid, Cell
from app.dungeon.tile_type import TileType


class FloorMapGenerator(FloorMapBuilder):
    """
    A class that can generate the floor structures such as rooms, hallways and
    lakes.
    """

    def __init__(self, data: FloorData, generator: random.Random = RNG):
        super().__init__()
        self.data = data
        self.generator = generator

        self.grid: Grid = None

    def init_grid(
        self, size: tuple[int, int], xs: list[int], ys: list[int], floor_size: int = 0
    ):
        self.grid = Grid(size, xs, ys, floor_size)

    def _is_tile_type(self, x: int, y: int, tile_type: TileType) -> bool:
        return self.floor[x, y].tile_type == tile_type

    def _is_primary_tile(self, x: int, y: int) -> bool:
        return self._is_tile_type(x, y, TileType.PRIMARY)

    def _is_secondary_tile(self, x: int, y: int) -> bool:
        return self._is_tile_type(x, y, TileType.SECONDARY)

    def _is_tertiary_tile(self, x: int, y: int) -> bool:
        return self._is_tile_type(x, y, TileType.TERTIARY)

    def reset(self):
        super().reset()
        self.grid = None

    def assign_rooms(self):
        """
        Sets random cells in the grid to a room cell.
        """
        valid_cells = self.grid.get_valid_cells()
        assert len(valid_cells) >= 2

        MIN_ROOMS = 2
        MAX_ROOMS = len(valid_cells)
        room_density = clamp(
            MIN_ROOMS, self.data.get_room_density_value(self.generator), MAX_ROOMS
        )

        self.generator.shuffle(valid_cells)
        for _ in range(room_density):
            valid_cells.pop().is_room = True

    def create_rooms(self):
        room_number = 1
        for cell in self.grid.get_valid_cells():
            x, y = cell.get_xy()

            x0, x1 = self.grid.xs[x : x + 2]
            y0, y1 = self.grid.ys[y : y + 2]
            max_w = x1 - x0 - 3
            max_h = y1 - y0 - 3

            if cell.is_room:
                w = self.generator.randrange(5, max_w)
                h = self.generator.randrange(4, max_h)
                w = min(w, h * 3 // 2)
                h = min(h, w * 3 // 2)
                cell.start_x = self.generator.randrange(max_w - w) + x0 + 2
                cell.start_y = self.generator.randrange(max_h - h) + y0 + 2
                cell.end_x = cell.start_x + w
                cell.end_y = cell.start_y + h

                self.set_rect_room((cell.start_x, cell.start_y), (w, h), room_number)

                cell.imperfect = (
                    self.generator.randrange(100) < self.data.imperfect_rooms
                )
                cell.secondary = (
                    self.generator.randrange(100) < self.data.secondary_percentage
                )
                room_number += 1
            else:  # Dummy room
                cell.start_x = self.generator.randrange(x0 + 2, x1 - 2)
                cell.start_y = self.generator.randrange(y0 + 2, y1 - 2)
                cell.end_x = cell.start_x + 1
                cell.end_y = cell.start_y + 1

                self.set_hallway([(cell.start_x, cell.start_y)])

    def connect_cells(self):
        position = self.generator.choice(
            [cell.get_xy() for cell in self.grid.get_valid_cells()]
        )
        for _ in range(self.data.floor_connectivity):
            position = self.connect_cell(position)
        if not self.data.dead_ends:
            self.remove_dead_ends()

    def connect_cell(self, position: tuple[int, int]):
        x, y = position
        ds: list[Direction] = []
        if x != 0:
            ds.append(Direction.WEST)
        if x != self.grid.w - 1 and self.grid[x + 1, y].valid_cell:
            ds.append(Direction.EAST)
        if y != 0:
            ds.append(Direction.NORTH)
        if y != self.grid.h - 1 and self.grid[x, y + 1].valid_cell:
            ds.append(Direction.SOUTH)
        d = self.generator.choice(ds)
        self.connect_cell_in_direction(position, d)
        return x + d.x, y + d.y

    def connect_cell_in_direction(self, position: tuple[int, int], d: Direction):
        x, y = position
        self.grid[x, y].connections.add(d)
        self.grid[x + d.x, y + d.y].connections.add(d.flip())

    def remove_dead_ends(self):
        dead_end_cells = (
            c
            for c in self.grid.get_valid_cells()
            if not c.is_room and c.connections == 1
        )
        for dead_end_cell in dead_end_cells:
            self.connect_cell(dead_end_cell.get_xy())

    def create_hallways(self):
        # Guarateed to get distinct connections since we skip the 'opposite'
        connections = (
            (cell, d)
            for cell in self.grid.get_valid_cells()
            for d in cell.connections
            if d in (Direction.EAST, Direction.SOUTH)
        )
        for cell, d in connections:
            self.create_hallway(cell, d)

    def create_hallway(self, cell: Cell, d: Direction):
        other_cell = self.grid.get_adjacent_cell(cell, d)

        cell.is_connected = True
        other_cell.is_connected = True

        x0, y0 = cell.get_random_xy_in_room(self.generator)
        x1, y1 = other_cell.get_random_xy_in_room(self.generator)

        if d.is_horizontal():
            xm = self.grid.xs[cell.x + (d is Direction.EAST)]

            min_x, max_x = min(x0, xm), max(x0, xm) + 1
            self.set_hallway([(x, y0) for x in range(min_x, max_x)])

            min_y, max_y = min(y0, y1), max(y0, y1) + 1
            self.set_hallway([(xm, y) for y in range(min_y, max_y)])

            min_x, max_x = min(xm, x1), max(xm, x1) + 1
            self.set_hallway([(x, y1) for x in range(min_x, max_x)])
        elif d.is_vertical():
            ym = self.grid.ys[cell.y + (d is Direction.SOUTH)]

            min_y, max_y = min(y0, ym), max(y0, ym) + 1
            self.set_hallway([(x0, y) for y in range(min_y, max_y)])

            min_x, max_x = min(x0, x1), max(x0, x1) + 1
            self.set_hallway([(x, ym) for x in range(min_x, max_x)])

            min_y, max_y = min(ym, y1), max(ym, y1) + 1
            self.set_hallway([(x1, y) for y in range(min_y, max_y)])

    def merge_rooms(self):
        MERGE_CHANCE = 5
        cells = (
            cell
            for cell in self.grid.get_valid_cells()
            if cell.is_room and cell.is_connected
        )
        for cell in cells:
            d = self.generator.choice(list(cell.connections))
            other_cell = self.grid.get_adjacent_cell(cell, d)
            valid_merge = (
                not (cell.is_merged or other_cell.is_merged) and other_cell in cells
            )
            if valid_merge and self.generator.randrange(100) < MERGE_CHANCE:
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
        isolated_cells = (
            cell
            for cell in self.grid.get_valid_cells()
            if not cell.is_connected and not cell.is_merged
        )
        for cell in isolated_cells:
            if cell.is_room:
                self.connect_cell(cell.get_xy())
                for d in cell.connections:
                    self.create_hallway(cell, d)
            else:
                self.floor[cell.start_x, cell.start_y].reset()

    def create_shop(self):
        if not self.data.shop or not (self.generator.randrange(100) < self.data.shop):
            return

        valid_shop_cells = [
            c
            for c in self.grid.get_valid_cells()
            if c.is_room and c.is_connected and not c.is_merged and not c.secondary
        ]
        if not valid_shop_cells:
            return

        cell = self.generator.choice(valid_shop_cells)
        self.floor.has_shop = True
        room_number = self.floor[cell.start_x, cell.start_y].room_index
        for x in range(cell.start_x + 1, cell.end_x - 1):
            for y in range(cell.start_y + 1, cell.end_y - 1):
                self.floor[x, y].shop_tile(room_number)

    def _find_extra_hallway_start(self, cell: Cell) -> tuple[int, int, Direction]:
        cur_x = self.generator.randrange(cell.start_x, cell.end_x)
        cur_y = self.generator.randrange(cell.start_y, cell.end_y)
        d = self.generator.choice(
            self.grid.get_valid_directions_from_cell(cell.x, cell.y)
        )

        # Walk to out of room to first non-ground tile
        while self.floor.is_room((cur_x, cur_y)) or self._is_tertiary_tile(
            cur_x, cur_y
        ):
            cur_x += d.x
            cur_y += d.y

        return cur_x, cur_y, d

    def _has_perpendicular_tertiary_tile(self, x: int, y: int, d: Direction) -> bool:
        d_cw = d.clockwise90()
        d_acw = d.anticlockwise90()
        return self._is_tertiary_tile(x + d_cw.x, y + d_cw.y) or self._is_tertiary_tile(
            x + d_acw.x, y + d_acw.y
        )

    def _is_valid_extra_hallway_start(self, x0: int, y0: int, d: Direction) -> bool:
        # Check if 5x5 surrounding area is in bounds
        return all(
            self.floor.in_bounds((x, y))
            for x in range(x0 - 2, x0 + 3)
            for y in range(y0 - 2, y0 + 3)
        ) and not self._has_perpendicular_tertiary_tile(x0, y0, d)

    def _will_form_2x2_tertiary(self, x, y):
        """
        Private method. Used in hallway generation to ensure that hallways do
        not create hallways of width greater that 1.

        :param x: X coordinate of floor tile.
        :param y: Y coordinate of floor tile.
        :return:  True iff placing a tertiary tile at (x, y) will create a 2x2
                  area of tertiary tiles.
        """
        return any(
            all(
                self._is_tertiary_tile(x + d.x, y + d.y)
                for d in (dd, dd.clockwise(), dd.anticlockwise())
            )
            for dd in Direction.get_diagonal_directions()
        )

    def create_extra_hallway(self, cell: Cell):
        """
        Attempts to create an extra hallway starting from the provided cell.

        :param cell: The grid cell to start creating the extra hallway from.
        """
        x, y, d = self._find_extra_hallway_start(cell)
        if not self._is_valid_extra_hallway_start(x, y, d):
            return

        MAX_X = (
            32
            if self.grid.floor_size == 1
            else 48 if self.grid.floor_size == 2 else self.floor.WIDTH - 2
        )
        MAX_Y = self.floor.HEIGHT - 2
        in_bounds = lambda x, y: 2 <= x < MAX_X and 2 <= y < MAX_Y

        segment_length = self.generator.randrange(3, 6)
        while (
            in_bounds(x, y)
            and not self._is_tertiary_tile(x, y)
            and not self._will_form_2x2_tertiary(x, y)
        ):
            self.floor[x, y].tertiary_tile()
            segment_length -= 1
            if segment_length == 0:
                segment_length = self.generator.randrange(3, 6)
                d = self.generator.choice((d.clockwise90(), d.anticlockwise90()))
            x += d.x
            y += d.y

    def create_extra_hallways(self):
        for _ in range(self.data.extra_hallway_density):
            """
            We do not filter for valid cells immediately due to high hallway
            density values in the floor list data.
            """
            cell: Cell = self.generator.choice(self.grid.get_cells())

            if cell.valid_cell and cell.is_connected and cell.is_room:
                self.create_extra_hallway(cell)

    def generate_river_lake(self, x: int, y: int):
        MIN_X, MAX_X = 2, self.floor.WIDTH - 2
        MIN_Y, MAX_Y = 2, self.floor.HEIGHT - 2

        is_in_bounds = lambda x, y: MIN_X <= x < MAX_X and MIN_Y <= y < MAX_Y

        x0, x1 = x - 3, x + 4
        y0, y1 = y - 3, y + 4
        valid_secondary_positions = [
            (x, y)
            for x in range(x0, x1)
            for y in range(y0, y1)
            if is_in_bounds(x, y) and self._is_primary_tile(x, y)
        ]
        if not valid_secondary_positions:
            return

        to_secondary = []
        for _ in range(100):
            x, y = self.generator.choice(valid_secondary_positions)
            if any(self._is_secondary_tile(x + d.x, y + d.y) for d in Direction):
                to_secondary.append((x, y))

        num_adjacent_secondary = lambda x, y: sum(
            1 for d in Direction if self._is_secondary_tile(x + d.x, y + d.y)
        )
        to_secondary.extend(
            (
                (x, y)
                for x, y in valid_secondary_positions
                if num_adjacent_secondary(x, y) >= 4
            )
        )
        self.set_secondary(to_secondary)

    def generate_lake(self):
        MIN_X, MAX_X = 2, self.floor.WIDTH - 2
        MIN_Y, MAX_Y = 2, self.floor.HEIGHT - 2

        is_border = lambda x, y: x == x0 or y == y0 or x == x1 - 1 or y == y1 - 1
        is_in_bounds = lambda x, y: MIN_X <= x < MAX_X and MIN_Y <= y < MAX_Y

        cx = self.generator.randrange(MIN_X, MAX_X)
        cy = self.generator.randrange(MIN_Y, MAX_Y)
        x0, x1 = cx - 5, cx + 5
        y0, y1 = cy - 5, cy + 5

        wet = {
            (x, y): not is_border(x, y) and is_in_bounds(x, y)
            for x in range(x0, x1)
            for y in range(y0, y1)
        }

        for _ in range(80):
            x = self.generator.randrange(x0 + 1, x1 - 1)
            y = self.generator.randrange(y0 + 1, y1 - 1)
            wet[x, y] = all(
                wet[x + d.x, y + d.y] for d in Direction.get_cardinal_directions()
            )

        to_secondary = [xy for xy in wet if wet[xy] and self._is_primary_tile(*xy)]
        self.set_secondary(to_secondary)

    def get_river_path(self) -> list[tuple[int, int]]:
        MIN_X, MAX_X = 2, self.floor.WIDTH - 2
        MIN_Y, MAX_Y = 2, self.floor.HEIGHT - 2
        NUM_SECTIONS = 20

        x = self.generator.randrange(MIN_X, MAX_X)
        d, y = self.generator.choice(
            ((Direction.NORTH, MAX_Y - 1), (Direction.SOUTH, MIN_Y))
        )
        D0 = d

        xys = []
        for _ in range(NUM_SECTIONS):
            for _ in range(self.generator.randrange(2, 8)):
                xys.append((x, y))
                x = clamp(MIN_X, x + d.x, MAX_X - 1)
                y = clamp(MIN_Y, y + d.y, MAX_Y - 1)
            d = (
                D0
                if d.is_horizontal()
                else self.generator.choice((Direction.EAST, Direction.WEST))
            )
        return xys

    def generate_river(self):
        lake_at = self.generator.randrange(10, 60)
        to_secondary = []
        for x, y in self.get_river_path():
            if self._is_secondary_tile(x, y):
                break
            if self._is_primary_tile(x, y):
                to_secondary.append((x, y))
            lake_at -= 1
            if lake_at == 0:
                self.generate_river_lake(x, y)

        self.set_secondary(to_secondary)

    def generate_secondary(self):
        NUM_RIVERS = self.generator.randrange(1, 4)
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
