import pygame
from app.pokemon import pokemon
from app.events import event
from app.model.animation import Animation


class LogEvent(event.Event):
    def __init__(self, text_surface: pygame.Surface):
        super().__init__()
        self.text_surface = text_surface
        self.new_divider = False

    def with_divider(self):
        self.new_divider = True
        return self


class DamageEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, amount: int):
        super().__init__()
        self.target = target
        self.amount = amount


class HealEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, amount: int):
        super().__init__()
        self.target = target
        self.amount = amount


class SetAnimationEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, animation_name: str):
        super().__init__()
        self.target = target
        self.animation_name = animation_name


class FaintEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon):
        super().__init__()
        self.target = target

class StatChangeEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, stat: str, amount: int):
        super().__init__()
        self.target = target
        self.stat = stat
        self.amount = amount

class StatusEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, status: str, value):
        super().__init__()
        self.target = target
        self.status = status
        self.value = value

class StatAnimationEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, anim: Animation):
        super().__init__()
        self.target = target
        self.anim = anim
        self.anim.restart()
