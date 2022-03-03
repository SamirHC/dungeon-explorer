import os
import sys

import pygame
import pygame.display
import pygame.event
import pygame.image
import pygame.mixer
import pygame.time

from dungeon_explorer.common import constants, inputstream, settings
from dungeon_explorer.scenes import scenemanager


def main():
    # Initialisation
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    pygame.init()
    display = pygame.display.set_mode(constants.DISPLAY_SIZE)
    pygame.display.set_caption(constants.CAPTION)
    pygame.display.set_icon(pygame.image.load(os.path.join("assets", "images", "icon", "icon.png")))
    pygame.mixer.music.set_volume(settings.get_bgm())

    clock = pygame.time.Clock()
    input_stream = inputstream.InputStream()
    scene_manager = scenemanager.SceneManager()

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

        scene_manager.process_input(input_stream)
        scene_manager.update()
        scene_manager.render(display)

        clock.tick(constants.FPS)

    settings.save()
    pygame.quit()


if __name__ == "__main__":
    main()
