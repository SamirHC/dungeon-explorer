from pygame.surface import Surface as Surface
import app.db.database as db
from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.scenes.scene import Scene
from app.gui import text


class Story0(StoryScene):
    def __init__(self):
        self.texts = [
            text.ScrollText(
                text.TextBuilder()
                .set_font(db.font_db.graphic_font)
                .write([61])  # Speech Bubble
                .set_font(db.font_db.normal_font)
                .set_shadow(True)
                .write(f": {msg}")
                .build(),
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
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 1]),
            story_event.ScreenFlashEvent(20),
            story_event.ScreenFlashEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[0]),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(self.texts[1]),
            story_event.ProcessInputEvent(),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 1]),
            story_event.ScreenFlashEvent(8),
            event.SleepEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[2]),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(self.texts[3]),
            story_event.ProcessInputEvent(),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 1]),
            story_event.ScreenFlashEvent(8),
            event.SleepEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[4]),
            story_event.ProcessInputEvent(),
            story_event.SetTextboxVisibilityEvent(False),
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 2]),
            story_event.ScreenFlashEvent(8),
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 2]),
            story_event.ScreenFlashEvent(8),
            event.SleepEvent(20),
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 1]),
            story_event.ScreenFlashEvent(8),
            story_event.ScreenFlashEvent(8),
            story_event.SfxEvent(db.sfx_db["Event Main01 SE", 3]),
            event.SleepEvent(20),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(self.texts[5]),
            story_event.ScreenFlashEvent(100, restore=False),
        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.story.chapter1.story1 import Story1

        return Story1()
