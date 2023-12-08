from app.common.direction import Direction
import app.db.database as db
from app.dungeon import floor_data, floor_status
from app.dungeon.floor_map_generator import FloorMapGenerator
from app.dungeon.structure import Structure
from app.dungeon.floor import Floor
from app.pokemon.party import Party
from app.dungeon.spawner import Spawner


import random


class FloorFactory:
    def __init__(self, data: floor_data.FloorData, party: Party, seed: int):
        self.data = data
        self.party = party
        self.random = random.Random(seed)
        self.floor_map_generator = FloorMapGenerator(data, random)
        self.floor = self.floor_map_generator.floor
        self.spawner = Spawner(self.floor, self.party, self.data, self.random)

    def grid_positions(self, grid_w, grid_h) -> tuple[list[int], list[int]]:
        cell_w = self.floor.WIDTH // grid_w
        cell_h = self.floor.HEIGHT // grid_h
        xs = list(range(0, self.floor.WIDTH+1, cell_w))
        ys = list(range(0, self.floor.HEIGHT+1, cell_h))
        return xs, ys

    def create_floor(self) -> Floor:
        self.build_floor_structure()
        self.spawner.fill_floor_with_spawns()
        self.floor.status = floor_status.FloorStatus(
            self.data.darkness_level,
            self.data.weather
        )
        self.floor.update_tile_masks()
        self.floor.find_room_exits()
        self.floor.tileset = db.tileset_db[self.data.tileset]
        return self.floor
    
    def build_floor_structure(self):
        if self.data.fixed_floor_id != "0":
            self.build_fixed_floor()
            return

        generating = True
        while generating:
            self.floor_map_generator.reset()
            self.generate_floor_structure()
            generating = not self.floor_map_generator.is_strongly_connected()

    def build_fixed_floor(self):
        pass

    def generate_floor_structure(self):
        s = self.data.structure
        if s is Structure.SMALL:
            grid_size = (4, self.random.randrange(2)+2)
            self.generate_normal_floor(grid_size, 1)
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
            grid_size = 4, self.random.randrange(2)+2
            self.generate_normal_floor(grid_size, 2)
        elif s is Structure.SMALL_MEDIUM:
            grid_size = self.random.randrange(2, 5), self.random.randrange(2, 4)
            self.generate_normal_floor(grid_size, 0)
        elif s.is_medium_large():
            grid_size = self.random.randrange(2, 7), self.random.randrange(2, 5)
            self.generate_normal_floor(grid_size, 0)
        if self.data.secondary_used:
            self.floor_map_generator.generate_secondary()

    def generate_normal_floor(self, grid_size, floor_size):
        xs, ys = self.grid_positions(*grid_size)
        self.floor_map_generator.init_grid(grid_size, xs, ys, floor_size)
        self.floor_map_generator.assign_rooms()
        self.floor_map_generator.create_rooms()
        self.floor_map_generator.connect_cells()
        self.floor_map_generator.create_hallways()
        self.floor_map_generator.merge_rooms()
        self.floor_map_generator.join_isolated_rooms()
        self.floor_map_generator.create_extra_hallways()

    def generate_ring(self):
        grid_size = (6, 4)
        xs = [0, 6, 17, 28, 39, 50, 56]
        ys = [0, 7, 16, 25, 32]
        self.floor_map_generator.init_grid(grid_size, xs, ys, 0)

        for x in range(1, 5):
            for y in range(1, 3):
                self.floor_map_generator.grid[x, y].is_room = True
        self.floor_map_generator.create_rooms()

        for x in range(5):
            self.floor_map_generator.connect_cell_in_direction((x, 0), Direction.EAST)
            self.floor_map_generator.connect_cell_in_direction((x, 3), Direction.EAST)
        for y in range(3):
            self.floor_map_generator.connect_cell_in_direction((0, y), Direction.SOUTH)
            self.floor_map_generator.connect_cell_in_direction((5, y), Direction.SOUTH)
        self.floor_map_generator.connect_cells()
        self.floor_map_generator.create_hallways()
        self.floor_map_generator.merge_rooms()
        self.floor_map_generator.join_isolated_rooms()
        self.floor_map_generator.create_extra_hallways()

    def generate_crossroads(self):
        grid_size = (5, 4)
        xs, ys = self.grid_positions(*grid_size)
        self.floor_map_generator.init_grid(grid_size, xs, ys)

        grid = self.floor_map_generator.grid
        for x in range(1, 4):
            grid[x, 0].is_room = True
            grid[x, 3].is_room = True
        for y in range(1, 3):
            grid[0, y].is_room = True
            grid[4, y].is_room = True
        for x in (0, 4):
            for y in (0, 3):
                grid[x, y].valid_cell = False
        self.floor_map_generator.create_rooms()

        for x in range(1, 4):
            for y in range(3):
                self.floor_map_generator.connect_cell_in_direction((x, y), Direction.SOUTH)
        for x in range(4):
            for y in range(1, 3):
                self.floor_map_generator.connect_cell_in_direction((x, y), Direction.EAST)
        self.floor_map_generator.create_hallways()
        self.floor_map_generator.join_isolated_rooms()
        self.floor_map_generator.create_extra_hallways()

    def generate_line(self):
        grid_size = 5, 1
        grid_xs = [0, 11, 22, 33, 44, 56]
        grid_ys = [4, 15]
        self.floor_map_generator.init_grid(grid_size, grid_xs, grid_ys)
        self.floor_map_generator.assign_rooms()
        self.floor_map_generator.create_rooms()
        self.floor_map_generator.connect_cells()
        self.floor_map_generator.create_hallways()
        self.floor_map_generator.join_isolated_rooms()
        self.floor_map_generator.create_extra_hallways()

    def generate_cross(self):
        grid_size = (3, 3)
        grid_xs = [11, 22, 33, 44]
        grid_ys = [2, 11, 20, 31]
        self.floor_map_generator.init_grid(grid_size, grid_xs, grid_ys)
        
        grid = self.floor_map_generator.grid
        for x in (0, 2):
            for y in (0, 2):
                grid[x, y].valid_cell = False
        for i in range(3):
            grid[i, 1].is_room = True
            grid[1, i].is_room = True
        self.floor_map_generator.create_rooms()
        for x in range(2):
            self.floor_map_generator.connect_cell_in_direction((x, 1), Direction.EAST)
        for y in range(2):
            self.floor_map_generator.connect_cell_in_direction((1, y), Direction.SOUTH)
        self.floor_map_generator.create_hallways()
        self.floor_map_generator.create_extra_hallways()

    def generate_beetle(self):
        grid_size = (3, 3)
        grid_xs = [5, 15, 36, 50]
        grid_ys = [2, 11, 20, 31]
        self.floor_map_generator.init_grid(grid_size, grid_xs, grid_ys)
        grid = self.floor_map_generator.grid
        for _, cell in grid.cells.items():
            cell.is_room = True
        self.floor_map_generator.create_rooms()
        for x in range(2):
            for y in range(3):
                self.floor_map_generator.connect_cell_in_direction((x, y), Direction.EAST)
        for y in range(2):
            self.floor_map_generator.connect_cell_in_direction((1, y), Direction.SOUTH)
        self.floor_map_generator.create_hallways()
        self.floor_map_generator.merge_specific_rooms(grid[1, 0], grid[1, 1])
        self.floor_map_generator.merge_specific_rooms(grid[1, 1], grid[1, 2])
        self.floor_map_generator.create_extra_hallways()
