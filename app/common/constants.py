"""
Stores commonly used constants for the app.
"""

import pygame
from app.common import settings

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
REGULAR_ATTACK_KEY = settings.get_regular_attack_key()
RUN_KEY = settings.get_run_key()
ATTACK_1_KEY = settings.get_attack_1_key()
ATTACK_2_KEY = settings.get_attack_2_key()
ATTACK_3_KEY = settings.get_attack_3_key()
ATTACK_4_KEY = settings.get_attack_4_key()
PASS_TURN_KEY = settings.get_pass_turn_key()
HOLD_TURN_KEY = settings.get_hold_turn_key()
WALK_NORTH_KEY = settings.get_walk_north_key()
WALK_WEST_KEY = settings.get_walk_west_key()
WALK_SOUTH_KEY = settings.get_walk_south_key()
WALK_EAST_KEY = settings.get_walk_east_key()
TOGGLE_MENU_KEY = settings.get_toggle_menu_key()
SELECT_KEY = settings.get_select_key()
OPTION_UP_KEY = settings.get_option_scroll_up_key()
OPTION_DOWN_KEY = settings.get_option_scroll_down_key()
PAGE_NEXT_KEY = settings.get_page_next_key()
PAGE_PREV_KEY = settings.get_page_prev_key()
TOGGLE_FULLSCREEN_KEY = settings.get_toggle_fullscreen_key()
QUIT_KEY = settings.get_quit_key()
