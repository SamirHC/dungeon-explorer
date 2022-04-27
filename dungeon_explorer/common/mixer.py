import pygame
import pygame.mixer

from dungeon_explorer.common import settings


pygame.mixer.init()

MUSIC_CHANNEL = pygame.mixer.Channel(0)
MUSIC_CHANNEL.set_volume(settings.get_bgm())

current_bgm_path = None

def play():
    if current_bgm_path is not None:
        MUSIC_CHANNEL.play(pygame.mixer.Sound(current_bgm_path), -1)
    
def set_bgm(music_path: str):
    global current_bgm_path
    if current_bgm_path != music_path:
        current_bgm_path = music_path
        play()
