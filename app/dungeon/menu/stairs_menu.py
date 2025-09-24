import pygame

from app.common import constants
from app.common.menu import MenuRenderer, MenuPage
from app.gui.frame import Frame
from app.gui import text


class StairsMenuRenderer(MenuRenderer):
    def __init__(self):
        super().__init__((9, 8), alpha=128)
        self.desc_frame = self.build_stairs_surface()

    def build_stairs_surface(self) -> pygame.Surface:
        surface = Frame((21, 6), 128).with_header_divider()
        stairs_text_surface = text.TextBuilder.build_white("Stairs").render()
        surface.blit(stairs_text_surface, (16, 10))
        surface.blit(stairs_text_surface, (24, 28))
        return surface

    def render(self, menu_page: MenuPage) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.desc_frame, (8, 8))
        surface.blit(super().render(menu_page), (176, 8))
        return surface
