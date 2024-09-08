import pygame

from app.scenes.scene import Scene
from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.gui import text
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.pokemon.animation_id import AnimationId
from app.pokemon.portrait import PortraitEmotion
import app.db.database as db


class Story4(StoryScene):
    def __init__(self):
        # Set beach waves bgm
        self.hero = user_pokemon_factory(0)
        self.sidekick = user_pokemon_factory(1)
        
        self.sidekick_msgs = iter(text.ScrollText(
            f"[C:YELLOW]{self.sidekick.base.name}[C:WHITE]: {msg}",
            with_sound=True,
            start_t=len(self.sidekick.base.name) + 2
        ) for msg in [
            "Wow! What a beautiful sight!",
            "When the weather's good, the\n"
            "[C:CYAN]Krabby[C:WHITE] come out at sundown to blow bubbles...",
            "All those bubbles, reflecting the\n"
            "setting of the sun off the waves...",
            "It's always beautiful.",
            "............",
            "This is where I always come\n"
            "when I'm feeling down on myself.",
            "But it makes me feel good to be\n"
            "here, like always.",
            "Coming here heals my spirits.",
            "Hey...[K]what's that?[K] What's going\n"
            "on over there?",
            "Waah![K] Someone has collapsed on\n"
            "the sand!",
            "What happened?![K] Are you OK?",
            
            "You're awake![K] Thank goodness!",
            "You wouldn't move at all. I was\n"
            "really scared for you!",
            "Do you have any idea how you\n"
            "ended up unconscious out here?",
            
            f"Anyway, I'm [C:YELLOW]{self.sidekick.base.name}[C:WHITE].[K]\n"
            "Happy to meet you!",
            "And who are you?",
            "I don't think I've seen you\n"
            "around before.",
            "What?[K] You say you're a human?",
            "You look like a totally normal\n"
            f"[C:LIME]{self.hero.base.name}[C:WHITE] to me!",
            
            "You're...[K]a little odd...",
            "Are you pulling some kind of\n"
            "trick on me?",
        ])
        self.hero_msgs = [text.ScrollText(msg) for msg in [
            "(..................)",
            "(...Ugh...)",
            "(Where...where am I...?)",
            
            "(I... I was unconscious?[K] What happened...?)",
            
            "(It's...it's true!)",
            f"I've turned into a [C:LIME]{self.hero.base.name}[C:WHITE]!)",
            "(...But how did this happen?[K] I don't remember\n"
            "anything...)",
        ]]
        
        
        
        self.hero = user_pokemon_factory(0)
        self.sidekick = user_pokemon_factory(1)
        
        super().__init__()

    def get_event_queue(self):
        return [
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.INSPIRED, left=False),

            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.SetTextboxVisibilityEvent(True),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),

            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.SURPRISED, left=False),

            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.SURPRISED, left=False),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.PAIN),
            
            story_event.MessageEvent(self.hero_msgs[0]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.hero_msgs[1]),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),

            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),

            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.NORMAL),
            
            story_event.MessageEvent(self.hero_msgs[2]),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),

            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),

            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.NORMAL),
            
            story_event.MessageEvent(self.hero_msgs[3]),
            story_event.ProcessInputEvent(),

            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),

            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),

            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.SURPRISED, left=False),

            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),

            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.SURPRISED),

            story_event.MessageEvent(self.hero_msgs[4]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.hero_msgs[5]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.hero_msgs[6]),
            story_event.ProcessInputEvent(),
            
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),

            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),


        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.scene import Scene
        return Scene()
