import pygame

from app.scenes.scene import Scene
from app.scenes.story.story_scene import StoryScene
from app.events import story_event, event
import app.db.map_background as map_background_db
import app.db.sfx as sfx_db


class Story1(StoryScene):
    def __init__(self):
        self.map_bg_1 = map_background_db.load("V00P01")
        self.map_bg_2 = map_background_db.load("V00P02")
        super().__init__()

    def get_event_queue(self):
        return [
            story_event.SetBackgroundEvent(self.map_bg_1),
            story_event.PanCameraEvent(
                pygame.Vector2(368, 48), pygame.Vector2(268, 48), 240
            ),
            story_event.FadeOutEvent(30),
            story_event.SetCameraPositionEvent(pygame.Vector2(0, 0)),
            story_event.SetBackgroundEvent(self.map_bg_2),
            story_event.FadeInEvent(30),
            event.SleepEvent(120),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 1)),
            event.SleepEvent(60),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 1)),
            event.SleepEvent(60),
        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.story.chapter1.story2 import Story2

        return Story2()
