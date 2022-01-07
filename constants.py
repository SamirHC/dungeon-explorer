import direction
import pygame

# Constants
# DISPLAY SETTINGS
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
CAPTION = "Pokemon Mystery Dungeon Remake"

# CLOCK
FPS = 60

# GAME CONSTANTS
TILE_SIZE = 24  # measured in pixels
POKE_SIZE = 200
TIME_FOR_ONE_TILE = 0.4  # seconds per tile
FASTER_TIME_FOR_ONE_TILE = 0.05  # seconds per tile

# COLOR CONSTANTS
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
