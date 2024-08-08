"""
Stores commonly used constants for the app.
"""
import os, sys
import random

import pygame

# Constants
# DISPLAY SETTINGS
DISPLAY_WIDTH = 256
DISPLAY_HEIGHT = 192
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)

# COLORS
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
OFF_BLACK = pygame.Color(32, 32, 32)
TRANSPARENT = pygame.Color(0, 0, 0, 0)

# SURFACES
EMPTY_SURFACE = pygame.Surface((0, 0))

# RANDOM
SEED = 1
RNG = random.Random(SEED)

# File Paths
BASE_DIRECTORY = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")

ASSETS_DIRECTORY = os.path.join(BASE_DIRECTORY, "assets")
IMAGES_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "images")
SOUND_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "sound")
FONT_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "font")

DATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "data")
USERDATA_DIRECTORY = os.path.join(DATA_DIRECTORY, "debug_userdata")
GAMEDATA_DIRECTORY = os.path.join(DATA_DIRECTORY, "gamedata")
