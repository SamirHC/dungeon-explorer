import math

from app.model.type import TypeEffectiveness
from app.move.move import MoveCategory
from app.common import text
from app.move import damage_mechanics
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.pokemon.status_effect import StatusEffect
from app.dungeon import target_getter
from app.events import game_event, event
from app.db import dungeon_log_text
import app.db.database as db


# TODO: Miss sfx, Miss gfx label
def get_miss_events(defender: Pokemon):
    text_surface = dungeon_log_text.move_miss(defender)
    return [game_event.LogEvent(text_surface), event.SleepEvent(20)]


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
    effectiveness = db.type_chart.get_move_effectiveness(ev.move.type, defender.data.type)
    if effectiveness is not TypeEffectiveness.REGULAR:
        effectiveness_text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(effectiveness.get_message())
            .build()
            .render()
        )
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
        defender = ev.attacker
        events += get_fling_events()
    return events


def get_faint_events(defender: Pokemon):
    text_surface = dungeon_log_text.defeated(defender)
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.FaintEvent(defender))
    events.append(event.SleepEvent(20))
    return events


def get_heal_events(defender: Pokemon, heal: int):
    p = defender
    tb = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(p.name_color)
        .write(p.data.name)
        .set_color(text.WHITE)
    )
    if p.status.hp.value == p.stats.hp.value or heal == 0:
        (
            tb.write("'s")
            .set_color(text.CYAN)
            .write(" HP")
            .set_color(text.WHITE)
            .write(" didn't change.")
        )
    elif heal + p.status.hp.value >= p.stats.hp.value:
        heal = p.stats.hp.value - p.status.hp.value
        (
            tb.write(" recovered ")
            .set_color(text.CYAN)
            .write(f"{heal} HP")
            .set_color(text.WHITE)
            .write("!")
        )
    text_surface = tb.build().render()
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.HealEvent(p, heal))
    events.append(event.SleepEvent(20))
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
    events.append(
        game_event.SetAnimationEvent(defender, AnimationId.HURT)
    )
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
    events.append(game_event.StatusEvent(defender, "confused", True))
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


def get_asleep_events(defender: Pokemon):
    defender.status.clear_affliction(StatusEffect.YAWNING)
    if defender.status.has_status_effect(StatusEffect.ASLEEP):
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
            .write(" is already asleep!")
            .build()
            .render()
        )
    else:
        defender.status.afflict(StatusEffect.ASLEEP)  # = random.randint(3, 6)
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
            .write(" fell asleep!")
            .build()
            .render()
        )

    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(
        game_event.SetAnimationEvent(defender, AnimationId.SLEEP, True)
    )
    events.append(event.SleepEvent(20))
    return events


def get_nightmare_events(defender: Pokemon):
    defender.status.clear_affliction(StatusEffect.NIGHTMARE)
    damage = 8
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
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
    events.append(game_event.LogEvent(text_surface))
    events.append(game_event.DamageEvent(defender, damage))
    events.append(
        game_event.SetAnimationEvent(defender, AnimationId.IDLE, True)
    )
    return events


def get_awaken_events(defender: Pokemon):
    events = []
    if defender.status.has_status_effect(StatusEffect.NIGHTMARE):
        events += get_nightmare_events()
    else:
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
        events.append(
            game_event.SetAnimationEvent(
                defender, AnimationId.IDLE, True
            )
        )
        events.append(event.SleepEvent(20))
    return events


def get_fling_events(defender: Pokemon):
    text_surface = (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(defender.name_color)
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" was sent flying!")
        .build()
        .render()
    )
    events = []
    events.append(game_event.LogEvent(text_surface))
    events.append(
        game_event.SetAnimationEvent(defender, AnimationId.HURT, True)
    )
    events.append(game_event.FlingEvent(defender))
    return events

"""
def get_dig_events(attacker: Pokemon):
    events = []
    move = db.move_db[8]
    events.append(gameevent.StatusEvent(attacker, "digging", False))
    events.append(gameevent.SetAnimationEvent(attacker, AnimationId(move.animation)))
    events += get_all_basic_attack_or_miss_events()
    events.append(event.SleepEvent(20))
    return events
"""

"""
def is_move_animation_event(target: Pokemon) -> bool:
    if not events:
        return False
    ev = events[0]
    if isinstance(ev, gameevent.StatAnimationEvent):
        return ev.target is target


def render() -> pygame.Surface:
    ev = events[0]
    if isinstance(ev, gameevent.StatAnimationEvent):
        return ev.anim.get_current_frame()
"""


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
