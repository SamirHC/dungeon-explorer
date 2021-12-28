import direction
import pygame
import pygame.display
import pygame.time

pygame.init()

# Constants
# DISPLAY SETTINGS
display_width = 1280
display_height = 720
CAPTION = "PMD Alpha"
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption(CAPTION)

# CLOCK
clock = pygame.time.Clock()
FPS = 120

# GAME CONSTANTS
TILE_SIZE = 48  # measured in pixels
POKE_SIZE = int(200 / 60 * TILE_SIZE)
AGGRO_RANGE = 5  # measured in tiles
TIME_FOR_ONE_TILE = 0.35  # seconds per tile
FASTER_TIME_FOR_ONE_TILE = 0.05  # seconds per tile

# COLOR CONSTANTS
TRANS = pygame.Color(0, 128, 128)  # RGB value of color that will be set to transparent
TRANS_PINK = pygame.Color(255, 0, 255)
RED = pygame.Color(255, 70, 70)
GREEN = pygame.Color(80, 255, 70)
BORDER_BLUE_1 = pygame.Color(154, 190, 237)
BORDER_BLUE_2 = pygame.Color(160, 210, 230)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)

# Controls
direction_keys = {
    pygame.K_q: direction.Direction.NORTH_WEST,
    pygame.K_w: direction.Direction.NORTH,
    pygame.K_e: direction.Direction.NORTH_EAST,
    pygame.K_a: direction.Direction.WEST,
    pygame.K_s: direction.Direction.SOUTH,
    pygame.K_d: direction.Direction.EAST,
    pygame.K_z: direction.Direction.SOUTH_WEST,
    pygame.K_c: direction.Direction.SOUTH_EAST
}

attack_keys = {
    pygame.K_1: 0,
    pygame.K_2: 1,
    pygame.K_3: 2,
    pygame.K_4: 3,
    pygame.K_5: 4
}