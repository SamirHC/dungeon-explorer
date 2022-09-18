import cProfile
import os
import sys

import pygame
import pygame.display
import pygame.event
import pygame.image
import pygame.time

from dungeon_explorer.common import constants, inputstream, settings, text
from dungeon_explorer.scenes import mainmenu


class Game():
    def __init__(self):
        # Initialisation
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)

        pygame.init()
        self.display = pygame.display.set_mode(constants.DISPLAY_SIZE)
        pygame.display.set_caption(constants.CAPTION)
        pygame.display.set_icon(pygame.image.load(os.path.join("assets", "images", "icon", "icon.png")))

        text.init_fonts()
        self.clock = pygame.time.Clock()
        self.input_stream = inputstream.InputStream()
        self.scene = mainmenu.MainMenuScene()

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

        # Checks if user quits
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

        # Toggle Fullscreen
        if self.input_stream.keyboard.is_pressed(pygame.K_F11):
            if self.display.get_flags() & pygame.FULLSCREEN:
                pygame.display.set_mode(constants.DISPLAY_SIZE)
            else:
                pygame.display.set_mode(constants.DISPLAY_SIZE, pygame.FULLSCREEN)

        self.scene.process_input(self.input_stream)

    def update(self):
        if self.scene.is_end:
            self.scene = self.scene.next_scene
        self.scene.update()

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
