import csv
import os

from app.common.constants import GAMEDATA_DIRECTORY
from app.model.type import Type, TypeEffectiveness, PokemonType
import app.db.database as db


class StatStageChart:
    def __init__(self):
        self.cursor = db.main_db.cursor()
        print(self.get_attack_multiplier(4))
        print(self.get_defense_multiplier(10))
        print(self.get_accuracy_multiplier(-3))
        print(self.get_evasion_multiplier(-10))

    def _get_multiplier(self, stat_name: str, stage: int) -> float:
        return self.cursor.execute(
            "SELECT multiplier FROM stat_stages "
            "WHERE stat_name = ? AND stage = ?",
            (stat_name, stage)
        ).fetchone()[0]

    def get_attack_multiplier(self, stage: int) -> float:
        return self._get_multiplier("Attack", stage)

    def get_defense_multiplier(self, stage: int) -> float:
        return self._get_multiplier("Defense", stage)

    def get_accuracy_multiplier(self, stage: int) -> float:
        return self._get_multiplier("Accuracy", stage)

    def get_evasion_multiplier(self, stage: int) -> float:
        return self._get_multiplier("Evasion", stage)


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

    def get_move_effectiveness(
        self, move_type: Type, pokemon_type: PokemonType
    ) -> TypeEffectiveness:
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
