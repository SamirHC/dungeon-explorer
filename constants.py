import pygame as p
import os
from direction import Direction

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
FONT_DIRECTORY = os.path.join(os.getcwd(), "Fonts", "PKMN-Mystery-Dungeon.ttf")
FONT = p.font.Font(FONT_DIRECTORY, FONT_SIZE)

# CLOCK
clock = p.time.Clock()
FPS = 120

# GAME CONSTANTS
ROWS, COLS = 40, 65  # Map dimensions (measured in tiles)
TILE_SIZE = 48  # measured in pixels
POKE_SIZE = int(200 / 60 * TILE_SIZE)
AGGRO_RANGE = 5  # measured in tiles
TRAPS_PER_FLOOR = 6
TIME_FOR_ONE_TILE = 0.35  # seconds per tile
FASTER_TIME_FOR_ONE_TILE = 0.05  # seconds per tile

# COLOR CONSTANTS
TRANS = p.Color(0, 128, 128)  # RGB value of color that will be set to transparent
TRANS_PINK = p.Color(255, 0, 255)
RED = p.Color(255, 70, 70)
GREEN = p.Color(80, 255, 70)
BORDER_BLUE_1 = p.Color(154, 190, 237)
BORDER_BLUE_2 = p.Color(160, 210, 230)
WHITE = p.Color(255, 255, 255)
BLACK = p.Color(0, 0, 0)

# Controls
key_press = {
    "Direction": {
        p.K_q: Direction.NORTH_WEST,
        p.K_w: Direction.NORTH,
        p.K_e: Direction.NORTH_EAST,
        p.K_a: Direction.WEST,
        p.K_s: Direction.SOUTH,
        p.K_d: Direction.EAST,
        p.K_z: Direction.SOUTH_WEST,
        p.K_x: Direction.SOUTH,
        p.K_c: Direction.SOUTH_EAST
    },
    "Attack": {
        p.K_1: 0,
        p.K_2: 1,
        p.K_3: 2,
        p.K_4: 3,
        p.K_5: 4
    },
    "Menu": {
    }
}
