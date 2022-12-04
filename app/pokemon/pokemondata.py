import dataclasses
import enum

from app.model.statistic import Statistic


@dataclasses.dataclass(frozen=True)
class PokemonStrings:
    name: str
    category: str


@dataclasses.dataclass(frozen=True)
class StatsGrowth:
    required_xp: tuple[int]
    hp: tuple[int]
    attack: tuple[int]
    defense: tuple[int]
    sp_attack: tuple[int]
    sp_defense: tuple[int]

    def get_required_xp(self, level: int):
        return self.required_xp[level]

    def get_hp(self, level: int):
        return sum(self.hp[:level+1])

    def get_attack(self, level: int):
        return sum(self.attack[:level+1])

    def get_defense(self, level: int):
        return sum(self.defense[:level+1])

    def get_sp_attack(self, level: int):
        return sum(self.sp_attack[:level+1])

    def get_sp_defense(self, level: int):
        return sum(self.sp_defense[:level+1])


@dataclasses.dataclass
class LevelUpMoves:
    levels: tuple[int]
    move_ids: tuple[int]

    def get_level_up_move_ids(self, level: int) -> list[int]:
        res = []
        for lv, move_id in zip(self.levels, self.move_ids):
            if lv > level:
                break
            res.append(move_id)
        return res


class PokemonStatus:
    def __init__(self):
        # Stat related
        self.hp = Statistic(1, 0, 1)
        self.attack = Statistic(10, 0, 20)
        self.defense = Statistic(10, 0, 20)
        self.sp_attack = Statistic(10, 0, 20)
        self.sp_defense = Statistic(10, 0, 20)
        self.evasion = Statistic(10, 0, 20)
        self.accuracy = Statistic(10, 0, 20)
        self.speed = Statistic(1, 0, 4)
        self.attack_division = Statistic(0, 0, 7)
        self.defense_division = Statistic(0, 0, 7)
        self.sp_attack_division = Statistic(0, 0, 7)
        self.sp_defense_division = Statistic(0, 0, 7)
        self.belly = Statistic(100, 0, 100)

        # Conditions

        # Sleep related
        self.asleep = False
        self.sleepless = False
        self.nightmare = False
        self.yawning = False
        self.napping = False

        # Major status conditions
        self.burned = False
        self.frozen = False
        self.poisoned = False
        self.badly_poisoned = False
        self.paralyzed = False

        # Mobility related
        self.half_speed = False
        self.double_speed = False
        self.shadow_hold = False
        self.petrified = False
        self.ingrain = False
        self.wrapped = False
        self.wrap = False
        self.constriction = False
        self.mobile = False
        self.slip = False
        self.magnet_rise = False

        # Move execution related
        self.cringe = False
        self.confused = False
        self.infatuated = False
        self.paused = False
        self.cowering = False
        self.whiffer = False
        self.muzzled = False
        self.taunted = False
        self.encore = False
        self.decoy = False
        self.terrified = False
        self.snatch = False
        self.charging = False
        self.enraged = False
        self.stockpiling = False

        # Move-based status conditions
        self.bide = False
        self.solar_beam = False
        self.sky_attack = False
        self.razor_wind = False
        self.focus_punch = False
        self.skull_bash = False
        self.flying = False
        self.bouncing = False
        self.diving = False
        self.digging = False
        self.shadow_force = False

        # Shield status conditions
        self.reflect = False
        self.light_screen = False
        self.safeguard = False
        self.mist = False
        self.lucky_chant = False
        self.magic_coat = False
        self.protect = False
        self.counter = False
        self.mirror_coat = False
        self.metal_burst = False
        self.mini_counter = False
        self.enduring = False
        self.mirror_move = False
        self.vital_throw = False
        self.grudge = False

        # Attack related conditions
        self.sure_shot = False
        self.set_damage = False
        self.focus_energy = False
        
        # Item related
        self.long_toss = False
        self.pierce = False
        self.embargo = False

        # HP related
        self.cursed = False
        self.leech_seed = False
        self.wish = False
        self.aqua_ring = False
        self.destiny_bond = False
        self.perish_song = False
        self.heal_block = False

        # Visibility related
        self.blinker = False
        self.cross_eyed = False
        self.invisible = False
        self.eyedrops = False
        self.dropeye = False
        self.radar = False
        self.scanning = False
        self.identifying = False
        self.stair_spotter = False
        self.exposed = False
        self.miracle_eye = False

        # Misc
        self.gastro_acid = False
        self.transformed = False
        self.conversion_2 = False
        self.famished = False
        self.hungry_pal = False

    def can_regenerate(self) -> bool:
        return not (self.poisoned or self.badly_poisoned or self.heal_block)

    def restore_stats(self):
        self.attack.value = 10
        self.defense.value = 10
        self.sp_attack.value = 10
        self.sp_defense.value = 10
        self.accuracy.value = 10
        self.evasion.value = 10
        self.attack_division.value = 0
        self.defense_division.value = 0
        self.sp_attack_division.value = 0
        self.sp_defense_division.value = 0

    def restore_status(self):
        self.speed.value = 0
        # Conditions
        # Sleep related
        self.asleep = False
        self.sleepless = False
        self.nightmare = False
        self.yawning = False
        self.napping = False
        # Major status conditions
        self.burned = False
        self.frozen = False
        self.poisoned = False
        self.badly_poisoned = False
        self.paralyzed = False
        # Mobility related
        self.half_speed = False
        self.double_speed = False
        self.shadow_hold = False
        self.petrified = False
        self.ingrain = False
        self.wrapped = False
        self.wrap = False
        self.constriction = False
        self.mobile = False
        self.slip = False
        self.magnet_rise = False
        # Move execution related
        self.cringe = False
        self.confused = False
        self.infatuated = False
        self.paused = False
        self.cowering = False
        self.whiffer = False
        self.muzzled = False
        self.taunted = False
        self.encore = False
        self.decoy = False
        self.terrified = False
        self.snatch = False
        self.charging = False
        self.enraged = False
        self.stockpiling = False
        # Move-based status conditions
        self.bide = False
        self.solar_beam = False
        self.sky_attack = False
        self.razor_wind = False
        self.focus_punch = False
        self.skull_bash = False
        self.flying = False
        self.bouncing = False
        self.diving = False
        self.digging = False
        self.shadow_force = False
        # Shield status conditions
        self.reflect = False
        self.light_screen = False
        self.safeguard = False
        self.mist = False
        self.lucky_chant = False
        self.magic_coat = False
        self.protect = False
        self.counter = False
        self.mirror_coat = False
        self.metal_burst = False
        self.mini_counter = False
        self.enduring = False
        self.mirror_move = False
        self.vital_throw = False
        self.grudge = False
        # Attack related conditions
        self.sure_shot = False
        self.set_damage = False
        self.focus_energy = False
        # Item related
        self.long_toss = False
        self.pierce = False
        self.embargo = False
        # HP related
        self.cursed = False
        self.leech_seed = False
        self.wish = False
        self.aqua_ring = False
        self.destiny_bond = False
        self.perish_song = False
        self.heal_block = False
        # Visibility related
        self.blinker = False
        self.cross_eyed = False
        self.invisible = False
        self.eyedrops = False
        self.dropeye = False
        self.radar = False
        self.scanning = False
        self.identifying = False
        self.stair_spotter = False
        self.exposed = False
        self.miracle_eye = False
        # Misc
        self.gastro_acid = False
        self.transformed = False
        self.conversion_2 = False
        self.famished = False
        self.hungry_pal = False


class PokemonStatistics:
    def __init__(self):
        self.level = Statistic(1, 1, 100)
        self.xp = Statistic(0, 0, 10_000_000)
        self.hp = Statistic(1, 1, 999)
        self.attack = Statistic(0, 0, 255)
        self.defense = Statistic(0, 0, 255)
        self.sp_attack = Statistic(0, 0, 255)
        self.sp_defense = Statistic(0, 0, 255)


class MovementType(enum.Enum):
    NORMAL = 0
    # UNUSED = 1
    LEVITATING = 2
    PHASING = 3
    LAVA_WALKER = 4
    WATER_WALKER = 5
