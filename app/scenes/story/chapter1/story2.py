import pygame

from app.scenes.scene import Scene
from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.gui import text
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.pokemon.animation_id import AnimationId
from app.pokemon.portrait import PortraitEmotion
import app.db.map_background as map_background_db
import app.db.sfx as sfx_db


class Story2(StoryScene):
    def __init__(self):
        self.texts = [text.ScrollText(msg) for msg in [
            "......",
            "............",
            "..................",
            "Urrgh...",
            "Where...",
            "...Where am I?",
            "...[K]I can't...[K] Drifting off..."
        ]]
        
        self.hero = user_pokemon_factory(0)
        
        super().__init__()

    def get_event_queue(self):
        return [
            story_event.SfxEvent(sfx_db.load("BG", "beach"), -1),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[0]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.texts[1]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.texts[2]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.texts[3]),
            story_event.ProcessInputEvent(),
            
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(120),
            
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[4]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.texts[5]),
            story_event.ProcessInputEvent(),

            story_event.SetTextboxVisibilityEvent(False),
            story_event.FadeOutEvent(0),
            story_event.SetBackgroundEvent(map_background_db.load("D01P11A"), alpha=0),
            story_event.SpawnSprite(self.hero, (288, 168)),
            story_event.SetSpriteAnimation(self.hero, AnimationId.ID_27),  # Laying
            story_event.SetCameraPositionEvent(pygame.Vector2(172, 68)),
            story_event.FadeInEvent(60),
            
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.PAIN),
            story_event.MessageEvent(self.texts[6]),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.FadeOutEvent(20),
            story_event.FadeInEvent(20),
            story_event.FadeOutEvent(20),
            story_event.FadeInEvent(20),
            event.SleepEvent(60),
        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.story.chapter1.story3 import Story3
        return Story3()
