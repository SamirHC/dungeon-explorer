import dataclasses
import enum
import os
import xml.etree.ElementTree as ET

from dungeon_explorer.dungeon import damage_chart
from dungeon_explorer.pokemon import move


class Moveset:
    MAX_MOVES = 4

    def __init__(self, moveset: list[move.Move]):
        self.moveset: list[move.Move] = []
        for m in moveset:
            self.learn(m)
        self.pp = [m.pp for m in self.moveset]

    def __getitem__(self, index: int) -> move.Move:
        return self.moveset[index]

    def __len__(self) -> int:
        return len(self.moveset)

    def __contains__(self, move: move.Move) -> bool:
        return move.name in [m.name for m in self.moveset]

    def can_use(self, index: int):
        return self.pp[index]

    def use(self, index: int):
        self.pp[index] -= 1

    def can_learn(self, move: move.Move) -> bool:
        return len(self) != Moveset.MAX_MOVES and move not in self

    def learn(self, move: move.Move):
        if self.can_learn(move):
            self.moveset.append(move)

    def forget(self, index: int):
        self.moveset.remove(index)

    def shift_up(self, index: int) -> int:
        if index == 0:
            return index
        self.moveset[index - 1], self.moveset[index] = self[index], self[index - 1]
        self.pp[index - 1], self.pp[index] = self.pp[index], self.pp[index - 1]
        return index - 1

    def shift_down(self, index: int) -> int:
        if index == len(self) - 1:
            return index
        self.moveset[index], self.moveset[index + 1] = self[index + 1], self[index]
        self.pp[index], self.pp[index + 1] = self.pp[index + 1], self.pp[index]
        return index + 1

    def get_weights(self) -> list[int]:
        return [m.weight for m in self]

@dataclasses.dataclass
class Statistic:
    value: int
    min_value: int
    max_value: int

    def increase(self, amount: int):
        self.value = min(self.value + amount, self.max_value)

    def reduce(self, amount: int):    
        self.value = max(self.min_value, self.value - amount)

    def set(self, result: int):
        self.value = max(self.min_value, min(result, self.max_value))


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


class BehaviourType(enum.Enum):
    RANDOM = 0  # Wanders around aimlessly in random directions
    FOLLOW = 1  # Follows the leader pokemon
    SEEK = 2  # Seeks out enemies
    LEAD = 3  # Based on user input
    PETRIFIED = 4  # Avoids enemies


@dataclasses.dataclass
class PokemonType:
    type1: damage_chart.Type
    type2: damage_chart.Type

    def __contains__(self, type: damage_chart.Type) -> bool:
        return self.type1 is type or self.type2 is type

    def get_damage_multiplier(self, move_type: damage_chart.Type) -> float:
        m1 = damage_chart.get_type_multiplier(
            move_type, self.type1)
        m2 = damage_chart.get_type_multiplier(
            move_type, self.type2)
        return m1 * m2


class GenericPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id

        file = self.get_file()
        tree = ET.parse(file)
        root = tree.getroot()

        self._name = root.find("Strings").find("English").find("Name").text
        self._pokedex_number = int(root.find("GenderedEntity").find("PokedexNumber").text)

        self._type = PokemonType(
            damage_chart.Type(int(root.find("GenderedEntity").find("PrimaryType").text)),
            damage_chart.Type(int(root.find("GenderedEntity").find("SecondaryType").text))
        )
        self._movement_type = MovementType(int(root.find("GenderedEntity").find("MovementType").text))

        base_stats = root.find("GenderedEntity").find("BaseStats")
        self._base_hp = int(base_stats.find("HP").text)
        self._base_attack = int(base_stats.find("Attack").text)
        self._base_defense = int(base_stats.find("Defense").text)
        self._base_sp_attack = int(base_stats.find("SpAttack").text)
        self._base_sp_defense = int(base_stats.find("SpDefense").text)

        stats_growth = root.find("StatsGrowth").findall("Level")
        self._required_xp = []
        self._hp_growth = []
        self._attack_growth = []
        self._defense_growth = []
        self._sp_attack_growth = []
        self._sp_defense_growth = []
        for level in stats_growth:
            self._required_xp.append(int(level.find("RequiredExp").text))
            self._hp_growth.append(int(level.find("HP").text))
            self._attack_growth.append(int(level.find("Attack").text))
            self._defense_growth.append(int(level.find("Defense").text))
            self._sp_attack_growth.append(int(level.find("SpAttack").text))
            self._sp_defense_growth.append(int(level.find("SpDefense").text))

        moveset = root.find("Moveset")
        self._level_up_moves = [(int(el.find("Level").text), el.find("MoveID").text) for el in moveset.find("LevelUpMoves").findall("Learn")]

    def get_file(self):
        return os.path.join("data", "gamedata", "pokemon", f"{self.poke_id}.xml")

    @property
    def name(self) -> str:
        return self._name

    @property
    def pokedex_number(self) -> int:
        return self._pokedex_number

    @property
    def type(self) -> PokemonType:
        return self._type

    @property
    def movement_type(self) -> MovementType:
        return self._movement_type

    def get_required_xp(self, level: int):
        return self._required_xp[level]

    def get_hp(self, level: int):
        return self._base_hp + sum(self._hp_growth[:level])

    def get_attack(self, level: int):
        return self._base_attack + sum(self._attack_growth[:level])

    def get_defense(self, level: int):
        return self._base_defense + sum(self._defense_growth[:level])

    def get_sp_attack(self, level: int):
        return self._base_sp_attack + sum(self._sp_attack_growth[:level])

    def get_sp_defense(self, level: int):
        return self._base_sp_defense + sum(self._sp_defense_growth[:level])

    def get_level_up_moves(self, level: int):
        res = []
        for lv, move_id in self._level_up_moves:
            if lv > level:
                break
            res.append(move.Move(move_id))
        return res


def get_poke_id_by_pokedex(dex: int) -> str:
    for i in range(dex, 600):
        poke_id = str(i)
        if GenericPokemon(poke_id).pokedex_number == dex:
            return poke_id