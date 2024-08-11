import os

import pygame

from app.common.action import Action
from app.common import constants
from app.common.inputstream import InputStream
from app.common import settings
from app.gui import text
from app.db import database


CAPTION = "Pokemon Mystery Dungeon Remake"
ICON_PATH = os.path.join(constants.IMAGES_DIRECTORY, "icon", "icon.png")
FPS = 60


class Game:
    def __init__(self):
        pygame.init()
        SCALE = 4
        self.scaled_size = (
            constants.DISPLAY_WIDTH * SCALE,
            constants.DISPLAY_HEIGHT * SCALE,
        )
        self.display = pygame.display.set_mode(self.scaled_size)
        pygame.display.set_caption(CAPTION)
        pygame.display.set_icon(pygame.image.load(ICON_PATH))

        database.init_database()

        self.clock = pygame.time.Clock()
        self.input_stream = InputStream()
        
        #from app.scenes.intro_scene import IntroScene
        #self.scene = IntroScene()
        #from app.scenes.mainmenu import MainMenuScene
        #self.scene = MainMenuScene()
        from app.scenes.story.chapter1 import chapter1_intro_scene
        self.scene = chapter1_intro_scene.Chapter1IntroScene()

    def run(self):
        self.running = True
        while self.running:
            self.input()
            self.update()
            self.render()
        settings.save()
        pygame.quit()

    def input(self):
        self.input_stream.update()

        for ev in pygame.event.get():
            if (
                ev.type == pygame.QUIT
                or ev.type == pygame.KEYDOWN
                and ev.key == settings.get_key(Action.QUIT)
            ):
                self.handle_quit()

        self.scene.process_input(self.input_stream)

    def update(self):
        if self.scene.is_end:
            self.scene = self.scene.next_scene
        self.scene.update()

        self.clock.tick(FPS)

    def handle_quit(self):
        self.running = False

    def render(self):
        surface = pygame.Surface(constants.DISPLAY_SIZE)
        surface.fill(constants.BLACK)
        scene_surf = self.scene.render()
        scene_surf.set_alpha(self.scene.alpha)
        surface.blit(scene_surf, (0, 0))
        surface.blit(self.render_fps(), (240, 8))
        self.display.blit(pygame.transform.scale(surface, self.scaled_size), (0, 0))
        pygame.display.update()

    def render_fps(self) -> pygame.Surface:
        return text.TextBuilder.build_white(str(round(self.clock.get_fps())))


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
