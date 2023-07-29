import math
import random

import pygame
from app.common.inputstream import InputStream
from app.common import settings, text
from app.dungeon.dungeon import Dungeon
from app.dungeon import floorstatus
from app.events import event, gameevent
from app.move import move
from app.pokemon import pokemon, pokemondata
from app.db import move_db, stat_stage_chart, statanimation_db, type_chart
from app.model.type import Type, TypeEffectiveness


class TargetGetter:
    def __init__(self, dungeon: Dungeon):
        self.floor = dungeon.floor
        self.party = dungeon.party
        self.enemies = self.floor.active_enemies
        self.target_getters = {
            move.MoveRange.ADJACENT_POKEMON: self.get_none,
            move.MoveRange.ALL_ENEMIES_IN_THE_ROOM: self.get_all_enemies_in_the_room,
            move.MoveRange.ALL_ENEMIES_ON_THE_FLOOR: self.get_all_enemies_on_the_floor,
            move.MoveRange.ALL_IN_THE_ROOM_EXCEPT_USER: self.get_all_in_the_room_except_user,
            move.MoveRange.ALL_POKEMON_IN_THE_ROOM: self.get_all_pokemon_in_the_room,
            move.MoveRange.ALL_POKEMON_ON_THE_FLOOR: self.get_all_pokemon_on_the_floor,
            move.MoveRange.ALL_TEAM_MEMBERS_IN_THE_ROOM: self.get_all_team_members_in_the_room,
            move.MoveRange.ENEMIES_WITHIN_1_TILE_RANGE: self.get_enemies_within_1_tile_range,
            move.MoveRange.ENEMY_IN_FRONT: self.get_enemy_in_front,
            move.MoveRange.ENEMY_IN_FRONT_CUTS_CORNERS: self.get_enemy_in_front_cuts_corners,
            move.MoveRange.ENEMY_UP_TO_2_TILES_AWAY: self.get_enemy_up_to_2_tiles_away,
            move.MoveRange.FACING_POKEMON: self.get_facing_pokemon,
            move.MoveRange.FACING_POKEMON_CUTS_CORNERS: self.get_facing_pokemon_cuts_corners,
            move.MoveRange.FACING_TILE_AND_2_FLANKING_TILES: self.get_facing_tile_and_2_flanking_tiles,
            move.MoveRange.FLOOR: self.get_none,
            move.MoveRange.ITEM: self.get_none,
            move.MoveRange.LINE_OF_SIGHT: self.get_line_of_sight,
            move.MoveRange.ONLY_THE_ALLIES_IN_THE_ROOM: self.get_only_the_allies_in_the_room,
            move.MoveRange.POKEMON_WITHIN_1_TILE_RANGE: self.get_pokemon_within_1_tile_range,
            move.MoveRange.POKEMON_WITHIN_2_TILE_RANGE: self.get_pokemon_within_2_tile_range,
            move.MoveRange.SPECIAL: self.get_none,
            move.MoveRange.TEAM_MEMBERS_ON_THE_FLOOR: self.get_team_members_on_the_floor,
            move.MoveRange.USER: self.get_user,
            move.MoveRange.WALL: self.get_none
        }
    
    def __getitem__(self, move_range: move.MoveRange):
        return self.target_getters[move_range]

    def activate(self, pokemon: pokemon.Pokemon):
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
        return [p for p in self.floor.spawned if p is not self.attacker]
    
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


class BattleSystem:
    def __init__(self, dungeon: Dungeon):
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log
        self.current_move = None
        self.is_active = False
        self.attacker = None
        self.defender = None
        self.targets: list[pokemon.Pokemon] = []
        self.current_move = None
        self.events: list[event.Event] = []
        self.event_index = 0
        self.target_getter = TargetGetter(dungeon)

        self.dispatcher = {i: getattr(self, f"effect_{i}", self.effect_0) for i in range(321)}

    @property
    def is_waiting(self) -> bool:
        return not self.is_active and self.attacker is not None

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
        self.target_getter.activate(self.attacker)
        if move_index == -1 or self.attacker.moveset.can_use(move_index):
            self.activate(move_index)
        else:
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
        self.target_getter.activate(p)
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
        if not any(self.target_getter[move.MoveRange.ALL_ENEMIES_IN_THE_ROOM]()):
            return False
        self.targets = self.get_targets()
        if not self.targets:
            return False
        return True

    # ACTIVATION
    def activate(self, move_index: int) -> bool:
        self.target_getter.activate(self.attacker)
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
        self.target_getter.deactivate()
        self.events.clear()
        self.attacker = None
        self.defender = None
        self.targets.clear()
        self.current_move = None
        self.event_index = 0
        self.is_active = False

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
            .write(" failed.")
            .build()
            .render()
        )
        return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]

    def get_events_from_move(self):
        effect = self.current_move.effect
        res = []
        self.targets = self.get_targets()
        if self.current_move.move_range is move.MoveRange.FLOOR:
            res += self.get_events_from_effect(effect)
        else:
            for target in self.targets:
                self.defender = target
                if self.miss():
                    res += self.get_miss_events()
                    continue
                res += self.get_events_from_effect(effect)
        return res

    # Move effect events
    def get_events_from_effect(self, effect: int):
        return self.dispatcher.get(effect, self.dispatcher[0])()
    
    # Deals damage, no special effects.
    def effect_0(self):
        damage = self.calculate_damage()
        return self.get_damage_events(damage)
    # The target's damage doubles if they are Digging.
    def effect_3(self):
        multiplier = 1
        if self.defender.status.digging:
            multiplier = 2
        damage = self.calculate_damage() * multiplier
        return self.get_damage_events(damage)
    # The target's damage doubles if they are Flying or are Bouncing.
    def effect_4(self):
        multiplier = 1
        if self.defender.status.flying or self.defender.status.bouncing:
            multiplier = 2
        damage = self.calculate_damage() * multiplier
        return self.get_damage_events(damage)
    # Recoil damage: the user loses 1/4 of their maximum HP. Furthermore, PP does not decrement. (This is used by Struggle.)
    def effect_5(self):
        res = self.effect_0()
        res += self.get_recoil_events(25)
        return res
    # 10% chance to burn the target.
    def effect_6(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_burn_events()
        return res
    def effect_7(self):
        return self.effect_6()
    # 10% chance to freeze the target.
    def effect_8(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_freeze_events()
        return res
    # This user goes into the resting Paused status after this move's use to recharge, but only if a target is hit.
    def effect_9(self):
        self.attacker.status.paused = True
        return self.effect_0()
    # Applies the Focus Energy status to the user, boosting their critical hit rate for 3-4 turns.
    def effect_10(self):
        self.attacker.status.focus_energy = True
        return []
    # The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0.
    def effect_12(self):  # Used by Fissure.
        if type_chart.get_move_effectiveness(self.current_move.type, self.defender.type) is TypeEffectiveness.LITTLE:
            return self.get_no_damage_events()
        else:
            return self.get_calamitous_damage_events()
    def effect_13(self):  # Used by Sheer Cold and Guillotine.
        return self.effect_12()
    # The target has a 10% chance to become constricted (unable to act while suffering several turns of damage).
    def effect_15(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_constricted_events()
        return res
    # The target has a 10% chance to become constricted (unable to act while suffering several turns of damage). Damage suffered doubles if the target is Diving.
    def effect_16(self):
        return self.effect_15()
    # Damage doubles if the target is diving.
    def effect_17(self):
        multiplier = 1
        if self.defender.status.diving:
            multiplier = 2
        damage = self.calculate_damage() * multiplier
        return self.get_damage_events(damage)
    # The target will be unable to move.
    def effect_18(self):
        self.defender.status.shadow_hold = True
        return []
    # The target has an 18% chance to become poisoned.
    def effect_19(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 18:
            res += self.get_poisoned_events()
        return res
    # This move has a 10% chance to lower the target's Sp. Def. by one stage.
    def effect_20(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.defender, "sp_defense", -1)
        return res
    # This move has a 10% chance to lower the target's Defense by one stage.
    def effect_21(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.defender, "defense", -1)
        return res
    # This move has a 10% chance to raise the user's Attack by one stage.
    def effect_22(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.attacker, "attack", 1)
        return res
    # This move has a 10% chance to raise the user's Defense by one stage.
    def effect_23(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.attacker, "defense", 1)
        return res
    # This move has a 10% chance to poison the target.
    def effect_24(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_poisoned_events()
        return res
    # The damage dealt is doubled if the target is Flying or Bouncing. This also has a 15% chance to make the target cringe.
    def effect_25(self):
        res = self.effect_4()
        if random.randrange(0, 100) < 15:
            res += self.get_cringe_events()
        return res
    # This move has a 10% chance to lower the target's movement speed by one stage.
    def effect_26(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.defender, "speed", -1)
        return res
    # This move has a 10% chance to raise the user's Attack, Defense, Sp. Atk., Sp. Def., and movement speed by one stage each.
    def effect_27(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_stat_change_events(self.attacker, "attack", 1)
            res += self.get_stat_change_events(self.attacker, "defense", 1)
            res += self.get_stat_change_events(self.attacker, "sp_attack", 1)
            res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
            res += self.get_stat_change_events(self.attacker, "speed", 1)
        return res
    # This move has a 10% chance to confuse the target.
    def effect_28(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_confusion_events()
        return res
    # This move has a 50% chance to lower the target's Sp. Atk. by one stage.
    def effect_29(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_stat_change_events(self.defender, "sp_attack", -1)
        return res
    # This move has a 50% chance to lower the target's Sp. Def. by one stage.
    def effect_30(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_stat_change_events(self.defender, "sp_defense", -1)
        return res
    # This move has a 50% chance to lower the target's Defense by one stage.
    def effect_31(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_stat_change_events(self.defender, "defense", -1)
        return res
    # This move has a 40% chance to poison the target.
    def effect_32(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 40:
            res += self.get_poisoned_events()
        return res
    # This move has a 50% chance to burn the target.
    def effect_33(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 50:
            res += self.get_burn_events()
        return res
    # This move has a 10% chance to paralyze the target.
    def effect_34(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_paralyze_events()
        return res
    # This move has a 15% chance to paralyze the target.
    def effect_35(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 15:
            res += self.get_paralyze_events()
        return res
    # This move has a 10% chance to make the target cringe.
    def effect_36(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 10:
            res += self.get_cringe_events()
        return res
    # This move has a 20% chance to make the target cringe.
    def effect_37(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 20:
            res += self.get_paralyze_events()
        return res
    #This move has a 25% chance to make the target cringe.
    def effect_38(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 25:
            res += self.get_paralyze_events()
        return res
    # This move has a 30% chance to make the target cringe.
    def effect_39(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 30:
            res += self.get_paralyze_events()
        return res
    # This move has a 40% chance to make the target cringe.
    def effect_40(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 40:
            res += self.get_paralyze_events()
        return res
    # This move has a 30% chance to confuse the target.
    def effect_41(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 30:
            res += self.get_confusion_events()
        return res
    # This move has a 20% chance to do one of these: burn, freeze, or paralyze the target.
    def effect_42(self):
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
    def effect_43(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 20:
            res += self.get_stat_change_events(self.attacker, "attack", 1)
        return res
    # This move has a 10% chance to burn the target.
    def effect_44(self):
        return self.effect_6()
    # The target can become infatuated, provided they are of the opposite gender of the user.
    def effect_45(self):
        self.defender.status.infatuated = True
        return []
    # This move paralyzes the target. (Used by Disable.)
    def effect_46(self):
        return self.get_paralyze_events()
    # This move has a 35% chance to make the target cringe.
    def effect_47(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 35:
            res += self.get_cringe_events()
        return res
    # This move deals fixed damage: 55 HP.
    def effect_48(self):
        return self.get_damage_events(55)
    # This move deals fixed damage: 65 HP.
    def effect_49(self):
        return self.get_damage_events(65)
    # This move paralyzes the target. (Used by Stun Spore.)
    def effect_50(self):
        return self.effect_46()
    # This move has a 10% chance to paralyze the target.
    def effect_51(self):
        res = self.effect_0()
        if random.randrange(100) < 10:
            res += self.get_paralyze_events()
        return res
    # This move puts the target to sleep.
    def effect_52(self):
        self.defender.status.asleep = True
        return []
    # The target begins to yawn.
    def effect_53(self):
        self.defender.status.yawning = True
        return []
    # This move has a 10% chance to paralyze the target.
    def effect_54(self):
        res = self.effect_0()
        if random.randrange(100) < 10:
            res += self.get_paralyze_events()
        return res
    # This move prevents the target from moving.
    def effect_55(self):
        self.defender.status.shadow_hold = True
        return []
    # The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0. Used by Horn Drill.
    def effect_56(self):
        return self.effect_12()
    # This move confuses the target.
    def effect_57(self):
        return self.get_confusion_events()
    # This move poisons the target.
    def effect_58(self):
        return self.get_poisoned_events()
    # This move paralyzes the target.
    def effect_59(self):
        return self.get_paralyze_events()
    # This move paralyzes the target.
    def effect_60(self):
        return self.get_paralyze_events()
    # This move deals damage and paralyzes the target.
    def effect_61(self):
        res = self.effect_0()
        res += self.get_paralyze_events()
        return res
    # If this move hits, then the user's Attack and Defense are lowered by one stage.
    def effect_62(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.attacker, "attack", -1)
        res += self.get_stat_change_events(self.attacker, "defense", -1)
        return res
    # If this move hits, then the target's movement speed is lower by one stage.
    def effect_63(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.defender, "speed", -1)
        return res
    # If this move hits, then the target is confused.
    def effect_64(self):
        res = self.effect_0()
        res += self.get_confusion_events()
        return res
    # If this move hits, then the target's Sp. Def. is lowered by two stages.
    def effect_65(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.defender, "sp_defense", -2)
        return res
    # The target is throw 10 spaces in a random direction or until it hits a wall, losing 5 HP in the latter case. Fails on boss floors with cliffs.
    def effect_66(self):
        return []
    # The user's and target's current HP are adjusted to become the average of the two, possibly raising or lowering.
    def effect_67(self):
        return []
    # This move raises the user's Sp. Atk. by two stages.
    def effect_68(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", 2)
    # This move raises the user's Evasion by one stage,
    def effect_69(self):
        return self.get_stat_change_events(self.attacker, "evasion", 1)
    # This move raises the user's Attack and movement speed by one stage each.
    def effect_70(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "attack", 1)
        res += self.get_stat_change_events(self.attacker, "speed", 1)
        return res
    # This move raises the user's Attack and Defense by one stage each.
    def effect_71(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "attack", 1)
        res += self.get_stat_change_events(self.attacker, "defense", 1)
        return res
    # This move raises the user's Attack by one stage.
    def effect_72(self):
        return self.get_stat_change_events(self.attacker, "attack", 1)
    # The user of this move becomes enraged.
    def effect_73(self):
        self.attacker.status.enraged = True
        return []
    # This move raises the user's Attack by two stages.
    def effect_74(self):
        self.get_stat_change_events(self.attacker, "attack", 2)
    # This move raises the user's Sp. Atk. and Sp. Def. by one stage.
    def effect_75(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "sp_attack", 1)
        res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
        return res
    # This move raises the user's Sp. Atk. by one stage.
    def effect_76(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", 1)
    # This move raises the user's Sp. Def. by two stages.
    def effect_77(self):
        return self.get_stat_change_events(self.attacker, "sp_defense", 1)
    # This move raises the user's Defense by one stage,
    def effect_78(self):
        return self.get_stat_change_events(self.attacker, "defense", 1)
    # This move raises the user's Defense by two stages.
    def effect_79(self):
        return self.get_stat_change_events(self.attacker, "defense", 2)
    # This move raises the user's Defense and Sp. Def. by one stage.
    def effect_80(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "defense", 1)
        res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
        return res
    # This move has a 40% chance to lower the target's accuracy by one stage.
    def effect_81(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 40:
            res += self.get_stat_change_events(self.defender, "accuracy", -1)
        return res
    # This move has a 60% chance to lower the target's accuracy by one stage.
    def effect_82(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 60:
            res += self.get_stat_change_events(self.defender, "accuracy", -1)
        return res
    # This move has a 60% chance to halve the target's Attack multiplier, with a minimum of 2 / 256.
    def effect_83(self):
        res = self.effect_0()
        if random.randrange(0, 100) < 60:
            res += self.get_stat_change_events(self.defender, "attack_divider", 1)
        return res
    # If this move hits the target, the target's Sp. Atk. is reduced by two stages.
    def effect_84(self):
        res = self.effect_0()
        res += self.get_stat_change_events(self.defender, "sp_attack", -2)
        return res
    # This move lower's the target's movement speed.
    def effect_85(self):
        return self.get_stat_change_events(self.defender, "speed", -1)
    # This move lowers the target's Attack by one stage.
    def effect_86(self):
        return self.get_stat_change_events(self.defender, "attack", -1)
    # This move lower's the target's Attack by two stages.
    def effect_87(self):
        return self.get_stat_change_events(self.defender, "attack", -2)
    # This move reduces the target's Defense multiplier to 1/4 of its current value, but no less than 2 / 256.
    def effect_88(self):
        return self.get_stat_change_events(self.defender, "defense_divider", 2)
    # This move reduces the target's HP by an amount equal to the user's level.
    def effect_89(self):
        return self.get_damage_events(self.attacker.level)
    # The user will regain HP equal to 50% of the damage dealt.
    def effect_90(self):
        damage = self.calculate_damage()
        heal = int(damage * 0.5)
        res = self.get_damage_events(damage)
        res += self.get_heal_events(self.attacker, heal)
        return res
    # The user suffers damage equal to 12.5% of their maximum HP. (Used only for Double-Edge for some reason.)
    def effect_91(self):
        res = self.effect_0()
        res += self.get_recoil_events(12.5)
        return res
    # The user suffers damage equal to 12.5% of their maximum HP.
    def effect_92(self):
        return self.effect_91()
    # The user will regain HP equal to 50% of the damage dealt. (Used only for Absorb for some reason.)
    def effect_93(self):
        return self.effect_90()
    # The target becomes confused but their Attack is boosted by two stages.
    def effect_94(self):
        res = self.get_confusion_events()
        res += self.get_stat_change_events(self.defender, "attack", 2)
        return res
    # When used, this move's damage increments with each hit.
    def effect_95(self):
        return []
    # The user of this move attacks twice in a row. Each hit has a 20% chance to poison the target (36% chance overall to poison).
    def effect_96(self):
        res = []
        for i in range(2):
            res += self.effect_0()
            if random.randrange(0, 100) < 20:
                res += self.get_poisoned_events()
        return res
    # SolarBeam's effect. The user charges up for one turn before attacking, or uses it instantly in Sun. If it is Hailing, Rainy, or Sandstorming, damage is halved (24 power).
    def effect_97(self):
        return []
    # Sky Attack's effect. The user charges up for a turn before attacking. Damage is doubled at the end of calculation.
    def effect_98(self):
        return []
    # This move lowers the target's movement speed by one stage. (This is simply used for the placeholder move Slow Down, for the generic effect.)
    def effect_99(self):
        return self.get_stat_change_events(self.defender, "speed", -1)
    # The user attacks 2-5 turns in a row, becoming confused at the end of it.
    def effect_100(self):
        return []
    # The user and target are immobilized for 3 to 5 turns while the target suffers damage from it.
    def effect_101(self):
        return []
    # If the target of this move is asleep, they are awakened.
    def effect_102(self):
        return []
    # This move has a 30% chance to badly poison the target.
    def effect_103(self):
        if random.randrange(0, 100) < 30:
            return self.get_badly_poisoned_events()
        else:
            return []
    # At random, one of the following occur: target recovers 25% HP (20%), target takes 40 damage (40%), target takes 80 damage (30%), or target takes 120 damage (10%).
    def effect_104(self):
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
    def effect_105(self):
        self.attacker.status.reflect = True
        return []
    # The floor's weather becomes Sandstorm.
    def effect_106(self):
        return []
    # The user's allies gain the Safeguard status.
    def effect_107(self):
        self.defender.status.safeguard = True
        return []
    # The Mist status envelopes the user.
    def effect_108(self):
        self.attacker.status.mist = True
        return []
    # The user falls under the effects of Light Screen.
    def effect_109(self):
        self.attacker.status.light_screen = True
        return []
    # The user attacks five times. If an attack misses, the attack ends. When used the damage increments by a factor of x1.5 with each hit.
    def effect_110(self):
        return []
    # Reduces the targets' Attack and Sp. Atk. multipliers to 1/4 of their current value, 2 / 256 at minimum. User is reduced to 1 HP and warps at random. Fails if no target.
    def effect_111(self):
        return []
    # The target regains HP equal to 1/4 of their maximum HP.
    def effect_112(self):
        return []
    # User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
    def effect_113(self):
        return []
    # User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
    def effect_114(self):
        return []
    # User falls asleep, recovers their HP, and recovers their status.
    def effect_115(self):
        return []
    # The user regains HP equal to 1/2 of their maximum HP.
    def effect_116(self):
        return self.get_heal_events(self.attacker, self.attacker.hp // 2)
    # Scans the area.
    def effect_117(self):
        return []
    # The user and the target swap hold items. This move fails if the user lacks one or if the target does.
    def effect_118(self):
        return []
    # If this move damages the target, the user steals the target's hold item if the user lacks one and the target has one.
    def effect_119(self):
        return []
    # If this move damages the target, the user steals the target's hold item if the user lacks one and the target has one.
    def effect_120(self):
        return []
    # This move raises the movement speed of all targets.
    def effect_121(self):
        return self.get_stat_change_events(self.defender, "speed", 1)
    # The user gains the Counter status.
    def effect_122(self):
        return []
    # The user gains the Bide status.
    def effect_123(self):
        return []
    # This flag is for the attack released at the end of Bide, reducing the target's HP by two times the damage intake. No valid move used this flag.
    def effect_124(self):
        return []
    # Creates a random trap based on the floor.
    def effect_125(self):
        return []
    # When attacked while knowing this move and asleep, the user faces their attack and uses a move at random. Ignores Confused/Cowering and links. Overriden by Snore.
    def effect_126(self):
        return []
    # If user is a Ghost type: user's HP is halved, and target is cursed. If user isn't a Ghost-type: the user's Attack and Defense are boosted by one stage while speed lowers.
    def effect_127(self):
        return []
    # This move has doubled damage. If the move misses, the user receives half of the intended damage, at minimum 1.
    def effect_128(self):
        return []
    # This move has doubled damage. If the move hits, the user becomes Paused at the end of the turn.
    def effect_129(self):
        return []
    # This move has a variable power and type.
    def effect_130(self):
        return []
    # The user charges up for Razor Wind, using it on the next turn. Damage is doubled.
    def effect_131(self):
        return []
    # User charges up for a Focus Punch, using it on the next turn. Damage is doubled.
    def effect_132(self):
        return []
    # The user gains the Magic Coat status.
    def effect_133(self):
        return []
    # The target gains the Nightmare status.
    def effect_134(self):
        return []
    # User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
    def effect_135(self):
        return []
    # This move deals exactly 35 damage. This move is Vacuum-Cut.
    def effect_136(self):
        return []
    # The floor gains the Mud Sport or Water Sport status. The former weakens Electric moves, and the latter weakens Fire.
    def effect_137(self):
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
    def effect_138(self):
        if random.randrange(0, 100) < 30:
            return self.get_stat_change_events(self.defender, "defense", -1)
        else:
            return []
    # This move will lower the target's Defense by one stage.
    def effect_139(self):
        return self.get_stat_change_events(self.defender, "defense", -1)
    # This move will burn the target.
    def effect_140(self):
        return self.get_burn_events()
    # This move gives the target the Ingrain status.
    def effect_141(self):
        return []
    # This move deals random damage between 128/256 to 383/256 of the user's Level. (Approximately: 0.5 to 1.5 times the user's Level.) Limited to the range of 1-199.
    def effect_142(self):
        return []
    # The target gains the Leech Seed status. Fails on Grass-types.
    def effect_143(self):
        return []
    # A Spikes trap appears beneath the user.
    def effect_144(self):
        return []
    # All of the target's/targets' status ailments are cured.
    def effect_145(self):
        return []
    # All targets have their stat stages and multipliers returned to normal levels. This neither considered a reduction or increment in stats for anything relevant to it.
    def effect_146(self):
        return []
    # The user gains the Power Ears status.
    def effect_147(self):
        return []
    # The targets are put to sleep.
    def effect_148(self):
        return []
    # If the target is paralyzed, the damage from this attack doubles, but the target is cured of their paralysis as well.
    def effect_149(self):
        return []
    # This move deals fixed damage (5, 10, 15, 20, 25, 30, 35, or 40, for Magnitudes 4 to 10 respectively). The damage doubles on a target who is Digging.
    def effect_150(self):
        return []
    # The user gains the Skull Bash status: their Defense boosts for a turn as they charge for an attack on the next turn. Damage is doubled.
    def effect_151(self):
        return []
    # The user gains the Wish status.
    def effect_152(self):
        return []
    # The target's Sp. Atk. is raised one stage, but they also become confused.
    def effect_153(self):
        res = []
        res += self.get_stat_change_events(self.defender, "sp_attack", 1)
        res += self.get_confusion_events()
        return res
    # This move will lower the target's Accuracy by one stage.
    def effect_154(self):
        return self.get_stat_change_events(self.defender, "accuracy", -1)
    # This move will lower the target's Accuracy by one stage.
    def effect_155(self):
        return self.effect_154()
    # This move will lower the user's Sp. Atk. by two stages if it hits the target.
    def effect_156(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", -2)
    # This move will badly poison the target.
    def effect_157(self):
        return self.get_badly_poisoned_events()
    # This move lowers the target's Sp. Def. by three stages.
    def effect_158(self):
        return self.get_stat_change_events(self.defender, "sp_defense", -3)
    # This move disables the last move the target used. It is not considered sealed however.
    def effect_159(self):
        return []
    # Reduces the target's HP by half, rounded down, but it cannot KO the target.
    def effect_160(self):
        return []
    # This move damage the target, but it cannot KO the target. If it would normally KO the target they are left with 1 HP.
    def effect_161(self):
        return []
    # This reduces all targets' HP to 1. For each target affected, the user's HP is halved, but cannot go lower than 1.
    def effect_162(self):
        return []
    # The target's HP becomes equal to that of the user's, provided the user has lower HP. Ineffective otherwise.
    def effect_163(self):
        return []
    # All targets switch position with the user.
    def effect_164(self):
        return []
    # The user regains HP equal to half of the damage dealt, rounded down. If the target is not asleep, napping, or having a nightmare, the move fails.
    def effect_165(self):
        return []
    # The layout of the map - including stairs, items, and Pokemon - are revealed. Visibility is cleared, though its range limitations remain.
    def effect_166(self):
        return []
    # If the floor in front of the user is water or lava, it becomes a normal floor tile.
    def effect_167(self):
        return []
    # All targets warp randomly.
    def effect_168(self):
        return []
    # All water and lava tiles turn into normal floor tiles.
    def effect_169(self):
        return []
    # You become able to see the location of the stairs on the map.
    def effect_170(self):
        return []
    # This move removes the effects of Light Screen and Reflect the target.
    def effect_171(self):
        return []
    # This move raises the user's Defense by one stage.
    def effect_172(self):
        return self.get_stat_change_events(self.attacker, "defense", 1)
    # The user gains the Sure Shot status, assuring that their next move will land.
    def effect_173(self):
        return []
    # The user gains the Vital Throw status.
    def effect_174(self):
        return []
    # The user begins to Fly, waiting for an attack on the next turn. Damage is doubled.
    def effect_175(self):
        return []
    # The user Bounces, and attacks on the next turn. Damage is doubled. This move has a 30% chance to paralyze the target.
    def effect_176(self):
        return []
    # The user begins to Dive, waiting for an attack on the next turn. Damage is doubled. Move fails if the user is not on a water tile.
    def effect_177(self):
        return []
    # The user begins to Dig, waiting for an attack on the next turn. Damage is doubled. Move fails if the user is not on a land tile.
    def effect_178(self):
        return []
    # This move lowers the targets' Evasion by one stage.
    def effect_179(self):
        return self.get_stat_change_events(self.defender, "evasion", -1)
    # This move raises the user's Evasion by one stage,
    def effect_180(self):
        return self.get_stat_change_events(self.attacker, "evasion", 1)
    # This move forces the target to drop its hold item onto the ground.
    def effect_181(self):
        return []
    # This removes all traps in the room, excepting Wonder Tiles. This will not work during boss battles.
    def effect_182(self):
        return []
    # This gives the user the Long Toss status.
    def effect_183(self):
        return []
    # This gives the user the Pierce status.
    def effect_184(self):
        return []
    # This gives the user the Grudge status.
    def effect_185(self):
        return []
    # This Petrifies the targets indefinitely until attacked.
    def effect_186(self):
        return []
    # This move's use will cause the user to use a move known by a random Pokemon on the floor. If Assist is chosen, this move fails.
    def effect_187(self):
        return []
    # This enables the Set Damage status on the target, fixing their damage output.
    def effect_188(self):
        return []
    # This will cause the target to Cower.
    def effect_189(self):
        return []
    # This move turns the target of it into a decoy.
    def effect_190(self):
        return []
    # If this move misses, the user receives half of the damage it would've normally dealt to the target, at minimum 1.
    def effect_191(self):
        return []
    # This enables the Protect status on the target.
    def effect_192(self):
        return []
    # The target becomes Taunted.
    def effect_193(self):
        return []
    # The target's Attack and Defense become lowered by one stage.
    def effect_194(self):
        res = []
        res += self.get_stat_change_events(self.defender, "attack", -1)
        res += self.get_stat_change_events(self.defender, "defense", -1)
        return res
    # The damage multiplier depends on user HP. 0-25% is 8x, 25-50% is 4x, 50-75% is 2x, 75-100% is 1x.
    def effect_195(self):
        return []
    # This move will cause a small explosion.
    def effect_196(self):
        return []
    # This move will cause a huge explosion.
    def effect_197(self):
        return []
    # This move causes the user to gain the Charging status.
    def effect_198(self):
        return []
    # This move' s damage doubles if the user is Burned, Poisoned, Badly Poisoned, or Paralyzed.
    def effect_199(self):
        return []
    # The damage for this move (Low Kick) is dependent on the target's species.
    def effect_200(self):
        return []
    # The damage multiplier depends on user HP. 0-25% is 25/256, 25%-50% is 51/256, 50-75% is 128/256, 75-100% is 256/256 (or just x1).
    def effect_201(self):
        return []
    # The damage multiplier depends on user HP. 0-25% is 25/256, 25%-50% is 51/256, 50-75% is 128/256, 75-100% is 256/256 (or just x1).
    def effect_202(self):
        return []
    # The target of this move obtains the Whiffer status.
    def effect_203(self):
        return []
    # This permits the target to sell as traps in the same room. They also will not be triggered.
    def effect_204(self):
        return []
    # The user stores power, up to three total times.
    def effect_205(self):
        return []
    # The damage of this move is multiplied by the number of times the user had used Stockpile (0, 1, 2, or 3). Only if this move hits does the Stockpile counter zero out.
    def effect_206(self):
        return []
    # The user recovers HP based on the number of times they've Stockpiled (0 = 0 HP, 1 = 20 HP, 2 = 40 HP, 3 = 80 HP). The Stockpile counter resets to zero after.
    def effect_207(self):
        return []
    # The weather becomes Rain.
    def effect_208(self):
        return []
    # The PP of the last move used by the target is set to zero.
    def effect_209(self):
        return []
    # The user becomes Invisible.
    def effect_210(self):
        return []
    # The user gains the Mirror Coat status.
    def effect_211(self):
        return []
    # The targets gain the Perish Song status.
    def effect_212(self):
        return []
    # This move removes all traps nearby.
    def effect_213(self):
        return []
    # The user gains Destiny Bond status with respect to the target of this move.
    def effect_214(self):
        return []
    # The target gains the Encore status, affecting their last move used. Fails if the target is either the team leader or if they haven't used a move on this floor.
    def effect_215(self):
        return []
    # If the current weather is not Clear/Cloudy, damage doubles. If Sunny, this move is Fire type; Fog or Rain, Water; Sandstorm, Rock; Hail or Snow, Ice.
    def effect_216(self):
        return []
    # The weather becomes Sunny.
    def effect_217(self):
        return []
    # If this move defeats the target and doesn't join your team, the target drops money.
    def effect_218(self):
        return []
    # One-Room the entirety of the room becomes regular floor tiles and the room a single room. Doesn't work on boss floors.
    def effect_219(self):
        return []
    # The user gains the Enduring status.
    def effect_220(self):
        return []
    # This move raises the Attack and Sp. Atk. of all targets by one stage, excepting the user of the move.
    def effect_221(self):
        res = []
        res += self.get_stat_change_events(self.defender, "attack", 1)
        res += self.get_stat_change_events(self.defender, "sp_attack", 1)
        return res
    # This move raises the user's Attack by 20 stages, but lowers the user's Belly to 1 point. Fails if the user has 1 Belly or less.
    def effect_222(self):
        return []
    # This move lowers the targets' Bellies by 10.
    def effect_223(self):
        return []
    # This move lowers the target's Attack by two stages.
    def effect_224(self):
        return self.get_stat_change_events(self.defender, "attack", -2)
    # This move has a 30% chance to lower the target's movement speed by one stage.
    def effect_225(self):
        if random.randrange(0, 100) < 30:
            return self.get_stat_change_events(self.defender, "speed", -1)
        else:
            return []
    # This move will lower the target's movement speed by one stage.
    def effect_226(self):
        return self.get_stat_change_events(self.defender, "speed", -1)
    # The wall tile the user is currently facing becomes replaced with a normal floor tile. Does not work on diagonal facings.
    def effect_227(self):
        return []
    # The user transforms into a random Pokemon species on the dungeon floor that can appear. Fails if the user already has transformed.
    def effect_228(self):
        return []
    # This move changes the weather on the floor to Hail.
    def effect_229(self):
        return []
    # This enables the Mobile status on the user.
    def effect_230(self):
        return []
    # This move lowers the targets' Evasion stage to 10 if it is any higher than that. Further, Ghost types become able to be hit by Normal and Fighting moves.
    def effect_231(self):
        return []
    # The user will move one space in a random direction, neglecting towards a wall. If it lands on a Pokemon, both will lose 5 HP and return to their positions. If it lands on a space it cannot enter normally, it warps. This move's movement will not induce traps to be triggered. Finally, the move can be used even when Hungry.
    def effect_232(self):
        return []
    # The user and target swap positions.
    def effect_233(self):
        return []
    # The target of the move warps, landing on the stairs, becoming Petrified indefinitely until attacked.
    def effect_234(self):
        return []
    # The allies of the user of this move warp, landing on the user.
    def effect_235(self):
        return []
    # The move's user gains the Mini Counter status.
    def effect_236(self):
        return []
    # This move's target becomes Paused.
    def effect_237(self):
        return []
    # The user's allies warp to the user and land on them.
    def effect_238(self):
        return []
    # This move has no effect. Associated with the Reviver Orb which was reduced to have no power and dummied out in development.
    def effect_239(self):
        return []
    # The team leader and their allies escape from the dungeon, and if used in a linked move - somehow - the moves stop being used.
    def effect_240(self):
        return []
    # This move causes special effects depending on the terrain, with 30% probability.
    def effect_241(self):
        return []
    # This move will cause a special effect depending on the terrain.
    def effect_242(self):
        return []
    # The target of the move transforms into an item. They will not drop any hold items, and the defeater of the Pokemon will not gain any experience.
    def effect_243(self):
        return []
    # This move transforms into the last move used by the target of the move permanently.
    def effect_244(self):
        return []
    # The user acquires the Mirror Move status.
    def effect_245(self):
        return []
    # The user of this move gains the target's Abilities. This will fail if the user were to gain Wonder Guard.
    def effect_246(self):
        return []
    # The user and the target of this move will swap their Abilities. If either party has Wonder Guard as an Ability, the move fails.
    def effect_247(self):
        return []
    # The user's type changes to that of one of their moves at random, regardless of the move's type. Weather Ball is considered to be Normal. Fails if the user has the Forecast Ability.
    def effect_248(self):
        return []
    # All items held by the user and their allies are no longer sticky. For members of rescue teams, this includes all items on their person in the bag.
    def effect_249(self):
        return []
    # The target loses HP based on the user's IQ.
    def effect_250(self):
        return []
    # The target obtains the Snatch status; to prevent conflicts, all others with the Snatch status at this time will lose it.
    def effect_251(self):
        return []
    # The user will change types based on the terrain.
    def effect_252(self):
        return []
    # The target loses HP based on the user's IQ.
    def effect_253(self):
        return []
    # The user of this move copies the stat changes on the target.
    def effect_254(self):
        return []
    # Whenever at an attack hits the user, if this move is known and the user asleep, the user will face the attack and use this move. 30% to cause cringing. Ignores Confusion and Cowering and linked moves.
    def effect_255(self):
        return []
    # If this move is used by a member of a rescue team, all items named "Used TM" are restored to their original usable state. Also unstickies them.
    def effect_256(self):
        return []
    # The target of this move becomes muzzled.
    def effect_257(self):
        return []
    # This move once used will cause the user to follow up with a random second attack.
    def effect_258(self):
        return []
    # The targets of this move can identify which Pokemon in the floor are holding items and thus will drop them if defeated (or other applicable instances).
    def effect_259(self):
        return []
    # The user gains the Conversion 2 status. Fails of the user has the Forecast ability.
    def effect_260(self):
        return []
    # The user of the move moves as far as possible in their direction of facing, stopping at a wall or Pokemon. Fails on floors with cliffs.
    def effect_261(self):
        return []
    # All unclaimed items on the floor, excepting those within two tiles of the user, land on the user's position, provided there is space around the user.
    def effect_262(self):
        return []
    # The user of this move uses the last move used by the target, excepting Assist, Mimic, Encore, Mirror Move, and Sketch, or if the target is charging for an attack.
    def effect_263(self):
        return []
    # The target is thrown onto a random space the target can enter within the room's range from the perspective of the user, and takes a random facing. If a foe is in the room, they are thrown to them instead, and both lose 10 HP.
    def effect_264(self):
        return []
    # The target loses HP dependent on their species.
    def effect_265(self):
        return []
    # One of an ally's stats is raised by two stages at random.
    def effect_266(self):
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
    def effect_267(self):
        return []
    # The damage for this move doubles if the user were attacked on the previous turn.
    def effect_268(self):
        return []
    # If the user is under 50% HP, then the damage from this move is doubled.
    def effect_269(self):
        return []
    # If the target is holding a Berry or has one in their bag or the like, then the user of this move ingests it and uses its effects.
    def effect_270(self):
        return []
    # This move has a 70% chance to raise the user's Sp. Atk. by one stage.
    def effect_271(self):
        if random.randrange(0, 100) < 70:
            return self.get_stat_change_events(self.attacker, "sp_attack", 1)
        else:
            return []
    # This move will confuse the target.
    def effect_272(self):
        return []
    # If this move hits, the user's Defense and Sp. Def. will be lowered by one stage each.
    def effect_273(self):
        res = []
        res += self.get_stat_change_events(self.attacker, "defense", -1)
        res += self.get_stat_change_events(self.attacker, "sp_defense", -1)
        return res
    # This move will deal more damage to foes with higher HP.
    def effect_274(self):
        return []
    # This move has a 60% chance to cause the targets to fall asleep.
    def effect_275(self):
        return []
    # This move clears the weather for the floor.
    def effect_276(self):
        return []
    # This move hits the foe twice.
    def effect_277(self):
        return []
    # The target cannot use items, nor will their items bear any effect if held.
    def effect_278(self):
        return []
    # This move ignores Protect status.
    def effect_279(self):
        return []
    # This move has a 10% to cause the foe to cringe, and a 10% chance to cause a burn.
    def effect_280(self):
        res = []
        if random.randrange(0, 100) < 10:
            res += self.get_cringe_events()
        if random.randrange(0, 100) < 10:
            res += self.get_burn_events()
        return res
    # This move throws an item at the target.
    def effect_281(self):
        return []
    # This move has a 30% chance to paralyze.
    def effect_282(self):
        if random.randrange(0, 100) < 30:
            return self.get_paralyze_events()
        else:
            return []
    # This move grants the Gastro Acid ability to the target, negating their abilities.
    def effect_283(self):
        return []
    # This move's damage increments with higher weight on the target.
    def effect_284(self):
        return []
    # The floor falls under the Gravity state: Flying Pokemon can be hit by Ground moves, and Levitate is negated.
    def effect_285(self):
        return []
    # The foe and the user swap stat changes to their Defense and Sp. Def. stats.
    def effect_286(self):
        return []
    # This move has a 30% chance to poison the target.
    def effect_287(self):
        if random.randrange(0, 100) < 30:
            return self.get_poisoned_events()
        else:
            return []
    # This move deals double damage to targets with halved movement speed.
    def effect_288(self):
        return []
    # After using this move, the user has its movement speed reduced.
    def effect_289(self):
        return self.get_stat_change_events(self.attacker, "speed", -1)
    # Grants all enemies in the user's room the Heal Block ailment, preventing healing of HP.
    def effect_290(self):
        return []
    # The user recovers 50% of their maximum HP.
    def effect_291(self):
        return []
    # The health of all targets and their status ailments are cured. However, the user of this move will also have their HP dropped to just 1.
    def effect_292(self):
        return []
    # The user and the target swap stat modifications for their Attack and Defense.
    def effect_293(self):
        return []
    # This move has a 10% to cause the foe to cringe, and a 10% chance to cause freezing.
    def effect_294(self):
        res = []
        if random.randrange(0, 100) < 10:
            return self.get_cringe_events()
        if random.randrange(0, 100) < 10:
            return self.get_freeze_events()
        return res
    # This move will inflict damage on the target, but only if the user has a move with 0 PP. Damage rises as more moves have 0 PP.
    def effect_295(self):
        return []
    # This move has a 30% chance to burn the target.
    def effect_296(self):
        if random.randrange(0, 100) < 30:
            return self.get_burn_events()
        else:
            return []
    # This move grants the Lucky Chant status to the targets, preventing critical hits.
    def effect_297(self):
        return []
    # This move heals all the HP and PP of the targets and all their ailments as well. However as a cost the user returns to 1 HP.
    def effect_298(self):
        return []
    # The user of this move gains the Magnet Rise status, gaining immunity to Ground moves.
    def effect_299(self):
        return []
    # The user is granted the Metal Burst status.
    def effect_300(self):
        return []
    # If the target has an evasion level above 10 stages, it becomes 10 stages. They are either way granted Miracle Eye status, permitting Psychic moves to hit Dark types.
    def effect_301(self):
        return []
    # This move has a 30% chance to lower the target's accuracy.
    def effect_302(self):
        if random.randrange(100) < 30:
            return self.get_stat_change_events(self.defender, "accuracy", -1)
        else:
            return []
    # The user's Sp. Atk. is boosted by two stages.
    def effect_303(self):
        return self.get_stat_change_events(self.attacker, "sp_attack", 2)
    # This move's damage as well as type will change depending on the Berry the user holds, if any.
    def effect_304(self):
        return []
    # The user and the target will swap modifications to their Attack and Sp. Atk. stats.
    def effect_305(self):
        return []
    # The user swaps their Attack and Defense stat modifiers.
    def effect_306(self):
        return []
    # The user transfers their status problems to the target of this move, while simultaneously curing their own.
    def effect_307(self):
        return []
    # This move increments power further if the target has boosted Attack, Defense, Sp. Atk., and/or Sp. Def., and more for every stage boosted.
    def effect_308(self):
        return []
    # This move has a 20% chance to confuse the target.
    def effect_309(self):
        return []
    # Targets of this move have their movement speed raised by two stages.
    def effect_310(self):
        return self.get_stat_change_events(self.defender, "speed", 2)
    # This move's user gains 50% of their maximum HP. In return however, they will lose any Flying-type designations until their next turn.
    def effect_311(self):
        return []
    # This move has a 40% chance to lower the targets' Sp. Atk. by two stages.
    def effect_312(self):
        if random.randrange(0, 100) < 40:
            return self.get_stat_change_events(self.defender, "sp_attack", -2)
        else:
            return []
    # The user gains the Shadow Force status: they become untouchable for a single turn, attacking on the next turn. This move deals double damage. This move defies Protect status. This move cannot be linked.
    def effect_313(self):
        return []
    # The user of the move creates a Stealth Rock trap underneath their feet.
    def effect_314(self):
        return []
    # This move has a 10% chance to make the target cringe, and a 10% chance to paralyze them too.
    def effect_315(self):
        res = []
        if random.randrange(0, 100) < 10:
            return self.get_cringe_events()
        if random.randrange(0, 100) < 10:
            return self.get_paralyze_events()
        return res
    # This move places a Toxic Spikes trap under the user's feet.
    def effect_316(self):
        return []
    # This move at random increases or lowers the movement speed of all targets by one stage.
    def effect_317(self):
        return self.get_stat_change_events(self.defender, "speed", random.choice([-1, 1]))
    # This move will deal more damage the lower its current PP.
    def effect_318(self):
        return []
    # This move will awaken a target affected by the Napping, Sleep, or Nightmare statuses, but if the target has one of these the move will also do double damage.
    def effect_319(self):
        return []
    # This move if it hits will inflict the target with the Sleepless status. It will fail on Pokemon with the Truant Ability.
    def effect_320(self):
        return []

    # Effects
    # TODO: Miss sfx, Miss gfx label
    def get_miss_events(self):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.attacker.name_color)
            .write(self.attacker.name)
            .set_color(text.WHITE)
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
            .set_color(text.WHITE)
            .write(" took no damage.")
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
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.hurt_animation_id()))
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
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.hurt_animation_id()))
        events.append(event.SleepEvent(20))
        if damage >= self.defender.hp_status:
            events += self.get_faint_events(self.defender)
        return events

    def get_faint_events(self, p: pokemon.Pokemon):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(p.name_color)
            .write(p.name)
            .set_color(text.WHITE)
            .write(" fainted!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.FaintEvent(p))
        events.append(event.SleepEvent(20))
        return events

    def get_heal_events(self, p: pokemon.Pokemon, heal: int):
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
            tb.write(" was fully healed!")
        else:
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
        events.append(gameevent.SetAnimationEvent(self.attacker, self.attacker.hurt_animation_id()))
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
        events.append(gameevent.SetAnimationEvent(self.defender, self.defender.hurt_animation_id()))
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

    def get_stat_change_events(self, target: pokemon.Pokemon, stat: str, amount: int):
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
        if abs(amount) > 1 or stat.endswith("division"):
            adverb = "sharply"
        elif abs(amount) == 1:
            adverb = "slightly"
        else:
            adverb = ""
        
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(target.name_color)
            .write(target.name)
            .set_color(text.WHITE)
            .write(f"'s {stat_name} {verb} {adverb}!")
            .build()
            .render()
        )
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(gameevent.StatChangeEvent(target, stat, amount))
        events.append(gameevent.StatAnimationEvent(target, statanimation_db[stat_anim_name, anim_type]))
        events.append(event.SleepEvent(20))
        return events

    def update(self):
        if not self.is_active:
            return
        if self.event_index == 0:
            for p in self.floor.spawned:
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
        elif isinstance(ev, gameevent.HealEvent):
            self.handle_heal_event(ev)
        elif isinstance(ev, gameevent.FaintEvent):
            self.handle_faint_event(ev)
        elif isinstance(ev, gameevent.StatChangeEvent):
            self.handle_stat_change_event(ev)
        elif isinstance(ev, gameevent.StatusEvent):
            self.handle_status_event(ev)
        elif isinstance(ev, gameevent.StatAnimationEvent):
            self.handle_stat_animation_event(ev)
        else:
            raise RuntimeError(f"Event not handled!: {ev}")

    def handle_log_event(self, ev: gameevent.LogEvent):
        if ev.new_divider:
            self.log.new_divider()
        self.log.write(ev.text_surface)
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
        ev.handled = True

    def handle_heal_event(self, ev: gameevent.HealEvent):
        ev.target.status.hp.increase(ev.amount)
        ev.handled = True
    
    def handle_faint_event(self, ev: gameevent.FaintEvent):
        self.floor[ev.target.position].pokemon_ptr = None
        if isinstance(ev.target, pokemon.EnemyPokemon):
            self.floor.active_enemies.remove(ev.target)
        else:
            self.party.standby(ev.target)
        self.floor.spawned.remove(ev.target)
        ev.handled = True

    def handle_stat_change_event(self, ev: gameevent.StatChangeEvent):
        statistic: pokemondata.Statistic = getattr(ev.target.status, ev.stat)
        statistic.increase(ev.amount)
        ev.handled = True

    def handle_status_event(self, ev: gameevent.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        ev.handled = True

    def handle_stat_animation_event(self, ev: gameevent.StatAnimationEvent):
        ev.anim.update()
        if ev.anim.is_restarted():
            ev.handled = True

    # Damage Mechanics
    def calculate_damage(self) -> int:
        # Step 0 - Special Exceptions
        if self.current_move.category is move.MoveCategory.OTHER:
            return 0
        if self.attacker.status.belly.value == 0 and self.attacker is not self.party.leader:
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
        damage *= (random.randint(0, 16383) + 57344) / 65536
        damage = round(damage)

        return damage

    def miss(self) -> bool:
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

        chance = random.randrange(0, 100)
        hits = chance < acc
        return not hits

    def is_move_animation_event(self, target: pokemon.Pokemon) -> bool:
        if not self.is_active:
            return False
        if not self.events:
            return False
        ev = self.events[self.event_index]
        if ev.handled:
            return False
        if isinstance(ev, gameevent.StatAnimationEvent):
            return ev.target is target

    def render(self) -> pygame.Surface:
        ev = self.events[self.event_index]
        if isinstance(ev, gameevent.StatAnimationEvent):
            return ev.anim.render()
