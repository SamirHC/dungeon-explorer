import enum
from ..dungeon import damage_chart
import os
import xml.etree.ElementTree as ET


class TargetType(enum.Enum):
    USER = "Self"
    ALL = "All"
    ENEMIES = "Enemies"
    ALLIES = "Allies"
    SPECIAL = "Special"


class MoveCategory(enum.Enum):
    PHYSICAL = 0
    SPECIAL = 1
    STATUS = 2


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

    def cuts_corners(self) -> bool:
        return self not in (
            MoveRange.USER,
            MoveRange.ENEMY_IN_FRONT,
            MoveRange.FACING_POKEMON)

    def target_type(self) -> TargetType:
        if self is MoveRange.USER: return TargetType.USER
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
        return TargetType.SPECIAL

    def straight(self) -> bool:
        return self in (
            MoveRange.ENEMY_IN_FRONT,
            MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS,
            MoveRange.LINE_OF_SIGHT,
            MoveRange.FACING_POKEMON,
            MoveRange.FACING_POKEMON_CUTS_CORNERS
        )


class Move:
    MOVE_DIRECTORY = os.path.join(os.getcwd(), "data", "gamedata", "moves")

    def __init__(self, move_id: str):
        self.move_id = move_id
        root = ET.parse(self.get_file()).getroot()

        self._name = root.find("Name").text
        self._description = root.find("Description").text
        self._type = damage_chart.Type(int(root.find("Type").text))
        self._category = MoveCategory(int(root.find("Category").text))

        stats = root.find("Stats")
        self._pp = int(stats.find("PP").text)
        self._power = int(stats.find("Power").text)
        self._accuracy = int(stats.find("Accuracy").text)
        self._critical = int(stats.find("Critical").text)
        
        self._animation = root.find("Animation").text
        self._chained_hits = int(root.find("ChainedHits").text)
        self._range_category = MoveRange(root.find("Range").text)
        self._cuts_corners = self._range_category.cuts_corners()

        flags = root.find("Flags")
        self._ginseng = int(flags.find("Ginseng").text)
        self._magic_coat = int(flags.find("MagicCoat").text)
        self._snatch = int(flags.find("Snatch").text)
        self._muzzled = int(flags.find("Muzzled").text)
        self._taunt = int(flags.find("Taunt").text)
        self._frozen = int(flags.find("Frozen").text)
        self._effect = int(flags.find("Effect").text)

        ai = root.find("AI")
        self._weight = int(ai.find("Weight").text)
        self._activation_condition = ai.find("ActivationCondition").text

    def get_file(self):
        return os.path.join(self.MOVE_DIRECTORY, f"{self.move_id}.xml")

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> damage_chart.Type:
        return self._type

    @property
    def category(self) -> MoveCategory:
        return self._category

    @property
    def pp(self) -> int:
        return self._pp

    @property
    def accuracy(self) -> int:
        return self._accuracy

    @property
    def critical(self) -> int:
        return self._critical

    @property
    def power(self) -> int:
        return self._power

    @property
    def animation(self) -> str:
        return self._animation

    @property
    def chained_hits(self) -> int:
        return self._chained_hits

    @property
    def cuts_corners(self) -> bool:
        return self._cuts_corners

    @property
    def range_category(self) -> MoveRange:
        return self._range_category

    @property
    def weight(self) -> int:
        return self._weight

    @property
    def activation_condition(self) -> str:
        return self._activation_condition

    @property
    def effect(self) -> int:
        return self._effect
