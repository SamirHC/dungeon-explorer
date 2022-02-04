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
        self.dungeon = dungeon
        self.current_move = None
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
    def defender(self) -> pokemon.Pokemon:
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

    def deactivate(self):
        self.events.clear()
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.index = 0
        self.is_active = False
    
    def ai_attack(self, p: pokemon.Pokemon):
        self.attacker = p
        if self.can_attack():
            self.activate_random()

    def input(self, input_stream: inputstream.InputStream):
        self.attacker = self.dungeon.active_team[0]
        for key in self.attack_keys:
            if input_stream.keyboard.is_pressed(key):
                self.activate_by_key(key)

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
            return False
        self.attacker.face_target(self.dungeon.active_team[0].grid_pos)  # Faces user
        return self.possible_moves()

    def activate_by_key(self, key: int) -> bool:
        return self.activate(self.move_input(key))
    
    def activate_random(self) -> bool:
        return self.activate(random.choice(self.possible_moves()))

    def activate(self, move_index: move.Move) -> bool:
        self.current_move = self.attacker.move_set[move_index]

        if not self.current_move:
            return False
        if self.attacker.current_status["Moves_pp"][move_index] == 0:
            msg = "You have ran out of PP for this move."
            textbox.message_log.append(text.Text(msg))
            return False

        self.is_active = True
        self.attacker.current_status["Moves_pp"][move_index] -= 1
        self.attacker.has_turn = False
        self.get_events()
        return True

    def get_events(self):
        self.events += self.get_init_events()
        fails = True
        for effect in self.current_move.primary_effects:
            for target in self.get_targets(effect):
                fails = False
                self.defender = target
                self.events += self.get_events_from_effect(effect)
        if fails:
            self.events += self.get_fail_events()
    
    def get_init_events(self):
        events = []
        name_item = (self.attacker.name, constants.BLUE if self.attacker.poke_type == "User" else constants.YELLOW)
        msg_item = (f" used {self.current_move.name}", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        events.append(("LogEvent", {"Text": text_object}))
        events.append(("SetAnimation", {"Attacker": self.current_move.animation}))
        return events

    def get_fail_events(self):
        text_object = text.Text("The move failed.")
        return [("LogEvent", {"Text": text_object})]

    # Returns a list of (event_type, event_data) tuples
    def get_events_from_effect(self, effect: move.MoveEffect):
        if effect == move.EffectType.DAMAGE:
            return self.get_events_from_damage_effect(effect)
        elif effect == move.EffectType.FIXED_DAMAGE:
            return self.get_events_from_fixed_damage_effect(effect)
    
    def get_events_from_damage_effect(self):
        if self.miss():
            return self.get_miss_events()
        damage = self.calculate_damage(self.current_move.power)
        if damage == 0:
            return self.get_no_damage_events()
        return self.get_damage_events(damage)

    def get_events_from_fixed_damage_effect(self):
        if self.miss():
            return self.get_miss_events()
        damage = self.current_move.power
        return self.get_damage_events(damage)

    # TODO: Miss sfx, Miss gfx label
    def get_miss_events(self):
        name_item = (self.attacker.name, constants.BLUE if self.attacker.poke_type == "User" else constants.YELLOW)
        msg_item = (" missed.", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        return [("LogEvent", {"Text": text_object})]

    # TODO: No dmg sfx (same as miss sfx)
    def get_no_damage_events(self):
        name_item = (self.defender.name, constants.BLUE if self.defender.poke_type == "User" else constants.YELLOW)
        msg_item = (f" took no damage.", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        return [("LogEvent", {"Text": text_object})]

    # TODO: Damage sfx, Defender hurt animation, type effectiveness message
    def get_damage_events(self, damage):
        events = []
        name_item = (self.defender.name, constants.BLUE if self.defender.poke_type == "User" else constants.YELLOW)
        msg_item = (f" took {damage} damage!", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        events.append(("LogEvent", {"Text": text_object}))
        events.append(("DamageEvent", {"Amount": damage}))
        return events

    def update(self):
        if self.index == len(self.events):
            return self.deactivate()
        event_type, event_data = self.events[self.index]
        if not event_data.get("Activated", False):
            self.handle_event(event_type, event_data)
            return
        self.index += 1

    def handle_event(self, event_type, event_data):
        if event_type == "LogEvent":
            self.handle_log_event(event_data)
        elif event_type == "SetAnimation":
            self.handle_set_animation_event(event_data)
        elif event_type == "DamageEvent":
            self.handle_damage_event(event_data)

    def handle_log_event(self, event_data):
        event_data["Activated"] = True
        textbox.message_log.append(event_data["Text"])
    
    def handle_set_animation_event(self, event_data):
        event_data["Activated"] = True
        self.attacker.animation_name = event_data["Attacker"]

    def handle_damage_event(self, event_data):
        event_data["Activated"] = True
        self.deal_damage(event_data["Amount"])

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
