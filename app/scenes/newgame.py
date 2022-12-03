import pygame
import pygame.mixer

from app.common import inputstream, constants, text
from app.scenes import scene, quiz


class NewGameScene(scene.Scene):
    def __init__(self):
        super().__init__(30, 30)
        self.scroll_texts = [
            "Welcome!",
            "This is the portal that leads to the\nworld inhabited only by Pokemon.",
            "Beyond this gateway, many new\nadventures and fresh experiences\nawait your arrival!",
            "Before you depart for adventure,\nyou must answer some questions.",
            "Be truthful when you answer them!",
            "Now, are you ready?",
            "Then... let the questions begin!"
        ]
        self.index = 0
        self.current_text = self.make_scroll_text(self.scroll_texts[self.index])
    
    def make_scroll_text(self, message: str) -> text.ScrollText:
        return text.ScrollText(
            text.TextBuilder()
            .set_alignment(text.Align.CENTER)
            .set_color(text.WHITE)
            .write(message)
            .build()
        )

    def process_input(self, input_stream: inputstream.InputStream):
        if self.in_transition:
            return
        if input_stream.keyboard.is_pressed(constants.SELECT_KEY) and self.current_text.is_done:
            if self.index != len(self.scroll_texts) - 1:
                self.index += 1
                self.current_text = self.make_scroll_text(self.scroll_texts[self.index])
            else:
                self.next_scene = quiz.QuizScene()

    def update(self):
        super().update()
        self.current_text.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.fill(constants.BLACK)
        rect = self.current_text.get_rect(centerx=surface.get_rect().centerx, y=80)
        surface.blit(self.current_text.render(), rect.topleft)
        return surface
