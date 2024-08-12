import os
import pygame.image
import pygame.mixer

from app.common import mixer, settings
from app.common.action import Action
from app.common.constants import IMAGES_DIRECTORY
from app.common.inputstream import InputStream
from app.scenes.scene import Scene
from app.scenes.mainmenu import MainMenuScene, NewGameMainMenuScene


class IntroScene(Scene):
    def __init__(self):
        super().__init__(30, 30)
        mixer.set_bgm(-3)
        bg_path = os.path.join(IMAGES_DIRECTORY, "bg", "system", "intro.png")
        self.bg = pygame.image.load(bg_path)

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.INTERACT)):
            # TODO: Choose between new game and continue main menu scenes.
            pygame.mixer.music.fadeout(500)
            self.next_scene = NewGameMainMenuScene()

    def update(self):
        super().update()

    def render(self):
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        return surface
