import os

import pygame
import pygame.image
import pygame.mixer

from app.common.constants import RNG as random
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings, mixer
from app.common.menu import MenuOption, MenuController, MenuPage, MenuRenderer, Menu
from app.gui.frame import Frame
from app.gui import text
from app.pokemon.party import Party
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.scenes.scene import Scene
from app.scenes import new_game_scene
from app.common.constants import IMAGES_DIRECTORY
from app.item.inventory import Inventory


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

        self.menu = self.build_menu()
        self.menu_renderer = MenuRenderer((10, 6), self.menu)
        self.menu_controller = MenuController(self.menu)

        self.option_desc_frame = Frame((30, 6))

    def build_menu(self) -> MenuPage:
        page = MenuPage("NewGameMainMenu-0")
        page.add_option(MenuOption(
            "New Game",
            metadata={"description": "Start an entirely new adventure."}
        ))
        page.add_option(MenuOption(
            "Options",
            metadata={"description": "\n".join((
                "View settings and saved game data,",
                "send a Demo Dungeon, and more..."
            ))}
        ))
        return page

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        if self.in_transition:
            return
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            self.menu_renderer.pointer_animation.restart()
            self.menu_controller.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            self.menu_renderer.pointer_animation.restart()
            self.menu_controller.prev()
        elif kb.is_pressed(settings.get_key(Action.INTERACT)):
            self.menu_renderer.pointer_animation.restart()
            self.menu_controller.select()

    def update(self):
        super().update()
        self.menu_renderer.update()
        intent = self.menu_controller.consume_intent()
        match intent:
            case "New Game":
                pygame.mixer.music.fadeout(500)
                self.next_scene = new_game_scene.NewGameScene()
            case "Options":
                print("Options")

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.menu_renderer.render(), (8, 8))
        surface.blit(self.option_desc_frame, (8, 17 * 8))
        surface.blit(self.get_option_description(), (8 + 12, 17 * 8 + 10))
        return surface

    def get_option_description(self) -> pygame.Surface:
        desc = self.menu.current_option.metadata.get("description")
        return text.TextBuilder.build_white(desc).render()


class MainMenuScene(Scene):
    def __init__(self):
        super().__init__(30, 30)
        mixer.set_bgm(-1)

        self.bg = load_random_bg_image()

        self.menu = self.build_menu() 
        self.menu_renderer = MenuRenderer((13, 16), self.menu)
        self.menu_controller = MenuController(self.menu)

        self.option_desc_frame = Frame((30, 6))

    def build_menu(self) -> MenuPage:
        menu = MenuPage("MainMenu-0")
        menu.add_option(MenuOption(
            "Continue",
            metadata={"description": "\n".join((
                "Resume your adventure from your last",
                "save point."
            ))}
        ))
        menu.add_option(MenuOption("Go Rescue"))
        menu.add_option(MenuOption("Friend Rescue"))
        menu.add_option(MenuOption("Wonder Mail"))
        menu.add_option(MenuOption("Trade Items"))
        menu.add_option(MenuOption("Trade Team"))
        menu.add_option(MenuOption("Other"))
        menu.add_option(MenuOption("Episode List"))

        return menu

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        if self.in_transition:
            return
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            self.menu_renderer.pointer_animation.restart()
            self.menu_controller.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            self.menu_renderer.pointer_animation.restart()
            self.menu_controller.prev()
        elif kb.is_pressed(settings.get_key(Action.INTERACT)):
            self.menu_renderer.pointer_animation.restart()
            self.menu_controller.select()

    def update(self):
        super().update()
        self.menu_renderer.update()
        intent = self.menu_controller.consume_intent()
        match intent:
            case "Continue":
                pygame.mixer.music.fadeout(500)
                # TODO: Should continue from save point.
                """
                Currently hardcoded for testing purposes.
                """
                entry_party = Party([user_pokemon_factory(0), user_pokemon_factory(1)])
                entry_party[0].position = (9 * 24, 8 * 24)
                entry_party[1].position = (10 * 24, 8 * 24)
                inventory = Inventory()
                inventory.add_money(12_345)
                from app.scenes import ground_scene

                self.next_scene = ground_scene.StartGroundScene(
                    0, entry_party, inventory
                )
            case x if x is not None:
                print(x)

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.menu_renderer.render(), (8, 8))
        surface.blit(self.option_desc_frame, (8, 17 * 8))
        surface.blit(self.get_option_description(), (8 + 12, 17 * 8 + 10))
        return surface

    def get_option_description(self) -> pygame.Surface:
        desc = self.menu.current_option.metadata.get("description", "")
        return text.TextBuilder.build_white(desc).render()
