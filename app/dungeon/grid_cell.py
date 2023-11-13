from app.common.direction import Direction


class Cell:
    """
    A helper data class for the dungeon generation algorithm, representing a
    segment of the floor map.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.valid_cell = False
        self.is_room = False
        self.is_connected = False
        self.is_merged = False
        self.connections: set[Direction] = set()
        self.imperfect = False
        self.secondary = False
    
    def get_xy(self) -> tuple[int, int]:
        return (self.x, self.y)


class Grid:
    """
    A helper class for the dungeon generation algorithm, representing the floor 
    as a grid of cells.
    """

    def __init__(self, size: tuple[int, int], xs: [int], ys: [int], floor_size: int=0):
        self.size = size
        self.w, self.h = size
        self.xs = xs
        self.ys = ys
        self.floor_size = floor_size
        self.cells = {
            (x, y): Cell(x, y) for x in range(self.w) for y in range(self.h)
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
    
    def get_valid_cells(self) -> list[Cell]:
        return list(filter(lambda c: c.valid_cell, list(self.cells.values())))

    def get_adjacent_cell(self, cell: Cell, d: Direction) -> Cell:
        x = cell.x + d.x
        y = cell.y + d.y
        if x < 0 or self.w <= x or y < 0 or self.h <= y:
            return None
        return self[x, y]
    
    def get_valid_directions_from_cell(self, x: int, y: int) -> list[Direction]:
        ds: list[Direction] = []
        if x > 0:
            ds.append(Direction.WEST)
        if x < self.w:
            ds.append(Direction.EAST)
        if y > 0:
            ds.append(Direction.NORTH)
        if y < self.h:
            ds.append(Direction.SOUTH)
        return ds
