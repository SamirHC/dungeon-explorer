import os

import pygame
import pygame.display
import pygame.image
import pygame.mixer

from app.common.constants import RNG as random
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings, menu, mixer
from app.gui.frame import Frame
from app.gui import text
from app.pokemon.party import Party
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.scenes.scene import Scene
from app.scenes import newgame
from app.common.constants import IMAGES_DIRECTORY


BG_DIRECTORY = os.path.join(IMAGES_DIRECTORY, "bg", "main")


def load_random_bg_image() -> pygame.Surface:
    bg_path = os.path.join(
        BG_DIRECTORY,
        random.choice(os.listdir(BG_DIRECTORY)),
    )
    return pygame.image.load(bg_path)


class NewGameMainMenuScene(Scene):
    def __init__(self):
        super().__init__(30, 30)
        mixer.set_bgm(-1)

        self.bg = load_random_bg_image()
        self.option_desc_frame = Frame((30, 6))
        self.menu = menu.Menu((10, 6), ["New Game", "Options"])
        self.descriptions = [
            "Start an entirely new adventure.",
            "View settings and saved game data,\nsend a Demo Dungeon, and more...",
        ]

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        if self.in_transition:
            return
        self.menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)):
            if self.menu.current_option == "New Game":
                pygame.mixer.music.fadeout(500)
                self.next_scene = newgame.NewGameScene()
            elif self.menu.current_option == "Options":
                print("Options")

    def update(self):
        super().update()
        self.menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.menu.render(), (8, 8))
        surface.blit(self.option_desc_frame, (8, 17 * 8))
        surface.blit(self.get_option_description(), (8 + 12, 17 * 8 + 10))
        return surface

    def get_option_description(self) -> pygame.Surface:
        return text.TextBuilder.build_white(self.descriptions[self.menu.pointer]).render()


class MainMenuScene(Scene):
    def __init__(self):
        super().__init__(30, 30)
        mixer.set_bgm(-1)

        self.bg = load_random_bg_image()
        self.option_desc_frame = Frame((30, 6))
        self.menu = menu.Menu(
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
        self.descriptions = [
            "Resume your adventure from your last\nsave point.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        if self.in_transition:
            return
        self.menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)):
            if self.menu.current_option == "Continue":
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
        self.menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.menu.render(), (8, 8))
        surface.blit(self.option_desc_frame, (8, 17 * 8))
        surface.blit(self.get_option_description(), (8 + 12, 17 * 8 + 10))
        return surface

    def get_option_description(self) -> pygame.Surface:
        return text.TextBuilder.build_white(self.descriptions[self.menu.pointer]).render()
