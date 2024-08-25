from __future__ import annotations


from app.common.direction import Direction
from app.dungeon import tile
from app.dungeon.terrain import Terrain
from app.dungeon.tile_type import TileType
from app.pokemon.party import Party
from app.pokemon import pokemon
from app.gui.tileset import Tileset
from app.dungeon.floor_status import FloorStatus


class Floor:
    def __init__(self, WIDTH=56, HEIGHT=32):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.SIZE = (WIDTH, HEIGHT)

        self._floor = tuple(tile.Tile() for _ in range(WIDTH * HEIGHT))

        self.room_exits: dict[int, list[tuple[int, int]]] = {}
        self.stairs_spawn = (0, 0)
        self.has_shop = False

        self.active_enemies: list[pokemon.Pokemon] = []
        self.spawned: list[pokemon.Pokemon] = []
        self.party: Party = None

        self.tileset: Tileset = None
        self.status: FloorStatus = None

    def __getitem__(self, position: tuple[int, int]) -> tile.Tile:
        if not self.in_bounds(position):
            return tile.Tile().impassable_tile()
        x, y = position
        return self._floor[x + y * self.WIDTH]

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

    def is_room(self, p: tuple[int, int]) -> bool:
        return self[p].room_index

    def in_same_room(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.is_room(p1) and self[p1].room_index == self[p2].room_index

    def is_tertiary(self, position: tuple[int, int]):
        return self[position].tile_type is TileType.TERTIARY

    def is_primary(self, position: tuple[int, int]):
        return self[position].tile_type is TileType.PRIMARY

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

    def get_terrain(self, position: tuple[int, int]) -> Terrain:
        return self.tileset.get_terrain(self[position].tile_type)

    def is_ground(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is Terrain.GROUND

    def is_wall(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is Terrain.WALL

    def is_water(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is Terrain.WATER

    def is_lava(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is Terrain.LAVA

    def is_void(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is Terrain.VOID

    def is_impassable(self, position: tuple[int, int]) -> bool:
        return self[position].is_impassable

    def cuts_corner(self, p: tuple[int, int], d: Direction) -> bool:
        if d.is_cardinal():
            return False
        x, y = p
        d1, d2 = d.clockwise(), d.anticlockwise()
        g1 = self.is_wall((x + d1.x, y + d1.y))
        g2 = self.is_wall((x + d2.x, y + d2.y))
        return g1 or g2

    def user_at_stairs(self) -> bool:
        return self.party.leader.position == self.stairs_spawn

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return self[position].pokemon_ptr is not None

    def can_see(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        if abs(p1[0] - p2[0]) <= 2:
            if abs(p1[1] - p2[1]) <= 2:
                return True
        return self.in_same_room(p1, p2)

    def get_local_ground_tiles_positions(self, position: tuple[int, int]):
        positions = []
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                other = x, y
                if self.can_see(position, other) and self.is_ground(other):
                    positions.append(other)
        return positions

    def get_local_pokemon_positions(self, position: tuple[int, int]):
        res = []
        for pos in self.get_local_ground_tiles_positions(position):
            if self[pos].pokemon_ptr:
                res.append(pos)
        return res

    def update_tile_masks(self):
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.update_tile_mask(x, y)

    def update_tile_mask(self, x, y):
        this_tile = self[x, y]
        mask = []
        cardinal_mask = []
        for d in (
            Direction.NORTH_WEST,
            Direction.NORTH,
            Direction.NORTH_EAST,
            Direction.WEST,
            Direction.EAST,
            Direction.SOUTH_WEST,
            Direction.SOUTH,
            Direction.SOUTH_EAST,
        ):
            other_tile = self[x + d.x, y + d.y]
            is_same = this_tile.tile_type is other_tile.tile_type
            mask.append(is_same)
            if d.is_cardinal():
                cardinal_mask.append(is_same)
        this_tile.tile_mask = tile.value(tuple(mask))
        this_tile.cardinal_tile_mask = tile.value(tuple(cardinal_mask))

    def find_room_exits(self):
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                position = (x, y)
                if not self.is_room_exit(position):
                    continue
                self[position].can_spawn = False
                room_number = self[position].room_index
                if room_number in self.room_exits:
                    self.room_exits[room_number].append(position)
                else:
                    self.room_exits[room_number] = [position]

    def is_room_exit(self, position: tuple[int, int]):
        if not self.is_room(position):
            return False
        x, y = position
        for d in Direction.get_cardinal_directions():
            d_pos = x + d.x, y + d.y
            if self.is_tertiary(d_pos) and not self.is_room(d_pos):
                return True
        return False
