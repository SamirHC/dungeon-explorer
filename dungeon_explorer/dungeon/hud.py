import os
import pygame
import pygame.display
import pygame.draw
import pygame.image
from ..common import constants

pygame.display.init()

component_color = constants.ORANGE
HUD_COMPONENTS_FILE = os.path.join(
    os.getcwd(), "assets", "images", "misc", "hud_components.png")

hud_components = pygame.image.load(HUD_COMPONENTS_FILE)
hud_components.set_colorkey(hud_components.get_at((0, 0)))
hud_components.set_palette_at(12, component_color)  # Makes the labelling text (e.g. B, F, Lv, HP) orange

def get_component(x: int, y: int, width: int = 1) -> pygame.Surface:
    return hud_components.subsurface(x*8, y*8, width*8, 8)

def parse_number(n: int) -> pygame.Surface:
    variant = 0  # Colour of number can be either white(0) or green(1)
    s = str(n)
    surface = pygame.Surface((8*len(s), 8), pygame.SRCALPHA)
    for i, c in enumerate(s):
        surface.blit(get_component(int(c), variant), (i*8, 0))
    return surface

def get_f_lv() -> pygame.Surface:
    return get_component(10, 0, 3)

def get_b() -> pygame.Surface:
    return get_component(13, 1)

def get_hp() -> pygame.Surface:
    return get_component(10, 1, 2)

def get_slash() -> pygame.Surface:
    return get_component(12, 1)

def draw(is_below: bool, floor_number: int, level: int, hp: int, max_hp: int) -> pygame.Surface:
    surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
    x = 0
    # Floor
    if is_below:
        surface.blit(get_b(), (x, 0))
        x += 8
    surface.blit(parse_number(floor_number), (x, 0))
    x += len(str(floor_number)) * 8
    surface.blit(get_f_lv(), (x, 0))
    x += 3 * 8
    # Level
    surface.blit(parse_number(level), (x, 0))
    x += 4 * 8
    # HP
    surface.blit(get_hp(), (x, 0))
    x += 2 * 8
    j = x
    surface.blit(parse_number(hp), (x, 0))
    x += len(str(hp)) * 8
    surface.blit(get_slash(), (x, 0))
    x += 8
    surface.blit(parse_number(max_hp), (x, 0))
    x = j + 7 * 8  # 3 digit hp, slash, 3 digit max hp
    # HP bar
    pygame.draw.rect(surface, constants.RED, (x, 0, max_hp, 8))
    if hp > 0:
        pygame.draw.rect(surface, constants.GREEN, (x, 0, hp, 8))
    pygame.draw.rect(surface, constants.BLACK, (x, 0, max_hp, 2))
    pygame.draw.rect(surface, constants.BLACK, (x, 6, max_hp, 2))
    pygame.draw.rect(surface, constants.WHITE, (x, 0, max_hp, 1))
    pygame.draw.rect(surface, constants.WHITE, (x, 6, max_hp, 1))
    return surface
