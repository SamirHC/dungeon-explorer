from app.model.type import Type, TypeEffectiveness, PokemonType
import app.db.database as db


cursor = db.main_db.cursor()


# Stat Stages
def _get_multiplier(stat_name: str, stage: int) -> float:
    return cursor.execute(
        "SELECT multiplier FROM stat_stages " "WHERE stat_name = ? AND stage = ?",
        (stat_name, stage),
    ).fetchone()[0]


def get_attack_multiplier(stage: int) -> float:
    return _get_multiplier("Attack", stage)


def get_defense_multiplier(stage: int) -> float:
    return _get_multiplier("Defense", stage)


def get_accuracy_multiplier(stage: int) -> float:
    return _get_multiplier("Accuracy", stage)


def get_evasion_multiplier(stage: int) -> float:
    return _get_multiplier("Evasion", stage)


# Types
def get_type_multiplier(attack: Type, defend: Type) -> float:
    return get_type_effectiveness(attack, defend).get_multiplier()


def get_type_effectiveness(attack: Type, defend: Type) -> TypeEffectiveness:
    return TypeEffectiveness(
        cursor.execute(
            "SELECT effectiveness FROM type_chart "
            "WHERE attacker_type = ? AND defender_type = ?",
            (attack.value, defend.value),
        ).fetchone()[0]
    )


def get_move_effectiveness(
    move_type: Type, pokemon_type: PokemonType
) -> TypeEffectiveness:
    eff1 = get_type_effectiveness(move_type, pokemon_type.type1)
    eff2 = get_type_effectiveness(move_type, pokemon_type.type2)
    effs = (eff1, eff2)

    le = TypeEffectiveness.LITTLE
    nve = TypeEffectiveness.NOT_VERY
    reg = TypeEffectiveness.REGULAR
    se = TypeEffectiveness.SUPER

    if le in effs:
        return le
    elif nve in effs and se not in effs:
        return nve
    elif se in effs and nve not in effs:
        return se
    return reg
