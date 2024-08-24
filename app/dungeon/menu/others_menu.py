import pygame

from app.gui import text
from app.common.menu import Menu
from app.common import constants, settings
from app.common.inputstream import InputStream
from app.common.action import Action
from app.gui.textbox import DungeonMessageLog


class OthersMenu:
    def __init__(self, message_log: DungeonMessageLog):
        self.message_log = message_log
        self.menu = Menu((15, 17),
            [
                "Options",
                "Window",
                "Map",
                "Message log",
                "Mission objectives",
                "Dungeon hints",
            ],
            128,
            True, True, text.TextBuilder.build_white("  Others")
        )
        self.status = "Top"
    
    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        match self.status:
            case "Top":
                self.menu.process_input(input_stream)
                if kb.is_pressed(settings.get_key(Action.INTERACT)):
                    match self.menu.current_option:
                        case "Message log":
                            self.status = "Message log"
                        case _:
                            pass
            case "Message log":
                if kb.is_pressed(settings.get_key(Action.MENU)):
                    self.status = "Top"
                elif kb.is_pressed(settings.get_key(Action.UP)):
                    self.message_log.scroll_up()
                elif kb.is_pressed(settings.get_key(Action.DOWN)):
                    self.message_log.scroll_down()
        
    def update(self):
        match self.status:
            case "Top":
                self.menu.update()
            case _:
                pass

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        match self.status:
            case "Top":
                # TODO: X on bottom corner
                surface.blit(self.menu.render(), (8, 8))
            case "Message log":
                surface.blit(self.message_log.render(), (8, 8))
        return surface