from app.model.type import Type, PokemonType
from app.pokemon.level_up_moves import LevelUpMoves
from app.pokemon.stats_growth import StatsGrowth
from app.pokemon.movement_type import MovementType
from app.pokemon.base_pokemon import BasePokemon, GenderedEntity
from app.pokemon.gender import Gender
import app.db.database as db


_cursor = db.main_db.cursor()


def load(poke_id: int):
    gendered_entities = {}
    gs = _cursor.execute(
        "SELECT gender, sprite_id, body_size, exp_yield, weight "
        "FROM gender_entities "
        "WHERE poke_id = ?",
        (poke_id,),
    ).fetchall()
    for g in gs:
        gender = Gender(g[0])
        gendered_entities[gender] = GenderedEntity(
            gender=gender, sprite_id=g[1], body_size=g[2], exp_yield=g[3], weight=g[4]
        )

    (
        pokedex_number,
        name,
        category,
        primary_type,
        secondary_type,
        iq_group,
        movement_type,
    ) = _cursor.execute(
        "SELECT pokedex, name, category, primary_type, secondary_type,"
        " iq_group, movement_type "
        "FROM pokemon "
        "WHERE poke_id = ?",
        (poke_id,),
    ).fetchone()

    type = PokemonType(Type(primary_type), Type(secondary_type))
    movement_type = MovementType(movement_type)

    stats_growth = StatsGrowth(
        *zip(
            *_cursor.execute(
                "SELECT required_exp, hp, attack, defense, sp_attack, sp_defense "
                "FROM stats_growth "
                "WHERE poke_id = ? "
                "ORDER BY level",
                (poke_id,),
            ).fetchall()
        )
    )

    level_up_moves = LevelUpMoves(
        *zip(
            *_cursor.execute(
                "SELECT level, move_id " "FROM level_up_moves " "WHERE poke_id = ?",
                (poke_id,),
            ).fetchall()
        )
    )

    egg_moves = tuple(
        _cursor.execute("SELECT move_id FROM egg_moves WHERE poke_id = ?", (poke_id,))
    )
    hm_tm_moves = tuple(
        _cursor.execute("SELECT move_id FROM hm_tm_moves WHERE poke_id = ?", (poke_id,))
    )

    return BasePokemon(
        name,
        category,
        poke_id,
        pokedex_number,
        type,
        movement_type,
        iq_group,
        gendered_entities,
        stats_growth,
        level_up_moves,
        egg_moves,
        hm_tm_moves,
    )


def get_poke_id_by_pokedex(dex: int) -> int:
    return _cursor.execute(
        "SELECT poke_id FROM pokemon WHERE pokedex = ?", (dex,)
    ).fetchone()[0]
