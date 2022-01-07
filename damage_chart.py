import enum

stage_dict = {
    0: 0.5,  # Levels for ATK,DEF,SPATK,SPDEF
    1: 0.52,
    2: 0.54,
    3: 0.56,
    4: 0.58,
    5: 0.6,
    6: 0.63,
    7: 0.67,
    8: 0.7,
    9: 0.8,
    10: 1,
    11: 1.2,
    12: 1.3,
    13: 1.4,
    14: 1.5,
    15: 1.6,
    16: 1.65,
    17: 1.7,
    18: 1.75,
    19: 1.8,
    20: 1.85
}


class TypeEffectiveness:
    SUPER = 1.4
    NORMAL = 1
    NOT_VERY = 0.7
    NONE = 0


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


class TypeChart:
    def get_multiplier(attack: Type, defend: Type) -> float:
        return TypeChart.type_chart[attack][defend]

    type_chart = {
        Type.NORMAL: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NOT_VERY,
            Type.GHOST: TypeEffectiveness.NONE,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL
        },
        Type.FIRE: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NOT_VERY,
            Type.WATER: TypeEffectiveness.NOT_VERY,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.SUPER,
            Type.ICE: TypeEffectiveness.SUPER,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.SUPER,
            Type.ROCK: TypeEffectiveness.NOT_VERY,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NOT_VERY,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.SUPER,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL
        },
        Type.WATER: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.SUPER,
            Type.WATER: TypeEffectiveness.NOT_VERY,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NOT_VERY,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.SUPER,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.SUPER,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NOT_VERY,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NORMAL,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.GRASS: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NOT_VERY,
            Type.WATER: TypeEffectiveness.SUPER,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NOT_VERY,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NOT_VERY,
            Type.GROUND: TypeEffectiveness.SUPER,
            Type.FLYING: TypeEffectiveness.NOT_VERY,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NOT_VERY,
            Type.ROCK: TypeEffectiveness.SUPER,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NOT_VERY,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.ELECTRIC: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.SUPER,
            Type.ELECTRIC: TypeEffectiveness.NOT_VERY,
            Type.GRASS: TypeEffectiveness.NOT_VERY,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NONE,
            Type.FLYING: TypeEffectiveness.SUPER,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NOT_VERY,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NORMAL,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.ICE: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NOT_VERY,
            Type.WATER: TypeEffectiveness.NOT_VERY,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.SUPER,
            Type.ICE: TypeEffectiveness.NOT_VERY,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.SUPER,
            Type.FLYING: TypeEffectiveness.SUPER,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.SUPER,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.FIGHTING: {
            Type.NORMAL: TypeEffectiveness.SUPER,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.SUPER,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NOT_VERY,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NOT_VERY,
            Type.PSYCHIC: TypeEffectiveness.NOT_VERY,
            Type.BUG: TypeEffectiveness.NOT_VERY,
            Type.ROCK: TypeEffectiveness.SUPER,
            Type.GHOST: TypeEffectiveness.NONE,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.SUPER,
            Type.STEEL: TypeEffectiveness.SUPER,
            Type.FAIRY: TypeEffectiveness.NOT_VERY,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.POISON: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.SUPER,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NOT_VERY,
            Type.GROUND: TypeEffectiveness.NOT_VERY,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NOT_VERY,
            Type.GHOST: TypeEffectiveness.NOT_VERY,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NONE,
            Type.FAIRY: TypeEffectiveness.SUPER,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.GROUND: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.SUPER,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.SUPER,
            Type.GRASS: TypeEffectiveness.NOT_VERY,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.SUPER,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NONE,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NOT_VERY,
            Type.ROCK: TypeEffectiveness.SUPER,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.SUPER,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.FLYING: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NOT_VERY,
            Type.GRASS: TypeEffectiveness.SUPER,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.SUPER,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.SUPER,
            Type.ROCK: TypeEffectiveness.NOT_VERY,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.PSYCHIC: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.SUPER,
            Type.POISON: TypeEffectiveness.SUPER,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NOT_VERY,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NONE,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.BUG: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NOT_VERY,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.SUPER,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NOT_VERY,
            Type.POISON: TypeEffectiveness.NOT_VERY,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NOT_VERY,
            Type.PSYCHIC: TypeEffectiveness.SUPER,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NOT_VERY,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.SUPER,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NOT_VERY,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.ROCK: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.SUPER,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.SUPER,
            Type.FIGHTING: TypeEffectiveness.NOT_VERY,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NOT_VERY,
            Type.FLYING: TypeEffectiveness.SUPER,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.SUPER,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.GHOST: {
            Type.NORMAL: TypeEffectiveness.NONE,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.SUPER,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.SUPER,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NOT_VERY,
            Type.STEEL: TypeEffectiveness.NORMAL,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.DRAGON: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.SUPER,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NOT_VERY,
            Type.FAIRY: TypeEffectiveness.NONE,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.DARK: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NOT_VERY,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.SUPER,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.SUPER,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NOT_VERY,
            Type.STEEL: TypeEffectiveness.NORMAL,
            Type.FAIRY: TypeEffectiveness.NOT_VERY,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        },
        Type.STEEL: {Type.NORMAL: TypeEffectiveness.NORMAL,
                     Type.FIRE: TypeEffectiveness.NOT_VERY,
                     Type.WATER: TypeEffectiveness.NOT_VERY,
                     Type.ELECTRIC: TypeEffectiveness.NOT_VERY,
                     Type.GRASS: TypeEffectiveness.NORMAL,
                     Type.ICE: TypeEffectiveness.SUPER,
                     Type.FIGHTING: TypeEffectiveness.NORMAL,
                     Type.POISON: TypeEffectiveness.NORMAL,
                     Type.GROUND: TypeEffectiveness.NORMAL,
                     Type.FLYING: TypeEffectiveness.NORMAL,
                     Type.PSYCHIC: TypeEffectiveness.NORMAL,
                     Type.BUG: TypeEffectiveness.NORMAL,
                     Type.ROCK: TypeEffectiveness.SUPER,
                     Type.GHOST: TypeEffectiveness.NORMAL,
                     Type.DRAGON: TypeEffectiveness.NORMAL,
                     Type.DARK: TypeEffectiveness.NORMAL,
                     Type.STEEL: TypeEffectiveness.NOT_VERY,
                     Type.FAIRY: TypeEffectiveness.SUPER,
                     Type.TYPELESS: TypeEffectiveness.NORMAL,
                     },
        Type.FAIRY: {Type.NORMAL: TypeEffectiveness.NORMAL,
                     Type.FIRE: TypeEffectiveness.NOT_VERY,
                     Type.WATER: TypeEffectiveness.NORMAL,
                     Type.ELECTRIC: TypeEffectiveness.NORMAL,
                     Type.GRASS: TypeEffectiveness.NORMAL,
                     Type.ICE: TypeEffectiveness.NORMAL,
                     Type.FIGHTING: TypeEffectiveness.SUPER,
                     Type.POISON: TypeEffectiveness.NOT_VERY,
                     Type.GROUND: TypeEffectiveness.NORMAL,
                     Type.FLYING: TypeEffectiveness.NORMAL,
                     Type.PSYCHIC: TypeEffectiveness.NORMAL,
                     Type.BUG: TypeEffectiveness.NORMAL,
                     Type.ROCK: TypeEffectiveness.NORMAL,
                     Type.GHOST: TypeEffectiveness.NORMAL,
                     Type.DRAGON: TypeEffectiveness.SUPER,
                     Type.DARK: TypeEffectiveness.SUPER,
                     Type.STEEL: TypeEffectiveness.NOT_VERY,
                     Type.FAIRY: TypeEffectiveness.NORMAL,
                     Type.TYPELESS: TypeEffectiveness.NORMAL,
                     },
        Type.TYPELESS: {
            Type.NORMAL: TypeEffectiveness.NORMAL,
            Type.FIRE: TypeEffectiveness.NORMAL,
            Type.WATER: TypeEffectiveness.NORMAL,
            Type.ELECTRIC: TypeEffectiveness.NORMAL,
            Type.GRASS: TypeEffectiveness.NORMAL,
            Type.ICE: TypeEffectiveness.NORMAL,
            Type.FIGHTING: TypeEffectiveness.NORMAL,
            Type.POISON: TypeEffectiveness.NORMAL,
            Type.GROUND: TypeEffectiveness.NORMAL,
            Type.FLYING: TypeEffectiveness.NORMAL,
            Type.PSYCHIC: TypeEffectiveness.NORMAL,
            Type.BUG: TypeEffectiveness.NORMAL,
            Type.ROCK: TypeEffectiveness.NORMAL,
            Type.GHOST: TypeEffectiveness.NORMAL,
            Type.DRAGON: TypeEffectiveness.NORMAL,
            Type.DARK: TypeEffectiveness.NORMAL,
            Type.STEEL: TypeEffectiveness.NORMAL,
            Type.FAIRY: TypeEffectiveness.NORMAL,
            Type.TYPELESS: TypeEffectiveness.NORMAL,
        }
    }
