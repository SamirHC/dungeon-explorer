import math
import random

import pygame
from dungeon_explorer.common import constants, direction, inputstream, text
from dungeon_explorer.dungeon import damage_chart, dungeon
from dungeon_explorer.events import event, gameevent
from dungeon_explorer.pokemon import move, pokemon


class BattleSystem:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon
        self.current_move = None
        self.is_active = False
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.events: list[event.Event] = []
        self.event_index = 0

    def deactivate(self):
        self.events.clear()
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.event_index = 0
        self.is_active = False

    # USER
    def input(self, input_stream: inputstream.InputStream):
        self.attacker = self.dungeon.user
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_1):
            move_index = 0
        elif kb.is_pressed(pygame.K_2):
            move_index = 1
        elif kb.is_pressed(pygame.K_3):
            move_index = 2
        elif kb.is_pressed(pygame.K_4):
            move_index = 3
        elif kb.is_pressed(pygame.K_RETURN):
            return self.activate(-1)
        else:
            return

        if self.attacker.moveset.can_use(move_index):
            self.activate(move_index)
        else:
            msg = "You have ran out of PP for this move."
            self.dungeon.message_log.append(text.build(msg))
        

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

    def in_room_with_enemies(self) -> bool:
        return any([self.dungeon.floor.in_same_room(self.attacker.position, enemy.position) for enemy in self.get_enemies()])

    def get_straight_targets(self):
        move_range = self.current_move.range_category
        target_group = {p.position: p for p in self.get_target_group()}
        result = []
        if not move_range.cuts_corners() and self.dungeon.cuts_corner(self.attacker.position, self.attacker.direction):
            return result
        x, y = self.attacker.position
        for _ in range(move_range.distance()):
            x += self.attacker.direction.x
            y += self.attacker.direction.y
            if self.dungeon.is_wall((x, y)):
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

    def ai_select_move_index(self) -> int:
        # TODO: Filters for "set" moves
        move_indices = [-1] + [i for i, _ in enumerate(self.attacker.moveset)]
        regular_attack_weight = len(move_indices)*10
        weights = [regular_attack_weight] + [w for w in self.attacker.moveset.get_weights()]
        return random.choices(move_indices, weights)[0]
    
    def ai_activate(self) -> bool:
        move_index = self.ai_select_move_index()
        if move_index == -1:
            self.current_move = move.REGULAR_ATTACK
        else:
            self.current_move = self.attacker.moveset[move_index]
            if not self.attacker.moveset.can_use(move_index):
                return
        if not self.can_activate():
            return
        return self.activate(move_index)

    def can_activate(self) -> bool:
        if self.current_move.activation_condition != "None":
            return False
        move_range = self.current_move.range_category
        if move_range is move.MoveRange.USER or move_range.is_room_wide():
            return self.in_room_with_enemies()
        for _ in range(len(direction.Direction)):
            targets = self.get_targets()
            if not targets:
                pass
            elif move_range is move.MoveRange.LINE_OF_SIGHT and targets[0] not in self.get_enemies():
                pass
            else:
                return True
            self.attacker.direction = self.attacker.direction.clockwise()
        return False

    # ACTIVATION
    def activate(self, move_index: int) -> bool:
        if move_index == -1:
            self.current_move = move.REGULAR_ATTACK
        else:
            if not self.attacker.moveset.can_use(move_index):
                return False
            self.attacker.moveset.use(move_index)
            self.current_move = self.attacker.moveset[move_index]

        self.is_active = True
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
        if self.current_move != move.REGULAR_ATTACK:
            items = []
            items.append((self.attacker.name, self.attacker.name_color))
            items.append((" used ", constants.OFF_WHITE))
            items.append((self.current_move.name, constants.GREEN2))
            items.append(("!", constants.OFF_WHITE))
            text_surface = text.build_multicolor(items)
            events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        events.append(event.SleepEvent(20))
        return events

    def get_fail_events(self):
        text_surface = text.build("The move failed.")
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

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
        items.append((" missed.", constants.OFF_WHITE))
        text_surface = text.build_multicolor(items)
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    # TODO: No dmg sfx (same as miss sfx)
    def get_no_damage_events(self):
        items = []
        items.append((self.defender.name, self.defender.name_color))
        items.append((" took no damage.", constants.OFF_WHITE))
        text_surface = text.build_multicolor(items)
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    # TODO: Damage sfx, Defender hurt animation, type effectiveness message
    def get_damage_events(self, damage):
        items = []
        items.append((self.defender.name, self.defender.name_color))
        items.append((" took ", constants.OFF_WHITE))
        items.append((f"{damage} ", constants.CYAN))
        items.append(("damage!", constants.OFF_WHITE))
        text_surface = text.build_multicolor(items)
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.DamageEvent(self.defender, damage))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.hurt_animation_id()))
        events.append(event.SleepEvent(20))
        if damage >= self.defender.hp_status:
            events += self.get_faint_events()
        return events

    def get_faint_events(self):
        items = []
        items.append((self.defender.name, self.defender.name_color))
        items.append((" fainted!", constants.OFF_WHITE))
        text_surface = text.build_multicolor(items)
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.FaintEvent(self.defender))
        events.append(event.SleepEvent(20))
        return events

    def update(self):
        if self.event_index == 0:
            for p in self.dungeon.all_sprites:
                p.animation_id = p.idle_animation_id()
        while True:
            if self.event_index == len(self.events):
                self.deactivate()
                break 
            event = self.events[self.event_index]
            self.handle_event(event)
            if not event.handled:
                break
            self.event_index += 1

    def handle_event(self, ev: event.Event):
        if isinstance(ev, gameevent.LogEvent):
            self.handle_log_event(ev)
        elif isinstance(ev, event.SleepEvent):
            self.handle_sleep_event(ev)
        elif isinstance(ev, gameevent.SetAnimationEvent):
            self.handle_set_animation_event(ev)
        elif isinstance(ev, gameevent.DamageEvent):
            self.handle_damage_event(ev)
        elif isinstance(ev, gameevent.FaintEvent):
            self.handle_faint_event(ev)

    def handle_log_event(self, ev: gameevent.LogEvent):
        self.dungeon.message_log.append(ev.text_surface)
        ev.handled = True

    def handle_sleep_event(self, ev: event.SleepEvent):
        if ev.time > 0:
            ev.time -= 1
        else:
            ev.handled = True
    
    def handle_set_animation_event(self, ev: gameevent.SetAnimationEvent):
        ev.target.animation_id = ev.animation_name
        ev.handled = True

    def handle_damage_event(self, ev: gameevent.DamageEvent):
        ev.target.status.hp.reduce(ev.amount)
        #print(self.defender.name, self.defender.hp_status)
        ev.handled = True
    
    def handle_faint_event(self, ev: gameevent.FaintEvent):
        self.dungeon.floor[ev.target.position].pokemon_ptr = None
        if isinstance(ev.target, pokemon.EnemyPokemon):
            self.dungeon.active_enemies.remove(ev.target)
        else:
            self.dungeon.party.remove(ev.target)
        self.dungeon.spawned.remove(ev.target)
        ev.handled = True

    def calculate_damage(self) -> int:
        # Step 0 - Determine Stats
        if self.current_move.category is move.MoveCategory.PHYSICAL:
            A = self.attacker.attack * \
                damage_chart.get_attack_multiplier(self.attacker.attack_status)
            D = self.defender.defense * \
                damage_chart.get_defense_multiplier(self.defender.defense_status)
        elif self.current_move.category is move.MoveCategory.SPECIAL:
            A = self.attacker.sp_attack * \
                damage_chart.get_attack_multiplier(self.attacker.sp_attack_status)
            D = self.defender.sp_defense * \
                damage_chart.get_defense_multiplier(self.defender.sp_defense_status)
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
        raw_accuracy = damage_chart.get_accuracy_multiplier(self.attacker.accuracy_status) * self.current_move.accuracy
        return round(raw_accuracy) <= i
