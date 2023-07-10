import configparser
import os
import pygame

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

# CONTROLS
def get_key(name: str) -> int:
    return pygame.key.key_code(config["CONTROLS"][name])

def set_key(name: str, key: int):
    config["CONTROLS"][name] = pygame.key.name(key)

def get_regular_attack_key() -> int:
    return get_key("REGULAR_ATTACK_KEY")
def get_attack_1_key() -> int:
    return get_key("ATTACK_1_KEY")
def get_attack_2_key() -> int:
    return get_key("ATTACK_2_KEY")
def get_attack_3_key() -> int:
    return get_key("ATTACK_3_KEY")
def get_attack_4_key() -> int:
    return get_key("ATTACK_4_KEY")
def get_pass_turn_key() -> int:
    return get_key("PASS_TURN_KEY")
def get_walk_north_key() -> int:
    return get_key("WALK_NORTH_KEY")
def get_walk_west_key() -> int:
    return get_key("WALK_WEST_KEY")
def get_walk_south_key() -> int:
    return get_key("WALK_SOUTH_KEY")
def get_walk_east_key() -> int:
    return get_key("WALK_EAST_KEY")
def get_toggle_menu_key() -> int:
    return get_key("TOGGLE_MENU_KEY")
def get_select_key() -> int:
    return get_key("SELECT_KEY")
def get_option_scroll_up_key() -> int:
    return get_key("OPTION_UP_KEY")
def get_option_scroll_down_key() -> int:
    return get_key("OPTION_DOWN_KEY")
def get_page_next_key() -> int:
    return get_key("PAGE_NEXT_KEY")
def get_page_prev_key() -> int:
    return get_key("PAGE_PREV_KEY")
def get_toggle_fullscreen_key() -> int:
    return get_key("TOGGLE_FULLSCREEN_KEY")
def get_quit_key() -> int:
    return get_key("QUIT_KEY")

def set_regular_attack_key(key: int):
    set_key("REGULAR_ATTACK_KEY", key)
def set_attack_1_key(key: int):
    set_key("ATTACK_1_KEY", key)
def set_attack_2_key(key: int):
    set_key("ATTACK_2_KEY", key)
def set_attack_3_key(key: int):
    set_key("ATTACK_3_KEY", key)
def set_attack_4_key(key: int):
    set_key("ATTACK_4_KEY", key)
def set_pass_turn_key(key: int):
    set_key("PASS_TURN_KEY", key)
def set_walk_north_key(key: int):
    set_key("WALK_NORTH_KEY", key)
def set_walk_west_key(key: int):
    set_key("WALK_WEST_KEY", key)
def set_walk_south_key(key: int):
    set_key("WALK_SOUTH_KEY", key)
def set_walk_east_key(key: int):
    set_key("WALK_EAST_KEY", key)
def set_toggle_menu_key(key: int):
    set_key("TOGGLE_MENU_KEY", key)
def set_select_key(key: int):
    set_key("SELECT_KEY", key)
def set_option_scroll_up_key(key: int):
    set_key("OPTION_UP_KEY", key)
def set_option_scroll_down_key(key: int):
    set_key("OPTION_DOWN_KEY", key)
def set_page_next_key(key: int):
    set_key("PAGE_NEXT_KEY", key)
def set_page_prev_key(key: int):
    set_key("PAGE_PREV_KEY", key)
def set_toggle_fullscreen_key(key: int):
    set_key("TOGGLE_FULLSCREEN_KEY", key)
def set_quit_key(key: int):
    set_key("QUIT_KEY", key)
