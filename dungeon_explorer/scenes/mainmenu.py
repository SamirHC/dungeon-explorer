import os
import random

import pygame
import pygame.display
import pygame.image
import pygame.mixer
from dungeon_explorer.common import inputstream, menu, frame, text, constants, mixer
from dungeon_explorer.pokemon import party
from dungeon_explorer.scenes import scene, newgame, dungeon


class MainMenuScene(scene.Scene):
    BG_DIRECTORY = os.path.join("assets", "images", "bg", "main")
    def __init__(self):
        super().__init__()
        self.bg = self.load_random_bg_image()
        self.option_description = frame.Frame((30, 6))

        self.new_game_menu = menu.Menu((10, 6), ["New Game", "Options"])
        self.new_game_descriptions = [
            "Start an entirely new adventure.",
            "View settings and saved game data,\nsend a Demo Dungeon, and more..."
        ]
        self.continue_game_menu = menu.Menu((13, 16), ["Continue", "Go Rescue", "Friend Rescue", "Wonder Mail", "Trade Items", "Trade Team", "Other", "Episode List"])
        self.continue_game_descriptions = [
            "Resume your adventure from your last\nsave point.",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
        self.current_menu = self.continue_game_menu if self.load_save_data() else self.new_game_menu

        mixer.set_bgm(os.path.join("assets", "sound", "music", "Top Menu Theme.mp3"))

    def process_input(self, input_stream: inputstream.InputStream):
        if self.current_menu is self.new_game_menu:
            self.process_input_new_game(input_stream)
        elif self.current_menu is self.continue_game_menu:
            self.process_input_continue_game(input_stream)

    def process_input_new_game(self, input_stream: inputstream.InputStream):
        self.new_game_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.new_game_menu.current_option == "New Game":
                mixer.MUSIC_CHANNEL.fadeout(500)
                self.next_scene = newgame.NewGameScene()
            elif self.new_game_menu.current_option == "Options":
                print("Options")

    def process_input_continue_game(self, input_stream: inputstream.InputStream):
        self.continue_game_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.continue_game_menu.current_option == "Continue":
                mixer.MUSIC_CHANNEL.fadeout(500)
                entry_party = party.Party("0")
                entry_party.add("3")
                self.next_scene = dungeon.StartDungeonScene("47", entry_party)

    def update(self):
        self.current_menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.current_menu.render(), (8, 8))
        surface.blit(self.option_description, (8, 17*8))
        surface.blit(self.get_option_description(), (8+12, 17*8+10))
        return surface

    def get_option_description(self) -> pygame.Surface:
        if self.current_menu is self.new_game_menu:
            current_descriptions = self.new_game_descriptions
        else:
            current_descriptions = self.continue_game_descriptions
        return (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(constants.OFF_WHITE)
            .write(current_descriptions[self.current_menu.pointer])
            .build()
            .render()
        )

    def load_random_bg_image(self) -> pygame.Surface:
        file = os.path.join(MainMenuScene.BG_DIRECTORY, random.choice(os.listdir(MainMenuScene.BG_DIRECTORY)))
        return pygame.image.load(file)

    def load_save_data(self) -> bool:
        return True