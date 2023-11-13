from app.dungeon.dungeon import Dungeon
from app.move.move import MoveRange
from app.pokemon.pokemondata import MovementType
from app.pokemon.pokemon import Pokemon, EnemyPokemon


class TargetGetter:
    def __init__(self, dungeon: Dungeon):
        self.floor = dungeon.floor
        self.party = dungeon.party
        self.enemies = self.floor.active_enemies
        self.target_getters = {
            MoveRange.ADJACENT_POKEMON: self.get_enemy_in_front,
            MoveRange.ALL_ENEMIES_IN_THE_ROOM: self.get_all_enemies_in_the_room,
            MoveRange.ALL_ENEMIES_ON_THE_FLOOR: self.get_all_enemies_on_the_floor,
            MoveRange.ALL_IN_THE_ROOM_EXCEPT_USER: self.get_all_in_the_room_except_user,
            MoveRange.ALL_POKEMON_IN_THE_ROOM: self.get_all_pokemon_in_the_room,
            MoveRange.ALL_POKEMON_ON_THE_FLOOR: self.get_all_pokemon_on_the_floor,
            MoveRange.ALL_TEAM_MEMBERS_IN_THE_ROOM: self.get_all_team_members_in_the_room,
            MoveRange.ENEMIES_WITHIN_1_TILE_RANGE: self.get_enemies_within_1_tile_range,
            MoveRange.ENEMY_IN_FRONT: self.get_enemy_in_front,
            MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS: self.get_enemy_in_front_cuts_corners,
            MoveRange.ENEMY_UP_TO_2_TILES_AWAY: self.get_enemy_up_to_2_tiles_away,
            MoveRange.FACING_POKEMON: self.get_facing_pokemon,
            MoveRange.FACING_POKEMON_CUTS_CORNERS: self.get_facing_pokemon_cuts_corners,
            MoveRange.FACING_TILE_AND_2_FLANKING_TILES: self.get_facing_tile_and_2_flanking_tiles,
            MoveRange.FLOOR: self.get_none,
            MoveRange.ITEM: self.get_none,
            MoveRange.LINE_OF_SIGHT: self.get_line_of_sight,
            MoveRange.ONLY_THE_ALLIES_IN_THE_ROOM: self.get_only_the_allies_in_the_room,
            MoveRange.POKEMON_WITHIN_1_TILE_RANGE: self.get_pokemon_within_1_tile_range,
            MoveRange.POKEMON_WITHIN_2_TILE_RANGE: self.get_pokemon_within_2_tile_range,
            MoveRange.SPECIAL: self.get_none,
            MoveRange.TEAM_MEMBERS_ON_THE_FLOOR: self.get_team_members_on_the_floor,
            MoveRange.USER: self.get_user,
            MoveRange.WALL: self.get_none
        }

    def __getitem__(self, move_range: MoveRange):
        return self.target_getters[move_range]

    def set_attacker(self, pokemon: Pokemon):
        self.attacker = pokemon

    def get_enemies(self) -> list[Pokemon]:
        if isinstance(self.attacker, EnemyPokemon):
            return self.party.members
        return self.enemies

    def get_allies(self) -> list[Pokemon]:
        if isinstance(self.attacker, EnemyPokemon):
            return self.enemies
        return self.party.members

    def deactivate(self):
        self.attacker = None

    def get_straight_pokemon(self, distance: int=1, cuts_corner: bool=False) -> list[Pokemon]:
        is_phasing = self.attacker.movement_type is MovementType.PHASING
        if is_phasing:
            pass
        elif not cuts_corner and self.floor.cuts_corner((self.attacker.position), self.attacker.direction):
            return []

        x, y = self.attacker.position
        dx, dy = self.attacker.direction.value
        for _ in range(distance):
            x += dx
            y += dy
            if self.floor.is_wall((x, y)) and not is_phasing:
                return []
            p = self.floor[x, y].pokemon_ptr
            if p is not None:
                return [p]
        return []

    def get_surrounding_pokemon(self, radius: int=1) -> list[Pokemon]:
        res = []
        for p in self.floor.spawned:
            if p is self.attacker:
                continue
            if max(abs(p.x - self.attacker.x), abs(p.y - self.attacker.y)) <= radius:
                res.append(p)
        return res

    def get_room_pokemon(self) -> list[Pokemon]:
        res = []
        for p in self.floor.spawned:
            if self.floor.in_same_room(self.attacker.position, p.position):
                res.append(p)
        for p in self.get_surrounding_pokemon(2):
            if p not in res:
                res.append(p)
        return res

    def get_none(self):
        return []

    def get_all_enemies_in_the_room(self):
        return [p for p in self.get_room_pokemon() if p in self.get_enemies()]

    def get_all_enemies_on_the_floor(self):
        return self.get_enemies()

    def get_all_in_the_room_except_user(self):
        return [p for p in self.get_room_pokemon() if p is not self.attacker]

    def get_all_pokemon_in_the_room(self):
        return self.get_room_pokemon()

    def get_all_pokemon_on_the_floor(self):
        return self.floor.spawned

    def get_all_team_members_in_the_room(self):
        return [p for p in self.get_room_pokemon() if p in self.get_allies()]

    def get_enemies_within_1_tile_range(self):
        return [p for p in self.get_surrounding_pokemon() if p in self.get_enemies()]

    def get_enemy_in_front(self):
        return [p for p in self.get_straight_pokemon(1, False) if p in self.get_enemies()]

    def get_enemy_in_front_cuts_corners(self):
        return [p for p in self.get_straight_pokemon(1, True) if p in self.get_enemies()]

    def get_enemy_up_to_2_tiles_away(self):
        return [p for p in self.get_straight_pokemon(2, True) if p in self.get_enemies()]

    def get_facing_pokemon(self):
        return self.get_straight_pokemon(1, False)

    def get_facing_pokemon_cuts_corners(self):
        return self.get_straight_pokemon(1, True)

    def get_facing_tile_and_2_flanking_tiles(self):
        return []

    def get_line_of_sight(self):
        return [p for p in self.get_straight_pokemon(10, True) if p in self.get_enemies()]

    def get_only_the_allies_in_the_room(self):
        return [p for p in self.get_room_pokemon() if p is not self.attacker and p in self.get_allies()]

    def get_pokemon_within_1_tile_range(self):
        return self.get_surrounding_pokemon(1)

    def get_pokemon_within_2_tile_range(self):
        return self.get_surrounding_pokemon(2)

    def get_team_members_on_the_floor(self):
        return self.get_allies()

    def get_user(self):
        return [self.attacker]