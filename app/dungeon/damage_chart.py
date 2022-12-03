import enum
import csv
import os


DENOMINATOR = 256
stat_stage_chart = {}
with open(os.path.join("data", "gamedata", "stat_stage_chart.csv"), newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        stat_stage_chart[row["Stat"]] = tuple(int(row[str(stage)]) for stage in range(-10, 11))

def get_attack_multiplier(stage: int) -> float:
    return stat_stage_chart["Attack"][stage] / DENOMINATOR

def get_defense_multiplier(stage: int) -> float:
    return stat_stage_chart["Defense"][stage] / DENOMINATOR

def get_accuracy_multiplier(stage: int) -> float:
    return stat_stage_chart["Accuracy"][stage] / DENOMINATOR

def get_evasion_multiplier(stage: int) -> float:
    return stat_stage_chart["Evasion"][stage] / DENOMINATOR


class TypeEffectiveness(enum.Enum):
    LITTLE = 0
    NOT_VERY = 1
    REGULAR = 2
    SUPER = 3

    def get_message(self) -> str:
        if self is TypeEffectiveness.SUPER:
            return "It's super effective!"
        elif self is TypeEffectiveness.REGULAR:
            return ""
        elif self is TypeEffectiveness.NOT_VERY:
            return "It's not very effective..."
        elif self is TypeEffectiveness.LITTLE:
            return "It has little effect..."
    
    def get_multiplier(self) -> float:
        if self is TypeEffectiveness.SUPER:
            return 1.4
        elif self is TypeEffectiveness.REGULAR:
            return 1
        elif self is TypeEffectiveness.NOT_VERY:
            return 0.7
        elif self is TypeEffectiveness.LITTLE:
            return 0.5


class Type(enum.Enum):
    TYPELESS = 0
    NORMAL = 1
    FIRE = 2
    WATER = 3
    GRASS = 4
    ELECTRIC = 5
    ICE = 6
    FIGHTING = 7
    POISON = 8
    GROUND = 9
    FLYING = 10
    PSYCHIC = 11
    BUG = 12
    ROCK = 13
    GHOST = 14
    DRAGON = 15
    DARK = 16
    STEEL = 17
    FAIRY = 18
    RANDOM = 19
    SPECIAL = 20

def get_type_multiplier(attack: Type, defend: Type) -> float:
    return get_type_effectiveness(attack, defend).get_multiplier()

def get_type_effectiveness(attack: Type, defend: Type) -> TypeEffectiveness:
    # Temporary fix
    if attack in (Type.RANDOM, Type.SPECIAL):
        attack = Type.TYPELESS
    if defend in (Type.RANDOM, Type.SPECIAL):
        defend = Type.TYPELESS
    if attack is Type.TYPELESS or defend is Type.TYPELESS:
        return TypeEffectiveness.REGULAR
    return type_chart[attack][defend]

type_chart: dict[Type, dict[Type, TypeEffectiveness]] = {}
with open(os.path.join("data", "gamedata", "damage_chart.csv"), newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        atk_type_dict = {}
        for def_type in Type:
            if def_type in (Type.TYPELESS, Type.RANDOM, Type.SPECIAL):
                continue
            atk_type_dict[def_type] = TypeEffectiveness(int(row[def_type.name]))
        type_chart[Type[row["Attacking"]]] = atk_type_dict
