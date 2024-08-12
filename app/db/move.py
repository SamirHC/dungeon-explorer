from app.move.move import Move, MoveCategory, MoveRange
from app.model.type import Type
import app.db.database as db


class MoveDatabase:
    def __init__(self):
        self.cursor = db.main_db.cursor()
        self.cache = {}
        self.REGULAR_ATTACK = self[0]
        self.STRUGGLE = self[352]

    def __getitem__(self, move_id: int) -> Move:
        if move_id not in self.cache:
            self.load(move_id)
        return self.cache[move_id]

    def load(self, move_id: int):
        self.cursor.execute("""SELECT * FROM moves WHERE move_id = ?""", (move_id,))
        result = self.cursor.fetchone()

        (
            move_id,
            name,
            description,
            type,
            category,
            pp,
            power,
            accuracy,
            critical,
            animation,
            chained_hits,
            move_range,
            ginseng,
            magic_coat,
            snatch,
            muzzled,
            taunt,
            frozen,
            weight,
            activation_condition,
        ) = result

        type = Type(type)
        category = MoveCategory[category]
        move_range = MoveRange(move_range)

        self.cache[move_id] = Move(
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
        )
