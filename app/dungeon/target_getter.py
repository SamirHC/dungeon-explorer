from app.dungeon.dungeon import Dungeon
from app.move.move import MoveRange
from app.pokemon.movement_type import MovementType
from app.pokemon.pokemon import Pokemon


# Getters
def get_enemies(attacker: Pokemon, dungeon: Dungeon) -> list[Pokemon]:
    return dungeon.party.members if attacker.is_enemy else dungeon.floor.active_enemies


def get_allies(attacker: Pokemon, dungeon: Dungeon) -> list[Pokemon]:
    return dungeon.floor.active_enemies if attacker.is_enemy else dungeon.party.members


# Helpers
def get_straight_pokemon(
    attacker: Pokemon, dungeon: Dungeon, distance: int = 1, cuts_corner: bool = False
) -> list[Pokemon]:
    x, y = attacker.position
    d = attacker.direction
    is_phasing = attacker.data.movement_type is MovementType.PHASING

    if not is_phasing and not cuts_corner and dungeon.floor.cuts_corner((x, y), d):
        return []

    targets = list(
        filter(
            lambda p: p is not None,
            (
                dungeon.floor[x + i * d.x, y + i * d.y].pokemon_ptr
                for i in range(1, distance + 1)
                if not dungeon.floor.is_wall((x + i * d.x, y + i * d.y)) or is_phasing
            ),
        )
    )
    return [targets[0]] if targets else []


def get_surrounding_pokemon(
    attacker: Pokemon, dungeon: Dungeon, radius: int = 1
) -> list[Pokemon]:
    return [
        p
        for p in dungeon.floor.spawned
        if max(abs(p.x - attacker.x), abs(p.y - attacker.y)) <= radius
        and p is not attacker
    ]


def get_room_pokemon(attacker: Pokemon, dungeon: Dungeon) -> list[Pokemon]:
    return [
        p
        for p in dungeon.floor.spawned
        if dungeon.floor.in_same_room(attacker.position, p.position)
        or max(abs(p.x - attacker.x), abs(p.y - attacker.y)) <= 2
    ]


def get_none(attacker: Pokemon, dungeon: Dungeon):
    return []


# Target Getters in the dispatcher
def get_all_enemies_in_the_room(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_room_pokemon(attacker, dungeon)
        if p in get_enemies(attacker, dungeon)
    ]


def get_all_enemies_on_the_floor(attacker: Pokemon, dungeon: Dungeon):
    return get_enemies(attacker, dungeon)


def get_all_in_the_room_except_user(attacker, dungeon: Dungeon):
    return [p for p in get_room_pokemon(dungeon) if p is not attacker]


def get_all_pokemon_in_the_room(attacker: Pokemon, dungeon: Dungeon):
    return get_room_pokemon(attacker, dungeon)


def get_all_pokemon_on_the_floor(attacker: Pokemon, dungeon: Dungeon):
    return dungeon.floor.spawned


def get_all_team_members_in_the_room(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_room_pokemon(attacker, dungeon)
        if p in get_allies(attacker, dungeon)
    ]


def get_enemies_within_1_tile_range(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_surrounding_pokemon(attacker, dungeon)
        if p in get_enemies(attacker, dungeon)
    ]


def get_enemy_in_front(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_straight_pokemon(attacker, dungeon, 1, False)
        if p in get_enemies(attacker, dungeon)
    ]


def get_enemy_in_front_cuts_corners(attacker, dungeon: Dungeon):
    return [
        p
        for p in get_straight_pokemon(attacker, dungeon, 1, True)
        if p in get_enemies(attacker, dungeon)
    ]


def get_enemy_up_to_2_tiles_away(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_straight_pokemon(attacker, dungeon, 2, True)
        if p in get_enemies(attacker, dungeon)
    ]


def get_facing_pokemon(attacker: Pokemon, dungeon: Dungeon):
    return get_straight_pokemon(attacker, dungeon, 1, False)


def get_facing_pokemon_cuts_corners(attacker: Pokemon, dungeon: Dungeon):
    return get_straight_pokemon(attacker, dungeon, 1, True)


def get_facing_tile_and_2_flanking_tiles(attacker: Pokemon, dungeon: Dungeon):
    # TODO
    return []


def get_line_of_sight(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_straight_pokemon(attacker, dungeon, 10, True)
        if p in get_enemies(attacker, dungeon)
    ]


def get_only_the_allies_in_the_room(attacker: Pokemon, dungeon: Dungeon):
    return [
        p
        for p in get_room_pokemon(attacker, dungeon)
        if p is not attacker and p in get_allies(attacker, dungeon)
    ]


def get_pokemon_within_1_tile_range(attacker: Pokemon, dungeon: Dungeon):
    return get_surrounding_pokemon(attacker, dungeon, 1)


def get_pokemon_within_2_tile_range(attacker: Pokemon, dungeon: Dungeon):
    return get_surrounding_pokemon(attacker, dungeon, 2)


def get_team_members_on_the_floor(attacker: Pokemon, dungeon: Dungeon):
    return get_allies(attacker, dungeon)


def get_user(attacker: Pokemon, dungeon: Dungeon):
    return [attacker]


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


def get_targets(attacker: Pokemon, dungeon: Dungeon, move_range: MoveRange) -> list[Pokemon]:
    return target_getters[move_range](attacker, dungeon)
