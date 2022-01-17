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
        self.parse_file()

    def get_effects(self) -> list[MoveEffect]:
        effects = []
        for effect_element in self.root.find("Effects").findall("Effect"):
            effects.append(MoveEffect(effect_element))
        return effects

    def parse_file(self):
        file = os.path.join(self.MOVE_DIRECTORY, f"{self.move_id}.xml")
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.name = self.root.find("Name").text
        self.type = damage_chart.Type(int(self.root.find("Type").text))
        self.category = MoveCategory(int(self.root.find("Category").text))
        self.pp = int(self.root.find("PP").text)
        self.accuracy = int(self.root.find("Accuracy").text)
        self.critical = int(self.root.find("Critical").text)
        self.effects = self.get_effects()
