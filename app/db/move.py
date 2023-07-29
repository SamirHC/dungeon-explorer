import os
import xml.etree.ElementTree as ET

from app.common.constants import GAMEDATA_DIRECTORY
from app.move.move import Move, MoveCategory, MoveRange
from app.model.type import Type


class MoveDatabase:
    def __init__(self):
        self.base_dir = os.path.join(GAMEDATA_DIRECTORY, "moves")
        self.loaded: dict[int, Move] = {}
        self.REGULAR_ATTACK = self[0]
        self.STRUGGLE = self[352]

    def __getitem__(self, move_id: int) -> Move:
        if move_id not in self.loaded:
            self.load(move_id)
        return self.loaded[move_id]

    def load(self, move_id: int):
        if move_id in self.loaded:
            return
        
        filename = os.path.join(self.base_dir, f"{move_id}.xml")
        root = ET.parse(filename).getroot()

        name = root.find("Name").text
        description = root.find("Description").text
        type = Type(int(root.find("Type").text))
        category = MoveCategory(root.find("Category").text)

        stats = root.find("Stats")
        pp = int(stats.find("PP").text)
        power = int(stats.find("Power").text)
        accuracy = int(stats.find("Accuracy").text)
        critical = int(stats.find("Critical").text)
        
        animation = int(root.find("Animation").text)
        chained_hits = int(root.find("ChainedHits").text)
        move_range = MoveRange(root.find("Range").text)

        flags = root.find("Flags")
        ginseng = bool(int(flags.find("Ginseng").text))
        magic_coat = bool(int(flags.find("MagicCoat").text))
        snatch = bool(int(flags.find("Snatch").text))
        muzzled = bool(int(flags.find("Muzzled").text))
        taunt = bool(int(flags.find("Taunt").text))
        frozen = bool(int(flags.find("Frozen").text))
        effect = int(flags.find("Effect").text)

        ai = root.find("AI")
        weight = int(ai.find("Weight").text)
        activation_condition = ai.find("ActivationCondition").text

        self.loaded[move_id] = Move(
            move_id,
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
            move_range,
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
