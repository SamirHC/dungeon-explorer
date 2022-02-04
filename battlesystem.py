import constants
import damage_chart
import direction
import dungeon
import inputstream
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
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.events: list[tuple[str, dict]] = []
        self.index = 0

    def deactivate(self):
        self.events.clear()
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.index = 0
        self.is_active = False

    # USER
    def input(self, input_stream: inputstream.InputStream):
        self.attacker = self.dungeon.active_team[0]
        for key in self.attack_keys:
            if input_stream.keyboard.is_pressed(key):
                self.user_activate(key)

    def user_activate(self, key: int) -> bool:
        return self.activate(self.move_input(key))

    def move_input(self, key: int) -> int:
        move_count = len(self.attacker.move_set)
        if key == pygame.K_1: return 0
        if key == pygame.K_2 and move_count > 1: return 1
        if key == pygame.K_3 and move_count > 2: return 2
        if key == pygame.K_4 and move_count > 3: return 3
        if key == pygame.K_5 and move_count > 4: return 4
        return None

    # TARGETS
    def get_targets(self, move_range: move.MoveRange) -> list[pokemon.Pokemon]:
        if move_range == move.MoveRange.USER: return [self.attacker]
        targets = self.find_possible_targets(move_range.target_type())
        return self.get_targets_in_range(targets, move_range)

    def find_possible_targets(self, target_type: move.TargetType) -> list[pokemon.Pokemon]:
        if target_type == move.TargetType.USER: return [self.attacker]
        if target_type == move.TargetType.ALL: return self.dungeon.all_sprites

        allies = self.dungeon.active_team
        enemies = self.dungeon.active_enemies
        if self.attacker.poke_type == "Enemy":
            allies, enemies = enemies, allies
        if target_type == move.TargetType.ALLIES: return allies
        if target_type == move.TargetType.ENEMIES: return enemies

    def get_targets_in_range(self, targets: list[pokemon.Pokemon], move_range: move.MoveRange) -> list[pokemon.Pokemon]:
        if move_range == move.MoveRange.USER:
            return [self.attacker]

        possible_directions = list(direction.Direction)
        if not move_range.cuts_corners():
            possible_directions = [
                d for d in possible_directions if not self.dungeon.dungeon_map.cuts_corner(self.attacker.grid_pos, d)]

        if move_range in [r for r in list(move.MoveRange) if r.straight()]:
            possible_directions = [
                d for d in possible_directions if self.dungeon.dungeon_map[tuple(map(sum, zip(self.attacker.grid_pos, d.value)))].terrain != tile.Terrain.WALL]
            if self.attacker.direction not in possible_directions:
                return []
            if move_range in (move.MoveRange.ENEMY_IN_FRONT, move.MoveRange.FACING_POKEMON, move.MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS, move.MoveRange.FACING_POKEMON_CUTS_CORNERS):
                distance = 1
            elif move_range == move.MoveRange.ENEMY_UP_TO_TWO_TILES_AWAY:
                distance = 2
            elif move_range == move.MoveRange.LINE_OF_SIGHT:
                distance = 10
            for n in range(1, distance + 1):
                for target in targets:
                    x = self.attacker.grid_pos[0] + n * self.attacker.direction.x
                    y = self.attacker.grid_pos[1] + n * self.attacker.direction.y
                    if self.dungeon.dungeon_map[x, y].terrain == tile.Terrain.WALL:
                        return []
                    if target.grid_pos == (x, y):
                        return [target]

        new_targets = set()
        if move_range == move.MoveRange.ENEMIES_WITHIN_ONE_TILE_RANGE or move_range == move.MoveRange.ALL_ENEMIES_IN_THE_ROOM:
            for target in targets:
                for dir in possible_directions:
                    x = self.attacker.grid_pos[0] + dir.x
                    y = self.attacker.grid_pos[1] + dir.y
                    if target.grid_pos == (x, y):
                        new_targets.add(target)

        if move_range == move.MoveRange.ALL_ENEMIES_IN_THE_ROOM:
            if not self.dungeon.dungeon_map.is_room(self.attacker.grid_pos):
                return list(new_targets)
            for target in targets:
                if self.dungeon.dungeon_map.in_same_room(self.attacker.grid_pos, target.grid_pos):
                    new_targets.add(target)

        return list(new_targets)

    # AI
    def ai_attack(self, p: pokemon.Pokemon):
        self.attacker = p
        self.attacker.face_target(self.dungeon.user.grid_pos)
        self.ai_activate()
    
    def ai_activate(self) -> bool:
        choices = self.ai_possible_moves()
        m = None if not choices else random.choice(choices)
        return self.activate(m)

    def ai_possible_moves(self) -> list[move.Move]:
        res = []
        for i, pp in enumerate(self.attacker.current_status["Moves_pp"]):
            if pp == 0:
                continue
            m = self.attacker.move_set[i]
            if self.can_activate(m):
                res.append(i)
        return res

    def can_activate(self, m: move.Move) -> bool:
        if m.activation_condition != "None": return False
        if self.get_targets(m.range_category):
            return True
        return False

    # ACTIVATION
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

    # EVENTS
    def get_events(self):
        self.events += self.get_init_events()
        effect_events = self.get_events_from_move()
        if effect_events:
            self.events += effect_events
        else:
            self.events += self.get_fail_events()
    
    def get_init_events(self):
        events = []
        name_item = (self.attacker.name, constants.BLUE if self.attacker.poke_type == "User" else constants.YELLOW)
        msg_item = (f" used {self.current_move.name}", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        events.append(("LogEvent", {"Text": text_object}))
        events.append(("SetAnimation", {"Attacker": self.current_move.animation}))
        events.append(("SleepEvent", {"Timer": 20}))
        return events

    def get_fail_events(self):
        text_object = text.Text("The move failed.")
        return [("LogEvent", {"Text": text_object}), ("SleepEvent", {"Timer": 20})]

    def get_events_from_move(self):
        effect = self.current_move.effect_flag
        res = []
        # Deals damage, no special effects.
        if effect == 0:
            for target in self.get_targets(self.current_move.range_category):
                self.defender = target
                res += self.get_events_from_damage_effect()
        else:
            res += self.get_fail_events()
        return res
    
    def get_events_from_damage_effect(self):
        if self.miss():
            return self.get_miss_events()
        damage = self.calculate_damage()
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
        return [("LogEvent", {"Text": text_object}), ("SleepEvent", {"Timer": 20})]

    # TODO: No dmg sfx (same as miss sfx)
    def get_no_damage_events(self):
        name_item = (self.defender.name, constants.BLUE if self.defender.poke_type == "User" else constants.YELLOW)
        msg_item = (f" took no damage.", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        return [("LogEvent", {"Text": text_object}), ("SleepEvent", {"Timer": 20})]

    # TODO: Damage sfx, Defender hurt animation, type effectiveness message
    def get_damage_events(self, damage):
        events = []
        name_item = (self.defender.name, constants.BLUE if self.defender.poke_type == "User" else constants.YELLOW)
        msg_item = (f" took {damage} damage!", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        events.append(("LogEvent", {"Text": text_object}))
        events.append(("DamageEvent", {"Amount": damage, "Target": self.defender}))
        events.append(("SetAnimation", {"Defender": "Hurt"}))
        events.append(("SleepEvent", {"Timer": 20}))
        if damage >= self.defender.hp:
            events += self.get_faint_events()
        return events

    def get_faint_events(self):
        events = []
        name_item = (self.defender.name, constants.BLUE if self.defender.poke_type == "User" else constants.YELLOW)
        msg_item = (" fainted!", constants.WHITE)
        text_object = text.MultiColoredText([name_item, msg_item])
        events.append(("LogEvent", {"Text": text_object}))
        events.append(("FaintEvent", {"Target": self.defender}))
        events.append(("SleepEvent", {"Timer": 20}))
        return events

    def update(self):
        while True:
            if self.index == len(self.events):
                self.deactivate()
                break 
            event_type, event_data = self.events[self.index]
            self.handle_event(event_type, event_data)
            if not event_data.get("Activated", False):
                break
            self.index += 1
        if self.attacker is not None and self.attacker.animation.iterations:
            self.attacker.animation_name = "Idle"

    def handle_event(self, event_type, event_data):
        if event_type == "LogEvent":
            self.handle_log_event(event_data)
        elif event_type == "SleepEvent":
            self.handle_sleep_event(event_data)
        elif event_type == "SetAnimation":
            self.handle_set_animation_event(event_data)
        elif event_type == "DamageEvent":
            self.handle_damage_event(event_data)
        elif event_type == "FaintEvent":
            self.handle_faint_event(event_data)

    def handle_log_event(self, event_data):
        event_data["Activated"] = True
        textbox.message_log.append(event_data["Text"])

    def handle_sleep_event(self, event_data):
        if event_data["Timer"] > 0:
            event_data["Timer"] -= 1
        else:
            event_data["Activated"] = True
    
    def handle_set_animation_event(self, event_data):
        event_data["Activated"] = True
        if self.attacker is not None:
            self.attacker.animation_name = event_data.get("Attacker", self.attacker.animation_name)
        if self.defender is not None:
            self.defender.animation_name = event_data.get("Defender", self.defender.animation_name)

    def handle_damage_event(self, event_data):
        event_data["Activated"] = True
        self.defender = event_data["Target"]
        self.update_hp(event_data["Amount"])
    
    def handle_faint_event(self, event_data):
        event_data["Activated"] = True
        self.defender = event_data["Target"]
        if self.defender.poke_type == "Enemy":
            self.dungeon.active_enemies.remove(self.defender)
        else:
            self.dungeon.active_team.remove(self.defender)

    def calculate_damage(self) -> int:
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
        P = self.current_move.power
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

     # POKEMON LOGIC
    def update_hp(self, amount: int) -> int:
        self.defender.hp -= amount
        print(self.defender.name, self.defender.hp)

    def update_stat_level(self, stat_type, amount):
        self.defender.current_status[stat_type] += amount

    def deal_affliction(self, affliction_type):
        self.defender.current_status[affliction_type] = True

    def clear_affliction(self, affliction_type):
        self.defender.current_status[affliction_type] = False