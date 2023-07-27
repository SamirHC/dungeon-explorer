import random

from app.common import textbox, direction
from app.dungeon import dungeondata, dungeonstatus, floor, tile
from app.model import statistic
from app.pokemon import party, pokemon
from app.db import colormap_db, tileset_db, pokemonsprite_db


class Dungeon:
    def __init__(self, dungeon_data: dungeondata.DungeonData, floor_number: int, party: party.Party):
        self.dungeon_id = dungeon_data.dungeon_id
        self.dungeon_data = dungeon_data
        self.floor_number = floor_number
        self.party = party

        self.floor = floor.FloorBuilder(self.current_floor_data, party).build_floor()
        self.tileset = tileset_db[self.current_floor_data.tileset]
        
        self.status = self.load_status()
        self.weather = self.status.weather

        self.dungeon_log = textbox.DungeonTextBox()

    def load_status(self):
        darkness = self.current_floor_data.darkness_level
        weather = self.current_floor_data.weather
        turns = statistic.Statistic(0, 0, self.dungeon_data.turn_limit)
        return dungeonstatus.DungeonStatus(darkness, weather, turns)

    def has_next_floor(self) -> bool:
        return self.floor_number < self.dungeon_data.number_of_floors
    
    @property
    def current_floor_data(self) -> dungeondata.FloorData:
        return self.dungeon_data.floor_list[self.floor_number - 1]

    @property
    def weather(self) -> dungeonstatus.Weather:
        return self.status.weather

    @weather.setter
    def weather(self, new_weather: dungeonstatus.Weather):
        self.status.weather = new_weather
        col_map = colormap_db[new_weather]
        self.tileset = tileset_db[self.current_floor_data.tileset].with_colormap(col_map)
        for p in self.floor.spawned:
            p.sprite.sprite_collection = pokemonsprite_db[p.generic_data.pokedex_number].with_colormap(col_map)
            p.sprite.update_current_sprite()

    @property
    def user(self) -> pokemon.Pokemon:
        return self.party.leader

    def get_terrain(self, position: tuple[int, int]) -> tile.Terrain:
        return self.tileset.get_terrain(self.floor[position].tile_type)

    def is_ground(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is tile.Terrain.GROUND

    def is_wall(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is tile.Terrain.WALL
    
    def is_water(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is tile.Terrain.WATER

    def is_lava(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is tile.Terrain.LAVA

    def is_void(self, position: tuple[int, int]) -> bool:
        return self.get_terrain(position) is tile.Terrain.VOID

    def is_impassable(self, position: tuple[int, int]) -> bool:
        return self.floor[position].is_impassable

    def cuts_corner(self, p: tuple[int, int], d: direction.Direction) -> bool:
        if d.is_cardinal():
            return False
        x, y = p
        d1, d2 = d.clockwise(), d.anticlockwise()
        g1 = self.is_wall((x + d1.x, y + d1.y))
        g2 = self.is_wall((x + d2.x, y + d2.y))
        return g1 or g2

    def user_at_stairs(self) -> bool:
        return self.party.leader.position == self.floor.stairs_spawn

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return self.floor[position].pokemon_ptr is not None

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.floor.spawned])

    def next_turn(self):
        self.status.turns.increase(1)
        for sprite in self.floor.spawned:
            sprite.has_turn = True
            if sprite.status.can_regenerate():
                sprite.status.hp.increase(1)

    def user_is_dead(self) -> bool:
        return self.party.leader.hp_status == 0

    def can_see(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        if abs(p1[0] - p2[0]) <= 2:
            if abs(p1[1] - p2[1]) <= 2:
                return True
        return self.floor.in_same_room(p1, p2)
