import random

from app.common.constants import RNG
from app.dungeon.floor import Floor
from app.dungeon.floor_data import FloorData
from app.dungeon.tile_type import TileType
from app.item.item import Item
from app.dungeon.trap import Trap
from app.common.direction import Direction
from app.pokemon.pokemon import Pokemon
from app.pokemon.pokemon_factory import enemy_pokemon_factory
from app.pokemon.party import Party
import app.db.database as db


class Spawner:
    def __init__(
        self,
        floor: Floor,
        party: Party,
        data: FloorData,
        generator: random.Random = RNG,
    ):
        self.floor = floor
        self.party = party
        self.data = data
        self.generator = generator

    def get_valid_spawn_locations(self):
        return self.floor.get_valid_spawn_locations()

    def get_valid_buried_spawn_locations(self):
        valid_buried_spawns = []
        for x in range(self.floor.WIDTH):
            for y in range(self.floor.HEIGHT):
                if self.floor[x, y].tile_type is TileType.PRIMARY:
                    valid_buried_spawns.append((x, y))
        return valid_buried_spawns

    def spawn_stairs(self, position):
        self.floor.stairs_spawn = position

    def spawn_item(self, position, item: Item):
        self.floor[position].item_ptr = item

    def spawn_trap(self, position, trap: Trap):
        self.floor[position].trap = trap

    def fill_floor_with_spawns(self):
        valid_spawns = self.floor.get_valid_spawn_locations()
        self.generator.shuffle(valid_spawns)
        # Stairs
        self.spawn_stairs(valid_spawns[-1])
        valid_spawns.pop()
        # Traps
        num_traps = self.get_number_of_traps()
        for _ in range(num_traps):
            self.spawn_trap(valid_spawns[-1], self.get_random_trap())
            valid_spawns.pop()
        # Items
        num_items = self.get_number_of_items(self.data.item_density)
        for _ in range(num_items):
            self.spawn_item(valid_spawns[-1], self.get_random_item())
            valid_spawns.pop()
        # Buried Items
        valid_spawns = self.get_valid_buried_spawn_locations()
        self.generator.shuffle(valid_spawns)
        num_items = self.get_number_of_items(self.data.buried_item_density)
        for _ in range(num_items):
            self.spawn_item(valid_spawns[-1], self.get_random_item())
            valid_spawns.pop()
        # TODO: Shop
        # Characters
        self.spawn_party()
        self.spawn_enemies()

    def spawn_pokemon(self, p: Pokemon, position: tuple[int, int]):
        self.floor[position].pokemon_ptr = p
        p.spawn(position)
        self.floor.spawned.append(p)

    def spawn_party(self):
        valid_spawns = self.get_valid_spawn_locations()
        self.generator.shuffle(valid_spawns)
        self.spawn_pokemon(self.party.leader, valid_spawns[-1])
        valid_spawns.pop()

        leader_x, leader_y = self.party.leader.position

        for member in self.party:
            if member is self.party.leader:
                continue
            # TODO Improve party spawn algorithm
            for d in Direction:
                position = (d.x + leader_x, d.y + leader_y)
                if self.floor.is_valid_spawn_location(position):
                    self.spawn_pokemon(member, position)
                    break

        self.floor.party = self.party

    def spawn_enemies(self):
        valid_spawns = self.get_valid_spawn_locations()
        self.generator.shuffle(valid_spawns)
        for _ in range(self.data.initial_enemy_density):
            enemy = enemy_pokemon_factory(*self.data.get_random_pokemon())
            self.spawn_pokemon(enemy, valid_spawns[-1])
            valid_spawns.pop()
            self.floor.active_enemies.append(enemy)

    def get_number_of_items(self, density) -> int:
        if density != 0:
            return max(1, self.generator.randrange(density - 2, density + 2))
        return 0

    def get_number_of_traps(self):
        n = self.data.trap_density
        return self.generator.randint(n // 2, n)

    def get_random_item(self) -> Item:
        return db.item_db[183]

    def get_random_trap(self):
        return self.data.get_random_trap()
