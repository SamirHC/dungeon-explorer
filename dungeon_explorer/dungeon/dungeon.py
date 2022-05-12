import random

from dungeon_explorer.common import textbox, direction, statistic
from dungeon_explorer.dungeon import dungeondata, dungeonstatus, floor, tileset, tile, colormap
from dungeon_explorer.pokemon import party, pokemon


class Dungeon:
    def __init__(self, dungeon_data: dungeondata.DungeonData, floor_number: int, party: party.Party):
        self.dungeon_id = dungeon_data.dungeon_id
        self.dungeon_data = dungeon_data
        self.floor_number = floor_number
        self.party = party

        self.floor = floor.FloorBuilder(self.current_floor_data).build_floor()
        self.tileset = tileset.db[self.current_floor_data.tileset]

        self.status = self.load_status()
        self.weather = self.status.weather
        
        self.active_enemies: list[pokemon.Pokemon] = []
        self.spawned: list[pokemon.Pokemon] = []
        self.spawn_party(self.party)
        self.spawn_enemies()

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
        self.tileset = tileset.db[self.current_floor_data.tileset].with_colormap(colormap.db[new_weather])

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

    def get_random_pokemon(self) -> pokemon.Pokemon:
        id, level = self.current_floor_data.get_random_pokemon()
        return pokemon.EnemyPokemon(id, level)

    def user_at_stairs(self) -> bool:
        return self.party.leader.position == self.floor.stairs_spawn

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return self.floor[position].pokemon_ptr is not None

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.spawned])

    def next_turn(self):
        self.status.turns.increase(1)
        for sprite in self.spawned:
            sprite.has_turn = True
            if sprite.status.can_regenerate():
                sprite.status.hp.increase(1)

    def spawn_at(self, p: pokemon.Pokemon, position: tuple[int, int]):
        self.floor[position].pokemon_ptr = p
        p.spawn(position)
        self.spawned.append(p)

    def can_spawn_at(self, position: tuple[int, int]):
        return self.floor.is_room(position) and not self.is_occupied(position) and self.floor[position].can_spawn

    def spawn(self, p: pokemon.Pokemon):
        possible_spawn = []
        for position in self.floor:
            if self.can_spawn_at(position):
                possible_spawn.append(position)

        self.spawn_at(p, random.choice(possible_spawn))

    def spawn_party(self, party: party.Party):
        self.party = party
        self.spawn_at(party.leader, self.floor.player_spawn)

        x, y = party.leader.position
        for member in party:
            if member is party.leader:
                continue
            spawned = False
            for d in direction.Direction:
                position = (d.x + x, d.y + y)
                if self.can_spawn_at(position):
                    self.spawn_at(member, position)
                    spawned = True
                    break
            if not spawned:
                self.spawn(member)

    def spawn_enemies(self):
        self.active_enemies = []
        for _ in range(self.current_floor_data.initial_enemy_density):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)
            self.active_enemies.append(enemy)

    def user_is_dead(self) -> bool:
        return self.party.leader.hp_status == 0

    def can_see(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        if abs(p1[0] - p2[0]) <= 2:
            if abs(p1[1] - p2[1]) <= 2:
                return True
        return self.floor.in_same_room(p1, p2)
