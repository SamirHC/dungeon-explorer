from app.dungeon.floor import Floor
from app.dungeon.floor import tile


class FloorMapBuilder:
    """
    A class for building just the map related components of a floor. This class 
    is not responsible for the generation of the dungeon map. It is only
    responsible for modifying the tile elements and internal information of the 
    Floor object.
    """

    def __init__(self, floor: Floor):
        self.floor = floor

    def _set_tiles(self, coords, tile_setter, *args):
        """
        Private method. Applies a function on each tile.
        
        :param coords: List of tile coordinates.
        :param tile_setter: Function to be called on the tile.
        :param args: Additional arguments to be passed to the tile_setter.
        """
        for x, y in coords:
            tile_setter(self.floor[x, y], args)

    def set_room(self, coords: list[tuple[int, int]], room_num: int):
        """
        Associates each tile to a room with the provided room number.
        
        :param coords: List of tile coordinates.
        :param room_num: The id of the room.
        """
        self._set_tiles(coords, tile.Tile.room_tile, room_num)

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
        self._set_tiles(coords, tile.Tile.room_tile)

    def set_secondary(self, coords: list[tuple[int, int]]):
        """
        Sets a collection of tiles to a secondary tile.
        
        :param coords: List of tile coordinates.
        """
        self._set_tiles(coords, tile.Tile.secondary_tile)

    def reset(self):
        """
        Sets all tiles to its default state.
        """
        self.floor.clear()
