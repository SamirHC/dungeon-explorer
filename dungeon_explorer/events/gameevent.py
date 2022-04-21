import pygame
from dungeon_explorer.pokemon import pokemon
from dungeon_explorer.events import event


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


class SetAnimationEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon, animation_name: str):
        super().__init__()
        self.target = target
        self.animation_name = animation_name


class FaintEvent(event.Event):
    def __init__(self, target: pokemon.Pokemon):
        super().__init__()
        self.target = target