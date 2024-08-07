import math
import random

from app.dungeon.dungeon import Dungeon
from app.model.type import TypeEffectiveness
from app.move.move import MoveCategory
from app.gui import text
from app.move import damage_mechanics
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.pokemon.status_effect import StatusEffect
from app.dungeon import target_getter
from app.events import game_event, event
from app.db import dungeon_log_text
import app.db.database as db


def get_attacker_move_animation_events(ev: game_event.BattleSystemEvent):
    events = []
    events.append(
        game_event.SetAnimationEvent(ev.attacker, AnimationId(ev.move.animation))
    )
    events.append(event.SleepEvent(20))
    return events


# TODO: Miss sfx, Miss gfx label
def get_miss_events(defender: Pokemon):
    return [game_event.MoveMissEvent(defender)]


# TODO: No dmg sfx (same as miss sfx)
def get_no_damage_events(defender: Pokemon):
    text_surface = dungeon_log_text.no_damage(defender)
    return [game_event.LogEvent(text_surface), event.SleepEvent(20)]


def get_calamitous_damage_events(defender: Pokemon):
    text_surface = dungeon_log_text.calamatous_damage(defender)
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.DamageEvent(defender, 9999))
    return events


# TODO: Damage sfx, Defender hurt animation
def get_damage_events(ev: game_event.BattleSystemEvent, defender: Pokemon, damage: int):
    if damage == 0:
        return get_no_damage_events(defender)
    elif damage >= 9999:
        return get_calamitous_damage_events(defender)
    events = []
    effectiveness = db.type_chart.get_move_effectiveness(
        ev.move.type, defender.data.type
    )
    if effectiveness is not TypeEffectiveness.REGULAR:
        effectiveness_text_surface = text.TextBuilder.build_white(effectiveness.get_message())
        events.append(game_event.LogEvent(effectiveness_text_surface))
    damage_text_surface = dungeon_log_text.damage(defender, damage)
    events.append(game_event.LogEvent(damage_text_surface))
    events.append(game_event.DamageEvent(defender, damage))

    if (
        defender.status.has_status_effect(StatusEffect.VITAL_THROW)
        and ev.move.category is MoveCategory.PHYSICAL
        and abs(ev.attacker.x - defender.x) <= 1
        and abs(ev.attacker.y - defender.y) <= 1
    ):
        events.append(game_event.FlingEvent(ev.attacker))

    return events


def get_recoil_events(ev: game_event.BattleSystemEvent, percent: float):
    damage = math.ceil(ev.attacker.status.hp.max_value * percent / 100)
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(ev.attacker.name_color)
        .write(ev.attacker.data.name)
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
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.DamageEvent(ev.attacker, damage))
    return events


def get_burn_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" sustained a burn!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "burned", True))
    events.append(game_event.SetAnimationEvent(defender, AnimationId.HURT))
    events.append(event.SleepEvent(20))
    return events


def get_freeze_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" is frozen solid!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "frozen", True))
    events.append(event.SleepEvent(20))
    return events


def get_poisoned_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" was poisoned!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "poisoned", True))
    events.append(event.SleepEvent(20))
    return events


def get_badly_poisoned_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" was badly poisoned!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "badly_poisoned", True))
    events.append(event.SleepEvent(20))
    return events


def get_confusion_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" is confused!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(event.SleepEvent(20))
    return events


def get_paralyze_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" is paralyzed!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "paralyzed", True))
    events.append(event.SleepEvent(20))
    return events


def get_constricted_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" is constricted!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "constriction", True))
    events.append(event.SleepEvent(20))
    return events


def get_cringe_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" cringed!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.StatusEvent(defender, "cringe", True))
    events.append(event.SleepEvent(20))
    return events


def get_asleep_events(dungeon: Dungeon, defender: Pokemon):
    defender.status.clear_affliction(StatusEffect.YAWNING)
    tb = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
    )
    if defender.status.is_asleep():
        tb.write(" is already asleep!")
    else:
        defender.status.afflict(
            StatusEffect.ASLEEP, dungeon.turns.value + random.randint(3, 6)
        )
        tb.write(" fell asleep!")

    events = []
    events.append(game_event.SetAnimationEvent(defender, AnimationId.SLEEP, True))
    events.append(game_event.LogEvent(tb.build().render()))
    events.append(event.SleepEvent(20))
    return events


def get_awaken_events(defender: Pokemon):
    events = []
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" woke up!")
        .build()
        .render()
    )
    events.append(game_event.LogEvent(text_surface).with_divider())
    events.append(game_event.SetAnimationEvent(defender, AnimationId.IDLE, True))
    events.append(event.SleepEvent(20))
    return events


def get_events_on_target(
    ev: game_event.BattleSystemEvent, defender: Pokemon, hit_function
):
    res = []
    if damage_mechanics.calculate_accuracy(ev.dungeon, ev.attacker, defender, ev.move):
        res += hit_function(ev, defender)
    else:
        res += get_miss_events(defender)
    return res


def get_events_on_all_targets(ev: game_event.BattleSystemEvent, hit_function):
    res = []
    for target in target_getter.get_targets(
        ev.attacker, ev.dungeon, ev.move.move_range
    ):
        defender = target
        res += get_events_on_target(ev, defender, hit_function)
    return res


def get_basic_attack_events(ev: game_event.BattleSystemEvent, defender: Pokemon):
    damage = damage_mechanics.calculate_damage(
        ev.dungeon, ev.attacker, defender, ev.move
    )
    return get_damage_events(ev, defender, damage)
