from app.dungeon.dungeon import Dungeon
from app.move.move import MoveRange
from app.pokemon.movement_type import MovementType
from app.pokemon.pokemon import Pokemon

# The pokemon that is finding its target(s)
pokemon: Pokemon = None


def set_pokemon(p: Pokemon):
    global pokemon
    pokemon = p


def deactivate():
    global pokemon
    pokemon = None


# Getters
def get_enemies(dungeon: Dungeon) -> list[Pokemon]:
    if pokemon.is_enemy:
        return dungeon.party.members
    return dungeon.floor.active_enemies


def get_allies(dungeon: Dungeon) -> list[Pokemon]:
    if pokemon.is_enemy:
        return dungeon.floor.active_enemies
    return dungeon.party.members


# Helpers
def get_straight_pokemon(
    dungeon: Dungeon, distance: int = 1, cuts_corner: bool = False
) -> list[Pokemon]:
    is_phasing = pokemon.movement_type is MovementType.PHASING
    if is_phasing:
        pass
    elif not cuts_corner and dungeon.floor.cuts_corner(
        (pokemon.position), pokemon.direction
    ):
        return []

    x, y = pokemon.position
    dx, dy = pokemon.direction.value
    for _ in range(distance):
        x += dx
        y += dy
        if dungeon.floor.is_wall((x, y)) and not is_phasing:
            return []
        p = dungeon.floor[x, y].pokemon_ptr
        if p is not None:
            return [p]
    return []


def get_surrounding_pokemon(dungeon: Dungeon, radius: int = 1) -> list[Pokemon]:
    res = []
    for p in dungeon.floor.spawned:
        if p is pokemon:
            continue
        if max(abs(p.x - pokemon.x), abs(p.y - pokemon.y)) <= radius:
            res.append(p)
    return res


def get_room_pokemon(dungeon: Dungeon) -> list[Pokemon]:
    res = []
    for p in dungeon.floor.spawned:
        if dungeon.floor.in_same_room(pokemon.position, p.position):
            res.append(p)
    for p in get_surrounding_pokemon(dungeon, 2):
        if p not in res:
            res.append(p)
    return res


def get_none(dungeon: Dungeon):
    return []


# Target Getters in the dispatcher
def get_all_enemies_in_the_room(dungeon: Dungeon):
    return [p for p in get_room_pokemon(dungeon) if p in get_enemies(dungeon)]


def get_all_enemies_on_the_floor(dungeon: Dungeon):
    return get_enemies(dungeon)


def get_all_in_the_room_except_user(dungeon: Dungeon):
    return [p for p in get_room_pokemon(dungeon) if p is not pokemon]


def get_all_pokemon_in_the_room(dungeon: Dungeon):
    return get_room_pokemon(dungeon)


def get_all_pokemon_on_the_floor(dungeon: Dungeon):
    return dungeon.floor.spawned


def get_all_team_members_in_the_room(dungeon: Dungeon):
    return [p for p in get_room_pokemon(dungeon) if p in get_allies(dungeon)]


def get_enemies_within_1_tile_range(dungeon: Dungeon):
    return [p for p in get_surrounding_pokemon(dungeon) if p in get_enemies(dungeon)]


def get_enemy_in_front(dungeon: Dungeon):
    return [p for p in get_straight_pokemon(dungeon, 1, False) if p in get_enemies(dungeon)]


def get_enemy_in_front_cuts_corners(dungeon: Dungeon):
    return [p for p in get_straight_pokemon(dungeon, 1, True) if p in get_enemies(dungeon)]


def get_enemy_up_to_2_tiles_away(dungeon: Dungeon):
    return [p for p in get_straight_pokemon(dungeon, 2, True) if p in get_enemies(dungeon)]


def get_facing_pokemon(dungeon: Dungeon):
    return get_straight_pokemon(dungeon, 1, False)


def get_facing_pokemon_cuts_corners(dungeon: Dungeon):
    return get_straight_pokemon(dungeon, 1, True)


def get_facing_tile_and_2_flanking_tiles(dungeon: Dungeon):
    # TODO
    return []


def get_line_of_sight(dungeon: Dungeon):
    return [p for p in get_straight_pokemon(dungeon, 10, True) if p in get_enemies(dungeon)]


def get_only_the_allies_in_the_room(dungeon: Dungeon):
    return [p for p in get_room_pokemon(dungeon) if p is not pokemon and p in get_allies(dungeon)]


def get_pokemon_within_1_tile_range(dungeon: Dungeon):
    return get_surrounding_pokemon(dungeon, 1)


def get_pokemon_within_2_tile_range(dungeon: Dungeon):
    return get_surrounding_pokemon(dungeon, 2)


def get_team_members_on_the_floor(dungeon: Dungeon):
    return get_allies(dungeon)


def get_user(dungeon: Dungeon):
    return [pokemon]


target_getters = {
    MoveRange.ADJACENT_POKEMON: get_enemy_in_front,
    MoveRange.ALL_ENEMIES_IN_THE_ROOM: get_all_enemies_in_the_room,
    MoveRange.ALL_ENEMIES_ON_THE_FLOOR: get_all_enemies_on_the_floor,
    MoveRange.ALL_IN_THE_ROOM_EXCEPT_USER: get_all_in_the_room_except_user,
    MoveRange.ALL_POKEMON_IN_THE_ROOM: get_all_pokemon_in_the_room,
    MoveRange.ALL_POKEMON_ON_THE_FLOOR: get_all_pokemon_on_the_floor,
    MoveRange.ALL_TEAM_MEMBERS_IN_THE_ROOM: get_all_team_members_in_the_room,
    MoveRange.ENEMIES_WITHIN_1_TILE_RANGE: get_enemies_within_1_tile_range,
    MoveRange.ENEMY_IN_FRONT: get_enemy_in_front,
    MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS: get_enemy_in_front_cuts_corners,
    MoveRange.ENEMY_UP_TO_2_TILES_AWAY: get_enemy_up_to_2_tiles_away,
    MoveRange.FACING_POKEMON: get_facing_pokemon,
    MoveRange.FACING_POKEMON_CUTS_CORNERS: get_facing_pokemon_cuts_corners,
    MoveRange.FACING_TILE_AND_2_FLANKING_TILES: get_facing_tile_and_2_flanking_tiles,
    MoveRange.FLOOR: get_none,
    MoveRange.ITEM: get_none,
    MoveRange.LINE_OF_SIGHT: get_line_of_sight,
    MoveRange.ONLY_THE_ALLIES_IN_THE_ROOM: get_only_the_allies_in_the_room,
    MoveRange.POKEMON_WITHIN_1_TILE_RANGE: get_pokemon_within_1_tile_range,
    MoveRange.POKEMON_WITHIN_2_TILE_RANGE: get_pokemon_within_2_tile_range,
    MoveRange.SPECIAL: get_none,
    MoveRange.TEAM_MEMBERS_ON_THE_FLOOR: get_team_members_on_the_floor,
    MoveRange.USER: get_user,
    MoveRange.WALL: get_none,
}


def get_targets(attacker: Pokemon, dungeon: Dungeon, move_range: MoveRange):
    set_pokemon(attacker)
    res = target_getters[move_range](dungeon)
    deactivate()
    return res
