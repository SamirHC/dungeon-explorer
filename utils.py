import pygame as p
from constants import *

def scale(image: p.Surface, size: int) -> p.Surface:
    return p.transform.scale(image, (int(size), int(size)))

def cool_font(text: str, color: p.Color, position: tuple[int, int]):
    x = position[0]
    y = position[1]
    text_surf = FONT.render(text, False, color)
    shadow_surf = FONT.render(text, False, BLACK)
    display.blit(shadow_surf, (x + 1, y))
    display.blit(shadow_surf, (x, y + 1))
    display.blit(text_surf, position)

def remove_duplicates(collection):
    return list(dict.fromkeys(collection))