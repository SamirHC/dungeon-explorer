import constants
import pygame
import pygame.font
import os

pygame.font.init()


class Text:
    FONT_SIZE = 15
    FONT_DIRECTORY = os.path.join(
        os.getcwd(), "assets", "font", "PKMN-Mystery-Dungeon.ttf")
    FONT = pygame.font.Font(FONT_DIRECTORY, FONT_SIZE)

    def __init__(self, text: str, text_color=constants.WHITE):
        self.text = text
        self.text_color = text_color
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        return Text.FONT.render(self.text, False, self.text_color)
