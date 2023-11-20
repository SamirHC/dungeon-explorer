import random
from app.common.direction import Direction
from app.dungeon.dungeon import Dungeon
from app.events import event
from app.events import gameevent
from app.pokemon.pokemon import Pokemon
from app.pokemon import pokemon_data
from app.common import text
from app.dungeon.battle_system import BattleSystem

from collections import deque


"""
Handles all dungeon events. May want to break down into separate event handlers
later.
"""
class DungeonEventHandler:
    def __init__(self, dungeon: Dungeon, event_queue: deque[event.Event], battlesystem: BattleSystem):
        self.dungeon = dungeon
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log
        self.event_queue = event_queue
        self.battlesystem = battlesystem

    def update(self):
        if self.event_queue:
            self.handle_event(self.event_queue[0])
        
    def handle_event(self, ev: event.Event):
        if isinstance(ev, gameevent.LogEvent):
            self.handle_log_event(ev)
        elif isinstance(ev, event.SleepEvent):
            self.handle_sleep_event(ev)
        elif isinstance(ev, gameevent.SetAnimationEvent):
            self.handle_set_animation_event(ev)
        elif isinstance(ev, gameevent.DamageEvent):
            defender = ev.target
            self.handle_damage_event(ev)
            follow_up = [
                gameevent.SetAnimationEvent(defender, defender.sprite.HURT_ANIMATION_ID),
                event.SleepEvent(20)
            ]
            if defender.hp_status == 0:
                follow_up += self.battlesystem.get_faint_events(defender)
            self.event_queue.extendleft(reversed(follow_up))
        elif isinstance(ev, gameevent.HealEvent):
            self.handle_heal_event(ev)
        elif isinstance(ev, gameevent.FaintEvent):
            self.handle_faint_event(ev)
        elif isinstance(ev, gameevent.StatChangeEvent):
            self.handle_stat_change_event(ev)
        elif isinstance(ev, gameevent.StatusEvent):
            self.handle_status_event(ev)
        elif isinstance(ev, gameevent.DirectionEvent):
            self.handle_direction_event(ev)
        elif isinstance(ev, gameevent.StatAnimationEvent):
            self.handle_stat_animation_event(ev)
        elif isinstance(ev, gameevent.FlingEvent):
            self.handle_fling_event(ev)
        else:
            raise RuntimeError(f"Event not handled!: {ev}")

    def handle_log_event(self, ev: gameevent.LogEvent):
        if ev.new_divider:
            self.log.new_divider()
        self.log.write(ev.text_surface)
        self.event_queue.popleft()

    def handle_sleep_event(self, ev: event.SleepEvent):
        if ev.time > 0:
            ev.time -= 1
        else:
            self.event_queue.popleft()
    
    def handle_direction_event(self, ev: gameevent.DirectionEvent):
        ev.target.direction = ev.direction
        self.event_queue.popleft()
    
    def handle_set_animation_event(self, ev: gameevent.SetAnimationEvent):
        ev.target.animation_id = ev.animation_name
        if ev.reset_to:
            ev.target.sprite.reset_to = ev.animation_name
        self.event_queue.popleft()

    def handle_damage_event(self, ev: gameevent.DamageEvent):
        ev.target.status.hp.reduce(ev.amount)
        self.event_queue.popleft()

    def handle_heal_event(self, ev: gameevent.HealEvent):
        ev.target.status.hp.increase(ev.amount)
        self.event_queue.popleft()
    
    def handle_faint_event(self, ev: gameevent.FaintEvent):
        self.floor[ev.target.position].pokemon_ptr = None
        if ev.target.is_enemy:
            self.floor.active_enemies.remove(ev.target)
        else:
            self.party.standby(ev.target)
        self.floor.spawned.remove(ev.target)
        self.defender_fainted = False
        self.event_queue.popleft()

    def handle_stat_change_event(self, ev: gameevent.StatChangeEvent):
        statistic: pokemon_data.Statistic = getattr(ev.target.status, ev.stat)
        statistic.increase(ev.amount)
        self.event_queue.popleft()

    def handle_status_event(self, ev: gameevent.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        self.event_queue.popleft()

    def handle_stat_animation_event(self, ev: gameevent.StatAnimationEvent):
        ev.anim.update()
        if ev.anim.is_restarted():
            self.event_queue.popleft()

    def handle_fling_event(self, ev: gameevent.FlingEvent):
        TILESIZE = 24
        if ev.destination is None:
            start = x0, y0 = ev.target.position
            possible_destinations = [
                pos for pos in self.floor.get_local_pokemon_positions(start)
                if self.floor[pos].pokemon_ptr not in self.floor.party
                and pos != ev.target.position
            ]
            if not possible_destinations:
                possible_destinations = [
                    pos for pos in self.floor.get_local_ground_tiles_positions(start)
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
                .write(p.name)
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
                .write(ev.target.name)
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
            self.event_queue.append(gameevent.SetAnimationEvent(ev.target, ev.target.sprite.IDLE_ANIMATION_ID, True))
            self.event_queue.popleft()
