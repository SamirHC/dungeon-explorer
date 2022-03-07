import math
import random

import pygame
from dungeon_explorer.common import constants, direction, inputstream, text
from dungeon_explorer.dungeon import damage_chart, dungeon, tile
from dungeon_explorer.pokemon import move, pokemon, pokemondata


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
        self.attacker = self.dungeon.user
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
    def get_targets(self) -> list[pokemon.Pokemon]:
        move_range = self.current_move.range_category
        if move_range is move.MoveRange.USER:
            return [self.attacker]
        if move_range.is_straight():
            return self.get_straight_targets()
        if move_range.is_surrounding():
            return self.get_surrounding_targets()
        if move_range.is_room_wide():
            return self.get_room_targets()
        return []

    def get_target_group(self) -> list[pokemon.Pokemon]:
        target_type = self.current_move.range_category.target_type()
        if target_type is move.TargetType.USER:
            return [self.attacker]
        if target_type is move.TargetType.ALL:
            return self.dungeon.all_sprites

        if target_type is move.TargetType.ALLIES:
            return self.get_allies()
        if target_type is move.TargetType.ENEMIES:
            return self.get_enemies()

    def get_enemies(self) -> list[pokemon.Pokemon]:
        if isinstance(self.attacker, pokemon.EnemyPokemon):
            return self.dungeon.party.party
        return self.dungeon.active_enemies

    def get_allies(self) -> list[pokemon.Pokemon]:
        if isinstance(self.attacker, pokemon.EnemyPokemon):
            return self.dungeon.active_enemies
        return self.dungeon.party.party

    def get_straight_targets(self):
        move_range = self.current_move.range_category
        target_group = {p.position: p for p in self.get_target_group()}
        result = []
        if not move_range.cuts_corners() and self.dungeon.floor.cuts_corner(self.attacker.position, self.attacker.direction):
            return result
        x, y = self.attacker.position
        for _ in range(move_range.distance()):
            x += self.attacker.direction.x
            y += self.attacker.direction.y
            if self.dungeon.floor[x, y].terrain is tile.Terrain.WALL:
                return result
            if (x, y) in target_group:
                result.append(target_group[x, y])
                return result
        return result
            
    def get_surrounding_targets(self):
        target_group = {p.position: p for p in self.get_target_group()}
        result = []
        for d in list(direction.Direction):
            x = self.attacker.x + d.x
            y = self.attacker.y + d.y
            if (x, y) in target_group:
                result.append(target_group[x, y])
        return result

    def get_room_targets(self):
        target_group = {p.position: p for p in self.get_target_group()}
        result = []
        for position in target_group:
            if self.dungeon.floor.in_same_room(self.attacker.position, position):
                result.append(target_group[position])
        for p in self.get_surrounding_targets():
            if p not in result:
                result.append(p)
        return result

    # AI
    def ai_attack(self, p: pokemon.Pokemon):
        self.attacker = p
        self.attacker.face_target(self.dungeon.user.position)
        self.ai_activate()
    
    def ai_activate(self) -> bool:
        move_index = random.choices(range(len(self.attacker.move_set)), [m.weight for m in self.attacker.move_set])[0]
        self.current_move = self.attacker.move_set[move_index]
        if not self.can_activate():
            move_index = None
        return self.activate(move_index)

    def can_activate(self) -> bool:
        m = self.current_move
        if m.activation_condition != "None":
            return False
        if m.range_category is move.MoveRange.USER:
            return False
        for _ in range(len(direction.Direction)):
            if self.get_targets():
                return True
            self.attacker.direction = self.attacker.direction.clockwise()
        return False

    # ACTIVATION
    def activate(self, move_index: int) -> bool:
        self.current_move = self.attacker.move_set[move_index]

        if not self.current_move:
            return False
        if self.attacker.current_status["Moves_pp"][move_index] == 0:
            msg = "You have ran out of PP for this move."
            self.dungeon.message_log.append(text.build(msg))
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
        if self.current_move != pokemondata.Moveset.REGULAR_ATTACK:
            items = []
            items.append((self.attacker.name, self.attacker.name_color))
            items.append((" used ", constants.WHITE))
            items.append((self.current_move.name, constants.GREEN2))
            items.append(("!", constants.WHITE))
            text_surface = text.build_multicolor(items)
            events.append(("LogEvent", {"Text": text_surface}))
        events.append(("SetAnimation", {"Attacker": self.current_move.animation}))
        events.append(("SleepEvent", {"Timer": 20}))
        return events

    def get_fail_events(self):
        text_surface = text.build("The move failed.")
        return [("LogEvent", {"Text": text_surface}), ("SleepEvent", {"Timer": 20})]

    def get_events_from_move(self):
        effect = self.current_move.effect
        res = []
        # Deals damage, no special effects.
        if effect == 0:
            for target in self.get_targets():
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
        items = []
        items.append((self.attacker.name, self.attacker.name_color))
        items.append((" missed.", constants.WHITE))
        text_surface = text.build_multicolor(items)
        return [("LogEvent", {"Text": text_surface}), ("SleepEvent", {"Timer": 20})]

    # TODO: No dmg sfx (same as miss sfx)
    def get_no_damage_events(self):
        items = []
        items.append((self.defender.name, self.defender.name_color))
        items.append((" took no damage.", constants.WHITE))
        text_surface = text.build_multicolor(items)
        return [("LogEvent", {"Text": text_surface}), ("SleepEvent", {"Timer": 20})]

    # TODO: Damage sfx, Defender hurt animation, type effectiveness message
    def get_damage_events(self, damage):
        items = []
        items.append((self.defender.name, self.defender.name_color))
        items.append((" took ", constants.WHITE))
        items.append((f"{damage} ", constants.CYAN))
        items.append(("damage!", constants.WHITE))
        text_surface = text.build_multicolor(items)
        events = []
        events.append(("LogEvent", {"Text": text_surface}))
        events.append(("DamageEvent", {"Amount": damage, "Target": self.defender}))
        events.append(("SetAnimation", {"Defender": "Hurt"}))
        events.append(("SleepEvent", {"Timer": 20}))
        if damage >= self.defender.hp_status:
            events += self.get_faint_events()
        return events

    def get_faint_events(self):
        items = []
        items.append((self.defender.name, self.defender.name_color))
        items.append((" fainted!", constants.WHITE))
        text_surface = text.build_multicolor(items)
        events = []
        events.append(("LogEvent", {"Text": text_surface}))
        events.append(("FaintEvent", {"Target": self.defender}))
        events.append(("SleepEvent", {"Timer": 20}))
        return events

    def update(self):
        if self.index == 0:
            for p in self.dungeon.all_sprites:
                p.animation_name = "Idle"
        while True:
            if self.index == len(self.events):
                self.deactivate()
                break 
            event_type, event_data = self.events[self.index]
            self.handle_event(event_type, event_data)
            if not event_data.get("Activated", False):
                break
            self.index += 1

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
        self.dungeon.message_log.append(event_data["Text"])

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
        self.defender.status.hp.reduce(event_data["Amount"])
        print(self.defender.name, self.defender.hp_status)
    
    def handle_faint_event(self, event_data):
        event_data["Activated"] = True
        self.defender = event_data["Target"]
        if isinstance(self.defender, pokemon.EnemyPokemon):
            self.dungeon.active_enemies.remove(self.defender)
        else:
            self.dungeon.party.remove(self.defender)
        self.dungeon.spawned.remove(self.defender)

    def calculate_damage(self) -> int:
        # Step 0 - Determine Stats
        if self.current_move.category is move.MoveCategory.PHYSICAL:
            A = self.attacker.attack * \
                damage_chart.get_stat_multiplier(damage_chart.Stat.ATTACK, self.attacker.attack_status)
            D = self.defender.defense * \
                damage_chart.get_stat_multiplier(damage_chart.Stat.DEFENSE, self.defender.defense_status)
        elif self.current_move.category is move.MoveCategory.SPECIAL:
            A = self.attacker.sp_attack * \
                damage_chart.get_stat_multiplier(damage_chart.Stat.SP_ATTACK, self.attacker.sp_attack_status)
            D = self.defender.sp_defense * \
                damage_chart.get_stat_multiplier(damage_chart.Stat.SP_DEFENSE, self.defender.sp_defense_status)
        else:
            return 0
        L = self.attacker.level
        P = self.current_move.power
        if isinstance(self.defender, pokemon.UserPokemon):
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
        raw_accuracy = damage_chart.get_stat_multiplier(damage_chart.Stat.ACCURACY, self.attacker.accuracy_status) * self.current_move.accuracy
        return round(raw_accuracy) <= i
