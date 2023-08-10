import configparser
import os
import pygame
from app.common.action import Action

from app.common.constants import USERDATA_DIRECTORY

config = configparser.ConfigParser()

file = os.path.join(USERDATA_DIRECTORY, "settings.cfg")
config.read(file)

def save():
    with open(file, "w") as f:
        config.write(f)

# SOUND
def get_bgm() -> float:
    return float(config["SOUND"]["bgm"])

def update_bgm(value: float):
    config["SOUND"]["bgm"] = max(0.0, min(value, 1.0))

def get_sfx() -> float:
    return float(config["SOUND"]["sfx"])

def update_sfx(value: float):
    config["SOUND"]["sfx"] = max(0.0, min(value, 1.0))

# GRAPHICS
def get_frame() -> int:
    return int(config["GRAPHICS"]["frame"])

def update_frame(value: int):
    config["GRAPHICS"]["frame"] = max(0, min(value, 4))

# CONTROLS
def get_key(action: Action) -> int:
    return pygame.key.key_code(config["CONTROLS"][action.name])

def set_key(action: Action, key: int):
    config["CONTROLS"][action.name] = pygame.key.name(key)
