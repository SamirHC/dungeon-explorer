import os
import random

import pygame
import pygame.display
import pygame.image
import pygame.mixer
from dungeon_explorer.common import inputstream, menu, textbox
from dungeon_explorer.pokemon import party
from dungeon_explorer.scenes import dungeon, scene


class MainMenuScene(scene.Scene):
    BG_DIRECTORY = os.path.join("assets", "images", "bg", "main")
    def __init__(self):
        super().__init__()
        self.bg = self.load_random_bg_image()
        self.menu = menu.Menu((10, 6), ["New Game", "Options"])
        self.option_description = textbox.TextBox((30, 6), 2)
        pygame.mixer.music.load(os.path.join("assets", "sound", "music", "Top Menu Theme.mp3"))
        pygame.mixer.music.play(-1)

    def process_input(self, input_stream: inputstream.InputStream):
        self.menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.menu.current_option == "New Game":
                entry_party = party.Party()
                entry_party.add("0")
                entry_party.add("3")
                self.next_scene = dungeon.StartDungeonScene("25", entry_party)
                pygame.mixer.music.fadeout(500)
            elif self.menu.current_option == "Options":
                print("Options")

    def update(self):
        self.menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.menu.render(), (8, 8))
        surface.blit(self.option_description.surface, (8, 17*8))
        return surface

    def load_random_bg_image(self) -> pygame.Surface:
        file = os.path.join(MainMenuScene.BG_DIRECTORY, random.choice(os.listdir(MainMenuScene.BG_DIRECTORY)))
        return pygame.image.load(file)
