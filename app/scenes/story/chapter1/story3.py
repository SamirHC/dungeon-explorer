import pygame

from app.scenes.scene import Scene
from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.gui import text
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.pokemon.animation_id import AnimationId
from app.pokemon.portrait import PortraitEmotion
import app.db.database as db


class Story3(StoryScene):
    def __init__(self):
        # Play fire bgm
        self.sidekick = user_pokemon_factory(1)
        self.sidekick_msgs = [text.ScrollText(
            f"[C:YELLOW]{self.sidekick.base.name}[C:WHITE]: {msg}",
            with_sound=True,
            start_t=len(self.sidekick.base.name) + 2
        ) for msg in (
            "Hmm...",
            # Paces right to left to right to middle
            # Faces forward
            # Angry portrait
            "No.[K] I refuse to be paralyzed\n"
            "by this any longer!",
            "This is it. Today I'm going to\n"
            "be brave.",
            # Steps onto grate
            # Shocked
            "Waah!",
            "That shocked me!",
            "Whew...",
            "...[K]I can't...[K] I can't bring myself\n"
            "to go in.",
            "I vowed that I would do it\n"
            "today, but...",
            "I thought that holding on to my\n"
            "personal treasure would inspire me...",
            "Sigh...I just can't do it.",
            "I'm such a coward...",
            "This is so discouraging...",
        )
        ]

        self.speech_mark_msgs = [
            text.ScrollText(f"[G:61]: {msg}")
            for msg in [
                "Pokemon detected! Pokemon detected!",
                "Whose footprint? Whose footprint?",
                f"The footprint is [C:LIME]{self.sidekick.base.name}[C:WHITE]'s![K]\n"
                f"The footprint is [C:LIME]{self.sidekick.base.name}[C:WHITE]'s!",
                "Hey, [C:CYAN]Zubat[C:WHITE].[K] Did you get a load of that?!",
        ]]
        
        self.zubat_msgs = [text.ScrollText(
            f"[C:CYAN]Zubat[C:WHITE]: {msg}",
            with_sound=True
        ) for msg in (
            "You bet I did, [C:CYAN]Koffing[C:WHITE].",
            "That wimp had something, that's\n"
            "for sure.[K] It looked like some kind of treasure.",
            "We do."
        )
        ]
        
        self.koffing_msgs = [text.ScrollText(
            f"[C:CYAN]Koffing[C:WHITE]: {msg}",
            with_sound=True
        ) for msg in (
            "That little wimp that was pacing\n"
            "around...[K]had something good, right?",
            "Do we go after it?"
        )
        ]
        
        super().__init__()
        
    def get_event_queue(self):
        return [
            story_event.SetBackgroundEvent(db.map_background_db["G01P01B"]),
            story_event.SetCameraPositionEvent(pygame.Vector2(115, 81)),
            story_event.SpawnSprite(self.sidekick, (240, 200)),
            
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.WORRIED),
            
            story_event.MessageEvent(self.sidekick_msgs[0]),
            story_event.ProcessInputEvent(),
            
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SetPortrait(None, None),
            
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.WORRIED),
            
            story_event.MessageEvent(self.sidekick_msgs[1]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.sidekick_msgs[2]),
            story_event.ProcessInputEvent(),
            
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SetPortrait(None, None),
            
            story_event.SetTextboxVisibilityEvent(True),
            
            story_event.MessageEvent(self.speech_mark_msgs[0]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.speech_mark_msgs[1]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.speech_mark_msgs[2]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.sidekick_msgs[3]),
            story_event.ProcessInputEvent(),
            
            story_event.MessageEvent(self.sidekick_msgs[4]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[5]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[6]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[7]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[8]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[9]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[10]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.sidekick_msgs[11]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.speech_mark_msgs[3]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.zubat_msgs[0]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.koffing_msgs[0]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.zubat_msgs[1]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.koffing_msgs[1]),
            story_event.ProcessInputEvent(),

            story_event.MessageEvent(self.zubat_msgs[2]),
            story_event.ProcessInputEvent(),

        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.story.chapter1.story4 import Story4
        return Story4()
