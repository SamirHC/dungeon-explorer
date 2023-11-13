from app.dungeon.floor import Floor
from app.dungeon.tile import Tile

from functools import partial


class FloorMapBuilder:
    """
    A class for building just the map related components of a floor. This class 
    is not responsible for the generation of the dungeon map. It is only
    responsible for modifying the tile elements and internal information of the 
    Floor object.
    """

    def __init__(self, width=56, height=32):
        self.floor = Floor(width, height)

    def _set_tiles(self, coords, tile_setter):
        """
        Private method. Applies a function on each tile.
        
        :param coords: List of tile coordinates.
        :param tile_setter: Function to be called on the tile. If arguments need
                            to be passed in, change to a partial function.
        """
        for x, y in coords:
            tile_setter(self.floor[x, y])

    def set_room(self, coords: list[tuple[int, int]], room_num: int):
        """
        Associates each tile to a room with the provided room number.
        
        :param coords: List of tile coordinates.
        :param room_num: The id of the room.
        """
        self._set_tiles(coords, partial(Tile.room_tile, room_number=room_num))

    def set_rect_room(self, topleft: tuple[int, int], size: tuple[int, int], room_num: int):
        """
        Associates a rectanglar collection of tiles to a room with the provided
        room number.
        
        :param topleft: Top-left coordinate of the rectangle.
        :param size: The dimensions of the rectangle.
        :param room_num: The id of the room.
        """
        x0, y0 = topleft
        w, h = size
        coords = [(x, y) for x in range(x0, x0+w) for y in range(y0, y0+h)]
        self.set_room(coords, room_num)

    def set_hallway(self, coords: list[tuple[int, int]]):
        """
        Sets a collection of tiles to a hallway tile.
        
        :param coords: List of tile coordinates.
        """
        self._set_tiles(coords, Tile.hallway_tile)

    def set_secondary(self, coords: list[tuple[int, int]]):
        """
        Sets a collection of tiles to a secondary tile.
        
        :param coords: List of tile coordinates.
        """
        self._set_tiles(coords, Tile.secondary_tile)

    def reset(self):
        """
        Sets all tiles and data to its default state.
        """
        for tile in self.floor:
            tile.reset()
        self.floor.room_exits.clear()
        self.floor.stairs_spawn = (0, 0)
        self.floor.has_shop = False

        self.floor.active_enemies.clear()
        self.floor.spawned.clear()

        self.floor.tileset = None
        self.floor.status = None

