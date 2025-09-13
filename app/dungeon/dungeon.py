from app.dungeon.floor_factory import FloorFactory
from app.dungeon.weather import Weather
from app.model.bounded_int import BoundedInt
from app.pokemon.party import Party
import app.db.floor_data as floor_data_db
import app.db.dungeon_data as dungeon_data_db
from app.item.inventory import Inventory
from app.dungeon.spawner import Spawner


class Dungeon:
    SPAWN_RATE = 36
    REGEN_RATE = 6
    HUNGER_RATE = 10

    def __init__(
        self, dungeon_id: int, floor_number: int, party: Party, inventory: Inventory
    ):
        self.dungeon_id = dungeon_id
        self.floor_number = floor_number
        self.party = party
        self.inventory = inventory

        self.dungeon_data = dungeon_data_db.load(dungeon_id)
        self.turns = BoundedInt(0, 0, self.dungeon_data.turn_limit)

        self.floor = FloorFactory.from_id(dungeon_id, floor_number, party)
        self.spawner = Spawner(
            self.floor, self.party, floor_data_db.load(dungeon_id, floor_number)
        )

    def set_weather(self, new_weather: Weather):
        self.floor.status.weather = new_weather

    def is_next_turn(self) -> bool:
        return not any(s.has_turn for s in self.floor.spawned)

    def next_turn(self):
        self.turns.add(1)

        for sprite in self.floor.spawned:
            sprite.has_turn = True
            sprite.has_started_turn = False
        # TODO:
        # Spawn new pokemon
        if self.turns.value % Dungeon.SPAWN_RATE == 0:
            self.spawner.spawn_enemies(1)
        if self.turns.value % Dungeon.REGEN_RATE == 0:
            for sprite in self.floor.spawned:
                sprite.status.hp.add(1)
        if self.turns.value % Dungeon.HUNGER_RATE == 0:
            self.party.leader.status.belly.add(-1)
        # Change weather
        # Display turn warnings/Kick user from dungeon on turn limit

    def user_is_dead(self) -> bool:
        return self.party.leader.status.is_fainted()
