"""
Stores commonly used constants for the app.
"""
import os
from pygame import Color

# Constants
# DISPLAY SETTINGS
DISPLAY_WIDTH = 256
DISPLAY_HEIGHT = 192
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
CAPTION = "Pokemon Mystery Dungeon Remake"

# CLOCK
FPS = 60

# COLOR CONSTANTS
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
OFF_BLACK = Color(32, 32, 32)
TRANSPARENT = Color(0, 0, 0, 0)

# File Paths
BASE_DIRECTORY = os.getcwd()

ASSETS_DIRECTORY = os.path.join(BASE_DIRECTORY, "assets")
IMAGES_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "images")
SOUND_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "sound")
FONT_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "font")

DATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "data")
USERDATA_DIRECTORY = os.path.join(DATA_DIRECTORY, "debug_userdata")
GAMEDATA_DIRECTORY = os.path.join(DATA_DIRECTORY, "gamedata")
