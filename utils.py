import constants
import pygame
import text


def cool_font(text_obj: text.Text, color: pygame.Color, position: tuple[int, int], display: pygame.Surface):
    x, y = position
    text_surf = text.Text(text_obj, color).surface
    shadow_surf = text.Text(text_obj, constants.BLACK).surface
    display.blit(shadow_surf, (x + 1, y))
    display.blit(shadow_surf, (x, y + 1))
    display.blit(text_surf, position)


def remove_duplicates(collection):
    return list(dict.fromkeys(collection))
