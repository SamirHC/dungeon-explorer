from . import constants
import pygame
import pygame.font
import os

pygame.font.init()


class Text:
    FONT_SIZE = 15
    FONT_DIRECTORY = os.path.join(
        os.getcwd(), "assets", "font", "PKMN-Mystery-Dungeon.ttf")
    FONT = pygame.font.Font(FONT_DIRECTORY, FONT_SIZE)

    def __init__(self, text: str, text_color: pygame.Color=constants.WHITE):
        text_surface = Text.FONT.render(text, False, text_color)
        shadow_surface = Text.FONT.render(text, False, constants.BLACK)
        w, h = text_surface.get_size()
        self.surface = pygame.Surface((w+1, h+1), pygame.SRCALPHA)
        self.surface.blit(shadow_surface, (0, 1))
        self.surface.blit(shadow_surface, (1, 0))
        self.surface.blit(text_surface, (0, 0))


class MultiColoredText:
    def __init__(self, items: list[tuple[str, pygame.Color]]):
        surfaces: list[pygame.Surface] = []
        w, h = 0, 0
        for text, color in items:
            surfaces.append(Text(text, color).surface)
            w += surfaces[-1].get_width()
            h = max(h, surfaces[-1].get_height())
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        w = 0
        for surface in surfaces:
            self.surface.blit(surface, (w, 0))
            w += surface.get_width()
