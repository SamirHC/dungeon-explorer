import pygame

# Constants
# DISPLAY SETTINGS
DISPLAY_WIDTH = 256
DISPLAY_HEIGHT = 192
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
CAPTION = "Pokemon Mystery Dungeon Remake"

# CLOCK
FPS = 60

# COLOR CONSTANTS
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
OFF_BLACK = pygame.Color(32, 32, 32)
TRANSPARENT = pygame.Color(0, 0, 0, 0)

# Controls
REGULAR_ATTACK_KEY = pygame.K_RETURN
ATTACK_1_KEY = pygame.K_1
ATTACK_2_KEY = pygame.K_2
ATTACK_3_KEY = pygame.K_3
ATTACK_4_KEY = pygame.K_4

PASS_TURN_KEY = pygame.K_x

WALK_NORTH_KEY = pygame.K_w
WALK_WEST_KEY = pygame.K_a
WALK_SOUTH_KEY = pygame.K_s
WALK_EAST_KEY = pygame.K_d

TOGGLE_MENU_KEY = pygame.K_n
SELECT_KEY = pygame.K_RETURN
OPTION_SCROLL_UP_KEY = pygame.K_w
OPTION_SCROLL_DOWN_KEY = pygame.K_s
PAGE_NEXT_KEY = pygame.K_d
PAGE_PREV_KEY = pygame.K_a

TOGGLE_FULLSCREEN_KEY = pygame.K_F11
QUIT_KEY = pygame.K_ESCAPE