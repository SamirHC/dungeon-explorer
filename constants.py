import direction
import pygame

# Constants
# DISPLAY SETTINGS
DISPLAY_WIDTH = 256
DISPLAY_HEIGHT = 192
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
CAPTION = "Pokemon Mystery Dungeon Remake"

# CLOCK
FPS = 60

# GAME CONSTANTS
TILE_SIZE = 24  # measured in pixels
WALK_ANIMATION_TIME = 0.4  # seconds per tile
SPRINT_ANIMATION_TIME = 0.05  # seconds per tile

# COLOR CONSTANTS
RED = pygame.Color(255, 70, 70)
BLUE = pygame.Color(0, 152, 248)
GREEN = pygame.Color(40, 248, 48)
YELLOW = pygame.Color(248, 248, 0)
GREEN2 = pygame.Color(0, 248, 0)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
ORANGE = pygame.Color(248, 128, 88)

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
