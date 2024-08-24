from collections import deque

from app.common.constants import RNG as random
from app.common.direction import Direction
from app.dungeon.dungeon import Dungeon
from app.events import event
from app.events import game_event
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.pokemon.stat import Stat
from app.gui import text
from app.dungeon.battle_system import BattleSystem
from app.events import dungeon_battle_event
import app.db.database as db
from app.db import dungeon_log_text


STAT_NAMES = {
    Stat.ATTACK: "Attack",
    Stat.DEFENSE: "Defense",
    Stat.SP_ATTACK: "Sp. Atk.",
    Stat.SP_DEFENSE: "Sp. Def.",
    Stat.ACCURACY: "accuracy",
    Stat.EVASION: "evasion",
}

DB_STAT_NAMES = {
    Stat.ATTACK: "attack",
    Stat.DEFENSE: "defense",
    Stat.SP_ATTACK: "sp_attack",
    Stat.SP_DEFENSE: "sp_defense",
    Stat.ACCURACY: "accuracy",
    Stat.EVASION: "evasion",
}


"""
Handles all dungeon events. May want to break down into separate event handlers
later.
"""


class DungeonEventHandler:
    def __init__(
        self,
        dungeon: Dungeon,
        event_queue: deque[event.Event],
        battlesystem: BattleSystem,
    ):
        self.dungeon = dungeon
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log
        self.event_queue = event_queue
        self.battlesystem = battlesystem

        self.dispatcher = {
            event.SleepEvent: self.handle_sleep_event,
            game_event.LogEvent: self.handle_log_event,
            game_event.SetAnimationEvent: self.handle_set_animation_event,
            game_event.DamageEvent: self.handle_damage_event,
            game_event.HealEvent: self.handle_heal_event,
            game_event.FaintEvent: self.handle_faint_event,
            game_event.StatStageChangeEvent: self.handle_stat_stage_change_event,
            game_event.StatDivideEvent: self.handle_stat_divide_event,
            game_event.StatusEvent: self.handle_status_event,
            game_event.DirectionEvent: self.handle_direction_event,
            game_event.StatAnimationEvent: self.handle_stat_animation_event,
            game_event.FlingEvent: self.handle_fling_event,
            game_event.BattleSystemEvent: self.handle_battle_system_event,
            game_event.MoveMissEvent: self.handle_move_miss_event,
            game_event.SetWeatherEvent: self.handle_set_weather_event,
        }

    def update(self):
        if self.event_queue:
            self.handle_event(self.event_queue[0])

    def handle_event(self, ev: event.Event):
        self.dispatcher.get(type(ev))(ev)

    def pop_event(self):
        self.event_queue.popleft()

    def handle_log_event(self, ev: game_event.LogEvent):
        if ev.new_divider:
            self.log.new_divider()
        self.log.write(ev.text_surface)
        self.pop_event()

    def handle_sleep_event(self, ev: event.SleepEvent):
        if ev.time > 0:
            ev.time -= 1
        else:
            self.pop_event()

    def handle_direction_event(self, ev: game_event.DirectionEvent):
        ev.target.direction = ev.direction
        self.pop_event()

    def handle_set_animation_event(self, ev: game_event.SetAnimationEvent):
        ev.target.animation_id = ev.animation_id
        if ev.reset_to:
            ev.target.sprite.reset_to = ev.animation_id
        self.pop_event()

    def handle_damage_event(self, ev: game_event.DamageEvent):
        ev.target.status.hp.add(-ev.amount)
        self.pop_event()

        is_fainted = ev.target.status.is_fainted()

        follow_up = [
            game_event.SetAnimationEvent(ev.target, AnimationId.HURT, is_fainted),
            event.SleepEvent(20),
        ]
        if is_fainted:
            follow_up.append(game_event.FaintEvent(ev.target))

        self.event_queue.extendleft(reversed(follow_up))

    def handle_heal_event(self, ev: game_event.HealEvent):
        self.pop_event()

        target = ev.target
        amount = ev.amount

        before = target.status.hp.value
        target.status.hp.add(amount)
        after = target.status.hp.value

        change = after - before

        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(target.name_color)
            .write(target.data.name)
            .set_color(text.WHITE)
        )
        if change == 0:
            (
                tb.write("'s")
                .set_color(text.CYAN)
                .write(" HP")
                .set_color(text.WHITE)
                .write(" didn't change.")
            )
        else:
            (
                tb.write(" recovered ")
                .set_color(text.CYAN)
                .write(f"{change} HP")
                .set_color(text.WHITE)
                .write("!")
            )
        events = []
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        self.event_queue.extendleft(reversed(events))

    def handle_faint_event(self, ev: game_event.FaintEvent):
        self.pop_event()
        defender = ev.target

        events = []
        if defender is self.floor.party.leader:
            # Replace with more verbose defeat message
            events.append(game_event.LogEvent(dungeon_log_text.defeated(defender)))
            events.append(event.SleepEvent(100))
        else:
            events.append(game_event.LogEvent(dungeon_log_text.defeated(defender)))
            events.append(event.SleepEvent(20))

        self.floor[ev.target.position].pokemon_ptr = None
        if ev.target.is_enemy:
            self.floor.active_enemies.remove(ev.target)
        else:
            self.party.standby(ev.target)
        self.floor.spawned.remove(ev.target)

        self.event_queue.extendleft(reversed(events))

    def handle_stat_stage_change_event(self, ev: game_event.StatStageChangeEvent):
        self.pop_event()

        # Extract data from event object
        defender = ev.target
        stat = ev.stat
        amount = ev.amount

        if defender.status.is_fainted():
            return

        # Modify stat
        stat_stage = defender.status.stat_stages[stat]
        before = stat_stage.value
        stat_stage.add(ev.amount)
        after = stat_stage.value

        # Create Log Event
        change = after - before

        stat_name = STAT_NAMES[stat]
        db_stat_name = DB_STAT_NAMES[stat]

        description = f"'s {stat_name} "
        if amount < 0:
            anim_type = 0
        elif amount > 0:
            anim_type = 1

        if change < -1:
            description += "fell sharply!"
        elif change == -1:
            description += "fell slightly!"
        elif change == 0 and amount < 0:
            description += "cannot go any lower!"
        elif change == 0 and amount > 0:
            description += "cannot go any higher!"
        elif change == 1:
            description += "rose slightly!"
        elif change > 1:
            description += "rose sharply!"

        follow_up = [
            game_event.LogEvent(
                (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(defender.name_color)
                    .write(defender.data.name)
                    .set_color(text.WHITE)
                    .write(description)
                    .build()
                    .render()
                )
            ),
            game_event.StatAnimationEvent(
                defender, db.statanimation_db[db_stat_name, anim_type]
            ),
            event.SleepEvent(20),
        ]
        self.event_queue.extendleft(reversed(follow_up))

    def handle_stat_divide_event(self, ev: game_event.StatDivideEvent):
        self.pop_event()

        # Extract data from event object
        defender = ev.target
        stat = ev.stat

        if defender.status.is_fainted():
            return

        # Modify stat
        stat_divide_stage = defender.status.stat_divider[stat]
        before = stat_divide_stage.value
        stat_divide_stage.add(ev.amount)
        after = stat_divide_stage.value

        # Create Log Event
        change = after - before

        stat_name = STAT_NAMES[stat]
        db_stat_name = DB_STAT_NAMES[stat]

        description = f"'s {stat_name} "

        if change > 0:
            description += "fell sharply!"
        else:
            description += "cannot go any lower!"

        follow_up = [
            game_event.LogEvent(
                (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(defender.name_color)
                    .write(defender.data.name)
                    .set_color(text.WHITE)
                    .write(description)
                    .build()
                    .render()
                )
            ),
            game_event.StatAnimationEvent(
                defender, db.statanimation_db[db_stat_name, 0]
            ),
            event.SleepEvent(20),
        ]
        self.event_queue.extendleft(reversed(follow_up))

    def handle_status_event(self, ev: game_event.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        self.pop_event()

    def handle_stat_animation_event(self, ev: game_event.StatAnimationEvent):
        ev.anim.update()
        if ev.anim.is_restarted():
            self.pop_event()

    def handle_fling_event(self, ev: game_event.FlingEvent):
        self.pop_event()
        TILESIZE = 24
        SPIN_RATE = 6
        DAMAGE = 10

        events = []

        if ev.destination is None:
            # Display message
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(ev.pokemon.name_color)
                .write(ev.pokemon.data.name)
                .set_color(text.WHITE)
                .write(" was sent flying!")
                .build()
                .render()
            )
            events.append(
                game_event.SetAnimationEvent(ev.pokemon, AnimationId.HURT, True)
            )
            events.append(game_event.LogEvent(text_surface))
            events.append(ev)
            # Get location thrown to
            start = x0, y0 = ev.pokemon.position
            possible_destinations = [
                pos
                for pos in self.floor.get_local_pokemon_positions(start)
                if self.floor[pos].pokemon_ptr not in self.floor.party
                and pos != ev.pokemon.position
            ]
            if not possible_destinations:
                possible_destinations = [
                    pos
                    for pos in self.floor.get_local_ground_tiles_positions(start)
                    if self.floor[pos].pokemon_ptr not in self.floor.party
                    and pos != ev.pokemon.position
                ]

            ev.destination = x1, y1 = random.choice(possible_destinations)

            # Calculate arc trajectory
            delta_x = (x1 - x0) * TILESIZE
            delta_y = (y1 - y0) * TILESIZE
            t = 12 + max(abs(delta_x), abs(delta_y))
            for i in range(t):
                ev.x.append(ev.pokemon.moving_entity.x + round(i * delta_x / t))
                ev.y.append(ev.pokemon.moving_entity.y + round(i * delta_y / t))

        elif ev.x:
            ev.t += 1
            ev.pokemon.moving_entity.x = ev.x.pop(0)
            ev.pokemon.moving_entity.y = ev.y.pop(0)
            if ev.t % SPIN_RATE == 0:
                ev.pokemon.direction = ev.pokemon.direction.anticlockwise()
            self.event_queue.appendleft(ev)

        # Another arc if collides with pokemon
        elif self.floor.is_occupied(ev.destination):
            directions = list(Direction)
            random.shuffle(directions)
            for d in directions:
                x0, y0 = ev.pokemon.position
                x1, y1 = ev.destination
                pos = x2, y2 = x1 + d.x, y1 + d.y
                if not self.floor.is_occupied(pos) and self.floor.is_ground(pos):
                    break
            delta_x = (x2 - x1) * TILESIZE
            delta_y = (y2 - y1) * TILESIZE
            t = 12 + max(abs(delta_x), abs(delta_y))
            for i in range(t):
                ev.x.append(ev.pokemon.moving_entity.x + round(i * delta_x / t))
                ev.y.append(ev.pokemon.moving_entity.y + round(i * delta_y / t))

            # Collided pokemon
            other: Pokemon = self.floor[ev.destination].pokemon_ptr
            other_text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(other.name_color)
                .write(other.data.name)
                .set_color(text.WHITE)
                .write(" took ")
                .set_color(text.CYAN)
                .write(f"{DAMAGE}")
                .set_color(text.WHITE)
                .write(" damage!")
                .build()
                .render()
            )

            # Flung pokemon
            damage_text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(ev.pokemon.name_color)
                .write(ev.pokemon.data.name)
                .set_color(text.WHITE)
                .write(" took ")
                .set_color(text.CYAN)
                .write(f"{DAMAGE}")
                .set_color(text.WHITE)
                .write(" damage!")
                .build()
                .render()
            )
            events.append(ev)
            events.append(game_event.SetAnimationEvent(other, AnimationId.HURT))
            events.append(game_event.LogEvent(other_text_surface))
            events.append(game_event.DamageEvent(other, DAMAGE))
            events.append(game_event.LogEvent(damage_text_surface))
            events.append(game_event.DamageEvent(ev.pokemon, DAMAGE))
            ev.destination = pos

        else:
            self.floor[ev.pokemon.position].pokemon_ptr = None
            ev.pokemon.position = ev.destination
            self.floor[ev.pokemon.position].pokemon_ptr = ev.pokemon
            events.append(
                game_event.SetAnimationEvent(ev.pokemon, AnimationId.IDLE, True)
            )

        self.event_queue += events

    def handle_battle_system_event(self, ev: game_event.BattleSystemEvent):
        self.pop_event()
        self.event_queue.extend(dungeon_battle_event.get_events(ev))

    def handle_move_miss_event(self, ev: game_event.MoveMissEvent):
        self.pop_event()
        text_surface = dungeon_log_text.move_miss(ev.defender)
        self.event_queue.extendleft(
            reversed([game_event.LogEvent(text_surface), event.SleepEvent(20)])
        )

    def handle_set_weather_event(self, ev: game_event.SetWeatherEvent):
        self.pop_event()
        self.dungeon.set_weather(ev.weather)
        weather_text = text.TextBuilder.build_white(
            f" Weather: {ev.weather.value.capitalize()}"
        ).render()
        events = []
        events.append(game_event.LogEvent(weather_text))
        events.append(event.SleepEvent(20))
        self.event_queue.extendleft(reversed(events))
