import os
import random

import pygame
import pygame.display
import pygame.image
import pygame.mixer
from dungeon_explorer.common import inputstream, menu, textbox
from dungeon_explorer.scenes import scene, newgame


class MainMenuScene(scene.Scene):
    BG_DIRECTORY = os.path.join("assets", "images", "bg", "main")
    def __init__(self):
        super().__init__()
        self.bg = self.load_random_bg_image()
        self.option_description = textbox.TextBox((30, 6), 2)

        self.new_game_menu = menu.Menu((10, 6), ["New Game", "Options"])
        self.continue_game_menu = menu.Menu((13, 16), ["Continue", "Go Rescue", "Friend Rescue", "Wonder Mail", "Trade Items", "Trade Team", "Other", "Episode List"])
        self.current_menu = self.continue_game_menu if self.load_save_data() else self.new_game_menu

        pygame.mixer.music.load(os.path.join("assets", "sound", "music", "Top Menu Theme.mp3"))
        pygame.mixer.music.play(-1)

    def process_input(self, input_stream: inputstream.InputStream):
        if self.current_menu is self.new_game_menu:
            self.process_input_new_game(input_stream)
        elif self.current_menu is self.continue_game_menu:
            self.process_input_continue_game(input_stream)

    def process_input_new_game(self, input_stream: inputstream.InputStream):
        self.new_game_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.new_game_menu.current_option == "New Game":
                pygame.mixer.music.fadeout(500)
                self.next_scene = newgame.NewGameScene()
            elif self.new_game_menu.current_option == "Options":
                print("Options")

    def process_input_continue_game(self, input_stream: inputstream.InputStream):
        self.continue_game_menu.process_input(input_stream)

    def update(self):
        self.current_menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.current_menu.render(), (8, 8))
        surface.blit(self.option_description.surface, (8, 17*8))
        return surface

    def load_random_bg_image(self) -> pygame.Surface:
        file = os.path.join(MainMenuScene.BG_DIRECTORY, random.choice(os.listdir(MainMenuScene.BG_DIRECTORY)))
        return pygame.image.load(file)

    def load_save_data(self) -> bool:
        return False