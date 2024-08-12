import pygame
import pygame.mixer

from app.common import constants
from app.gui import text
from app.events import story_event
from app.scenes.scene import Scene
from app.scenes.story.story_scene import StoryScene


class NewGameScene(StoryScene):
    def __init__(self):
        self.texts = [
            text.ScrollText(
                text.TextBuilder()
                .set_alignment(text.Align.CENTER)
                .set_color(text.WHITE)
                .write(msg)
                .build(),
            )
            for msg in (
                "Welcome!",
                "This is the portal that leads to the\nworld inhabited only by Pokemon.",
                "Beyond this gateway, many new\nadventures and fresh experiences\nawait your arrival!",
                "Before you depart for adventure,\nyou must answer some questions.",
                "Be truthful when you answer them!",
                "Now, are you ready?",
                "Then...[K] let the questions begin!",
            )
        ]

        super().__init__()
        self.is_textbox_mode = False

    def get_event_queue(self):
        return sum(
            [
                [story_event.MessageEvent(t), story_event.ProcessInputEvent()]
                for t in self.texts
            ],
            [],
        )

    def get_next_scene(self) -> Scene:
        from app.scenes.quiz import QuizScene

        return QuizScene()

    def render(self) -> pygame.Surface:
        if self.scroll_text is not None:
            self.text_pos = self.scroll_text.get_rect(
                centerx=constants.DISPLAY_WIDTH // 2, y=80
            ).topleft
        return super().render()
