import os
import xml.etree.ElementTree as ET
import sqlite3


from app.common.constants import GAMEDATA_DIRECTORY
from app.move.move import Move, MoveCategory, MoveRange
from app.model.type import Type


class MoveDatabase:
    def __init__(self):
        self.base_dir = os.path.join(GAMEDATA_DIRECTORY, "moves")
        self.conn = sqlite3.connect(os.path.join(GAMEDATA_DIRECTORY, "gamedata.db"))
        self.cursor = self.conn.cursor()
        self.REGULAR_ATTACK = self[0]
        self.STRUGGLE = self[352]

    def __getitem__(self, move_id: int) -> Move:
        return self.load(move_id)

    def load(self, move_id: int):
        self.cursor.execute(f"""SELECT * FROM moves WHERE move_id = {move_id}""")
        result = self.cursor.fetchone()

        move_id, name, description, type, category, pp, power, accuracy, \
            critical, animation, chained_hits, move_range, ginseng, magic_coat, \
            snatch, muzzled, taunt, frozen, weight, activation_condition = result
        
        type = Type(type)
        category = MoveCategory[category]
        move_range = MoveRange(move_range)

        return Move(
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
            frozen
        )
