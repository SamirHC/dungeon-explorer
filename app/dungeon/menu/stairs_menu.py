from app.common import constants, menu
from app.common.inputstream import InputStream
from app.gui.frame import Frame

import pygame

from app.gui import text


class StairsMenu:
    def __init__(self):
        self.menu = menu.Menu((9, 8), ["Proceed", "Info", "Cancel"], 128)
        self.frame = self.build_stairs_surface()
        # SIGNALS
        self.is_quick_access = False  # Signal to open directly when user steps on stair
        self.proceed = False  # Signal to DungeonScene to move to next scene

    def build_stairs_surface(self) -> pygame.Surface:
        surface = Frame((21, 6), 128).with_header_divider()
        stairs_text_surface = text.TextBuilder.build_white("Stairs").render()
        surface.blit(stairs_text_surface, (16, 10))
        surface.blit(stairs_text_surface, (24, 28))
        return surface

    def process_input(self, input_stream: InputStream):
        self.menu.process_input(input_stream)

    def update(self):
        self.menu.update()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.frame, (8, 8))
        surface.blit(self.menu.render(), (176, 8))
        return surface
