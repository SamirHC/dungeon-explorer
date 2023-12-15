from app.dungeon.dungeon import Dungeon
from app.pokemon.pokemon import Pokemon
from app.pokemon.status_effect import StatusEffect
from app.events import event, game_event
from app.move import move_effect_helpers
from app.common import text


# Expired Status Events
def get_expired_yawning_events(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    return move_effect_helpers.get_asleep_events(dungeon, pokemon)


def get_expired_asleep_events(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    return move_effect_helpers.get_awaken_events(pokemon)


expired_status_dispatcher = {
    StatusEffect.YAWNING: get_expired_yawning_events,
    StatusEffect.ASLEEP: get_expired_asleep_events,
}


# Current Status Events
def get_current_asleep_events(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    pokemon.has_turn = False
    events = []
    # Only to alert user why they cannot make a move.
    if pokemon is dungeon.user:
        text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(pokemon.name_color)
            .write(pokemon.data.name)
            .set_color(text.WHITE)
            .write(" is asleep!")
            .build()
            .render()
        )
        events.append(game_event.LogEvent(text_surface).with_divider())
        events.append(event.SleepEvent(20))
    return events


current_status_dispatcher = {
    StatusEffect.ASLEEP: get_current_asleep_events,
}


def start_turn(dungeon: Dungeon, pokemon: Pokemon) -> list[event.Event]:
    events = []

    expired_statuses = pokemon.status.get_expired(dungeon.turns.value)
    pokemon.status.remove_statuses(expired_statuses)
    """
    if p.status.vital_throw:
        p.status.vital_throw -= 1
        if p.status.vital_throw == 0:
            text_surface = (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(p.name_color)
                    .write(p.name)
                    .set_color(text.WHITE)
                    .write("'s Vital Throw status faded.")
                    .build()
                    .render()
                )
            self.event_queue.append(gameevent.LogEvent(text_surface))
            self.event_queue.append(SleepEvent(20))
    """
    """
        if self.user.has_status_effect(StatusEffect.DIGGING):
            self.user.has_turn = False
            self.battle_system.attacker = self.user
            self.battle_system.target_getter.attacker = self.user
            self.event_queue.extend(self.battle_system.get_dig_events())
    """
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
