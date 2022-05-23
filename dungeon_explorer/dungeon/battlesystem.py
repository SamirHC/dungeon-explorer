import math
import random

import pygame
from dungeon_explorer.common import constants, direction, inputstream, text
from dungeon_explorer.dungeon import damage_chart, dungeon, dungeonstatus
from dungeon_explorer.events import event, gameevent
from dungeon_explorer.move import move, animation
from dungeon_explorer.pokemon import pokemon, pokemondata


class BattleSystem:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon
        self.current_move = None
        self.is_active = False
        self.attacker = None
        self.defender = None
        self.targets: list[pokemon.Pokemon] = []
        self.current_move = None
        self.events: list[event.Event] = []
        self.event_index = 0

        self.dispatcher = {i: getattr(self, f"effect_{i}", self.effect_0) for i in range(321)}

    @property
    def is_waiting(self) -> bool:
        return not self.is_active and self.attacker is not None

    def deactivate(self):
        self.events.clear()
        self.attacker = None
        self.defender = None
        self.targets.clear()
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

        if move_index + 1 > len(self.dungeon.user.moveset):
            return False
        if not self.dungeon.user.moveset.selected[move_index]:
            return False
        
        self.attacker = self.dungeon.user
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
            return self.dungeon.spawned
        if target_type is move.TargetType.ALLIES:
            return self.get_allies()
        if target_type is move.TargetType.ENEMIES:
            return self.get_enemies()
        if target_type is move.TargetType.SPECIAL:
            range_type = self.current_move.range_category
            if range_type is move.MoveRange.EVERYONE_IN_THE_ROOM_EXCEPT_THE_USER:
                return [p for p in self.dungeon.spawned if p is not self.attacker]

    def get_enemies(self) -> list[pokemon.Pokemon]:
        if isinstance(self.attacker, pokemon.EnemyPokemon):
            return self.dungeon.party.members
        return self.dungeon.active_enemies

    def get_allies(self) -> list[pokemon.Pokemon]:
        if isinstance(self.attacker, pokemon.EnemyPokemon):
            return self.dungeon.active_enemies
        return self.dungeon.party.members

    def in_room_with_enemies(self) -> bool:
        return any([self.dungeon.floor.in_same_room(self.attacker.position, enemy.position) for enemy in self.get_enemies()])

    def get_straight_targets(self):
        move_range = self.current_move.range_category
        target_group = {p.position: p for p in self.get_target_group()}
        result = []
        if not move_range.cuts_corners() and self.dungeon.cuts_corner(self.attacker.position, self.attacker.direction) and self.attacker.movement_type is not pokemondata.MovementType.PHASING:
            return result
        x, y = self.attacker.position
        for _ in range(move_range.distance()):
            x += self.attacker.direction.x
            y += self.attacker.direction.y
            if self.dungeon.is_wall((x, y)) and self.attacker.movement_type is not pokemondata.MovementType.PHASING:
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
        if p in self.dungeon.party:
            enemies = [e for e in self.dungeon.active_enemies if self.dungeon.can_see(p.position, e.position)]
        else:
            enemies = [e for e in self.dungeon.party if self.dungeon.can_see(p.position, e.position)]
        
        if enemies:
            target_enemy = min(enemies, key=lambda e: max(abs(e.x - p.x), abs(e.y - p.y)))
            p.face_target(target_enemy.position)

        self.attacker = p
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
            self.current_move = move.REGULAR_ATTACK
        else:
            self.current_move = self.attacker.moveset[move_index]
        if self.can_activate():
            return self.activate(move_index)
        return False

    def can_activate(self) -> bool:
        if self.current_move.activation_condition != "None":
            return False
        move_range = self.current_move.range_category
        if move_range is move.MoveRange.USER or move_range.is_room_wide() or move_range is move.MoveRange.FLOOR:
            return self.in_room_with_enemies()
        self.targets = self.get_targets()
        if not self.targets:
            return False
        elif move_range is move.MoveRange.LINE_OF_SIGHT and self.targets[0] not in self.get_enemies():
            return False
        return True

    # ACTIVATION
    def activate(self, move_index: int) -> bool:
        if move_index == -1:
            self.current_move = move.REGULAR_ATTACK
        elif self.attacker.moveset.can_use(move_index):
            self.attacker.moveset.use(move_index)
            self.current_move = self.attacker.moveset[move_index]
        else:
            self.current_move = move.STRUGGLE

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
        if self.current_move is move.REGULAR_ATTACK:
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
        if self.current_move.range_category is move.MoveRange.FLOOR:
            res += self.get_events_from_effect(effect)
        else:
            for target in self.targets:
                self.defender = target
                if self.miss():
                    res += self.get_miss_events()
                    continue
                if self.current_move.taunt:
                    res += self.get_events_from_damage_effect()
                res += self.get_events_from_effect(effect)
        return res

    # Move effect events
    def get_events_from_effect(self, effect: int):
        return self.dispatcher.get(effect, self.dispatcher[0])()
    
    # Deals damage, no special effects.
    def effect_0(self):
        return []
    # The target's damage doubles if they are Digging.
    def effect_3(self):
        for ev in self.events:
            if isinstance(ev, gameevent.DamageEvent):
                if ev.target.status.digging:
                    ev.amount *= 2
                return []
        return []
    # The target's damage doubles if they are Flying or are Bouncing.
    def effect_4(self):
        for ev in self.events:
            if isinstance(ev, gameevent.DamageEvent):
                if ev.target.status.bouncing or ev.target.status.flying:
                    ev.amount *= 2
                return []
        return []
    # Recoil damage: the user loses 1/4 of their maximum HP. Furthermore, PP does not decrement. (This is used by Struggle.)
    def effect_5(self):
        return self.get_recoil_events(25)
    # 10% chance to burn the target.
    def effect_6(self):
        if random.randrange(0, 100) < 10:
            return self.get_burn_events()
        else:
            return []
    def effect_7(self):
        return self.effect_6()
    # 10% chance to freeze the target.
    def effect_8(self):
        if random.randrange(0, 100) < 10:
            return self.get_freeze_events()
        else:
            return []
    # This user goes into the resting Paused status after this move's use to recharge, but only if a target is hit.
    def effect_9(self):
        self.attacker.status.paused = True
        return []
    # Applies the Focus Energy status to the user, boosting their critical hit rate for 3-4 turns.
    def effect_10(self):
        self.attacker.status.focus_energy = True
        return []
    # The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0.
    def effect_12(self):  # Used by Fissure.
        for ev in self.events:
            if isinstance(ev, gameevent.DamageEvent):
                if ev.target.type.get_type_effectiveness(self.current_move.type) is damage_chart.TypeEffectiveness.LITTLE:
                    ev.amount = 0
                else:
                    ev.amount = 9999
                return []
        return []
    def effect_13(self):  # Used by Sheer Cold and Guillotine.
        return self.effect_12()
    # The target has a 10% chance to become constricted (unable to act while suffering several turns of damage).
    def effect_15(self):
        if random.randrange(0, 100) < 10:
            return self.get_constricted_events()
        else:
            return []
    # The target has a 10% chance to become constricted (unable to act while suffering several turns of damage). Damage suffered doubles if the target is Diving.
    def effect_16(self):
        return self.effect_15()
    # Damage doubles if the target is diving.
    def effect_17(self):
        for ev in self.events:
            if isinstance(ev, gameevent.DamageEvent):
                if ev.target.status.diving:
                    ev.amount *= 2
                return []
        return []
    # The target will be unable to move.
    def effect_18(self):
        self.defender.status.shadow_hold = True
        return []
    # The target has an 18% chance to become poisoned.
    def effect_19(self):
        if random.randrange(0, 100) < 18:
            return self.get_poisoned_events()
        else:
            return []
    # This move has a 10% chance to lower the target's Sp. Def. by one stage.
    def effect_20(self):
        if random.randrange(0, 100) < 10:
            return self.get_stat_change_events(self.defender, "sp_defense", -1)
        else:
            return []
    # This move has a 10% chance to lower the target's Defense by one stage.
    def effect_21(self):
        if random.randrange(0, 100) < 10:
            return self.get_stat_change_events(self.defender, "defense", -1)
        else:
            return []
    # This move has a 10% chance to raise the user's Attack by one stage.
    def effect_22(self):
        if random.randrange(0, 100) < 10:
            return self.get_stat_change_events(self.attacker, "attack", 1)
        else:
            return []
    # This move has a 10% chance to raise the user's Defense by one stage.
    def effect_23(self):
        if random.randrange(0, 100) < 10:
            return self.get_stat_change_events(self.attacker, "defense", 1)
        else:
            return []
    # This move has a 10% chance to poison the target.
    def effect_24(self):
        if random.randrange(0, 100) < 10:
            return self.get_poisoned_events()
        else:
            return []
    # The damage dealt is doubled if the target is Flying or Bouncing. This also has a 15% chance to make the target cringe.
    def effect_25(self):
        res = []
        res += self.effect_4()
        if random.randrange(0, 100) < 15:
            res += self.get_cringe_events()
        return res
    # This move has a 10% chance to lower the target's movement speed by one stage.
    def effect_26(self):
        if random.randrange(0, 100) < 10:
            return self.get_stat_change_events(self.defender, "speed", -1)
        else:
            return []
    # This move has a 10% chance to raise the user's Attack, Defense, Sp. Atk., Sp. Def., and movement speed by one stage each.
    def effect_27(self):
        if random.randrange(0, 100) < 10:
            res = []
            res += self.get_stat_change_events(self.attacker, "attack", 1)
            res += self.get_stat_change_events(self.attacker, "defense", 1)
            res += self.get_stat_change_events(self.attacker, "sp_attack", 1)
            res += self.get_stat_change_events(self.attacker, "sp_defense", 1)
            res += self.get_stat_change_events(self.attacker, "speed", 1)
        else:
            return []
    # This move has a 10% chance to confuse the target.
    def effect_28(self):
        if random.randrange(0, 100) < 10:
            return self.get_confusion_events()
        else:
            return []
    # This move has a 50% chance to lower the target's Sp. Atk. by one stage.
    def effect_29(self):
        if random.randrange(0, 100) < 50:
            return self.get_stat_change_events(self.defender, "sp_attack", -1)
        else:
            return []
    # This move has a 50% chance to lower the target's Sp. Def. by one stage.
    def effect_30(self):
        if random.randrange(0, 100) < 50:
            return self.get_stat_change_events(self.defender, "sp_defense", -1)
        else:
            return []
    # This move has a 50% chance to lower the target's Defense by one stage.
    def effect_31(self):
        if random.randrange(0, 100) < 50:
            return self.get_stat_change_events(self.defender, "defense", -1)
        else:
            return []
    # This move has a 40% chance to poison the target.
    def effect_32(self):
        if random.randrange(0, 100) < 40:
            return self.get_poisoned_events()
        else:
            return []
    # This move has a 50% chance to burn the target.
    def effect_33(self):
        if random.randrange(0, 100) < 50:
            return self.get_burn_events()
        else:
            return []
    # This move has a 10% chance to paralyze the target.
    def effect_34(self):
        if random.randrange(0, 100) < 10:
            return self.get_paralyze_events()
        else:
            return []
    # This move has a 15% chance to paralyze the target.
    def effect_35(self):
        if random.randrange(0, 100) < 15:
            return self.get_paralyze_events()
        else:
            return []
    # This move has a 10% chance to make the target cringe.
    def effect_36(self):
        if random.randrange(0, 100) < 10:
            return self.get_cringe_events()
        else:
            return []
    # This move has a 20% chance to make the target cringe.
    def effect_37(self):
        if random.randrange(0, 100) < 20:
            return self.get_paralyze_events()
        else:
            return []
    #This move has a 25% chance to make the target cringe.
    def effect_38(self):
        if random.randrange(0, 100) < 25:
            return self.get_paralyze_events()
        else:
            return []
    # This move has a 30% chance to make the target cringe.
    def effect_39(self):
        if random.randrange(0, 100) < 30:
            return self.get_paralyze_events()
        else:
            return []
    # This move has a 40% chance to make the target cringe.
    def effect_40(self):
        if random.randrange(0, 100) < 40:
            return self.get_paralyze_events()
        else:
            return []
    # This move has a 30% chance to confuse the target.
    def effect_41(self):
        if random.randrange(0, 100) < 30:
            return self.get_confusion_events()
        else:
            return []
    # This move has a 20% chance to do one of these: burn, freeze, or paralyze the target.
    def effect_42(self):
        if random.randrange(0, 100) < 20:
            choice = random.randint(0, 2)
            if choice == 0:
                return self.get_burn_events()
            elif choice == 1:
                return self.get_freeze_events()
            else:
                return self.get_paralyze_events()
        else:
            return []
    # This move has a 20% chance to raise the user's Attack by one stage.
    def effect_43(self):
        if random.randrange(0, 100) < 20:
            return self.get_stat_change_events(self.attacker, "attack", 1)
        else:
            return []
    # This move has a 10% chance to burn the target.
    def effect_44(self):
        return self.effect_6()
    # The target can become infatuated, provided they are of the opposite gender of the user.
    def effect_45(self):
        pass
    # This move paralyzes the target. (Used by Disable.)
    def effect_46(self):
        return self.get_paralyze_events()
    # This move has a 35% chance to make the target cringe.
    def effect_47(self):
        if random.randrange(0, 100) < 35:
            return self.get_cringe_events()
        else:
            return []
    # This move deals fixed damage: 55 HP.
    def effect_48(self):
        for ev in self.events:
            if isinstance(ev, gameevent.DamageEvent):
                ev.amount = 55
                return []
        return []
    # This move deals fixed damage: 65 HP.
    def effect_49(self):
        for ev in self.events:
            if isinstance(ev, gameevent.DamageEvent):
                ev.amount = 65
                return []
        return []
    # This move paralyzes the target. (Used by Stun Spore.)
    def effect_50(self):
        return self.effect_46()
    # The floor gains the Mud Sport or Water Sport status. The former weakens Electric moves, and the latter weakens Fire.
    def effect_137(self):
        if self.current_move.name == "Water Sport":
                self.dungeon.status.water_sport.value = self.dungeon.status.water_sport.max_value
        elif self.current_move.name == "Mud Sport":
            self.dungeon.status.mud_sport.value = self.dungeon.status.mud_sport.max_value
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
    # This move will lower the target's Accuracy by one stage.
    def effect_154(self):
        return self.get_stat_change_events(self.defender, "accuracy", -1)
    # This move raises the user's Defense by one stage.
    def effect_172(self):
        return self.get_stat_change_events(self.attacker, "defense", 1)
    
    # Effects
    def get_events_from_damage_effect(self):
        res = []
        damage = self.calculate_damage()
        res += self.get_damage_events(damage)
        return res

    def get_events_from_fixed_damage_effect(self):
        damage = self.current_move.power
        return self.get_damage_events(damage)

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

    # TODO: Damage sfx, Defender hurt animation
    def get_damage_events(self, damage):
        if damage == 0:
            return self.get_no_damage_events()
        events = []
        effectiveness = self.defender.type.get_type_effectiveness(self.current_move.type)
        if effectiveness is not damage_chart.TypeEffectiveness.REGULAR:
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

    def get_recoil_events(self, percent: int):
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
        if amount < 0:
            verb = "fell"
            anim_type = "000"
        elif amount > 0:
            verb = "rose"
            anim_type = "001"
        else:
            verb = "returned to normal"
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
        events.append(gameevent.StatAnimationEvent(target, animation.stat_change_anim_data[stat_name, anim_type]))
        events.append(event.SleepEvent(20))
        return events

    def update(self):
        if not self.is_active:
            return
        if self.event_index == 0:
            for p in self.dungeon.spawned:
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
        ev.handled = True
    
    def handle_faint_event(self, ev: gameevent.FaintEvent):
        self.dungeon.floor[ev.target.position].pokemon_ptr = None
        if isinstance(ev.target, pokemon.EnemyPokemon):
            self.dungeon.active_enemies.remove(ev.target)
        else:
            self.dungeon.party.standby(ev.target)
        self.dungeon.spawned.remove(ev.target)
        ev.handled = True

    def handle_stat_change_event(self, ev: gameevent.StatChangeEvent):
        statistic: pokemondata.Statistic = getattr(ev.target.status, ev.stat)
        statistic.increase(ev.amount)
        ev.handled = True

    def handle_status_event(self, ev: gameevent.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        ev.handled = True

    def handle_stat_animation_event(self, ev: gameevent.StatAnimationEvent):
        ev.time += 1
        if ev.time < ev.stat_anim_data.durations[ev.index]:
            return
        ev.time = 0
        ev.index += 1
        if ev.index >= len(ev.stat_anim_data.durations):
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
            return ev.stat_anim_data.get_frame(ev.index)
