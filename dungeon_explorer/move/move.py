import dataclasses
import enum
import os
import xml.etree.ElementTree as ET

from dungeon_explorer.dungeon import damage_chart


class TargetType(enum.Enum):
    USER = "Self"
    ALL = "All"
    ENEMIES = "Enemies"
    ALLIES = "Allies"
    SPECIAL = "Special"


class MoveCategory(enum.Enum):
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    OTHER = "Other"


class MoveRange(enum.Enum):
    USER = "User"
    ENEMY_IN_FRONT = "Enemy in front"
    ENEMY_IN_FRONT_CUTS_CORNERS = "Enemy in front, cuts corners"
    FACING_POKEMON = "Facing Pokemon"
    FACING_POKEMON_CUTS_CORNERS = "Facing Pokemon, cuts corners"
    ENEMY_UP_TO_TWO_TILES_AWAY = "Enemy up to 2 tiles away"
    LINE_OF_SIGHT = "Line of sight"
    ENEMIES_WITHIN_ONE_TILE_RANGE = "Enemies within 1-tile range"
    ALL_ENEMIES_IN_THE_ROOM = "All enemies in the room"
    ALL_ALLIES_IN_THE_ROOM = "All allies in the room"
    EVERYONE_IN_THE_ROOM = "Everyone in the room"
    EVERYONE_IN_THE_ROOM_EXCEPT_THE_USER = "Everyone in the room, except the user"
    FLOOR = "Floor"
    WALL = "Wall"
    VARIES = "Varies"
    ITEM = "Item"

    def cuts_corners(self) -> bool:
        return self not in (
            MoveRange.USER,
            MoveRange.ENEMY_IN_FRONT,
            MoveRange.FACING_POKEMON)

    def target_type(self) -> TargetType:
        if self is MoveRange.USER:
            return TargetType.USER
        if self in (
            MoveRange.ENEMY_IN_FRONT,
            MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS,
            MoveRange.ENEMY_UP_TO_TWO_TILES_AWAY,
            MoveRange.ENEMIES_WITHIN_ONE_TILE_RANGE,
            MoveRange.ALL_ENEMIES_IN_THE_ROOM):
            return TargetType.ENEMIES
        if self in (
            MoveRange.FACING_POKEMON,
            MoveRange.FACING_POKEMON_CUTS_CORNERS,
            MoveRange.LINE_OF_SIGHT):
            return TargetType.ALL
        if self is MoveRange.ALL_ALLIES_IN_THE_ROOM:
            return TargetType.ALLIES
        return TargetType.SPECIAL

    def is_straight(self) -> bool:
        return self in (
            MoveRange.ENEMY_IN_FRONT,
            MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS,
            MoveRange.ENEMY_UP_TO_TWO_TILES_AWAY,
            MoveRange.LINE_OF_SIGHT,
            MoveRange.FACING_POKEMON,
            MoveRange.FACING_POKEMON_CUTS_CORNERS
        )

    def is_surrounding(self) -> bool:
        return self is MoveRange.ENEMIES_WITHIN_ONE_TILE_RANGE
    
    def is_room_wide(self) -> bool:
        return self in (
            MoveRange.ALL_ENEMIES_IN_THE_ROOM,
            MoveRange.ALL_ALLIES_IN_THE_ROOM,
            MoveRange.EVERYONE_IN_THE_ROOM,
            MoveRange.EVERYONE_IN_THE_ROOM_EXCEPT_THE_USER
        )

    def distance(self) -> int:
        if self in (
            MoveRange.ENEMY_IN_FRONT,
            MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS,
            MoveRange.FACING_POKEMON,
            MoveRange.FACING_POKEMON_CUTS_CORNERS,
            MoveRange.ENEMIES_WITHIN_ONE_TILE_RANGE):
            return 1
        if self is MoveRange.ENEMY_UP_TO_TWO_TILES_AWAY: return 2
        if self is MoveRange.LINE_OF_SIGHT: return 10
        return 0


@dataclasses.dataclass(frozen=True)
class Move:
    name: str
    description: str
    type: damage_chart.Type
    category: MoveCategory
    pp: int
    accuracy: int
    critical: int
    power: int
    animation: int
    chained_hits: int
    range_category: MoveRange
    cuts_corners: bool
    weight: int
    activation_condition: str
    ginseng: bool
    magic_coat: bool
    snatch: bool
    muzzled: bool
    taunt: bool
    frozen: bool
    effect: int


def load_move(move_id) -> Move:
    MOVE_DIRECTORY = os.path.join("data", "gamedata", "moves")
    filename = os.path.join(MOVE_DIRECTORY, f"{move_id}.xml")
    root = ET.parse(filename).getroot()

    name = root.find("Name").text
    description = root.find("Description").text
    type = damage_chart.Type(int(root.find("Type").text))
    category = MoveCategory(root.find("Category").text)

    stats = root.find("Stats")
    pp = int(stats.find("PP").text)
    power = int(stats.find("Power").text)
    accuracy = int(stats.find("Accuracy").text)
    critical = int(stats.find("Critical").text)
    
    animation = int(root.find("Animation").text)
    chained_hits = int(root.find("ChainedHits").text)
    range_category = MoveRange(root.find("Range").text)
    cuts_corners = range_category.cuts_corners()

    flags = root.find("Flags")
    ginseng = bool(int(flags.find("Ginseng").text))
    magic_coat = bool(int(flags.find("MagicCoat").text))
    snatch = bool(int(flags.find("Snatch").text))
    muzzled = bool(int(flags.find("Muzzled").text))
    taunt = bool(int(flags.find("Taunt").text))
    frozen = bool(int(flags.find("Frozen").text))
    effect = bool(int(flags.find("Effect").text))

    ai = root.find("AI")
    weight = int(ai.find("Weight").text)
    activation_condition = ai.find("ActivationCondition").text

    return Move(
        name,
        description,
        type,
        category,
        pp,
        accuracy,
        critical,
        power,
        animation,
        chained_hits,
        range_category,
        cuts_corners,
        weight,
        activation_condition,
        ginseng,
        magic_coat,
        snatch,
        muzzled,
        taunt,
        frozen,
        effect
    )

REGULAR_ATTACK = load_move("0")