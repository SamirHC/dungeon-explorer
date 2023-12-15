import random
from app.common.direction import Direction
from app.dungeon.dungeon import Dungeon
from app.events import event
from app.events import game_event
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.pokemon.stat import Stat
from app.common import text
from app.dungeon.battle_system import BattleSystem
from app.events import dungeon_battle_event
from app.move import move_effect_helpers
import app.db.database as db
from app.db import dungeon_log_text

from collections import deque


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
            game_event.StatusEvent: self.handle_status_event,
            game_event.DirectionEvent: self.handle_direction_event,
            game_event.StatAnimationEvent: self.handle_stat_animation_event,
            game_event.FlingEvent: self.handle_fling_event,
            game_event.BattleSystemEvent: self.handle_battle_system_event,
            game_event.MoveMissEvent: self.handle_move_miss_event,
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
        ev.target.status.hp.add(ev.amount)
        self.pop_event()

    def handle_faint_event(self, ev: game_event.FaintEvent):
        self.pop_event()
        defender = ev.target

        events = []
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
        defender.status.stat_stages[stat].add(ev.amount)
        after = stat_stage.value

        # Create Log Event
        change = after - before

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

    def handle_status_event(self, ev: game_event.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        self.pop_event()

    def handle_stat_animation_event(self, ev: game_event.StatAnimationEvent):
        ev.anim.update()
        if ev.anim.is_restarted():
            self.pop_event()

    def handle_fling_event(self, ev: game_event.FlingEvent):
        TILESIZE = 24
        if ev.destination is None:
            start = x0, y0 = ev.target.position
            possible_destinations = [
                pos
                for pos in self.floor.get_local_pokemon_positions(start)
                if self.floor[pos].pokemon_ptr not in self.floor.party
                and pos != ev.target.position
            ]
            if not possible_destinations:
                possible_destinations = [
                    pos
                    for pos in self.floor.get_local_ground_tiles_positions(start)
                    if self.floor[pos].pokemon_ptr not in self.floor.party
                    and pos != ev.target.position
                ]
            ev.destination = x1, y1 = random.choice(possible_destinations)

            # Calculate arc trajectory
            delta_x = (x1 - x0) * TILESIZE
            delta_y = (y1 - y0) * TILESIZE
            t = 12 + max(abs(delta_x), abs(delta_y))
            for i in range(t):
                ev.dx.append(round(i * delta_x / t))
                ev.dy.append(round(i * delta_y / t))
                ev.dh.append(0)

        if ev.dx:
            ev.t += 1
            ev.dx.pop(0)
            ev.dy.pop(0)
            ev.dh.pop(0)
            if ev.t % 6 == 0:
                ev.target.direction = ev.target.direction.anticlockwise()

        # Another arc if collides with pokemon
        if not ev.dx and self.floor.is_occupied(ev.destination):
            directions = list(Direction)
            random.shuffle(directions)
            for d in directions:
                x0, y0 = ev.target.position
                x1, y1 = ev.destination
                pos = x2, y2 = x1 + d.x, y1 + d.y
                if not self.floor.is_occupied(pos) and self.floor.is_ground(pos):
                    break
            delta_x = (x2 - x1) * TILESIZE
            delta_y = (y2 - y1) * TILESIZE
            vx = (x1 - x0) * TILESIZE
            vy = (y1 - y0) * TILESIZE
            t = 12 + max(abs(delta_x), abs(delta_y))
            for i in range(t):
                ev.dx.append(vx + round(i * delta_x / t))
                ev.dy.append(vy + round(i * delta_y / t))
                ev.dh.append(0)
            DAMAGE = 10
            # Collided pokemon
            p: Pokemon = self.floor[ev.destination].pokemon_ptr
            damage_text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(p.name_color)
                .write(p.data.name)
                .set_color(text.WHITE)
                .write(" took ")
                .set_color(text.CYAN)
                .write(f"{DAMAGE}")
                .set_color(text.WHITE)
                .write(" damage!")
                .build()
                .render()
            )
            self.event_queue.append(game_event.LogEvent(damage_text_surface))
            self.event_queue.append(game_event.DamageEvent(p, DAMAGE))

            # Flung pokemon
            damage_text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(ev.target.name_color)
                .write(ev.target.data.name)
                .set_color(text.WHITE)
                .write(" took ")
                .set_color(text.CYAN)
                .write(f"{DAMAGE}")
                .set_color(text.WHITE)
                .write(" damage!")
                .build()
                .render()
            )
            self.event_queue.append(game_event.LogEvent(damage_text_surface))
            self.event_queue.append(game_event.DamageEvent(ev.target, DAMAGE))
            ev.destination = pos

        if not ev.dx and not self.floor.is_occupied(ev.destination):
            self.floor[ev.target.position].pokemon_ptr = None
            ev.target.position = ev.destination
            self.floor[ev.target.position].pokemon_ptr = ev.target
            self.event_queue.append(
                game_event.SetAnimationEvent(ev.target, AnimationId.IDLE, True)
            )
            self.pop_event()

    def handle_battle_system_event(self, ev: game_event.BattleSystemEvent):
        self.pop_event()
        self.event_queue.extend(dungeon_battle_event.get_events(ev))

    def handle_move_miss_event(self, ev: game_event.MoveMissEvent):
        self.pop_event()
        text_surface = dungeon_log_text.move_miss(ev.defender)
        self.event_queue.extendleft(
            reversed([game_event.LogEvent(text_surface), event.SleepEvent(20)])
        )
