import os

import pygame

from app.common.action import Action
from app.common import constants
from app.common.inputstream import InputStream
from app.common import settings
from app.gui import text
from app.db import database
from app.events import event
from app.scenes.mainmenu import MainMenuScene, NewGameMainMenuScene


CAPTION = "Pokemon Mystery Dungeon Remake"
ICON_PATH = os.path.join(constants.IMAGES_DIRECTORY, "icon", "icon.png")
FPS = 60


class Game:
    def __init__(self):
        pygame.init()
        SCALE = 4
        self.scaled_size = (constants.DISPLAY_WIDTH * SCALE, constants.DISPLAY_HEIGHT * SCALE)
        self.display = pygame.display.set_mode(self.scaled_size)
        pygame.display.set_caption(CAPTION)
        pygame.display.set_icon(pygame.image.load(ICON_PATH))

        database.init_database()

        self.clock = pygame.time.Clock()
        self.input_stream = InputStream()
        self.scene = NewGameMainMenuScene()
        self.event_handler_dispatcher = {
            pygame.QUIT: self.handle_quit,
            event.TOGGLE_FULLSCREEN_EVENT: self.handle_toggle_fullscreen,
        }

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

        kb = self.input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.QUIT)):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif kb.is_pressed(settings.get_key(Action.FULLSCREEN)):
            pygame.event.post(pygame.event.Event(event.TOGGLE_FULLSCREEN_EVENT))

        self.scene.process_input(self.input_stream)

    def update(self):
        if self.scene.is_end:
            self.scene = self.scene.next_scene
        self.scene.update()

        for ev in pygame.event.get():
            self.event_handler_dispatcher.get(ev.type, lambda: None)()

        self.clock.tick(FPS)

    def handle_quit(self):
        self.running = False

    def handle_toggle_fullscreen(self):
        flags = self.display.get_flags()
        if flags & pygame.FULLSCREEN:
            flags &= ~pygame.FULLSCREEN
        else:
            flags |= pygame.FULLSCREEN
        pygame.display.set_mode(constants.DISPLAY_SIZE, flags)

    def render(self):
        surface = pygame.Surface(constants.DISPLAY_SIZE)
        surface.fill(constants.BLACK)
        surface.blit(self.scene.render(), (0, 0))
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
