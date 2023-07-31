from app.dungeon.dungeon import Dungeon
from app.events import event
from app.events import gameevent
from app.pokemon import pokemon
from app.pokemon import pokemondata

from collections import deque


"""
Handles all dungeon events. May want to break down into separate event handlers
later.
"""
class DungeonEventHandler:
    def __init__(self, dungeon: Dungeon, event_queue: deque[event.Event]):
        self.dungeon = dungeon
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log
        self.event_queue = event_queue

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
            self.handle_damage_event(ev)
        elif isinstance(ev, gameevent.HealEvent):
            self.handle_heal_event(ev)
        elif isinstance(ev, gameevent.FaintEvent):
            self.handle_faint_event(ev)
        elif isinstance(ev, gameevent.StatChangeEvent):
            self.handle_stat_change_event(ev)
        elif isinstance(ev, gameevent.StatusEvent):
            self.handle_status_event(ev)
        elif isinstance(ev, gameevent.StatAnimationEvent):
            self.handle_stat_animation_event(ev)
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
        if isinstance(ev.target, pokemon.EnemyPokemon):
            self.floor.active_enemies.remove(ev.target)
        else:
            self.party.standby(ev.target)
        self.floor.spawned.remove(ev.target)
        self.defender_fainted = False
        self.event_queue.popleft()

    def handle_stat_change_event(self, ev: gameevent.StatChangeEvent):
        statistic: pokemondata.Statistic = getattr(ev.target.status, ev.stat)
        statistic.increase(ev.amount)
        self.event_queue.popleft()

    def handle_status_event(self, ev: gameevent.StatusEvent):
        setattr(ev.target.status, ev.status, ev.value)
        self.event_queue.popleft()

    def handle_stat_animation_event(self, ev: gameevent.StatAnimationEvent):
        ev.anim.update()
        if ev.anim.is_restarted():
            self.event_queue.popleft()
