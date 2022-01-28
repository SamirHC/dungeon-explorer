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


class MoveEffect:
    def __init__(self, root: ET.Element):
        self.root = root
        self.parse()

    def parse(self):
        self.target = self.root.find("Target").text
        self.animation = self.root.find("Animation").text
        self.effect_type = self.root.find("EffectType").text
        self.power = int(self.root.find("Power").text)
        self.cuts_corners = int(self.root.find("CutsCorners").text)
        self.range_category = MoveRange(
            int(self.root.find("RangeCategory").text))


class Move:
    MOVE_DIRECTORY = os.path.join(os.getcwd(), "gamedata", "moves")

    def __init__(self, move_id: str):
        self.move_id = move_id
        file = self.get_file()
        tree = ET.parse(file)
        root = tree.getroot()

        self._name = root.find("Name").text
        self._type = damage_chart.Type(int(root.find("Type").text))
        self._category = MoveCategory(int(root.find("Category").text))
        self._pp = int(root.find("PP").text)
        self._accuracy = int(root.find("Accuracy").text)
        self._critical = int(root.find("Critical").text)

        self._effects = []
        for effect_element in root.find("Effects").findall("Effect"):
            self._effects.append(MoveEffect(effect_element))

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
    def effects(self) -> list[MoveEffect]:
        return self._effects