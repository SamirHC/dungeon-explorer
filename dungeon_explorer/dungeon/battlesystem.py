import math
import random

import pygame
from dungeon_explorer.common import constants, direction, inputstream, text
from dungeon_explorer.dungeon import damage_chart, dungeon, dungeonstatus
from dungeon_explorer.events import event, gameevent
from dungeon_explorer.move import move
from dungeon_explorer.pokemon import pokemon


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
    def process_input(self, input_stream: inputstream.InputStream) -> bool:
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
            move_index = -1
        else:
            return False
        
        self.attacker = self.dungeon.user
        if move_index == -1 or self.attacker.moveset.can_use(move_index):
            self.activate(move_index)
        else:
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(constants.OFF_WHITE)
                .write("You have ran out of PP for this move.")
                .build()
                .render()
            )
            self.dungeon.dungeon_log.write(text_surface)
        
        return True

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
        if self.current_move is not move.REGULAR_ATTACK:
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(self.attacker.name_color)
                .write(self.attacker.name)
                .set_color(constants.OFF_WHITE)
                .write(" used ")
                .set_color(constants.GREEN2)
                .write(self.current_move.name)
                .set_color(constants.OFF_WHITE)
                .write("!")
                .build()
                .render()
            )
            events.append(gameevent.LogEvent(text_surface).with_divider())
        events.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        events.append(event.SleepEvent(20))
        return events

    def get_fail_events(self):
        if self.current_move is move.REGULAR_ATTACK:
            return []
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(constants.OFF_WHITE)
            .write("The move failed.")
            .build()
            .render()
        )
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
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.attacker.name_color)
            .write(self.attacker.name)
            .set_color(constants.OFF_WHITE)
            .write(" missed.")
            .build()
            .render()
        )
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    # TODO: No dmg sfx (same as miss sfx)
    def get_no_damage_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(constants.OFF_WHITE)
            .write(" took no damage.")
            .build()
            .render()
        )
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    # TODO: Damage sfx, Defender hurt animation
    def get_damage_events(self, damage):
        events = []
        effectiveness = self.defender.type.get_type_effectiveness(self.current_move.type)
        if effectiveness is not damage_chart.TypeEffectiveness.REGULAR:
            effectiveness_text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(constants.OFF_WHITE)
                .write(effectiveness.get_message())
                .build()
                .render()
            )
            events.append(gameevent.LogEvent(effectiveness_text_surface))
        damage_text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(constants.OFF_WHITE)
            .write(" took ")
            .set_color(constants.CYAN)
            .write(f"{damage} ")
            .set_color(constants.OFF_WHITE)
            .write("damage!")
            .build()
            .render()
        )
        events.append(gameevent.LogEvent(damage_text_surface))
        events.append(gameevent.DamageEvent(self.defender, damage))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.hurt_animation_id()))
        events.append(event.SleepEvent(20))
        if damage >= self.defender.hp_status:
            events += self.get_faint_events()
        return events

    def get_faint_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(constants.OFF_WHITE)
            .write(" fainted!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.FaintEvent(self.defender))
        events.append(event.SleepEvent(20))
        return events

    def update(self):
        if not self.is_active:
            return
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
        if ev.new_divider:
            self.dungeon.dungeon_log.new_divider()
        self.dungeon.dungeon_log.write(ev.text_surface)
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

    # Damage Mechanics

    def calculate_damage(self) -> int:
        # Step 0 - Special Exceptions
        if self.current_move.category is move.MoveCategory.OTHER:
            return 0
        if self.attacker.status.belly.value == 0 and self.attacker is not self.dungeon.user:
            return 1
        # Step 1 - Stat Modifications
        # Step 2 - Raw Damage Calculation
        if self.current_move.category is move.MoveCategory.PHYSICAL:
            a = self.attacker.attack
            a_stage = self.attacker.attack_status
            d = self.defender.defense
            d_stage = self.defender.defense_status
        elif self.current_move.category is move.MoveCategory.SPECIAL:
            a = self.attacker.attack
            a_stage = self.attacker.attack_status
            d = self.defender.defense
            d_stage = self.defender.defense_status

        A = a * damage_chart.get_attack_multiplier(a_stage)
        D = d * damage_chart.get_defense_multiplier(d_stage)
        L = self.attacker.level
        P = self.current_move.power
        if self.defender not in self.dungeon.party:
            Y = 340 / 256
        else:
            Y = 1
        
        damage = ((A + P) * (39168 / 65536) - (D / 2) +
                  50 * math.log(((A - D) / 8 + L + 50) * 10) - 311) / Y
        
        # Step 3 - Final Damage Modifications
        if damage < 1:
            damage = 1
        elif damage > 999:
            damage = 999

        multiplier = 1
        multiplier *= self.defender.type.get_type_effectiveness(self.current_move.type).value
        
        # STAB bonus
        if self.current_move.type in self.attacker.type:
            multiplier *= 1.5
        
        if self.dungeon.weather is dungeonstatus.Weather.CLOUDY:
            if self.current_move.type is not damage_chart.Type.NORMAL:
                multiplier *= 0.75
        elif self.dungeon.weather is dungeonstatus.Weather.FOG:
            if self.current_move.type is damage_chart.Type.ELECTRIC:
                multiplier *= 0.5
        elif self.dungeon.weather is dungeonstatus.Weather.RAINY:
            if self.current_move.type is damage_chart.Type.FIRE:
                multiplier *= 0.5
            elif self.current_move.type is damage_chart.Type.WATER:
                multiplier *= 1.5
        elif self.dungeon.weather is dungeonstatus.Weather.SUNNY:
            if self.current_move.type is damage_chart.Type.WATER:
                multiplier *= 0.5
            elif self.current_move.type is damage_chart.Type.FIRE:
                multiplier *= 1.5

        critical_chance = random.randint(0, 99)
        if self.current_move.critical > critical_chance:
            multiplier *= 1.5
        
        # Step 4 - Final Calculations
        damage *= multiplier
        damage *= (random.randint(0, 16383) + 57344) / 65536
        damage = round(damage)

        return damage

    def miss(self) -> bool:
        move_acc = self.current_move.accuracy
        if move_acc > 100:
            return False

        acc_stage = self.attacker.accuracy_status
        if self.dungeon.weather is dungeonstatus.Weather.RAINY:
            if self.current_move.name == "Thunder":
                return False
        elif self.dungeon.weather is dungeonstatus.Weather.SUNNY:
            acc_stage -= 2
        if acc_stage < 0:
            acc_stage = 0
        elif acc_stage > 20:
            acc_stage = 20
        acc = move_acc * damage_chart.get_accuracy_multiplier(acc_stage)
        
        eva_stage = self.defender.evasion_status
        if eva_stage < 0:
            eva_stage = 0
        elif eva_stage > 20:
            eva_stage = 20
        acc *= damage_chart.get_evasion_multiplier(eva_stage)

        chance = random.randrange(0, 100)
        hits = chance < acc
        return not hits