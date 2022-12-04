import cProfile
import os
import sys

import pygame
import pygame.display
import pygame.event
import pygame.image
import pygame.time

from app.common import constants

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

pygame.init()
display = pygame.display.set_mode(constants.DISPLAY_SIZE)

from app.common import inputstream, settings, text
from app.scenes import mainmenu
from app.events import event

class Game():
    def __init__(self):
        # Initialisation
        self.clock = pygame.time.Clock()
        self.input_stream = inputstream.InputStream()
        self.scene = mainmenu.MainMenuScene()
        self.init_display()

    def init_display(self):
        self.display = display
        pygame.display.set_caption(constants.CAPTION)
        ICON_PATH = os.path.join("assets", "images", "icon", "icon.png")
        pygame.display.set_icon(pygame.image.load(ICON_PATH))

    def run(self):
        self.running = True
        while self.running:
            self.input()
            self.update()
            self.render()
        settings.save()
        pygame.quit()

    def input(self):
        # Gets the keyboard state
        self.input_stream.update()
        kb = self.input_stream.keyboard

        # Post events to queue on kb input
        if kb.is_pressed(constants.QUIT_KEY):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif kb.is_pressed(constants.TOGGLE_FULLSCREEN_KEY):
            pygame.event.post(pygame.event.Event(event.TOGGLE_FULLSCREEN_EVENT))

        self.scene.process_input(self.input_stream)

    def update(self):
        if self.scene.is_end:
            self.scene = self.scene.next_scene
        self.scene.update()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == event.TOGGLE_FULLSCREEN_EVENT:
                flags = self.display.get_flags()
                if flags & pygame.FULLSCREEN:
                    flags &= ~pygame.FULLSCREEN
                else:
                    flags |= pygame.FULLSCREEN
                pygame.display.set_mode(constants.DISPLAY_SIZE, flags)

        self.clock.tick(constants.FPS)

    def render(self):
        self.display.fill(constants.BLACK)
        self.display.blit(self.scene.render(), (0, 0))
        fps_surface = (text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(str(round(self.clock.get_fps())))
            .build()
            .render()
        )
        self.display.blit(fps_surface, (240, 8))
        pygame.display.update()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    cProfile.run('main()')
