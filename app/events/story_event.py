import pygame

from app.events.event import Event
from app.gui.text import ScrollText


class StoryEvent(Event):
    pass

class MessageEvent(StoryEvent):
    def __init__(self, scroll_text: ScrollText):
        self.scroll_text = scroll_text

class ScreenFlashEvent(StoryEvent):
    def __init__(self, duration: int, restore=True):
        self.duration = duration
        self.restore = restore
        self.t = 0
        
    @property
    def alpha(self):
        return int((self.t / self.duration) * 255)

    @property
    def is_done(self):
        return self.t >= self.duration
        

class SetTextboxVisibilityEvent(StoryEvent):
    def __init__(self, is_visible: bool):
        self.is_visible = is_visible

class ProcessInputEvent(StoryEvent):
    def __init__(self):
        self.handled = False

class SetBackgroundEvent(StoryEvent):
    def __init__(self, bg):
        self.bg = bg

class PanCameraEvent(StoryEvent):
    def __init__(self, start: pygame.Vector2, dest: pygame.Vector2, duration: int):
        self.start = start
        self.dest = dest
        self.duration = duration
        self.t = 0
        
    @property
    def is_done(self):
        return self.t >= self.duration

class FadeOutEvent(StoryEvent):
    def __init__(self, duration: int):
        self.duration = duration
        self.t = 0
        
    @property
    def alpha(self):
        return 255 - int((self.t / self.duration) * 255)

    @property
    def is_done(self):
        return self.t >= self.duration

class FadeInEvent(StoryEvent):
    def __init__(self, duration: int):
        self.duration = duration
        self.t = 0
        
    @property
    def alpha(self):
        return int((self.t / self.duration) * 255)

    @property
    def is_done(self):
        return self.t >= self.duration
    
class SetCameraPositionEvent(StoryEvent):
    def __init__(self, position: pygame.Vector2):
        self.position = position

class SfxEvent(StoryEvent):
    def __init__(self, sfx: pygame.mixer.Sound, loops: int=0):
        self.sfx = sfx
        self.loops = loops
