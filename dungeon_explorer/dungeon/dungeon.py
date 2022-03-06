import random

from dungeon_explorer.common import textbox
from dungeon_explorer.dungeon import dungeondata, dungeonmap, floor, minimap, tileset
from dungeon_explorer.pokemon import party, pokemon


class Dungeon:
    def __init__(self, dungeon_data: dungeondata.DungeonData, floor_number: int, party: party.Party):
        self.dungeon_id = dungeon_data.dungeon_id
        self.dungeon_data = dungeon_data
        self.floor_number = floor_number
        self.party = party

        self.turns = 0

        self.floor = floor.FloorBuilder(self.current_floor_data).build_floor()
        self.tileset = tileset.TileSet(self.current_floor_data.tileset)
        self.dungeonmap = dungeonmap.DungeonMap(self.floor, self.tileset, self.dungeon_data.is_below)
        self.minimap = minimap.MiniMap(self.floor)
        
        self.active_enemies = []
        self.spawned = []
        self.spawn_party(self.party)
        self.spawn_enemies()

        self.message_log = textbox.TextBox((30, 7), 3)

    def has_next_floor(self) -> bool:
        return self.floor_number < self.dungeon_data.number_of_floors
    
    @property
    def current_floor_data(self) -> dungeondata.FloorData:
        return self.dungeon_data.floor_list[self.floor_number - 1]

    @property
    def user(self) -> pokemon.Pokemon:
        return self.party.user

    @property
    def all_sprites(self) -> list[pokemon.Pokemon]:
        return self.spawned

    def get_random_pokemon(self) -> pokemon.Pokemon:
        id, level = self.current_floor_data.get_random_pokemon()
        return pokemon.EnemyPokemon(id, level)

    def user_at_stairs(self) -> bool:
        return self.party.user.position == self.floor.stairs_spawn

    def is_occupied(self, position: tuple[int, int]) -> bool:
        return any(map(lambda s: s.position == position, self.all_sprites))

    def is_next_turn(self) -> bool:
        return not any([s.has_turn for s in self.all_sprites])

    def next_turn(self):
        self.turns += 1
        for sprite in self.all_sprites:
            sprite.has_turn = True
            if self.turns % pokemon.Pokemon.REGENRATION_RATE == 0 and sprite.current_status["Regen"]:
                sprite.hp += 1

    def spawn(self, p: pokemon.Pokemon):
        possible_spawn = []
        for position in self.floor:
            if self.floor.is_room(position) and not self.is_occupied(position) and self.floor[position].can_spawn:
                possible_spawn.append(position)

        self.spawned.append(p)
        p.spawn(random.choice(possible_spawn))

    def spawn_party(self, party: party.Party):
        self.party = party
        for member in party:
            self.spawn(member)

    def spawn_enemies(self):
        self.active_enemies = []
        for _ in range(self.current_floor_data.initial_enemy_density):
            enemy = self.get_random_pokemon()
            self.spawn(enemy)
            self.active_enemies.append(enemy)

    def user_is_dead(self) -> bool:
        return self.party.is_defeated()

    def tile_is_visible_from(self, observer: tuple[int, int], target: tuple[int, int]) -> bool:
        if abs(observer[0] - target[0]) <= 2:
            if abs(observer[1] - target[1]) <= 2:
                return True
        return self.floor.in_same_room(observer, target)
