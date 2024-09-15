from app.dungeon.floor_factory import FloorFactory
from app.dungeon.weather import Weather
from app.model.bounded_int import BoundedInt
from app.pokemon.party import Party
from app.pokemon.pokemon import Pokemon
from app.gui.tileset import Tileset
import app.db.dungeon_data as dungeon_data_db
import app.db.floor_data as floor_data_db


class Dungeon:
    def __init__(self, dungeon_id: int, floor_number: int, party: Party):
        self.dungeon_id = dungeon_id
        self.floor_number = floor_number
        self.party = party

        self.dungeon_data = dungeon_data_db.load(dungeon_id)
        self.floor_data = floor_data_db.load(dungeon_id, floor_number)

        self.floor = FloorFactory(self.floor_data, party).create_floor()
        self.turns = BoundedInt(0, 0, self.dungeon_data.turn_limit)

    @property
    def has_next_floor(self) -> bool:
        return self.floor_number < self.dungeon_data.number_of_floors

    @property
    def tileset(self) -> Tileset:
        return self.floor.tileset

    def set_weather(self, new_weather: Weather):
        self.floor.status.weather = new_weather

    @property
    def user(self) -> Pokemon:
        return self.party.leader

    def is_next_turn(self) -> bool:
        return not any(s.has_turn for s in self.floor.spawned)

    def next_turn(self):
        self.turns.add(1)
        for sprite in self.floor.spawned:
            sprite.has_turn = True
            sprite.has_started_turn = False
        # TODO:
        # Spawn new pokemon
        # Change weather
        # Display turn warnings/Kick user from dungeon on turn limit

    def user_is_dead(self) -> bool:
        return self.party.leader.status.is_fainted()
