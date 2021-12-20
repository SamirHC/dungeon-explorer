# Imports
import pygame as p
import os
from random import randint

p.init()

# Constants
# DISPLAY SETTINGS
display_width = 1280
display_height = 720
CAPTION = "PMD Alpha"
display = p.display.set_mode((display_width, display_height))
p.display.set_caption(CAPTION)

# FONT
FONT_SIZE = 36
FONT = p.font.Font(os.path.join(os.getcwd(), "Fonts", "PKMN-Mystery-Dungeon.ttf"), FONT_SIZE)

# CLOCK
clock = p.time.Clock()
FPS = 120

# GAME CONSTANTS
ROWS, COLS = 40, 65  # Map dimensions (measured in tiles)
TILE_SIZE = 50  # measured in pixels
POKE_SIZE = int(200 / 60 * TILE_SIZE)
AGGRO_RANGE = 5  # measured in tiles
TRAPS_PER_FLOOR = randint(0, 6)
TIME_FOR_ONE_TILE = 0.35  # seconds per tile
FASTER_TIME_FOR_ONE_TILE = 0.05  # seconds per tile

time_for_one_tile = TIME_FOR_ONE_TILE
motion_time_left = 0
attack_time_left = 0
# COLOR CONSTANTS
TRANS = (0, 128, 128)  # RGB value of color that will be set to transparent
TRANS_PINK = (255, 0, 255)
RED = (255, 70, 70)
GREEN = (80, 255, 70)
BORDER_BLUE_1 = (154, 190, 237)
BORDER_BLUE_2 = (160, 210, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Controls
KeyPress = {"Direction": {p.K_q: (-1, -1),  # UP-LEFT
                          p.K_w: (0, -1),  # UP
                          p.K_e: (1, -1),  # UP-RIGHT
                          p.K_a: (-1, 0),  # LEFT
                          p.K_s: (0, 0),  # CENTRE
                          p.K_d: (1, 0),  # RIGHT
                          p.K_z: (-1, 1),  # DOWN-LEFT
                          p.K_x: (0, 1),  # DOWN
                          p.K_c: (1, 1),  # DOWN-RIGHT
                          },
            "Attack": {p.K_1: 0,
                       p.K_2: 1,
                       p.K_3: 2,
                       p.K_4: 3,
                       p.K_5: 4,
                       },
            "Menu": {
            },
            }

# FUNCTIONS
def scale(image, size):
    return p.transform.scale(image, (int(size), int(size)))

def cool_font(text, color, position):
    x = position[0]
    y = position[1]
    text_surf = FONT.render(text, False, color)
    shadow_surf = FONT.render(text, False, BLACK)
    display.blit(shadow_surf, (x + 1, y))
    display.blit(shadow_surf, (x, y + 1))
    display.blit(text_surf, position)

def remove_duplicates(collection):
    return list(dict.fromkeys(collection))
