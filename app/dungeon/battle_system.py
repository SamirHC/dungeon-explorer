import math
import random
from collections import deque

import pygame
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings, text
from app.dungeon import target_getter
from app.dungeon.dungeon import Dungeon
from app.events import event, gameevent
from app.move.move import MoveRange, MoveCategory
from app.move import damage_mechanics
from app.pokemon.pokemon import Pokemon
from app.pokemon.status_effect import StatusEffect
import app.db.database as db
from app.db import dungeon_log_text
from app.model.type import TypeEffectiveness


class BattleSystem:
    def __init__(self, dungeon: Dungeon, event_queue: deque[event.Event]):
        self.dungeon = dungeon
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log
        self.dispatcher = {i: getattr(self, f"move_{i}", self.move_0) for i in range(321)}

        self.current_move = None
        self.attacker: Pokemon = None
        self.defender: Pokemon = None
        self.defender_fainted = False  # To bypass side effects of damaging moves

        self.events: deque[event.Event] = event_queue

    # USER
    def process_input(self, input_stream: InputStream) -> bool:
        kb = input_stream.keyboard

        attacker = self.party.leader
        action_index = {
            Action.INTERACT: -1,
        }
        for i in range(len(attacker.moveset)):
            if attacker.moveset.selected[i] and attacker.moveset.can_use(i):
                action_index[Action[f"MOVE_{i + 1}"]] = i

        pressed = [a for a in action_index if kb.is_pressed(settings.get_key(a))]

        success = len(pressed) == 1
        if len(pressed) == 1:        
            self.attacker = attacker
            target_getter.set_pokemon(attacker)
            self.activate(action_index[pressed[0]])
        
        return success

    # TARGETS
    def get_targets(self) -> list[Pokemon]:
        return target_getter.get_targets(self.dungeon, self.current_move.move_range)

    # AI
    def ai_attack(self, p: Pokemon):
        self.attacker = p
        target_getter.set_pokemon(p)
        enemies = target_getter.get_enemies(self.dungeon)
        if enemies:
            target_enemy = min(enemies, key=lambda e: max(abs(e.x - self.attacker.x), abs(e.y - self.attacker.y)))
            if self.floor.can_see(self.attacker.position, target_enemy.position):
                self.attacker.face_target(target_enemy.position)
        if self.ai_activate():
            return True
        self.deactivate()
        return False

    def ai_select_move_index(self) -> int:
        REGULAR_ATTACK_INDEX = -1
        moveset = self.attacker.moveset

        move_indices = [REGULAR_ATTACK_INDEX] + [i for i in range(len(moveset)) if moveset.selected[i]]
        weights = [0] + [moveset.weights[i] for i in range(len(moveset)) if moveset.selected[i]]
        weights[0] = len(move_indices)*10

        return random.choices(move_indices, weights)[0]

    def ai_activate(self) -> bool:
        move_index = self.ai_select_move_index()
        self.current_move = (
            self.attacker.moveset[move_index] if move_index != -1
            else db.move_db.REGULAR_ATTACK
        )
        if success := self.can_activate():
            self.activate(move_index)
        return success

    def can_activate(self) -> bool:
        return (
            self.current_move.activation_condition == "None"
            and target_getter.get_targets(self.dungeon, MoveRange.ALL_ENEMIES_IN_THE_ROOM)
            and self.get_targets()
        )

    def activate(self, move_index: int):
        target_getter.set_pokemon(self.attacker)

        self.current_move = (
            db.move_db.REGULAR_ATTACK if move_index == -1
            else self.attacker.moveset[move_index] if self.attacker.moveset.can_use(move_index)
            else db.move_db.STRUGGLE
        )
        if self.current_move in self.attacker.moveset:
            self.attacker.moveset.use(move_index)

        self.attacker.has_turn = False
        self.get_events()

    def deactivate(self):
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.defender_fainted = False

    # EVENTS
    def get_events(self):
        self.events.extend(self.get_init_events())
        effect_events = self.get_events_from_move()
        if effect_events:
            self.events.extend(effect_events)
        else:
            self.events.extend(self.get_fail_events())
    
    def get_init_events(self):
        events = []
        if self.current_move is not db.move_db.REGULAR_ATTACK:
            text_surface = dungeon_log_text.use_move(self.attacker, self.current_move)
            events.append(gameevent.LogEvent(text_surface).with_divider())
        # Skip for:
        # Thrash(9)
        if self.current_move.move_id != 9:
            events += self.get_attacker_move_animation_events()
        return events

    def get_attacker_move_animation_events(self):
        res = []
        res.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        res.append(event.SleepEvent(20))
        return res

    def get_fail_events(self):
        if self.current_move is db.move_db.REGULAR_ATTACK:
            return []
        text_surface = dungeon_log_text.move_fail()
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    def get_events_from_move(self):
        # print(self.current_move.move_id)
        return self.dispatcher.get(self.current_move.move_id, self.dispatcher[0])()
    
    # Effects
    # TODO: Miss sfx, Miss gfx label
    def get_miss_events(self):
        text_surface = dungeon_log_text.move_miss(self.defender)
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    # TODO: No dmg sfx (same as miss sfx)
    def get_no_damage_events(self):
        text_surface = dungeon_log_text.no_damage(self.defender)
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]
    
    def get_calamitous_damage_events(self):
        text_surface = dungeon_log_text.calamatous_damage(self.defender)
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.DamageEvent(self.defender, 9999))
        return events

    # TODO: Damage sfx, Defender hurt animation
    def get_damage_events(self, damage: int):
        if damage == 0:
            return self.get_no_damage_events()
        elif damage >= 9999:
            return self.get_calamitous_damage_events()
        events = []
        effectiveness = db.type_chart.get_move_effectiveness(self.current_move.type, self.defender.type)
        if effectiveness is not TypeEffectiveness.REGULAR:
            effectiveness_text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write(effectiveness.get_message())
                .build()
                .render()
            )
            events.append(gameevent.LogEvent(effectiveness_text_surface))
        damage_text_surface = dungeon_log_text.damage(self.defender, damage)
        events.append(gameevent.LogEvent(damage_text_surface))
        events.append(gameevent.DamageEvent(self.defender, damage))
        if self.defender.has_status_effect(StatusEffect.VITAL_THROW) and self.current_move.category is MoveCategory.PHYSICAL \
            and abs(self.attacker.x - self.defender.x) <= 1 and abs(self.attacker.y - self.defender.y) <= 1:
            self.defender = self.attacker
            events += self.get_fling_events()
        return events

    def get_faint_events(self, p: Pokemon):
        text_surface = dungeon_log_text.defeated(p)
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.FaintEvent(p))
        events.append(event.SleepEvent(20))
        self.defender_fainted = True
        return events

    def get_heal_events(self, heal: int):
        p = self.defender
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(p.name_color)
            .write(p.name)
            .set_color(text.WHITE)
        )
        if p.hp_status == p.hp or heal == 0:
            (tb.write("'s")
            .set_color(text.CYAN)
            .write(" HP")
            .set_color(text.WHITE)
            .write(" didn't change.")
            )
        elif heal + p.hp_status >= p.hp:
            heal = p.hp - p.hp_status
            (tb.write(" recovered ")
            .set_color(text.CYAN)
            .write(f"{heal} HP")
            .set_color(text.WHITE)
            .write("!")
            )
        text_surface = tb.build().render()
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.HealEvent(p, heal))
        events.append(event.SleepEvent(20))
        return events

    def get_recoil_events(self, percent: float):
        damage = math.ceil(self.attacker.status.hp.max_value * percent / 100)
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.attacker.name_color)
            .write(self.attacker.name)
            .set_color(text.WHITE)
            .write(" took ")
            .set_color(text.CYAN)
            .write(str(damage))
            .set_color(text.WHITE)
            .write(" recoil damage\nfrom the move!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.DamageEvent(self.attacker, damage))
        return events

    def get_burn_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" sustained a burn!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "burned", True))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.HURT_ANIMATION_ID))
        events.append(event.SleepEvent(20))
        return events

    def get_freeze_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" is frozen solid!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "frozen", True))
        events.append(event.SleepEvent(20))
        return events

    def get_poisoned_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" was poisoned!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "poisoned", True))
        events.append(event.SleepEvent(20))
        return events

    def get_badly_poisoned_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" was badly poisoned!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "badly_poisoned", True))
        events.append(event.SleepEvent(20))
        return events

    def get_confusion_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" is confused!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "confused", True))
        events.append(event.SleepEvent(20))
        return events

    def get_paralyze_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" is paralyzed!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "paralyzed", True))
        events.append(event.SleepEvent(20))
        return events

    def get_constricted_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" is constricted!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "constriction", True))
        events.append(event.SleepEvent(20))
        return events

    def get_cringe_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" cringed!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.defender, "cringe", True))
        events.append(event.SleepEvent(20))
        return events

    def get_stat_change_events(self, stat: str, amount: int):
        if self.defender_fainted:
            return []
        stat_names = {
            "attack": "Attack",
            "defense": "Defense",
            "sp_attack": "Sp. Atk.",
            "sp_defense": "Sp. Def.",
            "attack_division": "Attack",
            "defense_division": "Defense",
            "sp_attack_division": "Sp. Atk.",
            "sp_defense_division": "Sp. Def.",
            "accuracy": "accuracy",
            "evasion": "evasion",
            "speed": "speed"
        }
        stat_name = stat_names[stat]
        stat_anim_name = stat
        if stat_anim_name.endswith("_division"):
            stat_anim_name = stat_anim_name[:-len("_division")]
        if amount < 0:
            verb = "fell"
            anim_type = 0
        elif amount > 0:
            verb = "rose"
            anim_type = 1
        else:
            verb = "returned to normal"
            anim_type = 2
        if stat.endswith("division"):
            adverb = "harshly"
        elif abs(amount) > 1:
            adverb = "sharply"
        elif abs(amount) == 1:
            adverb = "slightly"
        else:
            adverb = ""
        
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(f"'s {stat_name} {verb} {adverb}!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatChangeEvent(self.defender, stat, amount))
        events.append(gameevent.StatAnimationEvent(self.defender, db.statanimation_db[stat_anim_name, anim_type]))
        events.append(event.SleepEvent(20))
        return events
    
    def get_defense_lower_1_stage(self):
        return self.get_stat_change_events("defense", -1)
    
    def get_asleep_events(self):
        self.defender.clear_affliction(StatusEffect.YAWNING)
        if self.defender.has_status_effect(StatusEffect.ASLEEP):
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(self.defender.name_color)
                .write(self.defender.name)
                .set_color(text.WHITE)
                .write(" is already asleep!")
                .build()
                .render()
            )
        else:
            self.defender.afflict(StatusEffect.ASLEEP) # = random.randint(3, 6)
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(self.defender.name_color)
                .write(self.defender.name)
                .set_color(text.WHITE)
                .write(" fell asleep!")
                .build()
                .render()
                )
        
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.SLEEP_ANIMATION_ID, True))
        events.append(event.SleepEvent(20))
        return events
    
    def get_nightmare_events(self):
        self.defender.clear_affliction(StatusEffect.NIGHTMARE)
        damage = 8
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" awoke from its nightmare\nand took ")
            .set_color(text.CYAN)
            .write(str(damage))
            .set_color(text.WHITE)
            .write(" damage!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.DamageEvent(self.defender, damage))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.IDLE_ANIMATION_ID, True))
        return events
    
    def get_awaken_events(self):
        events = []
        if self.defender.has_status_effect(StatusEffect.NIGHTMARE):
            events += self.get_nightmare_events()
        else:
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(self.defender.name_color)
                .write(self.defender.name)
                .set_color(text.WHITE)
                .write(" woke up!")
                .build()
                .render()
            )
            events.append(gameevent.LogEvent(text_surface).with_divider())
            events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.IDLE_ANIMATION_ID, True))
            events.append(event.SleepEvent(20))
        return events
    
    def get_fling_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" was sent flying!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.HURT_ANIMATION_ID, True))
        events.append(gameevent.FlingEvent(self.defender))
        return events
    
    def get_dig_events(self):
        events = []
        self.current_move = db.move_db[8]
        events.append(gameevent.StatusEvent(self.attacker, "digging", False))
        events.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        events += self.get_all_basic_attack_or_miss_events()
        events.append(event.SleepEvent(20))
        return events

    def is_move_animation_event(self, target: Pokemon) -> bool:
        if not self.events:
            return False
        ev = self.events[0]
        if isinstance(ev, gameevent.StatAnimationEvent):
            return ev.target is target

    def render(self) -> pygame.Surface:
        ev = self.events[0]
        if isinstance(ev, gameevent.StatAnimationEvent):
            return ev.anim.get_current_frame()
        
    def get_single_hit_or_miss_events(self, hit_function):
        res = []
        if damage_mechanics.miss(self.dungeon, self.attacker, self.defender, self.current_move):
            res += self.get_miss_events()
        else:
            res += hit_function()
        return res
    
    def get_all_hit_or_miss_events(self, hit_function):
        res = []
        for target in self.get_targets():
            self.defender = target
            res += self.get_single_hit_or_miss_events(hit_function)
        return res

    def get_basic_attack_events(self):
        damage = damage_mechanics.calculate_damage(self.dungeon, self.attacker, self.defender, self.current_move)
        return self.get_damage_events(damage)

    def get_all_basic_attack_or_miss_events(self):
        return self.get_all_hit_or_miss_events(self.get_basic_attack_events)
    
    def get_chance(self, p: int) -> bool:
        return random.randrange(0, 100) < p

    def get_chance_events(self, p: int, hit_function):
        if self.get_chance(p):
            return hit_function()
        return []

    # Regular Attack
    def move_0(self):
        return self.get_all_basic_attack_or_miss_events()