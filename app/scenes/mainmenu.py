import os
import random

import pygame
import pygame.display
import pygame.image
import pygame.mixer
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings, menu, text, mixer
from app.model.frame import Frame
from app.pokemon.party import Party
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.scenes.scene import Scene
from app.scenes import newgame
from app.common.constants import IMAGES_DIRECTORY


class MainMenuScene(Scene):
    BG_DIRECTORY = os.path.join(IMAGES_DIRECTORY, "bg", "main")

    def __init__(self):
        super().__init__(30, 30)
        self.bg = self.load_random_bg_image()
        self.option_description = Frame((30, 6))

        self.new_game_menu = menu.Menu((10, 6), ["New Game", "Options"])
        self.new_game_descriptions = [
            "Start an entirely new adventure.",
            "View settings and saved game data,\nsend a Demo Dungeon, and more...",
        ]
        self.continue_game_menu = menu.Menu(
            (13, 16),
            [
                "Continue",
                "Go Rescue",
                "Friend Rescue",
                "Wonder Mail",
                "Trade Items",
                "Trade Team",
                "Other",
                "Episode List",
            ],
        )
        self.continue_game_descriptions = [
            "Resume your adventure from your last\nsave point.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
        self.current_menu = (
            self.continue_game_menu if self.load_save_data() else self.new_game_menu
        )

        mixer.set_bgm(-1)

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        if self.in_transition:
            return
        if self.current_menu is self.new_game_menu:
            self.process_input_new_game(input_stream)
        elif self.current_menu is self.continue_game_menu:
            self.process_input_continue_game(input_stream)

    def process_input_new_game(self, input_stream: InputStream):
        self.new_game_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)):
            if self.new_game_menu.current_option == "New Game":
                pygame.mixer.music.fadeout(500)
                self.next_scene = newgame.NewGameScene()
            elif self.new_game_menu.current_option == "Options":
                print("Options")

    def process_input_continue_game(self, input_stream: InputStream):
        self.continue_game_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)):
            if self.continue_game_menu.current_option == "Continue":
                pygame.mixer.music.fadeout(500)
                # TODO: Should continue from save point.
                """
                Currently hardcoded for testing purposes.
                """
                entry_party = Party([user_pokemon_factory(0), user_pokemon_factory(1)])
                entry_party[0].position = (9 * 24, 8 * 24)
                entry_party[1].position = (10 * 24, 8 * 24)
                from app.scenes import groundscene

                self.next_scene = groundscene.StartGroundScene(0, entry_party)

    def update(self):
        super().update()
        self.current_menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.current_menu.render(), (8, 8))
        surface.blit(self.option_description, (8, 17 * 8))
        surface.blit(self.get_option_description(), (8 + 12, 17 * 8 + 10))
        surface.set_alpha(self.alpha)
        return surface

    def get_option_description(self) -> pygame.Surface:
        if self.current_menu is self.new_game_menu:
            current_descriptions = self.new_game_descriptions
        else:
            current_descriptions = self.continue_game_descriptions
        return (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(current_descriptions[self.current_menu.pointer])
            .build()
            .render()
        )

    def load_random_bg_image(self) -> pygame.Surface:
        file = os.path.join(
            MainMenuScene.BG_DIRECTORY,
            random.choice(os.listdir(MainMenuScene.BG_DIRECTORY)),
        )
        return pygame.image.load(file)

    def load_save_data(self) -> bool:
        return True
