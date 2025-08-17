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
from app.gui.textbox import DungeonTextBox, DungeonMessageLog
from app.dungeon.battle_system import BattleSystem
from app.events import dungeon_battle_event
import app.db.stat_animation as statanimation_db
from app.db.stat_animation import StatAnimationType
from app.db import dungeon_log_text


class DungeonEventHandler:
    def __init__(
        self,
        dungeon: Dungeon,
        dungeon_log: DungeonTextBox,
        message_log: DungeonMessageLog,
        event_queue: deque[event.Event],
        battlesystem: BattleSystem,
    ):
        self.dungeon = dungeon
        self.log = dungeon_log
        self.message_log = message_log
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
            game_event.GetXpEvent: self.handle_get_xp_event,
            game_event.LevelUpEvent: self.handle_level_up_event,
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
            self.log.write(ev.text.render())
            self.message_log.message_list.write_bar_line(ev.text)
        else:
            self.log.write(ev.text.render())
            self.message_log.message_list.write_line(ev.text)
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
            .write(target.base.name)
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
        events.append(game_event.LogEvent(tb.build()))
        events.append(event.SleepEvent(20))
        self.event_queue.extendleft(reversed(events))

    def handle_faint_event(self, ev: game_event.FaintEvent):
        self.pop_event()
        defender = ev.target

        events = []
        if defender is self.dungeon.floor.party.leader:
            # Replace with more verbose defeat message
            events.append(game_event.LogEvent(dungeon_log_text.defeated(defender)))
            events.append(event.SleepEvent(100))
        else:
            events.append(game_event.LogEvent(dungeon_log_text.defeated(defender)))
            events.append(event.SleepEvent(20))

        self.dungeon.floor[ev.target.position].pokemon_ptr = None
        if ev.target.is_enemy:
            self.dungeon.floor.active_enemies.remove(ev.target)
            events.extend(
                game_event.GetXpEvent(p, ev.target) for p in self.dungeon.party
            )
        else:
            self.dungeon.party.standby(ev.target)
        self.dungeon.floor.spawned.remove(ev.target)

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

        description = f"'s {stat.get_log_string()} "
        if amount < 0:
            anim_type = StatAnimationType.FALL
        elif amount > 0:
            anim_type = StatAnimationType.RISE

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
                    .write(defender.base.name)
                    .set_color(text.WHITE)
                    .write(description)
                    .build()
                )
            ),
            game_event.StatAnimationEvent(
                defender, statanimation_db.load(stat, anim_type)
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

        description = f"'s {stat.get_log_string()} "

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
                    .write(defender.base.name)
                    .set_color(text.WHITE)
                    .write(description)
                    .build()
                )
            ),
            game_event.StatAnimationEvent(
                defender, statanimation_db.load(stat, StatAnimationType.FALL)
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
        floor = self.dungeon.floor

        events = []

        if ev.destination is None:
            # Display message
            events.append(
                game_event.SetAnimationEvent(ev.pokemon, AnimationId.HURT, True)
            )
            events.append(game_event.LogEvent(dungeon_log_text.sent_flying(ev.pokemon)))
            events.append(ev)
            # Get location thrown to
            start = x0, y0 = ev.pokemon.position
            possible_destinations = [
                pos
                for pos in floor.get_local_pokemon_positions(start)
                if floor[pos].pokemon_ptr not in floor.party
                and pos != ev.pokemon.position
            ]
            if not possible_destinations:
                possible_destinations = [
                    pos
                    for pos in floor.get_local_ground_tiles_positions(start)
                    if floor[pos].pokemon_ptr not in floor.party
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
        elif floor.is_occupied(ev.destination):
            directions = list(Direction)
            random.shuffle(directions)
            for d in directions:
                x0, y0 = ev.pokemon.position
                x1, y1 = ev.destination
                pos = x2, y2 = x1 + d.x, y1 + d.y
                if not floor.is_occupied(pos) and floor.is_ground(pos):
                    break
            delta_x = (x2 - x1) * TILESIZE
            delta_y = (y2 - y1) * TILESIZE
            t = 12 + max(abs(delta_x), abs(delta_y))
            for i in range(t):
                ev.x.append(ev.pokemon.moving_entity.x + round(i * delta_x / t))
                ev.y.append(ev.pokemon.moving_entity.y + round(i * delta_y / t))

            # Collided pokemon
            other: Pokemon = floor[ev.destination].pokemon_ptr

            events.append(ev)
            events.append(game_event.SetAnimationEvent(other, AnimationId.HURT))
            events.append(game_event.LogEvent(dungeon_log_text.damage(other, DAMAGE)))
            events.append(game_event.DamageEvent(other, DAMAGE))
            events.append(
                game_event.LogEvent(dungeon_log_text.damage(ev.pokemon, DAMAGE))
            )
            # Flung pokemon
            events.append(game_event.DamageEvent(ev.pokemon, DAMAGE))
            ev.destination = pos

        else:
            floor[ev.pokemon.position].pokemon_ptr = None
            ev.pokemon.position = ev.destination
            floor[ev.pokemon.position].pokemon_ptr = ev.pokemon
            events.append(
                game_event.SetAnimationEvent(ev.pokemon, AnimationId.IDLE, True)
            )

        self.event_queue += events

    def handle_battle_system_event(self, ev: game_event.BattleSystemEvent):
        self.pop_event()
        self.event_queue.extend(dungeon_battle_event.get_events(ev))

    def handle_move_miss_event(self, ev: game_event.MoveMissEvent):
        self.pop_event()
        self.event_queue.extendleft(
            reversed(
                [
                    game_event.LogEvent(dungeon_log_text.move_miss(ev.defender)),
                    event.SleepEvent(20),
                ]
            )
        )

    def handle_set_weather_event(self, ev: game_event.SetWeatherEvent):
        self.pop_event()
        self.dungeon.set_weather(ev.weather)
        events = []
        events.append(game_event.LogEvent(dungeon_log_text.weather(ev.weather)))
        events.append(event.SleepEvent(20))
        self.event_queue.extendleft(reversed(events))

    def handle_get_xp_event(self, ev: game_event.GetXpEvent):
        self.pop_event()
        events = []
        # TODO: Find xp formula based on pokemon's exp_yield value, hold items etc.
        xp_earned = ev.killed.stats.level.value * 10

        ev.target.stats.xp.add(xp_earned)
        total_xp = ev.target.stats.xp.value

        events.append(
            game_event.LogEvent(dungeon_log_text.gain_xp(ev.target, xp_earned))
        )

        MAX_LEVEL = ev.target.stats.level.max_value
        level = ev.target.stats.level.value

        if level < MAX_LEVEL and ev.target.base.get_required_xp(level + 1) <= total_xp:
            events.append(game_event.LevelUpEvent(ev.target))

        self.event_queue.extendleft(reversed(events))

    def handle_level_up_event(self, ev: game_event.LevelUpEvent):
        self.pop_event()
        events = []

        total_hp_growth = 0
        total_atk_growth = 0
        total_def_growth = 0
        total_sp_atk_growth = 0
        total_sp_def_growth = 0

        level = ev.target.stats.level.value
        while (
            level < 100
            and ev.target.base.get_required_xp(level + 1) <= ev.target.stats.xp.value
        ):
            ev.target.stats.level.add(1)
            level = ev.target.stats.level.value

            hp_growth = ev.target.base.stats_growth.hp[level]
            atk_growth = ev.target.base.stats_growth.attack[level]
            def_growth = ev.target.base.stats_growth.defense[level]
            sp_atk_growth = ev.target.base.stats_growth.sp_attack[level]
            sp_def_growth = ev.target.base.stats_growth.sp_defense[level]

            total_hp_growth += hp_growth
            total_atk_growth += atk_growth
            total_def_growth += def_growth
            total_sp_atk_growth += sp_atk_growth
            total_sp_def_growth += sp_def_growth

            ev.target.status.hp.max_value += hp_growth
            ev.target.stats.hp.add(hp_growth)
            ev.target.status.hp.add(hp_growth)

            ev.target.stats.attack.add(atk_growth)
            ev.target.stats.defense.add(def_growth)
            ev.target.stats.sp_attack.add(sp_atk_growth)
            ev.target.stats.sp_defense.add(sp_def_growth)

            events.append(event.SleepEvent(20))
            events.append(
                game_event.LogEvent(dungeon_log_text.level_up(ev.target, level))
            )
            events.append(event.SleepEvent(20))

        if total_hp_growth > 0:
            events.append(
                game_event.LogEvent(dungeon_log_text.hp_up(ev.target, total_hp_growth))
            )
        if total_atk_growth > 0:
            events.append(
                game_event.LogEvent(
                    dungeon_log_text.stat_up(ev.target, Stat.ATTACK, total_atk_growth)
                )
            )
        if total_def_growth > 0:
            events.append(
                game_event.LogEvent(
                    dungeon_log_text.stat_up(ev.target, Stat.DEFENSE, total_def_growth)
                )
            )
        if total_sp_atk_growth > 0:
            events.append(
                game_event.LogEvent(
                    dungeon_log_text.stat_up(
                        ev.target, Stat.SP_ATTACK, total_sp_atk_growth
                    )
                )
            )
        if total_sp_def_growth > 0:
            events.append(
                game_event.LogEvent(
                    dungeon_log_text.stat_up(
                        ev.target, Stat.SP_DEFENSE, total_sp_def_growth
                    )
                )
            )
        events.append(event.SleepEvent(20))

        self.event_queue.extendleft(reversed(events))
