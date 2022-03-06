import dataclasses
import enum
import os
import xml.etree.ElementTree as ET

from dungeon_explorer.dungeon import damage_chart
from dungeon_explorer.pokemon import move


class Moveset:
    MAX_MOVES = 4
    REGULAR_ATTACK = move.Move("0")

    def __init__(self, moveset: list[move.Move] = []):
        self._moveset = [self.REGULAR_ATTACK] + moveset

    def __getitem__(self, i: int) -> move.Move:
        if i is None:
            return None
        return self._moveset[i]

    def __len__(self) -> int:
        return len(self._moveset)


@dataclasses.dataclass
class Statistic:
    value: int
    min_value: int
    max_value: int

    def increase(self, amount: int):
        self.value = min(self.value + amount, self.max_value)

    def reduce(self, amount: int):    
        self.value = max(self.min_value, self.value - amount)


@dataclasses.dataclass
class PokemonStatus:
    level: Statistic
    xp: Statistic
    hp: Statistic
    attack = Statistic(10, 0, 20)
    defense = Statistic(10, 0, 20)
    sp_attack = Statistic(10, 0, 20)
    sp_defense = Statistic(10, 0, 20)
    evasion = Statistic(10, 0, 20)
    accuracy = Statistic(10, 0, 20)


@dataclasses.dataclass
class SpecificPokemon:
    level: int = 1
    xp: int = 0
    hp: int = 1
    attack: int = 0
    defense: int = 0
    sp_attack: int = 0
    sp_defense: int = 0
    moveset: Moveset = Moveset()


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

    def is_type(self, type: damage_chart.Type) -> bool:
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
