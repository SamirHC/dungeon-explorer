import app.db.database as db
from app.db import dungeon_log_text
from app.events import gameevent, event
from app.move import move_effects


def get_events(ev: gameevent.BattleSystemEvent):
    events = []
    events.extend(get_init_events(ev))
    effect_events = move_effects.get_events_from_move(ev)
    if effect_events:
        events.extend(effect_events)
    else:
        events.extend(get_fail_events(ev))
    return events


def get_init_events(ev: gameevent.BattleSystemEvent):
    events = []
    if ev.move is not db.move_db.REGULAR_ATTACK:
        text_surface = dungeon_log_text.use_move(ev.attacker, ev.move)
        events.append(gameevent.LogEvent(text_surface).with_divider())
    # Skip for:
    # Thrash(9)
    if ev.move.move_id != 9:
        events += get_attacker_move_animation_events(ev)
    return events


def get_attacker_move_animation_events(ev: gameevent.BattleSystemEvent):
    res = []
    res.append(gameevent.SetAnimationEvent(ev.attacker, ev.move.animation))
    res.append(event.SleepEvent(20))
    return res


def get_fail_events(ev: gameevent.BattleSystemEvent):
    if ev.move is db.move_db.REGULAR_ATTACK:
        return []
    text_surface = dungeon_log_text.move_fail()
    return [gameevent.LogEvent(text_surface), event.SleepEvent(20)]
