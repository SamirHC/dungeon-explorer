import pygame

from app.scenes.scene import Scene
from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.gui import text
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.pokemon.animation_id import AnimationId
from app.pokemon.portrait import PortraitEmotion
import app.db.database as db


class Story2(StoryScene):
    def __init__(self):
        # Set beach waves bgm
        self.sidekick_msgs = [
            "Wow! What a beautiful sight!",
            "When the weather's good, the\n"
            "[C:CYAN]Krabby[C:WHITE] come out at sundown to blow bubbles...",
            "All those bubbles, reflecting the\n"
            " setting of the sun off the waves...",
            "It's always beautiful.",
            "............",
            "This is where I always come\n"
            "when I'm feeling down on myself.",
            "But it makes me feel good to be\n",
            "here, like always.",
            "Coming here heals my spirits.",
            "Hey...[K]what's that?[K] What's going\n"
            "on over there?",
            "Waah![K] Someone has collapsed on\n"
            "the sand!",
            "What happened?![K] Are you OK?",
            
            "(..................)"
            "(...Ugh...)"
            "(Where...where am I...?)"
            
            "You're awake![K] Thank goodness!",
            "You wouldn't move at all. I was really scared for you!",
            "Do you have any idea how you\n"
            "ended up unconscious out here?",
            
            "(I... I was unconscious?[K] What happened...?)",
            
            "Anyway, I'm [C:YELLOW]{sidekick.name}[C:WHITE].[K]\n"
            "Happy to meet you!",
            "And who are you?",
            "I don't think I've seen you\n"
            "around before.",
            "What?[K] You say you're a human?",
            "You look like a totally normal\n"
            "[C:LIME]{hero.name}[C:WHITE] to me!",
            
            "(It's...it's true!)",
            "I've turned into a [C:LIME]{hero.name}!)",
            "(...But how did this happen?[K] I don't remember\n)"
            "anything...)",
            
        ]
        
        
        
        self.hero = user_pokemon_factory(0)
        self.sidekick = user_pokemon_factory(1)
        
        super().__init__()

    def get_event_queue(self):
        return [
            story_event.SfxEvent(db.sfx_db["BG", "beach"], -1),
            story_event.SetBackgroundEvent(db.map_background_db["D01P11A"], alpha=0),
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
        from app.scenes.scene import Scene
        return Scene()
