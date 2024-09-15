from app.move.move import Move, MoveCategory, MoveRange
from app.model.type import Type
import app.db.database as db


_cursor = db.main_db.cursor()


def load(move_id: int) -> Move:
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
    ) = _cursor.execute(
        """SELECT * FROM moves WHERE move_id = ?""", (move_id,)
    ).fetchone()

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
        frozen,
    )


REGULAR_ATTACK = load(0)
STRUGGLE = load(352)
