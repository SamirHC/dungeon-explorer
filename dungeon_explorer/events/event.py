import pygame

TOGGLE_FULLSCREEN_EVENT = pygame.USEREVENT + 1


class Event:
    def __init__(self):
        self.handled = False


class SleepEvent(Event):
    def __init__(self, time: int):
        super().__init__()
        self.time = time
