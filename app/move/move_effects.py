import random

from app.common import utils

# from app.move.move import Move
import app.move.move_effect_helpers as eff
from app.events import event, game_event
from app.pokemon.pokemon import Pokemon
from app.pokemon.stat import Stat
from app.pokemon.status_effect import StatusEffect
from app.pokemon.animation_id import AnimationId
from app.dungeon import target_getter
from app.move import damage_mechanics
from app.common import text
from app.dungeon.weather import Weather


# Regular Attack
def move_0(ev: game_event.BattleSystemEvent):
    def _regular_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _regular_attack_effect))
    return events


# Iron Tail
def move_1(ev: game_event.BattleSystemEvent):
    def _iron_tail_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        events = eff.get_basic_attack_events(ev, defender)
        if utils.is_success(30):
            events.append(game_event.StatStageChangeEvent(defender, Stat.DEFENSE, -1))
        return events

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _iron_tail_effect))
    return events


# Ice Ball
def move_2(ev: game_event.BattleSystemEvent):
    HIT_MULTIPLIER = 1.5

    def _ice_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        damage = damage_mechanics.calculate_damage(
            ev.dungeon, ev.attacker, defender, ev.move, ev.kwargs["multiplier"]
        )
        events = eff.get_damage_events(ev, defender, damage)
        return events

    if not ev.kwargs:
        ev.kwargs["multiplier"] = 1
        ev.kwargs["iterations"] = 1

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _ice_ball_effect)
    if (
        any(isinstance(e, game_event.DamageEvent) for e in events)
        and ev.kwargs["iterations"] < 5
    ):
        ev.kwargs["iterations"] += 1
        ev.kwargs["multiplier"] *= HIT_MULTIPLIER
        events.append(ev)

    return events


# Yawn
def move_3(ev: game_event.BattleSystemEvent):
    def _yawn_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
        )
        if defender.status.has_status_effect(StatusEffect.YAWNING):
            tb.write(" is already yawning!")
        elif defender.status.is_asleep():
            tb.write(" is already asleep!")
        else:
            tb.write(" yawned!")
            defender.status.afflict(StatusEffect.YAWNING, ev.dungeon.turns.value + 3)

        events = []
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _yawn_effect)
    return events


# Lovely Kiss
def move_4(ev: game_event.BattleSystemEvent):
    def _lovely_kiss_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_asleep_events(ev.dungeon, defender)

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _lovely_kiss_effect)
    return events


# Nightmare
def move_5(ev: game_event.BattleSystemEvent):
    def _nightmare_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
        )
        if not defender.status.has_status_effect(StatusEffect.NIGHTMARE):
            # Overrides any other sleep status conditions
            defender.status.clear_affliction(StatusEffect.ASLEEP)
            defender.status.clear_affliction(StatusEffect.NAPPING)
            defender.status.clear_affliction(StatusEffect.YAWNING)
            defender.status.afflict(
                StatusEffect.NIGHTMARE, ev.dungeon.turns.value + random.randint(4, 7)
            )
            tb.write(" is caught in a nightmare!")
        else:
            tb.write(" is already having a nightmare!")

        events = []
        events.append(game_event.SetAnimationEvent(defender, AnimationId.SLEEP, True))
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _nightmare_effect)
    return events


# Morning Sun
def move_6(ev: game_event.BattleSystemEvent):
    def _morning_sun_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        SWITCHER = {
            Weather.CLEAR: 50,
            Weather.CLOUDY: 30,
            Weather.FOG: 10,
            Weather.HAIL: 10,
            Weather.RAINY: 10,
            Weather.SANDSTORM: 20,
            Weather.SNOW: 1,
            Weather.SUNNY: 80,
        }
        heal_amount = SWITCHER.get(ev.dungeon.floor.status.weather, 0)
        return [game_event.HealEvent(defender, heal_amount)]

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _morning_sun_effect)
    return events


"""
# Vital Throw
def move_7(ev: BattleSystemEvent):
    def _vital_throw_effect(defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.name)
            .set_color(text.WHITE)
        )
        if defender.has_status_effect(StatusEffect.VITAL_THROW):
            tb.write(" is already ready with its\nVital Throw!")
        else:
            tb.write(" readied its Vital Throw!")
            defender.afflict(StatusEffect.VITAL_THROW)  # = 18
        text_surface = tb.build().render()
        events = []
        events.append(gameevent.LogEvent(text_surface))
        events.append(event.SleepEvent(20))
        return events

    return get_all_hit_or_miss_events(_vital_throw_effect)


# Dig
def move_8(ev: BattleSystemEvent):
    if ev.dungeon.tileset.underwater:
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
            .set_color(ev.attacker.name_color)
            .write(ev.attacker.name)
            .set_color(text.WHITE)
            .write(" burrowed underground!")
            .build()
            .render()
        )
    events = []
    events.append(gameevent.LogEvent(text_surface))
    events.append(gameevent.StatusEvent(ev.attacker, "digging", True))
    events.append(event.SleepEvent(20))
    return events


# Thrash
def move_9(ev: BattleSystemEvent):
    events = []
    original_direction = ev.attacker.direction
    for _ in range(3):
        d = original_direction  # random.choice(list(Direction))
        ev.attacker.direction = d
        events.append(gameevent.DirectionEvent(ev.attacker, d))
        # events += get_attacker_move_animation_events()
        for target in target_getter.get_targets(ev.attacker, ev.dungeon, ev.move.move_range):
            defender = target
            if defender.fainted:
                break
            if damage_mechanics.miss(ev.dungeon, ev.attacker, defender, ev.move):
                events += get_miss_events()
                break
            damage = damage_mechanics.calculate_damage(
                ev.dungeon, ev.attacker, defender, ev.move
            )
            events += get_damage_events(damage)
    ev.attacker.direction = original_direction
    return events
"""
############
"""
# Deals damage, no special effects.
def move_0():
    damage = damage_mechanics.calculate_damage(dungeon, attacker, defender, current_move)
    return get_damage_events(damage)
# The target's damage doubles if they are Digging.
def move_3():
    multiplier = 1
    if defender.status.digging:
        multiplier = 2
    damage = damage_mechanics.calculate_damage(dungeon, attacker, defender, current_move) * multiplier
    return get_damage_events(damage)
# The target's damage doubles if they are Flying or are Bouncing.
def move_4():
    multiplier = 1
    if defender.status.flying or defender.status.bouncing:
        multiplier = 2
    damage = damage_mechanics.calculate_damage(dungeon, attacker, defender, current_move) * multiplier
    return get_damage_events(damage)
# Recoil damage: the user loses 1/4 of their maximum HP. Furthermore, PP does not decrement. (This is used by Struggle.)
def move_5():
    res = effect_0()
    res += get_recoil_events(25)
    return res
# 10% chance to burn the target.
def move_6():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_burn_events()
    return res
def move_7():
    return effect_6()
# 10% chance to freeze the target.
def move_8():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_freeze_events()
    return res
# This user goes into the resting Paused status after this move's use to recharge, but only if a target is hit.
def move_9():
    attacker.status.paused = True
    return effect_0()
# Applies the Focus Energy status to the user, boosting their critical hit rate for 3-4 turns.
def move_10():
    attacker.status.focus_energy = True
    return []
# The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0.
def move_12():  # Used by Fissure.
    if type_chart.get_move_effectiveness(current_move.type, defender.type) is TypeEffectiveness.LITTLE:
        return get_no_damage_events()
    else:
        return get_calamitous_damage_events()
def move_13():  # Used by Sheer Cold and Guillotine.
    return effect_12()
# The target has a 10% chance to become constricted (unable to act while suffering several turns of damage).
def move_15():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_constricted_events()
    return res
# The target has a 10% chance to become constricted (unable to act while suffering several turns of damage). Damage suffered doubles if the target is Diving.
def move_16():
    return effect_15()
# Damage doubles if the target is diving.
def move_17():
    multiplier = 1
    if defender.status.diving:
        multiplier = 2
    damage = damage_mechanics.calculate_damage(dungeon, attacker, defender, current_move) * multiplier
    return get_damage_events(damage)
# The target will be unable to move.
def move_18():
    defender.status.shadow_hold = True
    return []
# The target has an 18% chance to become poisoned.
def move_19():
    res = effect_0()
    if random.randrange(0, 100) < 18:
        res += get_poisoned_events()
    return res
# This move has a 10% chance to lower the target's Sp. Def. by one stage.
def move_20():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_stat_change_events(defender, "sp_defense", -1)
    return res
# This move has a 10% chance to lower the target's Defense by one stage.
def move_21():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_stat_change_events(defender, "defense", -1)
    return res
# This move has a 10% chance to raise the user's Attack by one stage.
def move_22():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_stat_change_events(attacker, "attack", 1)
    return res
# This move has a 10% chance to raise the user's Defense by one stage.
def move_23():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_stat_change_events(attacker, "defense", 1)
    return res
# This move has a 10% chance to poison the target.
def move_24():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_poisoned_events()
    return res
# The damage dealt is doubled if the target is Flying or Bouncing. This also has a 15% chance to make the target cringe.
def move_25():
    res = effect_4()
    if random.randrange(0, 100) < 15:
        res += get_cringe_events()
    return res
# This move has a 10% chance to lower the target's movement speed by one stage.
def move_26():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_stat_change_events(defender, "speed", -1)
    return res
# This move has a 10% chance to raise the user's Attack, Defense, Sp. Atk., Sp. Def., and movement speed by one stage each.
def move_27():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_stat_change_events(attacker, "attack", 1)
        res += get_stat_change_events(attacker, "defense", 1)
        res += get_stat_change_events(attacker, "sp_attack", 1)
        res += get_stat_change_events(attacker, "sp_defense", 1)
        res += get_stat_change_events(attacker, "speed", 1)
    return res
# This move has a 10% chance to confuse the target.
def move_28():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_confusion_events()
    return res
# This move has a 50% chance to lower the target's Sp. Atk. by one stage.
def move_29():
    res = effect_0()
    if random.randrange(0, 100) < 50:
        res += get_stat_change_events(defender, "sp_attack", -1)
    return res
# This move has a 50% chance to lower the target's Sp. Def. by one stage.
def move_30():
    res = effect_0()
    if random.randrange(0, 100) < 50:
        res += get_stat_change_events(defender, "sp_defense", -1)
    return res
# This move has a 50% chance to lower the target's Defense by one stage.
def move_31():
    res = effect_0()
    if random.randrange(0, 100) < 50:
        res += get_stat_change_events(defender, "defense", -1)
    return res
# This move has a 40% chance to poison the target.
def move_32():
    res = effect_0()
    if random.randrange(0, 100) < 40:
        res += get_poisoned_events()
    return res
# This move has a 50% chance to burn the target.
def move_33():
    res = effect_0()
    if random.randrange(0, 100) < 50:
        res += get_burn_events()
    return res
# This move has a 10% chance to paralyze the target.
def move_34():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_paralyze_events()
    return res
# This move has a 15% chance to paralyze the target.
def move_35():
    res = effect_0()
    if random.randrange(0, 100) < 15:
        res += get_paralyze_events()
    return res
# This move has a 10% chance to make the target cringe.
def move_36():
    res = effect_0()
    if random.randrange(0, 100) < 10:
        res += get_cringe_events()
    return res
# This move has a 20% chance to make the target cringe.
def move_37():
    res = effect_0()
    if random.randrange(0, 100) < 20:
        res += get_paralyze_events()
    return res
#This move has a 25% chance to make the target cringe.
def move_38():
    res = effect_0()
    if random.randrange(0, 100) < 25:
        res += get_paralyze_events()
    return res
# This move has a 30% chance to make the target cringe.
def move_39():
    res = effect_0()
    if random.randrange(0, 100) < 30:
        res += get_paralyze_events()
    return res
# This move has a 40% chance to make the target cringe.
def move_40():
    res = effect_0()
    if random.randrange(0, 100) < 40:
        res += get_paralyze_events()
    return res
# This move has a 30% chance to confuse the target.
def move_41():
    res = effect_0()
    if random.randrange(0, 100) < 30:
        res += get_confusion_events()
    return res
# This move has a 20% chance to do one of these: burn, freeze, or paralyze the target.
def move_42():
    res = effect_0()
    if random.randrange(0, 100) < 20:
        choice = random.randint(0, 2)
        if choice == 0:
            res += get_burn_events()
        elif choice == 1:
            res += get_freeze_events()
        else:
            res += get_paralyze_events()
    return res
# This move has a 20% chance to raise the user's Attack by one stage.
def move_43():
    res = effect_0()
    if random.randrange(0, 100) < 20:
        res += get_stat_change_events(attacker, "attack", 1)
    return res
# This move has a 10% chance to burn the target.
def move_44():
    return effect_6()
# The target can become infatuated, provided they are of the opposite gender of the user.
def move_45():
    defender.status.infatuated = True
    return []
# This move paralyzes the target. (Used by Disable.)
def move_46():
    return get_paralyze_events()
# This move has a 35% chance to make the target cringe.
def move_47():
    res = effect_0()
    if random.randrange(0, 100) < 35:
        res += get_cringe_events()
    return res
# This move deals fixed damage: 55 HP.
def move_48():
    return get_damage_events(55)
# This move deals fixed damage: 65 HP.
def move_49():
    return get_damage_events(65)
# This move paralyzes the target. (Used by Stun Spore.)
def move_50():
    return effect_46()
# This move has a 10% chance to paralyze the target.
def move_51():
    res = effect_0()
    if random.randrange(100) < 10:
        res += get_paralyze_events()
    return res
# This move puts the target to sleep.
def move_52():
    defender.status.asleep = True
    return []
# The target begins to yawn.
def move_53():
    defender.status.yawning = True
    return []
# This move has a 10% chance to paralyze the target.
def move_54():
    res = effect_0()
    if random.randrange(100) < 10:
        res += get_paralyze_events()
    return res
# This move prevents the target from moving.
def move_55():
    defender.status.shadow_hold = True
    return []
# The target suffers 9,999 damage (essentially a one-hit KO), though if immune to the move type it's 0. Used by Horn Drill.
def move_56():
    return effect_12()
# This move confuses the target.
def move_57():
    return get_confusion_events()
# This move poisons the target.
def move_58():
    return get_poisoned_events()
# This move paralyzes the target.
def move_59():
    return get_paralyze_events()
# This move paralyzes the target.
def move_60():
    return get_paralyze_events()
# This move deals damage and paralyzes the target.
def move_61():
    res = effect_0()
    res += get_paralyze_events()
    return res
# If this move hits, then the user's Attack and Defense are lowered by one stage.
def move_62():
    res = effect_0()
    res += get_stat_change_events(attacker, "attack", -1)
    res += get_stat_change_events(attacker, "defense", -1)
    return res
# If this move hits, then the target's movement speed is lower by one stage.
def move_63():
    res = effect_0()
    res += get_stat_change_events(defender, "speed", -1)
    return res
# If this move hits, then the target is confused.
def move_64():
    res = effect_0()
    res += get_confusion_events()
    return res
# If this move hits, then the target's Sp. Def. is lowered by two stages.
def move_65():
    res = effect_0()
    res += get_stat_change_events(defender, "sp_defense", -2)
    return res
# The target is throw 10 spaces in a random direction or until it hits a wall, losing 5 HP in the latter case. Fails on boss floors with cliffs.
def move_66():
    return []
# The user's and target's current HP are adjusted to become the average of the two, possibly raising or lowering.
def move_67():
    return []
# This move raises the user's Sp. Atk. by two stages.
def move_68():
    return get_stat_change_events(attacker, "sp_attack", 2)
# This move raises the user's Evasion by one stage,
def move_69():
    return get_stat_change_events(attacker, "evasion", 1)
# This move raises the user's Attack and movement speed by one stage each.
def move_70():
    res = []
    res += get_stat_change_events(attacker, "attack", 1)
    res += get_stat_change_events(attacker, "speed", 1)
    return res
# This move raises the user's Attack and Defense by one stage each.
def move_71():
    res = []
    res += get_stat_change_events(attacker, "attack", 1)
    res += get_stat_change_events(attacker, "defense", 1)
    return res
# This move raises the user's Attack by one stage.
def move_72():
    return get_stat_change_events(attacker, "attack", 1)
# The user of this move becomes enraged.
def move_73():
    attacker.status.enraged = True
    return []
# This move raises the user's Attack by two stages.
def move_74():
    get_stat_change_events(attacker, "attack", 2)
# This move raises the user's Sp. Atk. and Sp. Def. by one stage.
def move_75():
    res = []
    res += get_stat_change_events(attacker, "sp_attack", 1)
    res += get_stat_change_events(attacker, "sp_defense", 1)
    return res
# This move raises the user's Sp. Atk. by one stage.
def move_76():
    return get_stat_change_events(attacker, "sp_attack", 1)
# This move raises the user's Sp. Def. by two stages.
def move_77():
    return get_stat_change_events(attacker, "sp_defense", 1)
# This move raises the user's Defense by one stage,
def move_78():
    return get_stat_change_events(attacker, "defense", 1)
# This move raises the user's Defense by two stages.
def move_79():
    return get_stat_change_events(attacker, "defense", 2)
# This move raises the user's Defense and Sp. Def. by one stage.
def move_80():
    res = []
    res += get_stat_change_events(attacker, "defense", 1)
    res += get_stat_change_events(attacker, "sp_defense", 1)
    return res
# This move has a 40% chance to lower the target's accuracy by one stage.
def move_81():
    res = effect_0()
    if random.randrange(0, 100) < 40:
        res += get_stat_change_events(defender, "accuracy", -1)
    return res
# This move has a 60% chance to lower the target's accuracy by one stage.
def move_82():
    res = effect_0()
    if random.randrange(0, 100) < 60:
        res += get_stat_change_events(defender, "accuracy", -1)
    return res
# This move has a 60% chance to halve the target's Attack multiplier, with a minimum of 2 / 256.
def move_83():
    res = effect_0()
    if random.randrange(0, 100) < 60:
        res += get_stat_change_events(defender, "attack_divider", 1)
    return res
# If this move hits the target, the target's Sp. Atk. is reduced by two stages.
def move_84():
    res = effect_0()
    res += get_stat_change_events(defender, "sp_attack", -2)
    return res
# This move lower's the target's movement speed.
def move_85():
    return get_stat_change_events(defender, "speed", -1)
# This move lowers the target's Attack by one stage.
def move_86():
    return get_stat_change_events(defender, "attack", -1)
# This move lower's the target's Attack by two stages.
def move_87():
    return get_stat_change_events(defender, "attack", -2)
# This move reduces the target's Defense multiplier to 1/4 of its current value, but no less than 2 / 256.
def move_88():
    return get_stat_change_events(defender, "defense_divider", 2)
# This move reduces the target's HP by an amount equal to the user's level.
def move_89():
    return get_damage_events(attacker.level)
# The user will regain HP equal to 50% of the damage dealt.
def move_90():
    damage = damage_mechanics.calculate_damage(dungeon, attacker, defender, current_move)
    heal = int(damage * 0.5)
    res = get_damage_events(damage)
    res += get_heal_events(attacker, heal)
    return res
# The user suffers damage equal to 12.5% of their maximum HP. (Used only for Double-Edge for some reason.)
def move_91():
    res = effect_0()
    res += get_recoil_events(12.5)
    return res
# The user suffers damage equal to 12.5% of their maximum HP.
def move_92():
    return effect_91()
# The user will regain HP equal to 50% of the damage dealt. (Used only for Absorb for some reason.)
def move_93():
    return effect_90()
# The target becomes confused but their Attack is boosted by two stages.
def move_94():
    res = get_confusion_events()
    res += get_stat_change_events(defender, "attack", 2)
    return res
# When used, this move's damage increments with each hit.
def move_95():
    return []
# The user of this move attacks twice in a row. Each hit has a 20% chance to poison the target (36% chance overall to poison).
def move_96():
    res = []
    for i in range(2):
        res += effect_0()
        if random.randrange(0, 100) < 20:
            res += get_poisoned_events()
    return res
# SolarBeam's effect. The user charges up for one turn before attacking, or uses it instantly in Sun. If it is Hailing, Rainy, or Sandstorming, damage is halved (24 power).
def move_97():
    return []
# Sky Attack's effect. The user charges up for a turn before attacking. Damage is doubled at the end of calculation.
def move_98():
    return []
# This move lowers the target's movement speed by one stage. (This is simply used for the placeholder move Slow Down, for the generic effect.)
def move_99():
    return get_stat_change_events(defender, "speed", -1)
# The user attacks 2-5 turns in a row, becoming confused at the end of it.
def move_100():
    return []
# The user and target are immobilized for 3 to 5 turns while the target suffers damage from it.
def move_101():
    return []
# If the target of this move is asleep, they are awakened.
def move_102():
    return []
# This move has a 30% chance to badly poison the target.
def move_103():
    if random.randrange(0, 100) < 30:
        return get_badly_poisoned_events()
    else:
        return []
# At random, one of the following occur: target recovers 25% HP (20%), target takes 40 damage (40%), target takes 80 damage (30%), or target takes 120 damage (10%).
def move_104():
    choice = random.choices(range(4), [20, 40, 30, 10], k=1)[0]
    if choice == 0:
        return get_heal_events(defender, defender.hp // 4)
    elif choice == 1:
        return get_damage_events(40)
    elif choice == 2:
        return get_damage_events(80)
    elif choice == 3:
        return get_damage_events(120)
# The user falls under the effects of Reflect.
def move_105():
    attacker.status.reflect = True
    return []
# The floor's weather becomes Sandstorm.
def move_106():
    return []
# The user's allies gain the Safeguard status.
def move_107():
    defender.status.safeguard = True
    return []
# The Mist status envelopes the user.
def move_108():
    attacker.status.mist = True
    return []
# The user falls under the effects of Light Screen.
def move_109():
    attacker.status.light_screen = True
    return []
# The user attacks five times. If an attack misses, the attack ends. When used the damage increments by a factor of x1.5 with each hit.
def move_110():
    return []
# Reduces the targets' Attack and Sp. Atk. multipliers to 1/4 of their current value, 2 / 256 at minimum. User is reduced to 1 HP and warps at random. Fails if no target.
def move_111():
    return []
# The target regains HP equal to 1/4 of their maximum HP.
def move_112():
    return []
# User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
def move_113():
    return []
# User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
def move_114():
    return []
# User falls asleep, recovers their HP, and recovers their status.
def move_115():
    return []
# The user regains HP equal to 1/2 of their maximum HP.
def move_116():
    return get_heal_events(attacker, attacker.hp // 2)
# Scans the area.
def move_117():
    return []
# The user and the target swap hold items. This move fails if the user lacks one or if the target does.
def move_118():
    return []
# If this move damages the target, the user steals the target's hold item if the user lacks one and the target has one.
def move_119():
    return []
# If this move damages the target, the user steals the target's hold item if the user lacks one and the target has one.
def move_120():
    return []
# This move raises the movement speed of all targets.
def move_121():
    return get_stat_change_events(defender, "speed", 1)
# The user gains the Counter status.
def move_122():
    return []
# The user gains the Bide status.
def move_123():
    return []
# This flag is for the attack released at the end of Bide, reducing the target's HP by two times the damage intake. No valid move used this flag.
def move_124():
    return []
# Creates a random trap based on the floor.
def move_125():
    return []
# When attacked while knowing this move and asleep, the user faces their attack and uses a move at random. Ignores Confused/Cowering and links. Overriden by Snore.
def move_126():
    return []
# If user is a Ghost type: user's HP is halved, and target is cursed. If user isn't a Ghost-type: the user's Attack and Defense are boosted by one stage while speed lowers.
def move_127():
    return []
# This move has doubled damage. If the move misses, the user receives half of the intended damage, at minimum 1.
def move_128():
    return []
# This move has doubled damage. If the move hits, the user becomes Paused at the end of the turn.
def move_129():
    return []
# This move has a variable power and type.
def move_130():
    return []
# The user charges up for Razor Wind, using it on the next turn. Damage is doubled.
def move_131():
    return []
# User charges up for a Focus Punch, using it on the next turn. Damage is doubled.
def move_132():
    return []
# The user gains the Magic Coat status.
def move_133():
    return []
# The target gains the Nightmare status.
def move_134():
    return []
# User recovers a portion of their HP relative to the weather: 50 HP in Clear, 80 HP in Sun, 30 HP in Sandstorm, 40 HP if Cloudy, 10 HP in Rain and Hail, 1 HP in Snow.
def move_135():
    return []
# This move deals exactly 35 damage. This move is Vacuum-Cut.
def move_136():
    return []
# The floor gains the Mud Sport or Water Sport status. The former weakens Electric moves, and the latter weakens Fire.
def move_137():
    if current_move.name == "Water Sport":
            floor.status.water_sport.value = floor.status.water_sport.max_value
    elif current_move.name == "Mud Sport":
        floor.status.mud_sport.value = floor.status.mud_sport.max_value
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(text.PALE_YELLOW)
        .write(current_move.name)
        .set_color(text.WHITE)
        .write(" came into effect!")
        .build()
        .render()
    )
    return [gameevent.LogEvent(text_surface).with_divider()]
# This move has a 30% chance to lower the target's Defense by one stage.
def move_138():
    if random.randrange(0, 100) < 30:
        return get_stat_change_events(defender, "defense", -1)
    else:
        return []
# This move will lower the target's Defense by one stage.
def move_139():
    return get_stat_change_events(defender, "defense", -1)
# This move will burn the target.
def move_140():
    return get_burn_events()
# This move gives the target the Ingrain status.
def move_141():
    return []
# This move deals random damage between 128/256 to 383/256 of the user's Level. (Approximately: 0.5 to 1.5 times the user's Level.) Limited to the range of 1-199.
def move_142():
    return []
# The target gains the Leech Seed status. Fails on Grass-types.
def move_143():
    return []
# A Spikes trap appears beneath the user.
def move_144():
    return []
# All of the target's/targets' status ailments are cured.
def move_145():
    return []
# All targets have their stat stages and multipliers returned to normal levels. This neither considered a reduction or increment in stats for anything relevant to it.
def move_146():
    return []
# The user gains the Power Ears status.
def move_147():
    return []
# The targets are put to sleep.
def move_148():
    return []
# If the target is paralyzed, the damage from this attack doubles, but the target is cured of their paralysis as well.
def move_149():
    return []
# This move deals fixed damage (5, 10, 15, 20, 25, 30, 35, or 40, for Magnitudes 4 to 10 respectively). The damage doubles on a target who is Digging.
def move_150():
    return []
# The user gains the Skull Bash status: their Defense boosts for a turn as they charge for an attack on the next turn. Damage is doubled.
def move_151():
    return []
# The user gains the Wish status.
def move_152():
    return []
# The target's Sp. Atk. is raised one stage, but they also become confused.
def move_153():
    res = []
    res += get_stat_change_events(defender, "sp_attack", 1)
    res += get_confusion_events()
    return res
# This move will lower the target's Accuracy by one stage.
def move_154():
    return get_stat_change_events(defender, "accuracy", -1)
# This move will lower the target's Accuracy by one stage.
def move_155():
    return effect_154()
# This move will lower the user's Sp. Atk. by two stages if it hits the target.
def move_156():
    return get_stat_change_events(attacker, "sp_attack", -2)
# This move will badly poison the target.
def move_157():
    return get_badly_poisoned_events()
# This move lowers the target's Sp. Def. by three stages.
def move_158():
    return get_stat_change_events(defender, "sp_defense", -3)
# This move disables the last move the target used. It is not considered sealed however.
def move_159():
    return []
# Reduces the target's HP by half, rounded down, but it cannot KO the target.
def move_160():
    return []
# This move damage the target, but it cannot KO the target. If it would normally KO the target they are left with 1 HP.
def move_161():
    return []
# This reduces all targets' HP to 1. For each target affected, the user's HP is halved, but cannot go lower than 1.
def move_162():
    return []
# The target's HP becomes equal to that of the user's, provided the user has lower HP. Ineffective otherwise.
def move_163():
    return []
# All targets switch position with the user.
def move_164():
    return []
# The user regains HP equal to half of the damage dealt, rounded down. If the target is not asleep, napping, or having a nightmare, the move fails.
def move_165():
    return []
# The layout of the map - including stairs, items, and Pokemon - are revealed. Visibility is cleared, though its range limitations remain.
def move_166():
    return []
# If the floor in front of the user is water or lava, it becomes a normal floor tile.
def move_167():
    return []
# All targets warp randomly.
def move_168():
    return []
# All water and lava tiles turn into normal floor tiles.
def move_169():
    return []
# You become able to see the location of the stairs on the map.
def move_170():
    return []
# This move removes the effects of Light Screen and Reflect the target.
def move_171():
    return []
# This move raises the user's Defense by one stage.
def move_172():
    return get_stat_change_events(attacker, "defense", 1)
# The user gains the Sure Shot status, assuring that their next move will land.
def move_173():
    return []
# The user gains the Vital Throw status.
def move_174():
    return []
# The user begins to Fly, waiting for an attack on the next turn. Damage is doubled.
def move_175():
    return []
# The user Bounces, and attacks on the next turn. Damage is doubled. This move has a 30% chance to paralyze the target.
def move_176():
    return []
# The user begins to Dive, waiting for an attack on the next turn. Damage is doubled. Move fails if the user is not on a water tile.
def move_177():
    return []
# The user begins to Dig, waiting for an attack on the next turn. Damage is doubled. Move fails if the user is not on a land tile.
def move_178():
    return []
# This move lowers the targets' Evasion by one stage.
def move_179():
    return get_stat_change_events(defender, "evasion", -1)
# This move raises the user's Evasion by one stage,
def move_180():
    return get_stat_change_events(attacker, "evasion", 1)
# This move forces the target to drop its hold item onto the ground.
def move_181():
    return []
# This removes all traps in the room, excepting Wonder Tiles. This will not work during boss battles.
def move_182():
    return []
# This gives the user the Long Toss status.
def move_183():
    return []
# This gives the user the Pierce status.
def move_184():
    return []
# This gives the user the Grudge status.
def move_185():
    return []
# This Petrifies the targets indefinitely until attacked.
def move_186():
    return []
# This move's use will cause the user to use a move known by a random Pokemon on the floor. If Assist is chosen, this move fails.
def move_187():
    return []
# This enables the Set Damage status on the target, fixing their damage output.
def move_188():
    return []
# This will cause the target to Cower.
def move_189():
    return []
# This move turns the target of it into a decoy.
def move_190():
    return []
# If this move misses, the user receives half of the damage it would've normally dealt to the target, at minimum 1.
def move_191():
    return []
# This enables the Protect status on the target.
def move_192():
    return []
# The target becomes Taunted.
def move_193():
    return []
# The target's Attack and Defense become lowered by one stage.
def move_194():
    res = []
    res += get_stat_change_events(defender, "attack", -1)
    res += get_stat_change_events(defender, "defense", -1)
    return res
# The damage multiplier depends on user HP. 0-25% is 8x, 25-50% is 4x, 50-75% is 2x, 75-100% is 1x.
def move_195():
    return []
# This move will cause a small explosion.
def move_196():
    return []
# This move will cause a huge explosion.
def move_197():
    return []
# This move causes the user to gain the Charging status.
def move_198():
    return []
# This move' s damage doubles if the user is Burned, Poisoned, Badly Poisoned, or Paralyzed.
def move_199():
    return []
# The damage for this move (Low Kick) is dependent on the target's species.
def move_200():
    return []
# The damage multiplier depends on user HP. 0-25% is 25/256, 25%-50% is 51/256, 50-75% is 128/256, 75-100% is 256/256 (or just x1).
def move_201():
    return []
# The damage multiplier depends on user HP. 0-25% is 25/256, 25%-50% is 51/256, 50-75% is 128/256, 75-100% is 256/256 (or just x1).
def move_202():
    return []
# The target of this move obtains the Whiffer status.
def move_203():
    return []
# This permits the target to sell as traps in the same room. They also will not be triggered.
def move_204():
    return []
# The user stores power, up to three total times.
def move_205():
    return []
# The damage of this move is multiplied by the number of times the user had used Stockpile (0, 1, 2, or 3). Only if this move hits does the Stockpile counter zero out.
def move_206():
    return []
# The user recovers HP based on the number of times they've Stockpiled (0 = 0 HP, 1 = 20 HP, 2 = 40 HP, 3 = 80 HP). The Stockpile counter resets to zero after.
def move_207():
    return []
# The weather becomes Rain.
def move_208():
    return []
# The PP of the last move used by the target is set to zero.
def move_209():
    return []
# The user becomes Invisible.
def move_210():
    return []
# The user gains the Mirror Coat status.
def move_211():
    return []
# The targets gain the Perish Song status.
def move_212():
    return []
# This move removes all traps nearby.
def move_213():
    return []
# The user gains Destiny Bond status with respect to the target of this move.
def move_214():
    return []
# The target gains the Encore status, affecting their last move used. Fails if the target is either the team leader or if they haven't used a move on this floor.
def move_215():
    return []
# If the current weather is not Clear/Cloudy, damage doubles. If Sunny, this move is Fire type; Fog or Rain, Water; Sandstorm, Rock; Hail or Snow, Ice.
def move_216():
    return []
# The weather becomes Sunny.
def move_217():
    return []
# If this move defeats the target and doesn't join your team, the target drops money.
def move_218():
    return []
# One-Room the entirety of the room becomes regular floor tiles and the room a single room. Doesn't work on boss floors.
def move_219():
    return []
# The user gains the Enduring status.
def move_220():
    return []
# This move raises the Attack and Sp. Atk. of all targets by one stage, excepting the user of the move.
def move_221():
    res = []
    res += get_stat_change_events(defender, "attack", 1)
    res += get_stat_change_events(defender, "sp_attack", 1)
    return res
# This move raises the user's Attack by 20 stages, but lowers the user's Belly to 1 point. Fails if the user has 1 Belly or less.
def move_222():
    return []
# This move lowers the targets' Bellies by 10.
def move_223():
    return []
# This move lowers the target's Attack by two stages.
def move_224():
    return get_stat_change_events(defender, "attack", -2)
# This move has a 30% chance to lower the target's movement speed by one stage.
def move_225():
    if random.randrange(0, 100) < 30:
        return get_stat_change_events(defender, "speed", -1)
    else:
        return []
# This move will lower the target's movement speed by one stage.
def move_226():
    return get_stat_change_events(defender, "speed", -1)
# The wall tile the user is currently facing becomes replaced with a normal floor tile. Does not work on diagonal facings.
def move_227():
    return []
# The user transforms into a random Pokemon species on the dungeon floor that can appear. Fails if the user already has transformed.
def move_228():
    return []
# This move changes the weather on the floor to Hail.
def move_229():
    return []
# This enables the Mobile status on the user.
def move_230():
    return []
# This move lowers the targets' Evasion stage to 10 if it is any higher than that. Further, Ghost types become able to be hit by Normal and Fighting moves.
def move_231():
    return []
# The user will move one space in a random direction, neglecting towards a wall. If it lands on a Pokemon, both will lose 5 HP and return to their positions. If it lands on a space it cannot enter normally, it warps. This move's movement will not induce traps to be triggered. Finally, the move can be used even when Hungry.
def move_232():
    return []
# The user and target swap positions.
def move_233():
    return []
# The target of the move warps, landing on the stairs, becoming Petrified indefinitely until attacked.
def move_234():
    return []
# The allies of the user of this move warp, landing on the user.
def move_235():
    return []
# The move's user gains the Mini Counter status.
def move_236():
    return []
# This move's target becomes Paused.
def move_237():
    return []
# The user's allies warp to the user and land on them.
def move_238():
    return []
# This move has no effect. Associated with the Reviver Orb which was reduced to have no power and dummied out in development.
def move_239():
    return []
# The team leader and their allies escape from the dungeon, and if used in a linked move - somehow - the moves stop being used.
def move_240():
    return []
# This move causes special effects depending on the terrain, with 30% probability.
def move_241():
    return []
# This move will cause a special effect depending on the terrain.
def move_242():
    return []
# The target of the move transforms into an item. They will not drop any hold items, and the defeater of the Pokemon will not gain any experience.
def move_243():
    return []
# This move transforms into the last move used by the target of the move permanently.
def move_244():
    return []
# The user acquires the Mirror Move status.
def move_245():
    return []
# The user of this move gains the target's Abilities. This will fail if the user were to gain Wonder Guard.
def move_246():
    return []
# The user and the target of this move will swap their Abilities. If either party has Wonder Guard as an Ability, the move fails.
def move_247():
    return []
# The user's type changes to that of one of their moves at random, regardless of the move's type. Weather Ball is considered to be Normal. Fails if the user has the Forecast Ability.
def move_248():
    return []
# All items held by the user and their allies are no longer sticky. For members of rescue teams, this includes all items on their person in the bag.
def move_249():
    return []
# The target loses HP based on the user's IQ.
def move_250():
    return []
# The target obtains the Snatch status; to prevent conflicts, all others with the Snatch status at this time will lose it.
def move_251():
    return []
# The user will change types based on the terrain.
def move_252():
    return []
# The target loses HP based on the user's IQ.
def move_253():
    return []
# The user of this move copies the stat changes on the target.
def move_254():
    return []
# Whenever at an attack hits the user, if this move is known and the user asleep, the user will face the attack and use this move. 30% to cause cringing. Ignores Confusion and Cowering and linked moves.
def move_255():
    return []
# If this move is used by a member of a rescue team, all items named "Used TM" are restored to their original usable state. Also unstickies them.
def move_256():
    return []
# The target of this move becomes muzzled.
def move_257():
    return []
# This move once used will cause the user to follow up with a random second attack.
def move_258():
    return []
# The targets of this move can identify which Pokemon in the floor are holding items and thus will drop them if defeated (or other applicable instances).
def move_259():
    return []
# The user gains the Conversion 2 status. Fails of the user has the Forecast ability.
def move_260():
    return []
# The user of the move moves as far as possible in their direction of facing, stopping at a wall or Pokemon. Fails on floors with cliffs.
def move_261():
    return []
# All unclaimed items on the floor, excepting those within two tiles of the user, land on the user's position, provided there is space around the user.
def move_262():
    return []
# The user of this move uses the last move used by the target, excepting Assist, Mimic, Encore, Mirror Move, and Sketch, or if the target is charging for an attack.
def move_263():
    return []
# The target is thrown onto a random space the target can enter within the room's range from the perspective of the user, and takes a random facing. If a foe is in the room, they are thrown to them instead, and both lose 10 HP.
def move_264():
    return []
# The target loses HP dependent on their species.
def move_265():
    return []
# One of an ally's stats is raised by two stages at random.
def move_266():
    all_stats = ["attack", "defense", "sp_attack", "sp_defense", "speed", "evasion", "accuracy"]
    possible_stats = []
    for stat in all_stats:
        stat_obj: pokemondata.Statistic = getattr(defender.status, stat)
        if stat_obj.value < stat_obj.max_value:
            possible_stats.append(stat)
    if possible_stats:
        return get_stat_change_events(defender, random.choice(possible_stats), 2)
    else:
        return []
# The user obtains the Aqua Ring status.
def move_267():
    return []
# The damage for this move doubles if the user were attacked on the previous turn.
def move_268():
    return []
# If the user is under 50% HP, then the damage from this move is doubled.
def move_269():
    return []
# If the target is holding a Berry or has one in their bag or the like, then the user of this move ingests it and uses its effects.
def move_270():
    return []
# This move has a 70% chance to raise the user's Sp. Atk. by one stage.
def move_271():
    if random.randrange(0, 100) < 70:
        return get_stat_change_events(attacker, "sp_attack", 1)
    else:
        return []
# This move will confuse the target.
def move_272():
    return []
# If this move hits, the user's Defense and Sp. Def. will be lowered by one stage each.
def move_273():
    res = []
    res += get_stat_change_events(attacker, "defense", -1)
    res += get_stat_change_events(attacker, "sp_defense", -1)
    return res
# This move will deal more damage to foes with higher HP.
def move_274():
    return []
# This move has a 60% chance to cause the targets to fall asleep.
def move_275():
    return []
# This move clears the weather for the floor.
def move_276():
    return []
# This move hits the foe twice.
def move_277():
    return []
# The target cannot use items, nor will their items bear any effect if held.
def move_278():
    return []
# This move ignores Protect status.
def move_279():
    return []
# This move has a 10% to cause the foe to cringe, and a 10% chance to cause a burn.
def move_280():
    res = []
    if random.randrange(0, 100) < 10:
        res += get_cringe_events()
    if random.randrange(0, 100) < 10:
        res += get_burn_events()
    return res
# This move throws an item at the target.
def move_281():
    return []
# This move has a 30% chance to paralyze.
def move_282():
    if random.randrange(0, 100) < 30:
        return get_paralyze_events()
    else:
        return []
# This move grants the Gastro Acid ability to the target, negating their abilities.
def move_283():
    return []
# This move's damage increments with higher weight on the target.
def move_284():
    return []
# The floor falls under the Gravity state: Flying Pokemon can be hit by Ground moves, and Levitate is negated.
def move_285():
    return []
# The foe and the user swap stat changes to their Defense and Sp. Def. stats.
def move_286():
    return []
# This move has a 30% chance to poison the target.
def move_287():
    if random.randrange(0, 100) < 30:
        return get_poisoned_events()
    else:
        return []
# This move deals double damage to targets with halved movement speed.
def move_288():
    return []
# After using this move, the user has its movement speed reduced.
def move_289():
    return get_stat_change_events(attacker, "speed", -1)
# Grants all enemies in the user's room the Heal Block ailment, preventing healing of HP.
def move_290():
    return []
# The user recovers 50% of their maximum HP.
def move_291():
    return []
# The health of all targets and their status ailments are cured. However, the user of this move will also have their HP dropped to just 1.
def move_292():
    return []
# The user and the target swap stat modifications for their Attack and Defense.
def move_293():
    return []
# This move has a 10% to cause the foe to cringe, and a 10% chance to cause freezing.
def move_294():
    res = []
    if random.randrange(0, 100) < 10:
        return get_cringe_events()
    if random.randrange(0, 100) < 10:
        return get_freeze_events()
    return res
# This move will inflict damage on the target, but only if the user has a move with 0 PP. Damage rises as more moves have 0 PP.
def move_295():
    return []
# This move has a 30% chance to burn the target.
def move_296():
    if random.randrange(0, 100) < 30:
        return get_burn_events()
    else:
        return []
# This move grants the Lucky Chant status to the targets, preventing critical hits.
def move_297():
    return []
# This move heals all the HP and PP of the targets and all their ailments as well. However as a cost the user returns to 1 HP.
def move_298():
    return []
# The user of this move gains the Magnet Rise status, gaining immunity to Ground moves.
def move_299():
    return []
# The user is granted the Metal Burst status.
def move_300():
    return []
# If the target has an evasion level above 10 stages, it becomes 10 stages. They are either way granted Miracle Eye status, permitting Psychic moves to hit Dark types.
def move_301():
    return []
# This move has a 30% chance to lower the target's accuracy.
def move_302():
    if random.randrange(100) < 30:
        return get_stat_change_events(defender, "accuracy", -1)
    else:
        return []
# The user's Sp. Atk. is boosted by two stages.
def move_303():
    return get_stat_change_events(attacker, "sp_attack", 2)
# This move's damage as well as type will change depending on the Berry the user holds, if any.
def move_304():
    return []
# The user and the target will swap modifications to their Attack and Sp. Atk. stats.
def move_305():
    return []
# The user swaps their Attack and Defense stat modifiers.
def move_306():
    return []
# The user transfers their status problems to the target of this move, while simultaneously curing their own.
def move_307():
    return []
# This move increments power further if the target has boosted Attack, Defense, Sp. Atk., and/or Sp. Def., and more for every stage boosted.
def move_308():
    return []
# This move has a 20% chance to confuse the target.
def move_309():
    return []
# Targets of this move have their movement speed raised by two stages.
def move_310():
    return get_stat_change_events(defender, "speed", 2)
# This move's user gains 50% of their maximum HP. In return however, they will lose any Flying-type designations until their next turn.
def move_311():
    return []
# This move has a 40% chance to lower the targets' Sp. Atk. by two stages.
def move_312():
    if random.randrange(0, 100) < 40:
        return get_stat_change_events(defender, "sp_attack", -2)
    else:
        return []
# The user gains the Shadow Force status: they become untouchable for a single turn, attacking on the next turn. This move deals double damage. This move defies Protect status. This move cannot be linked.
def move_313():
    return []
# The user of the move creates a Stealth Rock trap underneath their feet.
def move_314():
    return []
# This move has a 10% chance to make the target cringe, and a 10% chance to paralyze them too.
def move_315():
    res = []
    if random.randrange(0, 100) < 10:
        return get_cringe_events()
    if random.randrange(0, 100) < 10:
        return get_paralyze_events()
    return res
# This move places a Toxic Spikes trap under the user's feet.
def move_316():
    return []
# This move at random increases or lowers the movement speed of all targets by one stage.
def move_317():
    return get_stat_change_events(defender, "speed", random.choice([-1, 1]))
# This move will deal more damage the lower its current PP.
def move_318():
    return []
# This move will awaken a target affected by the Napping, Sleep, or Nightmare statuses, but if the target has one of these the move will also do double damage.
def move_319():
    return []
# This move if it hits will inflict the target with the Sleepless status. It will fail on Pokemon with the Truant Ability.
def move_320():
    return []
"""

dispatcher = {i: globals().get(f"move_{i}", move_0) for i in range(321)}


def get_events_from_move(ev: game_event.BattleSystemEvent):
    # print(move.move_id)
    return dispatcher.get(ev.move.move_id, dispatcher[0])(ev)
