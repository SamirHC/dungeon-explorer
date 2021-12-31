import damage_chart
import math
import move
import pokemon
import random
import text
import textbox

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

    def deal_fixed_damage(self, amount):
        self.defender.status_dict["HP"] -= min(amount, self.defender.status_dict["HP"])
        return amount

    def deal_damage(self, move: move.Move, index):
        amount = self.calculate_damage(move, index)
        self.deal_fixed_damage(amount)
        return amount

    def calculate_damage(self, move: move.Move, index):
        # Step 0 - Determine Stats
        if move.category == "Physical":
            A = self.attacker.actual_stats.attack * damage_chart.stage_dict[self.attacker.status_dict["ATK"]]
            D = self.defender.actual_stats.defense * damage_chart.stage_dict[self.defender.status_dict["DEF"]]
        elif move.category == "Special":
            A = self.attacker.actual_stats.sp_attack * damage_chart.stage_dict[self.attacker.status_dict["SPATK"]]
            D = self.defender.actual_stats.sp_defense * damage_chart.stage_dict[self.defender.status_dict["SPDEF"]]
        else:
            return 0
        L = self.attacker.actual_stats.level
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

        damage *= self.defender.type.get_damage_multiplier(move)
        if move.critical > critical_chance:
            damage *= 1.5
        # Step 4 - Final Calculations
        damage *= (random.randint(0, 16383) + 57344) / 65536  # Random pertebation
        damage = round(damage)

        return damage

    def activate(self, move_index):
        if move_index == None:
            return []
        if move_index == 4:
            move_used = self.attacker.move_set.REGULAR_ATTACK
        else:
            move_used = self.attacker.move_set.moveset[move_index]
        steps = []
        if move_used.pp != 0:
            move_used.pp -= 1

            msg = self.attacker.name + " used " + move_used.name
            textbox.message_log.append(text.Text(msg))

            for i in range(len(move_used.effects)):
                Dict = {}
                effect = move_used.effects[i]
                move_range = move_used.ranges[i]
                target_type = move_used.target_type[i]
                targets = self.attacker.find_possible_targets(target_type)
                targets = self.attacker.filter_out_of_range_targets(targets, move_range, move_used.cuts_corners)
                if targets:
                    Dict["Targets"] = targets
                    Dict["Effect"] = effect
                    steps.append(Dict)
                    self.activate_effect(move_used, i, targets)
                else:
                    if i == 0:
                        msg = "The move failed."
                        textbox.message_log.append(text.Text(msg))
                    break
        else:
            msg = "You have ran out of PP for this move."
            textbox.message_log.append(text.Text(msg))

        return steps

    def miss(self, move_accuracy, evasion):
        i = random.randint(0, 99)
        raw_accuracy = self.attacker.status_dict["ACC"] / 100 * move_accuracy
        return round(raw_accuracy - evasion) <= i

    def activate_effect(self, move: move.Move, index, targets):
        effect = move.effects[index]
        if effect == "Damage":
            for target in targets:
                self.set_defender(target)
                evasion = self.defender.status_dict["EVA"]
                if self.attacker == self.defender:  # You cannot dodge recoil damage
                    evasion = 0

                if self.miss(move.accuracy[index], evasion):
                    msg = self.attacker.name + " missed."
                else:
                    damage = self.deal_damage(move, index)
                    if self.defender != self.attacker:
                        msg = self.defender.name + " took " + str(damage) + " damage!"
                    else:
                        msg = self.attacker.name + " took " + str(damage) + " recoil damage!"
                textbox.message_log.append(text.Text(msg))
                print(self.attacker.name, self.attacker.status_dict["HP"])
                print(self.defender.name, self.defender.status_dict["HP"])

        elif effect == "FixedDamage":
            for target in targets:
                self.set_defender(target)
                self.deal_fixed_damage(move.power[index])
