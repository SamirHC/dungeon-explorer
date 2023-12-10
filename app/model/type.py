import enum


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


class PokemonType:
    def __init__(self, type1: Type, type2: Type):
        self.type1 = type1
        self.type2 = type2

    def __contains__(self, type: Type) -> bool:
        return self.type1 is type or self.type2 is type
