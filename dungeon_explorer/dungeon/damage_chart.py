import enum
import csv
import os


DENOMINATOR = 256
ATTACK_NUMERATORS = (
    128, 133, 138, 143, 148, 153, 161, 171, 179, 204,
    256,
    307, 332, 358, 384, 409, 422, 435, 448, 460, 473
)
DEFENSE_NUMERATORS = (
    7, 12, 25, 38, 51, 64, 76, 102, 128, 179,
    256,
    332, 409, 486, 537, 588, 640, 691, 742, 793, 844
)
ACCURACY_NUMERATORS = (
    84, 89, 94, 102, 110, 115, 140, 153, 179, 204,
    256,
    320, 384, 409, 422, 435, 448, 460, 473, 486, 512
)
EVASION_NUMERATORS = (
    512, 486, 473, 460, 448, 435, 422, 409, 384, 345,
    256,
    204, 179, 153, 128, 102, 89, 76, 64, 51, 38
)

def get_attack_multiplier(stage: int) -> float:
    return ATTACK_NUMERATORS[stage] / DENOMINATOR

def get_defense_multiplier(stage: int) -> float:
    return DEFENSE_NUMERATORS[stage] / DENOMINATOR

def get_accuracy_multiplier(stage: int) -> float:
    return ACCURACY_NUMERATORS[stage] / DENOMINATOR

def get_evasion_multiplier(stage: int) -> float:
    return EVASION_NUMERATORS[stage] / DENOMINATOR


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
