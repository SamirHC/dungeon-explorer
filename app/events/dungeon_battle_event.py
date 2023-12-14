import app.db.database as db
from app.db import dungeon_log_text
from app.events import game_event, event
from app.move import move_effects
from app.pokemon.animation_id import AnimationId


def get_events(ev: game_event.BattleSystemEvent):
    events = []
    if not ev.init:
        events.extend(get_init_events(ev))
        ev.init = True
    effect_events = move_effects.get_events_from_move(ev)
    if effect_events:
        events.extend(effect_events)
    else:
        events.extend(get_fail_events(ev))
    return events


def get_init_events(ev: game_event.BattleSystemEvent):
    events = []
    if ev.move is not db.move_db.REGULAR_ATTACK:
        text_surface = dungeon_log_text.use_move(ev.attacker, ev.move)
        events.append(game_event.LogEvent(text_surface).with_divider())
    return events


def get_attacker_move_animation_events(ev: game_event.BattleSystemEvent):
    res = []
    res.append(game_event.SetAnimationEvent(ev.attacker, AnimationId(ev.move.animation)))
    res.append(event.SleepEvent(20))
    return res


def get_fail_events(ev: game_event.BattleSystemEvent):
    if ev.move is db.move_db.REGULAR_ATTACK:
        return []
    text_surface = dungeon_log_text.move_fail()
    return [game_event.LogEvent(text_surface), event.SleepEvent(20)]
