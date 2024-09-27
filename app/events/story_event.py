import pygame

from app.events.event import Event
from app.gui.text import ScrollText
from app.pokemon.pokemon import Pokemon
from app.pokemon.animation_id import AnimationId
from app.pokemon.portrait import PortraitEmotion


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
    def __init__(self, bg, alpha=255):
        self.bg = bg
        self.alpha = alpha


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
    def __init__(self, sfx: pygame.mixer.Sound, loops: int = 0):
        self.sfx = sfx
        self.loops = loops


class SpawnSprite(StoryEvent):
    def __init__(self, sprite: Pokemon, pos: tuple[int, int]):
        self.sprite = sprite
        self.pos = pos


class SetSpriteAnimation(StoryEvent):
    def __init__(self, sprite: Pokemon, anim_id: AnimationId):
        self.sprite = sprite
        self.anim_id = anim_id


class SetPortrait(StoryEvent):
    def __init__(self, sprite: Pokemon, emotion: PortraitEmotion, left=True):
        self.sprite = sprite
        self.emotion = emotion
        self.left = left
