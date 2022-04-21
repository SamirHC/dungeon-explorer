import enum


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
    SUPER = 1.4
    REGULAR = 1
    NOT_VERY = 0.7
    LITTLE = 0.5

    def get_message(self) -> str:
        if self is TypeEffectiveness.SUPER:
            return "It's super effective!"
        elif self is TypeEffectiveness.REGULAR:
            return ""
        elif self is TypeEffectiveness.NOT_VERY:
            return "It's not very effective..."
        elif self is TypeEffectiveness.LITTLE:
            return "It has little effect..."


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
    return get_type_effectiveness(attack, defend).value

def get_type_effectiveness(attack: Type, defend: Type) -> TypeEffectiveness:
    # Temporary fix
    if attack in (Type.RANDOM, Type.SPECIAL):
        attack = Type.TYPELESS
    if defend in (Type.RANDOM, Type.SPECIAL):
        defend = Type.TYPELESS
    return type_chart[attack][defend]

type_chart = {
    Type.NORMAL: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.NOT_VERY,
        Type.GHOST: TypeEffectiveness.LITTLE,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR
    },
    Type.FIRE: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.NOT_VERY,
        Type.WATER: TypeEffectiveness.NOT_VERY,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.SUPER,
        Type.ICE: TypeEffectiveness.SUPER,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.SUPER,
        Type.ROCK: TypeEffectiveness.NOT_VERY,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.NOT_VERY,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.SUPER,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR
    },
    Type.WATER: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.SUPER,
        Type.WATER: TypeEffectiveness.NOT_VERY,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.NOT_VERY,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.SUPER,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.SUPER,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.NOT_VERY,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.REGULAR,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.GRASS: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.NOT_VERY,
        Type.WATER: TypeEffectiveness.SUPER,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.NOT_VERY,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.NOT_VERY,
        Type.GROUND: TypeEffectiveness.SUPER,
        Type.FLYING: TypeEffectiveness.NOT_VERY,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.NOT_VERY,
        Type.ROCK: TypeEffectiveness.SUPER,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.NOT_VERY,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.ELECTRIC: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.SUPER,
        Type.ELECTRIC: TypeEffectiveness.NOT_VERY,
        Type.GRASS: TypeEffectiveness.NOT_VERY,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.LITTLE,
        Type.FLYING: TypeEffectiveness.SUPER,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.NOT_VERY,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.REGULAR,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.ICE: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.NOT_VERY,
        Type.WATER: TypeEffectiveness.NOT_VERY,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.SUPER,
        Type.ICE: TypeEffectiveness.NOT_VERY,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.SUPER,
        Type.FLYING: TypeEffectiveness.SUPER,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.SUPER,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.FIGHTING: {
        Type.NORMAL: TypeEffectiveness.SUPER,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.SUPER,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.NOT_VERY,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.NOT_VERY,
        Type.PSYCHIC: TypeEffectiveness.NOT_VERY,
        Type.BUG: TypeEffectiveness.NOT_VERY,
        Type.ROCK: TypeEffectiveness.SUPER,
        Type.GHOST: TypeEffectiveness.LITTLE,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.SUPER,
        Type.STEEL: TypeEffectiveness.SUPER,
        Type.FAIRY: TypeEffectiveness.NOT_VERY,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.POISON: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.SUPER,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.NOT_VERY,
        Type.GROUND: TypeEffectiveness.NOT_VERY,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.NOT_VERY,
        Type.GHOST: TypeEffectiveness.NOT_VERY,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.LITTLE,
        Type.FAIRY: TypeEffectiveness.SUPER,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.GROUND: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.SUPER,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.SUPER,
        Type.GRASS: TypeEffectiveness.NOT_VERY,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.SUPER,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.LITTLE,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.NOT_VERY,
        Type.ROCK: TypeEffectiveness.SUPER,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.SUPER,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.FLYING: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.NOT_VERY,
        Type.GRASS: TypeEffectiveness.SUPER,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.SUPER,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.SUPER,
        Type.ROCK: TypeEffectiveness.NOT_VERY,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.PSYCHIC: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.SUPER,
        Type.POISON: TypeEffectiveness.SUPER,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.NOT_VERY,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.LITTLE,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.BUG: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.NOT_VERY,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.SUPER,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.NOT_VERY,
        Type.POISON: TypeEffectiveness.NOT_VERY,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.NOT_VERY,
        Type.PSYCHIC: TypeEffectiveness.SUPER,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.NOT_VERY,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.SUPER,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.NOT_VERY,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.ROCK: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.SUPER,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.SUPER,
        Type.FIGHTING: TypeEffectiveness.NOT_VERY,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.NOT_VERY,
        Type.FLYING: TypeEffectiveness.SUPER,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.SUPER,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.GHOST: {
        Type.NORMAL: TypeEffectiveness.LITTLE,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.SUPER,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.SUPER,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.NOT_VERY,
        Type.STEEL: TypeEffectiveness.REGULAR,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.DRAGON: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.SUPER,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.LITTLE,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.DARK: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.NOT_VERY,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.SUPER,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.SUPER,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.NOT_VERY,
        Type.STEEL: TypeEffectiveness.REGULAR,
        Type.FAIRY: TypeEffectiveness.NOT_VERY,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.STEEL: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.NOT_VERY,
        Type.WATER: TypeEffectiveness.NOT_VERY,
        Type.ELECTRIC: TypeEffectiveness.NOT_VERY,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.SUPER,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.SUPER,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.SUPER,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.FAIRY: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.NOT_VERY,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.SUPER,
        Type.POISON: TypeEffectiveness.NOT_VERY,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.SUPER,
        Type.DARK: TypeEffectiveness.SUPER,
        Type.STEEL: TypeEffectiveness.NOT_VERY,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    },
    Type.TYPELESS: {
        Type.NORMAL: TypeEffectiveness.REGULAR,
        Type.FIRE: TypeEffectiveness.REGULAR,
        Type.WATER: TypeEffectiveness.REGULAR,
        Type.ELECTRIC: TypeEffectiveness.REGULAR,
        Type.GRASS: TypeEffectiveness.REGULAR,
        Type.ICE: TypeEffectiveness.REGULAR,
        Type.FIGHTING: TypeEffectiveness.REGULAR,
        Type.POISON: TypeEffectiveness.REGULAR,
        Type.GROUND: TypeEffectiveness.REGULAR,
        Type.FLYING: TypeEffectiveness.REGULAR,
        Type.PSYCHIC: TypeEffectiveness.REGULAR,
        Type.BUG: TypeEffectiveness.REGULAR,
        Type.ROCK: TypeEffectiveness.REGULAR,
        Type.GHOST: TypeEffectiveness.REGULAR,
        Type.DRAGON: TypeEffectiveness.REGULAR,
        Type.DARK: TypeEffectiveness.REGULAR,
        Type.STEEL: TypeEffectiveness.REGULAR,
        Type.FAIRY: TypeEffectiveness.REGULAR,
        Type.TYPELESS: TypeEffectiveness.REGULAR,
    }
}
