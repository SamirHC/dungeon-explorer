from enum import Enum, auto


class StatusEffect(Enum):
    # Sleep related conditions
    ASLEEP = auto()
    SLEEPLESS = auto()
    NIGHTMARE = auto()
    YAWNING = auto()
    NAPPING = auto()
    # Major status conditions
    BURNED = auto()
    FROZEN = auto()
    POISONED = auto()
    BADLY_POISONED = auto()
    PARALYZED = auto()
    # Mobility related
    HALF_SPEED = auto()
    DOUBLE_SPEED = auto()
    SHADOW_HOLD = auto()
    PETRIFIED = auto()
    INGRAIN = auto()
    WRAPPED = auto()
    WRAP = auto()
    CONSTRICTION = auto()
    MOBILE = auto()
    SLIP = auto()
    MAGNET_RISE = auto()
    # Move execution related
    CRINGE = auto()
    CONFUSED = auto()
    INFATUATED = auto()
    PAUSED = auto()
    COWERING = auto()
    WHIFFER = auto()
    MUZZLED = auto()
    TAUNTED = auto()
    ENCORE = auto()
    DECOY = auto()
    TERRIFIED = auto()
    SNATCH = auto()
    CHARGING = auto()
    ENRAGED = auto()
    STOCKPILING = auto()
    # Move-based status conditions
    BIDE = auto()
    SOLAR_BEAM = auto()
    SKY_ATTACK = auto()
    RAZOR_WIND = auto()
    FOCUS_PUNCH = auto()
    SKULL_BASH = auto()
    FLYING = auto()
    BOUNCING = auto()
    DIVING = auto()
    DIGGING = auto()
    SHADOW_FORCE = auto()
    # Shield status conditions
    REFLECT = auto()
    LIGHT_SCREEN = auto()
    SAFEGUARD = auto()
    MIST = auto()
    LUCKY_CHANT = auto()
    MAGIC_COAT = auto()
    PROTECT = auto()
    COUNTER = auto()
    MIRROR_COAT = auto()
    METAL_BURST = auto()
    MINI_COUNTER = auto()
    ENDURING = auto()
    MIRROR_MOVE = auto()
    VITAL_THROW = auto()
    GRUDGE = auto()
    # Attack related conditions
    SURE_SHOT = auto()
    SET_DAMAGE = auto()
    FOCUS_ENERGY = auto()
    # Item related
    LONG_TOSS = auto()
    PIERCE = auto()
    EMBARGO = auto()
    # HP related
    CURSED = auto()
    LEECH_SEED = auto()
    WISH = auto()
    AQUA_RING = auto()
    DESTINY_BOND = auto()
    PERISH_SONG = auto()
    HEAL_BLOCK = auto()
    # Visibility related
    BLINKER = auto()
    CROSS_EYED = auto()
    INVISIBLE = auto()
    EYEDROPS = auto()
    DROPEYE = auto()
    RADAR = auto()
    SCANNING = auto()
    IDENTIFYING = auto()
    STAIR_SPOTTER = auto()
    EXPOSED = auto()
    MIRACLE_EYE = auto()
    # Misc
    GASTRO_ACID = auto()
    TRANSFORMED = auto()
    CONVERSION_2 = auto()
    FAMISHED = auto()
    HUNGRY_PAL = auto()


BAD_STATUS_CONDITIONS = set(
    # Sleep related conditions
    StatusEffect.ASLEEP,
    StatusEffect.NIGHTMARE,
    StatusEffect.YAWNING,
    # Major status conditions
    StatusEffect.BURNED,
    StatusEffect.FROZEN,
    StatusEffect.POISONED,
    StatusEffect.BADLY_POISONED,
    StatusEffect.PARALYZED,
    # Mobility related
    StatusEffect.HALF_SPEED,
    StatusEffect.SHADOW_HOLD,
    StatusEffect.PETRIFIED,
    StatusEffect.WRAPPED,
    StatusEffect.WRAP,
    StatusEffect.CONSTRICTION,
    # Move execution related
    StatusEffect.CRINGE,
    StatusEffect.CONFUSED,
    StatusEffect.INFATUATED,
    StatusEffect.PAUSED,
    StatusEffect.COWERING,
    StatusEffect.WHIFFER,
    StatusEffect.MUZZLED,
    StatusEffect.TAUNTED,
    StatusEffect.ENCORE,
    StatusEffect.DECOY,
    StatusEffect.TERRIFIED,
    # Move-based status conditions (None)
    # Shield status conditions (None)
    # Attack related conditions (None)
    # Item related
    StatusEffect.EMBARGO,
    # HP related
    StatusEffect.CURSED,
    StatusEffect.LEECH_SEED,
    StatusEffect.PERISH_SONG,
    StatusEffect.HEAL_BLOCK,
    # Visibility related
    StatusEffect.BLINKER,
    StatusEffect.CROSS_EYED,
    StatusEffect.DROPEYE,
    StatusEffect.EXPOSED,
    StatusEffect.MIRACLE_EYE,
    # Misc
    StatusEffect.GASTRO_ACID,
    StatusEffect.FAMISHED,
    StatusEffect.HUNGRY_PAL,
)
