import pygame
import pygame.mixer

# Constants
# DISPLAY SETTINGS
DISPLAY_WIDTH = 256
DISPLAY_HEIGHT = 192
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
CAPTION = "Pokemon Mystery Dungeon Remake"

# CLOCK
FPS = 60

# GAME CONSTANTS
TILE_SIZE = 24  # Pixels
WALK_ANIMATION_TIME = 24  # Frames
SPRINT_ANIMATION_TIME = 4  # Frames

# COLOR CONSTANTS
RED = pygame.Color(255, 70, 70)
CYAN = pygame.Color(0, 248, 248)
BLUE = pygame.Color(0, 152, 248)
GREEN = pygame.Color(40, 248, 48)
YELLOW = pygame.Color(248, 248, 0)
GREEN2 = pygame.Color(0, 248, 0)
WHITE = pygame.Color(255, 255, 255)
OFF_WHITE = pygame.Color(248, 248, 248)
BLACK = pygame.Color(0, 0, 0)
OFF_BLACK = pygame.Color(32, 32, 32)
ORANGE = pygame.Color(248, 128, 88)
GOLD = pygame.Color(248, 192, 96)
TRANSPARENT = pygame.Color(0, 0, 0, 0)

# SOUND
pygame.mixer.init()
MUSIC_CHANNEL = pygame.mixer.Channel(0)