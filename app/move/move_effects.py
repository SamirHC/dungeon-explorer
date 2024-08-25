from app.common.constants import RNG as random

from app.common import utils
from app.common.direction import Direction
import app.move.move_effect_helpers as eff
from app.events import event, game_event
from app.pokemon.pokemon import Pokemon
from app.pokemon.stat import Stat
from app.pokemon.status_effect import StatusEffect
from app.pokemon.animation_id import AnimationId
from app.move import damage_mechanics
from app.gui import text
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
            .write(defender.base.name)
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
        events.append(game_event.LogEvent(tb.build()))
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
            .write(defender.base.name)
            .set_color(text.WHITE)
        )
        if not defender.status.has_status_effect(StatusEffect.NIGHTMARE):
            # Overrides any other sleep status conditions
            defender.status.clear_affliction(StatusEffect.ASLEEP)
            defender.status.clear_affliction(StatusEffect.NAPPING)
            defender.status.clear_affliction(StatusEffect.YAWNING)
            defender.status.afflict(
                StatusEffect.NIGHTMARE,
                ev.dungeon.turns.value + random.randint(4, 7),
            )
            tb.write(" is caught in a nightmare!")
        else:
            tb.write(" is already having a nightmare!")

        events = []
        events.append(game_event.SetAnimationEvent(defender, AnimationId.SLEEP, True))
        events.append(game_event.LogEvent(tb.build()))
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


# Vital Throw
def move_7(ev: game_event.BattleSystemEvent):
    def _vital_throw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.base.name)
            .set_color(text.WHITE)
        )
        if defender.status.has_status_effect(StatusEffect.VITAL_THROW):
            tb.write(" is already ready with its\nVital Throw!")
        else:
            tb.write(" readied its Vital Throw!")
            defender.status.afflict(
                StatusEffect.VITAL_THROW, ev.dungeon.turns.value + 18
            )

        events = []
        events.append(game_event.LogEvent(tb.build()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _vital_throw_effect)
    return events


# Dig
def move_8(ev: game_event.BattleSystemEvent):
    def _dig_effect(ev: game_event.BattleSystemEvent):
        tb = text.TextBuilder().set_shadow(True)
        if ev.dungeon.tileset.underwater:
            tb.set_color(text.WHITE).write(" It can only be used on the ground!")
        else:
            (
                tb.set_shadow(True)
                .set_color(ev.attacker.name_color)
                .write(ev.attacker.base.name)
                .set_color(text.WHITE)
                .write(" burrowed underground!")
            )
            ev.attacker.status.afflict(StatusEffect.DIGGING, ev.dungeon.turns.value + 1)

        events = []
        events.append(game_event.LogEvent(tb.build()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += _dig_effect(ev)
    return events


# Thrash
def move_9(ev: game_event.BattleSystemEvent):
    def _thrash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    if not ev.kwargs:
        ev.kwargs["direction"] = ev.attacker.direction
        ev.kwargs["iterations"] = 0

    events = []
    if ev.kwargs["iterations"] < 3:
        ev.kwargs["iterations"] += 1
        ev.attacker.direction = random.choice(list(Direction))
        events += eff.get_attacker_move_animation_events(ev)
        events += eff.get_events_on_all_targets(ev, _thrash_effect)
        events.append(ev)
    else:
        ev.attacker.direction = ev.kwargs["direction"]
        events.append(event.SleepEvent(20))

    return events


# Sweet Scent
def move_10(ev: game_event.BattleSystemEvent):
    def _sweet_scent_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return [game_event.StatStageChangeEvent(defender, Stat.EVASION, -1)]

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _sweet_scent_effect)
    return events


# Charm
def move_11(ev: game_event.BattleSystemEvent):
    def _charm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return [game_event.StatDivideEvent(defender, Stat.ATTACK, 1)]

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _charm_effect)
    return events


# Rain Dance
def move_12(ev: game_event.BattleSystemEvent):
    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events.append(game_event.SetWeatherEvent(Weather.RAINY))
    return events


# Confuse Ray
def move_13(ev: game_event.BattleSystemEvent):
    def _confuse_ray_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        defender.status.afflict(
            StatusEffect.CONFUSED,
            ev.dungeon.turns.value + random.randint(7, 12),
        )
        return eff.get_confusion_events(defender)

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _confuse_ray_effect)
    return events


# Hail
def move_14(ev: game_event.BattleSystemEvent):
    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events.append(game_event.SetWeatherEvent(Weather.HAIL))
    return events


# Aromatherapy
def move_15(ev: game_event.BattleSystemEvent):
    def _aromatherapy_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aromatherapy_effect))
    return events


# Bubble
def move_16(ev: game_event.BattleSystemEvent):
    def _bubble_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bubble_effect))
    return events


# Encore
def move_17(ev: game_event.BattleSystemEvent):
    def _encore_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _encore_effect))
    return events


# Cut
def move_18(ev: game_event.BattleSystemEvent):
    def _cut_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _cut_effect))
    return events


# Rage
def move_19(ev: game_event.BattleSystemEvent):
    def _rage_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rage_effect))
    return events


# Super Fang
def move_20(ev: game_event.BattleSystemEvent):
    def _super_fang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _super_fang_effect))
    return events


# Pain Split
def move_21(ev: game_event.BattleSystemEvent):
    def _pain_split_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _pain_split_effect))
    return events


# Torment
def move_22(ev: game_event.BattleSystemEvent):
    def _torment_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _torment_effect))
    return events


# String Shot
def move_23(ev: game_event.BattleSystemEvent):
    def _string_shot_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _string_shot_effect))
    return events


# Swagger
def move_24(ev: game_event.BattleSystemEvent):
    def _swagger_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _swagger_effect))
    return events


# Snore
def move_25(ev: game_event.BattleSystemEvent):
    def _snore_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _snore_effect))
    return events


# Heal Bell
def move_26(ev: game_event.BattleSystemEvent):
    def _heal_bell_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _heal_bell_effect))
    return events


# Screech
def move_27(ev: game_event.BattleSystemEvent):
    def _screech_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _screech_effect))
    return events


# Rock Throw
def move_28(ev: game_event.BattleSystemEvent):
    def _rock_throw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_throw_effect))
    return events


# Rock Smash
def move_29(ev: game_event.BattleSystemEvent):
    def _rock_smash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_smash_effect))
    return events


# Rock Slide
def move_30(ev: game_event.BattleSystemEvent):
    def _rock_slide_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_slide_effect))
    return events


# Weather Ball
def move_31(ev: game_event.BattleSystemEvent):
    def _weather_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _weather_ball_effect))
    return events


# Whirlpool
def move_32(ev: game_event.BattleSystemEvent):
    def _whirlpool_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _whirlpool_effect))
    return events


# Fake Tears
def move_33(ev: game_event.BattleSystemEvent):
    def _fake_tears_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fake_tears_effect))
    return events


# Sing
def move_34(ev: game_event.BattleSystemEvent):
    def _sing_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sing_effect))
    return events


# Spite
def move_35(ev: game_event.BattleSystemEvent):
    def _spite_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spite_effect))
    return events


# Air Cutter
def move_36(ev: game_event.BattleSystemEvent):
    def _air_cutter_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _air_cutter_effect))
    return events


# SmokeScreen
def move_37(ev: game_event.BattleSystemEvent):
    def _smokescreen_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _smokescreen_effect))
    return events


# Pursuit
def move_38(ev: game_event.BattleSystemEvent):
    def _pursuit_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _pursuit_effect))
    return events


# DoubleSlap
def move_39(ev: game_event.BattleSystemEvent):
    def _doubleslap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _doubleslap_effect))
    return events


# Mirror Move
def move_40(ev: game_event.BattleSystemEvent):
    def _mirror_move_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mirror_move_effect))
    return events


# Overheat
def move_41(ev: game_event.BattleSystemEvent):
    def _overheat_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _overheat_effect))
    return events


# Aurora Beam
def move_42(ev: game_event.BattleSystemEvent):
    def _aurora_beam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aurora_beam_effect))
    return events


# Memento
def move_43(ev: game_event.BattleSystemEvent):
    def _memento_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _memento_effect))
    return events


# Octazooka
def move_44(ev: game_event.BattleSystemEvent):
    def _octazooka_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _octazooka_effect))
    return events


# Flatter
def move_45(ev: game_event.BattleSystemEvent):
    def _flatter_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flatter_effect))
    return events


# Astonish
def move_46(ev: game_event.BattleSystemEvent):
    def _astonish_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _astonish_effect))
    return events


# Will-O-Wisp
def move_47(ev: game_event.BattleSystemEvent):
    def _will_o_wisp_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _will_o_wisp_effect))
    return events


# Return
def move_48(ev: game_event.BattleSystemEvent):
    def _return_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _return_effect))
    return events


# Grudge
def move_49(ev: game_event.BattleSystemEvent):
    def _grudge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _grudge_effect))
    return events


# Strength
def move_50(ev: game_event.BattleSystemEvent):
    def _strength_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _strength_effect))
    return events


# Counter
def move_51(ev: game_event.BattleSystemEvent):
    def _counter_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _counter_effect))
    return events


# Flame Wheel
def move_52(ev: game_event.BattleSystemEvent):
    def _flame_wheel_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flame_wheel_effect))
    return events


# Flamethrower
def move_53(ev: game_event.BattleSystemEvent):
    def _flamethrower_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flamethrower_effect))
    return events


# Odor Sleuth
def move_54(ev: game_event.BattleSystemEvent):
    def _odor_sleuth_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _odor_sleuth_effect))
    return events


# Sharpen
def move_55(ev: game_event.BattleSystemEvent):
    def _sharpen_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sharpen_effect))
    return events


# Double Team
def move_56(ev: game_event.BattleSystemEvent):
    def _double_team_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _double_team_effect))
    return events


# Gust
def move_57(ev: game_event.BattleSystemEvent):
    def _gust_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _gust_effect))
    return events


# Harden
def move_58(ev: game_event.BattleSystemEvent):
    def _harden_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _harden_effect))
    return events


# Disable
def move_59(ev: game_event.BattleSystemEvent):
    def _disable_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _disable_effect))
    return events


# Razor Wind
def move_60(ev: game_event.BattleSystemEvent):
    def _razor_wind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _razor_wind_effect))
    return events


# Bide
def move_61(ev: game_event.BattleSystemEvent):
    def _bide_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bide_effect))
    return events


# Crunch
def move_62(ev: game_event.BattleSystemEvent):
    def _crunch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _crunch_effect))
    return events


# Bite
def move_63(ev: game_event.BattleSystemEvent):
    def _bite_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bite_effect))
    return events


# Thunder
def move_64(ev: game_event.BattleSystemEvent):
    def _thunder_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thunder_effect))
    return events


# ThunderPunch
def move_65(ev: game_event.BattleSystemEvent):
    def _thunderpunch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thunderpunch_effect))
    return events


# Endeavor
def move_66(ev: game_event.BattleSystemEvent):
    def _endeavor_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _endeavor_effect))
    return events


# Facade
def move_67(ev: game_event.BattleSystemEvent):
    def _facade_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _facade_effect))
    return events


# Karate Chop
def move_68(ev: game_event.BattleSystemEvent):
    def _karate_chop_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _karate_chop_effect))
    return events


# Clamp
def move_69(ev: game_event.BattleSystemEvent):
    def _clamp_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _clamp_effect))
    return events


# Withdraw
def move_70(ev: game_event.BattleSystemEvent):
    def _withdraw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _withdraw_effect))
    return events


# Constrict
def move_71(ev: game_event.BattleSystemEvent):
    def _constrict_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _constrict_effect))
    return events


# Brick Break
def move_72(ev: game_event.BattleSystemEvent):
    def _brick_break_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _brick_break_effect))
    return events


# Rock Tomb
def move_73(ev: game_event.BattleSystemEvent):
    def _rock_tomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_tomb_effect))
    return events


# Focus Energy
def move_74(ev: game_event.BattleSystemEvent):
    def _focus_energy_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _focus_energy_effect))
    return events


# Focus Punch
def move_75(ev: game_event.BattleSystemEvent):
    def _focus_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _focus_punch_effect))
    return events


# Giga Drain
def move_76(ev: game_event.BattleSystemEvent):
    def _giga_drain_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _giga_drain_effect))
    return events


# Reversal
def move_77(ev: game_event.BattleSystemEvent):
    def _reversal_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _reversal_effect))
    return events


# SmellingSalt
def move_78(ev: game_event.BattleSystemEvent):
    def _smellingsalt_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _smellingsalt_effect))
    return events


# Spore
def move_79(ev: game_event.BattleSystemEvent):
    def _spore_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spore_effect))
    return events


# Leech Life
def move_80(ev: game_event.BattleSystemEvent):
    def _leech_life_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _leech_life_effect))
    return events


# Slash
def move_81(ev: game_event.BattleSystemEvent):
    def _slash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _slash_effect))
    return events


# Silver Wind
def move_82(ev: game_event.BattleSystemEvent):
    def _silver_wind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _silver_wind_effect))
    return events


# Metal Sound
def move_83(ev: game_event.BattleSystemEvent):
    def _metal_sound_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _metal_sound_effect))
    return events


# GrassWhistle
def move_84(ev: game_event.BattleSystemEvent):
    def _grasswhistle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _grasswhistle_effect))
    return events


# Tickle
def move_85(ev: game_event.BattleSystemEvent):
    def _tickle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _tickle_effect))
    return events


# Spider Web
def move_86(ev: game_event.BattleSystemEvent):
    def _spider_web_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spider_web_effect))
    return events


# Crabhammer
def move_87(ev: game_event.BattleSystemEvent):
    def _crabhammer_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _crabhammer_effect))
    return events


# Haze
def move_88(ev: game_event.BattleSystemEvent):
    def _haze_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _haze_effect))
    return events


# Mean Look
def move_89(ev: game_event.BattleSystemEvent):
    def _mean_look_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mean_look_effect))
    return events


# Cross Chop
def move_90(ev: game_event.BattleSystemEvent):
    def _cross_chop_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _cross_chop_effect))
    return events


# Outrage
def move_91(ev: game_event.BattleSystemEvent):
    def _outrage_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _outrage_effect))
    return events


# Low Kick
def move_92(ev: game_event.BattleSystemEvent):
    def _low_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _low_kick_effect))
    return events


# AncientPower
def move_93(ev: game_event.BattleSystemEvent):
    def _ancientpower_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ancientpower_effect))
    return events


# Synthesis
def move_94(ev: game_event.BattleSystemEvent):
    def _synthesis_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _synthesis_effect))
    return events


# Agility
def move_95(ev: game_event.BattleSystemEvent):
    def _agility_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _agility_effect))
    return events


# Rapid Spin
def move_96(ev: game_event.BattleSystemEvent):
    def _rapid_spin_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rapid_spin_effect))
    return events


# Icy Wind
def move_97(ev: game_event.BattleSystemEvent):
    def _icy_wind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _icy_wind_effect))
    return events


# Mind Reader
def move_98(ev: game_event.BattleSystemEvent):
    def _mind_reader_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mind_reader_effect))
    return events


# Cosmic Power
def move_99(ev: game_event.BattleSystemEvent):
    def _cosmic_power_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _cosmic_power_effect))
    return events


# Sky Attack
def move_100(ev: game_event.BattleSystemEvent):
    def _sky_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sky_attack_effect))
    return events


# Powder Snow
def move_101(ev: game_event.BattleSystemEvent):
    def _powder_snow_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _powder_snow_effect))
    return events


# Follow Me
def move_102(ev: game_event.BattleSystemEvent):
    def _follow_me_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _follow_me_effect))
    return events


# Meteor Mash
def move_103(ev: game_event.BattleSystemEvent):
    def _meteor_mash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _meteor_mash_effect))
    return events


# Endure
def move_104(ev: game_event.BattleSystemEvent):
    def _endure_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _endure_effect))
    return events


# Rollout
def move_105(ev: game_event.BattleSystemEvent):
    def _rollout_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rollout_effect))
    return events


# Scary Face
def move_106(ev: game_event.BattleSystemEvent):
    def _scary_face_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _scary_face_effect))
    return events


# Psybeam
def move_107(ev: game_event.BattleSystemEvent):
    def _psybeam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psybeam_effect))
    return events


# Psywave
def move_108(ev: game_event.BattleSystemEvent):
    def _psywave_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psywave_effect))
    return events


# Psychic
def move_109(ev: game_event.BattleSystemEvent):
    def _psychic_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psychic_effect))
    return events


# Psycho Boost
def move_110(ev: game_event.BattleSystemEvent):
    def _psycho_boost_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psycho_boost_effect))
    return events


# Hypnosis
def move_111(ev: game_event.BattleSystemEvent):
    def _hypnosis_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hypnosis_effect))
    return events


# Uproar
def move_112(ev: game_event.BattleSystemEvent):
    def _uproar_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _uproar_effect))
    return events


# Water Spout
def move_113(ev: game_event.BattleSystemEvent):
    def _water_spout_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _water_spout_effect))
    return events


# Signal Beam
def move_114(ev: game_event.BattleSystemEvent):
    def _signal_beam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _signal_beam_effect))
    return events


# Psych Up
def move_115(ev: game_event.BattleSystemEvent):
    def _psych_up_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psych_up_effect))
    return events


# Submission
def move_116(ev: game_event.BattleSystemEvent):
    def _submission_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _submission_effect))
    return events


# Recover
def move_117(ev: game_event.BattleSystemEvent):
    def _recover_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _recover_effect))
    return events


# Earthquake
def move_118(ev: game_event.BattleSystemEvent):
    def _earthquake_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _earthquake_effect))
    return events


# Nature Power
def move_119(ev: game_event.BattleSystemEvent):
    def _nature_power_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _nature_power_effect))
    return events


# Lick
def move_120(ev: game_event.BattleSystemEvent):
    def _lick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _lick_effect))
    return events


# Flail
def move_121(ev: game_event.BattleSystemEvent):
    def _flail_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flail_effect))
    return events


# Tail Whip
def move_122(ev: game_event.BattleSystemEvent):
    def _tail_whip_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _tail_whip_effect))
    return events


# Selfdestruct
def move_123(ev: game_event.BattleSystemEvent):
    def _selfdestruct_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _selfdestruct_effect))
    return events


# Stun Spore
def move_124(ev: game_event.BattleSystemEvent):
    def _stun_spore_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _stun_spore_effect))
    return events


# Bind
def move_125(ev: game_event.BattleSystemEvent):
    def _bind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bind_effect))
    return events


# Shadow Punch
def move_126(ev: game_event.BattleSystemEvent):
    def _shadow_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _shadow_punch_effect))
    return events


# Shadow Ball
def move_127(ev: game_event.BattleSystemEvent):
    def _shadow_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _shadow_ball_effect))
    return events


# Charge
def move_128(ev: game_event.BattleSystemEvent):
    def _charge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _charge_effect))
    return events


# Thunderbolt
def move_129(ev: game_event.BattleSystemEvent):
    def _thunderbolt_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thunderbolt_effect))
    return events


# Mist
def move_130(ev: game_event.BattleSystemEvent):
    def _mist_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mist_effect))
    return events


# Fissure
def move_131(ev: game_event.BattleSystemEvent):
    def _fissure_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fissure_effect))
    return events


# ExtremeSpeed
def move_132(ev: game_event.BattleSystemEvent):
    def _extremespeed_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _extremespeed_effect))
    return events


# Extrasensory
def move_133(ev: game_event.BattleSystemEvent):
    def _extrasensory_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _extrasensory_effect))
    return events


# Safeguard
def move_134(ev: game_event.BattleSystemEvent):
    def _safeguard_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _safeguard_effect))
    return events


# Absorb
def move_135(ev: game_event.BattleSystemEvent):
    def _absorb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _absorb_effect))
    return events


# Sky Uppercut
def move_136(ev: game_event.BattleSystemEvent):
    def _sky_uppercut_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sky_uppercut_effect))
    return events


# Skill Swap
def move_137(ev: game_event.BattleSystemEvent):
    def _skill_swap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _skill_swap_effect))
    return events


# Sketch
def move_138(ev: game_event.BattleSystemEvent):
    def _sketch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sketch_effect))
    return events


# Headbutt
def move_139(ev: game_event.BattleSystemEvent):
    def _headbutt_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _headbutt_effect))
    return events


# Double-Edge
def move_140(ev: game_event.BattleSystemEvent):
    def _double_edge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _double_edge_effect))
    return events


# Sandstorm
def move_141(ev: game_event.BattleSystemEvent):
    def _sandstorm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sandstorm_effect))
    return events


# Sand-Attack
def move_142(ev: game_event.BattleSystemEvent):
    def _sand_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sand_attack_effect))
    return events


# Sand Tomb
def move_143(ev: game_event.BattleSystemEvent):
    def _sand_tomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sand_tomb_effect))
    return events


# Spark
def move_144(ev: game_event.BattleSystemEvent):
    def _spark_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spark_effect))
    return events


# Swift
def move_145(ev: game_event.BattleSystemEvent):
    def _swift_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _swift_effect))
    return events


# Kinesis
def move_146(ev: game_event.BattleSystemEvent):
    def _kinesis_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _kinesis_effect))
    return events


# Smog
def move_147(ev: game_event.BattleSystemEvent):
    def _smog_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _smog_effect))
    return events


# Growth
def move_148(ev: game_event.BattleSystemEvent):
    def _growth_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _growth_effect))
    return events


# Sacred Fire
def move_149(ev: game_event.BattleSystemEvent):
    def _sacred_fire_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sacred_fire_effect))
    return events


# Sheer Cold
def move_150(ev: game_event.BattleSystemEvent):
    def _sheer_cold_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sheer_cold_effect))
    return events


# SolarBeam
def move_151(ev: game_event.BattleSystemEvent):
    def _solarbeam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _solarbeam_effect))
    return events


# SonicBoom
def move_152(ev: game_event.BattleSystemEvent):
    def _sonicboom_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sonicboom_effect))
    return events


# Fly
def move_153(ev: game_event.BattleSystemEvent):
    def _fly_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fly_effect))
    return events


# Tackle
def move_154(ev: game_event.BattleSystemEvent):
    def _tackle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _tackle_effect))
    return events


# Explosion
def move_155(ev: game_event.BattleSystemEvent):
    def _explosion_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _explosion_effect))
    return events


# Dive
def move_156(ev: game_event.BattleSystemEvent):
    def _dive_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dive_effect))
    return events


# Fire Blast
def move_157(ev: game_event.BattleSystemEvent):
    def _fire_blast_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fire_blast_effect))
    return events


# Waterfall
def move_158(ev: game_event.BattleSystemEvent):
    def _waterfall_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _waterfall_effect))
    return events


# Muddy Water
def move_159(ev: game_event.BattleSystemEvent):
    def _muddy_water_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _muddy_water_effect))
    return events


# Stockpile
def move_160(ev: game_event.BattleSystemEvent):
    def _stockpile_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _stockpile_effect))
    return events


# Slam
def move_161(ev: game_event.BattleSystemEvent):
    def _slam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _slam_effect))
    return events


# Twister
def move_162(ev: game_event.BattleSystemEvent):
    def _twister_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _twister_effect))
    return events


# Bullet Seed
def move_163(ev: game_event.BattleSystemEvent):
    def _bullet_seed_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bullet_seed_effect))
    return events


# Twineedle
def move_164(ev: game_event.BattleSystemEvent):
    def _twineedle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _twineedle_effect))
    return events


# Softboiled
def move_165(ev: game_event.BattleSystemEvent):
    def _softboiled_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _softboiled_effect))
    return events


# Egg Bomb
def move_166(ev: game_event.BattleSystemEvent):
    def _egg_bomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _egg_bomb_effect))
    return events


# Faint Attack
def move_167(ev: game_event.BattleSystemEvent):
    def _faint_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _faint_attack_effect))
    return events


# Barrage
def move_168(ev: game_event.BattleSystemEvent):
    def _barrage_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _barrage_effect))
    return events


# Minimize
def move_169(ev: game_event.BattleSystemEvent):
    def _minimize_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _minimize_effect))
    return events


# Seismic Toss
def move_170(ev: game_event.BattleSystemEvent):
    def _seismic_toss_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _seismic_toss_effect))
    return events


# Supersonic
def move_171(ev: game_event.BattleSystemEvent):
    def _supersonic_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _supersonic_effect))
    return events


# Taunt
def move_172(ev: game_event.BattleSystemEvent):
    def _taunt_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _taunt_effect))
    return events


# Moonlight
def move_173(ev: game_event.BattleSystemEvent):
    def _moonlight_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _moonlight_effect))
    return events


# Peck
def move_174(ev: game_event.BattleSystemEvent):
    def _peck_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _peck_effect))
    return events


# Arm Thrust
def move_175(ev: game_event.BattleSystemEvent):
    def _arm_thrust_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _arm_thrust_effect))
    return events


# Horn Attack
def move_176(ev: game_event.BattleSystemEvent):
    def _horn_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _horn_attack_effect))
    return events


# Horn Drill
def move_177(ev: game_event.BattleSystemEvent):
    def _horn_drill_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _horn_drill_effect))
    return events


# Wing Attack
def move_178(ev: game_event.BattleSystemEvent):
    def _wing_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wing_attack_effect))
    return events


# Aerial Ace
def move_179(ev: game_event.BattleSystemEvent):
    def _aerial_ace_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aerial_ace_effect))
    return events


# Icicle Spear
def move_180(ev: game_event.BattleSystemEvent):
    def _icicle_spear_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _icicle_spear_effect))
    return events


# Swords Dance
def move_181(ev: game_event.BattleSystemEvent):
    def _swords_dance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _swords_dance_effect))
    return events


# Vine Whip
def move_182(ev: game_event.BattleSystemEvent):
    def _vine_whip_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _vine_whip_effect))
    return events


# Conversion
def move_183(ev: game_event.BattleSystemEvent):
    def _conversion_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _conversion_effect))
    return events


# Conversion 2
def move_184(ev: game_event.BattleSystemEvent):
    def _conversion_2_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _conversion_2_effect))
    return events


# Helping Hand
def move_185(ev: game_event.BattleSystemEvent):
    def _helping_hand_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _helping_hand_effect))
    return events


# Iron Defense
def move_186(ev: game_event.BattleSystemEvent):
    def _iron_defense_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _iron_defense_effect))
    return events


# Teleport
def move_187(ev: game_event.BattleSystemEvent):
    def _teleport_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _teleport_effect))
    return events


# ThunderShock
def move_188(ev: game_event.BattleSystemEvent):
    def _thundershock_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thundershock_effect))
    return events


# Shock Wave
def move_189(ev: game_event.BattleSystemEvent):
    def _shock_wave_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _shock_wave_effect))
    return events


# Quick Attack
def move_190(ev: game_event.BattleSystemEvent):
    def _quick_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _quick_attack_effect))
    return events


# Sweet Kiss
def move_191(ev: game_event.BattleSystemEvent):
    def _sweet_kiss_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sweet_kiss_effect))
    return events


# Thunder Wave
def move_192(ev: game_event.BattleSystemEvent):
    def _thunder_wave_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thunder_wave_effect))
    return events


# Zap Cannon
def move_193(ev: game_event.BattleSystemEvent):
    def _zap_cannon_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _zap_cannon_effect))
    return events


# Block
def move_194(ev: game_event.BattleSystemEvent):
    def _block_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _block_effect))
    return events


# Howl
def move_195(ev: game_event.BattleSystemEvent):
    def _howl_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _howl_effect))
    return events


# Poison Gas
def move_196(ev: game_event.BattleSystemEvent):
    def _poison_gas_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _poison_gas_effect))
    return events


# Toxic
def move_197(ev: game_event.BattleSystemEvent):
    def _toxic_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _toxic_effect))
    return events


# Poison Fang
def move_198(ev: game_event.BattleSystemEvent):
    def _poison_fang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _poison_fang_effect))
    return events


# PoisonPowder
def move_199(ev: game_event.BattleSystemEvent):
    def _poisonpowder_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _poisonpowder_effect))
    return events


# Poison Sting
def move_200(ev: game_event.BattleSystemEvent):
    def _poison_sting_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _poison_sting_effect))
    return events


# Spike Cannon
def move_201(ev: game_event.BattleSystemEvent):
    def _spike_cannon_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spike_cannon_effect))
    return events


# Acid Armor
def move_202(ev: game_event.BattleSystemEvent):
    def _acid_armor_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _acid_armor_effect))
    return events


# Take Down
def move_203(ev: game_event.BattleSystemEvent):
    def _take_down_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _take_down_effect))
    return events


# Jump Kick
def move_204(ev: game_event.BattleSystemEvent):
    def _jump_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _jump_kick_effect))
    return events


# Bounce
def move_205(ev: game_event.BattleSystemEvent):
    def _bounce_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bounce_effect))
    return events


# Hi Jump Kick
def move_206(ev: game_event.BattleSystemEvent):
    def _hi_jump_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hi_jump_kick_effect))
    return events


# Tri Attack
def move_207(ev: game_event.BattleSystemEvent):
    def _tri_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _tri_attack_effect))
    return events


# Dragon Claw
def move_208(ev: game_event.BattleSystemEvent):
    def _dragon_claw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dragon_claw_effect))
    return events


# Trick
def move_209(ev: game_event.BattleSystemEvent):
    def _trick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _trick_effect))
    return events


# Triple Kick
def move_210(ev: game_event.BattleSystemEvent):
    def _triple_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _triple_kick_effect))
    return events


# Drill Peck
def move_211(ev: game_event.BattleSystemEvent):
    def _drill_peck_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _drill_peck_effect))
    return events


# Mud Sport
def move_212(ev: game_event.BattleSystemEvent):
    def _mud_sport_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mud_sport_effect))
    return events


# Mud-Slap
def move_213(ev: game_event.BattleSystemEvent):
    def _mud_slap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mud_slap_effect))
    return events


# Thief
def move_214(ev: game_event.BattleSystemEvent):
    def _thief_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thief_effect))
    return events


# Amnesia
def move_215(ev: game_event.BattleSystemEvent):
    def _amnesia_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _amnesia_effect))
    return events


# Night Shade
def move_216(ev: game_event.BattleSystemEvent):
    def _night_shade_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _night_shade_effect))
    return events


# Growl
def move_217(ev: game_event.BattleSystemEvent):
    def _growl_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _growl_effect))
    return events


# Slack Off
def move_218(ev: game_event.BattleSystemEvent):
    def _slack_off_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _slack_off_effect))
    return events


# Surf
def move_219(ev: game_event.BattleSystemEvent):
    def _surf_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _surf_effect))
    return events


# Role Play
def move_220(ev: game_event.BattleSystemEvent):
    def _role_play_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _role_play_effect))
    return events


# Needle Arm
def move_221(ev: game_event.BattleSystemEvent):
    def _needle_arm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _needle_arm_effect))
    return events


# Double Kick
def move_222(ev: game_event.BattleSystemEvent):
    def _double_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _double_kick_effect))
    return events


# Sunny Day
def move_223(ev: game_event.BattleSystemEvent):
    def _sunny_day_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sunny_day_effect))
    return events


# Leer
def move_224(ev: game_event.BattleSystemEvent):
    def _leer_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _leer_effect))
    return events


# Wish
def move_225(ev: game_event.BattleSystemEvent):
    def _wish_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wish_effect))
    return events


# Fake Out
def move_226(ev: game_event.BattleSystemEvent):
    def _fake_out_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fake_out_effect))
    return events


# Sleep Talk
def move_227(ev: game_event.BattleSystemEvent):
    def _sleep_talk_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sleep_talk_effect))
    return events


# Pay Day
def move_228(ev: game_event.BattleSystemEvent):
    def _pay_day_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _pay_day_effect))
    return events


# Assist
def move_229(ev: game_event.BattleSystemEvent):
    def _assist_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _assist_effect))
    return events


# Heat Wave
def move_230(ev: game_event.BattleSystemEvent):
    def _heat_wave_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _heat_wave_effect))
    return events


# Sleep Powder
def move_231(ev: game_event.BattleSystemEvent):
    def _sleep_powder_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sleep_powder_effect))
    return events


# Rest
def move_232(ev: game_event.BattleSystemEvent):
    def _rest_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rest_effect))
    return events


# Ingrain
def move_233(ev: game_event.BattleSystemEvent):
    def _ingrain_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ingrain_effect))
    return events


# Confusion
def move_234(ev: game_event.BattleSystemEvent):
    def _confusion_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _confusion_effect))
    return events


# Body Slam
def move_235(ev: game_event.BattleSystemEvent):
    def _body_slam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _body_slam_effect))
    return events


# Swallow
def move_236(ev: game_event.BattleSystemEvent):
    def _swallow_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _swallow_effect))
    return events


# Curse
def move_237(ev: game_event.BattleSystemEvent):
    def _curse_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _curse_effect))
    return events


# Frenzy Plant
def move_238(ev: game_event.BattleSystemEvent):
    def _frenzy_plant_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _frenzy_plant_effect))
    return events


# Hydro Cannon
def move_239(ev: game_event.BattleSystemEvent):
    def _hydro_cannon_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hydro_cannon_effect))
    return events


# Hydro Pump
def move_240(ev: game_event.BattleSystemEvent):
    def _hydro_pump_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hydro_pump_effect))
    return events


# Hyper Voice
def move_241(ev: game_event.BattleSystemEvent):
    def _hyper_voice_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hyper_voice_effect))
    return events


# Hyper Beam
def move_242(ev: game_event.BattleSystemEvent):
    def _hyper_beam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hyper_beam_effect))
    return events


# Superpower
def move_243(ev: game_event.BattleSystemEvent):
    def _superpower_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _superpower_effect))
    return events


# Steel Wing
def move_244(ev: game_event.BattleSystemEvent):
    def _steel_wing_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _steel_wing_effect))
    return events


# Spit Up
def move_245(ev: game_event.BattleSystemEvent):
    def _spit_up_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spit_up_effect))
    return events


# DynamicPunch
def move_246(ev: game_event.BattleSystemEvent):
    def _dynamicpunch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dynamicpunch_effect))
    return events


# Guillotine
def move_247(ev: game_event.BattleSystemEvent):
    def _guillotine_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _guillotine_effect))
    return events


# ViceGrip
def move_248(ev: game_event.BattleSystemEvent):
    def _vicegrip_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _vicegrip_effect))
    return events


# Knock Off
def move_249(ev: game_event.BattleSystemEvent):
    def _knock_off_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _knock_off_effect))
    return events


# Pound
def move_250(ev: game_event.BattleSystemEvent):
    def _pound_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _pound_effect))
    return events


# Razor Leaf
def move_251(ev: game_event.BattleSystemEvent):
    def _razor_leaf_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _razor_leaf_effect))
    return events


# Baton Pass
def move_252(ev: game_event.BattleSystemEvent):
    def _baton_pass_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _baton_pass_effect))
    return events


# Petal Dance
def move_253(ev: game_event.BattleSystemEvent):
    def _petal_dance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _petal_dance_effect))
    return events


# Splash
def move_254(ev: game_event.BattleSystemEvent):
    def _splash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _splash_effect))
    return events


# BubbleBeam
def move_255(ev: game_event.BattleSystemEvent):
    def _bubblebeam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bubblebeam_effect))
    return events


# Doom Desire
def move_256(ev: game_event.BattleSystemEvent):
    def _doom_desire_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _doom_desire_effect))
    return events


# Belly Drum
def move_257(ev: game_event.BattleSystemEvent):
    def _belly_drum_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _belly_drum_effect))
    return events


# Barrier
def move_258(ev: game_event.BattleSystemEvent):
    def _barrier_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _barrier_effect))
    return events


# Light Screen
def move_259(ev: game_event.BattleSystemEvent):
    def _light_screen_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _light_screen_effect))
    return events


# Scratch
def move_260(ev: game_event.BattleSystemEvent):
    def _scratch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _scratch_effect))
    return events


# Hyper Fang
def move_261(ev: game_event.BattleSystemEvent):
    def _hyper_fang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hyper_fang_effect))
    return events


# Ember
def move_262(ev: game_event.BattleSystemEvent):
    def _ember_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ember_effect))
    return events


# Secret Power
def move_263(ev: game_event.BattleSystemEvent):
    def _secret_power_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _secret_power_effect))
    return events


# Dizzy Punch
def move_264(ev: game_event.BattleSystemEvent):
    def _dizzy_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dizzy_punch_effect))
    return events


# Bulk Up
def move_265(ev: game_event.BattleSystemEvent):
    def _bulk_up_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bulk_up_effect))
    return events


# Imprison
def move_266(ev: game_event.BattleSystemEvent):
    def _imprison_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _imprison_effect))
    return events


# FeatherDance
def move_267(ev: game_event.BattleSystemEvent):
    def _featherdance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _featherdance_effect))
    return events


# Whirlwind
def move_268(ev: game_event.BattleSystemEvent):
    def _whirlwind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _whirlwind_effect))
    return events


# Beat Up
def move_269(ev: game_event.BattleSystemEvent):
    def _beat_up_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _beat_up_effect))
    return events


# Blizzard
def move_270(ev: game_event.BattleSystemEvent):
    def _blizzard_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _blizzard_effect))
    return events


# Stomp
def move_271(ev: game_event.BattleSystemEvent):
    def _stomp_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _stomp_effect))
    return events


# Blast Burn
def move_272(ev: game_event.BattleSystemEvent):
    def _blast_burn_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _blast_burn_effect))
    return events


# Flash
def move_273(ev: game_event.BattleSystemEvent):
    def _flash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flash_effect))
    return events


# Teeter Dance
def move_274(ev: game_event.BattleSystemEvent):
    def _teeter_dance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _teeter_dance_effect))
    return events


# Crush Claw
def move_275(ev: game_event.BattleSystemEvent):
    def _crush_claw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _crush_claw_effect))
    return events


# Blaze Kick
def move_276(ev: game_event.BattleSystemEvent):
    def _blaze_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _blaze_kick_effect))
    return events


# Present
def move_277(ev: game_event.BattleSystemEvent):
    def _present_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _present_effect))
    return events


# Eruption
def move_278(ev: game_event.BattleSystemEvent):
    def _eruption_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _eruption_effect))
    return events


# Sludge
def move_279(ev: game_event.BattleSystemEvent):
    def _sludge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sludge_effect))
    return events


# Sludge Bomb
def move_280(ev: game_event.BattleSystemEvent):
    def _sludge_bomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sludge_bomb_effect))
    return events


# Glare
def move_281(ev: game_event.BattleSystemEvent):
    def _glare_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _glare_effect))
    return events


# Transform
def move_282(ev: game_event.BattleSystemEvent):
    def _transform_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _transform_effect))
    return events


# Poison Tail
def move_283(ev: game_event.BattleSystemEvent):
    def _poison_tail_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _poison_tail_effect))
    return events


# Roar
def move_284(ev: game_event.BattleSystemEvent):
    def _roar_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _roar_effect))
    return events


# Bone Rush
def move_285(ev: game_event.BattleSystemEvent):
    def _bone_rush_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bone_rush_effect))
    return events


# Camouflage
def move_286(ev: game_event.BattleSystemEvent):
    def _camouflage_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _camouflage_effect))
    return events


# Covet
def move_287(ev: game_event.BattleSystemEvent):
    def _covet_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _covet_effect))
    return events


# Tail Glow
def move_288(ev: game_event.BattleSystemEvent):
    def _tail_glow_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _tail_glow_effect))
    return events


# Bone Club
def move_289(ev: game_event.BattleSystemEvent):
    def _bone_club_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bone_club_effect))
    return events


# Bonemerang
def move_290(ev: game_event.BattleSystemEvent):
    def _bonemerang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bonemerang_effect))
    return events


# Fire Spin
def move_291(ev: game_event.BattleSystemEvent):
    def _fire_spin_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fire_spin_effect))
    return events


# Fire Punch
def move_292(ev: game_event.BattleSystemEvent):
    def _fire_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fire_punch_effect))
    return events


# Perish Song
def move_293(ev: game_event.BattleSystemEvent):
    def _perish_song_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _perish_song_effect))
    return events


# Wrap
def move_294(ev: game_event.BattleSystemEvent):
    def _wrap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wrap_effect))
    return events


# Spikes
def move_295(ev: game_event.BattleSystemEvent):
    def _spikes_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spikes_effect))
    return events


# Magnitude
def move_296(ev: game_event.BattleSystemEvent):
    def _magnitude_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _magnitude_effect))
    return events


# Magical Leaf
def move_297(ev: game_event.BattleSystemEvent):
    def _magical_leaf_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _magical_leaf_effect))
    return events


# Magic Coat
def move_298(ev: game_event.BattleSystemEvent):
    def _magic_coat_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _magic_coat_effect))
    return events


# Mud Shot
def move_299(ev: game_event.BattleSystemEvent):
    def _mud_shot_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mud_shot_effect))
    return events


# Mach Punch
def move_300(ev: game_event.BattleSystemEvent):
    def _mach_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mach_punch_effect))
    return events


# Protect
def move_301(ev: game_event.BattleSystemEvent):
    def _protect_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _protect_effect))
    return events


# Defense Curl
def move_302(ev: game_event.BattleSystemEvent):
    def _defense_curl_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _defense_curl_effect))
    return events


# Rolling Kick
def move_303(ev: game_event.BattleSystemEvent):
    def _rolling_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rolling_kick_effect))
    return events


# Substitute
def move_304(ev: game_event.BattleSystemEvent):
    def _substitute_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _substitute_effect))
    return events


# Detect
def move_305(ev: game_event.BattleSystemEvent):
    def _detect_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _detect_effect))
    return events


# Pin Missile
def move_306(ev: game_event.BattleSystemEvent):
    def _pin_missile_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _pin_missile_effect))
    return events


# Water Sport
def move_307(ev: game_event.BattleSystemEvent):
    def _water_sport_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _water_sport_effect))
    return events


# Water Gun
def move_308(ev: game_event.BattleSystemEvent):
    def _water_gun_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _water_gun_effect))
    return events


# Mist Ball
def move_309(ev: game_event.BattleSystemEvent):
    def _mist_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mist_ball_effect))
    return events


# Water Pulse
def move_310(ev: game_event.BattleSystemEvent):
    def _water_pulse_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _water_pulse_effect))
    return events


# Fury Attack
def move_311(ev: game_event.BattleSystemEvent):
    def _fury_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fury_attack_effect))
    return events


# Fury Swipes
def move_312(ev: game_event.BattleSystemEvent):
    def _fury_swipes_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fury_swipes_effect))
    return events


# Destiny Bond
def move_313(ev: game_event.BattleSystemEvent):
    def _destiny_bond_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _destiny_bond_effect))
    return events


# False Swipe
def move_314(ev: game_event.BattleSystemEvent):
    def _false_swipe_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _false_swipe_effect))
    return events


# Foresight
def move_315(ev: game_event.BattleSystemEvent):
    def _foresight_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _foresight_effect))
    return events


# Mirror Coat
def move_316(ev: game_event.BattleSystemEvent):
    def _mirror_coat_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mirror_coat_effect))
    return events


# Future Sight
def move_317(ev: game_event.BattleSystemEvent):
    def _future_sight_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _future_sight_effect))
    return events


# Milk Drink
def move_318(ev: game_event.BattleSystemEvent):
    def _milk_drink_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _milk_drink_effect))
    return events


# Calm Mind
def move_319(ev: game_event.BattleSystemEvent):
    def _calm_mind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _calm_mind_effect))
    return events


# Mega Drain
def move_320(ev: game_event.BattleSystemEvent):
    def _mega_drain_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mega_drain_effect))
    return events


# Mega Kick
def move_321(ev: game_event.BattleSystemEvent):
    def _mega_kick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mega_kick_effect))
    return events


# Mega Punch
def move_322(ev: game_event.BattleSystemEvent):
    def _mega_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mega_punch_effect))
    return events


# Megahorn
def move_323(ev: game_event.BattleSystemEvent):
    def _megahorn_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _megahorn_effect))
    return events


# Hidden Power
def move_324(ev: game_event.BattleSystemEvent):
    def _hidden_power_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hidden_power_effect))
    return events


# Metal Claw
def move_325(ev: game_event.BattleSystemEvent):
    def _metal_claw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _metal_claw_effect))
    return events


# Attract
def move_326(ev: game_event.BattleSystemEvent):
    def _attract_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _attract_effect))
    return events


# Mimic
def move_327(ev: game_event.BattleSystemEvent):
    def _mimic_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mimic_effect))
    return events


# Frustration
def move_328(ev: game_event.BattleSystemEvent):
    def _frustration_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _frustration_effect))
    return events


# Leech Seed
def move_329(ev: game_event.BattleSystemEvent):
    def _leech_seed_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _leech_seed_effect))
    return events


# Metronome
def move_330(ev: game_event.BattleSystemEvent):
    def _metronome_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _metronome_effect))
    return events


# Dream Eater
def move_331(ev: game_event.BattleSystemEvent):
    def _dream_eater_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dream_eater_effect))
    return events


# Acid
def move_332(ev: game_event.BattleSystemEvent):
    def _acid_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _acid_effect))
    return events


# Meditate
def move_333(ev: game_event.BattleSystemEvent):
    def _meditate_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _meditate_effect))
    return events


# Snatch
def move_334(ev: game_event.BattleSystemEvent):
    def _snatch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _snatch_effect))
    return events


# Luster Purge
def move_335(ev: game_event.BattleSystemEvent):
    def _luster_purge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _luster_purge_effect))
    return events


# Leaf Blade
def move_336(ev: game_event.BattleSystemEvent):
    def _leaf_blade_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _leaf_blade_effect))
    return events


# Recycle
def move_337(ev: game_event.BattleSystemEvent):
    def _recycle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _recycle_effect))
    return events


# Reflect
def move_338(ev: game_event.BattleSystemEvent):
    def _reflect_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _reflect_effect))
    return events


# Refresh
def move_339(ev: game_event.BattleSystemEvent):
    def _refresh_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _refresh_effect))
    return events


# Revenge
def move_340(ev: game_event.BattleSystemEvent):
    def _revenge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _revenge_effect))
    return events


# Dragon Rage
def move_341(ev: game_event.BattleSystemEvent):
    def _dragon_rage_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dragon_rage_effect))
    return events


# DragonBreath
def move_342(ev: game_event.BattleSystemEvent):
    def _dragonbreath_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dragonbreath_effect))
    return events


# Dragon Dance
def move_343(ev: game_event.BattleSystemEvent):
    def _dragon_dance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dragon_dance_effect))
    return events


# Ice Punch
def move_344(ev: game_event.BattleSystemEvent):
    def _ice_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ice_punch_effect))
    return events


# Ice Beam
def move_345(ev: game_event.BattleSystemEvent):
    def _ice_beam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ice_beam_effect))
    return events


# Fury Cutter
def move_346(ev: game_event.BattleSystemEvent):
    def _fury_cutter_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fury_cutter_effect))
    return events


# Comet Punch
def move_347(ev: game_event.BattleSystemEvent):
    def _comet_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _comet_punch_effect))
    return events


# Skull Bash
def move_348(ev: game_event.BattleSystemEvent):
    def _skull_bash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _skull_bash_effect))
    return events


# Lock-On
def move_349(ev: game_event.BattleSystemEvent):
    def _lock_on_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _lock_on_effect))
    return events


# Rock Blast
def move_350(ev: game_event.BattleSystemEvent):
    def _rock_blast_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_blast_effect))
    return events


# Cotton Spore
def move_351(ev: game_event.BattleSystemEvent):
    def _cotton_spore_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _cotton_spore_effect))
    return events


# Struggle
def move_352(ev: game_event.BattleSystemEvent):
    def _struggle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _struggle_effect))
    return events


# Aeroblast
def move_353(ev: game_event.BattleSystemEvent):
    def _aeroblast_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aeroblast_effect))
    return events


# Volt Tackle
def move_354(ev: game_event.BattleSystemEvent):
    def _volt_tackle_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _volt_tackle_effect))
    return events


# regular attack
def move_355(ev: game_event.BattleSystemEvent):
    def _regular_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _regular_attack_effect))
    return events


# Wide Slash
def move_360(ev: game_event.BattleSystemEvent):
    def _wide_slash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wide_slash_effect))
    return events


# Vacuum-Cut
def move_394(ev: game_event.BattleSystemEvent):
    def _vacuum_cut_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _vacuum_cut_effect))
    return events


# Hammer Arm
def move_430(ev: game_event.BattleSystemEvent):
    def _hammer_arm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _hammer_arm_effect))
    return events


# Iron Head
def move_431(ev: game_event.BattleSystemEvent):
    def _iron_head_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _iron_head_effect))
    return events


# Aqua Jet
def move_432(ev: game_event.BattleSystemEvent):
    def _aqua_jet_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aqua_jet_effect))
    return events


# Aqua Tail
def move_433(ev: game_event.BattleSystemEvent):
    def _aqua_tail_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aqua_tail_effect))
    return events


# Aqua Ring
def move_434(ev: game_event.BattleSystemEvent):
    def _aqua_ring_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aqua_ring_effect))
    return events


# Spacial Rend
def move_435(ev: game_event.BattleSystemEvent):
    def _spacial_rend_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _spacial_rend_effect))
    return events


# Dark Pulse
def move_436(ev: game_event.BattleSystemEvent):
    def _dark_pulse_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dark_pulse_effect))
    return events


# Ominous Wind
def move_437(ev: game_event.BattleSystemEvent):
    def _ominous_wind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ominous_wind_effect))
    return events


# Gastro Acid
def move_438(ev: game_event.BattleSystemEvent):
    def _gastro_acid_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _gastro_acid_effect))
    return events


# Healing Wish
def move_439(ev: game_event.BattleSystemEvent):
    def _healing_wish_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _healing_wish_effect))
    return events


# Close Combat
def move_440(ev: game_event.BattleSystemEvent):
    def _close_combat_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _close_combat_effect))
    return events


# Wood Hammer
def move_441(ev: game_event.BattleSystemEvent):
    def _wood_hammer_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wood_hammer_effect))
    return events


# Air Slash
def move_442(ev: game_event.BattleSystemEvent):
    def _air_slash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _air_slash_effect))
    return events


# Energy Ball
def move_443(ev: game_event.BattleSystemEvent):
    def _energy_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _energy_ball_effect))
    return events


# Tailwind
def move_444(ev: game_event.BattleSystemEvent):
    def _tailwind_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _tailwind_effect))
    return events


# Punishment
def move_445(ev: game_event.BattleSystemEvent):
    def _punishment_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _punishment_effect))
    return events


# Chatter
def move_446(ev: game_event.BattleSystemEvent):
    def _chatter_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _chatter_effect))
    return events


# Lucky Chant
def move_447(ev: game_event.BattleSystemEvent):
    def _lucky_chant_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _lucky_chant_effect))
    return events


# Guard Swap
def move_448(ev: game_event.BattleSystemEvent):
    def _guard_swap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _guard_swap_effect))
    return events


# Heal Order
def move_449(ev: game_event.BattleSystemEvent):
    def _heal_order_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _heal_order_effect))
    return events


# Heal Block
def move_450(ev: game_event.BattleSystemEvent):
    def _heal_block_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _heal_block_effect))
    return events


# Shadow Sneak
def move_451(ev: game_event.BattleSystemEvent):
    def _shadow_sneak_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _shadow_sneak_effect))
    return events


# Thunder Fang
def move_452(ev: game_event.BattleSystemEvent):
    def _thunder_fang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _thunder_fang_effect))
    return events


# Rock Wrecker
def move_453(ev: game_event.BattleSystemEvent):
    def _rock_wrecker_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_wrecker_effect))
    return events


# Focus Blast
def move_454(ev: game_event.BattleSystemEvent):
    def _focus_blast_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _focus_blast_effect))
    return events


# Giga Impact
def move_455(ev: game_event.BattleSystemEvent):
    def _giga_impact_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _giga_impact_effect))
    return events


# Defog
def move_456(ev: game_event.BattleSystemEvent):
    def _defog_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _defog_effect))
    return events


# Trump Card
def move_457(ev: game_event.BattleSystemEvent):
    def _trump_card_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _trump_card_effect))
    return events


# Grass Knot
def move_458(ev: game_event.BattleSystemEvent):
    def _grass_knot_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _grass_knot_effect))
    return events


# Cross Poison
def move_459(ev: game_event.BattleSystemEvent):
    def _cross_poison_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _cross_poison_effect))
    return events


# Attack Order
def move_460(ev: game_event.BattleSystemEvent):
    def _attack_order_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _attack_order_effect))
    return events


# Ice Fang
def move_461(ev: game_event.BattleSystemEvent):
    def _ice_fang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ice_fang_effect))
    return events


# Ice Shard
def move_462(ev: game_event.BattleSystemEvent):
    def _ice_shard_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _ice_shard_effect))
    return events


# Psycho Cut
def move_463(ev: game_event.BattleSystemEvent):
    def _psycho_cut_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psycho_cut_effect))
    return events


# Psycho Shift
def move_464(ev: game_event.BattleSystemEvent):
    def _psycho_shift_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _psycho_shift_effect))
    return events


# Me First
def move_465(ev: game_event.BattleSystemEvent):
    def _me_first_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _me_first_effect))
    return events


# Embargo
def move_466(ev: game_event.BattleSystemEvent):
    def _embargo_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _embargo_effect))
    return events


# $$$ (Judgment)
def move_467(ev: game_event.BattleSystemEvent):
    def _judgment_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _judgment_effect))
    return events


# Seed Flare
def move_468(ev: game_event.BattleSystemEvent):
    def _seed_flare_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _seed_flare_effect))
    return events


# Brine
def move_469(ev: game_event.BattleSystemEvent):
    def _brine_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _brine_effect))
    return events


# X-Scissor
def move_470(ev: game_event.BattleSystemEvent):
    def _x_scissor_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _x_scissor_effect))
    return events


# Natural Gift
def move_471(ev: game_event.BattleSystemEvent):
    def _natural_gift_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _natural_gift_effect))
    return events


# Payback
def move_472(ev: game_event.BattleSystemEvent):
    def _payback_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _payback_effect))
    return events


# Zen Headbutt
def move_473(ev: game_event.BattleSystemEvent):
    def _zen_headbutt_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _zen_headbutt_effect))
    return events


# Wring Out
def move_474(ev: game_event.BattleSystemEvent):
    def _wring_out_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wring_out_effect))
    return events


# Gyro Ball
def move_475(ev: game_event.BattleSystemEvent):
    def _gyro_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _gyro_ball_effect))
    return events


# Shadow Claw
def move_476(ev: game_event.BattleSystemEvent):
    def _shadow_claw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _shadow_claw_effect))
    return events


# Shadow Force
def move_477(ev: game_event.BattleSystemEvent):
    def _shadow_force_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _shadow_force_effect))
    return events


# Gravity
def move_478(ev: game_event.BattleSystemEvent):
    def _gravity_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _gravity_effect))
    return events


# Vacuum Wave
def move_479(ev: game_event.BattleSystemEvent):
    def _vacuum_wave_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _vacuum_wave_effect))
    return events


# Stealth Rock
def move_480(ev: game_event.BattleSystemEvent):
    def _stealth_rock_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _stealth_rock_effect))
    return events


# Stone Edge
def move_481(ev: game_event.BattleSystemEvent):
    def _stone_edge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _stone_edge_effect))
    return events


# Switcheroo
def move_482(ev: game_event.BattleSystemEvent):
    def _switcheroo_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _switcheroo_effect))
    return events


# Dark Void
def move_483(ev: game_event.BattleSystemEvent):
    def _dark_void_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dark_void_effect))
    return events


# Earth Power
def move_484(ev: game_event.BattleSystemEvent):
    def _earth_power_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _earth_power_effect))
    return events


# Gunk Shot
def move_485(ev: game_event.BattleSystemEvent):
    def _gunk_shot_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _gunk_shot_effect))
    return events


# Seed Bomb
def move_486(ev: game_event.BattleSystemEvent):
    def _seed_bomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _seed_bomb_effect))
    return events


# Double Hit
def move_487(ev: game_event.BattleSystemEvent):
    def _double_hit_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _double_hit_effect))
    return events


# Assurance
def move_488(ev: game_event.BattleSystemEvent):
    def _assurance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _assurance_effect))
    return events


# Charge Beam
def move_489(ev: game_event.BattleSystemEvent):
    def _charge_beam_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _charge_beam_effect))
    return events


# Pluck
def move_490(ev: game_event.BattleSystemEvent):
    def _pluck_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _pluck_effect))
    return events


# Night Slash
def move_491(ev: game_event.BattleSystemEvent):
    def _night_slash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _night_slash_effect))
    return events


# Acupressure
def move_492(ev: game_event.BattleSystemEvent):
    def _acupressure_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _acupressure_effect))
    return events


# Magnet Rise
def move_493(ev: game_event.BattleSystemEvent):
    def _magnet_rise_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _magnet_rise_effect))
    return events


# Roar of Time
def move_494(ev: game_event.BattleSystemEvent):
    def _roar_of_time_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _roar_of_time_effect))
    return events


# Poison Jab
def move_495(ev: game_event.BattleSystemEvent):
    def _poison_jab_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _poison_jab_effect))
    return events


# Toxic Spikes
def move_496(ev: game_event.BattleSystemEvent):
    def _toxic_spikes_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _toxic_spikes_effect))
    return events


# Last Resort
def move_497(ev: game_event.BattleSystemEvent):
    def _last_resort_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _last_resort_effect))
    return events


# Dragon Rush
def move_498(ev: game_event.BattleSystemEvent):
    def _dragon_rush_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dragon_rush_effect))
    return events


# Trick Room
def move_499(ev: game_event.BattleSystemEvent):
    def _trick_room_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _trick_room_effect))
    return events


# Drain Punch
def move_500(ev: game_event.BattleSystemEvent):
    def _drain_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _drain_punch_effect))
    return events


# Mud Bomb
def move_501(ev: game_event.BattleSystemEvent):
    def _mud_bomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mud_bomb_effect))
    return events


# U-turn
def move_502(ev: game_event.BattleSystemEvent):
    def _u_turn_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _u_turn_effect))
    return events


# Fling
def move_503(ev: game_event.BattleSystemEvent):
    def _fling_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fling_effect))
    return events


# Worry Seed
def move_504(ev: game_event.BattleSystemEvent):
    def _worry_seed_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _worry_seed_effect))
    return events


# Crush Grip
def move_505(ev: game_event.BattleSystemEvent):
    def _crush_grip_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _crush_grip_effect))
    return events


# Heart Swap
def move_506(ev: game_event.BattleSystemEvent):
    def _heart_swap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _heart_swap_effect))
    return events


# Force Palm
def move_507(ev: game_event.BattleSystemEvent):
    def _force_palm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _force_palm_effect))
    return events


# Aura Sphere
def move_508(ev: game_event.BattleSystemEvent):
    def _aura_sphere_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _aura_sphere_effect))
    return events


# Roost
def move_509(ev: game_event.BattleSystemEvent):
    def _roost_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _roost_effect))
    return events


# Bullet Punch
def move_510(ev: game_event.BattleSystemEvent):
    def _bullet_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bullet_punch_effect))
    return events


# Power Whip
def move_511(ev: game_event.BattleSystemEvent):
    def _power_whip_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _power_whip_effect))
    return events


# Power Gem
def move_512(ev: game_event.BattleSystemEvent):
    def _power_gem_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _power_gem_effect))
    return events


# Power Swap
def move_513(ev: game_event.BattleSystemEvent):
    def _power_swap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _power_swap_effect))
    return events


# Power Trick
def move_514(ev: game_event.BattleSystemEvent):
    def _power_trick_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _power_trick_effect))
    return events


# Sucker Punch
def move_515(ev: game_event.BattleSystemEvent):
    def _sucker_punch_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _sucker_punch_effect))
    return events


# Feint
def move_516(ev: game_event.BattleSystemEvent):
    def _feint_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _feint_effect))
    return events


# Flare Blitz
def move_517(ev: game_event.BattleSystemEvent):
    def _flare_blitz_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flare_blitz_effect))
    return events


# Brave Bird
def move_518(ev: game_event.BattleSystemEvent):
    def _brave_bird_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _brave_bird_effect))
    return events


# Lava Plume
def move_519(ev: game_event.BattleSystemEvent):
    def _lava_plume_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _lava_plume_effect))
    return events


# Defend Order
def move_520(ev: game_event.BattleSystemEvent):
    def _defend_order_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _defend_order_effect))
    return events


# Discharge
def move_521(ev: game_event.BattleSystemEvent):
    def _discharge_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _discharge_effect))
    return events


# Fire Fang
def move_522(ev: game_event.BattleSystemEvent):
    def _fire_fang_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _fire_fang_effect))
    return events


# Magnet Bomb
def move_523(ev: game_event.BattleSystemEvent):
    def _magnet_bomb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _magnet_bomb_effect))
    return events


# Magma Storm
def move_524(ev: game_event.BattleSystemEvent):
    def _magma_storm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _magma_storm_effect))
    return events


# Copycat
def move_525(ev: game_event.BattleSystemEvent):
    def _copycat_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _copycat_effect))
    return events


# Lunar Dance
def move_526(ev: game_event.BattleSystemEvent):
    def _lunar_dance_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _lunar_dance_effect))
    return events


# Mirror Shot
def move_527(ev: game_event.BattleSystemEvent):
    def _mirror_shot_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _mirror_shot_effect))
    return events


# Miracle Eye
def move_528(ev: game_event.BattleSystemEvent):
    def _miracle_eye_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _miracle_eye_effect))
    return events


# Bug Bite
def move_529(ev: game_event.BattleSystemEvent):
    def _bug_bite_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bug_bite_effect))
    return events


# Bug Buzz
def move_530(ev: game_event.BattleSystemEvent):
    def _bug_buzz_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _bug_buzz_effect))
    return events


# Wake-Up Slap
def move_531(ev: game_event.BattleSystemEvent):
    def _wake_up_slap_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _wake_up_slap_effect))
    return events


# Metal Burst
def move_532(ev: game_event.BattleSystemEvent):
    def _metal_burst_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _metal_burst_effect))
    return events


# Head Smash
def move_533(ev: game_event.BattleSystemEvent):
    def _head_smash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _head_smash_effect))
    return events


# Captivate
def move_534(ev: game_event.BattleSystemEvent):
    def _captivate_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _captivate_effect))
    return events


# Avalanche
def move_535(ev: game_event.BattleSystemEvent):
    def _avalanche_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _avalanche_effect))
    return events


# Flash Cannon
def move_536(ev: game_event.BattleSystemEvent):
    def _flash_cannon_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _flash_cannon_effect))
    return events


# Leaf Storm
def move_537(ev: game_event.BattleSystemEvent):
    def _leaf_storm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _leaf_storm_effect))
    return events


# Draco Meteor
def move_538(ev: game_event.BattleSystemEvent):
    def _draco_meteor_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _draco_meteor_effect))
    return events


# Dragon Pulse
def move_539(ev: game_event.BattleSystemEvent):
    def _dragon_pulse_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _dragon_pulse_effect))
    return events


# Rock Polish
def move_540(ev: game_event.BattleSystemEvent):
    def _rock_polish_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_polish_effect))
    return events


# Rock Climb
def move_541(ev: game_event.BattleSystemEvent):
    def _rock_climb_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _rock_climb_effect))
    return events


# Nasty Plot
def move_542(ev: game_event.BattleSystemEvent):
    def _nasty_plot_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _nasty_plot_effect))
    return events


dispatcher = {i: globals().get(f"move_{i}", move_0) for i in range(543)}


def get_events_from_move(ev: game_event.BattleSystemEvent):
    return dispatcher.get(ev.move.move_id, dispatcher[0])(ev)
