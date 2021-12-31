import damage_chart
import math
import move
import pokemon
import random

class BattleSystem:
    def __init__(self):
        pass
    
    def set_attacker(self, attacker: pokemon.Pokemon):
        self.attacker = attacker

    def set_defender(self, defender: pokemon.Pokemon):
        self.defender = defender

    def set_battlers(self, attacker, defender):
        self.set_attacker(attacker)
        self.set_defender(defender)

    def deal_damage(self, move: move.Move, index):
        amount = self.calculate_damage(move, index)
        self.attacker.battle_info.status["HP"] -= min(amount, self.attacker.battle_info.status["HP"])

    def calculate_damage(self, move: move.Move, index):
        # Step 0 - Determine Stats
        if move.category == "Physical":
            A = self.attacker.battle_info.base.attack * damage_chart.stage_dict[self.attacker.battle_info.status["ATK"]]
            D = self.defender.battle_info.base.defense * damage_chart.stage_dict[self.defender.battle_info.status["DEF"]]
        elif move.category == "Special":
            A = self.attacker.battle_info.base.sp_attack * damage_chart.stage_dict[self.attacker.battle_info.status["SPATK"]]
            D = self.defender.battle_info.base.sp_defense * damage_chart.stage_dict[self.defender.battle_info.status["SPDEF"]]
        else:
            return 0
        L = self.attacker.battle_info.base.level
        P = move.power[index]
        if self.defender.poke_type in ("User", "Team"):
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

        damage *= self.defender.battle_info.types.get_damage_multiplier(move)
        if move.critical > critical_chance:
            damage *= 1.5
        # Step 4 - Final Calculations
        damage *= (random.randint(0, 16383) + 57344) / 65536  # Random pertebation
        damage = round(damage)

        return damage

