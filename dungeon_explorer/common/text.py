from . import constants
import pygame
import pygame.constants
import pygame.font
import os

pygame.font.init()


class Text:
    FONT_SIZE = 15
    FONT_DIRECTORY = os.path.join(
        os.getcwd(), "assets", "font", "PKMN-Mystery-Dungeon.ttf")
    FONT = pygame.font.Font(FONT_DIRECTORY, FONT_SIZE)

    def __init__(self, text: str, text_color: pygame.Color=constants.WHITE):
        self.text = text
        self.text_color = text_color
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        surface = Text.FONT.render(self.text, False, self.text_color)
        shadow_surface = Text.FONT.render(self.text, False, constants.BLACK)
        w, h = surface.get_size()
        new_surface = pygame.Surface((w+1, h+1), pygame.constants.SRCALPHA)
        new_surface.blit(shadow_surface, (0, 1))
        new_surface.blit(shadow_surface, (1, 0))
        new_surface.blit(surface, (0, 0))
        return new_surface


class MultiColoredText:
    def __init__(self, items: list[tuple[str, pygame.Color]]):
        self.items = items
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        surfaces: list[pygame.Surface] = []
        w = 0
        h = 0
        for text, color in self.items:
            surfaces.append(Text(text, color).surface)
            w += surfaces[-1].get_width()
            h = max(h, surfaces[-1].get_height())
        result_surface = pygame.Surface((w, h), pygame.constants.SRCALPHA)
        w = 0
        for surface in surfaces:
            result_surface.blit(surface, (w, 0))
            w += surface.get_width()
        return result_surface