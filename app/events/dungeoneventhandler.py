import random
from app.common.direction import Direction
from app.dungeon.dungeon import Dungeon
from app.events import event
from app.events import gameevent
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.common import text
from app.model.statistic import Statistic
from app.dungeon.battle_system import BattleSystem
from app.events import dungeon_battle_event
from app.move import move_effect_helpers

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
            gameevent.LogEvent: self.handle_log_event,
            gameevent.SetAnimationEvent: self.handle_set_animation_event,
            gameevent.DamageEvent: self.handle_damage_event,
            gameevent.HealEvent: self.handle_heal_event,
            gameevent.FaintEvent: self.handle_faint_event,
            gameevent.StatChangeEvent: self.handle_stat_change_event,
            gameevent.StatusEvent: self.handle_status_event,
            gameevent.DirectionEvent: self.handle_direction_event,
            gameevent.StatAnimationEvent: self.handle_stat_animation_event,
            gameevent.FlingEvent: self.handle_fling_event,
            gameevent.BattleSystemEvent: self.handle_battle_system_event,
        }

    def update(self):
        if self.event_queue:
            self.handle_event(self.event_queue[0])

    def handle_event(self, ev: event.Event):
        try:
            self.dispatcher.get(type(ev))(ev)
        except KeyError as e:
            print(f"KeyError: {e} is not handled!")

    def pop_event(self):
        self.event_queue.popleft()

    def handle_log_event(self, ev: gameevent.LogEvent):
        if ev.new_divider:
            self.log.new_divider()
        self.log.write(ev.text_surface)
        self.pop_event()

    def handle_sleep_event(self, ev: event.SleepEvent):
        if ev.time > 0:
            ev.time -= 1
        else:
            self.pop_event()

    def handle_direction_event(self, ev: gameevent.DirectionEvent):
        ev.target.direction = ev.direction
        self.pop_event()

    def handle_set_animation_event(self, ev: gameevent.SetAnimationEvent):
        ev.target.animation_id = ev.animation_id
        if ev.reset_to:
            ev.target.sprite.reset_to = ev.animation_id
        self.pop_event()

    def handle_damage_event(self, ev: gameevent.DamageEvent):
        ev.target.status.hp.reduce(ev.amount)
        self.pop_event()

        follow_up = [
            gameevent.SetAnimationEvent(ev.target, AnimationId.HURT),
            event.SleepEvent(20),
        ]
        if ev.target.status.hp.value == 0:
            follow_up.extend(move_effect_helpers.get_faint_events(ev.target))
        self.event_queue.extendleft(reversed(follow_up))

    def handle_heal_event(self, ev: gameevent.HealEvent):
        ev.target.status.hp.increase(ev.amount)
        self.pop_event()

    def handle_faint_event(self, ev: gameevent.FaintEvent):
        self.floor[ev.target.position].pokemon_ptr = None
        if ev.target.is_enemy:
            self.floor.active_enemies.remove(ev.target)
        else:
            self.party.standby(ev.target)
        self.floor.spawned.remove(ev.target)
        self.defender_fainted = False
        self.pop_event()

    def handle_stat_change_event(self, ev: gameevent.StatChangeEvent):
        statistic: Statistic = getattr(ev.target.status, ev.stat)
        statistic.increase(ev.amount)
        self.pop_event()

    def handle_status_event(self, ev: gameevent.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        self.pop_event()

    def handle_stat_animation_event(self, ev: gameevent.StatAnimationEvent):
        ev.anim.update()
        if ev.anim.is_restarted():
            self.pop_event()

    def handle_fling_event(self, ev: gameevent.FlingEvent):
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
            self.event_queue.append(gameevent.LogEvent(damage_text_surface))
            self.event_queue.append(gameevent.DamageEvent(p, DAMAGE))

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
            self.event_queue.append(gameevent.LogEvent(damage_text_surface))
            self.event_queue.append(gameevent.DamageEvent(ev.target, DAMAGE))
            ev.destination = pos

        if not ev.dx and not self.floor.is_occupied(ev.destination):
            self.floor[ev.target.position].pokemon_ptr = None
            ev.target.position = ev.destination
            self.floor[ev.target.position].pokemon_ptr = ev.target
            self.event_queue.append(
                gameevent.SetAnimationEvent(
                    ev.target, AnimationId.IDLE, True
                )
            )
            self.pop_event()

    def handle_battle_system_event(self, ev: gameevent.BattleSystemEvent):
        self.pop_event()
        self.event_queue.extend(dungeon_battle_event.get_events(ev))
