import pygame
from app.common.direction import Direction
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon
from app.events.event import Event
from app.model.animation import Animation
from app.dungeon.dungeon import Dungeon
from app.move.move import Move


class LogEvent(Event):
    def __init__(self, text_surface: pygame.Surface):
        super().__init__()
        self.text_surface = text_surface
        self.new_divider = False

    def with_divider(self):
        self.new_divider = True
        return self


class DamageEvent(Event):
    def __init__(self, target: Pokemon, amount: int):
        super().__init__()
        self.target = target
        self.amount = amount


class HealEvent(Event):
    def __init__(self, target: Pokemon, amount: int):
        super().__init__()
        self.target = target
        self.amount = amount


class SetAnimationEvent(Event):
    def __init__(self, target: Pokemon, animation_id: AnimationId, reset_to=False):
        super().__init__()
        self.target = target
        self.animation_id = animation_id
        self.reset_to = reset_to


class FaintEvent(Event):
    def __init__(self, target: Pokemon):
        super().__init__()
        self.target = target


class StatChangeEvent(Event):
    def __init__(self, target: Pokemon, stat: str, amount: int):
        super().__init__()
        self.target = target
        self.stat = stat
        self.amount = amount


class StatusEvent(Event):
    def __init__(self, target: Pokemon, status: str, value):
        super().__init__()
        self.target = target
        self.status = status
        self.value = value


class StatAnimationEvent(Event):
    def __init__(self, target: Pokemon, anim: Animation):
        super().__init__()
        self.target = target
        self.anim = anim
        self.anim.restart()


class FlingEvent(Event):
    def __init__(self, target: Pokemon):
        self.target = target
        self.destination = None
        self.dx = []
        self.dy = []
        self.dh = []
        self.t = 0


class DirectionEvent(Event):
    def __init__(self, target: Pokemon, direction: Direction):
        self.target = target
        self.direction = direction


class BattleSystemEvent(Event):
    def __init__(self, dungeon: Dungeon, attacker: Pokemon, move: Move):
        self.dungeon = dungeon
        self.attacker = attacker
        self.move = move
