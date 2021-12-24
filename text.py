from constants import WHITE
import pygame as p
import os

class Text:
    FONT_SIZE = 36
    FONT_DIRECTORY = os.path.join(os.getcwd(), "Fonts", "PKMN-Mystery-Dungeon.ttf")
    FONT = p.font.Font(FONT_DIRECTORY, FONT_SIZE)

    def __init__(self, text, text_color=WHITE):
        self.text = text
        self.text_color = text_color
        self.surface = self.draw()

    def draw(self):
        return Text.FONT.render(self.text, False, self.text_color)
