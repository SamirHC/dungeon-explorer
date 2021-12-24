import pygame as p
from constants import *
from text import Text

def scale(image: p.Surface, size: int) -> p.Surface:
    return p.transform.scale(image, (int(size), int(size)))

def cool_font(text: str, color: p.Color, position: tuple[int, int]):
    x, y = position
    text_surf = Text(text, color).surface
    shadow_surf = Text(text, BLACK).surface
    display.blit(shadow_surf, (x + 1, y))
    display.blit(shadow_surf, (x, y + 1))
    display.blit(text_surf, position)

def remove_duplicates(collection):
    return list(dict.fromkeys(collection))