import configparser
import os

config = configparser.ConfigParser()

file = os.path.join("data", "userdata", "settings.cfg")
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
