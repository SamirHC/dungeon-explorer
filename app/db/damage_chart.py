import csv
import os

from app.common.constants import GAMEDATA_DIRECTORY
from app.model.type import Type, TypeEffectiveness, PokemonType


class StatStageChart:
    DENOMINATOR = 256

    def __init__(self):
        self.stat_stage_chart = {}
        with open(os.path.join(GAMEDATA_DIRECTORY, "stat_stage_chart.csv"), newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.stat_stage_chart[row["Stat"]] = tuple(int(row[str(stage)]) for stage in range(-10, 11))

    def get_attack_multiplier(self, stage: int) -> float:
        return self.stat_stage_chart["Attack"][stage] / self.DENOMINATOR

    def get_defense_multiplier(self, stage: int) -> float:
        return self.stat_stage_chart["Defense"][stage] / self.DENOMINATOR

    def get_accuracy_multiplier(self, stage: int) -> float:
        return self.stat_stage_chart["Accuracy"][stage] / self.DENOMINATOR

    def get_evasion_multiplier(self, stage: int) -> float:
        return self.stat_stage_chart["Evasion"][stage] / self.DENOMINATOR


class TypeChart:
    def __init__(self):
        self.type_chart: dict[Type, dict[Type, TypeEffectiveness]] = {}
        chart_path = os.path.join(GAMEDATA_DIRECTORY, "damage_chart.csv")
        with open(chart_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                atk_type_dict = {}
                for def_type in Type:
                    atk_type_dict[def_type] = TypeEffectiveness(int(row[def_type.name]))
                self.type_chart[Type[row["Attacking"]]] = atk_type_dict

    def get_type_multiplier(self, attack: Type, defend: Type) -> float:
        return self.get_type_effectiveness(attack, defend).get_multiplier()

    def get_type_effectiveness(self, attack: Type, defend: Type) -> TypeEffectiveness:
        return self.type_chart[attack][defend]

    def get_move_effectiveness(self, move_type: Type, pokemon_type: PokemonType) -> TypeEffectiveness:
        eff1 = self.get_type_effectiveness(move_type, pokemon_type.type1)
        eff2 = self.get_type_effectiveness(move_type, pokemon_type.type2)
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
