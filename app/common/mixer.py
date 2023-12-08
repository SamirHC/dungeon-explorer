import pygame
import pygame.mixer

from app.common import settings
import app.db.database as db


pygame.mixer.init()
pygame.mixer.music.set_volume(settings.get_bgm())

current_bgm = None

def set_bgm(new_bgm: int):
    global current_bgm
    if current_bgm is new_bgm:
        return
    if current_bgm is not None:
        pygame.mixer.music.fadeout(500)
    current_bgm = new_bgm
    if new_bgm is not None:
        pygame.mixer.music.load(db.music_db[new_bgm])
        pygame.mixer.music.play(-1)
