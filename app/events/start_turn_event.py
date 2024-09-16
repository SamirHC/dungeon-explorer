from app.dungeon.dungeon import Dungeon
from app.pokemon.pokemon import Pokemon
from app.pokemon.status_effect import StatusEffect
from app.pokemon.animation_id import AnimationId
from app.events import event, game_event
from app.move import move_effect_helpers
from app.gui import text
import app.db.move as move_db


# Expired Status Events
def get_expired_yawning_events(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    return move_effect_helpers.get_asleep_events(dungeon, pokemon)


def get_expired_asleep_events(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    return move_effect_helpers.get_awaken_events(pokemon)


def get_expired_nightmare_events(
    dungeon: Dungeon, pokemon: Pokemon
) -> list[event.Event]:
    pokemon.status.clear_affliction(StatusEffect.NIGHTMARE)
    DAMAGE = 8
    events = []
    events.append(game_event.LogEvent(text.TextBuilder()
        .set_shadow(True)
        .set_color(pokemon.name_color)
        .write(pokemon.base.name)
        .set_color(text.WHITE)
        .write(" awoke from its nightmare\nand took ")
        .set_color(text.CYAN)
        .write(str(DAMAGE))
        .set_color(text.WHITE)
        .write(" damage!")
        .build()))
    events.append(game_event.DamageEvent(pokemon, DAMAGE))
    events.append(game_event.SetAnimationEvent(pokemon, AnimationId.IDLE, True))
    return events


def get_expired_vital_throw_events(
    dungeon: Dungeon, pokemon: Pokemon
) -> list[event.Event]:
    events = []
    events.append(game_event.LogEvent(text.TextBuilder()
        .set_shadow(True)
        .set_color(pokemon.name_color)
        .write(pokemon.base.name)
        .set_color(text.WHITE)
        .write("'s Vital Throw status faded.")
        .build()))
    events.append(event.SleepEvent(20))
    return events


def get_expired_dig_events(dungeon: Dungeon, pokemon: Pokemon):
    pokemon.has_turn = False
    events = []
    DIG = move_db.load(8)
    events.append(game_event.SetAnimationEvent(pokemon, AnimationId(DIG.animation)))
    events += move_effect_helpers.get_events_on_all_targets(
        game_event.BattleSystemEvent(dungeon, pokemon, DIG),
        move_effect_helpers.get_basic_attack_events,
    )
    events.append(event.SleepEvent(20))
    return events


def get_expired_confused_events(dungeon: Dungeon, pokemon: Pokemon):
    events = []
    events.append(game_event.LogEvent(text.TextBuilder()
        .set_shadow(True)
        .set_color(pokemon.name_color)
        .write(pokemon.base.name)
        .set_color(text.WHITE)
        .write(" is no longer confused.")
        .build()))
    events.append(event.SleepEvent(20))
    return events


expired_status_dispatcher = {
    StatusEffect.YAWNING: get_expired_yawning_events,
    StatusEffect.ASLEEP: get_expired_asleep_events,
    StatusEffect.NIGHTMARE: get_expired_nightmare_events,
    StatusEffect.VITAL_THROW: get_expired_vital_throw_events,
    StatusEffect.DIGGING: get_expired_dig_events,
    StatusEffect.CONFUSED: get_expired_confused_events,
}


# Current Status Events
def get_current_asleep_events(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    pokemon.has_turn = False
    events = []
    # Only to alert user why they cannot make a move.
    if pokemon is dungeon.party.leader:
        events.append(game_event.LogEvent(text.TextBuilder()
            .set_shadow(True)
            .set_color(pokemon.name_color)
            .write(pokemon.base.name)
            .set_color(text.WHITE)
            .write(" is asleep!")
            .build()).with_divider())
        events.append(event.SleepEvent(20))
    return events


def get_current_nightmare_events(
    dungeon: Dungeon, pokemon: Pokemon
) -> list[event.Event]:
    return get_current_asleep_events(dungeon, pokemon)


current_status_dispatcher = {
    StatusEffect.ASLEEP: get_current_asleep_events,
    StatusEffect.NIGHTMARE: get_current_nightmare_events,
}


def start_turn(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    events = []

    expired_statuses = pokemon.status.get_expired(dungeon.turns.value)
    pokemon.status.remove_statuses(expired_statuses)

    for status in expired_statuses:
        events += expired_status_dispatcher.get(status, lambda p, d: [])(
            dungeon, pokemon
        )

    current_statuses = pokemon.status.status_conditions
    for status in current_statuses:
        events += current_status_dispatcher.get(status, lambda p, d: [])(
            dungeon, pokemon
        )

    pokemon.has_started_turn = True
    return events
