from app.common.textbox import DungeonTextBox
from app.dungeon.dungeon_data import DungeonData
from app.dungeon.floor_factory import FloorFactory
from app.dungeon.weather import Weather
from app.dungeon.floor_data import FloorData
from app.model.statistic import Statistic
from app.pokemon.party import Party
from app.pokemon.pokemon import Pokemon
import app.db.database as db


class Dungeon:
    def __init__(self, dungeon_data: DungeonData, floor_number: int, party: Party):
        self.dungeon_id = dungeon_data.dungeon_id
        self.dungeon_data = dungeon_data
        self.floor_number = floor_number
        self.party = party

        seed = 10

        self.floor = FloorFactory(self.current_floor_data, party, seed).create_floor()
        
        self.dungeon_log = DungeonTextBox()
        self.turns = Statistic(0, 0, self.dungeon_data.turn_limit)

    def has_next_floor(self) -> bool:
        return self.floor_number < self.dungeon_data.number_of_floors
    
    @property
    def tileset(self):
        return self.floor.tileset
    
    @property
    def current_floor_data(self) -> FloorData:
        return self.dungeon_data.floor_list[self.floor_number - 1]

    def set_weather(self, new_weather: Weather):
        self.floor.status.weather = new_weather
        col_map = db.colormap_db[new_weather]
        self.floor.tileset = db.tileset_db[self.current_floor_data.tileset].with_colormap(col_map)
        for p in self.floor.spawned:
            p.sprite.sprite_collection = db.pokemonsprite_db[p.data.pokedex_number].with_colormap(col_map)
            p.sprite.update_current_sprite()

    @property
    def user(self) -> Pokemon:
        return self.party.leader

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.floor.spawned])

    def next_turn(self):
        self.turns.increase(1)
        for sprite in self.floor.spawned:
            sprite.has_turn = True
            if sprite.status.can_regenerate():
                sprite.status.hp.increase(1)

    def user_is_dead(self) -> bool:
        return self.party.leader.hp_status == 0

