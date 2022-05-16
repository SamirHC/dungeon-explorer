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


def main():
    # Initialisation
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    pygame.init()
    display = pygame.display.set_mode(constants.DISPLAY_SIZE)
    pygame.display.set_caption(constants.CAPTION)
    pygame.display.set_icon(pygame.image.load(os.path.join("assets", "images", "icon", "icon.png")))

    text.init_fonts()
    clock = pygame.time.Clock()
    input_stream = inputstream.InputStream()
    scene = mainmenu.MainMenuScene()

    # Game loop
    running = True
    while running:
        # Gets the keyboard state
        input_stream.update()

        # Checks if user quits
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Toggle Fullscreen
        if input_stream.keyboard.is_pressed(pygame.K_F11):
            if display.get_flags() & pygame.FULLSCREEN:
                pygame.display.set_mode(constants.DISPLAY_SIZE)
            else:
                pygame.display.set_mode(constants.DISPLAY_SIZE, pygame.FULLSCREEN)

        scene.process_input(input_stream)
        if scene.next_scene:
            scene = scene.next_scene
        scene.update()
        display.blit(scene.render(), (0, 0))
        fps_surface = (text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(str(round(clock.get_fps())))
            .build()
            .render()
        )
        display.blit(fps_surface, (240, 8))

        pygame.display.update()
        clock.tick(constants.FPS)

    settings.save()
    pygame.quit()


if __name__ == "__main__":
    cProfile.run('main()')
