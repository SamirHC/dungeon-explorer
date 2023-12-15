import random

from app.common import utils
from app.common.direction import Direction
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


# Vital Throw
def move_7(ev: game_event.BattleSystemEvent):
    def _vital_throw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
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
        events.append(game_event.LogEvent(tb.build().render()))
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
                .write(ev.attacker.data.name)
                .set_color(text.WHITE)
                .write(" burrowed underground!")
            )
            ev.attacker.status.afflict(StatusEffect.DIGGING, ev.dungeon.turns.value + 1)

        events = []
        events.append(game_event.LogEvent(tb.build().render()))
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


dispatcher = {i: globals().get(f"move_{i}", move_0) for i in range(321)}


def get_events_from_move(ev: game_event.BattleSystemEvent):
    return dispatcher.get(ev.move.move_id, dispatcher[0])(ev)
