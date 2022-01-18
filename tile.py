import enum


class Terrain(enum.Enum):
    WALL = 0
    SECONDARY = 1
    GROUND = 2


class Tile:
    terrain = Terrain.WALL
    room_index = 0
    is_impassable = False
    trap_index = 0
    stairs_index = 0
    can_spawn = False

    @classmethod
    def hallway_tile(cls):
        t = Tile()
        t.terrain = Terrain.GROUND
        return t

    @classmethod
    def impassable_tile(cls):
        t = Tile()
        t.is_impassable = True
        return t

    @classmethod
    def secondary_tile(cls):
        t = Tile()
        t.terrain = Terrain.SECONDARY
        return t

    @classmethod
    def room_tile(cls, room_number):
        t = Tile()
        t.terrain = Terrain.GROUND
        t.room_index = room_number
        t.can_spawn = True
        return t