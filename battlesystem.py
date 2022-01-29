import constants
import damage_chart
import direction
import dungeon
import inputstream
import numpy as np
import math
import move
import pokemon
import pygame
import random
import text
import textbox
import tile


class BattleSystem:
    attack_keys = {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5}

    def __init__(self, dungeon: dungeon.Dungeon):
        self.current_move = None
        self.dungeon = dungeon
        self.is_active = False
        self._attacker = None
        self._defender = None
        self._current_move = None
        self.events: list[tuple[str, dict]] = []
        self.index = 0

    @property
    def attacker(self) -> pokemon.Pokemon:
        return self._attacker
    @attacker.setter
    def attacker(self, attacker: pokemon.Pokemon):
        self._attacker = attacker

    @property
    def defender(self):
        return self._defender
    @defender.setter
    def defender(self, defender: pokemon.Pokemon):
        self._defender = defender

    @property
    def current_move(self) -> move.Move:
        return self._current_move
    @current_move.setter
    def current_move(self, move: move.Move):
        self._current_move = move

    def clear(self):
        self.events.clear()
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.index = 0
        self.is_active = False
    
    def ai_attack(self, p: pokemon.Pokemon):
        self.attacker = p
        if self.can_attack():
            if self.activate_random():
                self.is_active = True
                self.set_attack_animation()
                self.attacker.animation.restart()

    def input(self, input_stream: inputstream.InputStream):
        self.attacker = self.dungeon.active_team[0]
        for key in self.attack_keys:
            if input_stream.keyboard.is_pressed(key):
                if self.activate_by_key(key):
                    self.is_active = True
                    self.set_attack_animation()
                    self.attacker.animation.restart()

    def move_input(self, key: int) -> int:
        move_count = len(self.attacker.move_set)
        if key == pygame.K_1: return 0
        if key == pygame.K_2 and move_count > 1: return 1
        if key == pygame.K_3 and move_count > 2: return 2
        if key == pygame.K_4 and move_count > 3: return 3
        if key == pygame.K_5 and move_count > 4: return 4
        return None

    def can_attack(self) -> bool:
        if not 1 <= np.linalg.norm(np.array(self.attacker.grid_pos) - np.array(self.dungeon.active_team[0].grid_pos)) < 2:
            return
        self.attacker.face_target(self.dungeon.active_team[0].grid_pos)  # Faces user
        self.attacker.animation_name = "Walk"
        return self.possible_moves()

    def update(self):
        event_type, event_data = self.events[self.index]
        if not event_data.get("Activated", False):
            event_data["Activated"] = True
            if event_type == "Init":
                name_item = (self.attacker.name, constants.BLUE if self.attacker.poke_type == "User" else constants.YELLOW)
                msg_item = (f" used {self.current_move.name}", constants.WHITE)
                textbox.message_log.append(text.MultiColoredText([name_item, msg_item]))
                if len(self.events) == 1:
                    msg = "The move failed."
                    textbox.message_log.append(text.Text(msg))
            elif event_type == "MoveEvent":
                self.handle_move_event(event_data)
        
        if event_data.get("Animated", False):
            self.attacker.animation.update()
            if self.attacker.animation.iterations and self.events:
                #self.attacker.animation_name = "Idle"
                if self.index + 1 != len(self.events):
                    self.index += 1
                    self.attacker.animation.restart()
                else:
                    self.is_active = False
            elif self.attacker.animation.iterations:
                self.clear()
        else:
            self.attacker.animation_name = "Idle"
            if self.index + 1 != len(self.events):
                self.index += 1
                self.attacker.animation.restart()
            else:
                self.clear()

    def handle_move_event(self, event_data):
        self.defender = event_data["Target"]
        if event_data["Effect"].effect_type == move.EffectType.DAMAGE:
            if self.miss():
                name_item = (self.attacker.name, constants.BLUE if self.attacker.poke_type == "User" else constants.YELLOW)
                msg_item = (" missed.", constants.WHITE)
            else:
                damage = self.deal_damage(event_data["Effect"])
                if self.defender != self.attacker:
                    name_item = (self.defender.name, constants.BLUE if self.defender.poke_type == "User" else constants.YELLOW)
                    msg_item = (f" took {damage} damage!", constants.WHITE)
                else:
                    name_item = (self.attacker.name, constants.BLUE if self.attacker.poke_type == "User" else constants.YELLOW)
                    msg_item = (f" took {damage} recoil damage!", constants.WHITE)
            self.events[self.index][1]["Animated"] = True
            textbox.message_log.append(text.MultiColoredText([name_item, msg_item]))
            print(self.attacker.name, self.attacker.hp)
            print(self.defender.name, self.defender.hp)

        elif event_data["Effect"].effect_type == move.EffectType.FIXED_DAMAGE:
            self.deal_fixed_damage(event_data["Effect"].power)

    def deal_fixed_damage(self, amount: int) -> int:
        self.defender.hp -= amount
        return amount

    def deal_damage(self, effect: move.MoveEffect) -> int:
        amount = self.calculate_damage(effect)
        self.deal_fixed_damage(amount)
        return amount

    def calculate_damage(self, effect: move.MoveEffect) -> int:
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
        P = effect.power
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
        # Random pertebation
        damage *= (random.randint(0, 16383) + 57344) / 65536
        damage = round(damage)

        return damage

    def activate_by_key(self, key: int) -> bool:
        return self.activate(self.move_input(key))
    
    def activate_random(self) -> bool:
        return self.activate(random.choice(self.possible_moves()))

    def activate(self, move_index: move.Move) -> bool:
        self.current_move = self.attacker.move_set[move_index]

        if not self.current_move:
            return False

        if self.attacker.current_status["Moves_pp"] == 0:
            msg = "You have ran out of PP for this move."
            textbox.message_log.append(text.Text(msg))
            return False

        self.attacker.current_status["Moves_pp"][move_index] -= 1
        self.attacker.has_turn = False

        self.events.append(("Init", {"Move": move_index}))
        
        for effect in self.current_move.effects:
            for target in self.get_targets(effect):
                event = {"Target": target, "Effect": effect}
                self.events.append(("MoveEvent", event))

        return True

    def deactivate(self):
        self.index = 0

    def miss(self) -> bool:
        i = random.randint(0, 99)
        raw_accuracy = self.attacker.accuracy_status / 100 * self.current_move.accuracy
        return round(raw_accuracy - self.defender.evasion_status) <= i

    def possible_moves(self) -> list[move.Move]:
        res = []
        for i, pp in enumerate(self.attacker.current_status["Moves_pp"]):
            if pp == 0:
                continue
            if self.get_targets(self.attacker.move_set[i].primary_effect):
                res.append(i)
        return res

    def get_targets(self, effect: move.MoveEffect) -> list[pokemon.Pokemon]:
        targets = self.find_possible_targets(effect.target)
        targets = self.filter_out_of_range_targets(
            targets, effect.range_category, effect.cuts_corners)
        return targets

    def find_possible_targets(self, target_type: str) -> list[pokemon.Pokemon]:
        allies = self.dungeon.active_team
        enemies = self.dungeon.active_enemies
        if self.attacker.poke_type == "Enemy":
            allies, enemies = enemies, allies

        if target_type == move.TargetType.SELF:
            return [self.attacker]
        elif target_type == move.TargetType.ALL:
            return self.dungeon.all_sprites
        elif target_type == move.TargetType.ALLIES:
            return allies
        elif target_type == move.TargetType.ENEMIES:
            return enemies

    def filter_out_of_range_targets(self, targets: list[pokemon.Pokemon], move_range: move.MoveRange, cuts_corners: bool) -> list[pokemon.Pokemon]:
        if move_range == move.MoveRange.SELF:
            return [self.attacker]

        possible_directions = list(direction.Direction)
        if not cuts_corners:
            possible_directions = [
                d for d in possible_directions if not self.dungeon.dungeon_map.cuts_corner(self.attacker.grid_pos, d)]

        if move_range in (move.MoveRange.DIRECTLY_IN_FRONT, move.MoveRange.UP_TO_TWO_IN_FRONT, move.MoveRange.IN_LINE_OF_SIGHT):
            possible_directions = [
                d for d in possible_directions if self.dungeon.dungeon_map[tuple(map(sum, zip(self.attacker.grid_pos, d.value)))].terrain != tile.Terrain.WALL]
            if self.attacker.direction not in possible_directions:
                return []
            if move_range == move.MoveRange.DIRECTLY_IN_FRONT:
                move_range = 1
            elif move_range == move.MoveRange.UP_TO_TWO_IN_FRONT:
                move_range = 2
            elif move_range == move.MoveRange.IN_LINE_OF_SIGHT:
                move_range = 10
            for n in range(1, move_range + 1):
                for target in targets:
                    x = self.attacker.grid_pos[0] + n * self.attacker.direction.x
                    y = self.attacker.grid_pos[1] + n * self.attacker.direction.y
                    if self.dungeon.dungeon_map[x, y].terrain == tile.Terrain.WALL:
                        return []
                    if target.grid_pos == (x, y):
                        return [target]

        new_targets = set()
        if move_range == move.MoveRange.ADJACENT or move_range == move.MoveRange.IN_SAME_ROOM:
            for target in targets:
                for dir in possible_directions:
                    x = self.attacker.grid_pos[0] + dir.x
                    y = self.attacker.grid_pos[1] + dir.y
                    if target.grid_pos == (x, y):
                        new_targets.add(target)

        if move_range == move.MoveRange.IN_SAME_ROOM:
            if not self.dungeon.dungeon_map.is_room(self.attacker.grid_pos):
                return list(new_targets)
            room = self.dungeon.dungeon_map[x, y].room_index
            for target in targets:
                if self.dungeon.dungeon_map[target.grid_pos].room_index == room:
                    new_targets.add(target)

        return list(new_targets)

    def set_attack_animation(self):
        category = self.current_move.category
        if category == move.MoveCategory.PHYSICAL:
            animation_name = "Attack"
        elif category == move.MoveCategory.SPECIAL:
            animation_name = "Attack"
        elif category == move.MoveCategory.STATUS:
            animation_name = "Charge"
        else:
            animation_name = "Idle"
        self.attacker.animation_name = animation_name
