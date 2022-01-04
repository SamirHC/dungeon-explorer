import damage_chart
import dungeon
import math
import move
import pokemon
import pygame
import random
import text
import textbox

class BattleSystem:
    def __init__(self, current_dungeon: dungeon.Dungeon):
        self.current_move = None
        self.index = 0
        self.current_dungeon = current_dungeon
    
    def set_attacker(self, attacker: pokemon.Pokemon):
        self.attacker = attacker

    def set_defender(self, defender: pokemon.Pokemon):
        self.defender = defender

    def set_current_move(self, m: move.Move):
        self.current_move = m

    def move_input(self, key):
        if key == pygame.K_1:
            return self.attacker.move_set.moveset[0]
        if key == pygame.K_2:
            return self.attacker.move_set.moveset[1]
        if key == pygame.K_3:
            return self.attacker.move_set.moveset[2]
        if key == pygame.K_4:
            return self.attacker.move_set.moveset[3]
        if key == pygame.K_5:
            return self.attacker.move_set.REGULAR_ATTACK

    def current_effect(self):
        if self.current_move:
            return self.current_move.effects[self.index]

    def next_effect(self):
        self.index += 1
        return self.index < len(self.current_move.effects)

    def deal_fixed_damage(self, amount):
        self.defender.hp -= amount
        return amount

    def deal_damage(self):
        amount = self.calculate_damage()
        self.deal_fixed_damage(amount)
        return amount

    def calculate_damage(self):
        # Step 0 - Determine Stats
        if self.current_move.category == move.MoveCategory.PHYSICAL:
            A = self.attacker.attack * damage_chart.stage_dict[self.attacker.attack_status]
            D = self.defender.defense * damage_chart.stage_dict[self.defender.defense_status]
        elif self.current_move.category == move.MoveCategory.SPECIAL:
            A = self.attacker.sp_attack * damage_chart.stage_dict[self.attacker.sp_attack_status]
            D = self.defender.sp_defense * damage_chart.stage_dict[self.defender.sp_defense_status]
        else:
            return 0
        L = self.attacker.level
        P = self.current_effect().power
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

        damage *= self.defender.type.get_damage_multiplier(self.current_move.type)
        if self.current_move.critical > critical_chance:
            damage *= 1.5
        # Step 4 - Final Calculations
        damage *= (random.randint(0, 16383) + 57344) / 65536  # Random pertebation
        damage = round(damage)

        return damage

    def activate_by_key(self, key):
        return self.activate(self.move_input(key))

    def activate(self, m: move.Move):
        steps = []
        self.set_current_move(m)

        if not self.current_move:
            return steps

        if self.current_move.pp == 0:
            msg = "You have ran out of PP for this move."
            textbox.message_log.append(text.Text(msg))
            return steps
        
        self.current_move.pp -= 1
        
        msg = self.attacker.name + " used " + self.current_move.name
        textbox.message_log.append(text.Text(msg))

        while True:
            Dict = {}
            targets = self.attacker.get_targets(self.current_effect())

            if not targets and self.index == 0:
                msg = "The move failed."
                textbox.message_log.append(text.Text(msg))
                break

            if targets:
                Dict["Targets"] = targets
                Dict["Effect"] = self.current_effect().effect_type
                steps.append(Dict)
                if self.current_effect().effect_type == "Damage":
                    for target in targets:
                        self.set_defender(target)
                        if self.miss():
                            msg = self.attacker.name + " missed."
                        else:
                            damage = self.deal_damage()
                            if self.defender != self.attacker:
                                msg = self.defender.name + " took " + str(damage) + " damage!"
                            else:
                                msg = self.attacker.name + " took " + str(damage) + " recoil damage!"
                        textbox.message_log.append(text.Text(msg))
                        print(self.attacker.name, self.attacker.hp)
                        print(self.defender.name, self.defender.hp)

                elif self.current_effect() == "FixedDamage":
                    for target in targets:
                        self.set_defender(target)
                        self.deal_fixed_damage(self.current_effect().power)

            if not self.next_effect():
                self.deactivate()
                break

        return steps

    def deactivate(self):
        self.index = 0

    def miss(self):
        i = random.randint(0, 99)
        raw_accuracy = self.attacker.accuracy_status / 100 * self.current_move.accuracy
        return round(raw_accuracy - self.defender.evasion_status) <= i
