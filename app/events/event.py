import pygame

from app.common.action import Action

TOGGLE_FULLSCREEN_EVENT = pygame.USEREVENT + 1


class Event:
    pass


class SleepEvent(Event):
    def __init__(self, time: int):
        super().__init__()
        self.time = time


class ActionEvent(Event):
    def __init__(self, action: Action):
        self.action = action
