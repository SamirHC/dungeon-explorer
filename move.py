import enum
import damage_chart
import os
import xml.etree.ElementTree as ET


class MoveCategory(enum.Enum):
    PHYSICAL = 0
    SPECIAL = 1
    STATUS = 2


class MoveRange(enum.Enum):
    SELF = 0
    DIRECTLY_IN_FRONT = 1
    UP_TO_TWO_IN_FRONT = 2
    IN_LINE_OF_SIGHT = 3
    ADJACENT = 4
    IN_SAME_ROOM = 5
    FLOOR_WIDE = 6


class EffectType(enum.Enum):
    DAMAGE = "Damage"
    FIXED_DAMAGE = "FixedDamage"


class TargetType(enum.Enum):
    SELF = "Self"
    ALL = "All"
    ENEMIES = "Enemies"
    ALLIES = "Allies"


class MoveEffect:
    def __init__(self, root: ET.Element):
        self._target = TargetType(root.find("Target").text)
        self._animation_name = root.find("Animation").text
        self._effect_type = EffectType(root.find("EffectType").text)
        self._power = int(root.find("Power").text)
        self._cuts_corners = int(root.find("CutsCorners").text)
        self._range_category = MoveRange(int(root.find("RangeCategory").text))

    @property
    def target(self) -> TargetType:
        return self._target

    @property
    def animation_name(self) -> str:
        return self._animation_name

    @property
    def effect_type(self) -> EffectType:
        return self._effect_type

    @property
    def power(self) -> int:
        return self._power

    @property
    def cuts_corners(self) -> bool:
        return self._cuts_corners

    @property
    def range_category(self) -> MoveRange:
        return self._range_category


class Move:
    MOVE_DIRECTORY = os.path.join(os.getcwd(), "gamedata", "moves")

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
        self._max_upgrade = int(root.find("MaxUpgrade").text)

        flags = root.find("Flags")
        self._affected_by_magic_coat = int(flags.find("AffectedByMagicCoat"))
        self._is_snatchable = int(flags.find("IsSnatchable"))
        self._uses_mouth = int(flags.find("UsesMouth"))
        self._ignores_taunt = int(flags.find("IgnoresTaunt"))
        self._ignores_frozen = int(flags.find("IgnoresFrozen"))

        range = root.find("Range")
        self._cuts_corners = int(range.find("CutsCorners"))
        self._range_category = MoveRange(range.find("RangeCategory"))

        ai = root.find("AI")
        self._weight = int(ai.find("Weight"))
        self._activation_condition = ai.find("ActivationCondition")

        self._primary_effects = []
        for effect_element in root.find("PrimaryEffects").findall("Effect"):
            self._primary_effects.append(MoveEffect(effect_element))

        self._extra_effects = []
        for effect_element in root.find("ExtraEffects").findall("Effect"):
            self._extra_effects.append(MoveEffect(effect_element))

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
