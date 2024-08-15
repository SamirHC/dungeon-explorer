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
            text.TextBuilder()
                .set_color(text.YELLOW)
                .write(self.sidekick.data.name)
                .set_color(text.WHITE).write(": ")
                .write(msg)
                .build(),
            with_sound=True
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
        self.speech_mark_msgs = [text.ScrollText(msg.build()) for msg in [
            text.TextBuilder()
                .set_font(db.font_db.graphic_font)
                .write([61])
                .set_font(db.font_db.normal_font)
                .write(": ")
                .write("Pokemon detected! Pokemon detected!"),
            text.TextBuilder()
                .set_font(db.font_db.graphic_font)
                .write([61])
                .set_font(db.font_db.normal_font)
                .write(": ")
                .write("Whose footprint? Whose footprint?"),
            text.TextBuilder()
                .set_font(db.font_db.graphic_font)
                .write([61])
                .set_font(db.font_db.normal_font)
                .write(": ")
                .write("The footprint is ")
                .set_color(text.LIME)
                .write(self.sidekick.data.name)
                .set_color(text.WHITE)
                .write("'s![K]\n")
                .write("The footprint is ")
                .set_color(text.LIME)
                .write(self.sidekick.data.name)
                .set_color(text.WHITE)
                .write("'s!"),
            text.TextBuilder()
                .set_font(db.font_db.graphic_font)
                .write([61])
                .set_font(db.font_db.normal_font)
                .write(": ")
                .write("Hey, ")
                .set_color(text.CYAN)
                .write("Zubat")
                .set_color(text.WHITE)
                .write(".[K] Did you get a load of that?!"),
        ]]
        
        self.zubat_msgs = [text.ScrollText(
            f(text.TextBuilder()
                .set_color(text.CYAN)
                .write("Zubat")
                .set_color(text.WHITE).write(": ")
            ).build(),
            with_sound=True
        ) for f in (
            lambda x: x
                .write("You bet I did, ")
                .set_color(text.CYAN)
                .write("Koffing")
                .set_color(text.WHITE)
                .write("."),
            lambda x: x
                .write(
                    "That wimp had something, that's\n"
                    "for sure.[K] It looked like some kind of treasure."
                ),
            lambda x: x
                .write(
                    "We do."
                )
                ,
        )
        ]
        
        self.koffing_msgs = [text.ScrollText(
            f(text.TextBuilder()
                .set_color(text.CYAN)
                .write("Koffing")
                .set_color(text.WHITE).write(": ")
            ).build(),
            with_sound=True
        ) for f in (
            lambda x: x
                .write(
                    "That little wimp that was pacing\n"
                    "around...[K]had something good, right?"
                )
                ,
            lambda x: x
                .write(
                    "Do we go after it?"
                )
                ,
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
        return Scene()
