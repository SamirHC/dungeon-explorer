import damage_chart
import direction
import dungeon
import keyboard
import math
import move
import pokemon
import pygame
import random
import text
import textbox
import tile
import utils


class BattleSystem:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.current_move = None
        self.index = 0
        self.dungeon = dungeon
        self.is_active = False

    def set_attacker(self, attacker: pokemon.Pokemon):
        self.attacker = attacker

    def set_defender(self, defender: pokemon.Pokemon):
        self.defender = defender

    def set_current_move(self, m: move.Move):
        self.current_move = m

    def input(self, kb: keyboard.Keyboard):
        for key in self.attack_keys:
            if kb.is_pressed(key):
                if self.activate_by_key(key):
                    self.is_active = True
                    self.attacker.set_attack_animation(self.current_move)
                    self.attacker.animation.start()

    @property
    def attack_keys(self) -> dict[int, move.Move]:
        return {
            pygame.K_1: self.attacker.move_set.moveset[0],
            pygame.K_2: self.attacker.move_set.moveset[1],
            pygame.K_3: self.attacker.move_set.moveset[2],
            pygame.K_4: self.attacker.move_set.moveset[3],
            pygame.K_5: self.attacker.move_set.REGULAR_ATTACK
        }

    def move_input(self, key) -> move.Move:
        return self.attack_keys[key]

    def update(self):
        if self.attacker.animation.iterations and self.steps:
            self.attacker.animation_name = "Walk"
            if self.target_index + 1 != len(self.steps[self.step_index]["Targets"]):
                self.target_index += 1
                self.attacker.animation.start()
            elif self.step_index + 1 != len(self.steps):
                self.step_index += 1
                self.target_index = 0
                self.attacker.animation.start()
            else:
                self.attacker.has_turn = False
                self.is_active = False
        elif self.attacker.animation.iterations:
            self.attacker.animation_name = "Walk"
            self.is_active = False

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
            A = self.attacker.attack * \
                damage_chart.stage_dict[self.attacker.attack_status]
            D = self.defender.defense * \
                damage_chart.stage_dict[self.defender.defense_status]
        elif self.current_move.category == move.MoveCategory.SPECIAL:
            A = self.attacker.sp_attack * \
                damage_chart.stage_dict[self.attacker.sp_attack_status]
            D = self.defender.sp_defense * \
                damage_chart.stage_dict[self.defender.sp_defense_status]
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
        damage = ((A + P) * (39168 / 65536) - (D / 2) +
                  50 * math.log(log_input) - 311) / Y
        # Step 3 - Final Damage Modifications
        if damage < 1:
            damage = 1
        elif damage > 999:
            damage = 999

        damage *= self.defender.type.get_damage_multiplier(
            self.current_move.type)
        if self.current_move.critical > critical_chance:
            damage *= 1.5
        # Step 4 - Final Calculations
        damage *= (random.randint(0, 16383) + 57344) / \
            65536  # Random pertebation
        damage = round(damage)

        return damage

    def activate_by_key(self, key) -> bool:
        return self.activate(self.move_input(key))

    def activate(self, m: move.Move) -> bool:
        self.step_index = 0
        self.target_index = 0
        self.steps = []
        self.set_current_move(m)

        if not self.current_move:
            return False

        if self.current_move.pp == 0:
            msg = "You have ran out of PP for this move."
            textbox.message_log.append(text.Text(msg))
            return False

        self.current_move.pp -= 1

        msg = f"{self.attacker.name} used {self.current_move.name}"
        textbox.message_log.append(text.Text(msg))

        while True:
            Dict = {}
            targets = self.get_targets(self.current_effect())

            if not targets and self.index == 0:
                msg = "The move failed."
                textbox.message_log.append(text.Text(msg))
                break

            if targets:
                Dict["Targets"] = targets
                Dict["Effect"] = self.current_effect().effect_type
                self.steps.append(Dict)
                if self.current_effect().effect_type == "Damage":
                    for target in targets:
                        self.set_defender(target)
                        if self.miss():
                            msg = f"{self.attacker.name} missed."
                        else:
                            damage = self.deal_damage()
                            if self.defender != self.attacker:
                                msg = f"{self.defender.name} took {damage} damage!"
                            else:
                                msg = f"{self.attacker.name} took {damage} recoil damage!"
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

        return True

    def deactivate(self):
        self.index = 0

    def miss(self):
        i = random.randint(0, 99)
        raw_accuracy = self.attacker.accuracy_status / 100 * self.current_move.accuracy
        return round(raw_accuracy - self.defender.evasion_status) <= i

    def possible_moves(self) -> list[move.Move]:
        return [self.attacker.move_set.moveset[i] for i in range(4) if self.attacker.move_set.moveset[i].pp and self.get_targets(self.attacker.move_set.moveset[i].effects[0])]

    def get_targets(self, effect):
        targets = self.find_possible_targets(effect.target)
        targets = self.filter_out_of_range_targets(
            targets, effect.range_category, effect.cuts_corners)
        return targets

    def find_possible_targets(self, target_type):
        allies = self.dungeon.active_team
        enemies = self.dungeon.active_enemies
        if self.attacker.poke_type == "Enemy":
            allies, enemies = enemies, allies

        if target_type == "Self":
            return [self.attacker]
        elif target_type == "All":
            return self.dungeon.all_sprites
        elif target_type == "Allies":
            return allies
        elif target_type == "Enemies":
            return enemies

    def filter_out_of_range_targets(self, targets: list[pokemon.Pokemon], move_range, cuts_corners):
        if move_range == move.MoveRange.SELF:
            return [self.attacker]

        possible_directions = list(direction.Direction)
        if not cuts_corners:
            possible_directions = [
                d for d in possible_directions if not self.attacker.cuts_corner(d)]

        if move_range in (move.MoveRange.DIRECTLY_IN_FRONT, move.MoveRange.UP_TO_TWO_IN_FRONT, move.MoveRange.IN_LINE_OF_SIGHT):
            possible_directions = [
                d for d in possible_directions if self.attacker.tile_in_direction(d) != tile.Tile.WALL]
            if self.attacker.direction in possible_directions:
                if move_range == move.MoveRange.DIRECTLY_IN_FRONT:
                    move_range = 1
                elif move_range == move.MoveRange.UP_TO_TWO_IN_FRONT:
                    move_range = 2
                elif move_range == move.MoveRange.IN_LINE_OF_SIGHT:
                    move_range = 10
                for n in range(1, move_range + 1):
                    for target in targets:
                        x = self.attacker.grid_pos[0] + n * \
                            self.attacker.direction.value[0]
                        y = self.attacker.grid_pos[1] + n * \
                            self.attacker.direction.value[1]
                        if self.dungeon.dungeon_map.get_at(x, y) == tile.Tile.WALL:
                            return []
                        if target.grid_pos == (x, y):
                            return [target]

        new_targets = []
        if move_range == move.MoveRange.ADJACENT or move_range == move.MoveRange.IN_SAME_ROOM:
            for target in targets:
                for dir in possible_directions:
                    x = self.attacker.grid_pos[0] + dir.value[0]
                    y = self.attacker.grid_pos[1] + dir.value[1]
                    if target.grid_pos == (x, y):
                        new_targets.append(target)

        if move_range == move.MoveRange.IN_SAME_ROOM:
            x, y = self.attacker.grid_pos
            if self.dungeon.dungeon_map.get_at(x, y) == tile.Tile.GROUND:
                for room in self.dungeon.dungeon_map.room_coords:
                    if (x, y) in room:
                        possible_directions = room
                        break
                for target in targets:
                    if target.grid_pos in possible_directions:
                        new_targets.append(target)
            new_targets = utils.remove_duplicates(new_targets)
        return new_targets
