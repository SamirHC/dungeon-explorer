import damage_chart
import enum
import math
import move
import random

class PokemonBattleInfo:
    def __init__(self, poke_id, name, types, base, status, move_set):
        self.poke_id = poke_id
        self.name = name
        self.types = types
        self.base = base
        self.status = status
        self.move_set = move_set

    def lose_hp(self, amount):
        self.status["HP"] -= amount
        if self.status["HP"] < 0:
            self.status["HP"] = 0

    def deal_damage(self, move: move.Move, target, index):
        # Step 0 - Determine Stats
        if move.category == "Physical":
            A = self.base.attack * damage_chart.stage_dict[self.status["ATK"]]
            D = target.battle_info.base.defense * damage_chart.stage_dict[target.battle_info.status["DEF"]]
        elif move.category == "Special":
            A = self.base.sp_attack * damage_chart.stage_dict[self.status["SPATK"]]
            D = target.battle_info.base.sp_defense * damage_chart.stage_dict[target.battle_info.status["SPDEF"]]
        else:
            return 0
        L = self.base.level
        P = move.power[index]
        if target.poke_type in ["User", "Team"]:
            Y = 340 / 256
        else:
            Y = 1
        log_input = ((A - D) / 8 + L + 50) * 10
        if log_input < 1:
            log_input = 1
        elif log_input > 4095:
            log_input = 4095
        critical_chance = random.randint(0, 99)

        # Step 1 - Stat Modification
        # Step 2 - Raw Damage Calculation
        damage = ((A + P) * (39168 / 65536) - (D / 2) + 50 * math.log(log_input) - 311) / Y
        # Step 3 - Final Damage Modifications
        if damage < 1:
            damage = 1
        elif damage > 999:
            damage = 999

        damage *= target.battle_info.types.get_damage_multiplier(move)
        if move.critical > critical_chance:
            damage *= 1.5
        # Step 4 - Final Calculations
        damage *= (random.randint(0, 16383) + 57344) / 65536  # Random pertebation
        damage = round(damage)

        return damage

    def stat_change(self, effect, power):
        if effect[-1] == "+":
            effect = effect[:-1]
            self.status[effect] += power
            if self.status[effect] > 20:
                self.status[effect] = 20

        elif effect[-1] == "-":
            effect = effect[:-1]
            self.status[effect] -= power
            if self.status[effect] < 0:
                self.status[effect] = 0

    def afflict(self, effect, power):

        if not self.status[effect]:
            self.status[effect] = power
        else:
            print(self.name, "is already", effect)

    def heal(self, power):
        self.status["HP"] += power

class PokemonStat(enum.Enum):
    HP = 0
    ATTACK = 1
    DEFENSE = 2
    SP_ATTACK = 3
    SP_DEFENSE = 4
    ACCURACY = 5
    EVASION = 6
    REGENERATION = 7
