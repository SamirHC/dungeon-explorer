import math
import random
from collections import deque

import pygame
from app.common.inputstream import InputStream
from app.common import settings, text
from app.dungeon.dungeon import Dungeon
from app.dungeon import floorstatus
from app.events import event, gameevent
from app.move.move import MoveRange, MoveCategory
from app.pokemon import pokemon, pokemondata
from app.db import move_db, stat_stage_chart, statanimation_db, type_chart
from app.model.type import Type, TypeEffectiveness


class TargetGetter:
    def __init__(self, dungeon: Dungeon):
        self.floor = dungeon.floor
        self.party = dungeon.party
        self.enemies = self.floor.active_enemies
        self.target_getters = {
            MoveRange.ADJACENT_POKEMON: self.get_none,
            MoveRange.ALL_ENEMIES_IN_THE_ROOM: self.get_all_enemies_in_the_room,
            MoveRange.ALL_ENEMIES_ON_THE_FLOOR: self.get_all_enemies_on_the_floor,
            MoveRange.ALL_IN_THE_ROOM_EXCEPT_USER: self.get_all_in_the_room_except_user,
            MoveRange.ALL_POKEMON_IN_THE_ROOM: self.get_all_pokemon_in_the_room,
            MoveRange.ALL_POKEMON_ON_THE_FLOOR: self.get_all_pokemon_on_the_floor,
            MoveRange.ALL_TEAM_MEMBERS_IN_THE_ROOM: self.get_all_team_members_in_the_room,
            MoveRange.ENEMIES_WITHIN_1_TILE_RANGE: self.get_enemies_within_1_tile_range,
            MoveRange.ENEMY_IN_FRONT: self.get_enemy_in_front,
            MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS: self.get_enemy_in_front_cuts_corners,
            MoveRange.ENEMY_UP_TO_2_TILES_AWAY: self.get_enemy_up_to_2_tiles_away,
            MoveRange.FACING_POKEMON: self.get_facing_pokemon,
            MoveRange.FACING_POKEMON_CUTS_CORNERS: self.get_facing_pokemon_cuts_corners,
            MoveRange.FACING_TILE_AND_2_FLANKING_TILES: self.get_facing_tile_and_2_flanking_tiles,
            MoveRange.FLOOR: self.get_none,
            MoveRange.ITEM: self.get_none,
            MoveRange.LINE_OF_SIGHT: self.get_line_of_sight,
            MoveRange.ONLY_THE_ALLIES_IN_THE_ROOM: self.get_only_the_allies_in_the_room,
            MoveRange.POKEMON_WITHIN_1_TILE_RANGE: self.get_pokemon_within_1_tile_range,
            MoveRange.POKEMON_WITHIN_2_TILE_RANGE: self.get_pokemon_within_2_tile_range,
            MoveRange.SPECIAL: self.get_none,
            MoveRange.TEAM_MEMBERS_ON_THE_FLOOR: self.get_team_members_on_the_floor,
            MoveRange.USER: self.get_user,
            MoveRange.WALL: self.get_none
        }
    
    def __getitem__(self, move_range: MoveRange):
        return self.target_getters[move_range]

    def set_attacker(self, pokemon: pokemon.Pokemon):
        self.attacker = pokemon

    def get_enemies(self) -> list[pokemon.Pokemon]:
        if isinstance(self.attacker, pokemon.EnemyPokemon):
            return self.party.members
        return self.enemies

    def get_allies(self) -> list[pokemon.Pokemon]:
        if isinstance(self.attacker, pokemon.EnemyPokemon):
            return self.enemies
        return self.party.members       
    
    def deactivate(self):
        self.attacker = None

    def get_straight_pokemon(self, distance: int=1, cuts_corner: bool=False) -> list[pokemon.Pokemon]:
        is_phasing = self.attacker.movement_type is pokemondata.MovementType.PHASING
        if is_phasing:
            pass
        elif not cuts_corner and self.floor.cuts_corner((self.attacker.position), self.attacker.direction):
            return []
        
        x, y = self.attacker.position
        dx, dy = self.attacker.direction.value
        for _ in range(distance):
            x += dx
            y += dy
            if self.floor.is_wall((x, y)) and not is_phasing:
                return []
            p = self.floor[x, y].pokemon_ptr
            if p is not None:
                return [p]
        return []
    
    def get_surrounding_pokemon(self, radius: int=1) -> list[pokemon.Pokemon]:
        res = []
        for p in self.floor.spawned:
            if p is self.attacker:
                continue
            if max(abs(p.x - self.attacker.x), abs(p.y - self.attacker.y)) <= radius:
                res.append(p)
        return res

    def get_room_pokemon(self) -> list[pokemon.Pokemon]:
        res = []
        for p in self.floor.spawned:
            if self.floor.in_same_room(self.attacker.position, p.position):
                res.append(p)
        for p in self.get_surrounding_pokemon(2):
            if p not in res:
                res.append(p)
        return res

    def get_none(self):
        return []
        
    def get_all_enemies_in_the_room(self):
        return [p for p in self.get_room_pokemon() if p in self.get_enemies()]
    
    def get_all_enemies_on_the_floor(self):
        return self.get_enemies()

    def get_all_in_the_room_except_user(self):
        return [p for p in self.get_room_pokemon() if p is not self.attacker]
    
    def get_all_pokemon_in_the_room(self):
        return self.get_room_pokemon()

    def get_all_pokemon_on_the_floor(self):
        return self.floor.spawned

    def get_all_team_members_in_the_room(self):
        return [p for p in self.get_room_pokemon() if p in self.get_allies()]

    def get_enemies_within_1_tile_range(self):
        return [p for p in self.get_surrounding_pokemon() if p in self.get_enemies()]

    def get_enemy_in_front(self):
        return [p for p in self.get_straight_pokemon(1, False) if p in self.get_enemies()]

    def get_enemy_in_front_cuts_corners(self):
        return [p for p in self.get_straight_pokemon(1, True) if p in self.get_enemies()]

    def get_enemy_up_to_2_tiles_away(self):
        return [p for p in self.get_straight_pokemon(2, True) if p in self.get_enemies()]

    def get_facing_pokemon(self):
        return self.get_straight_pokemon(1, False)

    def get_facing_pokemon_cuts_corners(self):
        return self.get_straight_pokemon(1, True)

    def get_facing_tile_and_2_flanking_tiles(self):
        return []

    def get_line_of_sight(self):
        return [p for p in self.get_straight_pokemon(10, True) if p in self.get_enemies()]

    def get_only_the_allies_in_the_room(self):
        return [p for p in self.get_room_pokemon() if p is not self.attacker and p in self.get_allies()]

    def get_pokemon_within_1_tile_range(self):
        return self.get_surrounding_pokemon(1)

    def get_pokemon_within_2_tile_range(self):
        return self.get_surrounding_pokemon(2)

    def get_team_members_on_the_floor(self):
        return self.get_allies()

    def get_user(self):
        return [self.attacker]

"""
Event Producer/Publisher for battle-related events. Events published 
are sent to the EventQueue.
"""
class BattleSystem:
    def __init__(self, dungeon: Dungeon, event_queue: deque[event.Event]):
        self.dungeon = dungeon
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log
        self.dispatcher = {i: getattr(self, f"move_{i}", self.move_0) for i in range(321)}
        self.target_getter = TargetGetter(dungeon)

        self.current_move = None
        self.attacker: pokemon.Pokemon = None
        self.defender: pokemon.Pokemon = None
        self.defender_fainted = False  # To bypass side effects of damaging moves

        self.events: deque[event.Event] = event_queue

    # USER
    def process_input(self, input_stream: InputStream) -> bool:
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_attack_1_key()):
            move_index = 0
        elif kb.is_pressed(settings.get_attack_2_key()):
            move_index = 1
        elif kb.is_pressed(settings.get_attack_3_key()):
            move_index = 2
        elif kb.is_pressed(settings.get_attack_4_key()):
            move_index = 3
        elif kb.is_pressed(settings.get_regular_attack_key()):
            move_index = -1
        else:
            return False

        if move_index + 1 > len(self.party.leader.moveset):
            return False
        if not self.party.leader.moveset.selected[move_index]:
            return False
        
        self.attacker = self.party.leader
        self.target_getter.set_attacker(self.attacker)
        if move_index == -1 or self.attacker.moveset.can_use(move_index):
            self.activate(move_index)
        else:
            # "The set move can't be used."
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write("You have ran out of PP for this move.")
                .build()
                .render()
            )
            self.log.write(text_surface)
        
        return True

    # TARGETS
    def get_targets(self) -> list[pokemon.Pokemon]:
        return self.target_getter[self.current_move.move_range]()

    # AI
    def ai_attack(self, p: pokemon.Pokemon):
        self.attacker = p
        self.target_getter.set_attacker(p)
        enemies = self.target_getter.get_enemies()
        if enemies:
            target_enemy = min(enemies, key=lambda e: max(abs(e.x - self.attacker.x), abs(e.y - self.attacker.y)))
            if self.floor.can_see(self.attacker.position, target_enemy.position):
                self.attacker.face_target(target_enemy.position)
        if self.ai_activate():
            return True
        self.deactivate()
        return False

    def ai_select_move_index(self) -> int:
        move_indices = [-1]
        weights = [0]
        moveset = self.attacker.moveset
        for i, _ in enumerate(moveset):
            if not moveset.selected[i]:
                continue
            move_indices.append(i)
            weights.append(moveset.weights[i])
        regular_attack_weight = len(move_indices)*10
        weights[0] = regular_attack_weight
        return random.choices(move_indices, weights)[0]
    
    def ai_activate(self) -> bool:
        move_index = self.ai_select_move_index()
        if move_index == -1:
            self.current_move = move_db.REGULAR_ATTACK
        else:
            self.current_move = self.attacker.moveset[move_index]
        if self.can_activate():
            return self.activate(move_index)
        return False

    def can_activate(self) -> bool:
        if self.current_move.activation_condition != "None":
            return False
        if not any(self.target_getter[MoveRange.ALL_ENEMIES_IN_THE_ROOM]()):
            return False
        if not self.get_targets():
            return False
        return True

    # ACTIVATION
    def activate(self, move_index: int) -> bool:
        self.target_getter.set_attacker(self.attacker)
        if move_index == -1:
            self.current_move = move_db.REGULAR_ATTACK
        elif self.attacker.moveset.can_use(move_index):
            self.attacker.moveset.use(move_index)
            self.current_move = self.attacker.moveset[move_index]
        else:
            self.current_move = move_db.STRUGGLE

        self.attacker.has_turn = False
        self.get_events()
        return True

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
        if self.current_move is not move_db.REGULAR_ATTACK:
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(self.attacker.name_color)
                .write(self.attacker.name)
                .set_color(text.WHITE)
                .write(" used ")
                .set_color(text.LIME)
                .write(self.current_move.name)
                .set_color(text.WHITE)
                .write("!")
                .build()
                .render()
            )
            events.append(gameevent.LogEvent(text_surface).with_divider())
        events.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        events.append(event.SleepEvent(20))
        return events

    def get_attacker_move_animation_events(self):
        res = []
        res.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        res.append(event.SleepEvent(20))
        return res

    def get_fail_events(self):
        if self.current_move is move_db.REGULAR_ATTACK:
            return []
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("The ")
            .set_color(text.LIME)
            .write("move")
            .set_color(text.WHITE)
            .write(" failed!")
            .build()
            .render()
        )
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    def get_events_from_move(self):
        print(self.current_move.move_id)
        return self.dispatcher.get(self.current_move.move_id, self.dispatcher[0])()
    
    # Effects
    # TODO: Miss sfx, Miss gfx label
    def get_miss_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("The move missed ")
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write("!")
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
            .set_color(text.WHITE)
            .write(" took no damage!")
            .build()
            .render()
        )
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]
    
    def get_calamitous_damage_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write( "took calamitous damage!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.DamageEvent(self.defender, 9999))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.HURT_ANIMATION_ID))
        events.append(event.SleepEvent(20))
        events += self.get_faint_events(self.defender)
        return events

    # TODO: Damage sfx, Defender hurt animation
    def get_damage_events(self, damage: int):
        if damage == 0:
            return self.get_no_damage_events()
        elif damage >= 9999:
            return self.get_calamitous_damage_events()
        events = []
        effectiveness = type_chart.get_move_effectiveness(self.current_move.type, self.defender.type)
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
        damage_text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.defender.name_color)
            .write(self.defender.name)
            .set_color(text.WHITE)
            .write(" took ")
            .set_color(text.CYAN)
            .write(f"{damage} ")
            .set_color(text.WHITE)
            .write("damage!")
            .build()
            .render()
        )
        events.append(gameevent.LogEvent(damage_text_surface))
        events.append(gameevent.DamageEvent(self.defender, damage))
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.HURT_ANIMATION_ID))
        events.append(event.SleepEvent(20))
        if damage >= self.defender.hp_status:
            events += self.get_faint_events(self.defender)
        elif self.defender.status.vital_throw and self.current_move.category is MoveCategory.PHYSICAL \
            and abs(self.attacker.x - self.defender.x) <= 1 and abs(self.attacker.y - self.defender.y) <= 1:
            self.defender = self.attacker
            events += self.get_fling_events()
        return events

    def get_faint_events(self, p: pokemon.Pokemon):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(p.name_color)
            .write(p.name)
            .set_color(text.WHITE)
            .write(" was defeated!")
            .build()
            .render()
        )
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
        events.append(gameevent.SetAnimationEvent(self.attacker, self.attacker.sprite.HURT_ANIMATION_ID))
        events.append(event.SleepEvent(20))
        if damage >= self.attacker.hp_status:
            events += self.get_faint_events(self.attacker)
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
        events.append(gameevent.StatAnimationEvent(self.defender, statanimation_db[stat_anim_name, anim_type]))
        events.append(event.SleepEvent(20))
        return events
    
    def get_defense_lower_1_stage(self):
        return self.get_stat_change_events("defense", -1)
    
    def get_asleep_events(self):
        if self.defender.status.yawning > 0:
            self.defender.status.yawning = 0
        elif self.defender.status.asleep > 0:
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
            self.defender.status.asleep = random.randint(3, 6)
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
        self.defender.status.nightmare = False
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
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.HURT_ANIMATION_ID))
        events.append(event.SleepEvent(20))
        if self.defender.hp_status <= damage:
            events.append(gameevent.FaintEvent(self.defender))
        return events
    
    def get_awaken_events(self):
        events = []
        if self.defender.status.nightmare:
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
        self.current_move = move_db[8]
        events.append(gameevent.StatusEvent(self.attacker, "digging", False))
        events.append(gameevent.SetAnimationEvent(self.attacker, self.current_move.animation))
        events += self.get_all_basic_attack_or_miss_events()
        events.append(event.SleepEvent(20))
        return events

    # Damage Mechanics
    def calculate_damage(self, optional_multiplier=1) -> int:
        # Step 0 - Special Exceptions
        if self.current_move.category is MoveCategory.OTHER:
            return 0
        if self.attacker.status.belly.value == 0 and self.attacker is not self.party.leader:
            return 1
        # Step 1 - Stat Modifications
        # Step 2 - Raw Damage Calculation
        if self.current_move.category is MoveCategory.PHYSICAL:
            a = self.attacker.attack
            a_stage = self.attacker.attack_status
            d = self.defender.defense
            d_stage = self.defender.defense_status
        elif self.current_move.category is MoveCategory.SPECIAL:
            a = self.attacker.attack
            a_stage = self.attacker.attack_status
            d = self.defender.defense
            d_stage = self.defender.defense_status

        A = a * stat_stage_chart.get_attack_multiplier(a_stage)
        D = d * stat_stage_chart.get_defense_multiplier(d_stage)
        L = self.attacker.level
        P = self.current_move.power
        if self.defender not in self.party:
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
        multiplier *= type_chart.get_move_effectiveness(self.current_move.type, self.defender.type).value
        
        # STAB bonus
        if self.current_move.type in self.attacker.type:
            multiplier *= 1.5
        
        if self.floor.status.weather is floorstatus.Weather.CLOUDY:
            if self.current_move.type is not Type.NORMAL:
                multiplier *= 0.75
        elif self.floor.status.weather is floorstatus.Weather.FOG:
            if self.current_move.type is Type.ELECTRIC:
                multiplier *= 0.5
        elif self.floor.status.weather is floorstatus.Weather.RAINY:
            if self.current_move.type is Type.FIRE:
                multiplier *= 0.5
            elif self.current_move.type is Type.WATER:
                multiplier *= 1.5
        elif self.floor.status.weather is floorstatus.Weather.SUNNY:
            if self.current_move.type is Type.WATER:
                multiplier *= 0.5
            elif self.current_move.type is Type.FIRE:
                multiplier *= 1.5

        critical_chance = random.randint(0, 99)
        if self.current_move.critical > critical_chance:
            multiplier *= 1.5
        
        # Step 4 - Final Calculations
        damage *= multiplier
        damage *= optional_multiplier
        damage *= (random.randint(0, 16383) + 57344) / 65536
        damage = round(damage)

        return damage

    def miss(self) -> bool:
        if self.defender.status.digging:
            return True
        
        move_acc = self.current_move.accuracy
        if move_acc > 100:
            return False

        acc_stage = self.attacker.accuracy_status
        if self.current_move.name == "Thunder":
            if self.floor.status.weather is floorstatus.Weather.RAINY:
                return False
            elif self.floor.status.weather is floorstatus.Weather.SUNNY:
                acc_stage -= 2
        if acc_stage < 0:
            acc_stage = 0
        elif acc_stage > 20:
            acc_stage = 20
        acc = move_acc * stat_stage_chart.get_accuracy_multiplier(acc_stage)
        
        eva_stage = self.defender.evasion_status
        if eva_stage < 0:
            eva_stage = 0
        elif eva_stage > 20:
            eva_stage = 20
        acc *= stat_stage_chart.get_evasion_multiplier(eva_stage)

        return not self.get_chance(acc)

    def is_move_animation_event(self, target: pokemon.Pokemon) -> bool:
        if not self.events:
            return False
        ev = self.events[0]
        if isinstance(ev, gameevent.StatAnimationEvent):
            return ev.target is target

    def render(self) -> pygame.Surface:
        ev = self.events[0]
        if isinstance(ev, gameevent.StatAnimationEvent):
            return ev.anim.render()
        
    def get_single_hit_or_miss_events(self, hit_function):
        res = []
        if self.miss():
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
        damage = self.calculate_damage()
        return self.get_damage_events(damage)

    def get_all_basic_attack_or_miss_events(self):
        return self.get_all_hit_or_miss_events(self.get_basic_attack_events)
    
    def get_chance(self, p: int) -> bool:
        return random.randrange(0, 100) < p

    def get_chance_events(self, p: int, hit_function):
        if self.get_chance(p):
            return hit_function()
        return []

    # Moves
    # Regular Attack
    def move_0(self):
        return self.get_all_basic_attack_or_miss_events()
    # Iron Tail
    def move_1(self):
        # it shoudn't be possible to reduce defense when the attack misses.
        def _iron_tail_effect():
            events = self.get_basic_attack_events()
            events += self.get_chance_events(30, self.get_defense_lower_1_stage)
            return events
        return self.get_all_hit_or_miss_events(_iron_tail_effect)
    # Ice Ball
    def move_2(self):
        multiplier = 1
        res = []
        for target in self.get_targets():
            self.defender = target
            for i in range(5):
                if self.miss():
                    res += self.get_miss_events()
                    break
                damage = self.calculate_damage(multiplier)
                res += self.get_damage_events(damage)
                if (self.defender_fainted):
                    break
                if (i != 4):
                    multiplier *= 1.5
                    res += self.get_attacker_move_animation_events()
        return res
    # Yawn
    def move_3(self):
        def _yawn_events():
            yawn_state = self.defender.status.yawning
            sleep_state = self.defender.status.asleep
            if (yawn_state == 0 and sleep_state == 0):
                text_surface = (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(self.defender.name_color)
                    .write(self.defender.name)
                    .set_color(text.WHITE)
                    .write(" yawned!")
                    .build()
                    .render()
                )
                self.defender.status.yawning = 3
            elif (yawn_state > 0):
                text_surface = (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(self.defender.name_color)
                    .write(self.defender.name)
                    .set_color(text.WHITE)
                    .write(" is already yawning!")
                    .build()
                    .render()
                )
            elif (sleep_state > 0):
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
            events = []
            events.append(gameevent.LogEvent(text_surface))
            events.append(event.SleepEvent(20))
            return events
        return self.get_all_hit_or_miss_events(_yawn_events)
    # Lovely Kiss
    def move_4(self):
        return self.get_all_hit_or_miss_events(self.get_asleep_events)
    # Nightmare
    def move_5(self):
        def _nightmare_effect():
            if (not self.defender.status.nightmare):
                # Overrides any other sleep status conditions
                self.defender.status.asleep = random.randint(4, 7)
                self.defender.status.napping = False
                self.defender.status.yawning = 0
                self.defender.status.nightmare = True
                text_surface = (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(self.defender.name_color)
                    .write(self.defender.name)
                    .set_color(text.WHITE)
                    .write(" is caught in a nightmare!")
                    .build()
                    .render()
                )
            else:
                text_surface = (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(self.defender.name_color)
                    .write(self.defender.name)
                    .set_color(text.WHITE)
                    .write(" is already having a nightmare!")
                    .build()
                    .render()
                )
            events = []
            events.append(gameevent.LogEvent(text_surface))
            events.append(gameevent.SetAnimationEvent(self.defender, self.defender.sprite.SLEEP_ANIMATION_ID, True))
            events.append(event.SleepEvent(20))
            return events
        return self.get_all_hit_or_miss_events(_nightmare_effect)
    # Morning Sun
    def move_6(self):
        switcher = {
            floorstatus.Weather.CLEAR: 50,
            floorstatus.Weather.CLOUDY: 30,
            floorstatus.Weather.FOG: 10,
            floorstatus.Weather.HAIL: 10,
            floorstatus.Weather.RAINY: 10,
            floorstatus.Weather.SANDSTORM: 20,
            floorstatus.Weather.SNOW: 1,
            floorstatus.Weather.SUNNY: 80
        }
        heal_amount = switcher[self.floor.status.weather]
        def _morning_sun_effect():
            return self.get_heal_events(heal_amount)
        return self.get_all_hit_or_miss_events(_morning_sun_effect)
    # Vital Throw
    def move_7(self):
        def _vital_throw_effect():
            tb = (
                text.TextBuilder()
                    .set_shadow(True)
                    .set_color(self.defender.name_color)
                    .write(self.defender.name)
                    .set_color(text.WHITE)
            )
            if self.defender.status.vital_throw:
                tb.write(" is already ready with its\nVital Throw!")
            else:
                tb.write(" readied its Vital Throw!")
                self.defender.status.vital_throw = 18
            text_surface = tb.build().render()
            events = []
            events.append(gameevent.LogEvent(text_surface))
            events.append(event.SleepEvent(20))
            return events
        return self.get_all_hit_or_miss_events(_vital_throw_effect)
    # Dig
    def move_8(self):
        if self.dungeon.tileset.underwater:
            text_surface = (
                text.TextBuilder()
                    .set_shadow(True)
                    .set_color(text.WHITE)
                    .write(" It can only be used on the ground!")
                    .build()
                    .render()
            )
        else:
            text_surface = (
                text.TextBuilder()
                    .set_shadow(True)
                    .set_color(self.attacker.name_color)
                    .write(self.attacker.name)
                    .set_color(text.WHITE)
                    .write(" burrowed underground!")
                    .build()
                    .render()
            )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatusEvent(self.attacker, "digging", True))
        events.append(event.SleepEvent(20))
        return events
    """
    # Deals damage, no special effects.
    def move_0(self):
        damage = self.calculate_damage()
        return self.get_damage_events(damage)
    # The target's damage doubles if they are Digging.
    def move_3(self):
        multiplier = 1
        if self.defender.status.digging:
            multiplier = 2
        damage = self.calculate_damage() * multiplier
        return self.get_damage_events(damage)
    # The target's damage doubles if they are Flying or are Bouncing.
    def move_4(self):
        multiplier = 1
        if self.defender.status.flying or self.defender.status.bouncing:
            multiplier = 2
        damage = self.calculate_damage() * multiplier
        return self.get_damage_events(damage)
    # Recoil damage: the user loses 1/4 of their maximum HP. Furthermore, PP does not decrement. (This is used by Struggle.)
    def move_5(self):
        res = self.effect_0()
        res += self.get_recoil_events(25)
        return res
    # 10% chance to burn the target.
    def move_6(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_burn_events()
        return res
    def move_7(self):
        return self.effect_6()
    # 10% chance to freeze the target.
    def move_8(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_freeze_events()
        return res
    # This user goes into the resting Paused status after this move's use to recharge, but only if a target is hit.
    def move_9(self):
        self.attacker.status.paused = True
        return self.effect_0()
    # Applies the Focus Energy status to the user, boosting their critical hit rate for 3-4 turns.
    def move_10(self):
        self.attacker.status.focus_energy = True
        return []
    # The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0.
    def move_12(self):  # Used by Fissure.
        if type_chart.get_move_effectiveness(self.current_move.type, self.defender.type) is TypeEffectiveness.LITTLE:
            return self.get_no_damage_events()
        else:
            return self.get_calamitous_damage_events()
    def move_13(self):  # Used by Sheer Cold and Guillotine.
        return self.effect_12()
    # The target has a 10% chance to become constricted (unable to act while suffering several turns of damage).
    def move_15(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_constricted_events()
        return res
    # The target has a 10% chance to become constricted (unable to act while suffering several turns of damage). Damage suffered doubles if the target is Diving.
    def move_16(self):
        return self.effect_15()
    # Damage doubles if the target is diving.
    def move_17(self):
        multiplier = 1
        if self.defender.status.diving:
            multiplier = 2
        damage = self.calculate_damage() * multiplier
        return self.get_damage_events(damage)
    # The target will be unable to move.
    def move_18(self):
        self.defender.status.shadow_hold = True
        return []
    # The target has an 18% chance to become poisoned.
    def move_19(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 18:
            res += self.get_poisoned_events()
        return res
    # This move has a 10% chance to lower the target's Sp. Def. by one stage.
    def move_20(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.defender, "sp_defense", -1)
        return res
    # This move has a 10% chance to lower the target's Defense by one stage.
    def move_21(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.defender, "defense", -1)
        return res
    # This move has a 10% chance to raise the user's Attack by one stage.
    def move_22(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.attacker, "attack", 1)
        return res
    # This move has a 10% chance to raise the user's Defense by one stage.
    def move_23(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.attacker, "defense", 1)
        return res
    # This move has a 10% chance to poison the target.
    def move_24(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_poisoned_events()
        return res
    # The damage dealt is doubled if the target is Flying or Bouncing. This also has a 15% chance to make the target cringe.
    def move_25(self):
        res = self.effect_4()
        if random.randrange(0, 100) < 15:
            res += self.get_cringe_events()
        return res
    # This move has a 10% chance to lower the target's movement speed by one stage.
    def move_26(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.defender, "speed", -1)
        return res
    # This move has a 10% chance to raise the user's Attack, Defense, Sp. Atk., Sp. Def., and movement speed by one stage each.
    def move_27(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.attacker, "attack", 1)
            res += self.get_stat_change_events(self.attacker, "defense", 1)
            res += self.get_stat_change_events(self.attacker, "sp_attack", 1)
            res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
            res += self.get_stat_change_events(self.attacker, "speed", 1)
        return res
    # This move has a 10% chance to confuse the target.
    def move_28(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_confusion_events()
        return res
    # This move has a 50% chance to lower the target's Sp. Atk. by one stage.
    def move_29(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_stat_change_events(self.defender, "sp_attack", -1)
        return res
    # This move has a 50% chance to lower the target's Sp. Def. by one stage.
    def move_30(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_stat_change_events(self.defender, "sp_defense", -1)
        return res
    # This move has a 50% chance to lower the target's Defense by one stage.
    def move_31(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_stat_change_events(self.defender, "defense", -1)
        return res
    # This move has a 40% chance to poison the target.
    def move_32(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 40:
            res += self.get_poisoned_events()
        return res
    # This move has a 50% chance to burn the target.
    def move_33(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_burn_events()
        return res
    # This move has a 10% chance to paralyze the target.
    def move_34(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_paralyze_events()
        return res
    # This move has a 15% chance to paralyze the target.
    def move_35(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 15:
            res += self.get_paralyze_events()
        return res
    # This move has a 10% chance to make the target cringe.
    def move_36(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_cringe_events()
        return res
    # This move has a 20% chance to make the target cringe.
    def move_37(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 20:
            res += self.get_paralyze_events()
        return res
    #This move has a 25% chance to make the target cringe.
    def move_38(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 25:
            res += self.get_paralyze_events()
        return res
    # This move has a 30% chance to make the target cringe.
    def move_39(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 30:
            res += self.get_paralyze_events()
        return res
    # This move has a 40% chance to make the target cringe.
    def move_40(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 40:
            res += self.get_paralyze_events()
        return res
    # This move has a 30% chance to confuse the target.
    def move_41(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 30:
            res += self.get_confusion_events()
        return res
    # This move has a 20% chance to do one of these: burn, freeze, or paralyze the target.
    def move_42(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 20:
            choice = random.randint(0, 2)
            if choice == 0:
                res += self.get_burn_events()
            elif choice == 1:
                res += self.get_freeze_events()
            else:
                res += self.get_paralyze_events()
        return res
    # This move has a 20% chance to raise the user's Attack by one stage.
    def move_43(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 20:
            res += self.get_stat_change_events(self.attacker, "attack", 1)
        return res
    # This move has a 10% chance to burn the target.
    def move_44(self):
        return self.effect_6()
    # The target can become infatuated, provided they are of the opposite gender of the user.
    def move_45(self):
        self.defender.status.infatuated = True
        return []
    # This move paralyzes the target. (Used by Disable.)
    def move_46(self):
        return self.get_paralyze_events()
    # This move has a 35% chance to make the target cringe.
    def move_47(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 35:
            res += self.get_cringe_events()
        return res
    # This move deals fixed damage: 55 HP.
    def move_48(self):
        return self.get_damage_events(55)
    # This move deals fixed damage: 65 HP.
    def move_49(self):
        return self.get_damage_events(65)
    # This move paralyzes the target. (Used by Stun Spore.)
    def move_50(self):
        return self.effect_46()
    # This move has a 10% chance to paralyze the target.
    def move_51(self):
        res = self.effect_0()
        if random.randrange(100) < 10:
            res += self.get_paralyze_events()
        return res
    # This move puts the target to sleep.
    def move_52(self):
        self.defender.status.asleep = True
        return []
    # The target begins to yawn.
    def move_53(self):
        self.defender.status.yawning = True
        return []
    # This move has a 10% chance to paralyze the target.
    def move_54(self):
        res = self.effect_0()
        if random.randrange(100) < 10:
            res += self.get_paralyze_events()
        return res
    # This move prevents the target from moving.
    def move_55(self):
        self.defender.status.shadow_hold = True
        return []
    # The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0. Used by Horn Drill.
    def move_56(self):
        return self.effect_12()
    # This move confuses the target.
    def move_57(self):
        return self.get_confusion_events()
    # This move poisons the target.
    def move_58(self):
        return self.get_poisoned_events()
    # This move paralyzes the target.
    def move_59(self):
        return self.get_paralyze_events()
    # This move paralyzes the target.
    def move_60(self):
        return self.get_paralyze_events()
    # This move deals damage and paralyzes the target.
    def move_61(self):
        res = self.effect_0()
        res += self.get_paralyze_events()
        return res
    # If this move hits, then the user's Attack and Defense are lowered by one stage.
    def move_62(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.attacker, "attack", -1)
        res += self.get_stat_change_events(self.attacker, "defense", -1)
        return res
    # If this move hits, then the target's movement speed is lower by one stage.
    def move_63(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.defender, "speed", -1)
        return res
    # If this move hits, then the target is confused.
    def move_64(self):
        res = self.effect_0()
        res += self.get_confusion_events()
        return res
    # If this move hits, then the target's Sp. Def. is lowered by two stages.
    def move_65(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.defender, "sp_defense", -2)
        return res
    # The target is throw 10 spaces in a random direction or until it hits a wall, losing 5 HP in the latter case. Fails on boss floors with cliffs.
    def move_66(self):
        return []
    # The user's and target's current HP are adjusted to become the average of the two, possibly raising or lowering.
    def move_67(self):
        return []
    # This move raises the user's Sp. Atk. by two stages.
    def move_68(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", 2)
    # This move raises the user's Evasion by one stage,
    def move_69(self):
        return self.get_stat_change_events(self.attacker, "evasion", 1)
    # This move raises the user's Attack and movement speed by one stage each.
    def move_70(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "attack", 1)
        res += self.get_stat_change_events(self.attacker, "speed", 1)
        return res
    # This move raises the user's Attack and Defense by one stage each.
    def move_71(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "attack", 1)
        res += self.get_stat_change_events(self.attacker, "defense", 1)
        return res
    # This move raises the user's Attack by one stage.
    def move_72(self):
        return self.get_stat_change_events(self.attacker, "attack", 1)
    # The user of this move becomes enraged.
    def move_73(self):
        self.attacker.status.enraged = True
        return []
    # This move raises the user's Attack by two stages.
    def move_74(self):
        self.get_stat_change_events(self.attacker, "attack", 2)
    # This move raises the user's Sp. Atk. and Sp. Def. by one stage.
    def move_75(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "sp_attack", 1)
        res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
        return res
    # This move raises the user's Sp. Atk. by one stage.
    def move_76(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", 1)
    # This move raises the user's Sp. Def. by two stages.
    def move_77(self):
        return self.get_stat_change_events(self.attacker, "sp_defense", 1)
    # This move raises the user's Defense by one stage,
    def move_78(self):
        return self.get_stat_change_events(self.attacker, "defense", 1)
    # This move raises the user's Defense by two stages.
    def move_79(self):
        return self.get_stat_change_events(self.attacker, "defense", 2)
    # This move raises the user's Defense and Sp. Def. by one stage.
    def move_80(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "defense", 1)
        res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
        return res
    # This move has a 40% chance to lower the target's accuracy by one stage.
    def move_81(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 40:
            res += self.get_stat_change_events(self.defender, "accuracy", -1)
        return res
    # This move has a 60% chance to lower the target's accuracy by one stage.
    def move_82(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 60:
            res += self.get_stat_change_events(self.defender, "accuracy", -1)
        return res
    # This move has a 60% chance to halve the target's Attack multiplier, with a minimum of 2 / 256.
    def move_83(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 60:
            res += self.get_stat_change_events(self.defender, "attack_divider", 1)
        return res
    # If this move hits the target, the target's Sp. Atk. is reduced by two stages.
    def move_84(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.defender, "sp_attack", -2)
        return res
    # This move lower's the target's movement speed.
    def move_85(self):
        return self.get_stat_change_events(self.defender, "speed", -1)
    # This move lowers the target's Attack by one stage.
    def move_86(self):
        return self.get_stat_change_events(self.defender, "attack", -1)
    # This move lower's the target's Attack by two stages.
    def move_87(self):
        return self.get_stat_change_events(self.defender, "attack", -2)
    # This move reduces the target's Defense multiplier to 1/4 of its current value, but no less than 2 / 256.
    def move_88(self):
        return self.get_stat_change_events(self.defender, "defense_divider", 2)
    # This move reduces the target's HP by an amount equal to the user's level.
    def move_89(self):
        return self.get_damage_events(self.attacker.level)
    # The user will regain HP equal to 50% of the damage dealt.
    def move_90(self):
        damage = self.calculate_damage()
        heal = int(damage * 0.5)
        res = self.get_damage_events(damage)
        res += self.get_heal_events(self.attacker, heal)
        return res
    # The user suffers damage equal to 12.5% of their maximum HP. (Used only for Double-Edge for some reason.)
    def move_91(self):
        res = self.effect_0()
        res += self.get_recoil_events(12.5)
        return res
    # The user suffers damage equal to 12.5% of their maximum HP.
    def move_92(self):
        return self.effect_91()
    # The user will regain HP equal to 50% of the damage dealt. (Used only for Absorb for some reason.)
    def move_93(self):
        return self.effect_90()
    # The target becomes confused but their Attack is boosted by two stages.
    def move_94(self):
        res = self.get_confusion_events()
        res += self.get_stat_change_events(self.defender, "attack", 2)
        return res
    # When used, this move's damage increments with each hit.
    def move_95(self):
        return []
    # The user of this move attacks twice in a row. Each hit has a 20% chance to poison the target (36% chance overall to poison).
    def move_96(self):
        res = []
        for i in range(2):
            res += self.effect_0()
            if random.randrange(0, 100) < 20:
                res += self.get_poisoned_events()
        return res
    # SolarBeam's effect. The user charges up for one turn before attacking, or uses it instantly in Sun. If it is Hailing, Rainy, or Sandstorming, damage is halved (24 power).
    def move_97(self):
        return []
    # Sky Attack's effect. The user charges up for a turn before attacking. Damage is doubled at the end of calculation.
    def move_98(self):
        return []
    # This move lowers the target's movement speed by one stage. (This is simply used for the placeholder move Slow Down, for the generic effect.)
    def move_99(self):
        return self.get_stat_change_events(self.defender, "speed", -1)
    # The user attacks 2-5 turns in a row, becoming confused at the end of it.
    def move_100(self):
        return []
    # The user and target are immobilized for 3 to 5 turns while the target suffers damage from it.
    def move_101(self):
        return []
    # If the target of this move is asleep, they are awakened.
    def move_102(self):
        return []
    # This move has a 30% chance to badly poison the target.
    def move_103(self):
        if random.randrange(0, 100) < 30:
            return self.get_badly_poisoned_events()
        else:
            return []
    # At random, one of the following occur: target recovers 25% HP (20%), target takes 40 damage (40%), target takes 80 damage (30%), or target takes 120 damage (10%).
    def move_104(self):
        choice = random.choices(range(4), [20, 40, 30, 10], k=1)[0]
        if choice == 0:
            return self.get_heal_events(self.defender, self.defender.hp // 4)
        elif choice == 1:
            return self.get_damage_events(40)
        elif choice == 2:
            return self.get_damage_events(80)
        elif choice == 3:
            return self.get_damage_events(120)
    # The user falls under the effects of Reflect.
    def move_105(self):
        self.attacker.status.reflect = True
        return []
    # The floor's weather becomes Sandstorm.
    def move_106(self):
        return []
    # The user's allies gain the Safeguard status.
    def move_107(self):
        self.defender.status.safeguard = True
        return []
    # The Mist status envelopes the user.
    def move_108(self):
        self.attacker.status.mist = True
        return []
    # The user falls under the effects of Light Screen.
    def move_109(self):
        self.attacker.status.light_screen = True
        return []
    # The user attacks five times. If an attack misses, the attack ends. When used the damage increments by a factor of x1.5 with each hit.
    def move_110(self):
        return []
    # Reduces the targets' Attack and Sp. Atk. multipliers to 1/4 of their current value, 2 / 256 at minimum. User is reduced to 1 HP and warps at random. Fails if no target.
    def move_111(self):
        return []
    # The target regains HP equal to 1/4 of their maximum HP.
    def move_112(self):
        return []
    # User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
    def move_113(self):
        return []
    # User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
    def move_114(self):
        return []
    # User falls asleep, recovers their HP, and recovers their status.
    def move_115(self):
        return []
    # The user regains HP equal to 1/2 of their maximum HP.
    def move_116(self):
        return self.get_heal_events(self.attacker, self.attacker.hp // 2)
    # Scans the area.
    def move_117(self):
        return []
    # The user and the target swap hold items. This move fails if the user lacks one or if the target does.
    def move_118(self):
        return []
    # If this move damages the target, the user steals the target's hold item if the user lacks one and the target has one.
    def move_119(self):
        return []
    # If this move damages the target, the user steals the target's hold item if the user lacks one and the target has one.
    def move_120(self):
        return []
    # This move raises the movement speed of all targets.
    def move_121(self):
        return self.get_stat_change_events(self.defender, "speed", 1)
    # The user gains the Counter status.
    def move_122(self):
        return []
    # The user gains the Bide status.
    def move_123(self):
        return []
    # This flag is for the attack released at the end of Bide, reducing the target's HP by two times the damage intake. No valid move used this flag.
    def move_124(self):
        return []
    # Creates a random trap based on the floor.
    def move_125(self):
        return []
    # When attacked while knowing this move and asleep, the user faces their attack and uses a move at random. Ignores Confused/Cowering and links. Overriden by Snore.
    def move_126(self):
        return []
    # If user is a Ghost type: user's HP is halved, and target is cursed. If user isn't a Ghost-type: the user's Attack and Defense are boosted by one stage while speed lowers.
    def move_127(self):
        return []
    # This move has doubled damage. If the move misses, the user receives half of the intended damage, at minimum 1.
    def move_128(self):
        return []
    # This move has doubled damage. If the move hits, the user becomes Paused at the end of the turn.
    def move_129(self):
        return []
    # This move has a variable power and type.
    def move_130(self):
        return []
    # The user charges up for Razor Wind, using it on the next turn. Damage is doubled.
    def move_131(self):
        return []
    # User charges up for a Focus Punch, using it on the next turn. Damage is doubled.
    def move_132(self):
        return []
    # The user gains the Magic Coat status.
    def move_133(self):
        return []
    # The target gains the Nightmare status.
    def move_134(self):
        return []
    # User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
    def move_135(self):
        return []
    # This move deals exactly 35 damage. This move is Vacuum-Cut.
    def move_136(self):
        return []
    # The floor gains the Mud Sport or Water Sport status. The former weakens Electric moves, and the latter weakens Fire.
    def move_137(self):
        if self.current_move.name == "Water Sport":
                self.floor.status.water_sport.value = self.floor.status.water_sport.max_value
        elif self.current_move.name == "Mud Sport":
            self.floor.status.mud_sport.value = self.floor.status.mud_sport.max_value
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.PALE_YELLOW)
            .write(self.current_move.name)
            .set_color(text.WHITE)
            .write(" came into effect!")
            .build()
            .render()
        )
        return [gameevent.LogEvent(text_surface).with_divider()]
    # This move has a 30% chance to lower the target's Defense by one stage.
    def move_138(self):
        if random.randrange(0, 100) < 30:
            return self.get_stat_change_events(self.defender, "defense", -1)
        else:
            return []
    # This move will lower the target's Defense by one stage.
    def move_139(self):
        return self.get_stat_change_events(self.defender, "defense", -1)
    # This move will burn the target.
    def move_140(self):
        return self.get_burn_events()
    # This move gives the target the Ingrain status.
    def move_141(self):
        return []
    # This move deals random damage between 128/256 to 383/256 of the user's Level. (Approximately: 0.5 to 1.5 times the user's Level.) Limited to the range of 1-199.
    def move_142(self):
        return []
    # The target gains the Leech Seed status. Fails on Grass-types.
    def move_143(self):
        return []
    # A Spikes trap appears beneath the user.
    def move_144(self):
        return []
    # All of the target's/targets' status ailments are cured.
    def move_145(self):
        return []
    # All targets have their stat stages and multipliers returned to normal levels. This neither considered a reduction or increment in stats for anything relevant to it.
    def move_146(self):
        return []
    # The user gains the Power Ears status.
    def move_147(self):
        return []
    # The targets are put to sleep.
    def move_148(self):
        return []
    # If the target is paralyzed, the damage from this attack doubles, but the target is cured of their paralysis as well.
    def move_149(self):
        return []
    # This move deals fixed damage (5, 10, 15, 20, 25, 30, 35, or 40, for Magnitudes 4 to 10 respectively). The damage doubles on a target who is Digging.
    def move_150(self):
        return []
    # The user gains the Skull Bash status: their Defense boosts for a turn as they charge for an attack on the next turn. Damage is doubled.
    def move_151(self):
        return []
    # The user gains the Wish status.
    def move_152(self):
        return []
    # The target's Sp. Atk. is raised one stage, but they also become confused.
    def move_153(self):
        res = []
        res += self.get_stat_change_events(self.defender, "sp_attack", 1)
        res += self.get_confusion_events()
        return res
    # This move will lower the target's Accuracy by one stage.
    def move_154(self):
        return self.get_stat_change_events(self.defender, "accuracy", -1)
    # This move will lower the target's Accuracy by one stage.
    def move_155(self):
        return self.effect_154()
    # This move will lower the user's Sp. Atk. by two stages if it hits the target.
    def move_156(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", -2)
    # This move will badly poison the target.
    def move_157(self):
        return self.get_badly_poisoned_events()
    # This move lowers the target's Sp. Def. by three stages.
    def move_158(self):
        return self.get_stat_change_events(self.defender, "sp_defense", -3)
    # This move disables the last move the target used. It is not considered sealed however.
    def move_159(self):
        return []
    # Reduces the target's HP by half, rounded down, but it cannot KO the target.
    def move_160(self):
        return []
    # This move damage the target, but it cannot KO the target. If it would normally KO the target they are left with 1 HP.
    def move_161(self):
        return []
    # This reduces all targets' HP to 1. For each target affected, the user's HP is halved, but cannot go lower than 1.
    def move_162(self):
        return []
    # The target's HP becomes equal to that of the user's, provided the user has lower HP. Ineffective otherwise.
    def move_163(self):
        return []
    # All targets switch position with the user.
    def move_164(self):
        return []
    # The user regains HP equal to half of the damage dealt, rounded down. If the target is not asleep, napping, or having a nightmare, the move fails.
    def move_165(self):
        return []
    # The layout of the map - including stairs, items, and Pokemon - are revealed. Visibility is cleared, though its range limitations remain.
    def move_166(self):
        return []
    # If the floor in front of the user is water or lava, it becomes a normal floor tile.
    def move_167(self):
        return []
    # All targets warp randomly.
    def move_168(self):
        return []
    # All water and lava tiles turn into normal floor tiles.
    def move_169(self):
        return []
    # You become able to see the location of the stairs on the map.
    def move_170(self):
        return []
    # This move removes the effects of Light Screen and Reflect the target.
    def move_171(self):
        return []
    # This move raises the user's Defense by one stage.
    def move_172(self):
        return self.get_stat_change_events(self.attacker, "defense", 1)
    # The user gains the Sure Shot status, assuring that their next move will land.
    def move_173(self):
        return []
    # The user gains the Vital Throw status.
    def move_174(self):
        return []
    # The user begins to Fly, waiting for an attack on the next turn. Damage is doubled.
    def move_175(self):
        return []
    # The user Bounces, and attacks on the next turn. Damage is doubled. This move has a 30% chance to paralyze the target.
    def move_176(self):
        return []
    # The user begins to Dive, waiting for an attack on the next turn. Damage is doubled. Move fails if the user is not on a water tile.
    def move_177(self):
        return []
    # The user begins to Dig, waiting for an attack on the next turn. Damage is doubled. Move fails if the user is not on a land tile.
    def move_178(self):
        return []
    # This move lowers the targets' Evasion by one stage.
    def move_179(self):
        return self.get_stat_change_events(self.defender, "evasion", -1)
    # This move raises the user's Evasion by one stage,
    def move_180(self):
        return self.get_stat_change_events(self.attacker, "evasion", 1)
    # This move forces the target to drop its hold item onto the ground.
    def move_181(self):
        return []
    # This removes all traps in the room, excepting Wonder Tiles. This will not work during boss battles.
    def move_182(self):
        return []
    # This gives the user the Long Toss status.
    def move_183(self):
        return []
    # This gives the user the Pierce status.
    def move_184(self):
        return []
    # This gives the user the Grudge status.
    def move_185(self):
        return []
    # This Petrifies the targets indefinitely until attacked.
    def move_186(self):
        return []
    # This move's use will cause the user to use a move known by a random Pokemon on the floor. If Assist is chosen, this move fails.
    def move_187(self):
        return []
    # This enables the Set Damage status on the target, fixing their damage output.
    def move_188(self):
        return []
    # This will cause the target to Cower.
    def move_189(self):
        return []
    # This move turns the target of it into a decoy.
    def move_190(self):
        return []
    # If this move misses, the user receives half of the damage it would've normally dealt to the target, at minimum 1.
    def move_191(self):
        return []
    # This enables the Protect status on the target.
    def move_192(self):
        return []
    # The target becomes Taunted.
    def move_193(self):
        return []
    # The target's Attack and Defense become lowered by one stage.
    def move_194(self):
        res = []
        res += self.get_stat_change_events(self.defender, "attack", -1)
        res += self.get_stat_change_events(self.defender, "defense", -1)
        return res
    # The damage multiplier depends on user HP. 0-25% is 8x, 25-50% is 4x, 50-75% is 2x, 75-100% is 1x.
    def move_195(self):
        return []
    # This move will cause a small explosion.
    def move_196(self):
        return []
    # This move will cause a huge explosion.
    def move_197(self):
        return []
    # This move causes the user to gain the Charging status.
    def move_198(self):
        return []
    # This move' s damage doubles if the user is Burned, Poisoned, Badly Poisoned, or Paralyzed.
    def move_199(self):
        return []
    # The damage for this move (Low Kick) is dependent on the target's species.
    def move_200(self):
        return []
    # The damage multiplier depends on user HP. 0-25% is 25/256, 25%-50% is 51/256, 50-75% is 128/256, 75-100% is 256/256 (or just x1).
    def move_201(self):
        return []
    # The damage multiplier depends on user HP. 0-25% is 25/256, 25%-50% is 51/256, 50-75% is 128/256, 75-100% is 256/256 (or just x1).
    def move_202(self):
        return []
    # The target of this move obtains the Whiffer status.
    def move_203(self):
        return []
    # This permits the target to sell as traps in the same room. They also will not be triggered.
    def move_204(self):
        return []
    # The user stores power, up to three total times.
    def move_205(self):
        return []
    # The damage of this move is multiplied by the number of times the user had used Stockpile (0, 1, 2, or 3). Only if this move hits does the Stockpile counter zero out.
    def move_206(self):
        return []
    # The user recovers HP based on the number of times they've Stockpiled (0 = 0 HP, 1 = 20 HP, 2 = 40 HP, 3 = 80 HP). The Stockpile counter resets to zero after.
    def move_207(self):
        return []
    # The weather becomes Rain.
    def move_208(self):
        return []
    # The PP of the last move used by the target is set to zero.
    def move_209(self):
        return []
    # The user becomes Invisible.
    def move_210(self):
        return []
    # The user gains the Mirror Coat status.
    def move_211(self):
        return []
    # The targets gain the Perish Song status.
    def move_212(self):
        return []
    # This move removes all traps nearby.
    def move_213(self):
        return []
    # The user gains Destiny Bond status with respect to the target of this move.
    def move_214(self):
        return []
    # The target gains the Encore status, affecting their last move used. Fails if the target is either the team leader or if they haven't used a move on this floor.
    def move_215(self):
        return []
    # If the current weather is not Clear/Cloudy, damage doubles. If Sunny, this move is Fire type; Fog or Rain, Water; Sandstorm, Rock; Hail or Snow, Ice.
    def move_216(self):
        return []
    # The weather becomes Sunny.
    def move_217(self):
        return []
    # If this move defeats the target and doesn't join your team, the target drops money.
    def move_218(self):
        return []
    # One-Room the entirety of the room becomes regular floor tiles and the room a single room. Doesn't work on boss floors.
    def move_219(self):
        return []
    # The user gains the Enduring status.
    def move_220(self):
        return []
    # This move raises the Attack and Sp. Atk. of all targets by one stage, excepting the user of the move.
    def move_221(self):
        res = []
        res += self.get_stat_change_events(self.defender, "attack", 1)
        res += self.get_stat_change_events(self.defender, "sp_attack", 1)
        return res
    # This move raises the user's Attack by 20 stages, but lowers the user's Belly to 1 point. Fails if the user has 1 Belly or less.
    def move_222(self):
        return []
    # This move lowers the targets' Bellies by 10.
    def move_223(self):
        return []
    # This move lowers the target's Attack by two stages.
    def move_224(self):
        return self.get_stat_change_events(self.defender, "attack", -2)
    # This move has a 30% chance to lower the target's movement speed by one stage.
    def move_225(self):
        if random.randrange(0, 100) < 30:
            return self.get_stat_change_events(self.defender, "speed", -1)
        else:
            return []
    # This move will lower the target's movement speed by one stage.
    def move_226(self):
        return self.get_stat_change_events(self.defender, "speed", -1)
    # The wall tile the user is currently facing becomes replaced with a normal floor tile. Does not work on diagonal facings.
    def move_227(self):
        return []
    # The user transforms into a random Pokemon species on the dungeon floor that can appear. Fails if the user already has transformed.
    def move_228(self):
        return []
    # This move changes the weather on the floor to Hail.
    def move_229(self):
        return []
    # This enables the Mobile status on the user.
    def move_230(self):
        return []
    # This move lowers the targets' Evasion stage to 10 if it is any higher than that. Further, Ghost types become able to be hit by Normal and Fighting moves.
    def move_231(self):
        return []
    # The user will move one space in a random direction, neglecting towards a wall. If it lands on a Pokemon, both will lose 5 HP and return to their positions. If it lands on a space it cannot enter normally, it warps. This move's movement will not induce traps to be triggered. Finally, the move can be used even when Hungry.
    def move_232(self):
        return []
    # The user and target swap positions.
    def move_233(self):
        return []
    # The target of the move warps, landing on the stairs, becoming Petrified indefinitely until attacked.
    def move_234(self):
        return []
    # The allies of the user of this move warp, landing on the user.
    def move_235(self):
        return []
    # The move's user gains the Mini Counter status.
    def move_236(self):
        return []
    # This move's target becomes Paused.
    def move_237(self):
        return []
    # The user's allies warp to the user and land on them.
    def move_238(self):
        return []
    # This move has no effect. Associated with the Reviver Orb which was reduced to have no power and dummied out in development.
    def move_239(self):
        return []
    # The team leader and their allies escape from the dungeon, and if used in a linked move - somehow - the moves stop being used.
    def move_240(self):
        return []
    # This move causes special effects depending on the terrain, with 30% probability.
    def move_241(self):
        return []
    # This move will cause a special effect depending on the terrain.
    def move_242(self):
        return []
    # The target of the move transforms into an item. They will not drop any hold items, and the defeater of the Pokemon will not gain any experience.
    def move_243(self):
        return []
    # This move transforms into the last move used by the target of the move permanently.
    def move_244(self):
        return []
    # The user acquires the Mirror Move status.
    def move_245(self):
        return []
    # The user of this move gains the target's Abilities. This will fail if the user were to gain Wonder Guard.
    def move_246(self):
        return []
    # The user and the target of this move will swap their Abilities. If either party has Wonder Guard as an Ability, the move fails.
    def move_247(self):
        return []
    # The user's type changes to that of one of their moves at random, regardless of the move's type. Weather Ball is considered to be Normal. Fails if the user has the Forecast Ability.
    def move_248(self):
        return []
    # All items held by the user and their allies are no longer sticky. For members of rescue teams, this includes all items on their person in the bag.
    def move_249(self):
        return []
    # The target loses HP based on the user's IQ.
    def move_250(self):
        return []
    # The target obtains the Snatch status; to prevent conflicts, all others with the Snatch status at this time will lose it.
    def move_251(self):
        return []
    # The user will change types based on the terrain.
    def move_252(self):
        return []
    # The target loses HP based on the user's IQ.
    def move_253(self):
        return []
    # The user of this move copies the stat changes on the target.
    def move_254(self):
        return []
    # Whenever at an attack hits the user, if this move is known and the user asleep, the user will face the attack and use this move. 30% to cause cringing. Ignores Confusion and Cowering and linked moves.
    def move_255(self):
        return []
    # If this move is used by a member of a rescue team, all items named "Used TM" are restored to their original usable state. Also unstickies them.
    def move_256(self):
        return []
    # The target of this move becomes muzzled.
    def move_257(self):
        return []
    # This move once used will cause the user to follow up with a random second attack.
    def move_258(self):
        return []
    # The targets of this move can identify which Pokemon in the floor are holding items and thus will drop them if defeated (or other applicable instances).
    def move_259(self):
        return []
    # The user gains the Conversion 2 status. Fails of the user has the Forecast ability.
    def move_260(self):
        return []
    # The user of the move moves as far as possible in their direction of facing, stopping at a wall or Pokemon. Fails on floors with cliffs.
    def move_261(self):
        return []
    # All unclaimed items on the floor, excepting those within two tiles of the user, land on the user's position, provided there is space around the user.
    def move_262(self):
        return []
    # The user of this move uses the last move used by the target, excepting Assist, Mimic, Encore, Mirror Move, and Sketch, or if the target is charging for an attack.
    def move_263(self):
        return []
    # The target is thrown onto a random space the target can enter within the room's range from the perspective of the user, and takes a random facing. If a foe is in the room, they are thrown to them instead, and both lose 10 HP.
    def move_264(self):
        return []
    # The target loses HP dependent on their species.
    def move_265(self):
        return []
    # One of an ally's stats is raised by two stages at random.
    def move_266(self):
        all_stats = ["attack", "defense", "sp_attack", "sp_defense", "speed", "evasion", "accuracy"]
        possible_stats = []
        for stat in all_stats:
            stat_obj: pokemondata.Statistic = getattr(self.defender.status, stat)
            if stat_obj.value < stat_obj.max_value:
                possible_stats.append(stat)
        if possible_stats:
            return self.get_stat_change_events(self.defender, random.choice(possible_stats), 2)
        else:
            return []
    # The user obtains the Aqua Ring status.
    def move_267(self):
        return []
    # The damage for this move doubles if the user were attacked on the previous turn.
    def move_268(self):
        return []
    # If the user is under 50% HP, then the damage from this move is doubled.
    def move_269(self):
        return []
    # If the target is holding a Berry or has one in their bag or the like, then the user of this move ingests it and uses its effects.
    def move_270(self):
        return []
    # This move has a 70% chance to raise the user's Sp. Atk. by one stage.
    def move_271(self):
        if random.randrange(0, 100) < 70:
            return self.get_stat_change_events(self.attacker, "sp_attack", 1)
        else:
            return []
    # This move will confuse the target.
    def move_272(self):
        return []
    # If this move hits, the user's Defense and Sp. Def. will be lowered by one stage each.
    def move_273(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "defense", -1)
        res += self.get_stat_change_events(self.attacker, "sp_defense", -1)
        return res
    # This move will deal more damage to foes with higher HP.
    def move_274(self):
        return []
    # This move has a 60% chance to cause the targets to fall asleep.
    def move_275(self):
        return []
    # This move clears the weather for the floor.
    def move_276(self):
        return []
    # This move hits the foe twice.
    def move_277(self):
        return []
    # The target cannot use items, nor will their items bear any effect if held.
    def move_278(self):
        return []
    # This move ignores Protect status.
    def move_279(self):
        return []
    # This move has a 10% to cause the foe to cringe, and a 10% chance to cause a burn.
    def move_280(self):
        res = []
        if random.randrange(0, 100) < 10:
            res += self.get_cringe_events()
        if random.randrange(0, 100) < 10:
            res += self.get_burn_events()
        return res
    # This move throws an item at the target.
    def move_281(self):
        return []
    # This move has a 30% chance to paralyze.
    def move_282(self):
        if random.randrange(0, 100) < 30:
            return self.get_paralyze_events()
        else:
            return []
    # This move grants the Gastro Acid ability to the target, negating their abilities.
    def move_283(self):
        return []
    # This move's damage increments with higher weight on the target.
    def move_284(self):
        return []
    # The floor falls under the Gravity state: Flying Pokemon can be hit by Ground moves, and Levitate is negated.
    def move_285(self):
        return []
    # The foe and the user swap stat changes to their Defense and Sp. Def. stats.
    def move_286(self):
        return []
    # This move has a 30% chance to poison the target.
    def move_287(self):
        if random.randrange(0, 100) < 30:
            return self.get_poisoned_events()
        else:
            return []
    # This move deals double damage to targets with halved movement speed.
    def move_288(self):
        return []
    # After using this move, the user has its movement speed reduced.
    def move_289(self):
        return self.get_stat_change_events(self.attacker, "speed", -1)
    # Grants all enemies in the user's room the Heal Block ailment, preventing healing of HP.
    def move_290(self):
        return []
    # The user recovers 50% of their maximum HP.
    def move_291(self):
        return []
    # The health of all targets and their status ailments are cured. However, the user of this move will also have their HP dropped to just 1.
    def move_292(self):
        return []
    # The user and the target swap stat modifications for their Attack and Defense.
    def move_293(self):
        return []
    # This move has a 10% to cause the foe to cringe, and a 10% chance to cause freezing.
    def move_294(self):
        res = []
        if random.randrange(0, 100) < 10:
            return self.get_cringe_events()
        if random.randrange(0, 100) < 10:
            return self.get_freeze_events()
        return res
    # This move will inflict damage on the target, but only if the user has a move with 0 PP. Damage rises as more moves have 0 PP.
    def move_295(self):
        return []
    # This move has a 30% chance to burn the target.
    def move_296(self):
        if random.randrange(0, 100) < 30:
            return self.get_burn_events()
        else:
            return []
    # This move grants the Lucky Chant status to the targets, preventing critical hits.
    def move_297(self):
        return []
    # This move heals all the HP and PP of the targets and all their ailments as well. However as a cost the user returns to 1 HP.
    def move_298(self):
        return []
    # The user of this move gains the Magnet Rise status, gaining immunity to Ground moves.
    def move_299(self):
        return []
    # The user is granted the Metal Burst status.
    def move_300(self):
        return []
    # If the target has an evasion level above 10 stages, it becomes 10 stages. They are either way granted Miracle Eye status, permitting Psychic moves to hit Dark types.
    def move_301(self):
        return []
    # This move has a 30% chance to lower the target's accuracy.
    def move_302(self):
        if random.randrange(100) < 30:
            return self.get_stat_change_events(self.defender, "accuracy", -1)
        else:
            return []
    # The user's Sp. Atk. is boosted by two stages.
    def move_303(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", 2)
    # This move's damage as well as type will change depending on the Berry the user holds, if any.
    def move_304(self):
        return []
    # The user and the target will swap modifications to their Attack and Sp. Atk. stats.
    def move_305(self):
        return []
    # The user swaps their Attack and Defense stat modifiers.
    def move_306(self):
        return []
    # The user transfers their status problems to the target of this move, while simultaneously curing their own.
    def move_307(self):
        return []
    # This move increments power further if the target has boosted Attack, Defense, Sp. Atk., and/or Sp. Def., and more for every stage boosted.
    def move_308(self):
        return []
    # This move has a 20% chance to confuse the target.
    def move_309(self):
        return []
    # Targets of this move have their movement speed raised by two stages.
    def move_310(self):
        return self.get_stat_change_events(self.defender, "speed", 2)
    # This move's user gains 50% of their maximum HP. In return however, they will lose any Flying-type designations until their next turn.
    def move_311(self):
        return []
    # This move has a 40% chance to lower the targets' Sp. Atk. by two stages.
    def move_312(self):
        if random.randrange(0, 100) < 40:
            return self.get_stat_change_events(self.defender, "sp_attack", -2)
        else:
            return []
    # The user gains the Shadow Force status: they become untouchable for a single turn, attacking on the next turn. This move deals double damage. This move defies Protect status. This move cannot be linked.
    def move_313(self):
        return []
    # The user of the move creates a Stealth Rock trap underneath their feet.
    def move_314(self):
        return []
    # This move has a 10% chance to make the target cringe, and a 10% chance to paralyze them too.
    def move_315(self):
        res = []
        if random.randrange(0, 100) < 10:
            return self.get_cringe_events()
        if random.randrange(0, 100) < 10:
            return self.get_paralyze_events()
        return res
    # This move places a Toxic Spikes trap under the user's feet.
    def move_316(self):
        return []
    # This move at random increases or lowers the movement speed of all targets by one stage.
    def move_317(self):
        return self.get_stat_change_events(self.defender, "speed", random.choice([-1, 1]))
    # This move will deal more damage the lower its current PP.
    def move_318(self):
        return []
    # This move will awaken a target affected by the Napping, Sleep, or Nightmare statuses, but if the target has one of these the move will also do double damage.
    def move_319(self):
        return []
    # This move if it hits will inflict the target with the Sleepless status. It will fail on Pokemon with the Truant Ability.
    def move_320(self):
        return []
    """

