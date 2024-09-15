from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.scenes.scene import Scene
from app.gui import text
import app.db.sfx as sfx_db


class Story0(StoryScene):
    def __init__(self):
        self.texts = [
            text.ScrollText(
                f"[G:61]: {msg}",
                with_sound=True,
            )
            for msg in (
                "Whoa! Wh-wh-whoa...!",
                "Are...[K] Are you OK?!",
                "No![K] Don't let go!",
                "Just a little longer...[K] Come on! Hang on!",
                "N-n-no![K] I can't...[K]hold on...!",
                "Waaaaaah!",
            )
        ]

        super().__init__()

    def get_event_queue(self):
        return [
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 1)),
            story_event.ScreenFlashEvent(20),
            story_event.ScreenFlashEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[0]),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(self.texts[1]),
            story_event.ProcessInputEvent(),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 1)),
            story_event.ScreenFlashEvent(8),
            event.SleepEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[2]),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(self.texts[3]),
            story_event.ProcessInputEvent(),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 1)),
            story_event.ScreenFlashEvent(8),
            event.SleepEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[4]),
            story_event.ProcessInputEvent(),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 2)),
            story_event.ScreenFlashEvent(8),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 2)),
            story_event.ScreenFlashEvent(8),
            event.SleepEvent(20),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 1)),
            story_event.ScreenFlashEvent(8),
            story_event.ScreenFlashEvent(8),
            story_event.SfxEvent(sfx_db.load("Event Main01 SE", 3)),
            event.SleepEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[5]),
            story_event.ScreenFlashEvent(100, restore=False),
        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.story.chapter1.story1 import Story1

        return Story1()
